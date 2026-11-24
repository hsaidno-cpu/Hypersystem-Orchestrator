#!/usr/bin/env python3
"""Render the current HSO plugin version registry from canonical JSON records."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "plugins.json"
REPOSITORIES_PATH = ROOT / "catalog" / "repositories.json"
OUTPUT_PATH = ROOT / "docs" / "CURRENT-VERSION-REGISTRY.md"


def cell(value: object) -> str:
    if value is None or value == "":
        return "—"
    return str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ").strip()


def render(catalog: dict, repository_doc: dict) -> str:
    plugins = catalog["plugins"]
    repositories = {item["repository_id"]: item for item in repository_doc["repositories"]}
    names = {item["plugin_key"]: item["display_name"] for item in plugins}
    observed_dates = sorted({item["platform_metadata_observed_at"] for item in plugins})
    latest_observation = observed_dates[-1] if observed_dates else "UNKNOWN"

    lines = [
        "# Current Plugin Version Registry",
        "",
        "> **GENERATED FILE. DO NOT EDIT BY HAND.** Source: catalog/plugins.json and catalog/repositories.json. "
        "Regenerate with python tools/render_package_version_matrix.py --write; CI verifies it with --check.",
        "",
        f"**Registry revision:** {catalog['catalog_revision']}  ",
        f"**Plugin identities:** {len(plugins)} / {catalog['expected_plugin_count']}  ",
        f"**Plugin Creator release-metadata read-back:** {latest_observation}  ",
        "**Instruction snapshot index capture:** see catalog/instruction-snapshots.json",
        "",
        "## Version authority model",
        "",
        "The following values are independent and must never be collapsed into one generic version:",
        "",
        "1. **Plugin Creator package version and current release ID** — the installed/deployed package metadata in ChatGPT.",
        "2. **Canonical Git source version and immutable commit** — the source manifest version and pinned commit recorded by the parent repository.",
        "3. **Instruction-content parity** — direct file-level comparison of package files against the canonical source; matching version strings do not prove matching content.",
        "4. **Internal skill-header version / product label** — may be a separate label (for example v4.0.9 or V.01), not a package release.",
        "5. **Contract/schema version and runtime/adapter version** — separately governed interface and execution planes.",
        "6. **Instruction snapshot capture date and metadata observation date** — evidence timestamps, not software versions.",
        "",
        "## Current matrix",
        "",
        "| Plugin | Plugin Creator package | Current release ID | Git source version | Canonical source / pinned commit | Version alignment | Instruction parity | Source state | Metadata observed | Snapshot captured |",
        "|---|---:|---|---:|---|---|---|---|---|---|",
    ]

    for plugin in plugins:
        source_state = plugin["source_state"]
        repo = repositories.get(plugin.get("source_repository_id"))
        if source_state == "canonical_redirect":
            alias = plugin.get("alias_of")
            source_identity = f"Redirect only → {names.get(alias, alias or 'canonical target')}"
            source_version = "—"
        elif source_state == "candidate_repository":
            if repo:
                source_identity = f"{repo.get('full_name', repo['repository_id'])} (candidate; not pinned)"
            else:
                source_identity = "Candidate source; not pinned"
            source_version = "—"
        elif source_state == "pending_repository":
            source_identity = "NOT_IDENTIFIED"
            source_version = "—"
        elif repo and repo.get("pinned_commit"):
            source_identity = (
                f"{repo.get('full_name', repo['repository_id'])} @ "
                f"{repo['pinned_commit']}"
            )
            source_version = plugin.get("repository_version") or repo.get("source_manifest_version") or "—"
        else:
            source_identity = "Source locator unavailable"
            source_version = plugin.get("repository_version") or "—"

        lines.append("| " + " | ".join([
            cell(plugin["display_name"]),
            cell(plugin["platform_package_version"]),
            cell(plugin["platform_current_release_id"]),
            cell(source_version),
            cell(source_identity),
            cell(plugin["version_alignment_state"]),
            cell(plugin["source_instruction_parity_status"]),
            cell(source_state),
            cell(plugin["platform_metadata_observed_at"]),
            cell(plugin["instruction_capture_date"]),
        ]) + " |")

    lines.extend([
        "",
        "## Reconciliation findings requiring explicit disposition",
        "",
        "The following entries are not automatically repaired by changing a version string. Each requires the action listed below.",
        "",
    ])
    flagged = []
    for plugin in plugins:
        alignment = plugin.get("version_alignment_state")
        parity = plugin.get("source_instruction_parity_status")
        if alignment in {"SOURCE_AHEAD_OF_PLATFORM", "DEPLOYMENT_AHEAD_OF_SOURCE", "CANDIDATE_SOURCE_INCOMPLETE", "LEGACY_REDIRECT_VERSION"} or parity in {"DRIFT_DETECTED", "NOT_COMPARED"}:
            flagged.append(plugin)
    if not flagged:
        lines.append("No entries are currently flagged.")
    for plugin in flagged:
        lines.extend([
            f"### {plugin['display_name']}",
            "",
            f"- Plugin Creator: {plugin['platform_package_version']} / {plugin['platform_current_release_id']}.",
            f"- Git source: {plugin.get('repository_version') or 'NOT_IDENTIFIED'}.",
            f"- Alignment: {plugin['version_alignment_state']}; parity: {plugin['source_instruction_parity_status']}.",
            f"- Version evidence: {cell(plugin.get('version_alignment_note', 'No note recorded.'))}",
            f"- Parity evidence: {cell(plugin.get('source_instruction_parity_note', 'No parity note recorded.'))}",
            "",
        ])

    lines.extend([
        "## Canonical source manifest evidence",
        "",
        "| Repository | Manifest path | Manifest version | Manifest blob SHA | Pinned commit | Verified at |",
        "|---|---|---:|---|---|---|",
    ])
    for repo in repository_doc["repositories"]:
        if repo.get("status") not in {"integrated_submodule", "integrated_submodule_private"}:
            continue
        lines.append("| " + " | ".join([
            cell(repo.get("full_name")),
            cell(repo.get("source_manifest_path")),
            cell(repo.get("source_manifest_version")),
            cell(repo.get("source_manifest_blob_sha")),
            cell(repo.get("pinned_commit")),
            cell(repo.get("source_manifest_verified_at")),
        ]) + " |")

    lines.extend([
        "",
        "## Interpretation and release gates",
        "",
        "- SOURCE_AHEAD_OF_PLATFORM means the Git source manifest is ahead of the current ChatGPT package; the package remains at its observed release until an authorized package update is completed and read back.",
        "- DEPLOYMENT_AHEAD_OF_SOURCE means the current ChatGPT package is ahead of the canonical Git source. Do not rewrite source metadata to mimic the package; reconcile the complete package/source contents first.",
        "- SOURCE_AND_PLATFORM_MATCH describes version metadata only. DRIFT_DETECTED still blocks a claim of content parity.",
        "- NOT_IDENTIFIED and CANDIDATE_SOURCE_INCOMPLETE are intentional unknown/blocked states. Never fabricate a Git version from a package label.",
        "- NOT_COMPARED is not a pass. It means a defensible one-to-one file comparison was not available.",
        "- A release candidate remains an RC. It is not promoted to stable by being the highest source version.",
        "- Private packages stay private. A source version match does not grant redistribution or publication rights.",
        "",
        "## CI and freshness boundary",
        "",
        "tools/validate_catalog.py checks that every Plugin Creator metadata observation is at most 30 days old, that each integrated source manifest is pinned to the registered commit, and that the actual parent Git tree gitlink SHA equals catalog/repositories.json. tools/render_package_version_matrix.py --check ensures this document is generated from the canonical registry.",
        "",
        "**Important limitation:** the public GitHub Actions workflow does not query the private Plugin Creator service. The 30-day gate checks the recorded read-back date; it cannot independently prove that the date or external metadata is current. An authorized connector read-back must precede updates to the catalog.",
        "",
        "A green static CI run does not prove live ChatGPT host activation, package deployment, runtime execution, licensing clearance or human release approval.",
        "",
        "## Evidence snapshot",
        "",
        f"- Parent catalog revision: {catalog['catalog_revision']}.",
        f"- Platform metadata read-back dates represented: {', '.join(observed_dates)}.",
        f"- Parent source inventory date: {repository_doc.get('last_inventory_date', 'UNKNOWN')}.",
        "- Source pins are immutable commit identifiers; source manifest blob SHA identifies the exact version manifest inspected.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="fail if the committed registry differs from generated output")
    action.add_argument("--write", action="store_true", help="write the generated registry document")
    args = parser.parse_args()

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    repository_doc = json.loads(REPOSITORIES_PATH.read_text(encoding="utf-8"))
    expected = render(catalog, repository_doc)

    if args.write:
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
        print(f"WROTE: {OUTPUT_PATH.relative_to(ROOT)}")
        return 0
    if args.check:
        actual = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if actual != expected:
            print(
                f"FAIL: {OUTPUT_PATH.relative_to(ROOT)} is stale. "
                "Run python tools/render_package_version_matrix.py --write.",
                file=sys.stderr,
            )
            return 1
        print("PASS: current version registry matches canonical catalog data")
        return 0
    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
