import unittest

from tools.emit_hso_sync_event import reconcile_url


class HsoReconciliationSenderTests(unittest.TestCase):
    def test_supabase_webhook_url_maps_to_reconcile_endpoint(self):
        self.assertEqual(
            reconcile_url("https://project-ref.supabase.co/functions/v1/hso-github-webhook"),
            "https://project-ref.supabase.co/functions/v1/hso-reconcile",
        )

    def test_rejects_non_supabase_endpoint(self):
        with self.assertRaises(ValueError):
            reconcile_url("https://attacker.invalid/functions/v1/hso-github-webhook")

    def test_sync_workflow_only_runs_from_trusted_main(self):
        from pathlib import Path

        workflow = Path(".github/workflows/hso-mission-control-sync.yml").read_text(encoding="utf-8")
        self.assertIn("if: ${{ github.ref == 'refs/heads/main' }}", workflow)
        self.assertIn("ref: main", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("\n  pull_request:", workflow)
        self.assertNotIn("\nconcurrency:", workflow)
        self.assertNotIn("event-ingestion:", workflow)

    def test_rejects_query_string_and_userinfo(self):
        for value in (
            "https://project-ref.supabase.co/functions/v1/hso-github-webhook?token=secret",
            "https://user:pass@project-ref.supabase.co/functions/v1/hso-github-webhook",
            "https://project-ref.supabase.co/functions/v1/hso-reconcile",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                reconcile_url(value)


if __name__ == "__main__":
    unittest.main()
