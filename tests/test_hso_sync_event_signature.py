from __future__ import annotations

import hashlib
import hmac

import pytest

from tools.emit_hso_sync_event import event_signature, event_signing_payload


def test_hso_signature_binds_timestamp_delivery_id_and_exact_body() -> None:
    secret = "test-webhook-signing-secret-with-at-least-32-bytes"
    timestamp = "1795632000"
    delivery_id = "run-42-attempt-1-push-abcd1234"
    body = b'{"action":"opened","number":7}'
    preimage = timestamp.encode() + b"." + delivery_id.encode() + b"." + body

    assert event_signing_payload(timestamp, delivery_id, body) == preimage
    expected = hmac.new(secret.encode(), preimage, hashlib.sha256).hexdigest()
    signature = event_signature(secret, timestamp, delivery_id, body)
    assert signature == expected
    assert event_signature(secret, str(int(timestamp) + 1), delivery_id, body) != signature
    assert event_signature(secret, timestamp, delivery_id + "-changed", body) != signature
    assert event_signature(secret, timestamp, delivery_id, body + b" ") != signature


def test_hso_signing_context_and_key_strength_are_validated() -> None:
    with pytest.raises(ValueError):
        event_signing_payload("not-a-timestamp", "delivery-1", b"{}")
    with pytest.raises(ValueError):
        event_signing_payload("1795632000", "", b"{}")
    with pytest.raises(ValueError):
        event_signing_payload("1795632000", "delivery id", b"{}")
    with pytest.raises(ValueError):
        event_signature("short", "1795632000", "delivery-1", b"{}")
