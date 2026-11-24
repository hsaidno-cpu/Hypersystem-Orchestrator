#!/usr/bin/env python3
"""Resolve the authenticated GitHub Environment reviewer for this workflow run."""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ENVIRONMENT = "hso-p0-remote-mcp-live"


def api_get(url: str, token: str) -> object:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2026-03-10",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot retrieve GitHub Environment approval history ({type(exc).__name__})") from None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN", "").strip()
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    run_id = os.environ.get("GITHUB_RUN_ID", "").strip()
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1").strip()
    workflow_actor = os.environ.get("GITHUB_ACTOR", "").strip()
    workflow_actor_id_raw = os.environ.get("GITHUB_ACTOR_ID", "").strip()
    try:
        workflow_actor_id = int(workflow_actor_id_raw)
    except ValueError:
        workflow_actor_id = 0
    allowed_logins = {
        item.strip().lower()
        for item in os.environ.get("HSO_P0_ALLOWED_REVIEWER_LOGINS", "").split(",")
        if item.strip()
    }
    api_root = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    if not all((token, repository, run_id, workflow_actor, workflow_actor_id, allowed_logins)):
        raise SystemExit("P0 authenticated reviewer verification is missing required configuration")
    if run_attempt != "1":
        raise SystemExit("P0 only permits a first-attempt workflow run")

    encoded_environment = urllib.parse.quote(ENVIRONMENT, safe="")
    environment_url = f"{api_root}/repos/{repository}/environments/{encoded_environment}"
    run_approvals_url = f"{api_root}/repos/{repository}/actions/runs/{run_id}/approvals"
    environment = api_get(environment_url, token)
    if not isinstance(environment, dict):
        raise SystemExit("GitHub Environment configuration response is malformed")

    rules = environment.get("protection_rules", [])
    required_rules = [rule for rule in rules if rule.get("type") == "required_reviewers"]
    if len(required_rules) != 1:
        raise SystemExit("P0 Environment must have exactly one required-reviewers rule")
    reviewers = required_rules[0].get("reviewers", [])
    if required_rules[0].get("prevent_self_review") is not True:
        raise SystemExit("P0 Environment must prevent requester self-review")
    configured_users = {
        (item.get("reviewer") or {}).get("login", "").lower():
            (item.get("reviewer") or {}).get("id")
        for item in reviewers
        if item.get("type") == "User" and isinstance(item.get("reviewer"), dict)
    }
    if not configured_users or any(not isinstance(value, int) for value in configured_users.values()):
        raise SystemExit("P0 Environment must configure an individually identifiable User reviewer")
    if not set(configured_users).issubset(allowed_logins):
        raise SystemExit("Configured Environment reviewers must all be in HSO_P0_ALLOWED_REVIEWER_LOGINS")

    history = api_get(run_approvals_url, token)
    if not isinstance(history, list):
        raise SystemExit("GitHub workflow approval history is malformed")
    matching = []
    for item in history:
        if not isinstance(item, dict):
            continue
        environments = item.get("environments", [])
        if not any(isinstance(env, dict) and env.get("name") == ENVIRONMENT for env in environments):
            continue
        user = item.get("user")
        if isinstance(user, dict):
            matching.append((item, user))

    if not matching:
        raise SystemExit("GitHub API has no authenticated approval record for the P0 Environment")
    if len(matching) != 1:
        raise SystemExit("P0 requires exactly one Environment approval event for this workflow run")
    approval, user = matching[0]
    reviewer_login = str(user.get("login") or "").strip()
    reviewer_id = user.get("id")
    if approval.get("state") != "approved":
        raise SystemExit("The P0 Environment approval record is not approved")
    if not reviewer_login or not isinstance(reviewer_id, int):
        raise SystemExit("GitHub approval record does not expose a stable reviewer login and ID")
    if reviewer_login.lower() not in configured_users or reviewer_login.lower() not in allowed_logins:
        raise SystemExit("Authenticated approver is not an individually configured and allow-listed Environment reviewer")
    if configured_users[reviewer_login.lower()] != reviewer_id:
        raise SystemExit("Authenticated approver GitHub numeric ID does not match the configured Environment reviewer")
    if reviewer_login.lower() == workflow_actor.lower() or reviewer_id == workflow_actor_id:
        raise SystemExit("P0 workflow requester cannot approve their own invocation")

    record = {
        "schema_version": "1.0.0",
        "environment": ENVIRONMENT,
        "workflow_run_id": run_id,
        "workflow_run_attempt": run_attempt,
        "workflow_actor": workflow_actor,
        "workflow_actor_id": workflow_actor_id,
        "reviewer_login": reviewer_login,
        "reviewer_id": reviewer_id,
        "state": "approved",
        "approval_source": "github_actions_workflow_run_approvals_api",
        "api_url": run_approvals_url,
        "observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("Environment approval output already exists; refusing overwrite")
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(json.dumps(record, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({
        "environment": ENVIRONMENT,
        "workflow_run_id": run_id,
        "workflow_actor": workflow_actor,
        "workflow_actor_id": workflow_actor_id,
        "authenticated_reviewer_login": reviewer_login,
        "authenticated_reviewer_id": reviewer_id,
        "approval_verified": True,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
