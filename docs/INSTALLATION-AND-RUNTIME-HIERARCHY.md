# Installation and Runtime Hierarchy

**Version:** 1.0.0 — 23 November 2026.  
**Status:** Normative architecture contract; runtime not yet deployed.

## Core rule

Several plugins may share one installation envelope or one host-visible application entry. They must not be merged into one plugin. Each remains independently identified, versioned, permissioned, authorized and operationally addressable.

## Logical layers

1. User/workspace intent: requested plugin set and target platform.
2. Distribution manifest: selection mode, target, plugin keys, dependency and version policy.
3. Eligibility resolver: source, license, artifact, dependency, security and platform gates.
4. Distribution lock: resolved versions, source commits, digests and excluded items.
5. Platform adapter: host-specific package, configuration and auth mapping.
6. Gateway/registry: discovery and routing where remote execution is supported.
7. Identity/policy: authentication, entitlement, scopes, quotas and tenant isolation.
8. Plugin router: selects one primary plugin and only required supporting modules.
9. Plugin runtime: isolated package version, tools, skills and references.
10. Subskill/tool execution: bounded work under its owner's authority.

## Bundle modes

| Mode | Host-visible shape | Internal structure |
|---|---|---|
| Single | One plugin entry or MCP surface | One independent plugin |
| Multi | One bundle entry where supported; otherwise multiple host entries | N independent modules |
| Full Suite | One ecosystem entry where supported | Dynamic eligible set only; exclusions reported |

Never promise one visible host entry where that host requires multiple registrations.

## Endpoint model

One service may expose a unified namespaced MCP surface, individual logical MCP servers, bundle-specific surfaces or host-specific endpoints. The gateway is a service boundary, not a monolithic plugin. Each request is authenticated and authorized; tool names and metadata retain plugin ownership.

## Namespace and isolation

- Stable plugin_key is the canonical namespace.
- Unified tool identifiers must be collision-free and retain owning plugin.
- Every tool has one owner, one versioned contract and one permission declaration.
- Supporting plugins return bounded artifacts; they do not seize the primary plugin's final decision.
- Only declared hard dependencies affect installation; compatibility handoffs are not implied dependencies.
- A.S.F.R.E.E Legacy resolves to A.S.F.R.E.E Canonical, never a second implementation.

Isolate plugin identity/version, configuration/secrets, tool scopes, execution context/quotas, logs/traces, data ownership/retention, health/failure and rollback target. Enforce access control server-side.

## Lifecycle

~~~text
DISCOVER → SELECT → RESOLVE ELIGIBILITY → RESOLVE DEPENDENCIES
  → LOCK VERSIONS / SOURCE COMMITS / ARTIFACT DIGESTS
  → AUTHORIZE DISTRIBUTION → ADAPT TO HOST → INSTALL
  → ENABLE → VERIFY HOST ACTIVATION → VERIFY RUNTIME
~~~

Update, disable, uninstall and rollback are separate scoped operations. They should be idempotent. A failed module must not corrupt unrelated modules.

## Failure handling

- Selection: report unknown keys and cardinality requirements.
- Eligibility: report each source/license/artifact blocker.
- Dependency: report missing/conflicting/cyclic dependencies; do not add unrelated plugins.
- Authentication: stop before exposing protected tools.
- Authorization: deny the scoped action; never fall back to broader credentials.
- Adapter: keep package state unchanged and provide host-specific diagnostics.
- Partial bundle install: retain successful module state and allow per-plugin retry/rollback.
- Runtime: isolate the faulty module and preserve unrelated availability.

## Completion evidence

Every future install/update operation reports request and lock IDs; selected/excluded keys; package versions, commits and digests; host/version; installed/enabled/authorized/runtime_available state per plugin; dependency results; security/license references; test evidence; timestamp/principal and rollback reference.
