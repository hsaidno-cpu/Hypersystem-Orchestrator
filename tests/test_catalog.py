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
        self.assertIn("PASS: 22 unique plugin identities", result.stdout)
        self.assertIn("PASS: 5 declared and pinned source submodules", result.stdout)
        self.assertIn("PASS: 256 indexed skill instruction records", result.stdout)

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

    def test_video_explainer_deployment_and_source_versions_are_separate(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        item = next(p for p in catalog["plugins"] if p["plugin_key"] == "video-explainer-promkes-v4-1-12")
        self.assertEqual(item["release_version"], "4.1.12")
        self.assertEqual(item["target_version"], "4.1.12")
        self.assertEqual(item["deployed_plugin_version"], "4.1.12")
        self.assertEqual(item["source_repository_version"], "4.1.9")
        self.assertEqual(item["observed_skill_version"], "v4.0.9")
        self.assertEqual(item["version_reconciliation_status"], "DEPLOYED_RELEASE_VERIFIED_SOURCE_BEHIND")
        self.assertEqual(item["source_classification"], "OFFICIAL_PUBLIC_SOURCE_LAGGING")



    def test_package_version_planes_are_recorded_without_collapsing_source_and_deployment(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        by_key = {p["plugin_key"]: p for p in catalog["plugins"]}
        for item in catalog["plugins"]:
            self.assertTrue(item["platform_package_version"])
            self.assertTrue(item["platform_current_release_id"])
            self.assertEqual(item["platform_scope"], "USER")
            self.assertEqual(item["platform_discoverability"], "PRIVATE")
        self.assertEqual(by_key["skill-analyzer"]["repository_version"], "1.3.0")
        self.assertEqual(by_key["skill-analyzer"]["platform_package_version"], "1.0.0")
        self.assertEqual(by_key["asfree-canonical"]["repository_version"], "0.5.0-rc.1")
        self.assertEqual(by_key["asfree-canonical"]["platform_package_version"], "0.3.2")
        self.assertEqual(by_key["video-explainer-promkes-v4-1-12"]["repository_version"], "4.1.9")
        self.assertEqual(by_key["video-explainer-promkes-v4-1-12"]["platform_package_version"], "4.1.12")
        self.assertEqual(by_key["anatomi-prompt-v3-octa-prompt"]["repository_version"], "3.0.0")
        self.assertEqual(by_key["anatomi-prompt-v3-octa-prompt"]["platform_package_version"], "3.0.0")

    def test_primary_responsibility_boundaries_are_distinct(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        by_key = {p["plugin_key"]: p for p in catalog["plugins"]}
        self.assertIn("general analytical methodology", by_key["skill-analyzer"]["purpose"].lower())
        self.assertIn("technical anatomy", by_key["asfree-canonical"]["purpose"].lower())
        self.assertIn("independent", by_key["evaluator-team"]["purpose"].lower())
        self.assertIn("engineering lifecycle", by_key["skill-developer-orchestrator"]["purpose"].lower())
        self.assertIn("octa-prompt", by_key["anatomi-prompt-v3-octa-prompt"]["purpose"].lower())
        self.assertIn("source-content-to-prompt", by_key["ai-prompt-finder-creator"]["purpose"].lower())
        self.assertIn("general", by_key["photo-fixer"]["purpose"].lower())
        self.assertIn("restoration", by_key["master-photo-restoration"]["purpose"].lower())

    def test_media_plugin_owners_are_separated(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        by_key = {p["plugin_key"]: p for p in catalog["plugins"]}
        self.assertIn("audio/voice-over-first", by_key["godex-motion-audio"]["purpose"].lower())
        self.assertIn("visual-first", by_key["motion-graphic-arifanara-v-01"]["purpose"].lower())
        self.assertIn("health", by_key["pvee-promkes-super-orchestrator"]["primary_domain"])
        self.assertIn("renderer-neutral production engine", by_key["video-explainer-promkes-v4-1-12"]["purpose"].lower())

    def test_photo_restoration_and_legacy_route_are_exclusive(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        by_key = {p["plugin_key"]: p for p in catalog["plugins"]}
        fixer_negative = " ".join(by_key["photo-fixer"]["negative_triggers"]).lower()
        restoration_positive = " ".join(by_key["master-photo-restoration"]["primary_triggers"]).lower()
        self.assertIn("historical", fixer_negative)
        self.assertIn("aged", restoration_positive)
        self.assertEqual(by_key["asfree-legacy"]["source_classification"], "LEGACY_REDIRECT")
        self.assertEqual(by_key["asfree-legacy"]["alias_of"], "asfree-canonical")


    def test_compatibility_matrix_has_unique_edges_and_no_runtime_overclaim(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        matrix = json.loads((ROOT / "catalog" / "compatibility-matrix.json").read_text(encoding="utf-8"))
        keys = {p["plugin_key"] for p in catalog["plugins"]}
        edges = matrix["integrations"]
        ids = [e["integration_id"] for e in edges]
        self.assertEqual(len(edges), matrix["integration_count"])
        self.assertEqual(len(ids), len(set(ids)))
        for edge in edges:
            self.assertIn(edge["producer_plugin"], keys)
            self.assertIn(edge["consumer_plugin"], keys)
            self.assertIn(edge["canonical_truth_owner"], keys)
            self.assertTrue(edge["input_artifacts"])
            self.assertTrue(edge["output_artifact"])
            self.assertEqual(edge["contract_version"], "1.0.0")
            self.assertEqual(edge["runtime_execution_test"], "NOT_RUN")
            self.assertEqual(edge["host_activation_test"], "NOT_RUN")
        by_id = {e["integration_id"]: e for e in edges}
        self.assertEqual(by_id["INT-PVEE-VIDEO-001"]["canonical_truth_owner"], "pvee-promkes-super-orchestrator")
        self.assertEqual(by_id["INT-EVALUATOR-SDO-001"]["consumer_plugin"], "skill-developer-orchestrator")
        self.assertEqual(by_id["INT-PHOTO-RESTORE-ROUTE-001"]["handoff_type"], "ROUTING_OVERRIDE")
        self.assertEqual(by_id["INT-GODEX-MOTION-001"]["canonical_truth_owner"], "godex-motion-audio")


    def test_sdo_official_source_submodule_and_version_are_reconciled(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        repositories = json.loads((ROOT / "catalog" / "repositories.json").read_text(encoding="utf-8"))
        sdo = next(p for p in catalog["plugins"] if p["plugin_key"] == "skill-developer-orchestrator")
        source = next(r for r in repositories["repositories"] if r["repository_id"] == "skill-developer-orchestrator")
        self.assertEqual(sdo["source_state"], "integrated_submodule")
        self.assertEqual(sdo["source_classification"], "OFFICIAL_SUBMODULE")
        self.assertEqual(sdo["release_version"], "0.1.0")
        self.assertEqual(sdo["repository_version"], "0.1.0")
        self.assertEqual(sdo["platform_package_version"], "0.1.0")
        self.assertEqual(sdo["version_alignment_state"], "SOURCE_AND_PLATFORM_MATCH")
        self.assertEqual(source["pinned_commit"], "9d3c4bc09179ff857df4f3819be83e1847571add")
        self.assertEqual(source["license_status"], "APACHE-2.0")
        self.assertTrue(source["commit_signature_verified"])

    def test_pvee_repository_is_candidate_not_canonical_submodule(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        repositories = json.loads((ROOT / "catalog" / "repositories.json").read_text(encoding="utf-8"))
        pvee = next(p for p in catalog["plugins"] if p["plugin_key"] == "pvee-promkes-super-orchestrator")
        source = next(r for r in repositories["repositories"] if r["repository_id"] == "pvee-promkes-candidate")
        self.assertEqual(pvee["source_state"], "candidate_repository")
        self.assertEqual(pvee["source_classification"], "CANDIDATE_INCOMPLETE")
        self.assertEqual(source["status"], "candidate_not_integrated")
        self.assertNotIn("submodule_path", source)
        self.assertIsNone(pvee["repository_version"])

    def test_sdo_version_match_does_not_hide_instruction_content_drift(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        sdo = next(p for p in catalog["plugins"] if p["plugin_key"] == "skill-developer-orchestrator")
        self.assertEqual(sdo["repository_version"], "0.1.0")
        self.assertEqual(sdo["platform_package_version"], "0.1.0")
        self.assertEqual(sdo["version_alignment_state"], "SOURCE_AND_PLATFORM_MATCH")
        self.assertEqual(sdo["source_instruction_parity_status"], "DRIFT_DETECTED")
        self.assertEqual(sdo["source_sync_status"], "SOURCE_INSTRUCTION_DRIFT_DETECTED")
        self.assertIn("23,651", sdo["source_instruction_parity_note"])
        self.assertIn("10,573", sdo["source_instruction_parity_note"])
    def test_people_business_competency_academy_is_snapshot_only_and_scoped(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        item = next(p for p in catalog["plugins"] if p["plugin_key"] == "people-business-competency-academy")
        self.assertEqual(item["plugin_creator_id"], "plugins_6b039ef9d14c81918f521f6fe56a8ddc")
        self.assertEqual(item["source_state"], "pending_repository")
        self.assertIsNone(item["source_repository_id"])
        self.assertEqual(item["source_classification"], "NOT_IDENTIFIED")
        self.assertEqual(item["instruction_skill_count"], 9)
        self.assertEqual(item["platform_package_version"], "0.1.0")
        self.assertEqual(item["source_sync_status"], "GITHUB_SOURCE_NOT_IDENTIFIED")

        snapshot = json.loads((ROOT / "catalog" / "instruction-snapshots.json").read_text(encoding="utf-8"))
        indexed = next(p for p in snapshot["plugins"] if p["plugin_key"] == "people-business-competency-academy")
        self.assertEqual(indexed["skill_count"], 9)
        self.assertEqual(indexed["plugin_creator_release_id"], "pluginrel_6b039efc6dfc81919fffbe265e8f84c9")

        book_catalog = json.loads((ROOT / "plugin-instructions" / "people-business-competency-academy" / "assets" / "competency-and-reading-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(book_catalog["totals"]["competencies"], 20)
        self.assertEqual(book_catalog["totals"]["people_skills_competencies"], 12)
        self.assertEqual(book_catalog["totals"]["business_skills_competencies"], 8)
        self.assertEqual(book_catalog["totals"]["book_references"], 100)
        self.assertEqual(sum(len(d["books"]) for d in book_catalog["domains"]), 100)
        self.assertTrue(all(b["bibliographic_verification"] == "NOT_INDEPENDENTLY_VERIFIED" for d in book_catalog["domains"] for b in d["books"]))

    def test_pre_registration_is_additive_and_snapshot_only(self):
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        snapshots = json.loads((ROOT / "catalog" / "instruction-snapshots.json").read_text(encoding="utf-8"))
        pre = next(p for p in catalog["plugins"] if p["plugin_key"] == "progressive-roadmap-evaluator")
        indexed = next(p for p in snapshots["plugins"] if p["plugin_key"] == "progressive-roadmap-evaluator")
        self.assertEqual(catalog["expected_plugin_count"], 22)
        self.assertEqual(len(catalog["plugins"]), 22)
        self.assertEqual(pre["plugin_creator_id"], "plugins_6b038580bc4881911bbaa159e5ecf2a22")
        self.assertEqual(pre["platform_package_version"], "0.1.1")
        self.assertEqual(pre["platform_current_release_id"], "pluginrel_6b0385d7a4488191a681997c0d9ae531")
        self.assertEqual(pre["source_state"], "pending_repository")
        self.assertIsNone(pre["source_repository_id"])
        self.assertEqual(pre["instruction_skill_count"], 9)
        self.assertEqual(indexed["skill_count"], 9)
        self.assertEqual(snapshots["total_skill_records"], 256)

if __name__ == "__main__":
    unittest.main()
