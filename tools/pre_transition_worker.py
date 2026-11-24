#!/usr/bin/env python3
"""Scheduled PRE transition-queue evaluator for a persistent self-hosted runner.

This worker evaluates PENDING rows and writes decision receipts back to the
PRE Transition Queue. It deliberately does not update the canonical Work Item
PRE Stage property. Stage application requires a separately authorized adapter
and an access model that prevents ungoverned direct edits.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.pre_policy_engine import (
    NonceStore,
    PREPolicyError,
    canonical_json,
    digest_json,
    evaluate_transition,
    load_policy,
)

API_ROOT = "https://api.notion.com/v1"
API_VERSION = "2025-09-03"
DEFAULT_POLICY = Path(__file__).resolve().parents[1] / "governance" / "pre-r0-r9-policy.json"


class NotionWorkerError(RuntimeError):
    pass


def rich_text_value(prop: dict[str, Any] | None) -> str:
    if not isinstance(prop, dict):
        return ""
    chunks = prop.get("rich_text") or prop.get("title") or []
    return "".join(
        item.get("plain_text")
        or (item.get("text") or {}).get("content", "")
        for item in chunks if isinstance(item, dict)
    )


def select_value(prop: dict[str, Any] | None) -> str:
    if not isinstance(prop, dict):
        return ""
    selected = prop.get("select") or prop.get("status") or {}
    return selected.get("name", "") if isinstance(selected, dict) else ""


def rich_text_chunks(value: str, limit: int = 1800) -> list[dict[str, Any]]:
    if not value:
        return []
    return [
        {"type": "text", "text": {"content": value[index:index + limit]}}
        for index in range(0, len(value), limit)
    ]


def stage_id(value: str) -> str:
    """Convert a Notion display label such as 'R0 Intake' to canonical 'R0'."""
    if not isinstance(value, str):
        return ""
    candidate = value.strip().split(maxsplit=1)[0] if value.strip() else ""
    if len(candidate) == 2 and candidate[0] == "R" and candidate[1].isdigit():
        return candidate
    return value.strip()


def parse_json_list(raw: str, label: str) -> list[dict[str, Any]]:
    if not raw.strip():
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise NotionWorkerError(f"{label}_JSON_INVALID:{exc.msg}") from None
    if not isinstance(parsed, list):
        raise NotionWorkerError(f"{label}_MUST_BE_JSON_ARRAY")
    return parsed


class NotionAPI:
    def __init__(
        self, token: str, data_source_id: str, *,
        opener: Any = urllib.request.urlopen, sleeper: Any = time.sleep,
        timeout: int = 25,
    ):
        if not token:
            raise NotionWorkerError("HSO_PRE_NOTION_API_KEY is not configured")
        if not data_source_id:
            raise NotionWorkerError("HSO_PRE_NOTION_DATA_SOURCE_ID is not configured")
        self.token = token
        self.data_source_id = data_source_id
        self.opener = opener
        self.sleeper = sleeper
        self.timeout = timeout

    def request(
        self, method: str, path: str,
        payload: dict[str, Any] | None = None, *,
        retry_safe: bool = False,
    ) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": API_VERSION,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = API_ROOT + path
        attempts = 3 if retry_safe else 1
        for attempt in range(attempts):
            request = urllib.request.Request(url, data=body, headers=headers, method=method)
            try:
                with self.opener(request, timeout=self.timeout) as response:
                    raw = response.read()
                try:
                    return json.loads(raw.decode("utf-8")) if raw else {}
                except (UnicodeDecodeError, json.JSONDecodeError):
                    raise NotionWorkerError("NOTION_RESPONSE_INVALID_JSON") from None
            except urllib.error.HTTPError as exc:
                retryable = exc.code == 429 or exc.code >= 500
                if retry_safe and retryable and attempt < attempts - 1:
                    try:
                        delay = min(10.0, max(0.5, float(exc.headers.get("Retry-After", "2"))))
                    except (TypeError, ValueError):
                        delay = 2.0
                    self.sleeper(delay)
                    continue
                raise NotionWorkerError(f"NOTION_HTTP_{exc.code}") from None
            except (urllib.error.URLError, TimeoutError, OSError):
                if retry_safe and attempt < attempts - 1:
                    self.sleeper(min(2 ** attempt, 5))
                    continue
                raise NotionWorkerError("NOTION_TRANSPORT_ERROR") from None
        raise NotionWorkerError("NOTION_REQUEST_RETRIES_EXHAUSTED")

    def query_pending(self) -> list[dict[str, Any]]:
        pages: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            body: dict[str, Any] = {
                "page_size": 100,
                "filter": {
                    "or": [
                        {
                            "property": "Request State",
                            "select": {"equals": "PENDING"},
                        },
                        {
                            "property": "Request State",
                            "select": {"equals": "EVALUATING"},
                        },
                    ]
                },
            }
            if cursor:
                body["start_cursor"] = cursor
            result = self.request(
                "POST", f"/data_sources/{self.data_source_id}/query",
                body, retry_safe=True,
            )
            batch = result.get("results", [])
            if not isinstance(batch, list):
                raise NotionWorkerError("NOTION_QUERY_RESULTS_INVALID")
            pages.extend(batch)
            if not result.get("has_more"):
                break
            cursor = result.get("next_cursor")
            if not cursor:
                raise NotionWorkerError("NOTION_QUERY_CURSOR_MISSING")
        return pages

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request(
            "PATCH", f"/pages/{urllib.parse.quote(page_id)}",
            {"properties": properties}, retry_safe=True,
        )

    def get_page(self, page_id: str) -> dict[str, Any]:
        return self.request(
            "GET", f"/pages/{urllib.parse.quote(page_id)}", retry_safe=True,
        )


def request_from_page(page: dict[str, Any]) -> dict[str, Any]:
    props = page.get("properties") or {}
    page_id = page.get("id", "")
    idempotency_key = rich_text_value(props.get("Idempotency Key"))
    request_id = idempotency_key or f"notion-page:{page_id}"
    evidence = parse_json_list(
        rich_text_value(props.get("Evidence Envelope JSON")), "EVIDENCE_ENVELOPE"
    )
    approvals = parse_json_list(
        rich_text_value(props.get("Approval Receipt JSON")), "APPROVAL_RECEIPT"
    )
    return {
        "request_id": request_id,
        "project_id": rich_text_value(props.get("Project ID")),
        "scope_id": rich_text_value(props.get("Scope ID")),
        "from_stage": stage_id(select_value(props.get("From Stage"))),
        "to_stage": stage_id(select_value(props.get("Requested Stage"))),
        "requested_by_actor_id": rich_text_value(props.get("Requested By Actor ID")),
        "evidence": evidence,
        "approvals": approvals,
        "source_commit": rich_text_value(props.get("Source Commit")),
        "source_event": (props.get("Source Event") or {}).get("url"),
        "notion_page_id": page_id,
    }


def malformed_result(page: dict[str, Any], error: str, policy: dict[str, Any]) -> dict[str, Any]:
    """Deterministic DENY receipt for invalid queue JSON; never silently skip."""
    props = page.get("properties") or {}
    inputs = {
        "page_id": page.get("id"),
        "evidence_raw": rich_text_value(props.get("Evidence Envelope JSON")),
        "approval_raw": rich_text_value(props.get("Approval Receipt JSON")),
        "from_stage": select_value(props.get("From Stage")),
        "to_stage": select_value(props.get("Requested Stage")),
    }
    result: dict[str, Any] = {
        "decision": "DENY",
        "gate_state": "FAIL",
        "request_id": rich_text_value(props.get("Idempotency Key")) or f"notion-page:{page.get('id')}",
        "policy_id": policy["policy_id"],
        "policy_version": policy["version"],
        "input_digest": digest_json(inputs),
        "required_evidence_types": [],
        "required_approval_roles": [],
        "verified_approval_ids": [],
        "blockers": [],
        "reasons": [error],
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "stage_mutation_performed": False,
        "next_action": "REPAIR_REQUEST_AND_SUBMIT_AGAIN",
    }
    result["evaluation_digest"] = digest_json(result)
    return result


def result_properties(result: dict[str, Any], correlation_id: str) -> dict[str, Any]:
    decision = result["decision"]
    request_state = {
        "ALLOW": "POLICY_PASSED",
        "HOLD": "HOLD",
        "DENY": "REJECTED",
    }[decision]
    details = {
        "blockers": result.get("blockers", []),
        "reasons": result.get("reasons", []),
        "next_action": result.get("next_action"),
    }
    return {
        "Gate Decision": {"select": {"name": decision}},
        "Request State": {"select": {"name": request_state}},
        "Evaluation Digest": {"rich_text": rich_text_chunks(result["evaluation_digest"])},
        "Evaluation Receipt JSON": {"rich_text": rich_text_chunks(canonical_json(result))},
        "Block Reasons": {"rich_text": rich_text_chunks(canonical_json(details))},
        "Evaluated At": {"date": {"start": result["evaluated_at"]}},
        "Correlation ID": {"rich_text": rich_text_chunks(correlation_id)},
    }


def read_back_matches(page: dict[str, Any], result: dict[str, Any]) -> bool:
    props = page.get("properties") or {}
    return (
        select_value(props.get("Gate Decision")) == result["decision"]
        and rich_text_value(props.get("Evaluation Digest")) == result["evaluation_digest"]
        and select_value(props.get("Request State")) == {
            "ALLOW": "POLICY_PASSED", "HOLD": "HOLD", "DENY": "REJECTED"
        }[result["decision"]]
    )


def process_page(
    page: dict[str, Any], client: NotionAPI, policy: dict[str, Any],
    approval_secret: str | None, nonce_store: NonceStore,
    evidence_secret: str | None = None,
) -> dict[str, Any]:
    page_id = page.get("id")
    if not isinstance(page_id, str) or not page_id:
        raise NotionWorkerError("PENDING_ROW_HAS_NO_PAGE_ID")
    correlation_id = (
        rich_text_value((page.get("properties") or {}).get("Correlation ID"))
        or f"pre:{page_id}"
    )
    # Claim the queue item before consuming any single-use approval nonce.
    # A crash leaves EVALUATING, which the next poll can safely resume.
    client.update_page(page_id, {
        "Request State": {"select": {"name": "EVALUATING"}},
        "Correlation ID": {"rich_text": rich_text_chunks(correlation_id)},
    })
    claimed_page = client.get_page(page_id)
    if select_value((claimed_page.get("properties") or {}).get("Request State")) != "EVALUATING":
        raise NotionWorkerError(f"CLAIM_READ_BACK_MISMATCH:{page_id}")

    try:
        request = request_from_page(claimed_page)
        result = evaluate_transition(
            request, policy, approval_secret=approval_secret,
            evidence_secret=evidence_secret, nonce_store=nonce_store,
        )
    except NotionWorkerError as exc:
        result = malformed_result(claimed_page, str(exc), policy)

    client.update_page(page_id, result_properties(result, correlation_id))
    verified_page = client.get_page(page_id)
    if not read_back_matches(verified_page, result):
        raise NotionWorkerError(
            f"READ_BACK_MISMATCH:{page_id}:{result['evaluation_digest']}"
        )
    return {
        "page_id": page_id,
        "request_id": result["request_id"],
        "decision": result["decision"],
        "gate_state": result["gate_state"],
        "evaluation_digest": result["evaluation_digest"],
        "read_back_verified": True,
        "stage_mutation_performed": False,
    }


def run_once(
    client: NotionAPI, policy: dict[str, Any], approval_secret: str | None,
    nonce_store: NonceStore, evidence_secret: str | None = None,
) -> dict[str, Any]:
    pages = client.query_pending()
    results: list[dict[str, Any]] = []
    for page in pages:
        results.append(process_page(
            page, client, policy, approval_secret, nonce_store,
            evidence_secret=evidence_secret,
        ))
    return {
        "service": "hso.pre.r0-r9",
        "policy_version": policy["version"],
        "queried_pending": len(pages),
        "processed": len(results),
        "results": results,
        "stage_mutations_performed": 0,
        "completed_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Process pending HSO PRE transition requests")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--nonce-store", type=Path, default=Path(
        os.environ.get("HSO_PRE_NONCE_STORE_PATH", "/var/lib/hso/pre/approval-nonces.sqlite")
    ))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = load_policy(args.policy)
        token = os.environ.get("HSO_PRE_NOTION_API_KEY", "")
        data_source_id = os.environ.get(
            "HSO_PRE_NOTION_DATA_SOURCE_ID",
            "42299868-397f-819d-bb41-000b0d2a1886",
        )
        client = NotionAPI(token, data_source_id)
        approval_secret = os.environ.get(policy["approval"]["key_environment_variable"])
        evidence_secret = os.environ.get(policy["evidence"]["attestation"]["key_environment_variable"])
        nonce_store = NonceStore(args.nonce_store)
        if args.dry_run:
            pages = client.query_pending()
            print(json.dumps({
                "service": "hso.pre.r0-r9",
                "mode": "DRY_RUN",
                "pending_count": len(pages),
                "stage_mutations_performed": 0,
            }, indent=2))
            return 0
        result = run_once(client, policy, approval_secret, nonce_store, evidence_secret)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, PREPolicyError, NotionWorkerError) as exc:
        print(f"PRE_WORKER_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
