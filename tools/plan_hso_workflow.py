#!/usr/bin/env python3
"""Deterministic, plan-only dependency planner for HSO work packages."""
from __future__ import annotations

import argparse
import heapq
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "plugins.json"
PLANNER_VERSION = "0.1.0"

CAPABILITY_STATES = {
    "READY", "READY_WITH_LIMITATIONS", "NOT_CHECKED", "UNAVAILABLE",
    "ACCESS_DENIED", "EXPIRED", "BLOCKED", "OUT_OF_SCOPE",
}
AUTHORITY_RANK = {f"S{i}": i for i in range(6)}
MANDATORY_APPROVAL_SCOPES = {
    "CHILD_REPOSITORY_CHANGE", "EXTERNAL_SIDE_EFFECT", "PRODUCTION_RELEASE",
}
WRITE_SCOPE_MINIMUM = {
    "READ_ONLY": 0,
    "PARENT_REPOSITORY_BRANCH_WRITE": 3,
    "CHILD_REPOSITORY_CHANGE": 3,
    "EXTERNAL_SIDE_EFFECT": 4,
    "PRODUCTION_RELEASE": 5,
}
PLAN_FIELDS = {
    "schema_version", "case_id", "intent", "action_authority",
    "dispatch_requested", "work_packages",
}
PACKAGE_FIELDS = {
    "package_id", "primary_owner", "supporting_specialists", "depends_on",
    "capability_status", "capability_evidence", "write_scope",
    "requires_approval", "approval_status", "approval_reference",
    "expected_output", "acceptance_criteria",
}


class PlanError(ValueError):
    """The declared plan is structurally or semantically invalid."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PlanError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PlanError(
            f"Invalid JSON in {path} at line {exc.lineno}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise PlanError("The JSON root must be an object")
    return value


def _non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PlanError(f"{field} must be a non-empty string")
    return value.strip()


def _load_plugin_index(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    plugins = catalog.get("plugins")
    if not isinstance(plugins, list):
        raise PlanError("Catalog field 'plugins' must be an array")
    index: dict[str, dict[str, Any]] = {}
    for item in plugins:
        if not isinstance(item, dict):
            raise PlanError("Every catalog plugin record must be an object")
        key = _non_empty_string(item.get("plugin_key"), "catalog plugin_key")
        if key in index:
            raise PlanError(f"Catalog contains duplicate plugin_key: {key}")
        index[key] = item
    return index


def validate_plan(
    plan: dict[str, Any],
    catalog: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    unknown_plan_fields = set(plan) - PLAN_FIELDS
    if unknown_plan_fields:
        raise PlanError(
            "Unknown plan field(s): " + ", ".join(sorted(unknown_plan_fields))
        )
    if plan.get("schema_version") != "1.0.0":
        raise PlanError("schema_version must be '1.0.0'")
    _non_empty_string(plan.get("case_id"), "case_id")
    _non_empty_string(plan.get("intent"), "intent")

    authority = plan.get("action_authority")
    if authority not in AUTHORITY_RANK:
        raise PlanError("action_authority must be one of S0 through S5")
    if not isinstance(plan.get("dispatch_requested"), bool):
        raise PlanError("dispatch_requested must be a boolean")
    raw_packages = plan.get("work_packages")
    if not isinstance(raw_packages, list) or not raw_packages:
        raise PlanError("work_packages must be a non-empty array")

    plugin_index = _load_plugin_index(catalog)
    packages: dict[str, dict[str, Any]] = {}

    for raw in raw_packages:
        if not isinstance(raw, dict):
            raise PlanError("Every work package must be an object")
        package = dict(raw)
        unknown_package_fields = set(package) - PACKAGE_FIELDS
        if unknown_package_fields:
            raise PlanError(
                "Unknown field(s) in work package: "
                + ", ".join(sorted(unknown_package_fields))
            )
        package_id = _non_empty_string(package.get("package_id"), "package_id")
        if package_id in packages:
            raise PlanError(f"Duplicate package_id: {package_id}")

        owner = _non_empty_string(
            package.get("primary_owner"), f"{package_id}.primary_owner"
        )
        if owner not in plugin_index:
            raise PlanError(
                f"{package_id}: primary_owner '{owner}' is not in the plugin catalog"
            )
        if plugin_index[owner].get("source_state") == "canonical_redirect":
            raise PlanError(
                f"{package_id}: primary_owner '{owner}' is a legacy redirect, "
                "not an independent owner"
            )

        supporting = package.get("supporting_specialists")
        if not isinstance(supporting, list) or any(
            not isinstance(item, str)
            or not item.strip()
            or item != item.strip()
            for item in supporting
        ):
            raise PlanError(
                f"{package_id}: supporting_specialists must be an array "
                "of trimmed plugin keys"
            )
        if len(supporting) != len(set(supporting)):
            raise PlanError(
                f"{package_id}: supporting_specialists contains duplicates"
            )
        if owner in supporting:
            raise PlanError(
                f"{package_id}: primary_owner cannot also be a supporting specialist"
            )
        for specialist in supporting:
            if specialist not in plugin_index:
                raise PlanError(
                    f"{package_id}: supporting specialist '{specialist}' "
                    "is not in the plugin catalog"
                )
            if plugin_index[specialist].get("source_state") == "canonical_redirect":
                raise PlanError(
                    f"{package_id}: supporting specialist '{specialist}' "
                    "is a legacy redirect"
                )

        dependencies = package.get("depends_on")
        if not isinstance(dependencies, list) or any(
            not isinstance(item, str)
            or not item.strip()
            or item != item.strip()
            for item in dependencies
        ):
            raise PlanError(
                f"{package_id}: depends_on must be an array of trimmed package IDs"
            )
        if len(dependencies) != len(set(dependencies)):
            raise PlanError(f"{package_id}: depends_on contains duplicates")
        if package_id in dependencies:
            raise PlanError(
                f"{package_id}: a work package cannot depend on itself"
            )

        capability = package.get("capability_status")
        if capability not in CAPABILITY_STATES:
            raise PlanError(
                f"{package_id}: unsupported capability_status '{capability}'"
            )
        capability_evidence = package.get("capability_evidence")
        if capability in {"READY", "READY_WITH_LIMITATIONS"}:
            _non_empty_string(
                capability_evidence, f"{package_id}.capability_evidence"
            )
        elif capability_evidence not in (None, "") and not isinstance(
            capability_evidence, str
        ):
            raise PlanError(
                f"{package_id}: capability_evidence must be a string or null"
            )

        write_scope = package.get("write_scope")
        if write_scope not in WRITE_SCOPE_MINIMUM:
            raise PlanError(f"{package_id}: unsupported write_scope '{write_scope}'")
        requires_approval = package.get("requires_approval")
        if not isinstance(requires_approval, bool):
            raise PlanError(
                f"{package_id}: requires_approval must be a boolean"
            )
        approval_status = package.get("approval_status")
        if approval_status not in {"NOT_REQUIRED", "PENDING", "APPROVED", "DENIED"}:
            raise PlanError(
                f"{package_id}: invalid approval_status '{approval_status}'"
            )
        approval_reference = package.get("approval_reference")
        if approval_reference is not None and not isinstance(approval_reference, str):
            raise PlanError(
                f"{package_id}: approval_reference must be a string or null"
            )
        if approval_status == "APPROVED":
            _non_empty_string(
                approval_reference, f"{package_id}.approval_reference"
            )
        if write_scope in MANDATORY_APPROVAL_SCOPES and not requires_approval:
            raise PlanError(
                f"{package_id}: {write_scope} must require explicit approval"
            )
        if not requires_approval and approval_status != "NOT_REQUIRED":
            raise PlanError(
                f"{package_id}: approval_status must be NOT_REQUIRED "
                "when approval is false"
            )
        if requires_approval and approval_status == "NOT_REQUIRED":
            raise PlanError(
                f"{package_id}: approval_status cannot be NOT_REQUIRED "
                "when approval is required"
            )
        if AUTHORITY_RANK[authority] < WRITE_SCOPE_MINIMUM[write_scope]:
            package["_authority_blocked"] = True

        _non_empty_string(
            package.get("expected_output"), f"{package_id}.expected_output"
        )
        acceptance = package.get("acceptance_criteria")
        if not isinstance(acceptance, list) or not acceptance or any(
            not isinstance(item, str)
            or not item.strip()
            or item != item.strip()
            for item in acceptance
        ):
            raise PlanError(
                f"{package_id}: acceptance_criteria must contain "
                "at least one trimmed non-empty string"
            )
        packages[package_id] = package

    known_ids = set(packages)
    for package_id, package in packages.items():
        for dependency in package["depends_on"]:
            if dependency not in known_ids:
                raise PlanError(
                    f"{package_id}: unknown dependency '{dependency}'"
                )
    return plan, packages


def topological_order(
    packages: dict[str, dict[str, Any]],
) -> list[str]:
    """Return a deterministic topological order, preserving input order for ties."""
    input_index = {
        package_id: index for index, package_id in enumerate(packages)
    }
    indegree = {
        package_id: len(package["depends_on"])
        for package_id, package in packages.items()
    }
    dependents: dict[str, list[str]] = {
        package_id: [] for package_id in packages
    }
    for package_id, package in packages.items():
        for dependency in package["depends_on"]:
            dependents[dependency].append(package_id)

    ready = [
        (input_index[package_id], package_id)
        for package_id, degree in indegree.items()
        if degree == 0
    ]
    heapq.heapify(ready)
    ordered: list[str] = []
    while ready:
        _, current = heapq.heappop(ready)
        ordered.append(current)
        for dependent in dependents[current]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(
                    ready, (input_index[dependent], dependent)
                )
    if len(ordered) != len(packages):
        raise PlanError("Dependency cycle detected in work_packages")
    return ordered


def build_plan(
    plan: dict[str, Any],
    catalog: dict[str, Any],
) -> dict[str, Any]:
    plan, packages = validate_plan(plan, catalog)
    order = topological_order(packages)
    plugin_index = _load_plugin_index(catalog)
    package_results: list[dict[str, Any]] = []
    status_by_id: dict[str, str] = {}
    blocked_reasons: list[dict[str, str]] = []
    any_limited = False
    any_blocked = False

    for package_id in order:
        package = packages[package_id]
        blockers: list[str] = []
        limitations: list[str] = []

        if package.get("_authority_blocked"):
            blockers.append("ACTION_AUTHORITY_INSUFFICIENT")
        if package["capability_status"] not in {
            "READY", "READY_WITH_LIMITATIONS"
        }:
            blockers.append(f"CAPABILITY_{package['capability_status']}")
        elif package["capability_status"] == "READY_WITH_LIMITATIONS":
            limitations.append("CAPABILITY_READY_WITH_LIMITATIONS")
        if (
            package["requires_approval"]
            and package["approval_status"] != "APPROVED"
        ):
            blockers.append(f"APPROVAL_{package['approval_status']}")
        blocked_dependencies = [
            dependency for dependency in package["depends_on"]
            if status_by_id[dependency] == "BLOCKED"
        ]
        if blocked_dependencies:
            blockers.append(
                "DEPENDENCY_BLOCKED:" + ",".join(blocked_dependencies)
            )

        if blockers:
            readiness = "BLOCKED"
            any_blocked = True
        elif limitations:
            readiness = "READY_WITH_LIMITATIONS"
            any_limited = True
        else:
            readiness = "READY_FOR_REVIEW"

        status_by_id[package_id] = readiness
        for reason in blockers:
            blocked_reasons.append(
                {"package_id": package_id, "reason": reason}
            )
        package_results.append({
            "package_id": package_id,
            "primary_owner": package["primary_owner"],
            "primary_owner_source_state": plugin_index[
                package["primary_owner"]
            ].get("source_state", "UNKNOWN"),
            "supporting_specialists": package["supporting_specialists"],
            "depends_on": package["depends_on"],
            "readiness": readiness,
            "blockers": blockers,
            "limitations": limitations,
            "expected_output": package["expected_output"],
            "acceptance_criteria": package["acceptance_criteria"],
        })

    if plan["dispatch_requested"]:
        disposition = "BLOCKED_DISPATCH_UNAVAILABLE"
        blocked_reasons.append({
            "package_id": "*",
            "reason": "RUNTIME_DISPATCH_NOT_DEPLOYED",
        })
    elif any_blocked:
        disposition = "PLAN_VALIDATED_WITH_BLOCKERS"
    elif any_limited:
        disposition = "PLAN_VALIDATED_WITH_LIMITATIONS"
    else:
        disposition = "PLAN_VALIDATED"

    return {
        "plan_id": f"PLAN-{plan['case_id']}",
        "planner_version": PLANNER_VERSION,
        "mode": "PLAN_ONLY",
        "disposition": disposition,
        "dispatch_status": "NOT_AVAILABLE",
        "planned_order": order,
        "work_packages": package_results,
        "blocked_reasons": blocked_reasons,
        "limitations": [
            "The planner validates a declared plan; it does not infer plugin routes from natural language.",
            "Primary owners and supporting specialists are supplied by the caller and checked against the catalog.",
            "No plugin skill is invoked, no host/runtime dispatch occurs, and no external side effect is performed.",
            "A READY status is only as trustworthy as its supplied capability_evidence; the planner does not independently probe providers or hosts.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and order a declared HSO workflow plan (plan-only)."
    )
    parser.add_argument(
        "plan", type=Path, help="Path to a JSON workflow-plan input"
    )
    parser.add_argument(
        "--output", type=Path, help="Optional path for the JSON plan result"
    )
    args = parser.parse_args(argv)

    try:
        plan = load_json(args.plan)
        catalog = load_json(CATALOG_PATH)
        result = build_plan(plan, catalog)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            if args.output.resolve() == args.plan.resolve():
                raise PlanError("Output path must not overwrite the input plan")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except (PlanError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
