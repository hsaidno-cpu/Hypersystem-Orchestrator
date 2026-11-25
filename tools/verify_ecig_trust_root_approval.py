#!/usr/bin/env python3
"""Fail-closed GOV-01 exact-head approval gate for ECIG trust-root changes.

This script is executed only from the trusted default branch by a
pull_request_target / issue_comment workflow. It never checks out or executes
PR-head code. It uses GitHub read-only APIs and never logs credentials.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

OWNER = "hsaidno-cpu"
REPOSITORY = "Hypersystem-Orchestrator"
GOV01_LOGIN = "hsaidno-cpu"
TRUST_STORE_PATH = "governance/ecig-trusted-public-keys.json"
API_VERSION = "2022-11-28"


class GateError(RuntimeError):
    pass


def github_json(url: str, token: str) -> tuple[Any, dict[str, str]]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "HSO-ECIG-GOV01-Trust-Root-Gate",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
            headers = {key.lower(): value for key, value in response.headers.items()}
            return payload, headers
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None, {}
        raise GateError(f"GitHub API returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        raise GateError("GitHub API request failed or returned invalid JSON") from None


def api_root(repository: str) -> str:
    return f"https://api.github.com/repos/{repository}"


def decode_content(payload: Any) -> dict[str, Any]:
    if payload is None:
        return {"schema_version": "1.0.0", "algorithm": "Ed25519", "keys": []}
    if not isinstance(payload, dict) or payload.get("encoding") != "base64":
        raise GateError("Trust-store content response is malformed")
    try:
        raw = base64.b64decode(payload["content"], validate=False)
        parsed = json.loads(raw.decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise GateError("Trust-store JSON cannot be decoded") from None
    if not isinstance(parsed, dict):
        raise GateError("Trust-store root must be a JSON object")
    if parsed.get("algorithm") != "Ed25519" or not isinstance(parsed.get("keys"), list):
        raise GateError("Trust-store identity or keys array is invalid")
    return parsed


def active_key_map(registry: dict[str, Any]) -> dict[str, str]:
    active: dict[str, str] = {}
    seen: set[str] = set()
    for entry in registry["keys"]:
        if not isinstance(entry, dict):
            raise GateError("Trust-store contains a non-object key entry")
        key_id = entry.get("key_id")
        status = entry.get("status")
        public_key = entry.get("public_key_base64")
        if not isinstance(key_id, str) or not key_id or key_id in seen:
            raise GateError("Trust-store key IDs must be non-empty and unique")
        seen.add(key_id)
        if status not in {"ACTIVE", "REVOKED"}:
            raise GateError(f"Trust-store key {key_id} has an invalid status")
        if status == "ACTIVE":
            if not isinstance(public_key, str):
                raise GateError(f"Active trust-store key {key_id} has no public key")
            try:
                decoded = base64.b64decode(public_key, validate=True)
            except ValueError:
                raise GateError(f"Active trust-store key {key_id} is not valid base64") from None
            if len(decoded) != 32 or base64.b64encode(decoded).decode("ascii") != public_key:
                raise GateError(f"Active trust-store key {key_id} is not a canonical Ed25519 public key")
            active[key_id] = public_key
    return active


def get_file_at_ref(repository: str, path: str, ref: str, token: str) -> dict[str, Any]:
    url = f"{api_root(repository)}/contents/{path}?ref={ref}"
    payload, _ = github_json(url, token)
    return decode_content(payload)


def exact_owner_approval(comments: list[dict[str, Any]], head_sha: str) -> dict[str, Any] | None:
    expected = f"APPROVE TRUST ROOT {head_sha}"
    matches = [
        comment for comment in comments
        if isinstance(comment, dict)
        and comment.get("body", "").strip() == expected
        and (comment.get("user") or {}).get("login") == GOV01_LOGIN
    ]
    if not matches:
        return None
    # A duplicate exact approval is harmless; choose the earliest matching receipt
    # to keep one stable audit reference.
    return sorted(matches, key=lambda item: (item.get("created_at") or "", item.get("id") or 0))[0]


def check_trust_root_change(repository: str, pr_number: int, token: str) -> dict[str, Any]:
    if repository != f"{OWNER}/{REPOSITORY}":
        raise GateError("Repository is outside the HSO allowlist")
    pr, _ = github_json(f"{api_root(repository)}/pulls/{pr_number}", token)
    if not isinstance(pr, dict):
        raise GateError("Pull request could not be read")
    if pr.get("state") != "open":
        raise GateError("Trust-root approval gate only accepts open pull requests")
    base = pr.get("base") or {}
    head = pr.get("head") or {}
    base_repo = (base.get("repo") or {}).get("full_name")
    head_repo = (head.get("repo") or {}).get("full_name")
    base_sha = base.get("sha")
    head_sha = head.get("sha")
    if base_repo != repository or head_repo != repository:
        raise GateError("Trust-root changes from forks or cross-repository heads are not accepted")
    if not isinstance(base_sha, str) or len(base_sha) != 40 or not isinstance(head_sha, str) or len(head_sha) != 40:
        raise GateError("Pull request base/head SHA is missing or malformed")

    before = get_file_at_ref(repository, TRUST_STORE_PATH, base_sha, token)
    after = get_file_at_ref(repository, TRUST_STORE_PATH, head_sha, token)
    before_active = active_key_map(before)
    after_active = active_key_map(after)
    changed = before_active != after_active

    result = {
        "repository": repository,
        "pr_number": pr_number,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "trust_store_path": TRUST_STORE_PATH,
        "active_key_set_changed": changed,
        "human_decision_authority": "GOV-01",
        "additional_human_approvers": 0,
    }
    if not changed:
        result["decision"] = "NOT_REQUIRED"
        result["reason"] = "The active trusted-key set is unchanged."
        return result

    comments_payload, _ = github_json(
        f"{api_root(repository)}/issues/{pr_number}/comments?per_page=100&page=1",
        token,
    )
    if not isinstance(comments_payload, list):
        raise GateError("PR conversation comments could not be read completely")
    # Fail closed if the first page is full; this workflow deliberately avoids
    # partial pagination ambiguity by requiring a complete single-page result.
    if len(comments_payload) >= 100:
        raise GateError("PR has 100 or more comments; exact-head approval pagination is required")
    approval = exact_owner_approval(comments_payload, head_sha)
    if approval is None:
        result["decision"] = "PENDING"
        result["required_comment"] = f"APPROVE TRUST ROOT {head_sha}"
        raise GateError(
            "Active trust-root change requires the exact GOV-01 comment: "
            f"APPROVE TRUST ROOT {head_sha}"
        )
    result["decision"] = "APPROVED"
    result["approval_comment_id"] = approval.get("id")
    result["approval_author"] = (approval.get("user") or {}).get("login")
    result["approval_created_at"] = approval.get("created_at")
    result["approval_url"] = approval.get("html_url")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("ERROR: GITHUB_TOKEN is not configured", file=sys.stderr)
        return 2
    try:
        result = check_trust_root_change(args.repository, args.pr_number, token)
    except GateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
