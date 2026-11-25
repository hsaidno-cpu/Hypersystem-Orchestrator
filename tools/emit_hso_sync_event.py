#!/usr/bin/env python3
"""Send a signed, bounded HSO reconciliation request from the trusted main branch."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit, urlunsplit


def reconcile_url(webhook_url: str) -> str:
    parsed = urlsplit(webhook_url.strip())
    if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.endswith(".supabase.co"):
        raise ValueError("HSO webhook URL must be an HTTPS Supabase project endpoint")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("HSO webhook URL must not include userinfo, query parameters, or fragments")
    if parsed.path.rstrip("/") != "/functions/v1/hso-github-webhook":
        raise ValueError("HSO webhook URL path must be /functions/v1/hso-github-webhook")
    return urlunsplit((parsed.scheme, parsed.netloc, "/functions/v1/hso-reconcile", "", ""))


def post(url: str, token: str, body: bytes, delivery: str) -> int:
    signature = hmac.new(token.encode("utf-8"), body, hashlib.sha256).hexdigest()
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "X-HSO-Signature": "sha256=" + signature,
        "X-HSO-Delivery": delivery,
        "X-HSO-Event": "scheduled_reconciliation",
    })
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            # Never log response bodies: they may contain internal details.
            print("HSO reconciliation HTTP " + str(response.status))
            return response.status
    except urllib.error.HTTPError as exc:
        print("HSO reconciliation HTTP " + str(exc.code), file=sys.stderr)
        return exc.code
    except urllib.error.URLError:
        print("HSO reconciliation network request failed", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("reconcile",), default="reconcile")
    args = parser.parse_args()
    endpoint = os.getenv("HSO_SYNC_URL", "").strip()
    token = os.getenv("HSO_SYNC_TOKEN", "")
    if not endpoint or not token:
        print("HSO reconciliation configuration is missing", file=sys.stderr)
        return 2
    try:
        url = reconcile_url(endpoint)
    except ValueError as exc:
        print("Invalid HSO endpoint: " + str(exc), file=sys.stderr)
        return 2
    body = json.dumps(
        {"trigger_kind": "scheduled", "provider": "github_actions"},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    delivery = "-".join(filter(None, [
        os.getenv("GITHUB_RUN_ID", "manual"),
        os.getenv("GITHUB_RUN_ATTEMPT", "1"),
        args.mode,
    ]))
    status = post(url, token, body, delivery)
    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main())
