from __future__ import annotations

import hashlib
import hmac
import unittest

from tools.emit_hso_sync_event import event_signature, event_signing_payload


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


if __name__ == "__main__":
    unittest.main()
