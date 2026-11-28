import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from pre_rpeds_federation_sync import canonical_json, extract_event, hso_signature, post_oidc, request_oidc_token


class PreRpedsFederationSyncTests(unittest.TestCase):
    def build_event(self):
        return {
            "event_id": "pre-release-event-0001",
            "event_type": "PRE_SHARED_DNA_RELEASE",
            "canonical_identity": "pre-rpeds-shared-roadmap-dna",
            "version": "0.1.6",
            "release_id": "pluginrel_6b0961f9dca08191a8af34dbb2e02881",
            "source_locator": "https://example.invalid/pre/0.1.6",
            "artifact_sha256": "a" * 64,
            "contract_version": "1.0.0",
            "compatibility_range": ">=0.1.0 <1.0.0",
            "release_channel": "stable",
            "capability_classes": ["SHARED_DNA"],
            "target_host_ids": ["asfree-rpeds"],
            "is_breaking": False,
            "issuer": {"identity": "pre-publisher", "key_id": "test", "signature": "s" * 24},
            "issued_at": "2026-11-27T00:00:00Z",
            "idempotency_key": "pre-idempotency-key-0001",
        }

    def test_extract_repository_dispatch_event(self):
        event = self.build_event()
        self.assertEqual(extract_event({"client_payload": {"release_event": event}}), event)

    def test_extract_workflow_dispatch_json(self):
        event = self.build_event()
        self.assertEqual(extract_event({"inputs": {"release_event_json": json.dumps(event)}}), event)

    def test_release_event_requires_valid_target_host_ids(self):
        event = self.build_event()
        event.pop("target_host_ids")
        with self.assertRaises(ValueError):
            extract_event({"event_type": "PRE_SHARED_DNA_RELEASE", **event})

    def test_signed_body_is_deterministic(self):
        body = canonical_json({"event_id": "evt-1", "version": "0.1.6"})
        self.assertEqual(hso_signature("test-secret", body), hso_signature("test-secret", body))
        self.assertTrue(hso_signature("test-secret", body).startswith("sha256="))


class FakeResponse:
    def __init__(self, payload: bytes, status: int = 200):
        self.payload = payload
        self.status = status
    def read(self):
        return self.payload
    def __enter__(self):
        return self
    def __exit__(self, *_args):
        return False


class PreRpedsOidcTests(unittest.TestCase):
    def test_oidc_request_uses_exact_federation_audience(self):
        observed = {}
        def opener(request, timeout):
            observed["url"] = request.full_url
            observed["authorization"] = request.get_header("Authorization")
            observed["timeout"] = timeout
            return FakeResponse(b'{"value":"header.payload.signature"}')
        token = request_oidc_token(
            "https://example.supabase.co/functions/v1/pre-core-federation",
            {"ACTIONS_ID_TOKEN_REQUEST_URL": "https://token.actions.githubusercontent.com/?run=789",
             "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "runner-ephemeral-capability"},
            opener=opener,
        )
        from urllib.parse import parse_qs, urlsplit
        query = parse_qs(urlsplit(observed["url"]).query)
        self.assertEqual(token, "header.payload.signature")
        self.assertEqual(query["audience"], ["https://example.supabase.co/functions/v1/pre-core-federation"])
        self.assertEqual(observed["authorization"], "Bearer runner-ephemeral-capability")
        self.assertEqual(observed["timeout"], 15)

    def test_oidc_request_rejects_untrusted_request_endpoint(self):
        with self.assertRaises(RuntimeError):
            request_oidc_token(
                "https://example.supabase.co/functions/v1/pre-core-federation",
                {
                    "ACTIONS_ID_TOKEN_REQUEST_URL": "https://attacker.example/steal",
                    "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "runner-ephemeral-capability",
                },
                opener=lambda *_args, **_kwargs: self.fail("untrusted endpoint must not be called"),
            )

    def test_reconcile_post_uses_bearer_oidc_without_hmac_header(self):
        observed = {}
        def opener(request, timeout):
            observed["headers"] = {key.lower(): value for key, value in request.header_items()}
            return FakeResponse(b'{"accepted":true}', status=200)
        status, body = post_oidc(
            "https://example.supabase.co/functions/v1/pre-core-federation/reconcile",
            "header.payload.signature", {"trigger_kind": "test"}, opener=opener,
        )
        self.assertEqual(status, 200)
        self.assertEqual(body, '{"accepted":true}')
        self.assertEqual(observed["headers"]["authorization"], "Bearer header.payload.signature")
        self.assertNotIn("x-hso-signature", observed["headers"])


if __name__ == "__main__":
    unittest.main()
