#!/usr/bin/env python3
"""Validate the Hypersystem Orchestrator ecosystem catalog using stdlib only."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import subprocess
from datetime import date
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

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


def read_gitlink_sha(path: str) -> str:
    """Read the exact gitlink SHA from HEAD without initializing submodules."""
    try:
        completed = subprocess.run(
            ["git", "ls-tree", "HEAD", "--", path],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        fail(f"Cannot inspect gitlink for {path}: {exc}")
    lines = [line for line in completed.stdout.splitlines() if line.endswith("\t" + path)]
    if len(lines) != 1:
        fail(f"Expected exactly one git tree entry for submodule {path}; found {len(lines)}")
    metadata, _entry_path = lines[0].split("\t", 1)
    parts = metadata.split()
    if len(parts) != 3 or parts[0] != "160000" or parts[1] != "commit":
        fail(f"{path}: expected a gitlink (mode 160000, type commit), got {metadata}")
    return parts[2]


def git_blob_sha(content: bytes) -> str:
    """Return Git's SHA-1 object ID for a blob's exact byte content."""
    header = b"blob " + str(len(content)).encode("ascii") + b"\0"
    return hashlib.sha1(header + content).hexdigest()


def verify_source_manifest(repo: dict) -> str:
    """Verify a public source manifest at its immutable commit; fail closed."""
    repository_id = repo["repository_id"]
    visibility = repo.get("visibility")
    mode = repo.get("source_manifest_verification_mode")

    if visibility == "private":
        if mode != "PRIVATE_MANUAL_READBACK_ONLY":
            fail(f"{repository_id}: private source must be explicitly marked PRIVATE_MANUAL_READBACK_ONLY")
        # The public GitHub Actions workflow has no credential for private child repositories.
        # The exact manifest SHA/commit was manually read back by the authorized connector.
        return "PRIVATE_MANUAL_READBACK_ONLY"

    if visibility != "public":
        fail(f"{repository_id}: unsupported source visibility '{visibility}'")
    if mode != "CI_RAW_CONTENT_GIT_BLOB":
        fail(f"{repository_id}: public source must use CI_RAW_CONTENT_GIT_BLOB verification")
    full_name = repo.get("full_name", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", full_name):
        fail(f"{repository_id}: invalid GitHub owner/repository locator for manifest verification")
    manifest_path = repo.get("source_manifest_path", "")
    if not manifest_path or manifest_path.startswith("/") or ".." in manifest_path.split("/"):
        fail(f"{repository_id}: unsafe source_manifest_path")
    encoded_path = quote(manifest_path, safe="/._-")
    url = (
        f"https://raw.githubusercontent.com/{full_name}/"
        f"{repo['pinned_commit']}/{encoded_path}"
    )
    request = Request(url, headers={"User-Agent": "HSO-source-manifest-validator/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            content = response.read(1_048_577)
    except Exception as exc:
        fail(f"{repository_id}: could not read pinned source manifest from GitHub: {exc}")
    if len(content) > 1_048_576:
        fail(f"{repository_id}: source manifest exceeds 1 MiB validation limit")
    actual_blob_sha = git_blob_sha(content)
    if actual_blob_sha != repo["source_manifest_blob_sha"]:
        fail(
            f"{repository_id}: pinned source manifest blob SHA mismatch; "
            f"expected {repo['source_manifest_blob_sha']}, got {actual_blob_sha}"
        )
    try:
        manifest = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"{repository_id}: pinned source manifest is not valid UTF-8 JSON: {exc}")
    if manifest.get("version") != repo["source_manifest_version"]:
        fail(
            f"{repository_id}: pinned manifest version {manifest.get('version')!r} "
            f"does not match registered {repo['source_manifest_version']!r}"
        )
    if manifest.get("version") != repo.get("package_version"):
        fail(
            f"{repository_id}: pinned manifest version does not match repositories.json package_version"
        )
    return "CI_RAW_CONTENT_GIT_BLOB"


def validate():
    catalog = load_json(CATALOG_PATH)
    repo_doc = load_json(REPOSITORIES_PATH)
    plugins = catalog.get("plugins")
    repositories = repo_doc.get("repositories")

    if not isinstance(plugins, list) or not isinstance(repositories, list):
        fail("Catalog plugins and repositories must both be arrays")
    try:
        catalog_revision = date.fromisoformat(catalog.get("catalog_revision", ""))
    except (TypeError, ValueError):
        fail("catalog_revision must be an ISO-8601 calendar date")
    if catalog_revision > date.today():
        fail("catalog_revision must not be in the future")

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
            if plugin.get("repository_version") != repo.get("source_manifest_version"):
                fail(f"{key}: repository_version differs from the registered source manifest version")
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
        observed_metadata = plugin.get("platform_metadata_observed_at")
        try:
            observed_date = date.fromisoformat(observed_metadata or "")
        except (TypeError, ValueError):
            fail(f"{key}: platform_metadata_observed_at must be an ISO-8601 date")
        if observed_date > date.today():
            fail(f"{key}: Plugin Creator metadata observation date is in the future")
        if observed_date > catalog_revision:
            fail(f"{key}: Plugin Creator metadata observation date is later than catalog_revision")
        metadata_age_days = (date.today() - observed_date).days
        if metadata_age_days > 30:
            fail(
                f"{key}: Plugin Creator metadata is stale ({metadata_age_days} days); "
                "re-read current metadata and release ID before updating the registry"
            )

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
        parity = plugin.get("source_instruction_parity_status")
        if parity not in {"MATCH", "DRIFT_DETECTED", "NOT_COMPARED", "NOT_APPLICABLE"}:
            fail(f"{key}: invalid source_instruction_parity_status")
        if not plugin.get("source_instruction_parity_note"):
            fail(f"{key}: source_instruction_parity_note is required")
        if parity == "DRIFT_DETECTED" and plugin.get("source_sync_status") != "SOURCE_INSTRUCTION_DRIFT_DETECTED":
            fail(f"{key}: instruction drift must remain explicitly open")
        if parity == "MATCH" and plugin.get("source_sync_status") == "SOURCE_INSTRUCTION_DRIFT_DETECTED":
            fail(f"{key}: matching instruction state conflicts with drift status")
        for related in plugin.get("related_plugins", []):
            if related not in plugin_key_set:
                fail(f"{key}: unknown related plugin '{related}'")

    submodules = parse_submodules(GITMODULES_PATH)
    public_manifest_checks = 0
    private_manifest_skips = 0
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
            actual_gitlink_sha = read_gitlink_sha(path)
            if actual_gitlink_sha != repo["pinned_commit"]:
                fail(
                    f"{repo['repository_id']}: parent gitlink SHA {actual_gitlink_sha} "
                    f"does not match repositories.json pinned_commit {repo['pinned_commit']}"
                )
            manifest_fields = [
                "source_manifest_path",
                "source_manifest_blob_sha",
                "source_manifest_version",
                "source_manifest_commit",
                "source_manifest_verified_at",
            ]
            for field in manifest_fields:
                if not repo.get(field):
                    fail(f"{repo['repository_id']}: missing {field} for the pinned source manifest")
            if repo["source_manifest_commit"] != repo["pinned_commit"]:
                fail(f"{repo['repository_id']}: source manifest was not verified at its pinned commit")
            if not re.fullmatch(r"[0-9a-f]{40}", repo["source_manifest_blob_sha"]):
                fail(f"{repo['repository_id']}: source_manifest_blob_sha must be a 40-character SHA")
            if repo.get("package_version") != repo["source_manifest_version"]:
                fail(f"{repo['repository_id']}: package_version conflicts with source manifest version")
            try:
                date.fromisoformat(repo["source_manifest_verified_at"])
            except ValueError:
                fail(f"{repo['repository_id']}: source_manifest_verified_at must be an ISO-8601 date")
            verification_mode = verify_source_manifest(repo)
            if verification_mode == "CI_RAW_CONTENT_GIT_BLOB":
                public_manifest_checks += 1
            else:
                private_manifest_skips += 1
    if len(submodules) != 5:
        fail(f"Expected 5 verified source submodules at this stage, found {len(submodules)}")

    snapshot_index = load_json(ROOT / "catalog" / "instruction-snapshots.json")
    if len(snapshot_index.get("plugins", [])) != len(plugins):
        fail("Instruction snapshot index must contain all registered plugin identities")
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
    print(f"PASS: {len(plugins)} unique plugin identities")
    print(f"PASS: {len(repositories)} repository records")
    print(f"PASS: {len(submodules)} declared and pinned source submodules")
    print("PASS: parent gitlink SHAs equal registered source pins")
    print("PASS: integrated source manifest provenance is recorded and internally consistent")
    print(f"PASS: {public_manifest_checks} public source manifests fetched at pinned commits and Git-blob-hash/version verified")
    if private_manifest_skips:
        print(f"NOTE: {private_manifest_skips} private source manifest(s) require manual authorized read-back; CI does not claim to verify private repository contents")
    print("PASS: Plugin Creator metadata observations are no older than 30 days")
    print("PASS: source-state, alias, relationship and repository URL consistency")
    print("PASS: every plugin has a segregated instruction snapshot/pointer and explicit routing boundaries")
    print(f"PASS: {snapshot_index['total_skill_records']} indexed skill instruction records across {len(plugins)} plugins")

    compatibility = load_json(ROOT / "catalog" / "compatibility-matrix.json")
    integration_edges = compatibility.get("integrations")
    if not isinstance(integration_edges, list) or len(integration_edges) != compatibility.get("integration_count"):
        fail("Compatibility matrix integration_count does not match entries")
    integration_ids = [edge.get("integration_id") for edge in integration_edges]
    if len(integration_ids) != len(set(integration_ids)):
        fail("Duplicate compatibility integration_id detected")
    for edge in integration_edges:
        for field in ["producer_plugin","consumer_plugin","canonical_truth_owner","purpose","input_artifacts","output_artifact","contract_version","handoff_type","status","schema_contract_test","contract_behavior_test","runtime_execution_test","host_activation_test"]:
            if field not in edge or edge[field] in (None, ""):
                fail(f"Compatibility edge {edge.get('integration_id')}: missing {field}")
        for owner_field in ["producer_plugin","consumer_plugin","canonical_truth_owner"]:
            if edge[owner_field] not in plugin_key_set:
                fail(f"Compatibility edge {edge['integration_id']}: unknown {owner_field}")
        allowed_status = {"INTERFACE_DEFINED_NOT_EXECUTED","CONTRACT_TESTED","HOST_ACTIVATION_TESTED","RUNTIME_VERIFIED","BLOCKED","DEPRECATED"}
        test_states = {"NOT_RUN","PASS","FAIL"}
        if edge["status"] not in allowed_status:
            fail(f"Compatibility edge {edge['integration_id']}: invalid status")
        for field in ["schema_contract_test","contract_behavior_test","host_activation_test","runtime_execution_test"]:
            if edge[field] not in test_states:
                fail(f"Compatibility edge {edge['integration_id']}: invalid {field} state")
        if edge["status"] == "CONTRACT_TESTED" and not (edge["schema_contract_test"] == "PASS" and edge["contract_behavior_test"] == "PASS"):
            fail(f"Compatibility edge {edge['integration_id']}: CONTRACT_TESTED requires C2 and C3 PASS")
        if edge["status"] == "CONTRACT_TESTED" and (edge["host_activation_test"] != "NOT_RUN" or edge["runtime_execution_test"] != "NOT_RUN"):
            fail(f"Compatibility edge {edge['integration_id']}: C4/C5 must remain independent from C2/C3")
    if len(integration_edges) != 15:
        fail("Expected 15 defined compatibility edges for the current matrix")
    print(f"PASS: {len(integration_edges)} cross-plugin compatibility edges with explicit ownership and test states")
    print("NOTE: static checks do not prove host activation or runtime execution")


if __name__ == "__main__":
    try:
        validate()
    except (ValueError, StopIteration) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
