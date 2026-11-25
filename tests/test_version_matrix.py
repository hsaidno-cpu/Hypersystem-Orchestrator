"""Regression tests for the generated package/source version registry."""
import json
import unittest
from pathlib import Path

from tools.render_package_version_matrix import render
from tools.validate_catalog import git_blob_sha

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
        from datetime import date
        revision = date.fromisoformat(self.catalog["catalog_revision"])
        observations = [date.fromisoformat(p["platform_metadata_observed_at"]) for p in self.catalog["plugins"]]
        self.assertTrue(all(observed <= revision for observed in observations))

    def test_version_and_content_parity_are_independent(self):
        by_key = {p["plugin_key"]: p for p in self.catalog["plugins"]}
        sdo = by_key["skill-developer-orchestrator"]
        self.assertEqual(sdo["repository_version"], sdo["platform_package_version"])
        self.assertEqual(sdo["source_instruction_parity_status"], "DRIFT_DETECTED")
        analyzer = by_key["skill-analyzer"]
        self.assertNotEqual(analyzer["repository_version"], analyzer["platform_package_version"])
        self.assertEqual(analyzer["source_instruction_parity_status"], "DRIFT_DETECTED")

    def test_git_blob_sha_matches_git_object_format(self):
        self.assertEqual(
            git_blob_sha(b"test\n"),
            "9daeafb9864cf43055ae93beb0afd6c7d144bfa4",
        )

    def test_source_manifest_verification_mode_is_explicit(self):
        integrated = [
            r for r in self.repositories["repositories"]
            if r.get("status") in {"integrated_submodule", "integrated_submodule_private"}
        ]
        self.assertEqual(
            sum(r.get("source_manifest_verification_mode") == "CI_RAW_CONTENT_GIT_BLOB" for r in integrated),
            4,
        )
        self.assertEqual(
            sum(r.get("source_manifest_verification_mode") == "PRIVATE_MANUAL_READBACK_ONLY" for r in integrated),
            1,
        )

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
            self.assertEqual(record["source_manifest_version"], record["package_version"])


if __name__ == "__main__":
    unittest.main()
