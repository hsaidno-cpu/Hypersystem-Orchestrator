"""CSO -> HSO shared-handoff serializer.

This module validates and serializes a CSO-local handoff into the strict HSO
shared envelope. It deliberately does not dispatch network requests or claim
that a plugin host has executed the handoff.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = ROOT / "contracts" / "plugin-handoff.schema.json"
CSO_PLUGIN_KEY = "cognitive-superintelligence-orchestrator"

HSO_EPISTEMIC_STATUSES = {
    "OBSERVED",
    "VERIFIED_SOURCE",
    "USER_CLAIM",
    "SOURCE_CLAIM",
    "ASSUMPTION",
    "INFERENCE",
    "HYPOTHESIS",
    "UNKNOWN",
}
HSO_CAPABILITY_STATUSES = {
    "READY",
    "READY_WITH_LIMITATIONS",
    "NOT_CHECKED",
    "UNAVAILABLE",
    "ACCESS_DENIED",
    "EXPIRED",
    "BLOCKED",
    "OUT_OF_SCOPE",
}
HSO_COMPLETION_STATUSES = {
    "NOT_STARTED",
    "IN_PROGRESS",
    "PARTIAL",
    "BLOCKED",
    "READY_FOR_HANDOFF",
    "VERIFIED",
    "FAILED",
}

# These aliases are explicitly lossy toward lower certainty, never stronger.
EPISTEMIC_ALIASES = {
    "OBSERVATION": "OBSERVED",
    "VERIFIED_SOURCE_CLAIM": "VERIFIED_SOURCE",
    "PREDICTION": "HYPOTHESIS",
}

LOCAL_FIELDS = {
    "handoff_id",
    "case_id",
    "intent",
    "scope",
    "epistemic_status",
    "capability_status",
    "expected_output",
    "acceptance_criteria",
    "non_goals",
    "inputs",
    "findings",
    "authority",
    "dependencies",
    "risk_and_unknowns",
    "completion_status",
}


class HandoffAdapterError(ValueError):
    """Raised when local CSO data cannot safely become an HSO envelope."""


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HandoffAdapterError(f"{label} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, label: str, *, minimum: int = 0) -> list[str]:
    if not isinstance(value, list):
        raise HandoffAdapterError(f"{label} must be an array of strings")
    if len(value) < minimum:
        raise HandoffAdapterError(f"{label} must contain at least {minimum} item(s)")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_text(item, f"{label}[{index}]"))
    return result


def map_epistemic_status(value: Any) -> str:
    local = _text(value, "epistemic status").upper()
    mapped = EPISTEMIC_ALIASES.get(local, local)
    if mapped not in HSO_EPISTEMIC_STATUSES:
        raise HandoffAdapterError(
            f"CSO epistemic label {local!r} has no safe HSO mapping; "
            "represent recommendations as expected_output and normative criteria "
            "as decision criteria instead of epistemic facts"
        )
    return mapped


def validate_hso_handoff(
    envelope: Mapping[str, Any],
    *,
    schema_path: Path | str = DEFAULT_SCHEMA_PATH,
) -> None:
    path = Path(schema_path)
    try:
        import json

        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise HandoffAdapterError(f"Cannot load HSO shared handoff schema: {exc}") from None

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(dict(envelope)),
        key=lambda error: (list(map(str, error.absolute_path)), error.message),
    )
    if errors:
        details = []
        for error in errors:
            field = ".".join(str(part) for part in error.absolute_path) or "<root>"
            details.append(f"{field}: {error.message}")
        raise HandoffAdapterError("HSO handoff schema validation failed: " + "; ".join(details))


def serialize_cso_handoff(
    local: Mapping[str, Any],
    *,
    source_version_or_commit: str,
    recipient_plugin_key: str,
    contract_version: str,
    schema_path: Path | str = DEFAULT_SCHEMA_PATH,
) -> dict[str, Any]:
    """Map a bounded CSO handoff DTO into the exact HSO shared schema.

    The recipient identity is supplied by the HSO router, not guessed from the
    child plugin catalog. Local-only keys and unsupported epistemic labels fail
    closed rather than leaking into the strict shared envelope.
    """
    if not isinstance(local, Mapping):
        raise HandoffAdapterError("CSO handoff input must be a mapping")

    unknown = sorted(set(local) - LOCAL_FIELDS)
    if unknown:
        raise HandoffAdapterError(
            "Unsupported CSO-local handoff field(s): " + ", ".join(unknown)
        )

    epistemic_raw = local.get("epistemic_status")
    if isinstance(epistemic_raw, str):
        epistemic_values = [epistemic_raw]
    elif isinstance(epistemic_raw, list):
        epistemic_values = epistemic_raw
    else:
        raise HandoffAdapterError("epistemic_status must be a string or an array of strings")
    if not epistemic_values:
        raise HandoffAdapterError("epistemic_status must not be empty")
    epistemic = list(dict.fromkeys(map_epistemic_status(value) for value in epistemic_values))

    capability = _text(local.get("capability_status"), "capability_status").upper()
    if capability not in HSO_CAPABILITY_STATUSES:
        raise HandoffAdapterError(f"Unsupported HSO capability_status: {capability}")

    envelope: dict[str, Any] = {
        "handoff_id": _text(local.get("handoff_id"), "handoff_id"),
        "case_id": _text(local.get("case_id"), "case_id"),
        "source_plugin": {
            "plugin_key": CSO_PLUGIN_KEY,
            "version_or_commit": _text(source_version_or_commit, "source_version_or_commit"),
        },
        "recipient_plugin": {
            "plugin_key": _text(recipient_plugin_key, "recipient_plugin_key"),
            "contract_version": _text(contract_version, "contract_version"),
        },
        "intent": _text(local.get("intent"), "intent"),
        "scope": _string_list(local.get("scope"), "scope"),
        "epistemic_status": epistemic,
        "capability_status": capability,
        "expected_output": _text(local.get("expected_output"), "expected_output"),
        "acceptance_criteria": _string_list(
            local.get("acceptance_criteria"), "acceptance_criteria", minimum=1
        ),
    }

    for key in ("non_goals", "dependencies", "risk_and_unknowns"):
        if key in local:
            envelope[key] = _string_list(local[key], key)

    if "inputs" in local:
        if not isinstance(local["inputs"], list):
            raise HandoffAdapterError("inputs must be an array")
        projected_inputs = []
        for index, item in enumerate(local["inputs"]):
            if not isinstance(item, Mapping):
                raise HandoffAdapterError(f"inputs[{index}] must be an object")
            allowed = {"locator", "provenance", "sensitivity"}
            unknown_input = sorted(set(item) - allowed)
            if unknown_input:
                raise HandoffAdapterError(
                    f"inputs[{index}] contains unsupported field(s): " + ", ".join(unknown_input)
                )
            projected = {
                "locator": _text(item.get("locator"), f"inputs[{index}].locator"),
                "provenance": _text(item.get("provenance"), f"inputs[{index}].provenance"),
            }
            if "sensitivity" in item:
                projected["sensitivity"] = _text(
                    item["sensitivity"], f"inputs[{index}].sensitivity"
                )
            projected_inputs.append(projected)
        envelope["inputs"] = projected_inputs

    if "findings" in local:
        if not isinstance(local["findings"], list):
            raise HandoffAdapterError("findings must be an array")
        projected_findings = []
        for index, finding in enumerate(local["findings"]):
            if not isinstance(finding, Mapping):
                raise HandoffAdapterError(f"findings[{index}] must be an object")
            unknown_finding = sorted(set(finding) - {"id", "status", "summary"})
            if unknown_finding:
                raise HandoffAdapterError(
                    f"findings[{index}] contains unsupported field(s): "
                    + ", ".join(unknown_finding)
                )
            projected_findings.append({
                "id": _text(finding.get("id"), f"findings[{index}].id"),
                "status": map_epistemic_status(finding.get("status")),
                "summary": _text(finding.get("summary"), f"findings[{index}].summary"),
            })
        envelope["findings"] = projected_findings

    if "authority" in local:
        authority = local["authority"]
        if not isinstance(authority, Mapping):
            raise HandoffAdapterError("authority must be an object")
        unknown_authority = sorted(set(authority) - {"level", "approval_reference"})
        if unknown_authority:
            raise HandoffAdapterError(
                "authority contains unsupported field(s): " + ", ".join(unknown_authority)
            )
        envelope["authority"] = {
            key: _text(value, f"authority.{key}")
            for key, value in authority.items()
        }

    if "completion_status" in local:
        completion = _text(local["completion_status"], "completion_status").upper()
        if completion not in HSO_COMPLETION_STATUSES:
            raise HandoffAdapterError(f"Unsupported HSO completion_status: {completion}")
        envelope["completion_status"] = completion

    validate_hso_handoff(envelope, schema_path=schema_path)
    return envelope
