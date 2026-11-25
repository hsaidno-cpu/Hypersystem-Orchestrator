"""Contract tests for the CSO to HSO handoff serializer."""
import unittest

from tools.cso_handoff_adapter import (
    CSO_PLUGIN_KEY,
    HandoffAdapterError,
    map_epistemic_status,
    serialize_cso_handoff,
)


def local_payload():
    return {
        "handoff_id": "CSO-HANDOFF-020",
        "case_id": "CSO-020",
        "intent": "Transfer accepted CSO findings to the HSO router using the shared contract.",
        "scope": ["Serialize the CSO handoff", "Validate against the pinned HSO schema"],
        "epistemic_status": ["OBSERVATION", "VERIFIED_SOURCE_CLAIM"],
        "capability_status": "READY_WITH_LIMITATIONS",
        "expected_output": "A schema-valid HSO handoff envelope with explicit limitations.",
        "acceptance_criteria": [
            "The envelope contains every required HSO field.",
            "No CSO-only top-level field is emitted.",
            "The result validates against contracts/plugin-handoff.schema.json."
        ],
        "non_goals": ["No network dispatch", "No host activation claim"],
        "inputs": [{
            "locator": "plugin://cognitive-superintelligence-orchestrator",
            "provenance": "Plugin Creator release read-back",
            "sensitivity": "private-package-metadata-only"
        }],
        "findings": [{
            "id": "CSO-F-020",
            "status": "VERIFIED_SOURCE_CLAIM",
            "summary": "The local evidence was checked against the plugin release read-back."
        }],
        "authority": {"level": "proposal", "approval_reference": "NOT_GRANTED"},
        "dependencies": ["HSO shared handoff contract v1.0.0"],
        "risk_and_unknowns": ["The target plugin host has not been invoked."],
        "completion_status": "READY_FOR_HANDOFF"
    }


class CsoHandoffAdapterTests(unittest.TestCase):
    def test_cso_020_serializes_to_the_strict_shared_envelope(self):
        envelope = serialize_cso_handoff(
            local_payload(),
            source_version_or_commit="0.2.0",
            recipient_plugin_key="hso-test-router",
            contract_version="1.0.0"
        )
        self.assertEqual(envelope["case_id"], "CSO-020")
        self.assertEqual(envelope["source_plugin"]["plugin_key"], CSO_PLUGIN_KEY)
        self.assertEqual(envelope["recipient_plugin"]["plugin_key"], "hso-test-router")
        self.assertEqual(envelope["epistemic_status"], ["OBSERVED", "VERIFIED_SOURCE"])
        self.assertEqual(envelope["findings"][0]["status"], "VERIFIED_SOURCE")
        self.assertEqual(envelope["capability_status"], "READY_WITH_LIMITATIONS")
        self.assertNotIn("claim_id", envelope)
        self.assertNotIn("module_id", envelope)
        self.assertEqual(set(envelope) - {
            "handoff_id", "case_id", "source_plugin", "recipient_plugin", "intent",
            "scope", "non_goals", "inputs", "findings", "epistemic_status",
            "capability_status", "authority", "dependencies", "expected_output",
            "acceptance_criteria", "risk_and_unknowns", "completion_status"
        }, set())

    def test_prediction_is_narrowed_to_hypothesis_not_verified_source(self):
        self.assertEqual(map_epistemic_status("PREDICTION"), "HYPOTHESIS")

    def test_canonical_hso_epistemic_labels_pass_through(self):
        for label in (
            "OBSERVED", "VERIFIED_SOURCE", "USER_CLAIM", "SOURCE_CLAIM",
            "ASSUMPTION", "INFERENCE", "HYPOTHESIS", "UNKNOWN"
        ):
            with self.subTest(label=label):
                self.assertEqual(map_epistemic_status(label), label)

    def test_unsupported_normative_and_recommendation_labels_fail_closed(self):
        for label in ("NORMATIVE_JUDGMENT", "RECOMMENDATION", "SOURCE_SUPPORTED"):
            with self.subTest(label=label), self.assertRaises(HandoffAdapterError):
                map_epistemic_status(label)

    def test_unknown_local_fields_are_not_silently_dropped_or_forwarded(self):
        payload = local_payload()
        payload["private_debug_trace"] = "must not cross the boundary"
        with self.assertRaisesRegex(HandoffAdapterError, "Unsupported CSO-local"):
            serialize_cso_handoff(
                payload,
                source_version_or_commit="0.2.0",
                recipient_plugin_key="hso-test-router",
                contract_version="1.0.0"
            )

    def test_unsupported_capability_is_rejected(self):
        payload = local_payload()
        payload["capability_status"] = "SOURCE_SUPPORTED"
        with self.assertRaisesRegex(HandoffAdapterError, "Unsupported HSO capability_status"):
            serialize_cso_handoff(
                payload,
                source_version_or_commit="0.2.0",
                recipient_plugin_key="hso-test-router",
                contract_version="1.0.0"
            )

    def test_empty_acceptance_criteria_is_rejected_by_hso_schema(self):
        payload = local_payload()
        payload["acceptance_criteria"] = []
        with self.assertRaisesRegex(HandoffAdapterError, "acceptance_criteria must contain at least 1 item"):
            serialize_cso_handoff(
                payload,
                source_version_or_commit="0.2.0",
                recipient_plugin_key="hso-test-router",
                contract_version="1.0.0"
            )

    def test_missing_recipient_identity_is_rejected(self):
        with self.assertRaisesRegex(HandoffAdapterError, "recipient_plugin_key"):
            serialize_cso_handoff(
                local_payload(),
                source_version_or_commit="0.2.0",
                recipient_plugin_key=" ",
                contract_version="1.0.0"
            )


if __name__ == "__main__":
    unittest.main()
