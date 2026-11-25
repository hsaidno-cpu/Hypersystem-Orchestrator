#!/usr/bin/env python3
"""Send signed GitHub Actions events and scheduled sync requests to HSO."""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, sys, urllib.error, urllib.request
from pathlib import Path

def post(url: str, token: str, body: bytes, headers: dict[str, str]) -> int:
    signature = hmac.new(token.encode(), body, hashlib.sha256).hexdigest()
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json", "X-HSO-Signature": "sha256=" + signature, **headers
    })
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
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
    endpoint = os.getenv("HSO_SYNC_URL", "").strip()
    token = os.getenv("HSO_SYNC_TOKEN", "")
    if not endpoint or not token:
        print("HSO_SYNC_URL and HSO_SYNC_TOKEN are required; event not sent.", file=sys.stderr)
        return 2
    if args.mode == "reconcile":
        body = json.dumps({"trigger_kind":"scheduled"}, separators=(",",":")).encode()
        url = endpoint.replace("/hso-github-webhook", "/hso-reconcile")
        status = post(url, token, body, {"X-HSO-Delivery":"actions-" + os.getenv("GITHUB_RUN_ID","manual"),"X-HSO-Event":"scheduled_reconciliation"})
        return 0 if 200 <= status < 300 else 1
    if not args.event_file:
        print("GITHUB_EVENT_PATH is required in event mode.", file=sys.stderr); return 2
    try: event = json.loads(Path(args.event_file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print("Could not read GitHub event JSON: " + str(exc), file=sys.stderr); return 2
    repo = event.get("repository") or {}
    pr = event.get("pull_request") or {}
    run = event.get("workflow_run") or {}
    envelope = {
      "action":event.get("action"),
      "repository":{"full_name":repo.get("full_name"),"html_url":repo.get("html_url")},
      "ref":event.get("ref"),"before":event.get("before"),"after":event.get("after"),
      "number":event.get("number"),
      "pull_request":{k:pr.get(k) for k in ("number","title","html_url","state","head","base") if k in pr},
      "workflow_run":{k:run.get(k) for k in ("id","name","html_url","head_sha","conclusion","status","event") if k in run},
      "sender":{"login":(event.get("sender") or {}).get("login")}
    }
    body=json.dumps(envelope,separators=(",",":"),sort_keys=True).encode()
    delivery="-".join(filter(None,[os.getenv("GITHUB_RUN_ID"),os.getenv("GITHUB_RUN_ATTEMPT"),os.getenv("GITHUB_EVENT_NAME"),os.getenv("GITHUB_SHA","")[:12]]))
    status=post(endpoint,token,body,{"X-HSO-Delivery":delivery or "manual-event","X-HSO-Event":os.getenv("GITHUB_EVENT_NAME","repository_event")})
    return 0 if 200 <= status < 300 else 1

if __name__ == "__main__":
    raise SystemExit(main())
