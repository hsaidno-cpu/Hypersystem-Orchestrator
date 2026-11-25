#!/usr/bin/env python3
"""Validate HSO ECIG policy, attestations, evidence freshness and signatures."""
from __future__ import annotations

import base64
import hashlib
import json
import math
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts" / "ecosystem-integrity-attestation.schema.json"
POLICY_PATH = ROOT / "governance" / "ecosystem-integrity-policy.json"
TRUSTED_KEYS_PATH = ROOT / "governance" / "ecig-trusted-public-keys.json"
CLOCK_SKEW = timedelta(minutes=5)
EXAMPLE_PATH = ROOT / "examples" / "ecig-attestation-unknown.example.json"

# Policy can tighten these windows, but cannot silently relax the normative
# maximum ages documented by ECIG without a code and policy review.
FRESHNESS_UPPER_BOUNDS = {
    "source_commit_hours": 24,
    "package_metadata_days": 30,
    "installation_runtime_receipt_hours": 24,
    "instruction_parity_hours": 24,
    "documentation_projection_days": 7,
}

MANDATORY_HUMAN_APPROVALS = {
    "canonical_source_selection_or_replacement",
    "ownership_license_or_redistribution_disposition",
    "package_publication_republication_or_release_channel_promotion",
    "target_install_upgrade_enable_disable_or_uninstall",
    "instruction_overwrite_or_cross_plane_content_replacement",
    "production_permission_secret_scope_or_trust_policy_change",
    "milestone_acceptance_security_disposition_or_production_readiness",
}

MANDATORY_NEVER_AUTOMATIC = {
    "copy_arbitrary_notion_prose_into_canonical_source",
    "rewrite_source_or_package_to_force_checksum_match",
    "publish_or_install_because_a_newer_git_commit_exists",
    "infer_human_approval_from_ci_success",
    "delete_evidence_to_clear_drift",
    "widen_credentials_after_authorization_failure",
    "promote_unknown_stale_or_not_compared_to_pass",
}


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


def _decode_canonical_base64(value: Any, label: str) -> bytes:
    if not isinstance(value, str):
        raise ContractError(f"{label} must be a base64 string")
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, TypeError):
        raise ContractError(f"{label} is not valid base64") from None
    if base64.b64encode(decoded).decode("ascii") != value:
        raise ContractError(f"{label} must use canonical base64 encoding")
    return decoded


def load_trusted_public_keys(path: Path = TRUSTED_KEYS_PATH) -> dict[str, str]:
    """Load active Ed25519 public keys. An empty trust store intentionally fails closed."""
    value = load_json(path)
    if value.get("schema_version") != "1.0.0" or value.get("algorithm") != "Ed25519":
        raise ContractError("ECIG trusted-key registry identity or algorithm is invalid")
    entries = value.get("keys")
    if not isinstance(entries, list):
        raise ContractError("ECIG trusted-key registry keys must be an array")

    trusted: dict[str, str] = {}
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ContractError(f"Trusted key entry {index} must be an object")
        key_id = str(entry.get("key_id") or "").strip()
        status = entry.get("status")
        public_key = entry.get("public_key_base64")
        if not key_id or key_id in seen:
            raise ContractError(f"Trusted key entry {index} has a blank or duplicate key_id")
        seen.add(key_id)
        if status not in {"ACTIVE", "REVOKED"}:
            raise ContractError(f"Trusted key {key_id} has an unsupported status")
        decoded = _decode_canonical_base64(public_key, f"Trusted key {key_id} public_key_base64")
        if len(decoded) != 32:
            raise ContractError(f"Trusted key {key_id} must contain a 32-byte Ed25519 public key")
        if status == "ACTIVE":
            trusted[key_id] = public_key
    return trusted


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

    authority = policy.get("authority") or {}
    if authority.get("human_decision_authority") != "GOV-01":
        raise ContractError("ECIG human decision authority must remain GOV-01")
    if authority.get("human_decision_subject") != "hsaidno-cpu":
        raise ContractError("ECIG GOV-01 subject does not match the canonical owner")
    if authority.get("additional_human_approvers") != []:
        raise ContractError("ECIG must not introduce a second human approver")

    required_sections = {
        "authority", "hashing", "freshness_hours_or_days", "states",
        "auto_actions", "human_approval_required", "never_automatic",
        "notion", "github", "event_delivery", "signature",
    }
    missing = sorted(required_sections - set(policy))
    if missing:
        raise ContractError("ECIG policy missing sections: " + ", ".join(missing))

    freshness = policy.get("freshness_hours_or_days")
    if not isinstance(freshness, dict):
        raise ContractError("ECIG freshness_hours_or_days must be an object")
    for field, upper_bound in FRESHNESS_UPPER_BOUNDS.items():
        value = freshness.get(field)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or value <= 0
            or value > upper_bound
            or (isinstance(value, float) and not math.isfinite(value))
        ):
            raise ContractError(
                f"ECIG freshness policy {field} must be a finite positive number "
                f"no greater than {upper_bound}"
            )

    required_approvals = set(policy.get("human_approval_required") or [])
    if not MANDATORY_HUMAN_APPROVALS.issubset(required_approvals):
        raise ContractError("ECIG policy lost a mandatory human-approval action")

    never_automatic = policy.get("never_automatic")
    if not isinstance(never_automatic, list) or not MANDATORY_NEVER_AUTOMATIC.issubset(set(never_automatic)):
        raise ContractError("ECIG policy lost a mandatory never-automatic safeguard")

    notion = policy.get("notion") or {}
    if notion.get("api_key_secret") != "HSO_NOTION_API_KEY":
        raise ContractError("ECIG must use the dedicated HSO_NOTION_API_KEY secret")
    if notion.get("enable_variable") != "HSO_ECIG_SYNC_ENABLED":
        raise ContractError("ECIG sync enable variable is not explicit")
    if notion.get("write_mode") != "allowlisted_properties_only":
        raise ContractError("ECIG Notion writes must remain allowlisted")

    github = policy.get("github") or {}
    expected_permissions = ["contents:read", "pull-requests:read", "actions:read"]
    actual_permissions = github.get("evidence_permissions")
    if (
        not isinstance(actual_permissions, list)
        or len(actual_permissions) != len(set(actual_permissions))
        or set(actual_permissions) != set(expected_permissions)
    ):
        raise ContractError("ECIG GitHub evidence permissions must be the exact read-only allowlist")
    if github.get("source_changes") != "pull_request_only":
        raise ContractError("ECIG source changes must remain pull-request-only")
    if github.get("privileged_pull_request_rule") != "trusted_base_checkout_only_never_execute_untrusted_head_code":
        raise ContractError("ECIG privileged pull-request rule has been relaxed or changed")
    if github.get("default_branch") != "main":
        raise ContractError("ECIG canonical default branch must remain main")

    signature = policy.get("signature") or {}
    if signature.get("algorithm") != "Ed25519":
        raise ContractError("ECIG signature algorithm must remain Ed25519")
    if signature.get("payload_version") != "HSO-ECIG-JSON-1":
        raise ContractError("Unsupported ECIG signature payload version")
    if signature.get("canonicalization") != "UTF-8_JSON_SORT_KEYS_COMPACT_SEPARATORS_ENSURE_ASCII_FALSE":
        raise ContractError("ECIG signature canonicalization has drifted")
    if signature.get("exclude_root_field") != "signature":
        raise ContractError("ECIG signature must exclude only the root signature field")
    if signature.get("trust_store_path") != str(TRUSTED_KEYS_PATH.relative_to(ROOT)):
        raise ContractError("ECIG trusted-key registry path has drifted")
    if signature.get("trust_store_update") != "GOV-01_signed_exact_head_disposition_and_audited_key_ceremony":
        raise ContractError("ECIG trust-root updates must use the sole GOV-01 signed exact-head decision")
    if signature.get("evidence_proof_version") != "HSO-ECIG-EVIDENCE-1":
        raise ContractError("Unsupported ECIG evidence proof version")

    never_automatic = set(policy.get("never_automatic") or [])
    forbidden = {
        "infer_human_approval_from_ci_success",
        "delete_evidence_to_clear_drift",
        "widen_credentials_after_authorization_failure",
    }
    if not forbidden.issubset(never_automatic):
        raise ContractError("ECIG policy lost a mandatory never-automatic safeguard")


def _canonical_json_bytes(payload: Any, label: str) -> bytes:
    try:
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise ContractError(f"{label} cannot be represented as canonical JSON") from None


def attestation_signing_bytes(instance: dict[str, Any]) -> bytes:
    """Return HSO-ECIG-JSON-1 bytes; the root signature field is excluded."""
    payload = {key: value for key, value in instance.items() if key != "signature"}
    return _canonical_json_bytes(payload, "Attestation")


def _evidence_claim(instance: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    """Return the exact claim/target that this evidence record is permitted to support."""
    kind = evidence["kind"]
    context = {
        "schema_version": instance["schema_version"],
        "policy_version": instance["policy_version"],
        "attestation_id": instance["attestation_id"],
        "plugin_key": instance["plugin_key"],
        "target": instance["target"],
        "kind": kind,
    }
    source = instance["source"]
    if kind == "COMMIT":
        subject = {
            "repository_url": source["repository_url"],
            "ref": source["ref"],
            "commit_sha": source["commit_sha"],
        }
    elif kind == "MANIFEST":
        subject = {
            "manifest_path": source["manifest_path"],
            "manifest_sha256": source["manifest_sha256"],
            "tree_digest": source["tree_digest"],
            "commit_sha": source["commit_sha"],
        }
    elif kind == "PACKAGE_READBACK":
        subject = {"package": instance["package"]}
    elif kind == "INSTALL_RECEIPT":
        subject = {
            "package_id": instance["package"].get("package_id"),
            "release_id": instance["package"].get("release_id"),
            "target": instance["target"],
            "installation": {
                key: value for key, value in instance["installation"].items()
                if key not in {"runtime_state", "runtime_identity", "probe_id"}
            },
        }
    elif kind == "RUNTIME_PROBE":
        subject = {
            "target": instance["target"],
            "package_id": instance["package"].get("package_id"),
            "release_id": instance["package"].get("release_id"),
            "runtime": {
                key: instance["installation"].get(key)
                for key in ("runtime_state", "runtime_identity", "probe_id")
            },
        }
    elif kind == "INSTRUCTION_COMPARISON":
        subject = {"instructions": instance["instructions"]}
    elif kind == "DOCUMENTATION_READBACK":
        subject = {"documentation": instance["documentation"]}
    elif kind == "HUMAN_DECISION":
        matches = [
            approval for approval in instance.get("approvals", [])
            if approval.get("decision_reference") == evidence.get("locator")
        ]
        if len(matches) != 1:
            raise ContractError("HUMAN_DECISION evidence must identify exactly one approval record")
        subject = {"approval": matches[0]}
    else:
        subject = {"source_evidence_sha256": evidence.get("sha256")}
    return {"context": context, "subject": subject}


def evidence_binding_sha256(instance: dict[str, Any], evidence: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json_bytes(
        _evidence_claim(instance, evidence), "Evidence claim"
    )).hexdigest()


def evidence_signing_bytes(instance: dict[str, Any], evidence: dict[str, Any]) -> bytes:
    """Return HSO-ECIG-EVIDENCE-1 bytes signed by the trusted evidence verifier."""
    payload = {
        "proof_version": "HSO-ECIG-EVIDENCE-1",
        "attestation_id": instance["attestation_id"],
        "policy_version": instance["policy_version"],
        "plugin_key": instance["plugin_key"],
        "target": instance["target"],
        "kind": evidence["kind"],
        "locator": evidence["locator"],
        "observed_at": evidence["observed_at"],
        "verifier": evidence["verifier"],
        "sha256": evidence["sha256"],
        "binding_sha256": evidence["binding_sha256"],
    }
    return _canonical_json_bytes(payload, "Evidence proof")


def _parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{label} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ContractError(f"{label} must be an ISO-8601 timestamp") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ContractError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _validate_freshness(
    instance: dict[str, Any],
    policy: dict[str, Any],
    now: datetime,
) -> None:
    observed_at = _parse_timestamp(instance["observed_at"], "observed_at")
    if observed_at > now + CLOCK_SKEW:
        raise ContractError("SYNCED attestation observed_at is in the future")
    if now - observed_at > timedelta(hours=24):
        raise ContractError("SYNCED attestation observed_at is older than the 24-hour source freshness window")

    freshness = policy["freshness_hours_or_days"]
    requirements = {
        "source": (
            ("COMMIT", "MANIFEST"),
            timedelta(hours=float(freshness["source_commit_hours"])),
        ),
        "package": (
            ("PACKAGE_READBACK",),
            timedelta(days=float(freshness["package_metadata_days"])),
        ),
        "installation": (
            ("INSTALL_RECEIPT", "RUNTIME_PROBE"),
            timedelta(hours=float(freshness["installation_runtime_receipt_hours"])),
        ),
        "instructions": (
            ("INSTRUCTION_COMPARISON",),
            timedelta(hours=float(freshness["instruction_parity_hours"])),
        ),
        "documentation": (
            ("DOCUMENTATION_READBACK",),
            timedelta(days=float(freshness["documentation_projection_days"])),
        ),
    }
    evidence_by_kind: dict[str, list[tuple[datetime, dict[str, Any]]]] = {}
    for item in instance.get("evidence", []):
        timestamp = _parse_timestamp(item["observed_at"], f"evidence[{item['kind']}].observed_at")
        if timestamp > observed_at + CLOCK_SKEW:
            raise ContractError(f"Evidence {item['kind']} is newer than the parent attestation observation")
        evidence_by_kind.setdefault(item["kind"], []).append((timestamp, item))

    for plane, (required_kinds, max_age) in requirements.items():
        for kind in required_kinds:
            observations = evidence_by_kind.get(kind, [])
            if not observations:
                raise ContractError(f"SYNCED requires plane-specific {kind} evidence for {plane}")
            latest = max(timestamp for timestamp, _ in observations)
            if latest > now + CLOCK_SKEW:
                raise ContractError(f"{kind} evidence timestamp is in the future")
            if now - latest > max_age:
                raise ContractError(f"{kind} evidence exceeds the freshness window for {plane}")


def _validate_synced_approvals(
    instance: dict[str, Any],
    policy: dict[str, Any],
    observed_at: datetime,
) -> None:
    approvals = instance.get("approvals", [])
    human_decisions: dict[str, dict[str, Any]] = {}
    for evidence in instance.get("evidence", []):
        if evidence["kind"] != "HUMAN_DECISION":
            continue
        locator = str(evidence.get("locator") or "").strip()
        if not locator:
            raise ContractError("HUMAN_DECISION evidence requires a non-empty locator")
        if not evidence.get("sha256"):
            raise ContractError("HUMAN_DECISION evidence requires a SHA-256 digest")
        if locator in human_decisions:
            raise ContractError(f"Duplicate HUMAN_DECISION evidence locator: {locator}")
        human_decisions[locator] = evidence

    for index, approval in enumerate(approvals):
        if approval["decision"] != "APPROVED":
            raise ContractError(
                f"SYNCED cannot contain unresolved or rejected approval at approvals[{index}]"
            )
        if approval.get("approver") != policy["authority"]["human_decision_subject"]:
            raise ContractError(
                f"approvals[{index}] must be approved by the sole GOV-01 decision authority"
            )
        decided_at = _parse_timestamp(approval["decided_at"], f"approvals[{index}].decided_at")
        if decided_at > observed_at + CLOCK_SKEW:
            raise ContractError(f"approvals[{index}] is newer than the parent attestation observation")

        decision_reference = str(approval.get("decision_reference") or "").strip()
        decision_evidence = human_decisions.get(decision_reference)
        if decision_evidence is None:
            raise ContractError(
                f"approvals[{index}] decision_reference has no matching HUMAN_DECISION evidence"
            )
        if decision_evidence.get("verifier") != policy["authority"]["human_decision_subject"]:
            raise ContractError("HUMAN_DECISION evidence must be verified by GOV-01")
        decision_evidence_at = _parse_timestamp(
            decision_evidence["observed_at"],
            f"HUMAN_DECISION[{index}].observed_at",
        )
        if decision_evidence_at < decided_at - CLOCK_SKEW:
            raise ContractError(
                f"approvals[{index}] HUMAN_DECISION evidence predates the recorded decision"
            )

    required_actions: set[str] = set()
    if instance["source"]["state"] == "MATCH":
        required_actions.add("canonical_source_selection_or_replacement")
    if instance["rights"]["state"] == "CLEARED":
        required_actions.add("ownership_license_or_redistribution_disposition")
    if instance["package"]["publication_state"] == "PUBLISHED":
        required_actions.add("package_publication_republication_or_release_channel_promotion")
    if instance["installation"]["install_state"] == "INSTALLED":
        required_actions.add("target_install_upgrade_enable_disable_or_uninstall")

    policy_actions = set(policy.get("human_approval_required") or [])
    if not required_actions.issubset(policy_actions):
        raise ContractError("ECIG policy is missing a required human approval action")

    approved_actions = {
        approval["action"]
        for approval in approvals
        if approval["decision"] == "APPROVED" and str(approval.get("approver") or "").strip()
    }
    missing = sorted(required_actions - approved_actions)
    if missing:
        raise ContractError("SYNCED is missing required human approval records: " + ", ".join(missing))


def _verify_ed25519_signature(
    instance: dict[str, Any],
    trusted_public_keys: Mapping[str, str],
) -> None:
    signature = instance.get("signature")
    if not isinstance(signature, dict):
        raise ContractError("SYNCED attestation requires a verifiable Ed25519 signature")
    if signature.get("algorithm") != "Ed25519":
        raise ContractError("SYNCED attestation signature algorithm must be Ed25519")

    key_id = str(signature.get("key_id") or "").strip()
    if not key_id:
        raise ContractError("SYNCED attestation signature key_id must be non-empty")
    public_key_value = trusted_public_keys.get(key_id)
    if public_key_value is None:
        raise ContractError(f"SYNCED attestation key_id is not trusted: {key_id}")

    signature_bytes = _decode_canonical_base64(signature.get("value"), "Ed25519 signature")
    if len(signature_bytes) != 64:
        raise ContractError("Ed25519 signature must decode to exactly 64 bytes")
    public_key_bytes = _decode_canonical_base64(public_key_value, f"Trusted key {key_id}")
    if len(public_key_bytes) != 32:
        raise ContractError(f"Trusted key {key_id} must contain a 32-byte Ed25519 public key")

    try:
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(
            signature_bytes,
            attestation_signing_bytes(instance),
        )
    except InvalidSignature:
        raise ContractError("SYNCED attestation Ed25519 signature verification failed") from None
    except ValueError:
        raise ContractError("Trusted Ed25519 public key is malformed") from None


def _verify_synced_evidence_proofs(
    instance: dict[str, Any],
    trusted_public_keys: Mapping[str, str],
) -> None:
    """Authenticate verifiers and bind signed digests to exact claim/action/target tuples.

    The trusted verifier computes sha256 from the exact bytes it reads at locator.
    The validator deliberately does not dereference arbitrary locators: it verifies
    the verifier's signature over that digest, locator, timestamp and canonical
    target-bound claim, avoiding SSRF and non-deterministic network reads.
    """
    owner_key_id = instance["signature"]["key_id"]
    for index, evidence in enumerate(instance.get("evidence", [])):
        digest = evidence.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ContractError(f"evidence[{index}] must contain a SHA-256 digest")
        try:
            int(digest, 16)
        except ValueError:
            raise ContractError(f"evidence[{index}].sha256 must be lowercase hexadecimal") from None

        expected_binding = evidence_binding_sha256(instance, evidence)
        if evidence.get("binding_sha256") != expected_binding:
            raise ContractError(
                f"evidence[{index}] binding digest does not match its claim, action, and target"
            )

        proof = evidence.get("proof")
        if not isinstance(proof, dict) or proof.get("algorithm") != "Ed25519":
            raise ContractError(f"evidence[{index}] requires a verifiable Ed25519 verifier proof")
        key_id = str(proof.get("key_id") or "").strip()
        public_key_value = trusted_public_keys.get(key_id)
        if not key_id or public_key_value is None:
            raise ContractError(f"evidence[{index}] verifier key is not trusted: {key_id or '<blank>'}")

        signature_bytes = _decode_canonical_base64(
            proof.get("value"), f"evidence[{index}] verifier signature"
        )
        if len(signature_bytes) != 64:
            raise ContractError(f"evidence[{index}] verifier signature must be 64 bytes")
        public_key_bytes = _decode_canonical_base64(
            public_key_value, f"Trusted evidence verifier {key_id}"
        )
        if len(public_key_bytes) != 32:
            raise ContractError(f"Trusted evidence verifier {key_id} must be a 32-byte Ed25519 key")
        try:
            Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(
                signature_bytes, evidence_signing_bytes(instance, evidence)
            )
        except InvalidSignature:
            raise ContractError(f"evidence[{index}] verifier proof signature verification failed") from None
        except ValueError:
            raise ContractError(f"Trusted evidence verifier {key_id} is malformed") from None

        if evidence["kind"] == "HUMAN_DECISION" and key_id != owner_key_id:
            raise ContractError("HUMAN_DECISION proof must use the GOV-01 attestation signing key")


def _error_path(error: Any) -> str:
    return ".".join(str(part) for part in error.absolute_path) or "<root>"


def validate_attestation(
    instance: dict[str, Any],
    schema: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
    *,
    trusted_public_keys: Mapping[str, str] | None = None,
    now: datetime | None = None,
) -> None:
    if schema is None or policy is None:
        schema, policy = load_contract()
    # Library/API callers must not bypass anti-weakening bounds by avoiding the CLI.
    validate_policy(schema, policy)
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
        normalized_path = unicodedata.normalize("NFC", raw_path)
        if normalized_path in seen_paths:
            raise ContractError(f"Duplicate instruction manifest path after NFC normalization: {normalized_path}")
        if raw_path != normalized_path:
            raise ContractError(f"Instruction manifest path must already be Unicode NFC normalized: {raw_path!r}")
        path = PurePosixPath(normalized_path)
        if (
            not raw_path
            or path.is_absolute()
            or any(part in {"", ".", ".."} for part in path.parts)
            or "\\" in raw_path
            or "\x00" in raw_path
            or str(path) != raw_path
        ):
            raise ContractError(f"Instruction path is not a normalized relative POSIX path: {raw_path!r}")
        seen_paths.add(normalized_path)

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
        if instance.get("conflicts") or instance.get("limitations"):
            raise ContractError("SYNCED attestation cannot contain unresolved conflicts or limitations")

        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None or current_time.utcoffset() is None:
            raise ContractError("Validation clock must be timezone-aware")
        current_time = current_time.astimezone(timezone.utc)
        observed_at = _parse_timestamp(instance["observed_at"], "observed_at")
        _validate_freshness(instance, policy, current_time)
        _validate_synced_approvals(instance, policy, observed_at)

        keys = trusted_public_keys
        if keys is None:
            keys = load_trusted_public_keys()
        _verify_ed25519_signature(instance, keys)
        _verify_synced_evidence_proofs(instance, keys)

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
        trusted_keys = load_trusted_public_keys()
        example = load_json(EXAMPLE_PATH)
        validate_attestation(example, schema, policy, trusted_public_keys=trusted_keys)
        print("PASS: JSON Schema Draft 2020-12 is valid")
        print("PASS: checked-in UNKNOWN example validates against the attestation contract")
        print("PASS: ECIG policy identity, read-only GitHub permissions and safety controls are enforced")
        print("PASS: Ed25519 signature verification and plane-specific freshness rules are implemented")
        if trusted_keys:
            print(f"PASS: {len(trusted_keys)} active Ed25519 public key(s) loaded from the reviewed trust registry")
        else:
            print("NOTE: no active Ed25519 trust key is provisioned; SYNCED attestations fail closed until an approved key is added")
        return 0
    except (ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
