"""C2/C3 assurance for 15 tested edges; additional interface-only edges remain unexecuted.

C2 validates deterministic synthetic payloads against the published JSON Schema.
C3 exercises a strict mock receiver; no plugin, host or runtime is invoked.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts" / "plugin-handoff.schema.json"
MATRIX_PATH = ROOT / "catalog" / "compatibility-matrix.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "handoffs" / "contract-fixtures.json"


class MockReceiverRejected(ValueError):
    """The payload is valid JSON but violates the edge's receiver contract."""


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def mock_receiver_accept(payload: dict, edge: dict, validator: Draft202012Validator):
    """Validate schema and edge-specific semantics without invoking a plugin."""
    validator.validate(payload)

    actual_producer = payload["source_plugin"]["plugin_key"]
    actual_consumer = payload["recipient_plugin"]["plugin_key"]
    actual_contract = payload["recipient_plugin"]["contract_version"]

    if actual_producer != edge["producer_plugin"]:
        raise MockReceiverRejected("producer_plugin does not match edge producer")
    if actual_consumer != edge["consumer_plugin"]:
        raise MockReceiverRejected("recipient_plugin does not match edge consumer")
    if actual_contract != edge["contract_version"]:
        raise MockReceiverRejected("contract_version does not match edge contract")
    if payload["expected_output"] != edge["output_artifact"]:
        raise MockReceiverRejected("expected_output does not match edge output artifact")
    if payload["acceptance_criteria"] != edge["acceptance_criteria"]:
        raise MockReceiverRejected("acceptance_criteria do not match edge contract")

    return {
        "disposition": "MOCK_ACCEPTED",
        "integration_id": edge["integration_id"],
        "receiver": edge["consumer_plugin"],
        "contract_version": edge["contract_version"],
    }


class HandoffContractAssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.matrix = load_json(MATRIX_PATH)
        cls.fixture_doc = load_json(FIXTURE_PATH)
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)
        cls.edges = {
            edge["integration_id"]: edge
            for edge in cls.matrix["integrations"]
        }
        cls.fixtures = {
            fixture["fixture_id"]: fixture["payload"]
            for fixture in cls.fixture_doc["fixtures"]
        }

    def test_fixture_inventory_covers_all_15_tested_matrix_edges(self):
        self.assertEqual(self.matrix["integration_count"], 16)
        self.assertEqual(self.fixture_doc["count"], 15)
        tested = {key for key, edge in self.edges.items() if edge["status"] == "CONTRACT_TESTED"}
        interface_only = {key for key, edge in self.edges.items() if edge["status"] == "INTERFACE_DEFINED_NOT_EXECUTED"}
        self.assertEqual(set(self.fixtures), tested)
        self.assertEqual(len(tested), 15)
        self.assertEqual(interface_only, {"INT-GROWTHFORGE-ANATOMI-001"})

    def test_c2_all_synthetic_payloads_validate_against_schema(self):
        failures = []
        for integration_id, payload in self.fixtures.items():
            errors = sorted(
                self.validator.iter_errors(payload),
                key=lambda err: list(err.path),
            )
            if errors:
                failures.append(
                    f"{integration_id}: "
                    + "; ".join(error.message for error in errors)
                )
        self.assertEqual(failures, [])

    def test_c2_rejects_missing_required_field(self):
        payload = copy.deepcopy(next(iter(self.fixtures.values())))
        del payload["expected_output"]
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_c2_rejects_unknown_top_level_field(self):
        payload = copy.deepcopy(next(iter(self.fixtures.values())))
        payload["unregistered_authority_override"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_c2_rejects_invalid_capability_state(self):
        payload = copy.deepcopy(next(iter(self.fixtures.values())))
        payload["capability_status"] = "ASSUME_READY"
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_c3_mock_receiver_accepts_all_15_matching_contracts(self):
        accepted = []
        for integration_id, payload in self.fixtures.items():
            receipt = mock_receiver_accept(
                payload,
                self.edges[integration_id],
                self.validator,
            )
            self.assertEqual(receipt["disposition"], "MOCK_ACCEPTED")
            accepted.append(receipt["integration_id"])
        self.assertEqual(set(accepted), set(self.fixtures))

    def test_c3_rejects_wrong_producer(self):
        integration_id = "INT-ANALYZER-ASFREE-001"
        payload = copy.deepcopy(self.fixtures[integration_id])
        payload["source_plugin"]["plugin_key"] = "asfree-canonical"
        with self.assertRaisesRegex(MockReceiverRejected, "producer_plugin"):
            mock_receiver_accept(payload, self.edges[integration_id], self.validator)

    def test_c3_rejects_wrong_recipient(self):
        integration_id = "INT-ANALYZER-ASFREE-001"
        payload = copy.deepcopy(self.fixtures[integration_id])
        payload["recipient_plugin"]["plugin_key"] = "evaluator-team"
        with self.assertRaisesRegex(MockReceiverRejected, "recipient_plugin"):
            mock_receiver_accept(payload, self.edges[integration_id], self.validator)

    def test_c3_rejects_contract_version_mismatch(self):
        integration_id = "INT-ANALYZER-ASFREE-001"
        payload = copy.deepcopy(self.fixtures[integration_id])
        payload["recipient_plugin"]["contract_version"] = "9.9.9"
        with self.assertRaisesRegex(MockReceiverRejected, "contract_version"):
            mock_receiver_accept(payload, self.edges[integration_id], self.validator)

    def test_c3_rejects_wrong_output_artifact(self):
        integration_id = "INT-ANALYZER-ASFREE-001"
        payload = copy.deepcopy(self.fixtures[integration_id])
        payload["expected_output"] = "unrelated_output"
        with self.assertRaisesRegex(MockReceiverRejected, "expected_output"):
            mock_receiver_accept(payload, self.edges[integration_id], self.validator)

    def test_fixture_metadata_does_not_claim_runtime_evidence(self):
        self.assertIn("do not assert host activation or runtime execution",
                      self.fixture_doc["purpose"])
        for edge in self.matrix["integrations"]:
            self.assertEqual(edge["host_activation_test"], "NOT_RUN")
            self.assertEqual(edge["runtime_execution_test"], "NOT_RUN")


    def test_matrix_records_c2_c3_pass_without_claiming_c4_c5(self):
        for edge in self.matrix["integrations"]:
            if edge["integration_id"] == "INT-GROWTHFORGE-ANATOMI-001":
                self.assertEqual(edge["status"], "INTERFACE_DEFINED_NOT_EXECUTED")
                self.assertEqual(edge["schema_contract_test"], "NOT_RUN")
                self.assertEqual(edge["contract_behavior_test"], "NOT_RUN")
            else:
                self.assertEqual(edge["status"], "CONTRACT_TESTED")
                self.assertEqual(edge["schema_contract_test"], "PASS")
                self.assertEqual(edge["contract_behavior_test"], "PASS")
            self.assertEqual(edge["host_activation_test"], "NOT_RUN")
            self.assertEqual(edge["runtime_execution_test"], "NOT_RUN")

    def test_growthforge_anatomi_edge_is_not_runtime_overclaimed(self):
        edge = self.edges["INT-GROWTHFORGE-ANATOMI-001"]
        self.assertEqual(edge["producer_plugin"], "growthforge-business-os")
        self.assertEqual(edge["consumer_plugin"], "anatomi-prompt-v3-octa-prompt")
        self.assertEqual(edge["dependency"], "OPTIONAL")
        self.assertEqual(edge["status"], "INTERFACE_DEFINED_NOT_EXECUTED")
        self.assertEqual(edge["schema_contract_test"], "NOT_RUN")
        self.assertEqual(edge["contract_behavior_test"], "NOT_RUN")
        self.assertEqual(edge["host_activation_test"], "NOT_RUN")
        self.assertEqual(edge["runtime_execution_test"], "NOT_RUN")

if __name__ == "__main__":
    unittest.main()
