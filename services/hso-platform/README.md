# HSO Operational Control Plane

**Version:** 0.1.0  
**Architecture:** modular monolith + persistent PostgreSQL + API process + worker process  
**Status:** IMPLEMENTED ON FEATURE BRANCH / PRE-PRODUCTION / NO HOST DISPATCH ADAPTERS

## Modules delivered

| Module | Implementation | Boundary |
|---|---|---|
| Persistent registry | PostgreSQL plugins and capabilities | Rights and provenance default to NOT_ASSESSED |
| Workflow state | PostgreSQL workflow/work-package rows | Idempotency key, DAG validation, persisted states |
| Scheduler/worker | Polling worker + FOR UPDATE SKIP LOCKED + lease | At-least-once; adapters must be idempotent |
| Handoff/state | Versioned Pydantic contracts and persisted specialist contributions | Output waits for independent verification |
| Dispatch broker | Explicit Python RuntimeAdapter protocol and registry | Empty by default; no dynamic code loading |
| REST gateway | FastAPI /api/v1 routes | Scope-based authorization |
| MCP gateway | Streamable HTTP MCP server | Read-only registry/workflow tools in v0.1 |
| Identity/access | OIDC JWT validation + HMAC API keys | Fail closed in staging/production |
| Entitlement | Subject/product/scope/expiry records | No billing provider or payment execution |
| Package/release | Source pin, distribution-rights gate, SHA-256 and Ed25519 signature checks | No artifact publication until rights cleared |
| Installer | Installation request lifecycle | BLOCKED_ADAPTER_UNAVAILABLE until a target adapter exists |
| Synchronization | Transactional outbox + lease/ack/fail REST contract | Sink adapters are not bundled/enabled |
| Audit/observability | Hash-chained events, JSON request logs, Prometheus counters, health endpoints | Not WORM and not a full tracing/SIEM stack |

## Local development

Requirements: Docker Compose v2, Git, and a shell.

~~~bash
cd services/hso-platform
cp .env.example .env
docker compose up --build
~~~

The service is bound to 127.0.0.1:8000 and should not be exposed publicly with the development defaults.

Health checks:

~~~bash
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/health/ready
~~~

OpenAPI is available at /docs in development.

## Core lifecycle

1. Seed the parent catalog/plugins.json and catalog/repositories.json.
2. Review source provenance and execution rights for each plugin. The seed operation never grants rights.
3. Register a capability using REST or MCP metadata. A registered capability is disabled.
4. Record a named-host C4 verification with an evidence reference.
5. Enable the capability only after canonical source, execution rights and C4 verification pass.
6. Submit a workflow with one primary owner and a distinct contribution contract per supporting specialist.
7. Worker claims a ready package under a time-limited lease.
8. A trusted adapter performs an at-least-once invocation using the stable package idempotency key.
9. Worker submits output into AWAITING_VERIFICATION, including output locator, runtime trace, host and adapter versions.
10. A separate reviewer with workflow:verify reviews the evidence. The primary owner cannot verify its own result.

## Identity and security

Supported authorization mechanisms:
- OIDC JWT (RS256) with fixed issuer, audience and JWKS URL.
- High-entropy API key with HMAC-SHA256 keyed hash, one-time secret display, rotation and revocation.
- Endpoint scopes are enforced server-side; callers cannot delegate scopes they do not hold.
- Staging/production require HSO_AUTH_MODE=required, HTTPS OIDC endpoints, PostgreSQL, a strong API-key pepper, explicit MCP host/origin allowlists and an Ed25519 release verification key.

The application does not store raw API keys. Only the prefix and keyed hash are stored. Do not commit .env, signing keys, tokens, or production credentials.

## Operations and recovery

- GET /health/live and /health/ready are separate checks.
- Prometheus endpoint: /metrics (requires metrics:read).
- Audit integrity check: GET /api/v1/audit/verify.
- Outbox records are claimed with a worker lease and must be acknowledged or failed. Retries are bounded; exhausted events enter DEAD.
- Expired workflow leases are recovered on worker poll. Invocation is at-least-once, not exactly-once.
- Back up PostgreSQL with scripts/backup.sh; store dump and checksum outside the database, encrypted and access controlled.
- Restore with scripts/restore.sh only to an explicitly approved recovery target. A successful dump is not a tested DR exercise.

## Important deployment gaps

This branch is not a production deployment. Before staging or production:
- Provision PostgreSQL, encrypted backup destination and secret manager.
- Configure OIDC issuer/audience/JWKS, TLS termination, DNS and MCP allowlists.
- Provision trusted signing keys and independent release signing process.
- Add rate limits, request/response redaction, retention, WORM/tamper-evident external audit sink, log/metric alerting and tested restore/failover.
- Implement and security-test actual named-host MCP/REST runtime adapters; default broker has no adapters.
- Implement actual platform installer adapters; installation remains blocked.
- Implement authorized synchronization sink adapters; outbox can be consumed but is not automatically delivered to downstream platforms.
- Execute C4 named-host and C5 runtime pilot tests with trace and artifact read-back.
- Assign accountable operator, security reviewer and incident-response owner.

Do not change the service to production mode until all required settings and operational gates are complete.
