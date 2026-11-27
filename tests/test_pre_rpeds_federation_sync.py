import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from pre_rpeds_federation_sync import canonical_json, extract_event, hso_signature


class PreRpedsFederationSyncTests(unittest.TestCase):
    def build_event(self):
        return {
            "event_id": "pre-release-event-0001",
            "event_type": "PRE_SHARED_DNA_RELEASE",
            "canonical_identity": "pre-rpeds-shared-roadmap-dna",
            "version": "0.1.6",
            "release_id": "pluginrel_6b0961f9dca08191a8af34dbb2e02881",
            "source_locator": "https://example.invalid/pre/0.1.6",
            "artifact_sha256": "a" * 64,
            "contract_version": "1.0.0",
            "compatibility_range": ">=0.1.0 <1.0.0",
            "release_channel": "stable",
            "capability_classes": ["SHARED_DNA"],
            "is_breaking": False,
            "issuer": {"identity": "pre-publisher", "key_id": "test", "signature": "s" * 24},
            "issued_at": "2026-11-27T00:00:00Z",
            "idempotency_key": "pre-idempotency-key-0001",
        }

    def test_extract_repository_dispatch_event(self):
        event = self.build_event()
        self.assertEqual(extract_event({"client_payload": {"release_event": event}}), event)

    def test_extract_workflow_dispatch_json(self):
        event = self.build_event()
        self.assertEqual(extract_event({"inputs": {"release_event_json": json.dumps(event)}}), event)

    def test_signed_body_is_deterministic(self):
        body = canonical_json({"event_id": "evt-1", "version": "0.1.6"})
        self.assertEqual(hso_signature("test-secret", body), hso_signature("test-secret", body))
        self.assertTrue(hso_signature("test-secret", body).startswith("sha256="))


if __name__ == "__main__":
    unittest.main()
