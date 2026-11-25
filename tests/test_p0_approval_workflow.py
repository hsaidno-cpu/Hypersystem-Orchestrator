"""Tests for the P0 Remote MCP single-call scoped approval workflow."""
from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import issue_p0_skill_approval as issue
from tools import prepare_p0_skill_workflow as prepare

SECRET = "unit-test-approval-key-with-sufficient-entropy-12345"
ACTOR = "hsaidno-cpu"
RUN = "123456789"
SERVER_URL = "https://gateway.example.com/mcp"
TOKEN_URL = "https://tenant.example.com/oauth/token"
SOURCE = {
    "source_commit": "c469af7977c9bf6dcb3f5ab7b085a6de20d87004",
    "plugin_version": "1.3.0",
    "skill_sha256": "a" * 64,
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sign(unsigned, secret=SECRET):
    return hmac.new(secret.encode(), canonical(unsigned).encode(), hashlib.sha256).hexdigest()


class P0RemoteMCPApprovalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.approval = self.root / "approval.json"
        self.output = self.root / "workflow.json"
        self.template = self.root / "template.json"
        self.environment_approval = self.root / "environment-approval.json"
        self.environment_approval.write_text(json.dumps({
            "schema_version": "1.0.0",
            "environment": "hso-p0-remote-mcp-live",
            "workflow_run_id": RUN,
            "workflow_run_attempt": "1",
            "workflow_actor": ACTOR,
            "workflow_actor_id": 100,
            "reviewer_login": "independent-security-reviewer",
            "reviewer_id": 424242,
            "state": "approved",
            "approval_source": "github_actions_workflow_run_approvals_api",
            "observed_at": "2026-11-24T04:00:00Z",
        }), encoding="utf-8")
        source_template = json.loads(
            (Path(__file__).resolve().parents[1] / "examples" / "hso-p0-skill-invocation-request.json").read_text()
        )
        self.template.write_text(json.dumps(source_template), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def env(self, **extra):
        values = {
            "HSO_APPROVAL_HMAC_KEY": SECRET,
            "GITHUB_ACTOR": ACTOR,
            "GITHUB_ACTOR_ID": "100",
            "GITHUB_RUN_ID": RUN,
            "GITHUB_RUN_ATTEMPT": "1",
            "HSO_P0_ALLOWED_REVIEWER_LOGINS": "independent-security-reviewer",
            "MCP_SERVER_URL": SERVER_URL,
            "MCP_OIDC_AUDIENCE": SERVER_URL,
        }
        values.update(extra)
        return values

    def issue_receipt(self, extra_env=None):
        with patch.dict(os.environ, self.env(**(extra_env or {})), clear=True), \
             patch.object(issue, "TEMPLATE", self.template), \
             patch.object(issue.adapter, "inspect_local_skill_source", return_value=SOURCE), \
             patch.object(sys, "argv", ["issue", "--environment-approval", str(self.environment_approval),
                                        "--output", str(self.approval)]):
            issue.main()
        return json.loads(self.approval.read_text(encoding="utf-8"))

    def prepare_workflow(self, approval, extra_env=None):
        self.approval.write_text(json.dumps(approval), encoding="utf-8")
        with patch.dict(os.environ, self.env(**(extra_env or {})), clear=True), \
             patch.object(prepare, "TEMPLATE", self.template), \
             patch.object(prepare.adapter, "inspect_local_skill_source", return_value=SOURCE), \
             patch.object(sys, "argv", [
                 "prepare", "--approval-receipt", str(self.approval),
                 "--environment-approval", str(self.environment_approval),
                 "--output", str(self.output)
             ]):
            prepare.main()
        return json.loads(self.output.read_text(encoding="utf-8"))

    def test_issues_five_minute_approval_bound_to_exact_host_server_tool_args_and_source(self):
        receipt = self.issue_receipt()
        unsigned = {key: value for key, value in receipt.items() if key != "signature"}
        self.assertTrue(hmac.compare_digest(receipt["signature"], sign(unsigned)))
        start = datetime.datetime.fromisoformat(receipt["issued_at"].replace("Z", "+00:00"))
        end = datetime.datetime.fromisoformat(receipt["expires_at"].replace("Z", "+00:00"))
        self.assertAlmostEqual((end - start).total_seconds(), 300, delta=2)
        self.assertEqual(receipt["host"], "openai-responses-api")
        self.assertEqual(receipt["approver"], "independent-security-reviewer")
        self.assertEqual(receipt["workflow_actor"], ACTOR)
        self.assertEqual(receipt["workflow_actor_id"], 100)
        self.assertEqual(receipt["environment_reviewer_id"], 424242)
        self.assertEqual(receipt["mcp_server_label"], "skill_analyzer_internal")
        self.assertEqual(receipt["mcp_tool_name"], "invoke_skill_analyzer")
        self.assertEqual(receipt["plugin_source_commit"], SOURCE["source_commit"])
        self.assertEqual(receipt["skill_sha256"], SOURCE["skill_sha256"])
        self.assertEqual(receipt["mcp_server_url_sha256"], hashlib.sha256(SERVER_URL.encode()).hexdigest())
        self.assertEqual(self.approval.stat().st_mode & 0o777, 0o600)

    def test_preparation_binds_exact_package_and_source_digest(self):
        receipt = self.issue_receipt()
        workflow = self.prepare_workflow(receipt)
        package = workflow["work_packages"][0]
        self.assertEqual(workflow["requested_by"], ACTOR)
        self.assertEqual(package["idempotency_key"], "hso-p0-skill-analyzer-" + RUN)
        self.assertEqual(package["input"]["skill_sha256"], SOURCE["skill_sha256"])
        self.assertEqual(package["approval_receipt"]["nonce"], receipt["nonce"])
        self.assertEqual(package["approval_receipt"]["mcp_tool_name"], "invoke_skill_analyzer")

    def test_issue_rejects_wrong_actor_and_workflow_rerun(self):
        with self.assertRaises(SystemExit):
            self.issue_receipt({"GITHUB_ACTOR": "other"})
        with self.assertRaises(SystemExit):
            self.issue_receipt({"GITHUB_RUN_ATTEMPT": "2"})

    def test_preparation_rejects_server_scope_change(self):
        receipt = self.issue_receipt()
        with self.assertRaisesRegex(SystemExit, "mcp_server_url_sha256"):
            self.prepare_workflow(receipt, {"MCP_SERVER_URL": "https://other.example.com/mcp",
                                            "MCP_OIDC_AUDIENCE": "https://other.example.com/mcp"})

    def test_preparation_rejects_expired_receipt_even_with_valid_signature(self):
        receipt = self.issue_receipt()
        unsigned = {key: value for key, value in receipt.items() if key != "signature"}
        unsigned["expires_at"] = "2000-01-01T00:00:00Z"
        receipt = {**unsigned, "signature": sign(unsigned)}
        with self.assertRaisesRegex(SystemExit, "expired"):
            self.prepare_workflow(receipt)

    def test_preparation_rejects_tampered_receipt(self):
        receipt = self.issue_receipt()
        receipt["tool_arguments_sha256"] = "0" * 64
        with self.assertRaisesRegex(SystemExit, "tool_arguments_sha256"):
            self.prepare_workflow(receipt)

    def test_preparation_rejects_invalid_signature_and_existing_output(self):
        receipt = self.issue_receipt()
        receipt["signature"] = "0" * 64
        with self.assertRaisesRegex(SystemExit, "signature is invalid"):
            self.prepare_workflow(receipt)
        self.approval.unlink()
        receipt = self.issue_receipt()
        self.output.write_text("protected", encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "refusing overwrite"):
            self.prepare_workflow(receipt)


if __name__ == "__main__":
    unittest.main()
