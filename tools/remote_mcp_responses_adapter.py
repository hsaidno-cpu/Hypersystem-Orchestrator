#!/usr/bin/env python3
"""Narrow HSO host adapter: OpenAI Responses API -> one SKILL ANALYZER Remote MCP tool."""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import socket
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

PLUGIN_ID = "plugins_6ae2a122f5c881919193c9b0ba51961e"
PLUGIN_KEY = "skill-analyzer"
PLUGIN_VERSION = "1.3.0"
SOURCE_REPOSITORY = "hsaidno-cpu/skill-analyzer"
SOURCE_PIN = "c469af7977c9bf6dcb3f5ab7b085a6de20d87004"
HOST_ID = "openai-responses-api"
MODEL_ID = "gpt-6.2-astra"
SERVER_LABEL = "skill_analyzer_internal"
TOOL_NAME = "invoke_skill_analyzer"
ALLOWED_TOOLS = [TOOL_NAME]
MCP_PROTOCOL_VERSION = "2025-03-26"
MAX_HTTP_BYTES = 2_000_000
MAX_RESULT_CHARS = 60_000
MAX_ARTIFACT_BYTES = 90_000
HTTP_TIMEOUT_SECONDS = 25
API_TIMEOUT_SECONDS = 180


class RemoteMCPError(RuntimeError):
    """A fail-closed transport, authorization, host, or receipt error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def _require_https_public_url(value: str, *, expected_path: str | None = None) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 2048:
        raise RemoteMCPError("required HTTPS endpoint is missing or invalid")
    parsed = urlsplit(value.strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise RemoteMCPError("endpoints must use HTTPS and cannot contain embedded credentials")
    if parsed.query or parsed.fragment:
        raise RemoteMCPError("endpoint query strings and fragments are not permitted")
    if parsed.port not in (None, 443):
        raise RemoteMCPError("P0 endpoints must use the standard HTTPS port")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".localhost", ".local", ".internal")):
        raise RemoteMCPError("local and internal endpoints are not permitted")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise RemoteMCPError("non-public IP endpoints are not permitted")
    if expected_path is not None and parsed.path.rstrip("/") != expected_path:
        raise RemoteMCPError(f"endpoint path must be {expected_path}")
    if not parsed.path:
        raise RemoteMCPError("endpoint path is required")
    return value.strip().rstrip("/") if expected_path == "/mcp" else value.strip()


def _check_public_dns(host: str) -> None:
    """Reject DNS names resolving to private, loopback, link-local or reserved addresses."""
    try:
        records = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise RemoteMCPError("endpoint DNS resolution failed") from exc
    addresses = {record[4][0] for record in records}
    if not addresses:
        raise RemoteMCPError("endpoint DNS resolution returned no addresses")
    for raw in addresses:
        try:
            parsed = ipaddress.ip_address(raw)
        except ValueError as exc:
            raise RemoteMCPError("endpoint DNS returned an invalid address") from exc
        if not parsed.is_global:
            raise RemoteMCPError("endpoint DNS resolves to a non-public address")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _http_json(
    url: str,
    body: dict[str, Any],
    headers: dict[str, str],
    *,
    timeout: int = HTTP_TIMEOUT_SECONDS,
) -> tuple[dict[str, Any], dict[str, str], int]:
    encoded = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=encoded, headers=headers, method="POST")
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            status = int(response.status)
            raw = response.read(MAX_HTTP_BYTES + 1)
            response_headers = {k.lower(): v for k, v in response.headers.items()}
    except urllib.error.HTTPError as exc:
        raise RemoteMCPError(f"HTTPS endpoint rejected the request (HTTP {exc.code})") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RemoteMCPError(f"HTTPS endpoint is unreachable ({type(exc).__name__})") from exc
    if len(raw) > MAX_HTTP_BYTES:
        raise RemoteMCPError("HTTPS response exceeds the P0 response-size limit")
    if status < 200 or status >= 300:
        raise RemoteMCPError(f"HTTPS endpoint returned HTTP {status}")
    if not raw.strip():
        return {}, response_headers, status
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        parsed = _parse_sse(raw.decode("utf-8", errors="replace"))
    if not isinstance(parsed, dict):
        raise RemoteMCPError("HTTPS endpoint returned a non-object JSON-RPC response")
    return parsed, response_headers, status


def _parse_sse(text: str) -> dict[str, Any]:
    messages = []
    for line in text.splitlines():
        if line.startswith("data:"):
            data = line[5:].strip()
            if data and data != "[DONE]":
                try:
                    value = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    messages.append(value)
    if not messages:
        raise RemoteMCPError("MCP Streamable HTTP response contained no JSON message")
    return messages[-1]


def _obtain_mcp_token() -> str:
    token_url = _require_https_public_url(os.environ.get("MCP_OIDC_TOKEN_URL", ""))
    client_id = os.environ.get("MCP_OIDC_CLIENT_ID", "").strip()
    client_secret = os.environ.get("MCP_OIDC_CLIENT_SECRET", "").strip()
    audience = os.environ.get("MCP_OIDC_AUDIENCE", "").strip()
    server_url = _require_https_public_url(
        os.environ.get("MCP_SERVER_URL", ""), expected_path="/mcp"
    )
    if not all((client_id, client_secret, audience)):
        raise RemoteMCPError("MCP OIDC client credentials or audience are not configured")
    if audience.rstrip("/") != server_url.rstrip("/"):
        raise RemoteMCPError("OIDC audience must exactly match the Remote MCP resource URL")
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "scope": "analyzer:invoke",
    }
    result, _, _ = _http_json(
        token_url,
        payload,
        {"Accept": "application/json", "Content-Type": "application/json"},
    )
    token = result.get("access_token")
    token_type = str(result.get("token_type", "Bearer")).lower()
    expires_in = result.get("expires_in", 0)
    if not isinstance(token, str) or not token or token_type != "bearer":
        raise RemoteMCPError("OIDC provider did not return a bearer access token")
    if not isinstance(expires_in, (int, float)) or expires_in < 30:
        raise RemoteMCPError("OIDC access token lifetime is missing or too short")
    return token


def _mcp_post(
    server_url: str,
    token: str,
    body: dict[str, Any],
    *,
    session_id: str | None = None,
    protocol_version: str = MCP_PROTOCOL_VERSION,
) -> tuple[dict[str, Any], dict[str, str], int]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": protocol_version,
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    return _http_json(server_url, body, headers)


def _discover_remote_tools(server_url: str, token: str) -> tuple[list[dict[str, Any]], str | None, str]:
    initialize = {
        "jsonrpc": "2.0",
        "id": "hso-p0-initialize",
        "method": "initialize",
        "params": {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "hso-p0-host-adapter", "version": "1.0.0"},
        },
    }
    initialized, headers, _ = _mcp_post(server_url, token, initialize)
    if initialized.get("error") or not isinstance(initialized.get("result"), dict):
        raise RemoteMCPError("Remote MCP initialize handshake failed")
    negotiated = initialized["result"].get("protocolVersion")
    if not isinstance(negotiated, str) or not negotiated:
        raise RemoteMCPError("Remote MCP server did not negotiate a protocol version")
    session_id = headers.get("mcp-session-id")

    notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    _mcp_post(server_url, token, notification, session_id=session_id, protocol_version=negotiated)

    listed, _, _ = _mcp_post(
        server_url,
        token,
        {"jsonrpc": "2.0", "id": "hso-p0-tools-list", "method": "tools/list", "params": {}},
        session_id=session_id,
        protocol_version=negotiated,
    )
    if listed.get("error") or not isinstance(listed.get("result"), dict):
        raise RemoteMCPError("Remote MCP tools/list failed")
    tools = listed["result"].get("tools")
    if not isinstance(tools, list):
        raise RemoteMCPError("Remote MCP tools/list did not return a tool array")
    return tools, session_id, negotiated


def inspect_local_skill_source(workspace: Path) -> dict[str, str]:
    submodule = workspace / "plugins" / "skill-analyzer"
    skill = submodule / "skills" / "skill-analyzer" / "SKILL.md"
    manifest_path = submodule / "plugin.json"
    for path in (submodule, skill, manifest_path):
        if path.is_symlink():
            raise RemoteMCPError("pinned SKILL ANALYZER source cannot traverse symlinks")
    if not submodule.is_dir() or not skill.is_file() or not manifest_path.is_file():
        raise RemoteMCPError("pinned SKILL ANALYZER source submodule is missing or incomplete")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result = subprocess.run(
            ["git", "-C", str(submodule), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10, check=False,
            env={key: os.environ[key] for key in ("PATH", "LANG", "LC_ALL", "SYSTEMROOT") if key in os.environ},
        )
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise RemoteMCPError("pinned SKILL ANALYZER source verification failed") from exc
    commit = result.stdout.strip()
    if result.returncode != 0 or commit != SOURCE_PIN:
        raise RemoteMCPError("SKILL ANALYZER submodule does not match the approved immutable source pin")
    if manifest.get("name") != PLUGIN_KEY or manifest.get("version") != PLUGIN_VERSION:
        raise RemoteMCPError("SKILL ANALYZER package identity or source version mismatch")
    return {
        "source_commit": commit,
        "plugin_version": manifest["version"],
        "skill_sha256": sha256_bytes(skill.read_bytes()),
    }


def _expected_arguments(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("skill_name") != PLUGIN_KEY or payload.get("plugin_id") != PLUGIN_ID:
        raise RemoteMCPError("P0 plugin identity does not match the pinned SKILL ANALYZER package")
    if payload.get("source_commit") != SOURCE_PIN:
        raise RemoteMCPError("P0 source commit differs from the approved immutable source pin")
    target = payload.get("request")
    objective = payload.get("objective")
    context = payload.get("context")
    depth = payload.get("depth", "deep")
    constraints = payload.get("constraints")
    if not isinstance(target, str) or not 80 <= len(target) <= 12000:
        raise RemoteMCPError("P0 target must be a bounded synthetic analysis case")
    if not isinstance(objective, str) or not objective or len(objective) > 3000:
        raise RemoteMCPError("P0 objective is missing or exceeds its limit")
    if not isinstance(context, str) or len(context) > 8000:
        raise RemoteMCPError("P0 context is invalid or exceeds its limit")
    if depth not in {"standard", "deep", "forensic"}:
        raise RemoteMCPError("P0 depth is not supported")
    if not isinstance(constraints, list) or not constraints or len(constraints) > 10:
        raise RemoteMCPError("P0 constraints must be a non-empty bounded list")
    if any(not isinstance(value, str) or not value or len(value) > 1000 for value in constraints):
        raise RemoteMCPError("P0 constraints contain an invalid entry")
    return {
        "command": "analyze",
        "target": target,
        "objective": objective,
        "depth": depth,
        "context": context,
        "constraints": constraints,
    }


def _tool_config(server_url: str, token: str) -> dict[str, Any]:
    return {
        "type": "mcp",
        "server_label": SERVER_LABEL,
        "server_description": "Internal read-only SKILL ANALYZER analysis gateway. One analysis tool only; no write or external connector tools are authorized.",
        "server_url": server_url,
        "authorization": token,
        "allowed_tools": ALLOWED_TOOLS,
        "require_approval": "always",
    }


def _responses_post(payload: dict[str, Any]) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RemoteMCPError("OPENAI_API_KEY is not configured")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=API_TIMEOUT_SECONDS) as response:
            raw = response.read(MAX_HTTP_BYTES + 1)
            status = int(response.status)
    except urllib.error.HTTPError as exc:
        raise RemoteMCPError(f"OpenAI Responses API rejected the request (HTTP {exc.code})") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RemoteMCPError(f"OpenAI Responses API is unreachable ({type(exc).__name__})") from exc
    if status < 200 or status >= 300 or len(raw) > MAX_HTTP_BYTES:
        raise RemoteMCPError("OpenAI Responses API returned an invalid status or oversized body")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RemoteMCPError("OpenAI Responses API returned malformed JSON") from exc
    if not isinstance(result, dict) or not isinstance(result.get("id"), str):
        raise RemoteMCPError("OpenAI Responses API response is missing its response ID")
    return result


def _output_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    output = response.get("output")
    if not isinstance(output, list):
        raise RemoteMCPError("OpenAI Responses API response has no output item list")
    if any(not isinstance(item, dict) for item in output):
        raise RemoteMCPError("OpenAI Responses API output contains a malformed item")
    return output


def _decode_tool_output(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        value: Any = raw
    elif isinstance(raw, str):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RemoteMCPError("MCP tool output is not valid JSON") from exc
    elif isinstance(raw, list):
        text_items = [item.get("text") for item in raw if isinstance(item, dict) and isinstance(item.get("text"), str)]
        if len(text_items) != 1:
            raise RemoteMCPError("MCP tool output does not contain one structured text result")
        try:
            value = json.loads(text_items[0])
        except json.JSONDecodeError as exc:
            raise RemoteMCPError("MCP tool text result is not valid JSON") from exc
    else:
        raise RemoteMCPError("MCP tool output has an unsupported representation")

    # Some MCP servers wrap their result in content[] rather than structured JSON.
    if isinstance(value, dict) and "request_id" not in value and isinstance(value.get("content"), list):
        text_items = [item.get("text") for item in value["content"] if isinstance(item, dict) and isinstance(item.get("text"), str)]
        if len(text_items) == 1:
            try:
                value = json.loads(text_items[0])
            except json.JSONDecodeError as exc:
                raise RemoteMCPError("MCP wrapped tool result is not valid JSON") from exc
    if not isinstance(value, dict):
        raise RemoteMCPError("MCP tool result must be a JSON object")
    return value


def _validate_gateway_result(result: dict[str, Any], result_schema: dict[str, Any]) -> None:
    try:
        from jsonschema import Draft202012Validator
        Draft202012Validator(result_schema).validate(result)
    except Exception as exc:
        raise RemoteMCPError(f"SKILL ANALYZER response contract validation failed ({type(exc).__name__})") from exc
    if result.get("command") != "analyze":
        raise RemoteMCPError("Remote Gateway returned a command other than analyze")
    if "skill-analyzer" not in result.get("loaded_skills", []):
        raise RemoteMCPError("Remote Gateway result does not record the SKILL ANALYZER master skill")
    route = result.get("route", {})
    if not isinstance(route, dict) or route.get("id") != "analyze":
        raise RemoteMCPError("Remote Gateway did not confirm the canonical analyze route")
    if result.get("tool_execution_status") != "NOT_CONFIGURED":
        raise RemoteMCPError("P0 requires the analysis-only Gateway with no downstream tool execution")
    text = result.get("result")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_RESULT_CHARS:
        raise RemoteMCPError("SKILL ANALYZER returned an empty or oversized analysis result")


def _validate_approval_binding(
    approval: dict[str, Any] | None,
    *,
    server_url: str,
    arguments: dict[str, Any],
    source_commit: str,
) -> None:
    if not isinstance(approval, dict):
        raise RemoteMCPError("P0 signed approval receipt is missing from the runtime context")
    required = {
        "host": HOST_ID,
        "mcp_server_label": SERVER_LABEL,
        "mcp_tool_name": TOOL_NAME,
        "mcp_server_url_sha256": sha256_bytes(server_url.encode("utf-8")),
        "tool_arguments_sha256": sha256_json(arguments),
        "plugin_source_commit": source_commit,
    }
    for key, expected in required.items():
        if approval.get(key) != expected:
            raise RemoteMCPError(f"P0 approval receipt is not bound to the expected {key}")
    if not approval.get("nonce") or not approval.get("approver"):
        raise RemoteMCPError("P0 approval receipt is missing an approver or nonce")


def probe_remote_mcp_host(_workspace: Path | None = None, _skill_source_path: str | None = None) -> dict[str, Any]:
    required = (
        "OPENAI_API_KEY",
        "MCP_SERVER_URL",
        "MCP_OIDC_TOKEN_URL",
        "MCP_OIDC_CLIENT_ID",
        "MCP_OIDC_CLIENT_SECRET",
        "MCP_OIDC_AUDIENCE",
    )
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing:
        return {
            "status": "NOT_CONFIGURED",
            "host": HOST_ID,
            "evidence": "required host or Remote MCP configuration is absent",
            "missing_configuration": missing,
            "billable_inference_performed": False,
        }
    try:
        server_url = _require_https_public_url(os.environ["MCP_SERVER_URL"], expected_path="/mcp")
        token_url = _require_https_public_url(os.environ["MCP_OIDC_TOKEN_URL"])
        server_host = urlsplit(server_url).hostname
        token_host = urlsplit(token_url).hostname
        _check_public_dns(server_host)
        _check_public_dns(token_host)
        token = _obtain_mcp_token()
        tools, session_id, protocol = _discover_remote_tools(server_url, token)
        names = [item.get("name") for item in tools if isinstance(item, dict)]
        if TOOL_NAME not in names:
            raise RemoteMCPError("Remote MCP server does not advertise the one authorized P0 tool")
        # Do not accept a different case or duplicate target tool.
        if names.count(TOOL_NAME) != 1:
            raise RemoteMCPError("Remote MCP server advertises a duplicate invocation tool")
        return {
            "status": "READY_WITH_LIMITATIONS",
            "host": HOST_ID,
            "evidence": "HTTPS endpoint, Auth0-compatible client-credentials token, Streamable HTTP handshake and exact MCP tool discovery passed; OpenAI API entitlement is not tested",
            "server_label": SERVER_LABEL,
            "server_url_sha256": sha256_bytes(server_url.encode("utf-8")),
            "mcp_protocol_version": protocol,
            "session_id_present": bool(session_id),
            "tool_name": TOOL_NAME,
            "allowed_tools": ALLOWED_TOOLS,
            "advertised_tool_count": len(tools),
            "openai_api_key_presence_checked": True,
            "openai_api_authentication_tested": False,
            "billable_inference_performed": False,
        }
    except Exception as exc:
        return {
            "status": "UNAVAILABLE",
            "host": HOST_ID,
            "evidence": f"Remote MCP preflight failed closed ({type(exc).__name__})",
            "billable_inference_performed": False,
        }


def invoke_remote_mcp_skill(
    workspace: Path,
    target_path: str,
    payload: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    server_url = _require_https_public_url(
        os.environ.get("MCP_SERVER_URL", ""), expected_path="/mcp"
    )
    token_url = _require_https_public_url(os.environ.get("MCP_OIDC_TOKEN_URL", ""))
    _check_public_dns(urlsplit(server_url).hostname)
    _check_public_dns(urlsplit(token_url).hostname)
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise RemoteMCPError("OPENAI_API_KEY is not configured")

    if context.get("approval_verified") is not True:
        raise RemoteMCPError("HSO runtime has not authenticated the scoped approval receipt")
    source = inspect_local_skill_source(workspace)
    expected_arguments = _expected_arguments(payload)
    source_commit = payload["source_commit"]
    if source["source_commit"] != source_commit:
        raise RemoteMCPError("requested source commit differs from the checked-out source pin")
    if payload.get("skill_sha256") != source["skill_sha256"]:
        raise RemoteMCPError("requested skill digest differs from the checked-out master skill")
    _validate_approval_binding(
        context.get("approval_receipt"),
        server_url=server_url,
        arguments=expected_arguments,
        source_commit=source_commit,
    )
    if context["approval_receipt"].get("skill_sha256") != source["skill_sha256"]:
        raise RemoteMCPError("P0 approval receipt is not bound to the checked-out SKILL.md digest")

    # Refresh the scoped token immediately before the host operation; never log or persist it.
    mcp_token = _obtain_mcp_token()
    advertised, _, negotiated_protocol = _discover_remote_tools(server_url, mcp_token)
    if TOOL_NAME not in [item.get("name") for item in advertised if isinstance(item, dict)]:
        raise RemoteMCPError("authorized MCP tool disappeared between preflight and dispatch")

    prompt = (
        "Perform one SKILL ANALYZER invocation through the supplied Remote MCP tool. "
        "Do not answer the analytical task yourself. Call the one allowed tool exactly once. "
        "Use the following arguments exactly; do not paraphrase, add fields, or call any other tool. "
        "After the tool result is returned, summarize only that result briefly.\n\n"
        "EXACT_TOOL_ARGUMENTS_JSON:\n" + json.dumps(expected_arguments, ensure_ascii=False, indent=2)
    )
    tool_config = _tool_config(server_url, mcp_token)
    initial_response = _responses_post({
        "model": MODEL_ID,
        "input": prompt,
        "tools": [tool_config],
        "tool_choice": {"type": "mcp", "server_label": SERVER_LABEL, "name": TOOL_NAME},
        "parallel_tool_calls": False,
        "max_output_tokens": 1200,
    })
    initial_items = _output_items(initial_response)
    tool_lists = [item for item in initial_items if item.get("type") == "mcp_list_tools"]
    approvals = [item for item in initial_items if item.get("type") == "mcp_approval_request"]
    if len(tool_lists) != 1 or len(approvals) != 1:
        raise RemoteMCPError("Responses API did not return exactly one MCP tool-list receipt and one approval request")
    tool_list = tool_lists[0]
    if tool_list.get("server_label") != SERVER_LABEL or tool_list.get("error"):
        raise RemoteMCPError("Responses API tool discovery failed or resolved the wrong MCP server")
    listed_tools = tool_list.get("tools")
    if not isinstance(listed_tools, list):
        raise RemoteMCPError("Responses API MCP tool-list receipt is malformed")
    listed_names = [item.get("name") for item in listed_tools if isinstance(item, dict)]
    if listed_names != [TOOL_NAME]:
        raise RemoteMCPError("Responses API did not expose exactly the one allow-listed MCP tool")

    approval = approvals[0]
    approval_id = approval.get("id")
    approval_args = approval.get("arguments")
    if (
        approval.get("server_label") != SERVER_LABEL
        or approval.get("name") != TOOL_NAME
        or not isinstance(approval_id, str)
        or not isinstance(approval_args, str)
    ):
        raise RemoteMCPError("Responses API approval request is not for the approved server/tool")
    try:
        parsed_arguments = json.loads(approval_args)
    except json.JSONDecodeError as exc:
        raise RemoteMCPError("Responses API approval arguments are malformed") from exc
    if canonical_json(parsed_arguments) != canonical_json(expected_arguments):
        raise RemoteMCPError("Responses API requested tool arguments differ from the approved scope")
    approval_receipt = context["approval_receipt"]
    if approval_receipt.get("tool_arguments_sha256") != sha256_json(parsed_arguments):
        raise RemoteMCPError("Responses API tool arguments do not match the signed approval digest")

    # Approval is sent only after the host's server, tool, arguments and HSO signature checks pass.
    final_response = _responses_post({
        "model": MODEL_ID,
        "previous_response_id": initial_response["id"],
        "input": [{
            "type": "mcp_approval_response",
            "approval_request_id": approval_id,
            "approve": True,
        }],
        "tools": [tool_config],
        "parallel_tool_calls": False,
        "max_output_tokens": 1200,
    })
    if final_response.get("status") != "completed":
        raise RemoteMCPError("Responses API approval continuation did not complete")
    final_items = _output_items(final_response)
    calls = [item for item in final_items if item.get("type") == "mcp_call"]
    further_approvals = [item for item in final_items if item.get("type") == "mcp_approval_request"]
    if len(calls) != 1 or further_approvals:
        raise RemoteMCPError("Responses API did not return exactly one completed MCP call")
    call = calls[0]
    if (
        call.get("server_label") != SERVER_LABEL
        or call.get("name") != TOOL_NAME
        or call.get("approval_request_id") != approval_id
        or call.get("error")
        or call.get("status") not in (None, "completed")
    ):
        raise RemoteMCPError("Remote MCP call failed or its receipt did not match the approved call")
    call_arguments = call.get("arguments")
    if not isinstance(call_arguments, str) or canonical_json(json.loads(call_arguments)) != canonical_json(expected_arguments):
        raise RemoteMCPError("final MCP call arguments differ from the approved arguments")

    output = _decode_tool_output(call.get("output"))
    schema_path = Path(__file__).resolve().parents[1] / "contracts" / "hso-p0-skill-invocation-result.schema.json"
    try:
        result_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RemoteMCPError("canonical HSO P0 result schema is missing or invalid") from exc
    _validate_gateway_result(output, result_schema)

    result_text = output["result"]
    output_digest = sha256_bytes(result_text.encode("utf-8"))
    initial_usage = initial_response.get("usage", {}) if isinstance(initial_response.get("usage"), dict) else {}
    final_usage = final_response.get("usage", {}) if isinstance(final_response.get("usage"), dict) else {}
    usage = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        values = []
        for source in (initial_usage, final_usage):
            value = source.get(key)
            if isinstance(value, int) and value >= 0:
                values.append(value)
        if values:
            usage[key] = sum(values)

    receipt = {
        "receipt_schema_version": "1.0.0",
        "invocation_id": "INV-" + uuid.uuid4().hex,
        "case_id": context.get("case_id"),
        "timestamp": utc_now(),
        "status": "SUCCEEDED",
        "host": HOST_ID,
        "model": MODEL_ID,
        "plugin": {
            "plugin_id": PLUGIN_ID,
            "plugin_key": PLUGIN_KEY,
            "version": PLUGIN_VERSION,
            "source_repository": SOURCE_REPOSITORY,
            "source_commit": source_commit,
            "skill_sha256": source["skill_sha256"],
            "remote_source_attestation": "NOT_EXPOSED_BY_CURRENT_GATEWAY",
        },
        "remote_mcp": {
            "server_label": SERVER_LABEL,
            "server_url_sha256": sha256_bytes(server_url.encode("utf-8")),
            "transport": "STREAMABLE_HTTP",
            "protocol_version": negotiated_protocol,
            "tool_name": TOOL_NAME,
            "allowed_tools": ALLOWED_TOOLS,
            "additional_tools_exposed_to_model": 0,
            "approval_policy": "ALWAYS",
        },
        "host_session": {
            "initial_response_id": initial_response["id"],
            "final_response_id": final_response["id"],
            "approval_request_id": approval_id,
            "mcp_call_id": call.get("id"),
            "tool_arguments_sha256": sha256_json(expected_arguments),
            "host_tool_call_status": "COMPLETED",
        },
        "gateway_result": {
            "request_id": output["request_id"],
            "command": output["command"],
            "route": output["route"],
            "loaded_skills": output["loaded_skills"],
            "provider": output["provider"],
            "model": output["model"],
            "execution_status": output["execution_status"],
            "tool_execution_status": output["tool_execution_status"],
            "usage": output["usage"],
            "result_sha256": output_digest,
            "result_chars": len(result_text),
        },
        "approval": {
            "basis": "HSO_HMAC_SCOPED_APPROVAL_PLUS_RESPONSES_API_MCP_APPROVAL",
            "approver": approval_receipt.get("approver"),
            "nonce_sha256": sha256_bytes(str(approval_receipt["nonce"]).encode("utf-8")),
            "issued_at": approval_receipt.get("issued_at"),
            "expires_at": approval_receipt.get("expires_at"),
            "host_approval_request_id": approval_id,
        },
        "verification": {
            "remote_mcp_tools_discovered": True,
            "only_allowlisted_tool_exposed": True,
            "hso_approval_signature_checked_by_runtime": True,
            "approval_scope_matches_arguments": True,
            "mcp_call_completed": True,
            "gateway_result_contract_valid": True,
            "master_skill_reported_loaded": True,
            "remote_source_attestation": "NOT_EXPOSED_BY_CURRENT_GATEWAY",
            "external_data_mutation": "NOT_REQUESTED",
            "metadata_audit_only": True,
        },
        "request_sha256": sha256_json(expected_arguments),
        "usage": usage,
    }
    artifact = json.dumps(
        {"invocation_receipt": receipt, "analysis_result": output},
        ensure_ascii=False,
        indent=2,
    ) + "\n"
    raw_artifact = artifact.encode("utf-8")
    if len(raw_artifact) > MAX_ARTIFACT_BYTES:
        raise RemoteMCPError("P0 invocation artifact exceeds the bounded output limit")

    part = Path(target_path)
    if not target_path or part.is_absolute() or any(x in {".", ".."} for x in part.parts):
        raise RemoteMCPError("P0 receipt target must be a safe relative path")
    root = workspace.resolve()
    current = root
    for piece in part.parts:
        current = current / piece
        if current.is_symlink():
            raise RemoteMCPError("P0 receipt target cannot traverse symbolic links")
    target = current.resolve(strict=False)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise RemoteMCPError("P0 receipt target escapes the HSO workspace") from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(raw_artifact)
        stream.flush()
        os.fsync(stream.fileno())

    digest = sha256_bytes(raw_artifact)
    return {
        "target_path": str(target.relative_to(root)),
        "sha256": digest,
        "created": True,
        "no_op": False,
        "host": HOST_ID,
        "model": MODEL_ID,
        "host_response_id": final_response["id"],
        "mcp_call_id": call.get("id"),
        "approval_request_id": approval_id,
        "source_commit": source_commit,
        "tool_name": TOOL_NAME,
        "analysis_result_sha256": output_digest,
        "usage": usage,
    }
