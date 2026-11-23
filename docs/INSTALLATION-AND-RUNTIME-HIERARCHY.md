# Installation and Runtime Hierarchy

**Status:** Normative architecture contract, version 1.0.0 — 23 November 2026.

## 1. Core rule

Installing multiple plugins together must not merge their identities or responsibilities. The outer package may be one bundle or one host application entry, while every inner plugin remains an independently versioned and authorized module.

## 2. Logical layers

1. **User / Workspace Intent:** the requested plugin selection and target host.
2. **Distribution Manifest:** mode, target, plugin keys, dependency policy and version policy.
3. **Eligibility Resolver:** source, license, artifact, dependency, security and platform gates.
4. **Distribution Lock:** immutable resolved versions, source commits, artifact digests and excluded items.
5. **Platform Adapter:** host-specific packaging, configuration and authentication mapping.
6. **Gateway / Registry:** service discovery and routing, where remote execution is supported.
7. **Identity and Policy:** authentication, entitlement, scopes, quotas and tenant isolation.
8. **Plugin Router:** selects one primary plugin and only required supporting modules.
9. **Plugin Runtime:** isolated package version, tool surface, internal skills and references.
10. **Subskill / Tool Execution:** bounded work under the plugin's own authority.

The parent ecosystem controls discovery, package eligibility, platform mapping and cross-plugin handoff contracts. It does not absorb a plugin's internal source ownership.

## 3. Bundle modes

| Mode | Host-visible shape | Internal structure |
|---|---|---|
| Single plugin | One plugin entry or one MCP logical server | One independent plugin module |
| Multi-plugin bundle | One bundle entry where supported, otherwise multiple host entries | N independent modules, each separately addressable |
| Full suite | One ecosystem entry where supported | Dynamic set of all eligible modules; ineligible identities are excluded with reasons |

An adapter must not promise a single host-visible entry where the host only supports separate server registrations. Host UI presentation is not the source of truth for plugin identity.

## 4. One endpoint versus separate endpoints

A single service can host all routes. It may expose one namespaced MCP surface, individual logical MCP servers per plugin, bundle-specific logical surfaces, or separate per-host endpoints where the host's model requires it.

The gateway is a service boundary, not a monolithic plugin. Each request is authenticated and authorized before tool discovery and again before consequential actions. Tool names and returned metadata must retain plugin ownership.

## 5. Namespace and ownership rules

- Use a stable plugin_key as the canonical namespace.
- Tool identifiers exposed in a unified surface must be namespaced or mapped collision-free.
- Each tool has one owning plugin, one versioned contract and one permission declaration.
- A supporting plugin can produce a bounded handoff artifact; it cannot seize the primary plugin's final decision.
- Cross-plugin dependencies are hard only when declared in package manifests. Compatibility-matrix handoffs are not automatically installation dependencies.
- A.S.F.R.E.E Legacy resolves to A.S.F.R.E.E Canonical and is never installed as a second implementation.

## 6. Per-plugin isolation requirements

A runtime implementation must isolate, at minimum, identity and package version; configuration and secrets; tool permissions and action scopes; execution context and resource quotas; logs and trace identifiers; data ownership and retention policy; failure state, health and rollback target.

Isolation may be logical or process/container-level depending on risk and host constraints, but access-control decisions must be enforced server-side. A unified user interface must not collapse security boundaries.

## 7. Installation lifecycle

~~~text
DISCOVER
  → SELECT (single | multi | full_suite)
  → RESOLVE ELIGIBILITY
  → RESOLVE DEPENDENCIES
  → LOCK VERSIONS + SOURCE COMMITS + ARTIFACT DIGESTS
  → AUTHORIZE DISTRIBUTION
  → ADAPT TO HOST
  → INSTALL
  → ENABLE (separate user decision/policy)
  → VERIFY HOST ACTIVATION
  → VERIFY RUNTIME
~~~

Update, disable, uninstall and rollback are separate operations. They must be idempotent and scoped to the selected plugin/bundle. A failed module should not corrupt unrelated modules.

## 8. Four independent runtime states

- **installed:** package exists in the selected host/workspace.
- **enabled:** package is activated for use.
- **authorized:** current principal has a valid entitlement and action scope.
- **runtime_available:** host and backend can discover and invoke the capability.

These states must be stored and reported separately. For example, an installed-but-disabled plugin is not runtime available; an enabled plugin without entitlement is not authorized.

## 9. Failure and recovery

- **Selection failure:** report unknown plugin keys and accepted selection cardinality.
- **Eligibility failure:** list each per-plugin source/license/artifact blocker.
- **Dependency failure:** report missing, conflicting or cyclic dependencies; do not auto-select unrelated plugins.
- **Authentication failure:** stop before exposing protected tools.
- **Authorization failure:** deny the specific action and log a scoped event; do not fall back to broader credentials.
- **Adapter failure:** keep package state unchanged and provide host-specific diagnostics.
- **Partial bundle installation:** preserve successful module state, record failed modules and support per-plugin retry/rollback.
- **Runtime failure:** isolate the faulty module, preserve unrelated plugin availability and capture trace evidence.

## 10. Completion evidence

Every install/update operation must report request and lock IDs; selected and excluded plugin keys; exact package version, source commit and artifact digest; target host and exact version; installed/enabled/authorized/runtime_available state per plugin; dependency resolution; security and license decision references; test result, timestamp, operator/principal and rollback reference.

No operation is complete merely because the manifest was parsed or the package was downloaded.
