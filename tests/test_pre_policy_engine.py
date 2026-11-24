import hashlib
import hmac
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tools.pre_policy_engine import (
    NonceStore, evaluate_transition, load_policy, canonical_json, sign_evidence_envelope,
)

POLICY = load_policy()
NOW = datetime(2026, 11, 24, 3, 0, tzinfo=timezone.utc)
SECRET = "test-pre-approval-key-32-bytes-minimum"


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
    item["signature"] = sign_evidence_envelope(item, SECRET)
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


def signed_approval(req, role="HUMAN_DECISION_OWNER", *, evidence_secret=SECRET, now=NOW, subject="user:reviewer-1"):
    issued = now - timedelta(seconds=10)
    unsigned = {
        "approval_id": "APR-001-" + role,
        "decision": "APPROVED",
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
    unsigned["signature"] = hmac.new(
        SECRET.encode(), canonical_json(unsigned).encode(), hashlib.sha256
    ).hexdigest()
    return unsigned


class PREPolicyEngineTests(unittest.TestCase):
    def test_valid_r0_to_r1_transition_is_allowed(self):
        result = evaluate_transition(request(), POLICY, evidence_secret=SECRET, now=NOW)
        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(result["gate_state"], "PASS")
        self.assertFalse(result["stage_mutation_performed"])
        self.assertEqual(len(result["evaluation_digest"]), 64)

    def test_skipping_a_stage_is_denied(self):
        result = evaluate_transition(request("R0", "R2"), POLICY, now=NOW)
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("NON_ADJACENT_STAGE_TRANSITION", result["reasons"])

    def test_missing_evidence_holds_transition(self):
        req = request(types=[])
        result = evaluate_transition(req, POLICY, evidence_secret=SECRET, now=NOW)
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("MISSING_EVIDENCE:INTAKE_BRIEF", result["blockers"])

    def test_stale_or_unverified_evidence_cannot_pass(self):
        req = request()
        req["evidence"][0]["freshness"] = "STALE"
        result = evaluate_transition(req, POLICY, evidence_secret=SECRET, now=NOW)
        self.assertEqual(result["decision"], "HOLD")

    def test_invalid_evidence_digest_is_denied(self):
        req = request()
        req["evidence"][0]["sha256"] = "not-a-digest"
        result = evaluate_transition(req, POLICY, evidence_secret=SECRET, now=NOW)
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("INVALID_EVIDENCE_DIGEST:INTAKE_BRIEF", result["reasons"])

    def test_same_actor_cannot_be_evidence_verifier(self):
        req = request()
        req["evidence"][0]["verified_by"] = req["requested_by_actor_id"]
        result = evaluate_transition(req, POLICY, evidence_secret=SECRET, now=NOW)
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("NON_INDEPENDENT_VERIFIER:INTAKE_BRIEF", result["reasons"])

    def test_r2_to_r3_requires_signed_independent_human_approval(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        result = evaluate_transition(req, POLICY, approval_secret=SECRET, evidence_secret=SECRET, now=NOW)
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("MISSING_APPROVAL:HUMAN_DECISION_OWNER", result["blockers"])

    def test_self_approval_is_denied(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req, subject=req["requested_by_actor_id"])]
        with tempfile.TemporaryDirectory() as folder:
            result = evaluate_transition(
                req, POLICY, approval_secret=SECRET, evidence_secret=SECRET,
                nonce_store=NonceStore(Path(folder) / "nonces.sqlite"), evidence_secret=SECRET, now=NOW,
            )
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("SELF_APPROVAL_PROHIBITED", result["reasons"])

    def test_approval_signature_scope_and_role_are_verified(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req)]
        req["approvals"][0]["signature"] = "0" * 64
        with tempfile.TemporaryDirectory() as folder:
            result = evaluate_transition(
                req, POLICY, approval_secret=SECRET, evidence_secret=SECRET,
                nonce_store=NonceStore(Path(folder) / "nonces.sqlite"), evidence_secret=SECRET, now=NOW,
            )
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("APPROVAL_SIGNATURE_INVALID", result["reasons"])

    def test_approval_nonce_retry_is_idempotent_for_same_request_but_replay_is_denied(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req)]
        with tempfile.TemporaryDirectory() as folder:
            store = NonceStore(Path(folder) / "nonces.sqlite")
            first = evaluate_transition(
                req, POLICY, approval_secret=SECRET, evidence_secret=SECRET, nonce_store=store, evidence_secret=SECRET, now=NOW,
            )
            retry = evaluate_transition(
                req, POLICY, approval_secret=SECRET, evidence_secret=SECRET, nonce_store=store, evidence_secret=SECRET, now=NOW,
            )
            replay = dict(req)
            replay["request_id"] = "PRE-REQ-DIFFERENT"
            replayed = evaluate_transition(
                replay, POLICY, approval_secret=SECRET, evidence_secret=SECRET, nonce_store=store, evidence_secret=SECRET, now=NOW,
            )
        self.assertEqual(first["decision"], "ALLOW")
        self.assertEqual(retry["decision"], "ALLOW")
        self.assertEqual(retry["evaluation_digest"], first["evaluation_digest"])
        self.assertEqual(replayed["decision"], "DENY")
        self.assertTrue(any("nonce replay" in reason.lower() for reason in replayed["reasons"]))

    def test_approval_receipt_without_signing_key_holds_instead_of_false_denial(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req)]
        result = evaluate_transition(req, POLICY, evidence_secret=SECRET, now=NOW)
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("APPROVAL_SIGNING_KEY_NOT_CONFIGURED", result["blockers"])

    def test_required_approval_without_nonce_store_holds(self):
        req = request("R2", "R3", ["ROADMAP_PLAN", "DEPENDENCY_GRAPH"])
        req["approvals"] = [signed_approval(req)]
        result = evaluate_transition(req, POLICY, approval_secret=SECRET, evidence_secret=SECRET, now=NOW)
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("APPROVAL_NONCE_STORE_NOT_CONFIGURED", result["blockers"])

    def test_terminal_r9_cannot_advance(self):
        result = evaluate_transition(request("R9", "R9"), POLICY, now=NOW)
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("TERMINAL_STAGE_CANNOT_ADVANCE", result["reasons"])


if __name__ == "__main__":
    unittest.main()
