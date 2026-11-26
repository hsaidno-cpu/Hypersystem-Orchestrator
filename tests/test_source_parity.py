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

    def test_asfree_release_candidate_has_partial_parity_only(self):
        item = self.plugins["asfree-canonical"]
        self.assertEqual(item["source_instruction_parity_status"], "DRIFT_DETECTED")
        self.assertEqual(item["source_sync_status"], "SOURCE_INSTRUCTION_DRIFT_DETECTED")
        self.assertIn("5/13", item["source_instruction_parity_note"])
        self.assertEqual(item["repository_version"], "0.5.0-rc.1")
        self.assertEqual(item["platform_package_version"], "0.3.2")

    def test_sdo_same_version_does_not_hide_seven_file_drift(self):
        item = self.plugins["skill-developer-orchestrator"]
        self.assertEqual(item["source_instruction_parity_status"], "DRIFT_DETECTED")
        self.assertIn("0/7", item["source_instruction_parity_note"])
        self.assertEqual(item["repository_version"], "0.1.0")
        self.assertEqual(item["platform_package_version"], "0.1.0")

    def test_video_source_and_deployment_remain_uncompared(self):
        item = self.plugins["video-explainer-promkes-v4-1-12"]
        self.assertEqual(item["source_instruction_parity_status"], "NOT_COMPARED")
        self.assertEqual(item["repository_version"], "4.1.9")
        self.assertEqual(item["platform_package_version"], "4.1.12")
        self.assertIn("no SKILL.md", item["source_instruction_parity_note"])

    def test_pre_has_no_git_source_or_instruction_parity_baseline(self):
        item = self.plugins["progressive-roadmap-evaluator"]
        self.assertEqual(item["source_state"], "pending_repository")
        self.assertIsNone(item["source_repository_id"])
        self.assertEqual(item["source_instruction_parity_status"], "NOT_COMPARED")
        self.assertEqual(item["platform_package_version"], "0.1.1")
        self.assertIn("no independent canonical git source repository", item["version_evidence"].lower())

if __name__ == "__main__":
    unittest.main()
