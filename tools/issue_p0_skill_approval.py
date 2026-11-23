#!/usr/bin/env python3
"""Issue a short-lived HMAC approval receipt for one P0 paid inference."""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

CASE_ID="HSO-P0-SKILL-ANALYZER-001"
ACTION_ID="plugin.skill.invoke.codex.skill-analyzer"
TARGET_PATH="artifacts/p0-skill-analyzer-invocation.json"
AUTHORITY="S4"
AUTHORIZED_ACTOR="hsaidno-cpu"

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    secret=os.environ.get("HSO_APPROVAL_HMAC_KEY","").strip()
    actor=os.environ.get("GITHUB_ACTOR","").strip()
    run_id=os.environ.get("GITHUB_RUN_ID","").strip()
    attempt=os.environ.get("GITHUB_RUN_ATTEMPT","1").strip()
    if len(secret)<32: raise SystemExit("HSO_APPROVAL_HMAC_KEY must be a high-entropy secret of at least 32 characters")
    if actor!=AUTHORIZED_ACTOR: raise SystemExit("P0 paid inference is restricted to the repository owner workflow actor")
    if not run_id or attempt!="1": raise SystemExit("P0 approval requires a unique workflow run and prohibits workflow reruns")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists() or args.output.is_symlink(): raise SystemExit("approval output already exists; refusing overwrite")
    now=datetime.now(timezone.utc)
    unsigned={
        "case_id":CASE_ID,"action_id":ACTION_ID,"target_path":TARGET_PATH,"authority":AUTHORITY,
        "approver":actor,"issued_at":now.isoformat(timespec="seconds").replace("+00:00","Z"),
        "expires_at":(now+timedelta(minutes=5)).isoformat(timespec="seconds").replace("+00:00","Z"),
        "nonce":uuid.uuid4().hex,"workflow_run_id":run_id,"workflow_run_attempt":attempt
    }
    canonical=json.dumps(unsigned,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    signature=hmac.new(secret.encode(),canonical.encode(),hashlib.sha256).hexdigest()
    receipt={**unsigned,"signature":signature}
    fd=os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as stream:
        stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n");stream.flush();os.fsync(stream.fileno())
    print(json.dumps({"approval_created":True,"case_id":CASE_ID,"action_id":ACTION_ID,
        "approver":actor,"workflow_run_id":run_id,"expires_at":unsigned["expires_at"],
        "nonce_sha256":hashlib.sha256(unsigned["nonce"].encode()).hexdigest()}))
    return 0
if __name__=="__main__": raise SystemExit(main())
