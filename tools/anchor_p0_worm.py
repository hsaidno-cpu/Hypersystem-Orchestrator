#!/usr/bin/env python3
"""Preflight and anchor P0 evidence in AWS S3 Object Lock COMPLIANCE mode."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tarfile
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def aws_json(*args: str) -> dict:
    result = subprocess.run(
        ["aws", "s3api", *args, "--output", "json"],
        capture_output=True, text=True, timeout=90, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"AWS S3 API call failed ({result.returncode}): {result.stderr[-1200:]}")
    try:
        value = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        raise RuntimeError("AWS S3 API returned malformed JSON") from None
    if not isinstance(value, dict):
        raise RuntimeError("AWS S3 API response is not an object")
    return value


def config() -> tuple[str, int]:
    bucket = os.environ.get("HSO_P0_WORM_BUCKET", "").strip()
    retention = int(os.environ.get("HSO_P0_WORM_RETENTION_DAYS", "365"))
    if not bucket or not (365 <= retention <= 3650):
        raise RuntimeError("WORM bucket or retention configuration is missing/invalid (365-3650 days required)")
    return bucket, retention


def validate_bucket(bucket: str) -> dict:
    lock = aws_json("get-object-lock-configuration", "--bucket", bucket)
    if (lock.get("ObjectLockConfiguration") or {}).get("ObjectLockEnabled") != "Enabled":
        raise RuntimeError("S3 bucket Object Lock is not enabled")
    versioning = aws_json("get-bucket-versioning", "--bucket", bucket)
    if versioning.get("Status") != "Enabled":
        raise RuntimeError("S3 bucket versioning must be Enabled for Object Lock")
    return {"object_lock_enabled": True, "versioning_enabled": True}


def put_and_readback(bucket: str, key: str, body: Path, digest: str, retention_days: int) -> dict:
    retain_until = datetime.now(timezone.utc) + timedelta(days=retention_days)
    retain_value = retain_until.isoformat(timespec="seconds").replace("+00:00", "Z")
    put = aws_json(
        "put-object",
        "--bucket", bucket,
        "--key", key,
        "--body", str(body),
        "--object-lock-mode", "COMPLIANCE",
        "--object-lock-retain-until-date", retain_value,
        "--checksum-algorithm", "SHA256",
        "--server-side-encryption", "AES256",
        "--metadata", f"hso-sha256={digest}",
    )
    version_id = put.get("VersionId")
    if not version_id:
        raise RuntimeError("WORM PUT did not return an immutable object version ID")
    head = aws_json(
        "head-object",
        "--bucket", bucket,
        "--key", key,
        "--version-id", str(version_id),
        "--checksum-mode", "ENABLED",
    )
    if head.get("ObjectLockMode") != "COMPLIANCE":
        raise RuntimeError("S3 read-back does not confirm COMPLIANCE retention mode")
    actual_retain_until = head.get("ObjectLockRetainUntilDate")
    if not actual_retain_until:
        raise RuntimeError("S3 read-back does not expose the COMPLIANCE retain-until timestamp")
    try:
        actual_retention = datetime.fromisoformat(str(actual_retain_until).replace("Z", "+00:00"))
    except ValueError:
        raise RuntimeError("S3 returned an invalid retain-until timestamp") from None
    if actual_retention.tzinfo is None or actual_retention < retain_until:
        raise RuntimeError("S3 COMPLIANCE retention is shorter than the requested policy")
    if (head.get("Metadata") or {}).get("hso-sha256") != digest:
        raise RuntimeError("S3 read-back metadata digest mismatch")
    if int(head.get("ContentLength", -1)) != body.stat().st_size:
        raise RuntimeError("S3 read-back content length mismatch")
    with tempfile.TemporaryDirectory(prefix="hso-p0-worm-readback-") as tmp:
        recovered = Path(tmp) / body.name
        aws_json(
            "get-object",
            "--bucket", bucket,
            "--key", key,
            "--version-id", str(version_id),
            "--checksum-mode", "ENABLED",
            str(recovered),
        )
        readback_digest = sha256(recovered)
    if readback_digest != digest:
        raise RuntimeError("WORM object read-back SHA-256 does not match source artifact")
    return {
        "bucket": bucket,
        "key": key,
        "version_id": version_id,
        "object_lock_mode": head.get("ObjectLockMode"),
        "retain_until": head.get("ObjectLockRetainUntilDate"),
        "sha256": digest,
        "size_bytes": body.stat().st_size,
        "readback_sha256": readback_digest,
        "verified": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--verification", type=Path, default=Path("/tmp/hso-p0-verified-artifact.json"))
    parser.add_argument("--artifact", type=Path, default=Path("artifacts/p0-skill-analyzer-invocation.json"))
    parser.add_argument("--runtime-receipt", type=Path, default=Path("/tmp/hso-p0-run-receipt.json"))
    parser.add_argument("--audit", type=Path, default=Path("/tmp/hso-p0-audit.jsonl"))
    parser.add_argument("--approval", type=Path, default=Path("/tmp/hso-p0-approval.json"))
    parser.add_argument("--environment-approval", type=Path, default=Path("/tmp/hso-p0-environment-approval.json"))
    parser.add_argument("--output", type=Path, default=Path("/tmp/hso-p0-worm-anchor.json"))
    args = parser.parse_args()

    bucket, retention = config()
    bucket_state = validate_bucket(bucket)
    repository = os.environ.get("GITHUB_REPOSITORY", "local/unknown")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    prefix = f"hso/p0/{repository}/{run_id}"
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    if args.preflight_only:
        with tempfile.TemporaryDirectory(prefix="hso-p0-worm-preflight-") as tmp:
            probe = Path(tmp) / "worm-preflight.txt"
            probe.write_text(f"HSO P0 WORM preflight {repository} {run_id} {uuid.uuid4().hex}\n", encoding="utf-8")
            digest = sha256(probe)
            key = f"{prefix}/preflight-{digest}.txt"
            anchored = put_and_readback(bucket, key, probe, digest, retention)
        report = {
            "schema_version": "1.0.0",
            "status": "PREFLIGHT_VERIFIED",
            "provider": "AWS_S3_OBJECT_LOCK",
            "observed_at": now,
            "retention_days": retention,
            "bucket_state": bucket_state,
            "preflight_marker": anchored,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit("P0 WORM preflight report already exists; refusing overwrite")
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(report, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    else:
        evidence_paths = [
            args.verification, args.artifact, args.runtime_receipt,
            args.audit, args.approval, args.environment_approval,
            Path("/tmp/hso-p0-worm-preflight.json"),
        ]
        missing = [str(p) for p in evidence_paths if not p.is_file() or p.is_symlink()]
        if missing:
            raise SystemExit("P0 WORM anchor is missing required evidence files: " + ", ".join(missing))
        args.workspace.mkdir(parents=True, exist_ok=True)
        bundle = args.output.with_suffix(".tar.gz")
        if bundle.exists() or bundle.is_symlink():
            raise SystemExit("P0 WORM bundle already exists; refusing overwrite")
        with tarfile.open(bundle, "w:gz") as archive:
            for path in evidence_paths:
                arcname = path.name
                archive.add(path, arcname=arcname, recursive=False)
        digest = sha256(bundle)
        key = f"{prefix}/evidence-{digest}.tar.gz"
        anchored_bundle = put_and_readback(bucket, key, bundle, digest, retention)
        report = {
            "schema_version": "1.0.0",
            "status": "ANCHORED_AND_READBACK_VERIFIED",
            "provider": "AWS_S3_OBJECT_LOCK",
            "observed_at": now,
            "retention_days": retention,
            "bucket_state": bucket_state,
            "bundle": anchored_bundle,
        }
        anchor_file = args.output
        anchor_file.parent.mkdir(parents=True, exist_ok=True)
        if anchor_file.exists() or anchor_file.is_symlink():
            raise SystemExit("P0 WORM anchor record already exists; refusing overwrite")
        fd = os.open(anchor_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(report, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        anchor_digest = sha256(anchor_file)
        anchor_key = f"{prefix}/anchor-{anchor_digest}.json"
        report["anchor_manifest"] = put_and_readback(bucket, anchor_key, anchor_file, anchor_digest, retention)
        # The manifest object in S3 stores bundle version/digest/retention. The local report adds its own
        # immutable object reference for downstream reporting; it is not substituted for S3 read-back.
        temp_final = anchor_file.with_suffix(".final.json")
        fd = os.open(temp_final, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(report, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        temp_final.replace(anchor_file)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        raise SystemExit(f"P0 WORM anchoring failed closed ({type(exc).__name__}): {exc}") from None
