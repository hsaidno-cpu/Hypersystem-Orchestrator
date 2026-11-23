# HSO E4/E5 Operational Platform

**Baseline:** 23 November 2026  
**Feature branch:** platform/e4-e5-operational-kernel-20261123  
**Base:** HSO super-orchestrator PR #13 head d1185fc44ce00068bee133c6a12e0f251fadca89  
**Status:** IMPLEMENTATION BASELINE / PRE-PRODUCTION / NOT DEPLOYED

## Executive decision

Use a modular monolith first: one control-plane application, one PostgreSQL database, one worker process and explicit protocol/adapter boundaries. Keep the plugin source repositories independent. Split services only after a measured bottleneck, separate trust boundary, scaling requirement or distinct operator justifies another failure domain.

This implementation is not a claim that HSO can invoke every catalog plugin. Dispatch remains disabled until a trusted host-specific adapter is implemented and verified.

## Capability map

| User need | Operational component | Current boundary |
|---|---|---|
| Persistent registry | PostgreSQL plugin/capability tables + catalog seed | Seed preserves rights as NOT_ASSESSED; it never grants execution or distribution rights |
| Persistent scheduler/state | Workflow/work-package tables, DAG validation, idempotency key, lease and polling worker | At-least-once; external adapters must deduplicate by idempotency key |
| Dispatcher/runtime broker | Explicit RuntimeAdapter interface and protocol allowlist | Empty by default, no code downloaded or imported from plugin metadata |
| Universal REST/API gateway | FastAPI versioned REST API | Scope-based auth; no public production ingress |
| MCP gateway | Streamable HTTP MCP transport | Read-only registry/status tools in v0.1 |
| Identity/access | OIDC JWT + HMAC API keys, rotation/revoke and scopes | Production requires explicit OIDC, strong secret pepper and HTTPS |
| C4/C5 assurance | C4 host/adapter evidence attestation; C5 runtime trace/output evidence required at completion | No target host has passed a pilot yet |
| Cross-plugin synchronization | Transactional outbox with leases, retries, ack/fail and dead-letter state | No approved downstream sink adapter is installed |
| Package lifecycle | Rights-gated release, digest/signature verification, entitlement and installation request | Installation is recorded as blocked until a platform adapter exists |
| Observability | Request ID logs, metrics, liveness/readiness and DB audit chain | No external WORM, SIEM, alerting or tested DR proof |
| Recovery | Expired-lease recovery, bounded retries, backup/restore scripts | Restore/failover drills and RPO/RTO are not yet evidenced |

## Operating states

Workflow package:
- PLANNED / BLOCKED / PENDING / RUNNING
- AWAITING_VERIFICATION
- SUCCEEDED / FAILED / CANCELLED

A worker does not mark its own output as accepted. It submits an output and trace; a separate reviewer holding workflow:verify must issue PASS, PASS_WITH_CAVEATS or REJECT. The primary owner cannot independently verify its own output.

Capability:
- registration starts disabled;
- C4 evidence must identify host, host version, adapter version, result and evidence reference;
- activation requires canonical source pin, execution rights CLEARED and C4_PASS;
- no capability is invoked unless its protocol has an explicit trusted RuntimeAdapter implementation.

Package:
- source pin and distribution rights must be clear;
- artifact digest and Ed25519 signature are verified;
- publishing rechecks source pin and rights;
- installation requires active entitlement and a target adapter; without it, state stays BLOCKED_ADAPTER_UNAVAILABLE.

## Security decisions

- Default development-only auth bypass is unavailable in staging/production.
- Production requires OIDC issuer/audience/JWKS, PostgreSQL, API-key pepper of at least 32 characters, Ed25519 verification public key and explicit MCP Host/Origin allowlists.
- API keys are high entropy and stored as HMAC-SHA256 keyed hashes, not raw secrets.
- Scopes are checked server-side and scope delegation cannot exceed the caller's own scopes.
- Plugin registry metadata is data, never executable code or an adapter loader.
- External capability endpoints are stored as HTTPS metadata only. No generic network invocation or URL fetch is performed by the registry.
- C4 verification is an authorized attestation record, not an automatic host probe. It becomes trusted only under the designated verifier process and external evidence.
- C5 evidence requires output locator, runtime trace reference, host, host version and adapter version.
- Audit hashes detect changed records when checked, but PostgreSQL alone is not immutable/WORM evidence storage.

## Local deployment

From repository root:

~~~bash
cd services/hso-platform
cp .env.example .env
docker compose up --build
~~~

Local API binds to 127.0.0.1:8000. Development bypass and example passwords are for local disposable environments only.

## CI acceptance

The dedicated hso-platform-ci workflow:
1. provisions PostgreSQL 18.7;
2. installs the Python 3.13 project and test dependencies;
3. compiles source/tests;
4. applies Alembic migrations;
5. seeds the real parent catalog;
6. runs operational-kernel tests.

CI is a disposable Postgres integration environment. It is not a public deployment, production security certification, host activation, or C5 proof.

## Production gates remaining

1. Human/Code Owner review and merge of the stacked PR.
2. Select a named host/version and implement one adapter with allowlisted endpoint, authentication, permission mapping, timeouts, idempotency, cancellation, trace and read-back.
3. Run C4 host discovery and C5 controlled invocation on that exact adapter/host/version; preserve evidence and independent evaluation.
4. Provision managed PostgreSQL, backups, external encrypted secret manager, OIDC provider, domain, TLS, reverse proxy, network allowlists and rate limits.
5. Add request/response redaction, log retention, metrics alerts, WORM/tamper-evident audit sink, incident routing and tested restore/failover with approved RPO/RTO.
6. Implement at least one downstream outbox sink adapter and one target platform installer adapter. Verify lifecycle idempotency, retries, rollback and operator takeover.
7. Name the operations owner, security reviewer, incident commander and recovery owner.
8. Conduct production-readiness review and release approval.

E1 source/rights debt remains independent: fourteen source identities are not identified and two source candidates remain incomplete. E3 remains partial: C2/C3 are passed for 14 synthetic/mock edges, but C4/C5 have no named-host pilot evidence.
