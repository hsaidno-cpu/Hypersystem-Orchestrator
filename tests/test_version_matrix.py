"""Regression tests for the generated package/source version registry."""
import json
import unittest
from pathlib import Path

from tools.render_package_version_matrix import render

ROOT = Path(__file__).resolve().parents[1]


class PackageVersionMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        cls.repositories = json.loads((ROOT / "catalog" / "repositories.json").read_text(encoding="utf-8"))

    def test_generated_registry_is_exactly_in_sync(self):
        expected = render(self.catalog, self.repositories)
        actual = (ROOT / "docs" / "CURRENT-VERSION-REGISTRY.md").read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def test_metadata_observation_exists_for_every_registered_package(self):
        self.assertEqual(len(self.catalog["plugins"]), 23)
        self.assertTrue(all(p["platform_metadata_observed_at"] == "2026-11-24" for p in self.catalog["plugins"]))

    def test_version_and_content_parity_are_independent(self):
        by_key = {p["plugin_key"]: p for p in self.catalog["plugins"]}
        sdo = by_key["skill-developer-orchestrator"]
        self.assertEqual(sdo["repository_version"], sdo["platform_package_version"])
        self.assertEqual(sdo["source_instruction_parity_status"], "DRIFT_DETECTED")
        analyzer = by_key["skill-analyzer"]
        self.assertNotEqual(analyzer["repository_version"], analyzer["platform_package_version"])
        self.assertEqual(analyzer["source_instruction_parity_status"], "DRIFT_DETECTED")

    def test_current_source_manifest_evidence_covers_all_integrated_sources(self):
        source_records = [
            r for r in self.repositories["repositories"]
            if r.get("status") in {"integrated_submodule", "integrated_submodule_private"}
        ]
        self.assertEqual(len(source_records), 5)
        for record in source_records:
            self.assertEqual(record["source_manifest_commit"], record["pinned_commit"])
            self.assertRegex(record["source_manifest_blob_sha"], r"^[0-9a-f]{40}$")
            self.assertTrue(record["source_manifest_path"])


if __name__ == "__main__":
    unittest.main()
