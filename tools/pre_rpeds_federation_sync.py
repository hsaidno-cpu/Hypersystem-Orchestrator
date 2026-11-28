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
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_FEDERATION_URL = "https://ehgmtkkppmceaffhwcpc.supabase.co/functions/v1/pre-core-federation"

REQUIRED_EVENT_FIELDS = (
    "event_id", "event_type", "canonical_identity", "version", "release_id",
    "source_locator", "artifact_sha256", "contract_version", "compatibility_range",
    "release_channel", "capability_classes", "target_host_ids", "is_breaking", "issuer",
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
    target_host_ids = event["target_host_ids"]
    if (
        not isinstance(target_host_ids, list)
        or not target_host_ids
        or any(not isinstance(host_id, str) or not host_id.strip() for host_id in target_host_ids)
        or len(set(target_host_ids)) != len(target_host_ids)
    ):
        raise ValueError("target_host_ids must be a non-empty list of unique host IDs")
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



def request_oidc_token(
    audience: str,
    environ: dict[str, str] | None = None,
    opener: Any = None,
) -> str:
    """Request a short-lived GitHub Actions OIDC JWT for the exact endpoint audience."""
    env = os.environ if environ is None else environ
    endpoint = env.get("ACTIONS_ID_TOKEN_REQUEST_URL", "").strip()
    request_token = env.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "").strip()
    if not endpoint or not request_token:
        raise RuntimeError("GitHub Actions OIDC request context is unavailable; check id-token: write")
    parts = urllib.parse.urlsplit(endpoint)
    if parts.scheme != "https" or not parts.netloc:
        raise RuntimeError("GitHub Actions OIDC request endpoint is invalid")
    query = [(key, value) for key, value in urllib.parse.parse_qsl(parts.query, keep_blank_values=True) if key != "audience"]
    query.append(("audience", audience))
    scoped_url = urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query), parts.fragment)
    )
    request = urllib.request.Request(
        scoped_url,
        headers={"Authorization": "Bearer " + request_token, "Accept": "application/json"},
        method="GET",
    )
    call = opener or urllib.request.urlopen
    try:
        with call(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError("GitHub Actions OIDC token exchange failed") from error
    token = payload.get("value") if isinstance(payload, dict) else None
    if not isinstance(token, str) or len(token.split(".")) != 3:
        raise RuntimeError("GitHub Actions returned an invalid OIDC token response")
    return token


def post_oidc(url: str, oidc_token: str, payload: dict[str, Any], opener: Any = None) -> tuple[int, str]:
    body = canonical_json(payload)
    request = urllib.request.Request(
        url,
        data=body,
        headers={"content-type": "application/json", "authorization": "Bearer " + oidc_token, "accept": "application/json"},
        method="POST",
    )
    call = opener or urllib.request.urlopen
    try:
        with call(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("publish", "reconcile"))
    parser.add_argument("--event-file", default=os.environ.get("GITHUB_EVENT_PATH"))
    args = parser.parse_args()

    base_url = os.environ.get("PRE_FEDERATION_URL", DEFAULT_FEDERATION_URL).strip().rstrip("/")
    if not base_url:
        print("NOT_CONFIGURED: PRE_FEDERATION_URL is empty.", file=sys.stderr)
        return 2

    if args.mode == "publish":
        secret = os.environ.get("HSO_SYNC_TOKEN", "")
        if not secret:
            print("NOT_CONFIGURED: HSO_SYNC_TOKEN is required only for the legacy publisher relay.", file=sys.stderr)
            return 2
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
        try:
            status, response = post(endpoint, secret, payload)
        except (urllib.error.URLError, TimeoutError) as error:
            print("DELIVERY_FAILED: " + str(error), file=sys.stderr)
            return 1
    else:
        payload = {"trigger_kind": "scheduled_or_manual_reconciliation"}
        endpoint = base_url + "/reconcile"
        try:
            oidc_token = request_oidc_token(base_url)
            status, response = post_oidc(endpoint, oidc_token, payload)
        except (RuntimeError, urllib.error.URLError, TimeoutError) as error:
            print("OIDC_RECONCILIATION_FAILED: " + str(error), file=sys.stderr)
            return 1

    print(response)
    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main())
