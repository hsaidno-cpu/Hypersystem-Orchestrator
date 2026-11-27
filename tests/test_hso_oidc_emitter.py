import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from emit_hso_oidc_event import event_delivery_id, post_json, request_oidc_token


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


class HsoOidcEmitterTests(unittest.TestCase):
    def test_oidc_exchange_requests_exact_audience(self):
        observed = {}

        def opener(request, timeout):
            observed["url"] = request.full_url
            observed["authorization"] = request.get_header("Authorization")
            observed["timeout"] = timeout
            return FakeResponse(b'{"value":"header.payload.signature"}')

        token = request_oidc_token(
            "https://example.supabase.co/functions/v1/hso-github-webhook",
            {
                "ACTIONS_ID_TOKEN_REQUEST_URL": "https://token.actions.githubusercontent.com/?run=123",
                "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "runner-capability-token",
            },
            opener=opener,
        )
        query = parse_qs(urlsplit(observed["url"]).query)
        self.assertEqual(token, "header.payload.signature")
        self.assertEqual(query["audience"], ["https://example.supabase.co/functions/v1/hso-github-webhook"])
        self.assertEqual(query["run"], ["123"])
        self.assertEqual(observed["authorization"], "Bearer runner-capability-token")
        self.assertEqual(observed["timeout"], 15)

    def test_payload_post_uses_bearer_oidc_not_shared_hmac_secret(self):
        observed = {}

        def opener(request, timeout):
            observed["headers"] = {key.lower(): value for key, value in request.header_items()}
            observed["body"] = request.data
            observed["method"] = request.get_method()
            return FakeResponse(b'{"accepted":true}', status=202)

        status, body = post_json(
            "https://example.supabase.co/functions/v1/hso-github-webhook",
            "short-lived-oidc-jwt",
            b'{"repository":{"full_name":"hsaidno-cpu/Hypersystem-Orchestrator"}}',
            event_type="push",
            delivery_id="github-actions-123-push",
            opener=opener,
        )
        self.assertEqual(status, 202)
        self.assertEqual(body, '{"accepted":true}')
        self.assertEqual(observed["method"], "POST")
        self.assertEqual(observed["headers"]["authorization"], "Bearer short-lived-oidc-jwt")
        self.assertEqual(observed["headers"]["x-hso-event"], "push")
        self.assertEqual(observed["headers"]["x-hso-delivery"], "github-actions-123-push")
        self.assertNotIn("x-hso-signature", observed["headers"])
        self.assertNotIn("hso_sync_token", observed["headers"])
        self.assertIn(b'"repository"', observed["body"])

    def test_delivery_id_is_stable_for_retry_of_same_run(self):
        first = event_delivery_id("123456", "workflow_run")
        retried = event_delivery_id("123456", "workflow_run")
        another_run = event_delivery_id("123457", "workflow_run")
        self.assertEqual(first, retried)
        self.assertNotEqual(first, another_run)

    def test_oidc_request_fails_closed_without_runner_capability(self):
        with self.assertRaisesRegex(RuntimeError, "OIDC request context is unavailable"):
            request_oidc_token("https://example.invalid/audience", {})


if __name__ == "__main__":
    unittest.main()
