from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

from tools import emit_hso_sync_event


class _Response:
    status = 202

    def read(self) -> bytes:
        return b'{"status":"succeeded"}'

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class HsoScheduledReconciliationEmitterTests(unittest.TestCase):
    def test_scheduled_mode_posts_to_reconcile_with_dedicated_sync_token(self) -> None:
        captured = {}

        def fake_urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return _Response()

        env = {
            "HSO_GITHUB_WEBHOOK_URL": "https://project.supabase.co/functions/v1/hso-github-webhook",
            "HSO_SYNC_TOKEN": "separate-sync-token-value",
            "GITHUB_RUN_ID": "123456",
        }
        with patch.dict(os.environ, env, clear=True), patch.object(
            sys, "argv", ["emit_hso_sync_event.py", "--mode", "reconcile"]
        ), patch.object(emit_hso_sync_event.urllib.request, "urlopen", side_effect=fake_urlopen):
            self.assertEqual(emit_hso_sync_event.main(), 0)

        request = captured["request"]
        self.assertEqual(
            request.full_url,
            "https://project.supabase.co/functions/v1/hso-reconcile",
        )
        self.assertEqual(request.get_header("X-hso-sync-token"), "separate-sync-token-value")
        self.assertIsNone(request.get_header("X-hso-signature"))
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(request.data, b'{"trigger_kind":"scheduled"}')
        self.assertEqual(captured["timeout"], 55)

    def test_scheduled_mode_fails_closed_without_sync_token(self) -> None:
        env = {
            "HSO_GITHUB_WEBHOOK_URL": "https://project.supabase.co/functions/v1/hso-github-webhook",
        }
        with patch.dict(os.environ, env, clear=True), patch.object(
            sys, "argv", ["emit_hso_sync_event.py", "--mode", "reconcile"]
        ), patch.object(emit_hso_sync_event.urllib.request, "urlopen") as urlopen:
            self.assertEqual(emit_hso_sync_event.main(), 2)
            urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
