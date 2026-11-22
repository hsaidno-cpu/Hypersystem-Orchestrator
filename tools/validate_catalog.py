#!/usr/bin/env python3
"""Validate the Hypersystem Orchestrator ecosystem catalog using stdlib only."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "plugins.json"
REPOSITORIES_PATH = ROOT / "catalog" / "repositories.json"
GITMODULES_PATH = ROOT / ".gitmodules"


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        fail(f"Required file is missing: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path.relative_to(ROOT)} at line {exc.lineno}: {exc.msg}")


def parse_submodules(path: Path):
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    result = {}
    sections = re.split(r"(?m)^\[submodule\s+\"([^\"]+)\"\]\s*$", text)
    for index in range(1, len(sections), 2):
        name = sections[index]
        body = sections[index + 1]
        values = dict(re.findall(r"(?m)^\s*(path|url)\s*=\s*(.+?)\s*$", body))
        if "path" not in values or "url" not in values:
            fail(f"Submodule section '{name}' must define path and url")
        if values["path"] in result:
            fail(f"Duplicate submodule path: {values['path']}")
        result[values["path"]] = {"name": name, "url": values["url"]}
    return result


def validate():
    catalog = load_json(CATALOG_PATH)
    repo_doc = load_json(REPOSITORIES_PATH)
    plugins = catalog.get("plugins")
    repositories = repo_doc.get("repositories")

    if not isinstance(plugins, list) or not isinstance(repositories, list):
        fail("Catalog plugins and repositories must both be arrays")
    if len(plugins) != catalog.get("expected_plugin_count"):
        fail(f"Expected {catalog.get('expected_plugin_count')} plugin records, found {len(plugins)}")

    plugin_keys = [p.get("plugin_key") for p in plugins]
    plugin_ids = [p.get("plugin_creator_id") for p in plugins]
    repo_ids = [r.get("repository_id") for r in repositories]

    if len(plugin_keys) != len(set(plugin_keys)):
        fail("Duplicate plugin_key detected")
    if len(plugin_ids) != len(set(plugin_ids)):
        fail("Duplicate plugin_creator_id detected")
    if len(repo_ids) != len(set(repo_ids)):
        fail("Duplicate repository_id detected")

    plugin_key_set = set(plugin_keys)
    repo_id_set = set(repo_ids)
    source_states = {
        "integrated_submodule",
        "candidate_repository",
        "pending_repository",
        "canonical_redirect",
    }

    for plugin in plugins:
        key = plugin.get("plugin_key", "<missing>")
        required = [
            "display_name", "plugin_creator_id", "primary_domain", "purpose",
            "responsibility_owner", "boundary", "source_state",
            "version_evidence", "related_plugins", "source_classification",
            "instruction_snapshot_path", "instruction_capture_date",
            "instruction_source_authority",
        ]
        for field in required:
            if not plugin.get(field):
                fail(f"{key}: required field '{field}' is empty")
        if plugin.get("source_state") not in source_states:
            fail(f"{key}: unsupported source_state '{plugin.get('source_state')}'")
        repo_id = plugin.get("source_repository_id")
        state = plugin.get("source_state")
        if repo_id is not None and repo_id not in repo_id_set:
            fail(f"{key}: source repository '{repo_id}' is not registered")
        if state == "pending_repository" and repo_id is not None:
            fail(f"{key}: pending_repository must not claim a source repository")
        if state == "candidate_repository":
            repo = next(r for r in repositories if r["repository_id"] == repo_id)
            if repo.get("status") != "candidate_not_integrated":
                fail(f"{key}: candidate source must be marked candidate_not_integrated")
        if state == "integrated_submodule":
            repo = next(r for r in repositories if r["repository_id"] == repo_id)
            if repo.get("status") not in {"integrated_submodule", "integrated_submodule_private"}:
                fail(f"{key}: integrated plugin repository is not marked integrated")
            if not repo.get("submodule_path") or not repo.get("pinned_commit"):
                fail(f"{key}: integrated source requires submodule_path and pinned_commit")
        if state == "canonical_redirect":
            alias = plugin.get("alias_of")
            if alias not in plugin_key_set:
                fail(f"{key}: canonical redirect must point to a registered alias_of target")
            if alias == key:
                fail(f"{key}: alias cannot point to itself")
        if not plugin.get("primary_triggers") or not plugin.get("negative_triggers"):
            fail(f"{key}: positive and negative routing triggers are required")
        if not isinstance(plugin.get("instruction_skill_count"), int) or plugin["instruction_skill_count"] < 1:
            fail(f"{key}: instruction_skill_count must be a positive integer")
        snapshot_path = ROOT / plugin["instruction_snapshot_path"]
        if not snapshot_path.is_file():
            fail(f"{key}: instruction snapshot path is missing: {plugin['instruction_snapshot_path']}")
        if state == "pending_repository" and plugin.get("source_classification") != "NOT_IDENTIFIED":
            fail(f"{key}: pending repository must use NOT_IDENTIFIED classification")
        if state == "candidate_repository" and plugin.get("source_classification") != "CANDIDATE_INCOMPLETE":
            fail(f"{key}: candidate source must use CANDIDATE_INCOMPLETE classification")
        if state == "canonical_redirect" and plugin.get("source_classification") != "LEGACY_REDIRECT":
            fail(f"{key}: canonical redirect must use LEGACY_REDIRECT classification")
        if state == "integrated_submodule" and not plugin.get("source_classification", "").startswith("OFFICIAL_"):
            fail(f"{key}: integrated submodule must use an OFFICIAL source classification")
        for platform_field in ["platform_package_version", "platform_current_release_id", "platform_scope", "platform_discoverability", "platform_source_authority", "version_alignment_state", "repository_version", "version_alignment_note", "version_authority", "version_reconciliation_status", "source_sync_status"]:
            if platform_field not in plugin:
                fail(f"{key}: missing version-plane field '{platform_field}'")
        if not re.fullmatch(r"pluginrel_[A-Za-z0-9]+", plugin["platform_current_release_id"]):
            fail(f"{key}: invalid Plugin Creator release ID")
        if plugin["platform_scope"] != "USER" or plugin["platform_discoverability"] != "PRIVATE":
            fail(f"{key}: Plugin Creator scope/discoverability metadata drift")
        alignment = plugin["version_alignment_state"]
        if alignment in {"SOURCE_AHEAD_OF_PLATFORM", "SOURCE_AND_PLATFORM_MATCH", "DEPLOYMENT_AHEAD_OF_SOURCE"} and not plugin.get("repository_version"):
            fail(f"{key}: source-backed version alignment requires repository_version")
        if alignment == "SOURCE_AND_PLATFORM_MATCH" and plugin["repository_version"] != plugin["platform_package_version"]:
            fail(f"{key}: SOURCE_AND_PLATFORM_MATCH versions do not match")
        if alignment == "SOURCE_AHEAD_OF_PLATFORM" and plugin["repository_version"] == plugin["platform_package_version"]:
            fail(f"{key}: SOURCE_AHEAD_OF_PLATFORM must contain differing versions")
        if alignment == "DEPLOYMENT_AHEAD_OF_SOURCE" and plugin["repository_version"] == plugin["platform_package_version"]:
            fail(f"{key}: DEPLOYMENT_AHEAD_OF_SOURCE must contain differing versions")
        for related in plugin.get("related_plugins", []):
            if related not in plugin_key_set:
                fail(f"{key}: unknown related plugin '{related}'")

    submodules = parse_submodules(GITMODULES_PATH)
    for repo in repositories:
        path = repo.get("submodule_path")
        if repo.get("status") in {"integrated_submodule", "integrated_submodule_private"}:
            if not path:
                fail(f"{repo['repository_id']}: integrated repository has no submodule_path")
            entry = submodules.get(path)
            if not entry:
                fail(f"{repo['repository_id']}: {path} is not declared in .gitmodules")
            if entry["url"] != repo.get("url", "").removesuffix(".git") + ".git":
                fail(f"{repo['repository_id']}: .gitmodules URL does not match catalog URL")
            if not re.fullmatch(r"[0-9a-f]{40}", repo.get("pinned_commit", "")):
                fail(f"{repo['repository_id']}: pinned_commit must be a 40-character SHA")
    if len(submodules) != 4:
        fail(f"Expected 4 verified source submodules at this stage, found {len(submodules)}")

    snapshot_index = load_json(ROOT / "catalog" / "instruction-snapshots.json")
    if len(snapshot_index.get("plugins", [])) != len(plugins):
        fail("Instruction snapshot index must contain all 20 plugin identities")
    if snapshot_index.get("total_skill_records") != sum(p["instruction_skill_count"] for p in plugins):
        fail("Instruction snapshot skill total does not match the plugin catalog")
    index_by_key = {p["plugin_key"]: p for p in snapshot_index["plugins"]}
    for plugin in plugins:
        indexed = index_by_key.get(plugin["plugin_key"])
        if not indexed:
            fail(f"{plugin['plugin_key']}: missing instruction snapshot index record")
        if indexed.get("skill_count") != plugin["instruction_skill_count"]:
            fail(f"{plugin['plugin_key']}: instruction snapshot skill count mismatch")
        if indexed.get("instruction_path") != plugin["instruction_snapshot_path"]:
            fail(f"{plugin['plugin_key']}: instruction snapshot path mismatch")
    if snapshot_index["total_skill_records"] != 238:
        fail("Expected 238 instruction skill records in the current snapshot")

    print(f"PASS: {len(plugins)} unique plugin identities")
    print(f"PASS: {len(repositories)} repository records")
    print(f"PASS: {len(submodules)} declared and pinned source submodules")
    print("PASS: source-state, alias, relationship and repository URL consistency")
    print("PASS: every plugin has a segregated instruction snapshot/pointer and explicit routing boundaries")
    print(f"PASS: {snapshot_index['total_skill_records']} indexed skill instruction records across {len(plugins)} plugins")
    print("NOTE: static checks do not prove host activation or runtime execution")


if __name__ == "__main__":
    try:
        validate()
    except (ValueError, StopIteration) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
