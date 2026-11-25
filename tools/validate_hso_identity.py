#!/usr/bin/env python3
"""Validate HSO cross-platform immutable identities and canonical terminology."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config"/"hso-identity-registry.json"
DOC=ROOT/"docs"/"HSO-CANONICAL-IDENTITY-AND-NOMENCLATURE.md"

def fail(message: str) -> None:
    raise ValueError(message)

def validate() -> None:
    try:
        d=json.loads(REGISTRY.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("Canonical identity registry is missing")
    except json.JSONDecodeError as e:
        fail(f"Invalid registry JSON at line {e.lineno}: {e.msg}")
    c=d["canonical_identity"]; p=d["platforms"]; n=d["naming_policy"]
    gh=p["github"]; sb=p["supabase"]; no=p["notion"]; ve=p["vercel"]
    if c.get("system_name")!="Hypersystem-Orchestrator" or c.get("acronym")!="HSO":
        fail("Canonical system name/acronym drift")
    if gh.get("repository_full_name")!=c.get("canonical_repository") or gh.get("display_name")!=c.get("system_name"):
        fail("GitHub repository does not match canonical identity")
    if not re.fullmatch(r"[0-9]{5,20}",str(gh.get("repository_id",""))):
        fail("GitHub repository ID is not a stable numeric ID")
    ref=sb.get("project_ref","")
    if not re.fullmatch(r"[a-z0-9]{20}",ref) or sb.get("project_url")!=f"https://{ref}.supabase.co":
        fail("Supabase immutable ref and API URL are inconsistent")
    if sb.get("project_display_name",{}).get("desired")!=c.get("system_name"):
        fail("Supabase desired display name differs from canonical system name")
    if sb.get("table_prefix")!="hso_" or set(sb.get("immutable_identity_fields",[]))!={"project_ref","project_url","database_host"}:
        fail("Supabase namespace/immutable field contract drift")
    keys=d.get("operational_source_keys",[])
    expected={"notion-control-center","notion-roadmap","notion-execution-ledger","notion-evidence-registry","github-hso-parent"}
    if len(keys)!=len(set(keys)) or set(keys)!=expected:
        fail("Mandatory source keys missing, duplicated or renamed")
    ds=no.get("data_sources",{})
    if set(ds)!={"roadmap","execution_ledger","evidence_registry"}:
        fail("Notion data source identity set is incomplete")
    ids=[x.get("id") for x in ds.values()]
    if len(ids)!=len(set(ids)):
        fail("Duplicate Notion data_source_id")
    for name,x in ds.items():
        if x.get("url")!=f"collection://{x.get('id')}":
            fail(f"Notion {name} URL does not match data source ID")
    primary=ve["canonical_dashboard_project"]; secondary=ve["secondary_project"]
    project_ids=[primary.get("project_id"),secondary.get("project_id")]
    if None in project_ids or len(project_ids)!=len(set(project_ids)):
        fail("Vercel project IDs missing or colliding")
    if primary.get("canonical_app_name")!="HSO Mission Control" or primary.get("root_directory")!="apps/mission-control" or primary.get("state")!="CANONICAL_DASHBOARD_DEPLOYMENT":
        fail("Canonical Vercel dashboard identity/root is inconsistent")
    if secondary.get("state")!="NON_CANONICAL_HOLD":
        fail("Secondary Vercel project must remain explicitly on hold")
    if "HSMART" not in n.get("prohibited_aliases",{}) or "separate project" not in n["prohibited_aliases"]["HSMART"].lower():
        fail("HSMART must remain a separate project, not an HSO alias")
    terms=d.get("canonical_terms",{})
    expected_terms={
      "source_states":{"not_configured","connected","degraded"},
      "snapshot_states":{"UNKNOWN","COMPLETE","INCOMPLETE"},
      "scope_states":{"PENDING","IN_SCOPE","OUT_OF_SCOPE"},
      "weight_approval_states":{"PENDING","APPROVED","REJECTED"},
      "progress_states":{"UNMEASURED","PARTIAL_COVERAGE","SCOPE_UNCONFIRMED","SCOPE_CONFLICT","SOURCE_STALE"},
      "verification_terms":{"UNKNOWN","VERIFIED"}}
    for key,expected_values in expected_terms.items():
        actual=terms.get(key,[])
        if len(actual)!=len(set(actual)) or set(actual)!=expected_values:
            fail(f"Canonical state vocabulary drift: {key}")
    if not DOC.is_file():
        fail("Canonical nomenclature contract document is missing")
    print("PASS: canonical HSO / GitHub identity")
    print("PASS: immutable Supabase ref, URL and hso_ namespace")
    print("PASS: Notion data-source IDs and source keys")
    print("PASS: canonical/secondary Vercel project separation")
    print("PASS: HSMART is not an HSO alias")
    print("PASS: canonical machine-state vocabularies")

if __name__=="__main__":
    try: validate()
    except (ValueError,TypeError,KeyError) as exc:
        print(f"FAIL: {exc}",file=sys.stderr); raise SystemExit(1)
