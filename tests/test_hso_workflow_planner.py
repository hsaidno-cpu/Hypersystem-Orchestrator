"""Tests for the deterministic, plan-only HSO workflow planner."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

from tools.plan_hso_workflow import PlanError, build_plan, main, topological_order

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts" / "hso-workflow-plan.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "hso-workflow-plan.example.json"


def test_catalog():
    return {
        "plugins": [
            {"plugin_key": "skill-analyzer", "source_state": "integrated_submodule"},
            {"plugin_key": "asfree-canonical", "source_state": "integrated_submodule"},
            {"plugin_key": "anatomi-prompt-v3-octa-prompt", "source_state": "integrated_submodule"},
            {"plugin_key": "workflow-systems-orchestrator", "source_state": "pending_repository"},
            {"plugin_key": "skill-developer-orchestrator", "source_state": "integrated_submodule"},
            {"plugin_key": "evaluator-team", "source_state": "pending_repository"},
            {"plugin_key": "asfree-legacy", "source_state": "canonical_redirect"},
        ]
    }


def package(package_id="WP-01", *, owner="skill-analyzer", depends_on=None, **overrides):
    value = {
        "package_id": package_id,
        "primary_owner": owner,
        "supporting_specialists": [],
        "depends_on": [] if depends_on is None else depends_on,
        "capability_status": "READY",
        "capability_evidence": "connector/tool readiness inspected for this test",
        "write_scope": "READ_ONLY",
        "requires_approval": False,
        "approval_status": "NOT_REQUIRED",
        "approval_reference": None,
        "expected_output": "analysis dossier",
        "acceptance_criteria": ["all material claims have provenance"],
    }
    value.update(overrides)
    return value


def plan(*packages, authority="S2", dispatch=False):
    return {
        "schema_version": "1.0.0",
        "case_id": "TEST-CASE-001",
        "intent": "Validate the declared plan-only work graph",
        "action_authority": authority,
        "dispatch_requested": dispatch,
        "work_packages": list(packages),
    }


class HsoWorkflowPlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)
        cls.catalog = test_catalog()

    def test_example_matches_input_schema(self):
        payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(list(self.validator.iter_errors(payload)), [])

    def test_schema_rejects_unregistered_top_level_field(self):
        payload = plan(package())
        payload["force_dispatch"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_schema_rejects_duplicate_dependency_entry(self):
        payload = plan(package("WP-02", depends_on=["WP-01", "WP-01"]))
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_stable_topological_order_respects_dependencies(self):
        packages = {
            "WP-03": package("WP-03", depends_on=["WP-01"]),
            "WP-02": package("WP-02"),
            "WP-01": package("WP-01"),
        }
        self.assertEqual(topological_order(packages), ["WP-02", "WP-01", "WP-03"])

    def test_unknown_plan_field_is_rejected_by_planner(self):
        payload = plan(package())
        payload["unexpected"] = "no silent extension"
        with self.assertRaisesRegex(PlanError, "Unknown plan field"):
            build_plan(payload, self.catalog)

    def test_unknown_package_field_is_rejected_by_planner(self):
        payload = package(unreviewed_override=True)
        with self.assertRaisesRegex(PlanError, "Unknown field"):
            build_plan(plan(payload), self.catalog)

    def test_approval_reference_must_be_string_or_null(self):
        payload = package(
            write_scope="CHILD_REPOSITORY_CHANGE",
            requires_approval=True,
            approval_status="APPROVED",
            approval_reference={"fake": "object"},
        )
        with self.assertRaisesRegex(PlanError, "approval_reference must be a string or null"):
            build_plan(plan(payload, authority="S3"), self.catalog)

    def test_unknown_primary_owner_is_rejected(self):
        with self.assertRaisesRegex(PlanError, "not in the plugin catalog"):
            build_plan(plan(package(owner="unknown-plugin")), self.catalog)

    def test_legacy_redirect_cannot_be_primary_owner(self):
        with self.assertRaisesRegex(PlanError, "legacy redirect"):
            build_plan(plan(package(owner="asfree-legacy")), self.catalog)

    def test_legacy_redirect_cannot_be_supporting_specialist(self):
        with self.assertRaisesRegex(PlanError, "legacy redirect"):
            build_plan(plan(package(supporting_specialists=["asfree-legacy"])), self.catalog)

    def test_primary_owner_cannot_also_be_supporting_specialist(self):
        with self.assertRaisesRegex(PlanError, "cannot also be"):
            build_plan(plan(package(supporting_specialists=["skill-analyzer"])), self.catalog)

    def test_unknown_dependency_is_rejected(self):
        with self.assertRaisesRegex(PlanError, "unknown dependency"):
            build_plan(plan(package("WP-02", depends_on=["WP-MISSING"])), self.catalog)

    def test_dependency_cycle_is_rejected(self):
        payload = plan(
            package("WP-01", depends_on=["WP-02"]),
            package("WP-02", owner="asfree-canonical", depends_on=["WP-01"]),
        )
        with self.assertRaisesRegex(PlanError, "Dependency cycle"):
            build_plan(payload, self.catalog)

    def test_duplicate_package_id_is_rejected(self):
        with self.assertRaisesRegex(PlanError, "Duplicate package_id"):
            build_plan(
                plan(package("WP-01"), package("WP-01", owner="asfree-canonical")),
                self.catalog,
            )

    def test_ready_capability_requires_evidence(self):
        with self.assertRaisesRegex(PlanError, "capability_evidence"):
            build_plan(plan(package(capability_evidence=None)), self.catalog)

    def test_not_checked_capability_is_blocked(self):
        result = build_plan(
            plan(package(capability_status="NOT_CHECKED", capability_evidence=None)),
            self.catalog,
        )
        self.assertEqual(result["work_packages"][0]["readiness"], "BLOCKED")
        self.assertIn("CAPABILITY_NOT_CHECKED", result["work_packages"][0]["blockers"])
        self.assertEqual(result["disposition"], "PLAN_VALIDATED_WITH_BLOCKERS")

    def test_insufficient_action_authority_blocks_branch_write(self):
        result = build_plan(
            plan(package(write_scope="PARENT_REPOSITORY_BRANCH_WRITE"), authority="S2"),
            self.catalog,
        )
        self.assertIn("ACTION_AUTHORITY_INSUFFICIENT", result["work_packages"][0]["blockers"])

    def test_child_repository_change_requires_explicit_approval(self):
        payload = package(
            write_scope="CHILD_REPOSITORY_CHANGE",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
        )
        with self.assertRaisesRegex(PlanError, "must require explicit approval"):
            build_plan(plan(payload, authority="S3"), self.catalog)

    def test_pending_approval_blocks_even_with_sufficient_authority(self):
        payload = package(
            write_scope="CHILD_REPOSITORY_CHANGE",
            requires_approval=True,
            approval_status="PENDING",
        )
        result = build_plan(plan(payload, authority="S3"), self.catalog)
        self.assertIn("APPROVAL_PENDING", result["work_packages"][0]["blockers"])

    def test_approval_does_not_compensate_for_insufficient_authority(self):
        payload = package(
            write_scope="PRODUCTION_RELEASE",
            requires_approval=True,
            approval_status="APPROVED",
            approval_reference="DECISION-123",
        )
        result = build_plan(plan(payload, authority="S4"), self.catalog)
        self.assertIn("ACTION_AUTHORITY_INSUFFICIENT", result["work_packages"][0]["blockers"])

    def test_blocker_propagates_to_dependent_package(self):
        result = build_plan(
            plan(
                package("WP-01", capability_status="NOT_CHECKED", capability_evidence=None),
                package("WP-02", owner="asfree-canonical", depends_on=["WP-01"]),
            ),
            self.catalog,
        )
        by_id = {item["package_id"]: item for item in result["work_packages"]}
        self.assertEqual(by_id["WP-02"]["readiness"], "BLOCKED")
        self.assertTrue(
            any(reason.startswith("DEPENDENCY_BLOCKED") for reason in by_id["WP-02"]["blockers"])
        )

    def test_dispatch_request_is_blocked_without_dispatch_attempt(self):
        result = build_plan(plan(package(), dispatch=True), self.catalog)
        self.assertEqual(result["disposition"], "BLOCKED_DISPATCH_UNAVAILABLE")
        self.assertEqual(result["dispatch_status"], "NOT_AVAILABLE")
        self.assertIn(
            "RUNTIME_DISPATCH_NOT_DEPLOYED",
            [item["reason"] for item in result["blocked_reasons"]],
        )

    def test_output_must_not_overwrite_input(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "plan.json"
            path.write_text(json.dumps(plan(package())), encoding="utf-8")
            exit_code = main([str(path), "--output", str(path)])
            self.assertEqual(exit_code, 2)

    def test_plan_result_labels_primary_owner_source_state(self):
        result = build_plan(plan(package()), self.catalog)
        self.assertEqual(
            result["work_packages"][0]["primary_owner_source_state"],
            "integrated_submodule",
        )
        self.assertEqual(result["mode"], "PLAN_ONLY")


if __name__ == "__main__":
    unittest.main()
