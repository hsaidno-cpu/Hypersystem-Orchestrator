# HSO Super-Orchestrator — Controlled Runtime v0.1

**Status:** IMPLEMENTED_ON_PR_BRANCH / SANDBOX_RUNTIME_VERIFICATION_PENDING_CI / NOT_MERGED / NOT_PRODUCTION_READY  
**Scope:** capability discovery, route arbitration, policy enforcement, DAG execution, bounded retry, idempotency, target read-back, compensation and hash-chained audit.

## What is actually executable

The file tools/hso_super_orchestrator.py is a real Python execution engine. GitHub Actions runs it on an isolated hosted runner. The registered built-in adapter creates a new file inside a dedicated temporary workspace; the independent verifier reopens that file and checks its SHA-256 digest. A test-only adapter injects one transient fault so CI can observe retry and recovery.

This is real runtime execution against a real sandbox target. It is **not** proof of calling a ChatGPT plugin, remote MCP server, external API, child repository, staging or production. The runtime reports plugin and MCP dispatch as NOT_CONFIGURED.

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
