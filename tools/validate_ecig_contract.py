#!/usr/bin/env python3
"""Validate HSO ECIG policy, attestation schema and cross-field invariants."""
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts" / "ecosystem-integrity-attestation.schema.json"
POLICY_PATH = ROOT / "governance" / "ecosystem-integrity-policy.json"


class ContractError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"Cannot load {path.relative_to(ROOT)}: {exc}") from None
    if not isinstance(value, dict):
        raise ContractError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def load_contract() -> tuple[dict[str, Any], dict[str, Any]]:
    schema = load_json(SCHEMA_PATH)
    policy = load_json(POLICY_PATH)
    Draft202012Validator.check_schema(schema)
    return schema, policy


def validate_policy(schema: dict[str, Any], policy: dict[str, Any]) -> None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ContractError("Attestation schema must use JSON Schema Draft 2020-12")
    if policy.get("schema_version") != "1.0.0" or policy.get("policy_id") != "HSO-ECIG":
        raise ContractError("ECIG policy identity or schema version is invalid")
    if policy.get("policy_version") != "1.0.0":
        raise ContractError("Unsupported ECIG policy version")
    states = policy.get("states") or {}
    declared_overall = states.get("overall")
    schema_overall = schema.get("properties", {}).get("overall_state", {}).get("enum")
    if declared_overall != schema_overall:
        raise ContractError("Policy overall states and attestation schema enum have drifted")
    required_sections = {
        "authority", "hashing", "freshness_hours_or_days", "states",
        "auto_actions", "human_approval_required", "never_automatic",
        "notion", "github", "event_delivery",
    }
    missing = sorted(required_sections - set(policy))
    if missing:
        raise ContractError("ECIG policy missing sections: " + ", ".join(missing))
    notion = policy.get("notion") or {}
    if notion.get("api_key_secret") != "HSO_NOTION_API_KEY":
        raise ContractError("ECIG must use the dedicated HSO_NOTION_API_KEY secret")
    if notion.get("enable_variable") != "HSO_ECIG_SYNC_ENABLED":
        raise ContractError("ECIG sync enable variable is not explicit")
    if notion.get("write_mode") != "allowlisted_properties_only":
        raise ContractError("ECIG Notion writes must remain allowlisted")
    never_automatic = set(policy.get("never_automatic") or [])
    forbidden = {
        "infer_human_approval_from_ci_success",
        "delete_evidence_to_clear_drift",
        "widen_credentials_after_authorization_failure",
    }
    if not forbidden.issubset(never_automatic):
        raise ContractError("ECIG policy lost a mandatory never-automatic safeguard")


def _error_path(error: Any) -> str:
    return ".".join(str(part) for part in error.absolute_path) or "<root>"


def validate_attestation(
    instance: dict[str, Any],
    schema: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> None:
    if schema is None or policy is None:
        schema, policy = load_contract()
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda item: (list(map(str, item.absolute_path)), item.message),
    )
    if errors:
        messages = [f"{_error_path(item)}: {item.message}" for item in errors]
        raise ContractError("Attestation schema validation failed: " + "; ".join(messages))

    if instance["policy_version"] != policy["policy_version"]:
        raise ContractError("Attestation policy_version does not match the loaded policy")

    instructions = instance["instructions"]
    file_entries = instructions.get("per_file_digests", [])
    if instructions["file_count"] != len(file_entries):
        raise ContractError("instructions.file_count does not match per_file_digests length")
    seen_paths: set[str] = set()
    for entry in file_entries:
        raw_path = entry["path"]
        path = PurePosixPath(raw_path)
        if (
            not raw_path
            or path.is_absolute()
            or any(part in {"", ".", ".."} for part in path.parts)
            or "\\" in raw_path
            or str(path) != raw_path
        ):
            raise ContractError(f"Instruction path is not a normalized relative POSIX path: {raw_path!r}")
        if raw_path in seen_paths:
            raise ContractError(f"Duplicate instruction manifest path: {raw_path}")
        seen_paths.add(raw_path)

    for index, approval in enumerate(instance.get("approvals", [])):
        if approval["decision"] == "APPROVED" and not str(approval.get("approver") or "").strip():
            raise ContractError(f"approvals[{index}] is APPROVED without an approver subject")

    if instance["rights"]["state"] == "UNCLEARED" and instance["overall_state"] not in {
        "BLOCKED", "APPROVAL_REQUIRED"
    }:
        raise ContractError("Uncleared rights must block synchronization or require approval")

    if instance["overall_state"] == "SYNCED":
        required_plane_states = {
            "source": "MATCH",
            "package": "MATCH",
            "installation": "MATCH",
            "instructions": "MATCH",
            "documentation": "MATCH",
        }
        mismatches = [
            f"{plane}.state={instance[plane]['state']}"
            for plane, required in required_plane_states.items()
            if instance[plane]["state"] != required
        ]
        if instance["rights"]["state"] != "CLEARED":
            mismatches.append(f"rights.state={instance['rights']['state']}")
        if mismatches:
            raise ContractError("SYNCED attestation has non-matching planes: " + ", ".join(mismatches))
        signature = instance["signature"]
        if signature["algorithm"] != "Ed25519":
            raise ContractError("SYNCED attestation signature algorithm must be Ed25519")
        try:
            decoded_signature = base64.b64decode(signature["value"], validate=True)
        except (ValueError, TypeError):
            raise ContractError("SYNCED attestation signature value is not canonical base64") from None
        if len(decoded_signature) != 64:
            raise ContractError("Ed25519 signature must decode to exactly 64 bytes")
        if instance.get("conflicts") or instance.get("limitations"):
            raise ContractError("SYNCED attestation cannot contain unresolved conflicts or limitations")

    if instance["overall_state"] == "DRIFT":
        if not any(
            instance[plane]["state"] == "DRIFT"
            for plane in ("source", "package", "installation", "instructions", "documentation")
        ):
            raise ContractError("DRIFT overall state requires at least one DRIFT plane")


def main() -> int:
    try:
        schema, policy = load_contract()
        validate_policy(schema, policy)
        print("PASS: JSON Schema Draft 2020-12 is valid")
        print("PASS: ECIG policy identity, state enum, authority and safety controls are consistent")
        print("PASS: attestation semantic rules are available for SYNCED, DRIFT, rights, signatures and file manifests")
        return 0
    except (ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
