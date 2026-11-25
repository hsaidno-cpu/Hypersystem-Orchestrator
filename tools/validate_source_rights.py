#!/usr/bin/env python3
"""Validate one-to-one source provenance and distribution-rights evidence."""
from __future__ import annotations
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
ELIGIBLE = {"installable_public", "installable_private"}
ALLOWED_RIGHTS = {
    "CLEARED_APACHE_2_0_CONDITIONAL",
    "NOT_DECLARED",
    "PRIVATE_NO_LICENSE",
    "REVIEW_REQUIRED_NONCOMMERCIAL",
    "DECLARED_APACHE_2_0_CANDIDATE_ONLY",
    "NOT_ASSESSED",
    "INHERITED_CANONICAL_RESTRICTED",
}


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def validate() -> None:
    catalog = load("catalog/plugins.json")
    dist = load("catalog/distribution-registry.json")
    rights = load("catalog/source-rights-registry.json")
    schema = load("catalog/source-rights-registry.schema.json")
    Draft202012Validator.check_schema(schema)
    schema_validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_errors = sorted(
        schema_validator.iter_errors(rights),
        key=lambda error: (list(map(str, error.absolute_path)), error.message),
    )
    if schema_errors:
        details = []
        for error in schema_errors[:10]:
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            details.append(f"{location}: {error.message}")
        suffix = f" (and {len(schema_errors) - 10} more)" if len(schema_errors) > 10 else ""
        raise ValueError("Source/rights registry does not conform to its JSON Schema: " + "; ".join(details) + suffix)
    records = rights.get("records", [])
    catalog_by_key = {item["plugin_key"]: item for item in catalog["plugins"]}
    dist_by_key = {item["plugin_key"]: item for item in dist["plugins"]}
    rights_by_key = {item["plugin_key"]: item for item in records}
    expected = set(catalog_by_key)
    if len(rights_by_key) != len(records) or set(rights_by_key) != expected:
        raise ValueError("Source/rights registry must map one-to-one to all catalog identities")
    if set(dist_by_key) != expected:
        raise ValueError("Distribution registry is not one-to-one with catalog")
    if rights.get("counts", {}).get("plugin_identity_count") != len(expected):
        raise ValueError("source-rights plugin_identity_count mismatch")
    for key, item in rights_by_key.items():
        cat, d = catalog_by_key[key], dist_by_key[key]
        if item.get("source_state") != cat.get("source_state") or item.get("source_state") != d.get("source_state"):
            raise ValueError(f"{key}: source_state mismatch across registries")
        right = item.get("rights", {})
        if right.get("license_status") not in ALLOWED_RIGHTS and right.get("license_status") not in {
            "CLEARED_APACHE_2_0_CONDITIONAL", "NOT_DECLARED", "PRIVATE_NO_LICENSE",
            "REVIEW_REQUIRED_NONCOMMERCIAL", "DECLARED_APACHE_2_0_CANDIDATE_ONLY",
            "NOT_ASSESSED", "INHERITED_CANONICAL_RESTRICTED"
        }:
            raise ValueError(f"{key}: unknown rights license_status")
        if item["distribution"].get("status") != d.get("distribution_status"):
            raise ValueError(f"{key}: distribution status drift")
        if item["distribution"].get("license_status") != d.get("license_status"):
            raise ValueError(f"{key}: distribution license_status drift")
        source = item.get("source", {})
        if source.get("repository_id") != item.get("source_repository_id"):
            raise ValueError(
                f"{key}: nested source.repository_id does not match source_repository_id"
            )
        if item["source_state"] == "integrated_submodule":
            if source.get("kind") != "canonical" or source.get("verification_state") != "SUBMODULE_PINNED":
                raise ValueError(f"{key}: integrated source must be a pinned canonical repository")
            if not source.get("repository_url") or not source.get("parent_pinned_commit"):
                raise ValueError(f"{key}: pinned source requires repository URL and immutable commit")
            if source.get("parent_pinned_commit") != d.get("source_commit"):
                raise ValueError(f"{key}: source pin differs from distribution registry")
        elif item["source_state"] == "candidate_repository":
            if source.get("kind") != "candidate" or source.get("verification_state") != "CANDIDATE_INCOMPLETE":
                raise ValueError(f"{key}: candidate source cannot be promoted to canonical")
            if not source.get("observed_head_sha") or source.get("parent_pinned_commit") is not None:
                raise ValueError(f"{key}: candidate requires observed head but no parent source pin")
            if right.get("license_status") != "DECLARED_APACHE_2_0_CANDIDATE_ONLY":
                raise ValueError(f"{key}: candidate rights must remain candidate-only")
        elif item["source_state"] == "pending_repository":
            if source.get("kind") != "not_identified" or source.get("repository_url") is not None:
                raise ValueError(f"{key}: pending repository cannot advertise a canonical URL")
            if right.get("license_status") != "NOT_ASSESSED":
                raise ValueError(f"{key}: pending repository rights must remain not assessed")
        elif item["source_state"] == "canonical_redirect":
            if source.get("kind") != "legacy_redirect" or source.get("canonical_plugin_key") != "asfree-canonical":
                raise ValueError(f"{key}: legacy redirect must point to A.S.F.R.E.E Canonical")
            if item["distribution"].get("status") != "legacy_redirect":
                raise ValueError(f"{key}: legacy redirect cannot be independently distributed")
        if item["distribution"].get("eligible_for_redistribution") is True:
            if item["distribution"].get("status") not in ELIGIBLE:
                raise ValueError(f"{key}: eligibility flag conflicts with distribution status")
            if right.get("license_status") != "CLEARED_APACHE_2_0_CONDITIONAL":
                raise ValueError(f"{key}: no eligible package without an explicit licensed rights basis")
    counts = rights["counts"]
    observed = {
        "official_pinned_source_count": sum(x["source_state"] == "integrated_submodule" for x in records),
        "not_identified_git_source_count": sum(x["source_state"] == "pending_repository" for x in records),
        "candidate_incomplete_count": sum(x["source_state"] == "candidate_repository" for x in records),
        "legacy_redirect_count": sum(x["source_state"] == "canonical_redirect" for x in records),
        "currently_installable_count": sum(x["distribution"]["eligible_for_redistribution"] for x in records),
    }
    for name, value in observed.items():
        if counts.get(name) != value:
            raise ValueError(f"{name}: expected {value}, recorded {counts.get(name)}")
    if counts["official_pinned_source_count"] != 5 or counts["not_identified_git_source_count"] != 15 or counts["candidate_incomplete_count"] != 2 or counts["legacy_redirect_count"] != 1:
        raise ValueError("Source migration baseline counts changed; re-audit before updating expectations")
    if counts["currently_installable_count"] != 0:
        raise ValueError("This reviewed source/rights baseline expects zero installable packages")
    print(f"PASS: {len(records)} source/rights records map one-to-one to {len(expected)} plugin identities")
    print("PASS: 5 pinned sources, 15 not identified, 2 incomplete candidates, 1 legacy redirect")
    print("PASS: source pins, candidate/pending boundaries and license/distribution statuses are consistent")
    print("NOTE: registry records provenance and blockers; it does not grant or transfer copyright")
    print("NOTE: 0 plugin packages are currently cleared for installation/distribution")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
