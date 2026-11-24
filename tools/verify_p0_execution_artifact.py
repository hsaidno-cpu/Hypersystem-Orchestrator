#!/usr/bin/env python3
"""Verify the signed P0 invocation receipt and independently hash the target artifact."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    raw = args.artifact.read_bytes()
    if len(raw) > 90_000:
        raise SystemExit("P0 artifact exceeds verification size limit")
    artifact = json.loads(raw.decode("utf-8"))
    receipt = artifact.get("invocation_receipt")
    result = artifact.get("analysis_result")
    if not isinstance(receipt, dict) or not isinstance(result, dict):
        raise SystemExit("P0 artifact has no invocation receipt and structured result")

    signature = receipt.get("signature")
    if not isinstance(signature, dict) or signature.get("algorithm") != "Ed25519":
        raise SystemExit("P0 invocation receipt is not Ed25519-signed")
    key_id = os.environ.get("HSO_P0_RECEIPT_ED25519_KEY_ID", "").strip()
    public_b64 = os.environ.get("HSO_P0_RECEIPT_ED25519_PUBLIC_KEY_B64", "").strip()
    if not key_id or signature.get("key_id") != key_id or not public_b64:
        raise SystemExit("P0 receipt signing key identity is unavailable or mismatched")
    try:
        public_raw = base64.b64decode(public_b64, validate=True)
        signature_raw = base64.b64decode(signature["signature_base64"], validate=True)
        unsigned = {key: value for key, value in receipt.items() if key != "signature"}
        signed_payload = canonical(unsigned)
        if signature.get("signed_payload_sha256") != sha256(signed_payload):
            raise ValueError("signed payload digest mismatch")
        Ed25519PublicKey.from_public_bytes(public_raw).verify(signature_raw, signed_payload)
    except Exception as exc:
        raise SystemExit(f"P0 execution receipt signature verification failed ({type(exc).__name__})") from None

    approval = receipt.get("approval") or {}
    if (
        approval.get("environment") != "hso-p0-remote-mcp-live"
        or approval.get("approval_source") != "github_actions_workflow_run_approvals_api"
        or not isinstance(approval.get("approver_github_id"), int)
        or not approval.get("approver")
        or approval.get("approver", "").lower() == str(approval.get("workflow_actor") or "").lower()
    ):
        raise SystemExit("P0 receipt has no independent authenticated Environment reviewer")

    output_text = result.get("result")
    if not isinstance(output_text, str):
        raise SystemExit("P0 tool result text is missing")
    result_digest = sha256(output_text.encode("utf-8"))
    if result_digest != receipt.get("gateway_result", {}).get("result_sha256"):
        raise SystemExit("P0 result digest does not match the signed receipt")
    if result_digest != receipt.get("independent_target_result_sha256"):
        raise SystemExit("Independent target result digest does not match the signed receipt")

    host_session = receipt.get("host_session") or {}
    if not all(host_session.get(key) for key in ("final_response_id", "mcp_call_id", "approval_request_id")):
        raise SystemExit("P0 receipt is missing host response, MCP call, or approval request identifiers")
    if receipt.get("status") != "SUCCEEDED" or host_session.get("host_tool_call_status") != "COMPLETED":
        raise SystemExit("P0 invocation receipt is not a completed host/tool invocation")

    report = {
        "schema_version": "1.0.0",
        "verified": True,
        "signature_algorithm": "Ed25519",
        "key_id": key_id,
        "signed_payload_sha256": signature["signed_payload_sha256"],
        "target_artifact_sha256": sha256(raw),
        "target_result_sha256": result_digest,
        "host_response_id": host_session["final_response_id"],
        "mcp_call_id": host_session["mcp_call_id"],
        "authenticated_approval_request_id": host_session["approval_request_id"],
        "environment_reviewer_login": approval["approver"],
        "environment_reviewer_id": approval["approver_github_id"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("P0 verification report already exists; refusing overwrite")
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
