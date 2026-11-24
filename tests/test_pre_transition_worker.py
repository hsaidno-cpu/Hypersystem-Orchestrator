import base64
import json
import unittest
from pathlib import Path
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from tools.pre_policy_engine import (
    NonceStore, canonical_json, evidence_attestation_payload, load_policy,
)
from tools.pre_transition_worker import (
    NotionAPI, NotionWorkerError, process_page, rich_text_chunks, rich_text_value,
    select_value,
)

POLICY = load_policy()
EVIDENCE_PRIVATE = Ed25519PrivateKey.from_private_bytes(bytes.fromhex("11" * 32))
EVIDENCE_PUBLIC = base64.b64encode(
    EVIDENCE_PRIVATE.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
).decode("ascii")


def text_prop(value):
    return {"rich_text": rich_text_chunks(value)}


def select_prop(value):
    return {"select": {"name": value}}


def sign(payload):
    return base64.b64encode(
        EVIDENCE_PRIVATE.sign(canonical_json(payload).encode("utf-8"))
    ).decode("ascii")


def evidence():
    item = {
        "schema_version": "1.0.0",
        "evidence_id": "EV-INTAKE-001",
        "evidence_type": "INTAKE_BRIEF",
        "project_id": "HSO",
        "scope_id": "HSO:WI-001:baseline-v1",
        "state": "PASS",
        "freshness": "FRESH",
        "verified": True,
        "identity_verified": True,
        "verified_by": "evaluator:independent",
        "verifier_role": "Evaluator Team",
        "verified_at": "2026-11-24T03:00:00Z",
        "issuer": "hso-evidence-issuer",
        "source_locator": "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/blob/main/README.md",
        "sha256": "a" * 64,
    }
    item["signature"] = sign(evidence_attestation_payload(item))
    return [item]


def queue_page(*, evidence_raw=None, page_id="page-001"):
    props = {
        "Idempotency Key": text_prop("PRE-REQ-001"),
        "Request State": select_prop("PENDING"),
        "Project ID": text_prop("HSO"),
        "Scope ID": text_prop("HSO:WI-001:baseline-v1"),
        "From Stage": select_prop("R0 Intake"),
        "Requested Stage": select_prop("R1 Strategy & Baseline"),
        "Requested By Actor ID": text_prop("agent:hso"),
        "Evidence Envelope JSON": text_prop(
            json.dumps(evidence(), separators=(",", ":")) if evidence_raw is None else evidence_raw
        ),
        "Approval Receipt JSON": text_prop("[]"),
        "Source Commit": text_prop("a" * 40),
        "Source Event": {"url": "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/commit/" + "a" * 40},
        "Correlation ID": text_prop("corr-001"),
        "Work Item": {"relation": [{"id": "work-item-001"}]},
    }
    return {"id": page_id, "properties": props}


class MemoryNotion:
    def __init__(self, page):
        self.page = page
        self.updated = []

    def update_page(self, page_id, properties):
        self.updated.append((page_id, properties))
        self.page["properties"].update(properties)
        return {"id": page_id}

    def get_page(self, page_id):
        return self.page


class PRETransitionWorkerTests(unittest.TestCase):
    def test_valid_queue_item_is_evaluated_and_read_back_without_stage_mutation(self):
        page = queue_page()
        client = MemoryNotion(page)
        with tempfile.TemporaryDirectory() as folder:
            result = process_page(
                page, client, POLICY, None,
                NonceStore(Path(folder) / "nonces.sqlite"),
                evidence_public_key=EVIDENCE_PUBLIC,
            )
        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(result["gate_state"], "PASS")
        self.assertTrue(result["read_back_verified"])
        self.assertFalse(result["stage_mutation_performed"])
        self.assertEqual(len(client.updated), 2)
        self.assertEqual(select_value(client.updated[0][1]["Request State"]), "EVALUATING")
        self.assertEqual(select_value(page["properties"]["Request State"]), "POLICY_PASSED")
        self.assertEqual(select_value(page["properties"]["Gate Decision"]), "ALLOW")
        self.assertEqual(rich_text_value(page["properties"]["Evaluation Digest"]), result["evaluation_digest"])
        self.assertEqual(page["properties"]["Work Item"]["relation"][0]["id"], "work-item-001")
        self.assertNotIn("PRE Stage", client.updated[0][1])

    def test_unsigned_or_malformed_evidence_json_is_recorded_as_deny_and_read_back(self):
        page = queue_page(evidence_raw="{not-json")
        client = MemoryNotion(page)
        with tempfile.TemporaryDirectory() as folder:
            result = process_page(
                page, client, POLICY, None,
                NonceStore(Path(folder) / "nonces.sqlite"),
                evidence_public_key=EVIDENCE_PUBLIC,
            )
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("EVIDENCE_ENVELOPE_JSON_INVALID", rich_text_value(page["properties"]["Block Reasons"]))
        self.assertEqual(select_value(page["properties"]["Request State"]), "REJECTED")
        self.assertTrue(result["read_back_verified"])

    def test_missing_actor_identity_is_denied_by_policy_engine(self):
        page = queue_page()
        page["properties"]["Requested By Actor ID"] = text_prop("")
        client = MemoryNotion(page)
        with tempfile.TemporaryDirectory() as folder:
            result = process_page(
                page, client, POLICY, None,
                NonceStore(Path(folder) / "nonces.sqlite"),
                evidence_public_key=EVIDENCE_PUBLIC,
            )
        self.assertEqual(result["decision"], "DENY")
        self.assertIn("REQUEST_FIELDS_EMPTY", rich_text_value(page["properties"]["Block Reasons"]))

    def test_missing_evidence_public_key_holds_request(self):
        page = queue_page()
        client = MemoryNotion(page)
        with tempfile.TemporaryDirectory() as folder:
            result = process_page(
                page, client, POLICY, None,
                NonceStore(Path(folder) / "nonces.sqlite"),
            )
        self.assertEqual(result["decision"], "HOLD")
        self.assertIn("EVIDENCE_VERIFYING_KEY_NOT_CONFIGURED", rich_text_value(page["properties"]["Block Reasons"]))

    def test_read_back_mismatch_fails_closed(self):
        page = queue_page()
        class CorruptReadBack(MemoryNotion):
            def get_page(self, page_id):
                copied = {"id": page_id, "properties": dict(self.page["properties"])}
                copied["properties"]["Evaluation Digest"] = text_prop("0" * 64)
                return copied
        client = CorruptReadBack(page)
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(NotionWorkerError, "READ_BACK_MISMATCH"):
                process_page(
                    page, client, POLICY, None,
                    NonceStore(Path(folder) / "nonces.sqlite"),
                    evidence_public_key=EVIDENCE_PUBLIC,
                )

    def test_pending_query_follows_notion_cursor(self):
        responses = [
            {"results": [{"id": "first"}], "has_more": True, "next_cursor": "next-page"},
            {"results": [{"id": "second"}], "has_more": False, "next_cursor": None},
        ]
        requests = []
        class Response:
            def __init__(self, payload):
                self.payload = payload
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps(self.payload).encode()
        def opener(request, timeout=25):
            requests.append(json.loads(request.data.decode()))
            return Response(responses.pop(0))
        client = NotionAPI("test-token", "data-source-id", opener=opener, sleeper=lambda _: None)
        pages = client.query_pending()
        self.assertEqual([page["id"] for page in pages], ["first", "second"])
        self.assertNotIn("start_cursor", requests[0])
        self.assertEqual(requests[1]["start_cursor"], "next-page")
        self.assertEqual(len(requests[0]["filter"]["or"]), 2)
        self.assertEqual(requests[0]["filter"]["or"][0]["select"]["equals"], "PENDING")
        self.assertEqual(requests[0]["filter"]["or"][1]["select"]["equals"], "EVALUATING")

    def test_page_without_id_is_rejected_before_mutation(self):
        page = queue_page()
        page.pop("id")
        client = MemoryNotion(page)
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(NotionWorkerError, "NO_PAGE_ID"):
                process_page(
                    page, client, POLICY, None,
                    NonceStore(Path(folder) / "nonces.sqlite"),
                    evidence_public_key=EVIDENCE_PUBLIC,
                )
        self.assertEqual(client.updated, [])


if __name__ == "__main__":
    unittest.main()
