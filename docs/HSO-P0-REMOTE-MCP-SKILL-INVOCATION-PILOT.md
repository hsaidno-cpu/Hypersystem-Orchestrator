# HSO P0 — OpenAI Responses API + SKILL ANALYZER Remote MCP

**Status:** REMOTE_MCP_HOST_ADAPTER_IMPLEMENTED_ON_PR_BRANCH / MOCK_TESTS_PENDING / LIVE_ENDPOINT_NOT_CONFIGURED / NO_LIVE_INVOCATION_RECEIPT / PR_OPEN / NOT_PRODUCTION_READY  
**Purpose:** Prove one governed invocation of one SKILL ANALYZER analysis tool through one named AI host and obtain a receipt that binds the real host response, Remote MCP tool call, approval, result and independently verified local artifact.

## 1. Single vertical slice

| Dimension | Fixed choice |
|---|---|
| Host | OpenAI Responses API |
| Model | `gpt-6.2-astra` |
| Plugin | SKILL ANALYZER 1.3.0 |
| Source repository | `hsaidno-cpu/skill-analyzer` |
| Immutable local source pin | `c469af7977c9bf6dcb3f5ab7b085a6de20d87004` |
| Remote transport | MCP Streamable HTTP |
| MCP endpoint | `https://YOUR_DOMAIN/mcp` |
| MCP server label | `skill_analyzer_internal` |
| Sole permitted tool | `invoke_skill_analyzer` |
| Explicitly excluded tool | `list_skill_analyzer_commands` |
| MCP approval | `require_approval: "always"` |
| HSO authority | S4, SANDBOX only |
| Retry | One attempt; no automatic replay |
| Case | One synthetic security/privacy analysis, no production data |

The parent repo pins the plugin source. It does not copy the plugin's full source into HSO or modify the child repository.

## 2. What the adapter actually does

1. Validate the configured MCP and OIDC endpoints as public HTTPS URLs, resolve their hosts and reject private, loopback, local and reserved address targets.
2. Obtain a short-lived Auth0-compatible OAuth client-credentials token with only the `analyzer:invoke` scope and exact MCP resource audience.
3. Perform an MCP Streamable HTTP initialize handshake and `tools/list`. This is a zero-inference preflight; it does not call the model.
4. Verify the local submodule SHA, plugin identity/version and canonical master `SKILL.md` SHA-256.
5. Build one fixed `analyze` command argument set from the synthetic case. HSO's short-lived HMAC approval binds the action, target, actor, workflow run, server URL digest, tool name, exact argument digest, source commit and skill digest.
6. Call the Responses API with one MCP server, `allowed_tools: ["invoke_skill_analyzer"]`, `require_approval: "always"`, `tool_choice: "required"` and parallel tool calls disabled.
7. Inspect the returned `mcp_list_tools` and `mcp_approval_request`. HSO approves only if the server label, exact tool name and canonical arguments match the signed HSO approval.
8. Send one `mcp_approval_response`, then require exactly one completed `mcp_call` from the same server/tool with no error.
9. Validate the returned SKILL ANALYZER Gateway response contract, write the invocation receipt and analysis result to the isolated GitHub runner workspace, then have the parent runtime independently reopen the target and verify its SHA-256.
10. Preserve the host response IDs, MCP call ID, approval request ID, output digests, token usage, HSO audit chain and final run receipt as a CI artifact.

The Responses API supports remote MCP over Streamable HTTP and requires an approval round-trip when `require_approval` is set to `always`. HSO implements that round-trip explicitly; it does not rely on a model-generated statement that a tool was used. See [OpenAI MCP server documentation](https://developers.openai.com/api/docs/guides/tools-connectors-mcp) and [Responses API create reference](https://developers.openai.com/api/reference/resources/responses/methods/create).

## 3. Read-only boundary and cost boundary

“Read-only” here means the analysis operation does not request writes to the user's files, repositories, accounts or external business systems. It is **not** a zero-side-effect operation:

- The Responses API and the Gateway's configured model provider perform billable inference.
- The Gateway emits metadata-only audit events.
- The MCP tool currently reports `tool_execution_status: NOT_CONFIGURED`; no search, shell, filesystem, repository-write or other downstream tool is authorized by this pilot.
- The HSO runner writes one local evidence artifact in its disposable workspace. That is evidence capture, not a write to the remote plugin service.

The tool list is allow-listed by exact name rather than inferred from MCP `readOnlyHint` annotations. Only `invoke_skill_analyzer` is made available to the model. Any additional tool call, altered argument, second approval request, tool error, invalid response schema or uncertain host result fails closed.

## 4. Approval and failure rules

- The live job is manual-only and branch-locked to `architecture/control-plane-operating-contract-20261123`.
- The workflow actor must be `hsaidno-cpu`, the explicit `approve_single_billable_invocation` input must be true, and `github.run_attempt` must equal 1.
- The `hso-p0-remote-mcp-live` GitHub Environment must require reviewer approval.
- HSO issues a five-minute HMAC receipt and verifies it again during execution. A mismatched URL, tool, argument digest, skill digest, actor, case, action or target is rejected.
- This is a case/run-scoped approval primitive. It is not yet P3's centralized approval issuer or globally replay-resistant nonce service.
- The action is non-idempotent and has `max_attempts: 1`. A timeout or connection loss after a possible dispatch is `OUTCOME_UNKNOWN`; it is never retried automatically.

## 5. Required GitHub Environment configuration

Create Environment `hso-p0-remote-mcp-live`, restrict deployment branches to the exact PR branch and configure required reviewer protection.

**Environment variables**

| Variable | Expected value |
|---|---|
| `MCP_SERVER_URL` | Public HTTPS Remote MCP URL ending in `/mcp` |
| `MCP_OIDC_TOKEN_URL` | Auth0 tenant token endpoint, normally `https://YOUR_TENANT/oauth/token` |
| `MCP_OIDC_CLIENT_ID` | Machine-to-machine client ID |
| `MCP_OIDC_AUDIENCE` | Exactly the same URL as `MCP_SERVER_URL` |

**Environment secrets**

| Secret | Purpose |
|---|---|
| `OPENAI_API_KEY` | OpenAI Responses API access |
| `MCP_OIDC_CLIENT_SECRET` | OAuth client-credentials token exchange |
| `HSO_APPROVAL_HMAC_KEY` | High-entropy HMAC key, at least 32 characters |

Never put these values in chat, workflow JSON, commits, artifacts or logs. The adapter does not persist the MCP bearer token.

The reference identity profile in SKILL ANALYZER uses an Auth0 machine-to-machine client, audience equal to the MCP resource URL and only the `analyzer:invoke` scope. See [SKILL ANALYZER Auth0 profile](https://github.com/hsaidno-cpu/skill-analyzer/blob/c469af7977c9bf6dcb3f5ab7b085a6de20d87004/infra/identity/AUTH0.md).

## 6. Live deployment blocker

The SKILL ANALYZER source includes a FastAPI/MCP Streamable HTTP service and deployment configuration. Its own repository documentation says a commit does not provision a public endpoint, DNS record, OAuth client, provider secret or Redis instance. The public service endpoint has **not** been verified in this task. No actual Responses API call, MCP invocation or live invocation receipt is claimed yet.

The first zero-inference preflight will only pass after the endpoint, TLS/DNS, OAuth client credentials, audience and tool discovery are configured. The first approved live workflow then verifies OpenAI API authentication/model entitlement and produces the invocation receipt. The preflight does not test those OpenAI API credentials.

## 7. Evidence and acceptance

P0 is accepted only when one live run produces all of the following:

- capability probe: `READY_WITH_LIMITATIONS` with a successful OIDC + MCP handshake and exact tool discovery;
- one OpenAI Responses API initial response containing the expected MCP approval request;
- one HSO-validated approval and one completed `mcp_call` from the exact server/tool;
- no additional tool exposed to the model and no second MCP call;
- valid Gateway result contract with canonical `analyze` route and master skill listed as loaded;
- an invocation receipt containing host response ID, MCP call ID, approval request ID, source pin, skill digest and result digest;
- independent SHA-256 read-back of the local artifact;
- valid HSO hash-chained audit and preserved CI artifact.

**Source attestation limitation:** the current Remote Gateway does not expose a cryptographically verifiable deployment commit or runtime skill digest. HSO verifies the canonical local submodule pin and records that remote deployment attestation is `NOT_EXPOSED_BY_CURRENT_GATEWAY`. The receipt must not claim otherwise. This limitation is visible and remains a review item; it is not papered over with a source hash copied from the local checkout.

## 8. Files

- `tools/remote_mcp_responses_adapter.py`
- `tools/issue_p0_skill_approval.py`
- `tools/prepare_p0_skill_workflow.py`
- `catalog/hso-runtime-capabilities.json`
- `catalog/hso-routing-policy.json`
- `governance/hso-execution-policy.json`
- `contracts/hso-p0-skill-invocation-result.schema.json`
- `examples/hso-p0-skill-invocation-request.json`
- `tests/test_remote_mcp_responses_adapter.py`
- `tests/test_p0_approval_workflow.py`
- `.github/workflows/catalog-validation.yml` (manual P0 live job)

P0 acceptance must be completed before P1 work starts. P1 is not implicitly approved by this adapter contract.
