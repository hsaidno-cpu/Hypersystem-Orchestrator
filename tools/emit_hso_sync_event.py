#!/usr/bin/env python3
"""Send timestamp-bound HSO webhook events and authenticated reconcile requests."""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, re, sys, time, urllib.error, urllib.request
from pathlib import Path

DELIVERY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")

def event_signing_payload(timestamp: str, delivery_id: str, event_type: str, body: bytes) -> bytes:
    if not re.fullmatch(r"\d{10}", timestamp):
        raise ValueError("timestamp must contain 10-digit Unix seconds")
    if not DELIVERY_RE.fullmatch(delivery_id):
        raise ValueError("delivery_id is missing or invalid")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", event_type):
        raise ValueError("event_type is missing or invalid")
    return (
        timestamp.encode("ascii") + b"." + delivery_id.encode("ascii") +
        b"." + event_type.encode("ascii") + b"." + body
    )

def event_signature(signing_secret: str, timestamp: str, delivery_id: str, event_type: str, body: bytes) -> str:
    if len(signing_secret.encode("utf-8")) < 32:
        raise ValueError("HSO_WEBHOOK_SIGNING_SECRET must contain at least 32 bytes")
    return hmac.new(
        signing_secret.encode("utf-8"),
        event_signing_payload(timestamp, delivery_id, event_type, body),
        hashlib.sha256,
    ).hexdigest()

def build_reconciliation_request(endpoint: str, token: str, run_id: str) -> tuple[str, bytes, dict[str, str]]:
    """Build the authenticated scheduled reconciliation request."""
    if not token:
        raise ValueError("HSO_SYNC_TOKEN is required for reconciliation")
    suffix = "/hso-github-webhook"
    if not endpoint.endswith(suffix):
        raise ValueError("HSO_GITHUB_WEBHOOK_URL must end with /hso-github-webhook")
    reconcile_url = endpoint[:-len(suffix)] + "/hso-reconcile"
    body = json.dumps({"trigger_kind": "scheduled"}, separators=(",", ":")).encode()
    headers = {
        "X-HSO-Delivery": "actions-" + (run_id or "manual"),
        "X-HSO-Event": "scheduled_reconciliation",
        "X-HSO-Sync-Token": token,
    }
    return reconcile_url, body, headers


def post(url: str, body: bytes, headers: dict[str, str], signing_secret: str | None = None) -> int:
    request_headers = {"Content-Type": "application/json", **headers}
    if signing_secret is not None:
        request_headers["X-HSO-Signature"] = "sha256=" + event_signature(
            signing_secret,
            headers.get("X-HSO-Timestamp", ""),
            headers.get("X-HSO-Delivery", ""),
            headers.get("X-HSO-Event", "repository_event"),
            body,
        )
    request = urllib.request.Request(url, data=body, method="POST", headers=request_headers)
    try:
        with urllib.request.urlopen(request, timeout=55) as response:
            print(response.read().decode("utf-8", errors="replace"))
            return response.status
    except urllib.error.HTTPError as exc:
        print("HTTP " + str(exc.code) + ": " + exc.read().decode("utf-8", errors="replace"), file=sys.stderr)
        return exc.code
    except urllib.error.URLError as exc:
        print("Network error: " + str(exc), file=sys.stderr)
        return 1

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("event", "reconcile"), default="event")
    parser.add_argument("--event-file", default=os.getenv("GITHUB_EVENT_PATH", ""))
    args = parser.parse_args()
    endpoint = os.getenv("HSO_GITHUB_WEBHOOK_URL", "").strip()
    if not endpoint:
        print("HSO_GITHUB_WEBHOOK_URL is required; no request sent.", file=sys.stderr)
        return 2

    if args.mode == "reconcile":
        try:
            reconcile_url, body, headers = build_reconciliation_request(
                endpoint,
                os.getenv("HSO_SYNC_TOKEN", ""),
                os.getenv("GITHUB_RUN_ID", "manual"),
            )
        except ValueError as exc:
            print(str(exc) + "; no request sent.", file=sys.stderr)
            return 2
        status = post(reconcile_url, body, headers)
        return 0 if 200 <= status < 300 else 1

    signing_secret = os.getenv("HSO_WEBHOOK_SIGNING_SECRET", "")
    sync_token = os.getenv("HSO_SYNC_TOKEN", "")
    if len(signing_secret.encode("utf-8")) < 32:
        print("HSO_WEBHOOK_SIGNING_SECRET must contain at least 32 bytes; event not sent.", file=sys.stderr)
        return 2
    if sync_token and hmac.compare_digest(signing_secret, sync_token):
        print("HSO_WEBHOOK_SIGNING_SECRET and HSO_SYNC_TOKEN must be different; event not sent.", file=sys.stderr)
        return 2
    if not args.event_file:
        print("GITHUB_EVENT_PATH is required in event mode.", file=sys.stderr)
        return 2
    try:
        event = json.loads(Path(args.event_file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("Could not read GitHub event JSON: " + str(exc), file=sys.stderr)
        return 2
    if not isinstance(event, dict):
        print("GitHub event JSON must be an object.", file=sys.stderr)
        return 2

    repo, pr, run = event.get("repository") or {}, event.get("pull_request") or {}, event.get("workflow_run") or {}
    envelope = {
        "action": event.get("action"),
        "repository": {"full_name": repo.get("full_name"), "html_url": repo.get("html_url")},
        "ref": event.get("ref"), "before": event.get("before"), "after": event.get("after"),
        "number": event.get("number"),
        "pull_request": {k: pr.get(k) for k in ("number", "title", "html_url", "state", "head", "base") if k in pr},
        "workflow_run": {k: run.get(k) for k in ("id", "name", "html_url", "head_sha", "conclusion", "status", "event") if k in run},
        "sender": {"login": (event.get("sender") or {}).get("login")},
    }
    body = json.dumps(envelope, separators=(",", ":"), sort_keys=True).encode()
    delivery = "-".join(filter(None, [
        os.getenv("GITHUB_RUN_ID"), os.getenv("GITHUB_RUN_ATTEMPT"),
        os.getenv("GITHUB_EVENT_NAME"), os.getenv("GITHUB_SHA", "")[:12],
    ])) or "manual-event"
    timestamp = str(int(time.time()))
    status = post(endpoint, body, {
        "X-HSO-Delivery": delivery,
        "X-HSO-Event": os.getenv("GITHUB_EVENT_NAME", "repository_event"),
        "X-HSO-Timestamp": timestamp,
    }, signing_secret=signing_secret)
    return 0 if 200 <= status < 300 else 1

if __name__ == "__main__":
    raise SystemExit(main())
