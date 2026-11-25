from __future__ import annotations

import hashlib
import hmac
import unittest

from tools.emit_hso_sync_event import (
    build_reconciliation_request,
    event_signature,
    event_signing_payload,
)


class HsoSyncEventSignatureTests(unittest.TestCase):
    def test_signature_binds_timestamp_delivery_event_type_and_exact_body(self) -> None:
        secret = "test-webhook-signing-secret-with-at-least-32-bytes"
        timestamp = "1795632000"
        delivery_id = "run-42-attempt-1-push-abcd1234"
        event_type = "pull_request"
        body = b'{"action":"opened","number":7}'
        preimage = (
            timestamp.encode() + b"." + delivery_id.encode() +
            b"." + event_type.encode() + b"." + body
        )

        self.assertEqual(
            event_signing_payload(timestamp, delivery_id, event_type, body),
            preimage,
        )
        expected = hmac.new(secret.encode(), preimage, hashlib.sha256).hexdigest()
        signature = event_signature(secret, timestamp, delivery_id, event_type, body)
        self.assertEqual(signature, expected)
        self.assertNotEqual(
            event_signature(secret, str(int(timestamp) + 1), delivery_id, event_type, body),
            signature,
        )
        self.assertNotEqual(
            event_signature(secret, timestamp, delivery_id + "-changed", event_type, body),
            signature,
        )
        self.assertNotEqual(
            event_signature(secret, timestamp, delivery_id, "workflow_run", body),
            signature,
        )
        self.assertNotEqual(
            event_signature(secret, timestamp, delivery_id, event_type, body + b" "),
            signature,
        )

    def test_signing_context_and_key_strength_are_validated(self) -> None:
        with self.assertRaises(ValueError):
            event_signing_payload("not-a-timestamp", "delivery-1", "pull_request", b"{}")
        with self.assertRaises(ValueError):
            event_signing_payload("1795632000", "", "pull_request", b"{}")
        with self.assertRaises(ValueError):
            event_signing_payload("1795632000", "delivery-1", "bad event", b"{}")
        with self.assertRaises(ValueError):
            event_signature("short", "1795632000", "delivery-1", "pull_request", b"{}")


    def test_scheduled_reconciliation_uses_dedicated_sync_token_and_endpoint(self) -> None:
        endpoint, body, headers = build_reconciliation_request(
            "https://project.supabase.co/functions/v1/hso-github-webhook",
            "a-dedicated-sync-token",
            "987654321",
        )
        self.assertEqual(
            endpoint,
            "https://project.supabase.co/functions/v1/hso-reconcile",
        )
        self.assertEqual(body, b'{"trigger_kind":"scheduled"}')
        self.assertEqual(headers["X-HSO-Sync-Token"], "a-dedicated-sync-token")
        self.assertEqual(headers["X-HSO-Delivery"], "actions-987654321")
        self.assertEqual(headers["X-HSO-Event"], "scheduled_reconciliation")

    def test_scheduled_reconciliation_rejects_missing_token_or_ambiguous_endpoint(self) -> None:
        with self.assertRaises(ValueError):
            build_reconciliation_request(
                "https://project.supabase.co/functions/v1/hso-github-webhook",
                "",
                "987654321",
            )
        with self.assertRaises(ValueError):
            build_reconciliation_request(
                "https://project.supabase.co/functions/v1/legacy-webhook",
                "a-dedicated-sync-token",
                "987654321",
            )


if __name__ == "__main__":
    unittest.main()
