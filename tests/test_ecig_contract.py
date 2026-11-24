import copy
import unittest

from tools.validate_ecig_contract import (
    ContractError,
    load_contract,
    validate_attestation,
    validate_policy,
)


def sample_attestation():
    return {
        "schema_version": "1.0.0",
        "attestation_id": "hso-ecig-test-001",
        "policy_version": "1.0.0",
        "plugin_key": "hypersystem-orchestrator",
        "target": {"platform": "ChatGPT", "target_scope": "test-target"},
        "observed_at": "2026-11-24T04:50:00Z",
        "source": {
            "repository_url": "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator",
            "ref": "main",
            "commit_sha": "a" * 40,
            "manifest_path": "manifest.json",
            "manifest_sha256": "b" * 64,
            "tree_digest": "c" * 64,
            "state": "UNKNOWN",
        },
        "package": {"publication_state": "UNKNOWN", "state": "UNKNOWN"},
        "installation": {
            "install_state": "UNKNOWN", "runtime_state": "NOT_PROBED", "state": "UNKNOWN"
        },
        "instructions": {
            "manifest_version": "1.0.0",
            "bundle_digest": "d" * 64,
            "file_count": 0,
            "per_file_digests": [],
            "parity_state": "NOT_COMPARED",
            "state": "UNKNOWN",
        },
        "documentation": {
            "notion_page_url": None, "projection_digest": None, "state": "UNKNOWN"
        },
        "rights": {"state": "UNKNOWN"},
        "overall_state": "UNKNOWN",
        "evidence": [{
            "kind": "COMMIT",
            "locator": "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/commit/" + "a" * 40,
            "observed_at": "2026-11-24T04:50:00Z",
            "verifier": "test-fixture",
            "sha256": "e" * 64,
        }],
        "signature": None,
        "conflicts": [],
        "limitations": ["Test fixture intentionally has unknown package and install evidence."],
    }


def synced_attestation():
    item = sample_attestation()
    for plane in ("source", "package", "installation", "instructions", "documentation"):
        item[plane]["state"] = "MATCH"
    item["package"]["publication_state"] = "PUBLISHED"
    item["installation"]["install_state"] = "INSTALLED"
    item["installation"]["runtime_state"] = "ACTIVE"
    item["instructions"]["file_count"] = 1
    item["instructions"]["per_file_digests"] = [{
        "path": "skills/main/skill.md", "sha256": "f" * 64
    }]
    item["instructions"]["parity_state"] = "MATCH"
    item["documentation"]["notion_page_url"] = "https://www.notion.so/example"
    item["documentation"]["projection_digest"] = "1" * 64
    item["rights"]["state"] = "CLEARED"
    item["overall_state"] = "SYNCED"
    item["signature"] = {
        "algorithm": "Ed25519",
        "key_id": "hso-ecig-test-key-01",
        "value": "A" * 86 + "==",
    }
    item["limitations"] = []
    item["conflicts"] = []
    return item


class EcosystemIntegrityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema, cls.policy = load_contract()

    def test_schema_and_policy_are_consistent(self):
        validate_policy(self.schema, self.policy)

    def test_explicit_unknown_state_is_valid(self):
        validate_attestation(sample_attestation(), self.schema, self.policy)

    def test_synced_requires_every_plane_match_rights_clear_and_ed25519_signature(self):
        validate_attestation(synced_attestation(), self.schema, self.policy)

    def test_synced_rejects_unknown_rights_or_drifted_plane(self):
        item = synced_attestation()
        item["rights"]["state"] = "UNKNOWN"
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)
        item = synced_attestation()
        item["instructions"]["state"] = "DRIFT"
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)

    def test_synced_rejects_missing_signature_and_unresolved_limitation(self):
        item = synced_attestation()
        item["signature"] = None
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)
        item = synced_attestation()
        item["limitations"] = ["Not independently observed"]
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)

    def test_manifest_file_count_and_paths_are_consistent(self):
        item = sample_attestation()
        item["instructions"]["file_count"] = 1
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)
        item["instructions"]["per_file_digests"] = [
            {"path": "../escape.md", "sha256": "a" * 64}
        ]
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)

    def test_duplicate_manifest_paths_are_rejected(self):
        item = sample_attestation()
        item["instructions"]["file_count"] = 2
        item["instructions"]["per_file_digests"] = [
            {"path": "skills/main.md", "sha256": "a" * 64},
            {"path": "skills/main.md", "sha256": "b" * 64},
        ]
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)

    def test_approved_evidence_requires_approver_subject(self):
        item = sample_attestation()
        item["approvals"] = [{
            "action": "release",
            "decision": "APPROVED",
            "decision_reference": "decision-123",
            "decided_at": "2026-11-24T04:50:00Z",
            "approver": None,
        }]
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)

    def test_policy_version_mismatch_is_rejected(self):
        item = sample_attestation()
        item["policy_version"] = "0.9.0"
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)


if __name__ == "__main__":
    unittest.main()
