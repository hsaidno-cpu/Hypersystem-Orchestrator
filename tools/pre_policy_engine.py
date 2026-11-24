#!/usr/bin/env python3
"""Fail-closed PRE R0-R9 transition policy evaluator.

This module evaluates a proposed transition. It does not write Notion roadmap
properties or self-approve a gate. A host adapter must apply an ALLOW decision
with compare-and-swap against the canonical source and preserve the receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "governance" / "pre-r0-r9-policy.json"


class PREPolicyError(RuntimeError):
    """Raised when policy input cannot be safely evaluated."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp is missing")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


EVIDENCE_ATTESTED_FIELDS = (
    "schema_version", "evidence_id", "evidence_type", "project_id", "scope_id",
    "state", "freshness", "verified", "identity_verified", "verified_by", "verifier_role",
    "verified_at", "issuer", "source_locator", "sha256",
)


def evidence_attestation_payload(item: dict[str, Any]) -> dict[str, Any]:
    """Return the only fields covered by the evidence issuer signature."""
    return {key: item.get(key) for key in EVIDENCE_ATTESTED_FIELDS}


def sign_evidence_envelope(item: dict[str, Any], secret: str) -> str:
    """Issuer-side helper; call only after authenticating verifier identity and source."""
    if not secret:
        raise PREPolicyError("Evidence signing key is not configured")
    payload = evidence_attestation_payload(item)
    return hmac.new(
        secret.encode("utf-8"),
        canonical_json(payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PREPolicyError(f"Unable to load PRE policy ({exc.__class__.__name__})") from None
    if policy.get("policy_id") != "hso.pre.r0-r9" or policy.get("schema_version") != "1.0.0":
        raise PREPolicyError("PRE policy identity or schema version is not recognized")
    return policy


class NonceStore:
    """SQLite-backed single-writer nonce registry.

    This is suitable for deterministic tests and a single persistent service
    instance. Multi-worker production must replace it with a shared transactional
    store (for example PostgreSQL or Redis with atomic SET NX semantics).
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS consumed_approval_nonces (
                    nonce TEXT PRIMARY KEY,
                    scope_id TEXT NOT NULL,
                    approval_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    receipt_digest TEXT NOT NULL,
                    consumed_at TEXT NOT NULL
                )"""
            )
            # Upgrade the initial v1.0 table without discarding any existing
            # nonce records. Old rows remain non-replayable because the empty
            # request/digest values can never match a fresh signed receipt.
            columns = {row[1] for row in db.execute("PRAGMA table_info(consumed_approval_nonces)")}
            if "request_id" not in columns:
                db.execute("ALTER TABLE consumed_approval_nonces ADD COLUMN request_id TEXT NOT NULL DEFAULT ''")
            if "receipt_digest" not in columns:
                db.execute("ALTER TABLE consumed_approval_nonces ADD COLUMN receipt_digest TEXT NOT NULL DEFAULT ''")

    def consume_many(
        self, scope_id: str, request_id: str,
        approvals: list[dict[str, Any]], now: str,
    ) -> None:
        nonces = [item["nonce"] for item in approvals]
        if len(nonces) != len(set(nonces)):
            raise PREPolicyError("Approval nonce is duplicated inside this transition request")
        try:
            with sqlite3.connect(self.path, timeout=10, isolation_level="IMMEDIATE") as db:
                for item in approvals:
                    receipt_digest = digest_json(item)
                    existing = db.execute(
                        "SELECT scope_id, approval_id, request_id, receipt_digest "
                        "FROM consumed_approval_nonces WHERE nonce = ?",
                        (item["nonce"],),
                    ).fetchone()
                    expected = (scope_id, item["approval_id"], request_id, receipt_digest)
                    if existing is not None:
                        if tuple(existing) == expected:
                            # Exact same signed receipt replayed for the same
                            # logical request: safe retry, do not consume twice.
                            continue
                        raise PREPolicyError(
                            "Approval nonce replay detected across a different request or receipt"
                        )
                    db.execute(
                        "INSERT INTO consumed_approval_nonces"
                        "(nonce, scope_id, approval_id, request_id, receipt_digest, consumed_at) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            item["nonce"], scope_id, item["approval_id"],
                            request_id, receipt_digest, now,
                        ),
                    )
        except sqlite3.IntegrityError:
            raise PREPolicyError("Approval nonce replay detected; refusing transition") from None


def _verify_evidence(
    evidence: list[dict[str, Any]], required_types: list[str],
    request: dict[str, Any], policy: dict[str, Any],
    *, evidence_secret: str | None, now: datetime,
) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    denials: list[str] = []
    rules = policy["evidence"]
    attestation = rules.get("attestation", {})
    by_type: dict[str, list[dict[str, Any]]] = {}
    for item in evidence:
        if not isinstance(item, dict):
            denials.append("EVIDENCE_ENTRY_MALFORMED")
            continue
        kind = item.get("evidence_type")
        if not isinstance(kind, str) or not kind:
            denials.append("EVIDENCE_TYPE_MISSING")
            continue
        by_type.setdefault(kind, []).append(item)

    for kind in required_types:
        candidates = by_type.get(kind, [])
        if not candidates:
            blockers.append(f"MISSING_EVIDENCE:{kind}")
            continue
        accepted = False
        for item in candidates:
            if item.get("state") not in rules["accepted_states"]:
                continue
            if item.get("freshness") not in rules["accepted_freshness"]:
                continue
            if item.get("verified") is not True:
                denials.append(f"EVIDENCE_NOT_VERIFIED:{kind}")
                continue
            locator = item.get("source_locator")
            if rules.get("require_https_source_locator") and (
                not isinstance(locator, str) or not locator.startswith("https://")
            ):
                denials.append(f"INVALID_SOURCE_LOCATOR:{kind}")
                continue
            digest = item.get("sha256", "")
            if not isinstance(digest, str) or not re.fullmatch(rules["sha256_pattern"], digest):
                denials.append(f"INVALID_EVIDENCE_DIGEST:{kind}")
                continue
            verifier = item.get("verified_by")
            if rules.get("require_independent_verifier") and (
                not isinstance(verifier, str) or not verifier or
                verifier == request.get("requested_by_actor_id")
            ):
                denials.append(f"NON_INDEPENDENT_VERIFIER:{kind}")
                continue
            verifier_role = item.get("verifier_role")
            if verifier_role not in attestation.get("allowed_verifier_roles", []):
                denials.append(f"UNTRUSTED_VERIFIER_ROLE:{kind}")
                continue
            if item.get("project_id") != request.get("project_id") or item.get("scope_id") != request.get("scope_id"):
                denials.append(f"EVIDENCE_SCOPE_MISMATCH:{kind}")
                continue
            issuer = item.get("issuer")
            if issuer not in attestation.get("allowed_issuers", []):
                denials.append(f"UNTRUSTED_EVIDENCE_ISSUER:{kind}")
                continue
            if attestation.get("require_identity_verified") and item.get("identity_verified") is not True:
                denials.append(f"EVIDENCE_VERIFIER_IDENTITY_UNVERIFIED:{kind}")
                continue
            try:
                verified_at = parse_time(item.get("verified_at"))
            except (TypeError, ValueError):
                denials.append(f"EVIDENCE_VERIFICATION_TIME_INVALID:{kind}")
                continue
            if verified_at > now:
                denials.append(f"EVIDENCE_VERIFICATION_TIME_IN_FUTURE:{kind}")
                continue
            age_seconds = (now - verified_at).total_seconds()
            if age_seconds > int(attestation.get("max_age_seconds", 7776000)):
                blockers.append(f"EVIDENCE_ATTESTATION_EXPIRED:{kind}")
                continue
            if not evidence_secret:
                blockers.append(f"EVIDENCE_SIGNING_KEY_NOT_CONFIGURED:{kind}")
                continue
            signature = item.get("signature")
            expected_signature = sign_evidence_envelope(item, evidence_secret)
            if not isinstance(signature, str) or not hmac.compare_digest(signature, expected_signature):
                denials.append(f"EVIDENCE_SIGNATURE_INVALID:{kind}")
                continue
            accepted = True
            break
        if not accepted and not any(x.endswith(f":{kind}") for x in denials):
            blockers.append(f"NO_FRESH_VERIFIED_PASS_EVIDENCE:{kind}")
    return blockers, denials


def _verify_approval(
    receipt: dict[str, Any], request: dict[str, Any], required_role: str,
    policy: dict[str, Any], secret: str, now: datetime,
) -> tuple[bool, str]:
    required = {
        "approval_id", "decision", "scope_id", "from_stage", "to_stage",
        "approver_subject", "approver_role", "identity_issuer",
        "identity_verified", "independent", "issued_at", "expires_at",
        "nonce", "signature",
    }
    if not isinstance(receipt, dict) or not required.issubset(receipt):
        return False, "APPROVAL_RECEIPT_INCOMPLETE"
    if receipt["decision"] != "APPROVED":
        return False, "APPROVAL_NOT_GRANTED"
    if receipt["scope_id"] != request["scope_id"]:
        return False, "APPROVAL_SCOPE_MISMATCH"
    if receipt["from_stage"] != request["from_stage"] or receipt["to_stage"] != request["to_stage"]:
        return False, "APPROVAL_TRANSITION_MISMATCH"
    if receipt["approver_role"] != required_role:
        return False, "APPROVER_ROLE_INSUFFICIENT"
    if policy["approval"]["require_identity_verified"] and receipt["identity_verified"] is not True:
        return False, "APPROVER_IDENTITY_NOT_VERIFIED"
    if policy["approval"]["require_independent"] and receipt["independent"] is not True:
        return False, "APPROVER_NOT_INDEPENDENT"
    if receipt["approver_subject"] == request["requested_by_actor_id"]:
        return False, "SELF_APPROVAL_PROHIBITED"
    if receipt["identity_issuer"] not in policy["approval"]["allowed_issuers"]:
        return False, "UNTRUSTED_APPROVAL_ISSUER"
    try:
        issued = parse_time(receipt["issued_at"])
        expires = parse_time(receipt["expires_at"])
    except (TypeError, ValueError):
        return False, "APPROVAL_TIMESTAMP_INVALID"
    if expires <= now or issued > now:
        return False, "APPROVAL_EXPIRED_OR_FROM_FUTURE"
    validity = (expires - issued).total_seconds()
    if validity <= 0 or validity > int(policy["approval"]["max_validity_seconds"]):
        return False, "APPROVAL_VALIDITY_WINDOW_INVALID"
    unsigned = {key: value for key, value in receipt.items() if key != "signature"}
    expected = hmac.new(secret.encode("utf-8"), canonical_json(unsigned).encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(receipt["signature"]), expected):
        return False, "APPROVAL_SIGNATURE_INVALID"
    if not receipt["nonce"]:
        return False, "APPROVAL_NONCE_MISSING"
    return True, "APPROVAL_VERIFIED"


def evaluate_transition(
    request: dict[str, Any],
    policy: dict[str, Any],
    *,
    approval_secret: str | None = None,
    nonce_store: NonceStore | None = None,
    evidence_secret: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return ALLOW, HOLD, or DENY for one adjacent PRE stage transition."""
    evaluated_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    reasons: list[str] = []
    denials: list[str] = []

    required_fields = {
        "request_id", "project_id", "scope_id", "from_stage", "to_stage",
        "requested_by_actor_id", "evidence",
    }
    missing = sorted(required_fields - set(request))
    if missing:
        denials.append("REQUEST_FIELDS_MISSING:" + ",".join(missing))
    empty_fields = sorted(
        key for key in required_fields - {"evidence"}
        if key in request and (not isinstance(request[key], str) or not request[key].strip())
    )
    if empty_fields:
        denials.append("REQUEST_FIELDS_EMPTY:" + ",".join(empty_fields))
    if "evidence" in request and not isinstance(request["evidence"], list):
        denials.append("EVIDENCE_FIELD_MALFORMED")
    stage_ids = [item["id"] for item in policy["lifecycle"]]
    source = request.get("from_stage")
    target = request.get("to_stage")
    if source not in stage_ids or target not in stage_ids:
        denials.append("UNKNOWN_STAGE")
    elif source == policy["enforcement"]["terminal_stage"]:
        denials.append("TERMINAL_STAGE_CANNOT_ADVANCE")
    elif stage_ids.index(target) != stage_ids.index(source) + 1:
        denials.append("NON_ADJACENT_STAGE_TRANSITION")

    if denials:
        result = {
            "decision": "DENY", "gate_state": "FAIL",
            "request_id": request.get("request_id", "UNKNOWN"),
            "policy_id": policy["policy_id"], "policy_version": policy["version"],
            "input_digest": digest_json(request),
            "reasons": sorted(set(denials)), "blockers": [],
            "evaluated_at": evaluated_at.isoformat().replace("+00:00", "Z"),
            "stage_mutation_performed": False,
        }
        result["evaluation_digest"] = digest_json(result)
        return result

    edge = f"{source}->{target}"
    rule = policy["transitions"].get(edge)
    if not rule:
        denials.append("TRANSITION_NOT_REGISTERED")
        rule = {"required_evidence_types": [], "required_approval_roles": []}

    blockers, evidence_denials = _verify_evidence(
        request.get("evidence", []), rule["required_evidence_types"], request, policy,
        evidence_secret=evidence_secret, now=evaluated_at,
    )
    reasons.extend(blockers)
    denials.extend(evidence_denials)

    required_roles = rule["required_approval_roles"]
    valid_approvals: list[dict[str, Any]] = []
    supplied = request.get("approvals", [])
    if not isinstance(supplied, list):
        denials.append("APPROVALS_FIELD_MALFORMED")
        supplied = []
    for role in required_roles:
        matched = False
        if not approval_secret:
            reasons.append("APPROVAL_SIGNING_KEY_NOT_CONFIGURED")
        else:
            for receipt in supplied:
                ok, reason = _verify_approval(
                    receipt, request, role, policy, approval_secret,
                    evaluated_at,
                )
                if ok:
                    valid_approvals.append(receipt)
                    matched = True
                    break
                if reason not in {"APPROVAL_RECEIPT_INCOMPLETE", "APPROVAL_NOT_GRANTED"}:
                    denials.append(reason)
        if not matched and not any(item in denials for item in {
            "APPROVAL_SIGNATURE_INVALID", "SELF_APPROVAL_PROHIBITED",
            "APPROVAL_SCOPE_MISMATCH", "APPROVAL_TRANSITION_MISMATCH",
            "APPROVER_ROLE_INSUFFICIENT", "APPROVER_IDENTITY_NOT_VERIFIED",
            "APPROVER_NOT_INDEPENDENT", "UNTRUSTED_APPROVAL_ISSUER",
            "APPROVAL_EXPIRED_OR_FROM_FUTURE", "APPROVAL_VALIDITY_WINDOW_INVALID",
        }):
            reasons.append(f"MISSING_APPROVAL:{role}")

    if required_roles and valid_approvals and not denials:
        if nonce_store is None:
            reasons.append("APPROVAL_NONCE_STORE_NOT_CONFIGURED")
        else:
            try:
                nonce_store.consume_many(request["scope_id"], request["request_id"], valid_approvals, utc_now())
            except PREPolicyError as exc:
                denials.append(str(exc))

    decision = "DENY" if denials else ("HOLD" if reasons else "ALLOW")
    gate_state = "FAIL" if denials else ("HOLD" if reasons else "PASS")
    result = {
        "decision": decision,
        "gate_state": gate_state,
        "request_id": request["request_id"],
        "project_id": request["project_id"],
        "scope_id": request["scope_id"],
        "from_stage": source,
        "to_stage": target,
        "policy_id": policy["policy_id"],
        "policy_version": policy["version"],
        "input_digest": digest_json(request),
        "required_evidence_types": rule["required_evidence_types"],
        "required_approval_roles": required_roles,
        "verified_approval_ids": [item["approval_id"] for item in valid_approvals],
        "blockers": sorted(set(reasons)),
        "reasons": sorted(set(denials)),
        "evaluated_at": evaluated_at.isoformat().replace("+00:00", "Z"),
        "stage_mutation_performed": False,
        "next_action": (
            "HOST_MAY_APPLY_WITH_COMPARE_AND_SWAP" if decision == "ALLOW"
            else "REPAIR_EVIDENCE_OR_AUTHORITY" if decision == "HOLD"
            else "REJECT_REQUEST_AND_OPEN_ASSURANCE_REVIEW"
        ),
    }
    result["evaluation_digest"] = digest_json(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate HSO PRE R0-R9 stage transitions")
    sub = parser.add_subparsers(dest="command", required=True)
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--request-file", type=Path, required=True)
    evaluate.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    evaluate.add_argument("--nonce-store", type=Path)
    evaluate.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        request = json.loads(args.request_file.read_text(encoding="utf-8"))
        policy = load_policy(args.policy)
        secret = os.environ.get(policy["approval"]["key_environment_variable"])
        evidence_secret = os.environ.get(policy["evidence"]["attestation"]["key_environment_variable"])
        nonce_store = NonceStore(args.nonce_store) if args.nonce_store else None
        result = evaluate_transition(
            request, policy, approval_secret=secret,
            evidence_secret=evidence_secret, nonce_store=nonce_store,
        )
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0 if result["decision"] in {"ALLOW", "HOLD"} else 2
    except (OSError, json.JSONDecodeError, PREPolicyError, KeyError) as exc:
        print(f"PRE_POLICY_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
