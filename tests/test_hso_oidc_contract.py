import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HsoOidcContractTests(unittest.TestCase):
    def test_workflow_uses_oidc_and_trusted_main_checkout(self):
        workflow = (ROOT / ".github/workflows/hso-mission-control-sync.yml").read_text()
        self.assertIn("id-token: write", workflow)
        self.assertIn("pull_request_target:", workflow)
        self.assertIn("branches: [main]", workflow)
        self.assertIn("ref: main", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("tools/emit_hso_oidc_event.py event", workflow)
        self.assertIn("tools/emit_hso_oidc_event.py reconcile", workflow)
        self.assertNotIn("secrets.HSO_SYNC_TOKEN", workflow)
        self.assertNotIn("vars.HSO_GITHUB_WEBHOOK_URL", workflow)
        self.assertNotIn("\n  pull_request:\n", workflow)

    def test_edge_functions_pin_the_exact_repository_workflow_and_audience(self):
        shared = (ROOT / "supabase/functions/_shared/github_oidc.ts").read_text()
        webhook = (ROOT / "supabase/functions/hso-github-webhook/index.ts").read_text()
        reconcile = (ROOT / "supabase/functions/hso-reconcile/index.ts").read_text()
        workflow_ref = "hsaidno-cpu/Hypersystem-Orchestrator/.github/workflows/hso-mission-control-sync.yml@refs/heads/main"
        self.assertIn("https://token.actions.githubusercontent.com", shared)
        self.assertIn('header?.alg !== "RS256"', shared)
        self.assertIn("repositoryId", shared)
        self.assertIn(workflow_ref, webhook)
        self.assertIn(workflow_ref, reconcile)
        self.assertIn("/functions/v1/hso-github-webhook", webhook)
        self.assertIn("/functions/v1/hso-reconcile", reconcile)
        self.assertIn('allowedEvents: ["push", "pull_request_target", "workflow_run"]', webhook)
        self.assertIn('allowedEvents: ["schedule", "workflow_dispatch"]', reconcile)

    def test_vault_secret_is_resolved_server_side_only(self):
        webhook = (ROOT / "supabase/functions/hso-github-webhook/index.ts").read_text()
        reconcile = (ROOT / "supabase/functions/hso-reconcile/index.ts").read_text()
        self.assertIn('rpc("pre_federation_get_secret"', webhook)
        self.assertIn('rpc("pre_federation_get_secret"', reconcile)
        notion = (ROOT / "supabase/functions/hso-notion-webhook/index.ts").read_text()
        decision = (ROOT / "supabase/functions/hso-decision-engine/index.ts").read_text()
        self.assertIn('resolveVaultSecret(supabase, "HSO_SYNC_TOKEN")', webhook)
        self.assertIn('resolveVaultSecret(db, "HSO_SYNC_TOKEN")', reconcile)
        self.assertIn('resolveVaultSecret(supabase, "HSO_SYNC_TOKEN")', notion)
        self.assertIn('resolveVaultSecret(db, "HSO_SYNC_TOKEN")', decision)


if __name__ == "__main__":
    unittest.main()
