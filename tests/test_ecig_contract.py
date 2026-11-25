import base64
import copy
import json
import unittest
import unicodedata
from datetime import datetime, timedelta, timezone

from jsonschema import Draft202012Validator, ValidationError

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.validate_ecig_contract import (
    EXAMPLE_PATH,
    ContractError,
    attestation_signing_bytes,
    evidence_binding_sha256,
    evidence_signing_bytes,
    load_contract,
    load_trusted_public_keys,
    validate_attestation,
    validate_policy,
)


def iso_utc(value=None):
    value = value or datetime.now(timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parsed_utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def sample_attestation():
    observed_at = iso_utc()
    return {
        "schema_version": "1.0.0",
        "attestation_id": "hso-ecig-test-001",
        "policy_version": "1.0.0",
        "plugin_key": "hypersystem-orchestrator",
        "target": {"platform": "ChatGPT", "target_scope": "test-target"},
        "observed_at": observed_at,
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
            "observed_at": observed_at,
            "verifier": "test-fixture",
            "sha256": "e" * 64,
        }],
        "signature": None,
        "conflicts": [],
        "limitations": ["Test fixture intentionally has unknown package and install evidence."],
    }


def synced_attestation():
    item = sample_attestation()
    observed_at = item["observed_at"]
    timestamp = parsed_utc(observed_at)
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
    item["evidence"] = []
    evidence_kinds = (
        "COMMIT", "MANIFEST", "PACKAGE_READBACK",
        "INSTALL_RECEIPT", "RUNTIME_PROBE",
        "INSTRUCTION_COMPARISON", "DOCUMENTATION_READBACK",
    )
    for index, kind in enumerate(evidence_kinds):
        item["evidence"].append({
            "kind": kind,
            "locator": f"https://evidence.example.test/{kind.lower()}-{index}",
            "observed_at": observed_at,
            "verifier": "test-fixture",
            "sha256": f"{index + 2:x}" * 64,
        })
    actions = (
        "canonical_source_selection_or_replacement",
        "ownership_license_or_redistribution_disposition",
        "package_publication_republication_or_release_channel_promotion",
        "target_install_upgrade_enable_disable_or_uninstall",
    )
    item["approvals"] = []
    for index, action in enumerate(actions):
        decision_reference = f"https://evidence.example.test/decisions/{index + 1}"
        item["approvals"].append({
            "action": action,
            "decision": "APPROVED",
            "decision_reference": decision_reference,
            "decided_at": observed_at,
            "approver": "hsaidno-cpu",
        })
        item["evidence"].append({
            "kind": "HUMAN_DECISION",
            "locator": decision_reference,
            "observed_at": observed_at,
            "verifier": "hsaidno-cpu",
            "sha256": f"{index + 9:x}" * 64,
        })
    item["signature"] = {
        "algorithm": "Ed25519",
        "key_id": "hso-ecig-ephemeral-test-key",
        "value": base64.b64encode(bytes(64)).decode("ascii"),
    }
    item["limitations"] = []
    item["conflicts"] = []
    return item, timestamp


def signed_synced_attestation(private_key=None):
    item, timestamp = synced_attestation()
    private_key = private_key or Ed25519PrivateKey.generate()
    key_id = "gov01-ephemeral-test-key"
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    trusted = {key_id: base64.b64encode(public_key).decode("ascii")}

    for evidence in item["evidence"]:
        evidence["binding_sha256"] = evidence_binding_sha256(item, evidence)
        evidence["proof"] = {"algorithm": "Ed25519", "key_id": key_id, "value": ""}
        evidence["proof"]["value"] = base64.b64encode(
            private_key.sign(evidence_signing_bytes(item, evidence))
        ).decode("ascii")

    item["signature"] = {"algorithm": "Ed25519", "key_id": key_id, "value": ""}
    item["signature"]["value"] = base64.b64encode(
        private_key.sign(attestation_signing_bytes(item))
    ).decode("ascii")
    return item, trusted, timestamp


class EcosystemIntegrityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema, cls.policy = load_contract()

    def test_schema_and_policy_are_consistent(self):
        validate_policy(self.schema, self.policy)

    def test_explicit_unknown_state_is_valid(self):
        validate_attestation(sample_attestation(), self.schema, self.policy)

    def test_checked_in_unknown_example_is_valid(self):
        example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        validate_attestation(example, self.schema, self.policy)

    def test_human_decision_evidence_requires_sha256_digest(self):
        item = sample_attestation()
        item["evidence"].append({
            "kind": "HUMAN_DECISION",
            "locator": "https://evidence.example.test/decision/1",
            "observed_at": item["observed_at"],
            "verifier": "hsaidno-cpu",
        })
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(item)

    def test_trust_store_is_empty_until_a_key_is_approved(self):
        self.assertEqual(load_trusted_public_keys(), {})

    def test_synced_requires_trusted_ed25519_signature_plane_evidence_and_approvals(self):
        item, trusted, timestamp = signed_synced_attestation()
        validate_attestation(
            item, self.schema, self.policy,
            trusted_public_keys=trusted, now=timestamp,
        )

    def test_synced_rejects_unknown_trust_key_and_tampered_signature(self):
        item, trusted, timestamp = signed_synced_attestation()
        with self.assertRaisesRegex(ContractError, "not trusted"):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys={}, now=timestamp,
            )
        tampered = copy.deepcopy(item)
        tampered["signature"]["value"] = base64.b64encode(bytes([1]) * 64).decode("ascii")
        with self.assertRaisesRegex(ContractError, "signature verification failed"):
            validate_attestation(
                tampered, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

    def test_synced_rejects_tampered_or_untrusted_evidence_proofs(self):
        for mutation in ("digest", "locator", "key"):
            private_key = Ed25519PrivateKey.generate()
            item, trusted, timestamp = signed_synced_attestation(private_key)
            evidence = item["evidence"][0]
            if mutation == "digest":
                evidence["sha256"] = "f" * 64
            elif mutation == "locator":
                evidence["locator"] = "https://attacker.example.invalid/replaced"
            else:
                evidence["proof"]["key_id"] = "untrusted-verifier"
            # Re-sign only the outer envelope so failure must come from the evidence proof.
            item["signature"]["value"] = base64.b64encode(
                private_key.sign(attestation_signing_bytes(item))
            ).decode("ascii")
            with self.subTest(mutation=mutation), self.assertRaises(ContractError):
                validate_attestation(
                    item, self.schema, self.policy,
                    trusted_public_keys=trusted, now=timestamp,
                )

    def test_synced_evidence_binding_includes_exact_target_and_claim(self):
        private_key = Ed25519PrivateKey.generate()
        item, trusted, timestamp = signed_synced_attestation(private_key)
        item["target"]["target_scope"] = "different-target"
        # Re-sign the outer envelope; the evidence claim signatures remain stale.
        item["signature"]["value"] = base64.b64encode(
            private_key.sign(attestation_signing_bytes(item))
        ).decode("ascii")
        with self.assertRaisesRegex(ContractError, "binding digest does not match"):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

    def test_synced_rejects_stale_plane_specific_evidence(self):
        item, trusted, timestamp = signed_synced_attestation()
        old = iso_utc(timestamp - timedelta(days=31))
        next(entry for entry in item["evidence"] if entry["kind"] == "PACKAGE_READBACK")["observed_at"] = old
        with self.assertRaisesRegex(ContractError, "PACKAGE_READBACK evidence exceeds"):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

    def test_synced_rejects_missing_plane_specific_evidence(self):
        item, trusted, timestamp = signed_synced_attestation()
        item["evidence"] = [e for e in item["evidence"] if e["kind"] != "RUNTIME_PROBE"]
        with self.assertRaisesRegex(ContractError, "requires plane-specific RUNTIME_PROBE"):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

    def test_synced_rejects_missing_human_decision_evidence(self):
        item, trusted, timestamp = signed_synced_attestation()
        item["evidence"] = [
            evidence for evidence in item["evidence"]
            if evidence["kind"] != "HUMAN_DECISION"
        ]
        with self.assertRaisesRegex(ContractError, "no matching HUMAN_DECISION evidence"):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

    def test_synced_rejects_mismatched_human_decision_reference(self):
        item, trusted, timestamp = signed_synced_attestation()
        item["approvals"][0]["decision_reference"] = "https://evidence.example.test/decisions/not-the-same"
        with self.assertRaisesRegex(ContractError, "no matching HUMAN_DECISION evidence"):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

    def test_synced_rejects_human_decision_evidence_older_than_approval(self):
        item, trusted, timestamp = signed_synced_attestation()
        first_reference = item["approvals"][0]["decision_reference"]
        decision_evidence = next(
            evidence for evidence in item["evidence"]
            if evidence["kind"] == "HUMAN_DECISION" and evidence["locator"] == first_reference
        )
        decision_evidence["observed_at"] = iso_utc(timestamp - timedelta(minutes=10))
        with self.assertRaisesRegex(ContractError, "HUMAN_DECISION evidence predates the recorded decision"):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

    def test_synced_rejects_pending_or_rejected_approvals(self):
        for decision in ("PENDING", "REJECTED"):
            item, trusted, timestamp = signed_synced_attestation()
            item["approvals"][0]["decision"] = decision
            with self.subTest(decision=decision), self.assertRaisesRegex(ContractError, "unresolved or rejected"):
                validate_attestation(
                    item, self.schema, self.policy,
                    trusted_public_keys=trusted, now=timestamp,
                )

    def test_synced_requires_each_action_specific_approval(self):
        item, trusted, timestamp = signed_synced_attestation()
        item["approvals"] = [
            approval for approval in item["approvals"]
            if approval["action"] != "target_install_upgrade_enable_disable_or_uninstall"
        ]
        with self.assertRaisesRegex(ContractError, "missing required human approval"):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

    def test_synced_rejects_unknown_rights_or_drifted_plane(self):
        item, trusted, timestamp = signed_synced_attestation()
        item["rights"]["state"] = "UNKNOWN"
        with self.assertRaises(ContractError):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )
        item, trusted, timestamp = signed_synced_attestation()
        item["instructions"]["state"] = "DRIFT"
        with self.assertRaises(ContractError):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

    def test_synced_rejects_unresolved_limitation(self):
        item, trusted, timestamp = signed_synced_attestation()
        item["limitations"] = ["Not independently observed"]
        with self.assertRaises(ContractError):
            validate_attestation(
                item, self.schema, self.policy,
                trusted_public_keys=trusted, now=timestamp,
            )

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

    def test_manifest_paths_colliding_after_nfc_normalization_are_rejected(self):
        item = sample_attestation()
        item["instructions"]["file_count"] = 2
        item["instructions"]["per_file_digests"] = [
            {"path": "skills/café.md", "sha256": "a" * 64},
            {"path": unicodedata.normalize("NFD", "skills/café.md"), "sha256": "b" * 64},
        ]
        with self.assertRaisesRegex(ContractError, "after NFC normalization"):
            validate_attestation(item, self.schema, self.policy)

    def test_approved_evidence_requires_approver_subject(self):
        item = sample_attestation()
        item["approvals"] = [{
            "action": "release",
            "decision": "APPROVED",
            "decision_reference": "decision-123",
            "decided_at": item["observed_at"],
            "approver": None,
        }]
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)

    def test_policy_version_mismatch_is_rejected(self):
        item = sample_attestation()
        item["policy_version"] = "0.9.0"
        with self.assertRaises(ContractError):
            validate_attestation(item, self.schema, self.policy)

    def test_github_evidence_permissions_cannot_be_widened(self):
        policy = copy.deepcopy(self.policy)
        policy["github"]["evidence_permissions"].append("contents:write")
        with self.assertRaisesRegex(ContractError, "exact read-only allowlist"):
            validate_policy(self.schema, policy)

    def test_privileged_pull_request_rule_cannot_be_relaxed(self):
        policy = copy.deepcopy(self.policy)
        policy["github"]["privileged_pull_request_rule"] = "checkout_pr_head"
        with self.assertRaisesRegex(ContractError, "privileged pull-request rule"):
            validate_policy(self.schema, policy)

    def test_policy_requires_gov01_as_the_only_human_approval_authority(self):
        altered = copy.deepcopy(self.policy)
        altered["authority"]["human_decision_authority"] = "independent_reviewer"
        with self.assertRaisesRegex(ContractError, "authority must remain GOV-01"):
            validate_policy(self.schema, altered)

        altered = copy.deepcopy(self.policy)
        altered["authority"]["additional_human_approvers"] = ["security-reviewer"]
        with self.assertRaisesRegex(ContractError, "second human approver"):
            validate_policy(self.schema, altered)

    def test_policy_requires_gov01_exact_head_trust_root_change(self):
        altered = copy.deepcopy(self.policy)
        altered["signature"]["trust_store_update"] = "reviewed_pull_request_and_human_security_approval"
        with self.assertRaisesRegex(ContractError, "sole GOV-01"):
            validate_policy(self.schema, altered)

    def test_attestation_entry_point_revalidates_policy(self):
        altered = copy.deepcopy(self.policy)
        altered["freshness_hours_or_days"]["source_commit_hours"] = 8760
        with self.assertRaisesRegex(ContractError, "no greater than 24"):
            validate_attestation(sample_attestation(), self.schema, altered)

    def test_policy_rejects_freshness_window_expansion(self):
        policy = copy.deepcopy(self.policy)
        policy["freshness_hours_or_days"]["source_commit_hours"] = 24.01
        with self.assertRaisesRegex(ContractError, "no greater than 24"):
            validate_policy(self.schema, policy)

    def test_policy_rejects_invalid_freshness_values(self):
        for invalid in (True, float("inf"), float("nan"), 0, -1, "24", 10 ** 400):
            policy = copy.deepcopy(self.policy)
            policy["freshness_hours_or_days"]["source_commit_hours"] = invalid
            with self.subTest(value=repr(invalid)), self.assertRaises(ContractError):
                validate_policy(self.schema, policy)

    def test_policy_requires_all_mandatory_human_approvals(self):
        policy = copy.deepcopy(self.policy)
        policy["human_approval_required"].remove("production_permission_secret_scope_or_trust_policy_change")
        with self.assertRaisesRegex(ContractError, "mandatory human-approval action"):
            validate_policy(self.schema, policy)

    def test_policy_requires_all_never_automatic_controls(self):
        policy = copy.deepcopy(self.policy)
        policy["never_automatic"].remove("promote_unknown_stale_or_not_compared_to_pass")
        with self.assertRaisesRegex(ContractError, "mandatory never-automatic safeguard"):
            validate_policy(self.schema, policy)


if __name__ == "__main__":
    unittest.main()
