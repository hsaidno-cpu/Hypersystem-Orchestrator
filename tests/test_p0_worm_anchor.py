"""Unit tests for S3 Object Lock WORM preflight and read-back behavior."""
from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from tools import anchor_p0_worm as worm


class P0WormAnchorTests(unittest.TestCase):
    def test_config_requires_bucket_and_compliance_retention_window(self):
        with patch.dict(os.environ, {"HSO_P0_WORM_BUCKET": "hso-evidence"}, clear=True):
            self.assertEqual(worm.config(), ("hso-evidence", 365))
        with patch.dict(os.environ, {
            "HSO_P0_WORM_BUCKET": "hso-evidence",
            "HSO_P0_WORM_RETENTION_DAYS": "90",
        }, clear=True):
            with self.assertRaisesRegex(RuntimeError, "retention configuration"):
                worm.config()

    def test_bucket_must_have_object_lock_and_versioning(self):
        with patch.object(worm, "aws_json", side_effect=[
            {"ObjectLockConfiguration": {"ObjectLockEnabled": "Enabled"}},
            {"Status": "Enabled"},
        ]):
            self.assertEqual(
                worm.validate_bucket("hso-evidence"),
                {"object_lock_enabled": True, "versioning_enabled": True},
            )
        with patch.object(worm, "aws_json", return_value={"ObjectLockConfiguration": {"ObjectLockEnabled": "Disabled"}}):
            with self.assertRaisesRegex(RuntimeError, "Object Lock is not enabled"):
                worm.validate_bucket("hso-evidence")

    def test_put_requires_compliance_mode_and_verified_retention_and_download_digest(self):
        payload = b"immutable evidence bundle"
        digest = hashlib.sha256(payload).hexdigest()
        future = (datetime.now(timezone.utc) + timedelta(days=400)).isoformat().replace("+00:00", "Z")
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "evidence.tar.gz"
            source.write_bytes(payload)

            def fake_aws(*args):
                command = args[0]
                if command == "put-object":
                    return {"VersionId": "version-123"}
                if command == "head-object":
                    return {
                        "ObjectLockMode": "COMPLIANCE",
                        "ObjectLockRetainUntilDate": future,
                        "Metadata": {"hso-sha256": digest},
                        "ContentLength": len(payload),
                    }
                if command == "get-object":
                    Path(args[-1]).write_bytes(payload)
                    return {}
                raise AssertionError(f"Unexpected AWS command: {command}")

            with patch.object(worm, "aws_json", side_effect=fake_aws):
                receipt = worm.put_and_readback(
                    "hso-evidence", "hso/p0/test/evidence.tar.gz", source, digest, 365
                )
            self.assertEqual(receipt["version_id"], "version-123")
            self.assertEqual(receipt["object_lock_mode"], "COMPLIANCE")
            self.assertEqual(receipt["readback_sha256"], digest)
            self.assertTrue(receipt["verified"])

    def test_put_rejects_shortened_or_missing_compliance_retention(self):
        payload = b"evidence"
        digest = hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "evidence.bin"
            source.write_bytes(payload)
            def fake_aws(*args):
                if args[0] == "put-object":
                    return {"VersionId": "version-123"}
                if args[0] == "head-object":
                    return {
                        "ObjectLockMode": "COMPLIANCE",
                        "ObjectLockRetainUntilDate": "2026-12-01T00:00:00Z",
                        "Metadata": {"hso-sha256": digest},
                        "ContentLength": len(payload),
                    }
                raise AssertionError(f"Unexpected AWS command: {args[0]}")
            with patch.object(worm, "aws_json", side_effect=fake_aws):
                with self.assertRaisesRegex(RuntimeError, "shorter than the requested"):
                    worm.put_and_readback("hso-evidence", "key", source, digest, 365)


if __name__ == "__main__":
    unittest.main()
