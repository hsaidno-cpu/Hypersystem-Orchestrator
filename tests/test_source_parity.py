"""Regression assertions for source/package version and instruction parity findings."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "plugins.json"


class SourceParityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.plugins = {p["plugin_key"]: p for p in catalog["plugins"]}

    def test_anatomi_all_nine_skill_files_match(self):
        item = self.plugins["anatomi-prompt-v3-octa-prompt"]
        self.assertEqual(item["source_instruction_parity_status"], "MATCH")
        self.assertEqual(item["repository_version"], "3.0.0")
        self.assertEqual(item["platform_package_version"], "3.0.0")
        self.assertIn("9-file", item["source_instruction_parity_note"])

    def test_skill_analyzer_one_of_twelve_skill_files_drifts(self):
        item = self.plugins["skill-analyzer"]
        self.assertEqual(item["source_instruction_parity_status"], "DRIFT_DETECTED")
        self.assertEqual(item["source_sync_status"], "SOURCE_INSTRUCTION_DRIFT_DETECTED")
        self.assertIn("11/12", item["source_instruction_parity_note"])
        self.assertEqual(item["version_alignment_state"], "SOURCE_AHEAD_OF_PLATFORM")

    def test_asfree_source_and_creator_version_match_but_byte_parity_is_open(self):
        item = self.plugins["asfree-canonical"]
        self.assertEqual(item["source_instruction_parity_status"], "NOT_COMPARED")
        self.assertEqual(item["source_sync_status"], "SOURCE_PLATFORM_VERSION_MATCH_PARITY_NOT_COMPARED")
        self.assertEqual(item["repository_version"], "0.5.0-rc.2")
        self.assertEqual(item["platform_package_version"], "0.5.0-rc.2")
        self.assertIn("byte-level", item["source_instruction_parity_note"].lower())

    def test_sdo_same_version_does_not_hide_four_file_drift(self):
        item = self.plugins["skill-developer-orchestrator"]
        self.assertEqual(item["source_instruction_parity_status"], "DRIFT_DETECTED")
        self.assertIn("0/4", item["source_instruction_parity_note"])
        self.assertEqual(item["repository_version"], "0.1.0")
        self.assertEqual(item["platform_package_version"], "0.1.0")

    def test_video_source_and_deployment_remain_uncompared(self):
        item = self.plugins["video-explainer-promkes-v4-1-12"]
        self.assertEqual(item["source_instruction_parity_status"], "NOT_COMPARED")
        self.assertEqual(item["repository_version"], "4.1.9")
        self.assertEqual(item["platform_package_version"], "4.1.12")
        self.assertIn("no SKILL.md", item["source_instruction_parity_note"])

    def test_pre_private_canonical_source_is_registered_and_pinned(self):
        item = self.plugins["progressive-roadmap-evaluator"]
        self.assertEqual(item["source_state"], "private_repository_source")
        self.assertEqual(item["source_repository_id"], "pre-rpeds-shared-roadmap-dna")
        self.assertEqual(item["repository_version"], "0.1.6")
        self.assertEqual(item["source_instruction_parity_status"], "MATCH")
        self.assertEqual(item["source_sync_status"], "SOURCE_PACKAGE_PARITY_VERIFIED")
        self.assertEqual(item["platform_package_version"], "0.1.6")
        self.assertEqual(item["platform_current_release_id"], "pluginrel_6b0961f9dca08191a8af34dbb2e02881")
        self.assertEqual(item["current_installed_skill_count"], 14)
        self.assertIn("98008cdf3e082fd4cc8de03e51b2863fbae8cf11", item["version_evidence"])
        self.assertIn("artifact", item["version_evidence"].lower())

if __name__ == "__main__":
    unittest.main()
