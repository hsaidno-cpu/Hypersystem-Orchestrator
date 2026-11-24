import base64
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from tools.pre_policy_engine import (
    NonceStore, approval_binding_digest, canonical_json, evaluate_transition, load_policy,
    evidence_attestation_payload,
)

POLICY = load_policy()
NOW = datetime(2026, 11, 24, 3, 0, tzinfo=timezone.utc)
EVIDENCE_PRIVATE = Ed25519PrivateKey.from_private_bytes(bytes.fromhex("11" * 32))
APPROVAL_PRIVATE = Ed25519PrivateKey.from_private_bytes(bytes.fromhex("22" * 32))


def public_key_b64(private_key):
    raw = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(raw).decode("ascii")


EVIDENCE_PUBLIC = public_key_b64(EVIDENCE_PRIVATE)
APPROVAL_PUBLIC = public_key_b64(APPROVAL_PRIVATE)


def sign(private_key, payload):
    signature = private_key.sign(canonical_json(payload).encode("utf-8"))
    return base64.b64encode(signature).decode("ascii")


def evidence(
    kind, verified_by="evaluator:independent",
    project_id="HSO", scope_id="HSO:WI-001:baseline-v1",
):
    item = {
        "schema_version": "1.0.0",
        "evidence_id": "EV-" + kind,
        "evidence_type": kind,
        "project_id": project_id,
        "scope_id": scope_id,
        "state": "PASS",
        "freshness": "FRESH",
        "verified": True,
        "identity_verified": True,
        "verified_by": verified_by,
        "verifier_role": "Evaluator Team",
        "verified_at": NOW.isoformat().replace("+00:00", "Z"),
        "issuer": "hso-evidence-issuer",
        "source_locator": "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/commit/" + "a" * 40,
        "sha256": "a" * 64,
    }
    item["signature"] = sign(EVIDENCE_PRIVATE, evidence_attestation_payload(item))
    return item


def request(from_stage="R0", to_stage="R1", types=None):
    result = {
        "request_id": "PRE-REQ-001",
        "project_id": "HSO",
        "scope_id": "HSO:WI-001:baseline-v1",
        "from_stage": from_stage,
        "to_stage": to_stage,
        "requested_by_actor_id": "agent:hso",
        "evidence": [],
        "approvals": [],
    }
    result["evidence"] = [
        evidence(item, project_id=result["project_id"], scope_id=result["scope_id"])
        for item in (["INTAKE_BRIEF"] if types is None else types)
    ]
    return result


def signed_approval(req, role="HUMAN_DECISION_OWNER", *, now=NOW, subject="user:reviewer-1"):
    issued = now - timedelta(seconds=10)
    unsigned = {
        "approval_id": "APR-001-" + role,
        "decision": "APPROVED",
        "request_digest": approval_binding_digest(req),
        "scope_id": req["scope_id"],
        "from_stage": req["from_stage"],
        "to_stage": req["to_stage"],
        "approver_subject": subject,
        "approver_role": role,
        "identity_issuer": "hso-approval-issuer",
        "identity_verified": True,
        "independent": True,
        "issued_at": issued.isoformat().replace("+00:00", "Z"),
        "expires_at": (issued + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        "nonce": "nonce-" + role,
    }
    unsigned["signature"] = sign(APPROVAL_PRIVATE, {k: v for k, v in unsigned.items() if k != "signature"})
    return unsigned


class PREPolicyEngineTests(unittest.TestCase):
    def test_valid_r0_to_r1_transition_is_allowed_only_with_signed_scoped_evidence(self):
        result = evaluate_transition(
            request(), POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW
        )
        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(result["gate_state"], "PASS")
        self.assertFalse(result["stage_mutation_performed"])
        self.assertEqual(len(result["evaluation_digest"]), 64)
        self.assertEqual(len(result["input_digest"]), 64)

    def test_skipping_a_stage_is_denied(self):
        result = evaluate_transition(
            request("R0", "R2"), POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW
        )
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("NON_ADJACENT_STAGE_TRANSITION", result["reasons"])

    def test_missing_evidence_holds_transition(self):
        result = evaluate_transition(
            request(types=[]), POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW
        )
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("MISSING_EVIDENCE:INTAKE_BRIEF", result["blockers"])

    def test_stale_evidence_cannot_pass(self):
        req = request()
        req["evidence"][0]["freshness"] = "STALE"
        result = evaluate_transition(req, POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW)
        self.assertEqual(result["decision"], "HOLD")

    def test_invalid_content_digest_is_denied(self):
        req = request()
        req["evidence"][0]["sha256"] = "not-a-digest"
        result = evaluate_transition(req, POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW)
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("INVALID_EVIDENCE_DIGEST:INTAKE_BRIEF", result["reasons"])

    def test_same_actor_cannot_verify_own_evidence(self):
        req = request()
        req["evidence"][0]["verified_by"] = req["requested_by_actor_id"]
        result = evaluate_transition(req, POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW)
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("NON_INDEPENDENT_VERIFIER:INTAKE_BRIEF", result["reasons"])

    def test_invalid_evidence_signature_is_denied(self):
        req = request()
        req["evidence"][0]["signature"] = base64.b64encode(b"x" * 64).decode("ascii")
        result = evaluate_transition(req, POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW)
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("EVIDENCE_SIGNATURE_INVALID:INTAKE_BRIEF", result["reasons"])

    def test_evidence_cannot_be_replayed_across_project_or_scope(self):
        req = request()
        req["scope_id"] = "HSO:WI-OTHER:baseline-v1"
        result = evaluate_transition(req, POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW)
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("EVIDENCE_SCOPE_MISMATCH:INTAKE_BRIEF", result["reasons"])

    def test_missing_evidence_public_key_holds(self):
        result = evaluate_transition(request(), POLICY, now=NOW)
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("EVIDENCE_VERIFYING_KEY_NOT_CONFIGURED:INTAKE_BRIEF", result["blockers"])

    def test_expired_evidence_attestation_holds(self):
        req = request()
        req["evidence"][0]["verified_at"] = (
            NOW - timedelta(days=100)
        ).isoformat().replace("+00:00", "Z")
        req["evidence"][0]["signature"] = sign(
            EVIDENCE_PRIVATE,
            evidence_attestation_payload(req["evidence"][0]),
        )
        result = evaluate_transition(req, POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW)
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("EVIDENCE_ATTESTATION_EXPIRED:INTAKE_BRIEF", result["blockers"])

    def test_r2_to_r3_requires_signed_independent_human_approval(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        result = evaluate_transition(
            req, POLICY, approval_public_key=APPROVAL_PUBLIC,
            evidence_public_key=EVIDENCE_PUBLIC, now=NOW,
        )
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("MISSING_APPROVAL:HUMAN_DECISION_OWNER", result["blockers"])

    def test_self_approval_is_denied(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req, subject=req["requested_by_actor_id"])]
        with tempfile.TemporaryDirectory() as folder:
            result = evaluate_transition(
                req, POLICY, approval_public_key=APPROVAL_PUBLIC,
                evidence_public_key=EVIDENCE_PUBLIC,
                nonce_store=NonceStore(Path(folder) / "nonces.sqlite"), now=NOW,
            )
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("SELF_APPROVAL_PROHIBITED", result["reasons"])

    def test_approval_is_bound_to_exact_evidence_set(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req)]
        # Replace an evidence object after approval issuance. The signature on
        # the approval remains cryptographically valid, but its request binding
        # must no longer match the evidence set.
        req["evidence"][0]["sha256"] = "b" * 64
        with tempfile.TemporaryDirectory() as folder:
            result = evaluate_transition(
                req, POLICY, approval_public_key=APPROVAL_PUBLIC,
                evidence_public_key=EVIDENCE_PUBLIC,
                nonce_store=NonceStore(Path(folder) / "nonces.sqlite"), now=NOW,
            )
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("APPROVAL_REQUEST_DIGEST_MISMATCH", result["reasons"])

    def test_approval_signature_is_verified(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req)]
        req["approvals"][0]["signature"] = base64.b64encode(b"x" * 64).decode("ascii")
        with tempfile.TemporaryDirectory() as folder:
            result = evaluate_transition(
                req, POLICY, approval_public_key=APPROVAL_PUBLIC,
                evidence_public_key=EVIDENCE_PUBLIC,
                nonce_store=NonceStore(Path(folder) / "nonces.sqlite"), now=NOW,
            )
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("APPROVAL_SIGNATURE_INVALID", result["reasons"])

    def test_approval_nonce_retry_is_idempotent_but_cross_request_replay_is_denied(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req)]
        with tempfile.TemporaryDirectory() as folder:
            store = NonceStore(Path(folder) / "nonces.sqlite")
            first = evaluate_transition(
                req, POLICY, approval_public_key=APPROVAL_PUBLIC,
                evidence_public_key=EVIDENCE_PUBLIC, nonce_store=store, now=NOW,
            )
            retry = evaluate_transition(
                req, POLICY, approval_public_key=APPROVAL_PUBLIC,
                evidence_public_key=EVIDENCE_PUBLIC, nonce_store=store, now=NOW,
            )
            replay = dict(req)
            replay["request_id"] = "PRE-REQ-DIFFERENT"
            replayed = evaluate_transition(
                replay, POLICY, approval_public_key=APPROVAL_PUBLIC,
                evidence_public_key=EVIDENCE_PUBLIC, nonce_store=store, now=NOW,
            )
        self.assertEqual(first["decision"], "ALLOW")
        self.assertEqual(retry["decision"], "ALLOW")
        self.assertEqual(retry["evaluation_digest"], first["evaluation_digest"])
        self.assertEqual(replayed["decision"], "DENY")
        self.assertTrue(any("nonce replay" in reason.lower() for reason in replayed["reasons"]))

    def test_missing_approval_public_key_holds(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req)]
        result = evaluate_transition(
            req, POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW
        )
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("APPROVAL_VERIFYING_KEY_NOT_CONFIGURED", result["blockers"])

    def test_required_approval_without_nonce_store_holds(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req)]
        result = evaluate_transition(
            req, POLICY, approval_public_key=APPROVAL_PUBLIC,
            evidence_public_key=EVIDENCE_PUBLIC, now=NOW,
        )
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("APPROVAL_NONCE_STORE_NOT_CONFIGURED", result["blockers"])

    def test_empty_actor_identity_is_denied(self):
        req = request()
        req["requested_by_actor_id"] = ""
        result = evaluate_transition(req, POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW)
        self.assertEqual(result["decision"], "DENY")
        self.assertTrue(any(reason.startswith("REQUEST_FIELDS_EMPTY") for reason in result["reasons"]))

    def test_terminal_r9_cannot_advance(self):
        result = evaluate_transition(
            request("R9", "R9"), POLICY, evidence_public_key=EVIDENCE_PUBLIC, now=NOW
        )
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("TERMINAL_STAGE_CANNOT_ADVANCE", result["reasons"])


if __name__ == "__main__":
    unittest.main()
