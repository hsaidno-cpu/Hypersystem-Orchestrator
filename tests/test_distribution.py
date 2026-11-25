"""Tests for selective distribution registry and dry-run resolution."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"catalog"/"distribution-registry.json"
PLATFORMS=ROOT/"catalog"/"platform-registry.json"
RESOLVER=ROOT/"tools"/"resolve_distribution.py"


class DistributionValidationTests(unittest.TestCase):
    def load(self,path):
        return json.loads(path.read_text(encoding="utf-8"))

    def run_resolver(self,manifest):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"manifest.json"
            path.write_text(json.dumps(manifest),encoding="utf-8")
            return subprocess.run([sys.executable,str(RESOLVER),"--manifest",str(path)],cwd=ROOT,text=True,capture_output=True,check=False)

    def manifest(self,mode,keys):
        return {"schema_version":"1.0.0","request_id":"test-request","selection_mode":mode,"target_platform":"chatgpt","plugin_keys":keys,"dependency_policy":"explicit_only","version_policy":"pinned","private_source_access_granted":False,"dry_run":True}

    def test_all_catalog_identities_have_distribution_records(self):
        catalog=self.load(ROOT/"catalog"/"plugins.json")
        registry=self.load(REGISTRY)
        self.assertEqual({p["plugin_key"] for p in catalog["plugins"]},{p["plugin_key"] for p in registry["plugins"]})
        self.assertEqual(registry["plugin_count"],len(registry["plugins"]))

    def test_people_business_competency_academy_remains_snapshot_only(self):
        registry = self.load(REGISTRY)
        item = next(p for p in registry["plugins"] if p["plugin_key"] == "people-business-competency-academy")
        self.assertEqual(item["distribution_status"], "snapshot_only")
        self.assertEqual(item["source_state"], "pending_repository")
        self.assertEqual(item["license_status"], "not_assessed")
        self.assertIsNone(item["source_commit"])
        self.assertIsNone(item["package_artifact"])
        self.assertIn("CANONICAL_SOURCE_REPOSITORY_NOT_IDENTIFIED", item["blockers"])
        self.assertIn("PRIVATE_PLUGIN_CREATOR_SCOPE_NOT_PUBLICLY_INSTALLABLE", item["blockers"])

    def test_executive_workday_orchestrator_remains_snapshot_only_until_release_gates_pass(self):
        registry = self.load(REGISTRY)
        item = next(p for p in registry["plugins"] if p["plugin_key"] == "executive-workday-orchestrator")
        self.assertEqual(item["distribution_status"], "snapshot_only")
        self.assertEqual(item["source_state"], "pending_repository")
        self.assertEqual(item["license_status"], "not_assessed")
        self.assertIsNone(item["source_repository_id"])
        self.assertIsNone(item["source_commit"])
        self.assertIsNone(item["package_artifact"])
        self.assertIn("CANONICAL_SOURCE_REPOSITORY_NOT_IDENTIFIED", item["blockers"])
        self.assertIn("PRIVATE_PLUGIN_CREATOR_SCOPE_NOT_PUBLICLY_INSTALLABLE", item["blockers"])
        self.assertIn("PACKAGE_LICENSE_NOT_INDEPENDENTLY_ASSESSED", item["blockers"])
        self.assertIn("PLATFORM_ADAPTER_NOT_HOST_TESTED", item["blockers"])

    def test_no_package_is_falsely_marked_installable(self):
        registry=self.load(REGISTRY)
        eligible=[p for p in registry["plugins"] if p["distribution_status"] in {"installable_public","installable_private"}]
        self.assertEqual(eligible,[])
        self.assertTrue(all(p["blockers"] for p in registry["plugins"]))

    def test_single_request_is_resolved_but_blocked_by_real_gates(self):
        result=self.run_resolver(self.manifest("single",["skill-analyzer"]))
        self.assertEqual(result.returncode,2,msg=result.stdout+result.stderr)
        plan=json.loads(result.stdout)
        self.assertEqual(plan["action"],"PLAN_ONLY_NOT_INSTALLED")
        self.assertEqual(plan["resolution_status"],"BLOCKED")
        self.assertIn("LICENSE_DISTRIBUTION_NOT_CLEARED",plan["resolved_plugins"][0]["blockers"])

    def test_multi_requires_two_or_more(self):
        result=self.run_resolver(self.manifest("multi",["skill-analyzer"]))
        self.assertEqual(result.returncode,1)
        self.assertIn("multi mode requires at least two",result.stderr)

    def test_full_suite_is_dynamic_and_excludes_all_currently_unready_records(self):
        result=self.run_resolver(self.manifest("full_suite",[]))
        self.assertEqual(result.returncode,2)
        plan=json.loads(result.stdout)
        self.assertEqual(plan["requested_plugin_keys"],[])
        self.assertIn("NO_INSTALLABLE_PLUGIN_PACKAGES_AVAILABLE",plan["blockers"])
        registry = self.load(REGISTRY)
        expected_excluded = sum(
            1 for item in registry["plugins"]
            if item["distribution_status"] not in {"installable_public", "installable_private"}
        )
        self.assertEqual(len(plan["excluded_plugins"]), expected_excluded)

    def test_legacy_is_redirect_only(self):
        registry=self.load(REGISTRY)
        item=next(p for p in registry["plugins"] if p["plugin_key"]=="asfree-legacy")
        self.assertEqual(item["distribution_status"],"legacy_redirect")

    def test_host_adapter_states_are_not_overclaimed(self):
        platforms=self.load(PLATFORMS)
        for adapter in platforms["adapters"]:
            self.assertEqual(adapter["adapter_status"],"planned")
            self.assertEqual(adapter["host_activation_test"],"NOT_RUN")
            self.assertEqual(adapter["runtime_execution_test"],"NOT_RUN")


    def test_pre_remains_snapshot_only_until_source_and_rights_are_cleared(self):
        registry = self.load(REGISTRY)
        item = next(p for p in registry["plugins"] if p["plugin_key"] == "progressive-roadmap-evaluator")
        self.assertEqual(item["distribution_status"], "snapshot_only")
        self.assertEqual(item["source_state"], "pending_repository")
        self.assertEqual(item["license_status"], "not_assessed")
        self.assertIsNone(item["source_commit"])
        self.assertIsNone(item["package_artifact"])
        self.assertIn("CANONICAL_SOURCE_REPOSITORY_NOT_IDENTIFIED", item["blockers"])
        self.assertIn("PRIVATE_PLUGIN_CREATOR_SCOPE_NOT_PUBLICLY_INSTALLABLE", item["blockers"])


    def test_ponytail_private_package_remains_snapshot_only(self):
        registry = self.load(REGISTRY)
        item = next(p for p in registry["plugins"] if p["plugin_key"] == "ponytail-engineering-optimizer")
        self.assertEqual(item["distribution_status"], "snapshot_only")
        self.assertEqual(item["source_state"], "pending_repository")
        self.assertEqual(item["license_status"], "not_assessed")
        self.assertIsNone(item["source_commit"])
        self.assertIsNone(item["package_artifact"])
        self.assertIn("PRIVATE_PLUGIN_CREATOR_SCOPE_NOT_PUBLICLY_INSTALLABLE", item["blockers"])
        self.assertIn("PACKAGE_LICENSE_NOT_INDEPENDENTLY_ASSESSED", item["blockers"])


    def test_vibe_coding_mentor_remains_snapshot_only_until_source_and_rights_are_cleared(self):
        catalog = self.load(ROOT / "catalog" / "plugins.json")
        registry = self.load(REGISTRY)
        catalog_item = next(p for p in catalog["plugins"] if p["plugin_key"] == "vibe-coding-mentor")
        item = next(p for p in registry["plugins"] if p["plugin_key"] == "vibe-coding-mentor")
        self.assertEqual(item["distribution_status"], "snapshot_only")
        self.assertEqual(item["source_state"], "pending_repository")
        self.assertEqual(item["license_status"], "not_assessed")
        self.assertIsNone(item["source_repository_id"])
        self.assertIsNone(item["source_commit"])
        self.assertIsNone(item["package_artifact"])
        self.assertEqual(item["platform_package_version"], "0.1.0")
        self.assertIn("CANONICAL_SOURCE_REPOSITORY_NOT_IDENTIFIED", item["blockers"])
        self.assertIn("PRIVATE_PLUGIN_CREATOR_SCOPE_NOT_PUBLICLY_INSTALLABLE", item["blockers"])
        self.assertIn("PACKAGE_LICENSE_NOT_INDEPENDENTLY_ASSESSED", item["blockers"])
        self.assertEqual(catalog_item["platform_scope"], "USER")
        self.assertEqual(catalog_item["platform_discoverability"], "PRIVATE")

if __name__=="__main__":
    unittest.main()
