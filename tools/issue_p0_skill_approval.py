#!/usr/bin/env python3
"""Issue a five-minute HMAC approval bound to one exact Remote MCP tool call."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from tools import remote_mcp_responses_adapter as adapter
except ImportError:
    import remote_mcp_responses_adapter as adapter

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "examples" / "hso-p0-skill-invocation-request.json"
CASE_ID = "HSO-P0-SKILL-ANALYZER-001"
ACTION_ID = "plugin.skill.invoke.remote-mcp.skill-analyzer"
TARGET_PATH = "artifacts/p0-skill-analyzer-invocation.json"
AUTHORITY = "S4"
AUTHORIZED_ACTOR = "hsaidno-cpu"


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment-approval", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    secret = os.environ.get("HSO_APPROVAL_HMAC_KEY", "").strip()
    actor = os.environ.get("GITHUB_ACTOR", "").strip()
    run_id = os.environ.get("GITHUB_RUN_ID", "").strip()
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1").strip()
    if len(secret) < 32:
        raise SystemExit("HSO_APPROVAL_HMAC_KEY must contain at least 32 high-entropy characters")
    if actor != AUTHORIZED_ACTOR:
        raise SystemExit("P0 approval is restricted to the repository owner workflow actor")
    if not run_id or attempt != "1":
        raise SystemExit("P0 approval requires a unique first-attempt workflow run")
    if not TEMPLATE.is_file() or TEMPLATE.is_symlink():
        raise SystemExit("fixed P0 request template is missing or unsafe")
    if not args.environment_approval.is_file() or args.environment_approval.is_symlink():
        raise SystemExit("authenticated Environment approval record is missing or unsafe")
    environment_approval = json.loads(args.environment_approval.read_text(encoding="utf-8"))
    approver = str(environment_approval.get("reviewer_login") or "").strip()
    reviewer_id = environment_approval.get("reviewer_id")
    workflow_actor_id = environment_approval.get("workflow_actor_id")
    allowed_logins = {
        item.strip().lower()
        for item in os.environ.get("HSO_P0_ALLOWED_REVIEWER_LOGINS", "").split(",")
        if item.strip()
    }
    if not allowed_logins or approver.lower() not in allowed_logins:
        raise SystemExit("authenticated Environment approver is not in HSO_P0_ALLOWED_REVIEWER_LOGINS")
    if (
        environment_approval.get("environment") != "hso-p0-remote-mcp-live"
        or environment_approval.get("workflow_run_id") != run_id
        or environment_approval.get("workflow_run_attempt") != attempt
        or environment_approval.get("workflow_actor") != actor
        or environment_approval.get("approval_source") != "github_actions_workflow_run_approvals_api"
        or not approver
        or not isinstance(reviewer_id, int)
        or not isinstance(workflow_actor_id, int)
        or reviewer_id == workflow_actor_id
        or approver.lower() == actor.lower()
    ):
        raise SystemExit("authenticated Environment approver is missing, mismatched, or not independent")

    server_url = adapter._require_https_public_url(
        os.environ.get("MCP_SERVER_URL", ""), expected_path="/mcp"
    )
    audience = os.environ.get("MCP_OIDC_AUDIENCE", "").strip()
    if audience.rstrip("/") != server_url.rstrip("/"):
        raise SystemExit("MCP_OIDC_AUDIENCE must exactly match MCP_SERVER_URL")

    workflow = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    packages = workflow.get("work_packages", [])
    if workflow.get("case_id") != CASE_ID or len(packages) != 1:
        raise SystemExit("P0 template case or one-package boundary is invalid")
    package = packages[0]
    if package.get("action_id") != ACTION_ID or package.get("target_path") != TARGET_PATH:
        raise SystemExit("P0 template action or artifact target is invalid")

    source = adapter.inspect_local_skill_source(ROOT)
    payload = dict(package["input"])
    payload["skill_sha256"] = source["skill_sha256"]
    arguments = adapter._expected_arguments(payload)
    now = datetime.now(timezone.utc)
    unsigned = {
        "case_id": CASE_ID,
        "action_id": ACTION_ID,
        "target_path": TARGET_PATH,
        "authority": AUTHORITY,
        "approver": approver,
        "environment_reviewer_id": reviewer_id,
        "workflow_actor": actor,
        "workflow_actor_id": workflow_actor_id,
        "environment": environment_approval["environment"],
        "approval_source": environment_approval["approval_source"],
        "environment_approval_observed_at": environment_approval.get("observed_at"),
        "issued_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "expires_at": (now + timedelta(minutes=5)).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "nonce": uuid.uuid4().hex,
        "workflow_run_id": run_id,
        "workflow_run_attempt": attempt,
        "host": adapter.HOST_ID,
        "mcp_server_label": adapter.SERVER_LABEL,
        "mcp_tool_name": adapter.TOOL_NAME,
        "mcp_server_url_sha256": hashlib.sha256(server_url.encode("utf-8")).hexdigest(),
        "tool_arguments_sha256": adapter.sha256_json(arguments),
        "plugin_source_commit": source["source_commit"],
        "skill_sha256": source["skill_sha256"],
    }
    signature = hmac.new(secret.encode(), canonical_json(unsigned).encode("utf-8"), hashlib.sha256).hexdigest()
    receipt = {**unsigned, "signature": signature}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("approval output already exists; refusing overwrite")
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())

    print(json.dumps({
        "approval_created": True,
        "case_id": CASE_ID,
        "action_id": ACTION_ID,
        "approver": approver,
        "workflow_actor": actor,
        "workflow_actor_id": workflow_actor_id,
        "environment_reviewer_id": reviewer_id,
        "workflow_run_id": run_id,
        "mcp_server_label": adapter.SERVER_LABEL,
        "mcp_tool_name": adapter.TOOL_NAME,
        "expires_at": unsigned["expires_at"],
        "tool_arguments_sha256": unsigned["tool_arguments_sha256"],
        "mcp_server_url_sha256": unsigned["mcp_server_url_sha256"],
        "skill_sha256": source["skill_sha256"],
        "nonce_sha256": hashlib.sha256(unsigned["nonce"].encode()).hexdigest(),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
