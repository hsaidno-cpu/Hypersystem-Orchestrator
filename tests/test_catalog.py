"""Unit tests for central catalog and instruction vault invariants."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CatalogValidationTests(unittest.TestCase):
    def test_catalog_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate_catalog.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("PASS: 20 unique plugin identities", result.stdout)
        self.assertIn("PASS: 4 declared and pinned source submodules", result.stdout)
        self.assertIn("PASS: 238 indexed skill instruction records", result.stdout)

    def test_private_submodule_is_declared(self):
        gitmodules = (ROOT / ".gitmodules").read_text(encoding="utf-8")
        self.assertIn("anatomi-prompt-strategis", gitmodules)
        self.assertIn("https://github.com/hsaidno-cpu/anatomi-prompt-strategis.git", gitmodules)

    def test_legacy_plugin_is_redirect_only(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        legacy = next(p for p in catalog["plugins"] if p["plugin_key"] == "asfree-legacy")
        self.assertEqual(legacy["source_state"], "canonical_redirect")
        self.assertEqual(legacy["alias_of"], "asfree-canonical")
        self.assertEqual(legacy["source_classification"], "LEGACY_REDIRECT")

    def test_adjacent_domains_have_separate_owners(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        by_key = {p["plugin_key"]: p for p in catalog["plugins"]}
        self.assertIn("general analytical", by_key["skill-analyzer"]["purpose"].lower())
        self.assertIn("technical anatomy", by_key["asfree-canonical"]["purpose"].lower())
        self.assertIn("independent", by_key["evaluator-team"]["purpose"].lower())
        self.assertIn("engineering lifecycle", by_key["skill-developer-orchestrator"]["purpose"].lower())

    def test_video_explainer_target_version_is_not_misreported_as_released(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        item = next(p for p in catalog["plugins"] if p["plugin_key"] == "video-explainer-promkes-v4-1-12")
        self.assertIsNone(item["release_version"])
        self.assertEqual(item["target_version"], "4.1.12")
        self.assertEqual(item["observed_skill_version"], "v4.0.9")
        self.assertEqual(item["version_reconciliation_status"], "TARGET_SELECTED_SOURCE_SYNC_PENDING")


if __name__ == "__main__":
    unittest.main()
