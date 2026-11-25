#!/usr/bin/env python3
"""Validate distribution registry and platform adapter declarations (stdlib only)."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ELIGIBLE = {"installable_public", "installable_private"}
KNOWN = ELIGIBLE | {"review_required", "blocked", "private_source_restricted", "snapshot_only", "candidate_incomplete", "legacy_redirect"}


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: {exc}") from exc


def validate() -> None:
    catalog = load(ROOT / "catalog" / "plugins.json")
    distribution = load(ROOT / "catalog" / "distribution-registry.json")
    platforms = load(ROOT / "catalog" / "platform-registry.json")
    repositories_doc = load(ROOT / "catalog" / "repositories.json")
    repositories = {item["repository_id"]: item for item in repositories_doc.get("repositories", [])}
    catalog_plugins = catalog.get("plugins", [])
    records = distribution.get("plugins", [])
    keys = [p.get("plugin_key") for p in catalog_plugins]
    record_keys = [p.get("plugin_key") for p in records]
    if len(record_keys) != len(set(record_keys)):
        raise ValueError("Distribution registry contains duplicate plugin_key values")
    if set(record_keys) != set(keys):
        raise ValueError(f"Distribution/catalog identity mismatch; missing={sorted(set(keys)-set(record_keys))}, extra={sorted(set(record_keys)-set(keys))}")
    if distribution.get("plugin_count") != len(records):
        raise ValueError("distribution plugin_count does not match records")
    by_catalog = {p["plugin_key"]: p for p in catalog_plugins}
    for item in records:
        key, status = item["plugin_key"], item.get("distribution_status")
        source_state = by_catalog[key]["source_state"]
        if status not in KNOWN:
            raise ValueError(f"{key}: unsupported distribution_status {status!r}")
        if item.get("source_state") != source_state:
            raise ValueError(f"{key}: source_state drift between registries")
        if status in ELIGIBLE:
            if item.get("license_status") != "cleared" or not item.get("source_commit") or not item.get("package_artifact") or item.get("blockers"):
                raise ValueError(f"{key}: eligible packages require cleared rights, pinned source, artifact and no blockers")
        elif not item.get("blockers"):
            raise ValueError(f"{key}: non-installable state must disclose blockers")
        if status == "legacy_redirect" and source_state != "canonical_redirect":
            raise ValueError(f"{key}: legacy_redirect conflicts with catalog source state")
        if status == "snapshot_only" and source_state != "pending_repository":
            raise ValueError(f"{key}: snapshot_only requires pending_repository")
        if status == "candidate_incomplete" and source_state != "candidate_repository":
            raise ValueError(f"{key}: candidate_incomplete requires candidate_repository")
        if source_state == "private_repository_source":
            source = repositories.get(item.get("source_repository_id"))
            if source is None or source.get("status") != "private_source_verified" or source.get("visibility") != "private":
                raise ValueError(f"{key}: private repository source is not verified in the repository registry")
            if status != "private_source_restricted":
                raise ValueError(f"{key}: private source must remain private_source_restricted until distribution rights pass")
            if item.get("source_commit") != source.get("pinned_commit") or not item.get("source_commit"):
                raise ValueError(f"{key}: distribution source_commit must match the pinned private repository commit")
            if item.get("license_status") != "not_assessed":
                raise ValueError(f"{key}: private-source license status cannot be promoted without rights evidence")
            if item.get("package_artifact") is not None:
                raise ValueError(f"{key}: private restricted source cannot advertise a public package artifact")
            required_blockers = {
                "LICENSE_RIGHTS_NOT_ASSESSED",
                "PRIVATE_SOURCE_NOT_PUBLICLY_DISTRIBUTABLE",
                "VCM_HSO_HOST_ADAPTER_NOT_CONFIGURED",
            }
            if not required_blockers.issubset(set(item.get("blockers", []))):
                raise ValueError(f"{key}: private source must disclose license, visibility and runtime blockers")
        if item.get("package_artifact") is not None and status not in ELIGIBLE:
            raise ValueError(f"{key}: non-installable record cannot advertise a package artifact")
    adapters = platforms.get("adapters", [])
    adapter_ids = [a.get("target_id") for a in adapters]
    if not adapters or len(adapter_ids) != len(set(adapter_ids)):
        raise ValueError("Platform registry must have unique non-empty adapter targets")
    allowed = {"planned", "adapter_implemented", "host_tested", "runtime_verified"}
    for adapter in adapters:
        if adapter.get("adapter_status") not in allowed:
            raise ValueError(f"{adapter.get('target_id')}: invalid adapter_status")
        if adapter["adapter_status"] == "planned" and (adapter.get("host_activation_test") != "NOT_RUN" or adapter.get("runtime_execution_test") != "NOT_RUN"):
            raise ValueError(f"{adapter.get('target_id')}: planned adapter cannot claim completed tests")
    print(f"PASS: {len(records)} distribution records map one-to-one to catalog identities")
    print("PASS: eligibility, license, source, artifact and blocker invariants")
    print(f"PASS: {len(adapters)} adapter targets have explicit verification states")
    print(f"NOTE: {sum(1 for p in records if p['distribution_status'] in ELIGIBLE)} currently installable packages")
    print("NOTE: static validation does not prove installation, host activation or runtime execution")


if __name__ == "__main__":
    try:
        validate()
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
