"""Tests for canonical source and redistribution-rights provenance."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "catalog" / "source-rights-registry.json"
VALIDATOR = ROOT / "tools" / "validate_source_rights.py"


class SourceRightsRegistryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.records = {x["plugin_key"]: x for x in self.registry["records"]}

    def test_all_22_identities_have_exactly_one_rights_record(self):
        self.assertEqual(self.registry["counts"]["plugin_identity_count"], 22)
        self.assertEqual(set(self.records), {x["plugin_key"] for x in self.catalog["plugins"]})
        self.assertEqual(len(self.registry["records"]), 22)

    def test_verified_source_counts_match_current_parent_gitlinks(self):
        self.assertEqual(self.registry["counts"]["official_pinned_source_count"], 5)
        self.assertEqual(self.registry["counts"]["not_identified_git_source_count"], 14)
        self.assertEqual(self.registry["counts"]["candidate_incomplete_count"], 2)
        self.assertEqual(self.registry["counts"]["legacy_redirect_count"], 1)

    def test_only_sdo_has_apache_rights_cleared_for_its_source(self):
        cleared = [
            x["plugin_key"] for x in self.registry["records"]
            if x["rights"]["license_status"] == "CLEARED_APACHE_2_0_CONDITIONAL"
        ]
        self.assertEqual(cleared, ["skill-developer-orchestrator"])

    def test_asfree_is_noncommercial_and_brand_rights_are_separate(self):
        item = self.records["asfree-canonical"]
        self.assertEqual(item["rights"]["license_id"], "PolyForm-Noncommercial-1.0.0")
        self.assertEqual(item["rights"]["license_status"], "REVIEW_REQUIRED_NONCOMMERCIAL")
        self.assertIn("NOTICE", item["rights"]["required_notice_path"])
        self.assertFalse(item["distribution"]["eligible_for_redistribution"])

    def test_public_repo_without_license_is_not_assumed_redistributable(self):
        for key in ("video-explainer-promkes-v4-1-12", "skill-analyzer"):
            item = self.records[key]
            self.assertEqual(item["rights"]["license_status"], "PRIVATE_NO_LICENSE")
        self.assertEqual(item["plugin_creator_discoverability"], "PRIVATE")
            self.assertFalse(item["distribution"]["eligible_for_redistribution"])

    def test_private_anatomi_source_remains_private_and_unlicensed(self):
        item = self.records["anatomi-prompt-v3-octa-prompt"]
        self.assertEqual(item["source"]["visibility"], "PRIVATE")
        self.assertEqual(item["rights"]["license_status"], "NOT_DECLARED")
        self.assertFalse(item["distribution"]["eligible_for_redistribution"])

    def test_candidates_with_apache_license_are_still_incomplete(self):
        for key in ("photo-fixer", "pvee-promkes-super-orchestrator"):
            item = self.records[key]
            self.assertEqual(item["source"]["verification_state"], "CANDIDATE_INCOMPLETE")
            self.assertEqual(item["rights"]["license_status"], "DECLARED_APACHE_2_0_CANDIDATE_ONLY")
            self.assertFalse(item["distribution"]["eligible_for_redistribution"])

    def test_pending_plugin_creator_snapshots_are_not_release_packages(self):
        pending = [x for x in self.registry["records"] if x["source_state"] == "pending_repository"]
        self.assertEqual(len(pending), 14)
        for item in pending:
            self.assertIsNone(item["source"]["repository_url"])
            self.assertEqual(item["rights"]["license_status"], "NOT_ASSESSED")
            self.assertFalse(item["distribution"]["eligible_for_redistribution"])

    def test_validator_passes_and_installable_count_remains_zero(self):
        result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("0 plugin packages are currently cleared", result.stdout)


if __name__ == "__main__":
    unittest.main()
