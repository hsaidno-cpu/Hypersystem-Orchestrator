"""Static EWO routing and action-boundary contract tests.

These tests validate the public contract corpus and HSO registry alignment.
They do NOT invoke an LLM, activate the private plugin, or prove live routing.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "ewo-routing-contracts.json"
CATALOG_PATH = ROOT / "catalog" / "plugins.json"
SNAPSHOT_PATH = ROOT / "catalog" / "instruction-snapshots.json"
DISTRIBUTION_PATH = ROOT / "catalog" / "distribution-registry.json"

EXPECTED_SKILLS = {
    "workday-orchestrator",
    "task-intake-triage",
    "daily-planning",
    "priority-decision-engine",
    "project-portfolio-management",
    "calendar-meeting-operations",
    "email-communication-operations",
    "notes-knowledge-management",
    "focus-adaptive-scheduling",
    "performance-review-learning",
    "prompt-generator",
    "automation-integration-architect",
    "workday-data-governance",
    "approval-risk-gate",
}
KNOWN_EXTERNAL_OWNERS = {
    "workflow-systems-orchestrator",
    "plugin-agent-orchestrator",
    "skill-developer-orchestrator",
    "evaluator-team",
    "anatomi-prompt-v3-octa-prompt",
    "hso",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class EwoRoutingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = load_json(CONTRACT_PATH)
        cls.catalog = load_json(CATALOG_PATH)
        cls.snapshots = load_json(SNAPSHOT_PATH)
        cls.distribution = load_json(DISTRIBUTION_PATH)
        cls.plugin = next(
            item for item in cls.catalog["plugins"]
            if item["plugin_key"] == "executive-workday-orchestrator"
        )
        cls.snapshot = next(
            item for item in cls.snapshots["plugins"]
            if item["plugin_key"] == "executive-workday-orchestrator"
        )
        cls.distribution_item = next(
            item for item in cls.distribution["plugins"]
            if item["plugin_key"] == "executive-workday-orchestrator"
        )

    def test_contract_is_explicitly_static_not_host_verified(self):
        self.assertEqual(self.contract["classification"], "PUBLIC_TEST_METADATA_ONLY")
        self.assertEqual(
            self.contract["execution_status"],
            "STATIC_CONTRACT_CORPUS_NOT_HOST_INVOKED",
        )
        self.assertTrue(self.contract["test_limitations"])
        self.assertTrue(any(
            "not the actual EWO model response" in item
            or "not been executed against a live EWO model/host invocation" in item
            for item in self.contract["test_limitations"]
        ))

    def test_private_plugin_identity_and_release_are_pinned(self):
        self.assertEqual(self.plugin["plugin_creator_id"],
                         "plugins_6b073a60088081918a8958ab761cb505")
        self.assertEqual(self.plugin["platform_package_version"], "0.1.0")
        self.assertEqual(self.plugin["platform_current_release_id"],
                         "pluginrel_6b073a6285d481918d11cdbf1bb7643f")
        self.assertEqual(self.plugin["platform_scope"], "USER")
        self.assertEqual(self.plugin["platform_discoverability"], "PRIVATE")
        self.assertEqual(self.plugin["source_state"], "private_canonical_repository")
        self.assertEqual(self.plugin["source_repository_id"], "executive-workday-orchestrator")
        self.assertEqual(self.plugin["repository_version"], "0.1.0")
        self.assertEqual(self.plugin["version_alignment_state"], "SOURCE_AND_PLATFORM_MATCH")
        self.assertEqual(self.plugin["source_instruction_parity_status"], "MATCH")

    def test_registry_snapshot_contains_exactly_fourteen_unique_skills(self):
        names = {item["skill_name"] for item in self.snapshot["skills"]}
        contract_names = {item["skill_name"]
                          for item in self.contract["skill_contracts"]}
        self.assertEqual(names, EXPECTED_SKILLS)
        self.assertEqual(contract_names, EXPECTED_SKILLS)
        self.assertEqual(len(self.snapshot["skills"]), 14)
        self.assertEqual(self.snapshot["skill_count"], 14)

    def test_each_skill_has_positive_and_negative_routing_cases(self):
        for item in self.contract["skill_contracts"]:
            with self.subTest(skill=item["skill_name"]):
                self.assertTrue(item["positive_cases"])
                self.assertTrue(item["negative_cases"])
                for case in item["positive_cases"]:
                    self.assertTrue(case["case_id"])
                    self.assertEqual(case["expected_primary_route"],
                                     item["skill_name"])
                    self.assertTrue(case["user_intent"].strip())
                for case in item["negative_cases"]:
                    self.assertTrue(case["case_id"])
                    self.assertTrue(case["user_intent"].strip())
                    self.assertNotIn(item["skill_name"],
                                     case.get("expected_route_owner", ""))
                    self.assertIn(item["skill_name"],
                                  case.get("forbidden_skills", []))

    def test_all_expected_route_targets_exist_in_hso_catalog_or_known_external_owners(self):
        catalog_keys = {item["plugin_key"] for item in self.catalog["plugins"]}
        known = catalog_keys | EXPECTED_SKILLS | KNOWN_EXTERNAL_OWNERS
        for item in self.contract["skill_contracts"]:
            for case in item["positive_cases"]:
                self.assertIn(case["expected_primary_route"], known)
                for route in case.get("required_specialists", []):
                    self.assertIn(route, EXPECTED_SKILLS)
            for case in item["negative_cases"]:
                self.assertIn(case["expected_route_owner"], known)

        for case in self.contract["ambiguous_cases"]:
            for route in case["expected_route_sequence"]:
                self.assertIn(route, known)

    def test_positive_and_negative_case_ids_are_unique(self):
        ids = []
        for item in self.contract["skill_contracts"]:
            ids.extend(case["case_id"] for case in item["positive_cases"])
            ids.extend(case["case_id"] for case in item["negative_cases"])
        ids.extend(case["case_id"] for case in self.contract["ambiguous_cases"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_ambiguous_cases_have_explicit_safe_dispositions(self):
        self.assertGreaterEqual(len(self.contract["ambiguous_cases"]), 6)
        allowed = {
            "COMPOSE_SKILL_SEQUENCE",
            "ASK_CLARIFICATION_AND_REQUIRE_APPROVAL",
            "PROMPT_AND_SEPARATE_ACTION_PREFLIGHT",
            "CAPABILITY_PREFLIGHT_AND_AUTOMATION_DESIGN",
            "TRADE_OFF_ANALYSIS_WITH_HUMAN_DECISION",
        }
        for case in self.contract["ambiguous_cases"]:
            with self.subTest(case=case["case_id"]):
                self.assertIn(case["expected_disposition"], allowed)
                self.assertTrue(case["clarification_policy"].strip())
                self.assertFalse(case["external_side_effects_allowed"])
                self.assertTrue(case["assertions"])

    def test_prompt_generator_octaprompt_contract_is_exact_and_non_executing(self):
        prompt = self.contract["prompt_generator_contract"]
        self.assertEqual(
            prompt["modes"],
            ["BUILD", "REFINE", "AUDIT", "COMPARE", "EXPLAIN"],
        )
        self.assertEqual(len(prompt["mandatory_headings"]), 8)
        self.assertTrue(prompt["prompt_only_no_execution"])
        self.assertEqual(
            prompt["mandatory_headings"][0], "ROLE & PERSONA ARCHETYPE"
        )
        self.assertEqual(
            prompt["mandatory_headings"][-1], "OUTPUT SCHEMA & FORMATTING SPEC"
        )

    def test_action_gate_is_payload_specific_and_deny_by_default(self):
        gate = self.contract["action_gate_contract"]
        required = {
            "actor", "operation", "target_system", "target_record", "scope",
            "payload", "relevant_version_or_state", "approval_time", "expiry",
        }
        self.assertEqual(set(gate["approval_binding_fields"]), required)
        self.assertTrue(gate["deny_by_default"])
        self.assertTrue(gate["approval_is_payload_specific"])
        self.assertTrue(gate["read_back_required_for_consequential_write"])
        self.assertEqual(gate["unauthorized_side_effect_target"], 0)
        self.assertEqual(gate["duplicate_logical_side_effect_target"], 0)

    def test_global_invariants_cover_completion_persistence_and_recovery(self):
        rules = {item["id"]: item["rule"]
                 for item in self.contract["global_invariants"]}
        self.assertEqual(len(rules), 10)
        expected_fragments = [
            "PREPARED, not EXECUTED",
            "DONE only after",
            "VERIFIED only after",
            "action-specific approval",
            "Prompt-only requests",
            "configured store",
            "deployed and verified worker",
            "untrusted source data",
            "bounded",
            "fixed commitments",
        ]
        combined = " ".join(rules.values())
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment.lower(), combined.lower())

    def test_ewo_remains_non_installable_until_source_and_rights_gates_pass(self):
        item = self.distribution_item
        self.assertEqual(item["distribution_status"], "snapshot_only")
        self.assertEqual(item["license_status"], "not_assessed")
        self.assertIsNone(item["source_repository_id"])
        self.assertIsNone(item["source_commit"])
        self.assertIsNone(item["package_artifact"])
        self.assertIn("CANONICAL_SOURCE_REPOSITORY_NOT_IDENTIFIED",
                      item["blockers"])
        self.assertIn("PACKAGE_LICENSE_NOT_INDEPENDENTLY_ASSESSED",
                      item["blockers"])
        self.assertIn("LICENSE_FILE_NOT_PRESENT_IN_PLUGIN_SOURCE",
                      item["blockers"])
        self.assertIn("ORIGINAL_SOURCE_LICENSE_AND_ATTRIBUTION_NOT_ASSESSED",
                      item["blockers"])
        self.assertIn("PRIVATE_PLUGIN_CREATOR_SCOPE_NOT_PUBLICLY_INSTALLABLE",
                      item["blockers"])


if __name__ == "__main__":
    unittest.main()
