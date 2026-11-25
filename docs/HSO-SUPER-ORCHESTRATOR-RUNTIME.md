# HSO Super-Orchestrator — Controlled Runtime v0.1

**Status:** SANDBOX_RUNTIME_CI_VERIFIED / P0_REMOTE_MCP_HOST_ADAPTER_IMPLEMENTED / LIVE_ENDPOINT_NOT_CONFIGURED / NO_LIVE_INVOCATION_RECEIPT / NOT_MERGED / NOT_PRODUCTION_READY  
**Scope:** capability discovery, route arbitration, policy enforcement, DAG execution, bounded retry, idempotency, target read-back, compensation and hash-chained audit.

## What is actually executable

The file tools/hso_super_orchestrator.py is a real Python execution engine. GitHub Actions runs it on an isolated hosted runner. The registered built-in adapter creates a new file inside a dedicated temporary workspace; the independent verifier reopens that file and checks its SHA-256 digest. A test-only adapter injects one transient fault so CI can observe retry and recovery.

This is real runtime execution against a real sandbox target. The default continuous-integration workflow still proves only the sandbox path. A separate, narrowly allow-listed SKILL ANALYZER Remote MCP adapter is registered on the PR branch, but its public endpoint/OIDC configuration is not yet verified; no live plugin invocation is claimed. Generic plugin dispatch and generic multi-server MCP remain NOT_CONFIGURED.

## The eight requirements mapped to implementation

| Requirement | Implementation | Evidence boundary |
|---|---|---|
| Capability discovery | Runtime probes every allow-listed handler; write/read-back is tested in a temporary directory | Only registered built-in adapters are probed |
| Primary owner + specialists | Task-type routing table resolves one owner and only necessary specialists | Routing is not proof that a plugin skill was invoked |
| Dependency plan | Stable topological order; unknown dependencies, duplicates, self-links and cycles rejected | Serial execution in this version |
| Permission + approval | Policy registry is authoritative; default deny; action-specific scope, environment, S0-S5 floor and approval receipt verifier | Only ephemeral sandbox actions are enabled |
| Real dispatch | Trusted Python handler is called by the runtime in GitHub Actions | No arbitrary shell, dynamic import, plugin API or network dispatch |
| Failure + recovery | Retryable/permanent classification, max attempts, idempotency key, SQLite run ledger, conditional compensation | SQLite is local single-runner state, not a distributed production store |
| Target verification | Independent filesystem read-back and SHA-256 comparison after the handler returns | Verifies the sandbox artifact only |
| Traceable audit | JSONL events, sequence IDs, previous-hash chain, event hash, redaction and final chain verification | Hash chain is unsigned; archive/sign externally for strong tamper evidence |

## Execution model

REQUEST → SCHEMA VALIDATION → CAPABILITY PROBE → ROUTE RESOLUTION → POLICY CHECK → DAG ORDER → DISPATCH → RETRY / RECOVERY → TARGET READ-BACK → AUDIT RECEIPT

The action handler is selected by a fixed capability registry. The user-supplied workflow cannot choose a Python function, import path, shell command, arbitrary URL or executable. Unknown actions are denied. File paths must be relative to the declared workspace, cannot traverse parent segments or symlinks, and writes cannot overwrite different existing content.

### Capability status semantics

- READY: registered handler exists and a live probe succeeded.
- UNAVAILABLE: a configured handler failed its live probe.
- NOT_CONFIGURED: no adapter is installed for that capability.
- DISABLED_TEST_ONLY: a test adapter is intentionally excluded from normal discovery.

The capability receipt records adapter ID, scope, host, Python version, probe time and evidence. A registry row or a plugin identity alone is not enough to reach READY.

### Routing semantics

The runtime uses explicit task_type rules rather than keyword guessing. Each package receives exactly one primary owner. Supporting specialists come from the route registry and are validated against HSO components or the plugin catalog. In the sample artifact workflow, CP-05 owns dispatch while CP-07 is the independent verification specialist. A plugin-specific forensic route is present, but it remains blocked because plugin.skill.invoke has no verified host adapter.

### Authorization and approvals

The checked-in policy is the source of truth, not fields in the request. Sandbox writes require S3 and are restricted to SANDBOX. Unknown actions, staging, production, external HTTP, child-repository writes, remote MCP and plugin invocation are not enabled. Where a future action is marked approval_required, a scoped HMAC-SHA256 approval receipt must match case, action, target, authority, approver, nonce and expiry; missing key, invalid signature or expired receipt fails closed. The current allow-list contains no approval-gated external action and no central approval issuer or replay-resistant nonce service; this verifier is a local control primitive, not a complete enterprise approval workflow.

Never put approval secrets or API keys in workflow JSON, issue text, audit events or Git. Supply HSO_APPROVAL_HMAC_KEY through a secret manager only when a separately reviewed adapter actually needs signed approval.

### Recovery and idempotency

Retries are bounded by the action policy and allowed only for idempotent actions. An idempotency key is bound to an action digest in SQLite. Reuse with a different digest is rejected. A replay of an already successful operation performs target read-back before it can be reported as an idempotent skip. A stale or missing target after a recorded success becomes BLOCKED_OUTCOME_UNKNOWN, not an automatic repeat.

Compensation is conditional: the runtime removes only a target that the current execution created and whose digest still matches. If the target changed, compensation is blocked and requires manual review.

### Audit and evidence

The JSONL audit stream records route selection, dispatch, each attempt, retry scheduling, action result, target verification, compensation and final state. Secret-like fields are redacted; payload contents are not copied into the event stream. Every event includes a sequence number, timestamp, previous hash and event hash. The verify-audit command replays the chain.

A hash chain is tamper-evident, not independently authenticated: a privileged actor who can rewrite the entire file can recompute it. Production requires an external immutable/WORM store and a signed or externally anchored run receipt.

## Run locally

    python -m pip install -r requirements-test.txt
    python tools/hso_super_orchestrator.py discover --output /tmp/hso-capabilities.json
    python tools/hso_super_orchestrator.py run examples/hso-runtime-execution.example.json --workspace /tmp/hso-target --ledger /tmp/hso-ledger.sqlite --audit /tmp/hso-audit.jsonl --receipt /tmp/hso-receipt.json
    python tools/hso_super_orchestrator.py verify-audit /tmp/hso-audit.jsonl

For the test-only retry demonstration:

    HSO_ENABLE_TEST_ADAPTERS=1 python tools/hso_super_orchestrator.py run examples/hso-runtime-recovery.example.json --workspace /tmp/hso-recovery-target --ledger /tmp/hso-recovery.sqlite --audit /tmp/hso-recovery-audit.jsonl --receipt /tmp/hso-recovery-receipt.json

## P0 — one-host / one-skill Remote MCP invocation pilot

The selected host is OpenAI Responses API and the selected transport is Remote MCP over Streamable HTTP. The sole plugin owner is SKILL ANALYZER; the sole model-visible tool is `invoke_skill_analyzer`. The generic `plugin.skill.invoke` and generic multi-server `mcp.remote.invoke` capabilities remain NOT_CONFIGURED.

- Host: OpenAI Responses API; model: `gpt-6.2-astra`.
- Plugin source: `hsaidno-cpu/skill-analyzer`, version 1.3.0, immutable local source pin `c469af7977c9bf6dcb3f5ab7b085a6de20d87004`.
- Remote protocol: Streamable HTTP; one protected `/mcp` endpoint; Auth0-compatible client credentials with exact resource audience and only `analyzer:invoke`.
- Tool allowlist: exactly `invoke_skill_analyzer`; `list_skill_analyzer_commands` is not exposed to the model.
- Approval: scoped five-minute HMAC receipt plus Responses API `require_approval: "always"`; HSO checks exact server, tool, arguments, target and source digest before sending `mcp_approval_response`.
- Execution: one synthetic analysis case, S4, SANDBOX, manual workflow dispatch, repository owner guard, explicit checkbox, protected GitHub environment and one attempt only.
- Recovery: inference is non-idempotent. Any ambiguous post-dispatch failure is OUTCOME_UNKNOWN; no automatic retry.
- Receipt: host response IDs, approval request ID, MCP call ID, server/tool identity, argument digest, source pin, skill digest, Gateway route/load fields, result digest, token usage, HSO audit and independent artifact SHA-256 read-back.

**Zero-inference preflight:** validates public HTTPS/DNS endpoints, the Auth0-compatible token exchange, MCP Streamable HTTP initialize and the exact tool list. It does not call OpenAI Responses API or test model entitlement. The live approved invocation is still required to verify the OpenAI API key/model and generate a real MCP call receipt.

**Current status:** the adapter and governance are being prepared on PR #13. The SKILL ANALYZER source contains a deployable Gateway, but its own deployment guide says a Git commit does not provision a public endpoint, OAuth client, provider key or Redis service. No live endpoint or invocation receipt has been verified here. See `docs/HSO-P0-REMOTE-MCP-SKILL-INVOCATION-PILOT.md`.

**Remote attestation limitation:** HSO verifies the local canonical submodule SHA and master SKILL.md digest, but the currently inspected Gateway response does not expose a cryptographically verifiable deployed commit/runtime skill digest. The receipt records `remote_source_attestation=NOT_EXPOSED_BY_CURRENT_GATEWAY`; it must not be promoted to a source deployment attestation.

## Production blockers

Before calling this a universal super-orchestrator, the following must be delivered and verified separately:

1. A named host adapter for ChatGPT, Claude, Gemini, Copilot or another supported runtime, with actual plugin/MCP invocation receipts.
2. A remote MCP/HTTP connector with endpoint identity, TLS, OIDC or equivalent authentication, scoped authorization, egress policy and secret-manager integration.
3. A durable shared state store with transactional leases, distributed idempotency, event replay, dead-letter queues and multi-worker concurrency controls; SQLite is not that store.
4. A trusted approval issuer, key rotation and externally enforced staging/production environment protection.
5. An immutable audit backend, independent signing/attestation, retention policy and alerting.
6. Real-target integration tests proving effect, independent read-back, rollback/compensation and failure recovery for every supported adapter.
7. Security, load, chaos, compatibility, cost and operational-runbook evidence.

Do not unlock a higher environment merely because the local sandbox passes. Advance one adapter and one target at a time.

## Ponytail engineering-method route — declared, not dispatchable

The runtime routing policy declares `plugin.engineering_method` with:
- primary owner: `ponytail-engineering-optimizer`;
- supporting specialists: `skill-developer-orchestrator` and `evaluator-team`;
- required capability: `plugin.skill.invoke`.

This separates **route selection** from **capability availability**. The HSO route resolver can identify the correct specialist and ownership boundaries, but `plugin.skill.invoke` remains `NOT_CONFIGURED` in the runtime capability registry. The runtime therefore returns a capability blocker and does not pretend to invoke Ponytail. SDO remains the source-write owner; Evaluator Team remains the independent acceptance specialist.

The private Plugin Creator release is not a runtime adapter. Before dispatch can be enabled, a named host adapter must be implemented, authenticated, authorized, probed, tested against the exact package version and independently read back. Until then, C2/C3 can provide synthetic/mock contract evidence only; C4 host activation and C5 actual plugin runtime invocation remain `NOT_RUN`.


## Vibe Coding Mentor PRD route — selected, capability-blocked

The HSO routing policy now declares `plugin.vibe_coding_mentor_prd` with:
- primary owner: `vibe-coding-mentor`;
- supporting specialists: none by default;
- action: `plugin.skill.invoke`;
- required capability: `plugin.skill.invoke`.

The route resolver can select Vibe Coding Mentor as the sole primary owner for non-IT product discovery, PRD/MVP definition and PRD-to-builder prompt compilation. The generic plugin invocation capability remains `NOT_CONFIGURED`. The runtime therefore returns `BLOCKED_CAPABILITY` before dispatch. This is deliberate fail-closed behavior, not a successful plugin invocation.

The canonical package source is the private repository `hsaidno-cpu/vibe-coding-mentor`, pinned at `84214752bb298002b96f9ff1c60e16b7a09e99d7`. 18/18 package files match the Plugin Creator release v0.1.0, and its package-contract CI passed. The source being private and verified does not itself provide an invokable HTTP/MCP endpoint.

Do not enable a VCM capability row or reuse the SKILL ANALYZER-specific Remote MCP adapter. A VCM runtime adapter requires its own named endpoint, TLS identity, OIDC/client credentials, scoped authorization, tool allowlist, secret management, timeout/rate policy, invocation receipt and independent result verification. Until those controls and a real live invocation test exist, HSO must keep returning `BLOCKED_CAPABILITY`.
