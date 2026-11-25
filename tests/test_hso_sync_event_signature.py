from __future__ import annotations

import hashlib
import hmac

from tools.emit_hso_sync_event import event_signature, event_signing_payload


def test_hso_signature_binds_timestamp_delivery_and_exact_body() -> None:
    secret = "test-only-secret"
    timestamp = "1795632000"
    delivery_id = "run-42-attempt-1-push-abcd1234"
    body = b'{"action":"opened","number":7}'

    payload = event_signing_payload(timestamp, delivery_id, body)
    expected_payload = timestamp.encode() + b"." + delivery_id.encode() + b"." + body
    assert payload == expected_payload

    expected_signature = hmac.new(
        secret.encode(),
        expected_payload,
        hashlib.sha256,
    ).hexdigest()
    signature = event_signature(secret, timestamp, delivery_id, body)
    assert signature == expected_signature

    assert event_signature(secret, str(int(timestamp) + 1), delivery_id, body) != signature
    assert event_signature(secret, timestamp, delivery_id + "-replay", body) != signature
    assert event_signature(secret, timestamp, delivery_id, body + b" ") != signature


def test_hso_signature_rejects_empty_or_invalid_context() -> None:
    try:
        event_signing_payload("not-a-timestamp", "delivery-1", b"{}")
    except ValueError:
        pass
    else:
        raise AssertionError("invalid timestamp must be rejected")

    try:
        event_signing_payload("1795632000", "", b"{}")
    except ValueError:
        pass
    else:
        raise AssertionError("empty delivery ID must be rejected")
