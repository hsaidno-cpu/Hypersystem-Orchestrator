#!/usr/bin/env python3
"""Send HSO Mission Control events using short-lived GitHub Actions OIDC tokens.

No long-lived HSO shared token is copied into GitHub Actions. The HSO Edge
Functions verify the exact repository, main branch, workflow_ref, event and
endpoint audience before accepting these requests.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Mapping

DEFAULT_BASE_URL = "https://ehgmtkkppmceaffhwcpc.supabase.co/functions/v1"
DEFAULT_WEBHOOK_URL = DEFAULT_BASE_URL + "/hso-github-webhook"
DEFAULT_RECONCILE_URL = DEFAULT_BASE_URL + "/hso-reconcile"


def request_oidc_token(
    audience: str,
    environ: Mapping[str, str] | None = None,
    opener: Any = None,
) -> str:
    """Exchange the runner-provided request capability for a scoped OIDC JWT."""
    env = os.environ if environ is None else environ
    endpoint = env.get("ACTIONS_ID_TOKEN_REQUEST_URL", "").strip()
    request_token = env.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "").strip()
    if not endpoint or not request_token:
        raise RuntimeError("GitHub Actions OIDC request context is unavailable; check id-token: write")

    parts = urllib.parse.urlsplit(endpoint)
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    query = [(key, value) for key, value in query if key != "audience"]
    query.append(("audience", audience))
    scoped_url = urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query), parts.fragment)
    )
    request = urllib.request.Request(
        scoped_url,
        headers={
            "Authorization": "Bearer " + request_token,
            "Accept": "application/json",
        },
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


def post_json(
    endpoint: str,
    oidc_token: str,
    payload: bytes,
    *,
    event_type: str | None = None,
    delivery_id: str | None = None,
    opener: Any = None,
) -> tuple[int, str]:
    headers = {
        "Authorization": "Bearer " + oidc_token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if event_type:
        headers["X-HSO-Event"] = event_type
    if delivery_id:
        headers["X-HSO-Delivery"] = delivery_id
    request = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")
    call = opener or urllib.request.urlopen
    try:
        with call(request, timeout=45) as response:
            return int(response.status), response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError("HSO event delivery failed") from error


def event_delivery_id(run_id: str, event_name: str) -> str:
    if not run_id.isdigit():
        raise ValueError("GITHUB_RUN_ID must be numeric")
    if not event_name or any(ch not in "abcdefghijklmnopqrstuvwxyz_" for ch in event_name):
        raise ValueError("GITHUB_EVENT_NAME is invalid")
    # Stable across a retry of the same Actions run: replay does not create a new inbox row.
    return f"github-actions-{run_id}-{event_name}"


def run(mode: str, environ: Mapping[str, str] | None = None) -> int:
    env = os.environ if environ is None else environ
    webhook_url = env.get("HSO_GITHUB_WEBHOOK_URL", DEFAULT_WEBHOOK_URL).strip()
    reconcile_url = env.get("HSO_RECONCILE_URL", DEFAULT_RECONCILE_URL).strip()
    event_name = env.get("GITHUB_EVENT_NAME", "").strip()
    run_id = env.get("GITHUB_RUN_ID", "").strip()

    if mode == "event":
        event_path = env.get("GITHUB_EVENT_PATH", "").strip()
        if not event_path:
            raise RuntimeError("GITHUB_EVENT_PATH is required in event mode")
        if event_name not in {"push", "pull_request_target", "workflow_run"}:
            raise RuntimeError("Unsupported GitHub event type for Mission Control ingestion")
        body = Path(event_path).read_bytes()
        # Refuse accidental payload forwarding from a different repository.
        event = json.loads(body.decode("utf-8"))
        if (event.get("repository") or {}).get("full_name") != "hsaidno-cpu/Hypersystem-Orchestrator":
            raise RuntimeError("GitHub event repository does not match the HSO source repository")
        delivery = event_delivery_id(run_id, event_name)
        token = request_oidc_token(webhook_url, env)
        status, response = post_json(
            webhook_url, token, body, event_type=event_name, delivery_id=delivery
        )
    elif mode == "reconcile":
        if event_name not in {"schedule", "workflow_dispatch"}:
            raise RuntimeError("Reconciliation is permitted only for schedule or workflow_dispatch")
        token = request_oidc_token(reconcile_url, env)
        trigger = "scheduled" if event_name == "schedule" else "manual"
        body = json.dumps(
            {"trigger_kind": trigger, "source": "github_actions", "run_id": run_id},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        status, response = post_json(reconcile_url, token, body)
    else:
        raise ValueError("mode must be event or reconcile")

    # Server response is safe metadata; never print the JWT or runner request token.
    print(response)
    return 0 if 200 <= status < 300 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("event", "reconcile"))
    args = parser.parse_args(argv)
    try:
        return run(args.mode)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(type(error).__name__ + ": " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
