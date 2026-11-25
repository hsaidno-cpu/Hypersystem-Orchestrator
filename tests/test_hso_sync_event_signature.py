from __future__ import annotations

import hashlib
import hmac
import unittest

from tools.emit_hso_sync_event import event_signature, event_signing_payload


class HsoSyncEventSignatureTests(unittest.TestCase):
    def test_signature_binds_timestamp_delivery_id_and_exact_body(self) -> None:
        secret = "test-webhook-signing-secret-with-at-least-32-bytes"
        timestamp = "1795632000"
        delivery_id = "run-42-attempt-1-push-abcd1234"
        body = b'{"action":"opened","number":7}'
        preimage = timestamp.encode() + b"." + delivery_id.encode() + b"." + body

        self.assertEqual(event_signing_payload(timestamp, delivery_id, body), preimage)
        expected = hmac.new(secret.encode(), preimage, hashlib.sha256).hexdigest()
        signature = event_signature(secret, timestamp, delivery_id, body)
        self.assertEqual(signature, expected)
        self.assertNotEqual(event_signature(secret, str(int(timestamp) + 1), delivery_id, body), signature)
        self.assertNotEqual(event_signature(secret, timestamp, delivery_id + "-changed", body), signature)
        self.assertNotEqual(event_signature(secret, timestamp, delivery_id, body + b" "), signature)

    def test_signing_context_and_key_strength_are_validated(self) -> None:
        with self.assertRaises(ValueError):
            event_signing_payload("not-a-timestamp", "delivery-1", b"{}")
        with self.assertRaises(ValueError):
            event_signing_payload("1795632000", "", b"{}")
        with self.assertRaises(ValueError):
            event_signing_payload("1795632000", "delivery id", b"{}")
        with self.assertRaises(ValueError):
            event_signature("short", "1795632000", "delivery-1", b"{}")


if __name__ == "__main__":
    unittest.main()
