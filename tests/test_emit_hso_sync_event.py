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
