#!/usr/bin/env python3
"""Signed publisher/reconciliation client for the PRE–RPEDS HSO federation endpoint."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REQUIRED_EVENT_FIELDS = (
    "event_id", "event_type", "canonical_identity", "version", "release_id",
    "source_locator", "artifact_sha256", "contract_version", "compatibility_range",
    "release_channel", "capability_classes", "is_breaking", "issuer",
    "issued_at", "idempotency_key",
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def hso_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return "sha256=" + digest


def extract_event(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("event_type") == "PRE_SHARED_DNA_RELEASE":
        event = document
    elif isinstance(document.get("client_payload"), dict):
        event = document["client_payload"].get("release_event")
    elif isinstance(document.get("inputs"), dict):
        raw = document["inputs"].get("release_event_json", "")
        event = json.loads(raw) if raw else None
    else:
        event = None
    if not isinstance(event, dict):
        raise ValueError("release_event_json or client_payload.release_event is required")
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if missing:
        raise ValueError("missing release event fields: " + ", ".join(missing))
    if event["event_type"] != "PRE_SHARED_DNA_RELEASE":
        raise ValueError("unsupported event_type")
    if event["canonical_identity"] != "pre-rpeds-shared-roadmap-dna":
        raise ValueError("unexpected canonical_identity")
    if not isinstance(event["is_breaking"], bool):
        raise ValueError("is_breaking must be a JSON boolean")
    if not isinstance(event["issuer"], dict) or len(str(event["issuer"].get("signature", ""))) < 16:
        raise ValueError("issuer.signature is missing or too short")
    digest = str(event["artifact_sha256"])
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise ValueError("artifact_sha256 must be a lowercase SHA-256 hex digest")
    return event


def post(url: str, secret: str, payload: dict[str, Any]) -> tuple[int, str]:
    body = canonical_json(payload)
    request = urllib.request.Request(
        url,
        data=body,
        headers={"content-type": "application/json", "x-hso-signature": hso_signature(secret, body)},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("publish", "reconcile"))
    parser.add_argument("--event-file", default=os.environ.get("GITHUB_EVENT_PATH"))
    args = parser.parse_args()

    base_url = os.environ.get("PRE_FEDERATION_URL", "").strip().rstrip("/")
    secret = os.environ.get("HSO_SYNC_TOKEN", "")
    if not base_url or not secret:
        print("NOT_CONFIGURED: set PRE_FEDERATION_URL and HSO_SYNC_TOKEN in repository settings.", file=sys.stderr)
        return 2

    if args.mode == "publish":
        if not args.event_file:
            print("BLOCKED: GITHUB_EVENT_PATH or --event-file is required.", file=sys.stderr)
            return 2
        try:
            document = json.loads(Path(args.event_file).read_text(encoding="utf-8"))
            payload = extract_event(document)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print("INVALID_RELEASE_EVENT: " + str(error), file=sys.stderr)
            return 2
        endpoint = base_url + "/release"
    else:
        payload = {"trigger_kind": "scheduled_or_manual_reconciliation"}
        endpoint = base_url + "/reconcile"

    try:
        status, response = post(endpoint, secret, payload)
    except (urllib.error.URLError, TimeoutError) as error:
        print("DELIVERY_FAILED: " + str(error), file=sys.stderr)
        return 1
    print(response)
    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main())
