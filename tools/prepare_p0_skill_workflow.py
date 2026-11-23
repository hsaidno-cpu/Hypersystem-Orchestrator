#!/usr/bin/env python3
"""Bind the short-lived owner approval to the one fixed P0 workflow request."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from tools import remote_mcp_responses_adapter as adapter
except ImportError:
    import remote_mcp_responses_adapter as adapter

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "examples" / "hso-p0-skill-invocation-request.json"
ACTOR = "hsaidno-cpu"
CASE_ID = "HSO-P0-SKILL-ANALYZER-001"
ACTION_ID = "plugin.skill.invoke.remote-mcp.skill-analyzer"
TARGET = "artifacts/p0-skill-analyzer-invocation.json"


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approval-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    actor = os.environ.get("GITHUB_ACTOR", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    secret = os.environ.get("HSO_APPROVAL_HMAC_KEY", "").strip()
    if actor != ACTOR or not run_id or attempt != "1":
        raise SystemExit("P0 preparation requires authorized actor and first workflow attempt")
    if len(secret) < 32:
        raise SystemExit("HSO_APPROVAL_HMAC_KEY is unavailable or too short")
    if not TEMPLATE.is_file() or TEMPLATE.is_symlink():
        raise SystemExit("fixed P0 workflow template is missing or unsafe")
    if not args.approval_receipt.is_file() or args.approval_receipt.is_symlink():
        raise SystemExit("approval receipt is missing or unsafe")

    workflow = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    approval = json.loads(args.approval_receipt.read_text(encoding="utf-8"))
    source = adapter.inspect_local_skill_source(ROOT)
    server_url = adapter._require_https_public_url(
        os.environ.get("MCP_SERVER_URL", ""), expected_path="/mcp"
    )
    expected_base = {
        "case_id": CASE_ID,
        "action_id": ACTION_ID,
        "target_path": TARGET,
        "authority": "S4",
        "approver": actor,
        "workflow_run_id": run_id,
        "workflow_run_attempt": attempt,
        "host": adapter.HOST_ID,
        "mcp_server_label": adapter.SERVER_LABEL,
        "mcp_tool_name": adapter.TOOL_NAME,
        "mcp_server_url_sha256": hashlib.sha256(server_url.encode("utf-8")).hexdigest(),
        "plugin_source_commit": source["source_commit"],
        "skill_sha256": source["skill_sha256"],
    }
    packages = workflow.get("work_packages", [])
    if workflow.get("case_id") != CASE_ID or len(packages) != 1:
        raise SystemExit("P0 template must contain exactly one package for the canonical case")
    package = packages[0]
    if package.get("task_type") != "plugin.skill_analyzer_p0_pilot" or package.get("action_id") != ACTION_ID:
        raise SystemExit("P0 template route/action mismatch")
    payload = dict(package.get("input", {}))
    payload["skill_sha256"] = source["skill_sha256"]
    arguments = adapter._expected_arguments(payload)
    expected_base["tool_arguments_sha256"] = adapter.sha256_json(arguments)

    for key, expected in expected_base.items():
        if approval.get(key) != expected:
            raise SystemExit(f"approval receipt mismatch on {key}")
    signature = approval.get("signature")
    unsigned = {key: value for key, value in approval.items() if key != "signature"}
    expected_signature = hmac.new(secret.encode(), canonical_json(unsigned).encode("utf-8"), hashlib.sha256).hexdigest()
    if not isinstance(signature, str) or not hmac.compare_digest(signature, expected_signature):
        raise SystemExit("approval receipt signature is invalid")
    try:
        issued = datetime.fromisoformat(str(approval["issued_at"]).replace("Z", "+00:00"))
        expiry = datetime.fromisoformat(str(approval["expires_at"]).replace("Z", "+00:00"))
    except (KeyError, ValueError):
        raise SystemExit("approval receipt time window is missing or invalid")
    now = datetime.now(timezone.utc)
    if issued.tzinfo is None or expiry.tzinfo is None or issued > now or expiry <= now:
        raise SystemExit("approval receipt is expired or has invalid timezone/order")
    if (expiry - issued).total_seconds() > 300:
        raise SystemExit("approval validity window exceeds the five-minute P0 policy")

    package["input"] = payload
    package["idempotency_key"] = f"hso-p0-skill-analyzer-{run_id}"
    package["approval_receipt"] = approval
    workflow["requested_by"] = actor

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("prepared workflow output exists; refusing overwrite")
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(json.dumps(workflow, ensure_ascii=False, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())

    print(json.dumps({
        "workflow_prepared": True,
        "case_id": CASE_ID,
        "package_id": package["package_id"],
        "idempotency_key": package["idempotency_key"],
        "mcp_tool_name": adapter.TOOL_NAME,
        "tool_arguments_sha256": expected_base["tool_arguments_sha256"],
        "nonce_sha256": hashlib.sha256(approval["nonce"].encode()).hexdigest(),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
