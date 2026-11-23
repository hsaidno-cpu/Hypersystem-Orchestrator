#!/usr/bin/env python3
"""Bind a generated approval receipt to the single fixed P0 invocation workflow."""
from __future__ import annotations
import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/"examples"/"hso-p0-skill-invocation-request.json"
ACTOR="hsaidno-cpu"
CASE_ID="HSO-P0-SKILL-ANALYZER-001"
ACTION_ID="plugin.skill.invoke.codex.skill-analyzer"
TARGET="artifacts/p0-skill-analyzer-invocation.json"

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--approval-receipt",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    actor=os.environ.get("GITHUB_ACTOR","")
    run_id=os.environ.get("GITHUB_RUN_ID","")
    attempt=os.environ.get("GITHUB_RUN_ATTEMPT","1")
    if actor!=ACTOR or not run_id or attempt!="1":
        raise SystemExit("P0 preparation requires authorized actor and first workflow attempt")
    if not TEMPLATE.is_file() or TEMPLATE.is_symlink(): raise SystemExit("fixed P0 workflow template is missing or unsafe")
    if not args.approval_receipt.is_file() or args.approval_receipt.is_symlink(): raise SystemExit("approval receipt is missing or unsafe")
    workflow=json.loads(TEMPLATE.read_text(encoding="utf-8"))
    approval=json.loads(args.approval_receipt.read_text(encoding="utf-8"))
    expected={"case_id":CASE_ID,"action_id":ACTION_ID,"target_path":TARGET,"authority":"S4",
              "approver":actor,"workflow_run_id":run_id,"workflow_run_attempt":attempt}
    for key,value in expected.items():
        if approval.get(key)!=value: raise SystemExit(f"approval receipt mismatch on {key}")
    if not approval.get("signature") or not approval.get("nonce"): raise SystemExit("approval signature or nonce is missing")
    try: expiry=datetime.fromisoformat(str(approval["expires_at"]).replace("Z","+00:00"))
    except (KeyError,ValueError): raise SystemExit("approval receipt expiry is missing or malformed")
    if expiry.tzinfo is None or expiry<=datetime.now(timezone.utc): raise SystemExit("approval receipt is expired or has no timezone")
    packages=workflow.get("work_packages",[])
    if len(packages)!=1: raise SystemExit("P0 template must contain exactly one work package")
    package=packages[0]
    if package.get("task_type")!="plugin.skill_analyzer_p0_pilot" or package.get("action_id")!=ACTION_ID:
        raise SystemExit("P0 template route/action mismatch")
    workflow["requested_by"]=actor
    package["idempotency_key"]=f"hso-p0-skill-analyzer-{run_id}"
    package["approval_receipt"]=approval
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists() or args.output.is_symlink(): raise SystemExit("prepared workflow output exists; refusing overwrite")
    fd=os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"w",encoding="utf-8") as stream:
        stream.write(json.dumps(workflow,ensure_ascii=False,indent=2)+"\n");stream.flush();os.fsync(stream.fileno())
    print(json.dumps({"workflow_prepared":True,"case_id":CASE_ID,"package_id":package["package_id"],
        "idempotency_key":package["idempotency_key"],
        "approval_nonce_sha256":hashlib.sha256(approval["nonce"].encode()).hexdigest()}))
    return 0
if __name__=="__main__": raise SystemExit(main())
