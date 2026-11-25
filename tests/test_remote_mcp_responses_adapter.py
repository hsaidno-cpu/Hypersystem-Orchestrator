"""Contract and safety tests for the single OpenAI Responses API / Remote MCP P0 adapter."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import remote_mcp_responses_adapter as adapter

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "examples" / "hso-p0-skill-invocation-request.json"
SERVER_URL = "https://gateway.example.com/mcp"
TOKEN_URL = "https://tenant.example.com/oauth/token"
SKILL_HASH = "a" * 64


def gateway_result():
    return {
        "request_id": "gateway-request-001",
        "command": "analyze",
        "route": {
            "id": "analyze",
            "description": "Synthetic analysis route",
            "primary_skills": ["skill-analyzer"],
            "supporting_skills": ["analyzer"],
            "engines": ["knowledge-method-intelligence"],
            "conditional_capabilities": [],
            "default_mode": "adaptive",
        },
        "loaded_skills": ["skill-analyzer", "analyzer", "negative-collector", "positive-converter"],
        "provider": "api.openai.com",
        "model": "gpt-gateway-model",
        "execution_status": "MODEL_RESPONSE_RECEIVED",
        "tool_execution_status": "NOT_CONFIGURED",
        "usage": {"input_tokens": 100, "output_tokens": 500},
        "result": "Synthetic root-cause, risk and mitigation analysis result.",
    }


class RemoteMCPAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.payload = json.loads(TEMPLATE.read_text(encoding="utf-8"))["work_packages"][0]["input"]
        self.payload["skill_sha256"] = SKILL_HASH
        self.arguments = adapter._expected_arguments(self.payload)
        self.approval = {
            "host": adapter.HOST_ID,
            "mcp_server_label": adapter.SERVER_LABEL,
            "mcp_tool_name": adapter.TOOL_NAME,
            "mcp_server_url_sha256": hashlib.sha256(SERVER_URL.encode()).hexdigest(),
            "tool_arguments_sha256": adapter.sha256_json(self.arguments),
            "plugin_source_commit": adapter.SOURCE_PIN,
            "skill_sha256": SKILL_HASH,
            "approver": "hsaidno-cpu",
            "nonce": "single-use-test-nonce",
        }
        self.context = {
            "case_id": "HSO-P0-SKILL-ANALYZER-001",
            "idempotency_key": "p0-test-invocation",
            "approval_receipt": self.approval,
            "approval_verified": True,
        }
        self.env = {
            "OPENAI_API_KEY": "test-openai-key-not-real",
            "MCP_SERVER_URL": SERVER_URL,
            "MCP_OIDC_TOKEN_URL": TOKEN_URL,
            "MCP_OIDC_CLIENT_ID": "test-client",
            "MCP_OIDC_CLIENT_SECRET": "test-client-secret",
            "MCP_OIDC_AUDIENCE": SERVER_URL,
        }

    def tearDown(self):
        self.temp.cleanup()

    def tool_list_item(self, names=None):
        names = names or [adapter.TOOL_NAME]
        return {
            "type": "mcp_list_tools",
            "server_label": adapter.SERVER_LABEL,
            "tools": [{"name": name, "description": "analysis tool"} for name in names],
        }

    def approval_item(self, arguments=None):
        return {
            "type": "mcp_approval_request",
            "id": "mcpr-approval-001",
            "server_label": adapter.SERVER_LABEL,
            "name": adapter.TOOL_NAME,
            "arguments": json.dumps(arguments or self.arguments),
        }

    def initial_response(self, arguments=None, names=None):
        return {
            "id": "resp-initial-001",
            "status": "completed",
            "output": [self.tool_list_item(names), self.approval_item(arguments)],
            "usage": {"input_tokens": 120, "output_tokens": 80},
        }

    def final_response(self, *, output=None, error=None):
        return {
            "id": "resp-final-001",
            "status": "completed",
            "output": [{
                "type": "mcp_call",
                "id": "mcp-call-001",
                "server_label": adapter.SERVER_LABEL,
                "name": adapter.TOOL_NAME,
                "approval_request_id": "mcpr-approval-001",
                "arguments": json.dumps(self.arguments),
                "error": error,
                "output": json.dumps(output or gateway_result()),
                "status": "completed",
            }],
            "usage": {"input_tokens": 200, "output_tokens": 600},
        }

    def patch_transport(self, response_sequence):
        return (
            patch.object(adapter, "_check_public_dns"),
            patch.object(adapter, "_obtain_mcp_token", return_value="short-lived-test-token"),
            patch.object(
                adapter, "_discover_remote_tools",
                return_value=([{"name": adapter.TOOL_NAME}], "mcp-session-test", adapter.MCP_PROTOCOL_VERSION),
            ),
            patch.object(adapter, "_responses_post", side_effect=response_sequence),
            patch.object(adapter, "inspect_local_skill_source", return_value={
                "source_commit": adapter.SOURCE_PIN,
                "plugin_version": adapter.PLUGIN_VERSION,
                "skill_sha256": SKILL_HASH,
            }),
        )

    def test_probe_is_zero_inference_and_requires_the_exact_tool(self):
        with patch.dict(os.environ, self.env, clear=True):
            with patch.object(adapter, "_check_public_dns"), \
                 patch.object(adapter, "_obtain_mcp_token", return_value="short-token"), \
                 patch.object(adapter, "_discover_remote_tools",
                              return_value=([{"name": adapter.TOOL_NAME}], "session-id", adapter.MCP_PROTOCOL_VERSION)), \
                 patch.object(adapter, "_responses_post") as responses:
                result = adapter.probe_remote_mcp_host(self.workspace)
        self.assertEqual(result["status"], "READY_WITH_LIMITATIONS")
        self.assertEqual(result["allowed_tools"], [adapter.TOOL_NAME])
        self.assertFalse(result["billable_inference_performed"])
        self.assertFalse(result["openai_api_authentication_tested"])
        responses.assert_not_called()

    def test_probe_without_credentials_fails_closed_without_network(self):
        with patch.dict(os.environ, {}, clear=True), \
             patch.object(adapter, "_obtain_mcp_token") as token:
            result = adapter.probe_remote_mcp_host(self.workspace)
        self.assertEqual(result["status"], "NOT_CONFIGURED")
        self.assertFalse(result["billable_inference_performed"])
        token.assert_not_called()

    def test_probe_rejects_missing_authorized_tool(self):
        with patch.dict(os.environ, self.env, clear=True), \
             patch.object(adapter, "_check_public_dns"), \
             patch.object(adapter, "_obtain_mcp_token", return_value="short-token"), \
             patch.object(adapter, "_discover_remote_tools",
                          return_value=([{"name": "list_skill_analyzer_commands"}], "session-id", adapter.MCP_PROTOCOL_VERSION)):
            result = adapter.probe_remote_mcp_host(self.workspace)
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertFalse(result["billable_inference_performed"])

    def test_invoke_completes_one_approved_remote_mcp_call_and_writes_receipt(self):
        response_sequence = [self.initial_response(), self.final_response()]
        patches = self.patch_transport(response_sequence)
        with patch.dict(os.environ, self.env, clear=True):
            with patches[0], patches[1], patches[2], patches[3] as responses, patches[4]:
                result = adapter.invoke_remote_mcp_skill(
                    self.workspace, "artifacts/p0-invocation.json", self.payload, self.context
                )
        self.assertEqual(responses.call_count, 2)
        first_request = responses.call_args_list[0].args[0]
        second_request = responses.call_args_list[1].args[0]
        self.assertEqual(first_request["tool_choice"], {
            "type": "mcp", "server_label": adapter.SERVER_LABEL, "name": adapter.TOOL_NAME
        })
        self.assertEqual(first_request["tools"][0]["allowed_tools"], [adapter.TOOL_NAME])
        self.assertEqual(first_request["tools"][0]["require_approval"], "always")
        self.assertEqual(second_request["input"][0]["type"], "mcp_approval_response")
        self.assertNotIn("tool_choice", second_request)
        self.assertEqual(result["host"], "openai-responses-api")
        self.assertEqual(result["tool_name"], adapter.TOOL_NAME)
        target = self.workspace / "artifacts" / "p0-invocation.json"
        self.assertTrue(target.is_file())
        self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), result["sha256"])
        artifact = json.loads(target.read_text(encoding="utf-8"))
        receipt = artifact["invocation_receipt"]
        self.assertEqual(receipt["host_session"]["initial_response_id"], "resp-initial-001")
        self.assertEqual(receipt["host_session"]["mcp_call_id"], "mcp-call-001")
        self.assertEqual(receipt["remote_mcp"]["allowed_tools"], [adapter.TOOL_NAME])
        self.assertTrue(receipt["verification"]["mcp_call_completed"])
        self.assertEqual(receipt["verification"]["remote_source_attestation"], "NOT_EXPOSED_BY_CURRENT_GATEWAY")

    def test_invoke_rejects_altered_approval_arguments_before_approval_response(self):
        altered = dict(self.arguments)
        altered["target"] += " altered by model"
        response_sequence = [self.initial_response(arguments=altered), self.final_response()]
        patches = self.patch_transport(response_sequence)
        with patch.dict(os.environ, self.env, clear=True):
            with patches[0], patches[1], patches[2], patches[3] as responses, patches[4]:
                with self.assertRaisesRegex(adapter.RemoteMCPError, "differ from the approved scope"):
                    adapter.invoke_remote_mcp_skill(
                        self.workspace, "artifacts/p0-invocation.json", self.payload, self.context
                    )
        self.assertEqual(responses.call_count, 1)
        self.assertFalse((self.workspace / "artifacts" / "p0-invocation.json").exists())

    def test_invoke_rejects_more_than_one_model_visible_tool(self):
        response_sequence = [self.initial_response(names=[adapter.TOOL_NAME, "list_skill_analyzer_commands"])]
        patches = self.patch_transport(response_sequence)
        with patch.dict(os.environ, self.env, clear=True):
            with patches[0], patches[1], patches[2], patches[3] as responses, patches[4]:
                with self.assertRaisesRegex(adapter.RemoteMCPError, "exactly the one allow-listed"):
                    adapter.invoke_remote_mcp_skill(
                        self.workspace, "artifacts/p0-invocation.json", self.payload, self.context
                    )
        responses.assert_called_once()

    def test_invoke_requires_runtime_verified_hso_approval(self):
        context = dict(self.context)
        context["approval_verified"] = False
        patches = self.patch_transport([])
        with patch.dict(os.environ, self.env, clear=True):
            with patches[0], patches[1], patches[2], patches[3] as responses, patches[4]:
                with self.assertRaisesRegex(adapter.RemoteMCPError, "has not authenticated"):
                    adapter.invoke_remote_mcp_skill(
                        self.workspace, "artifacts/p0-invocation.json", self.payload, context
                    )
        responses.assert_not_called()

    def test_invoke_rejects_gateway_result_with_unconfigured_tool_execution_changed(self):
        invalid = gateway_result()
        invalid["tool_execution_status"] = "SUCCEEDED"
        patches = self.patch_transport([self.initial_response(), self.final_response(output=invalid)])
        with patch.dict(os.environ, self.env, clear=True):
            with patches[0], patches[1], patches[2], patches[3], patches[4]:
                with self.assertRaisesRegex(adapter.RemoteMCPError, "no downstream tool execution"):
                    adapter.invoke_remote_mcp_skill(
                        self.workspace, "artifacts/p0-invocation.json", self.payload, self.context
                    )
        self.assertFalse((self.workspace / "artifacts" / "p0-invocation.json").exists())

    def test_https_validation_rejects_local_private_and_credentialed_endpoints(self):
        bad_urls = [
            "http://gateway.example.com/mcp",
            "https://localhost/mcp",
            "https://127.0.0.1/mcp",
            "https://user:password@gateway.example.com/mcp",
            "https://gateway.example.com/mcp?token=leak",
            "https://gateway.example.com:8443/mcp",
        ]
        for url in bad_urls:
            with self.subTest(url=url):
                with self.assertRaises(adapter.RemoteMCPError):
                    adapter._require_https_public_url(url, expected_path="/mcp")

    def test_auth_token_request_requires_bearer_scope_and_exact_audience(self):
        with patch.dict(os.environ, self.env, clear=True), \
             patch.object(adapter, "_http_json", return_value=({"access_token": "ephemeral-token", "token_type": "Bearer", "expires_in": 300}, {}, 200)) as post:
            token = adapter._obtain_mcp_token()
        self.assertEqual(token, "ephemeral-token")
        payload = post.call_args.args[1]
        self.assertEqual(payload["grant_type"], "client_credentials")
        self.assertEqual(payload["scope"], "analyzer:invoke")
        self.assertEqual(payload["audience"], SERVER_URL)

    def test_invalid_approval_binding_is_rejected(self):
        context = dict(self.context)
        context["approval_receipt"] = dict(self.approval, tool_arguments_sha256="0" * 64)
        patches = self.patch_transport([])
        with patch.dict(os.environ, self.env, clear=True):
            with patches[0], patches[1], patches[2], patches[3], patches[4]:
                with self.assertRaisesRegex(adapter.RemoteMCPError, "tool_arguments_sha256"):
                    adapter.invoke_remote_mcp_skill(
                        self.workspace, "artifacts/p0-invocation.json", self.payload, context
                    )


if __name__ == "__main__":
    unittest.main()
