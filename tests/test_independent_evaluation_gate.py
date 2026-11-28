"""Tests for the read-only independent evaluation runtime and its evidence receipt."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools import independent_evaluation_gate as gate

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "sdo-independent-evaluation.input.json"


def complete_document():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for check in doc["checks"]:
        check["status"] = "PASS"
        check["evidence_refs"] = check["evidence_refs"] or [f"test://{check['domain']}/report"]
        check["evidence_digests"] = check.get("evidence_digests") or ["a" * 64]
    return doc


class IndependentEvaluationGateTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def evaluate(self, doc=None, trusted=False):
        context = {"workflow": "test"}
        if trusted:
            context.update({
                "GITHUB_EVENT_NAME": "workflow_dispatch",
                "GITHUB_REF": "refs/heads/main",
                "GITHUB_REF_PROTECTED": "true",
                "GITHUB_WORKFLOW_REF": "hsaidno-cpu/Hypersystem-Orchestrator/.github/workflows/catalog-validation.yml@refs/heads/main",
            })
        return gate.evaluate_document(
            doc or self.doc,
            input_sha256="1" * 64,
            evaluator_engine_sha256="2" * 64,
            execution_context=context,
            evaluated_at="2026-11-26T00:00:00Z",
        )

    def test_current_sdo_evidence_is_held_not_misreported_as_pass(self):
        report = self.evaluate()
        self.assertEqual(report["disposition"], "HOLD")
        self.assertEqual(report["score"]["percent"], 15.0)
        statuses = {x["domain"]: x["status"] for x in report["criteria_results"]}
        self.assertEqual(statuses["source_parity"], "FAIL")
        self.assertEqual(statuses["behavior"], "NOT_RUN")
        self.assertEqual(statuses["runtime"], "BLOCKED")
        self.assertEqual(statuses["independence"], "UNVERIFIABLE")
        self.assertTrue(report["evaluator"]["identity_separated"])
        self.assertFalse(report["evaluator"]["trusted_execution_context"])
        self.assertIs(report["integrity"]["candidate_mutated"], False)

    def test_complete_evidence_with_distinct_read_only_evaluator_passes(self):
        report = self.evaluate(complete_document(), trusted=True)
        self.assertEqual(report["disposition"], "PASS")
        self.assertEqual(report["score"]["percent"], 100.0)
        self.assertTrue(report["evaluator"]["identity_separated"])

    def test_security_failure_is_a_hard_fail(self):
        doc = complete_document()
        next(x for x in doc["checks"] if x["domain"] == "security")["status"] = "FAIL"
        report = self.evaluate(doc, trusted=True)
        self.assertEqual(report["disposition"], "FAIL")
        self.assertIn("security", report["decision_reasons"][0].lower())

    def test_missing_required_domain_is_not_silently_passed(self):
        doc = complete_document()
        doc["checks"] = [x for x in doc["checks"] if x["domain"] != "behavior"]
        report = self.evaluate(doc)
        statuses = {x["domain"]: x["status"] for x in report["criteria_results"]}
        self.assertEqual(statuses["behavior"], "NOT_RUN")
        self.assertEqual(report["disposition"], "HOLD")

    def test_passing_claim_without_evidence_is_downgraded(self):
        doc = complete_document()
        check = next(x for x in doc["checks"] if x["domain"] == "behavior")
        check["evidence_refs"] = []
        check["evidence_digests"] = []
        report = self.evaluate(doc)
        statuses = {x["domain"]: x["status"] for x in report["criteria_results"]}
        self.assertEqual(statuses["behavior"], "UNVERIFIABLE")
        self.assertEqual(report["disposition"], "HOLD")

    def test_evaluator_cannot_be_the_builder(self):
        doc = complete_document()
        doc["evaluator"]["identity"] = doc["builder_identity"]
        report = self.evaluate(doc, trusted=True)
        statuses = {x["domain"]: x["status"] for x in report["criteria_results"]}
        self.assertEqual(statuses["independence"], "FAIL")
        self.assertEqual(report["disposition"], "FAIL")

    def test_evaluator_must_be_read_only(self):
        doc = complete_document()
        doc["evaluator"]["read_only"] = False
        report = self.evaluate(doc, trusted=True)
        self.assertEqual(report["disposition"], "FAIL")

    def test_declared_distinct_evaluator_is_not_independent_on_pr_context(self):
        report = self.evaluate(complete_document())
        statuses = {x["domain"]: x["status"] for x in report["criteria_results"]}
        self.assertTrue(report["evaluator"]["identity_separated"])
        self.assertFalse(report["evaluator"]["trusted_execution_context"])
        self.assertEqual(statuses["independence"], "UNVERIFIABLE")
        self.assertEqual(report["disposition"], "HOLD")

    def test_source_commit_must_be_full_immutable_sha(self):
        doc = copy.deepcopy(self.doc)
        doc["candidate"]["source_commit"] = "9d3c4bc"
        with self.assertRaises(gate.EvaluationInputError):
            self.evaluate(doc)

    def test_duplicate_domain_check_is_rejected(self):
        doc = copy.deepcopy(self.doc)
        doc["checks"].append(copy.deepcopy(doc["checks"][0]))
        with self.assertRaises(gate.EvaluationInputError):
            self.evaluate(doc)

    def test_report_sha256_sidecar_detects_tampering(self):
        report = self.evaluate()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evaluation.json"
            digest = gate.write_report(report, path)
            self.assertEqual(gate.verify_report(path)["report_sha256"], digest)
            path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaises(gate.EvaluationReportError):
                gate.verify_report(path)


if __name__ == "__main__":
    unittest.main()
