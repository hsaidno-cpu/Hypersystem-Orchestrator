#!/usr/bin/env python3
"""Resolve selective/full-suite requests into plans; this is not an installer."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ELIGIBLE = {"installable_public", "installable_private"}
READY_ADAPTER = {"host_tested", "runtime_verified"}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc


def resolve(manifest: dict, registry: dict, platforms: dict) -> dict:
    if manifest.get("schema_version") != "1.0.0":
        raise ValueError("schema_version must be 1.0.0")
    if manifest.get("dry_run") is not True:
        raise ValueError("Only dry_run=true is supported; no installer is implemented.")
    mode, keys = manifest.get("selection_mode"), manifest.get("plugin_keys")
    if not isinstance(keys, list) or len(keys) != len(set(keys)):
        raise ValueError("plugin_keys must be a unique array")
    if mode == "single" and len(keys) != 1:
        raise ValueError("single mode requires exactly one plugin_key")
    if mode == "multi" and len(keys) < 2:
        raise ValueError("multi mode requires at least two plugin_keys")
    if mode == "full_suite" and keys:
        raise ValueError("full_suite mode requires an empty plugin_keys array; it resolves dynamically")
    if mode not in {"single", "multi", "full_suite"}:
        raise ValueError("selection_mode must be single, multi, or full_suite")
    distribution_items = registry.get("plugins", [])
    by_key = {p["plugin_key"]: p for p in distribution_items}
    platform_by_id = {a["target_id"]: a for a in platforms.get("adapters", [])}
    target = manifest.get("target_platform")
    adapter = platform_by_id.get(target)
    if adapter is None:
        raise ValueError(f"Unknown target_platform: {target}")
    if mode == "full_suite":
        requested = [p["plugin_key"] for p in distribution_items if p.get("distribution_status") in ELIGIBLE]
    else:
        unknown = sorted(set(keys) - set(by_key))
        if unknown:
            raise ValueError(f"Unknown plugin_key values: {unknown}")
        requested = keys
    adapter_blockers = []
    if adapter.get("adapter_status") not in READY_ADAPTER:
        adapter_blockers.append("PLATFORM_ADAPTER_NOT_HOST_TESTED")
    if adapter.get("host_activation_test") != "PASS" and adapter.get("adapter_status") != "runtime_verified":
        adapter_blockers.append("HOST_ACTIVATION_EVIDENCE_MISSING")
    resolved, excluded, global_blockers = [], [], []
    for key in requested:
        item = by_key[key]
        blockers = list(item.get("blockers", []))
        if item.get("distribution_status") not in ELIGIBLE:
            blockers.append("PLUGIN_NOT_DISTRIBUTION_ELIGIBLE")
        if item.get("license_status") != "cleared":
            blockers.append("LICENSE_DISTRIBUTION_NOT_CLEARED")
        if not item.get("source_commit"):
            blockers.append("SOURCE_COMMIT_NOT_PINNED")
        if not item.get("package_artifact"):
            blockers.append("PACKAGE_ARTIFACT_NOT_PUBLISHED")
        if item.get("distribution_status") == "installable_private" and manifest.get("private_source_access_granted") is not True:
            blockers.append("PRIVATE_SOURCE_ACCESS_NOT_GRANTED")
        blockers.extend(adapter_blockers)
        if manifest.get("dependency_policy") == "include_declared" and item.get("dependency_metadata_status") != "verified":
            blockers.append("DEPENDENCY_GRAPH_NOT_VERIFIED")
        resolved.append({
            "plugin_key":key,
            "distribution_status":item.get("distribution_status"),
            "package_version":item.get("platform_package_version") or item.get("source_version"),
            "source_commit":item.get("source_commit"),
            "package_artifact":item.get("package_artifact"),
            "status":"BLOCKED" if blockers else "ELIGIBLE_FOR_INSTALLER",
            "blockers":sorted(set(blockers))
        })
    for item in distribution_items:
        if item["plugin_key"] not in requested:
            excluded.append({"plugin_key":item["plugin_key"],"distribution_status":item["distribution_status"],"reason":"NOT_SELECTED" if mode != "full_suite" else "NOT_ELIGIBLE_FOR_FULL_SUITE"})
    if mode == "full_suite" and not requested:
        global_blockers.append("NO_INSTALLABLE_PLUGIN_PACKAGES_AVAILABLE")
    if any(item["status"] == "BLOCKED" for item in resolved):
        global_blockers.append("ONE_OR_MORE_SELECTED_PLUGINS_ARE_BLOCKED")
    status = "BLOCKED" if global_blockers or (resolved and all(i["status"] == "BLOCKED" for i in resolved)) else "READY_FOR_INSTALLER"
    return {
        "schema_version":"1.0.0","request_id":manifest.get("request_id"),
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "target_platform":target,"adapter_status":adapter.get("adapter_status"),
        "selection_mode":mode,"dependency_policy":manifest.get("dependency_policy"),
        "version_policy":manifest.get("version_policy"),"resolution_status":status,
        "action":"PLAN_ONLY_NOT_INSTALLED","requested_plugin_keys":requested,
        "resolved_plugins":resolved,"excluded_plugins":excluded,
        "blockers":sorted(set(global_blockers)),
        "non_claims":["No package was downloaded or installed.","No plugin was enabled or authorized.","No host activation or runtime execution was performed."]
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",required=True,type=Path)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--registry",type=Path,default=ROOT/"catalog"/"distribution-registry.json")
    parser.add_argument("--platforms",type=Path,default=ROOT/"catalog"/"platform-registry.json")
    args=parser.parse_args()
    try:
        plan=resolve(load_json(args.manifest),load_json(args.registry),load_json(args.platforms))
        rendered=json.dumps(plan,ensure_ascii=False,indent=2)+"\n"
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(rendered,encoding="utf-8")
        print(rendered,end="")
        return 0 if plan["resolution_status"]=="READY_FOR_INSTALLER" else 2
    except ValueError as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
