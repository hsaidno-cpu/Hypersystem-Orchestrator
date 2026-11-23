# Modular Distribution Architecture

**Status:** Architecture and static registry baseline; no production installer or runtime gateway is claimed.  
**Revision:** 1.0.0 — 23 November 2026

## 1. Decision

Hypersystem uses a **central registry with selective distribution and independently addressable plugin modules**.

> One ecosystem. Multiple plugins. Selective installation. Unified access. Independent execution.

The parent repository owns identity, distribution eligibility, package contracts, platform adapter declarations, governance and compatibility evidence. Each plugin source repository remains canonical for its own implementation and release lifecycle.

A single repository or bundle must never be interpreted as one merged plugin. Packaging convenience does not transfer ownership, authority, versioning or internal runtime boundaries.

## 2. Required distribution modes

| Mode | Request shape | Resolution rule |
|---|---|---|
| Single | Exactly one plugin key | Resolve only that plugin and its declared requirements |
| Multi | Two or more explicit plugin keys | Resolve the selected set independently; do not silently add adjacent plugins |
| Full suite | No explicit plugin keys | Dynamically select all packages currently eligible for the target platform |
| Custom bundle | Named profile or explicit set | Resolve the exact versioned profile; retain per-plugin identity |

**Full suite does not mean all catalog rows.** It means all packages that pass the current source, license, artifact, compatibility and host-adapter gates at resolution time. Snapshot-only, candidate, blocked, private-restricted and legacy redirect identities are excluded. When no plugin is eligible, the resolver must return a blocked plan; it must not pretend to install the 20 registered identities.

The distribution registry is the eligibility authority. The plugin identity catalog remains the identity and responsibility authority. Neither file is itself an installer.

## 3. Two different hierarchies

### 3.1 Distribution/package hierarchy

- **Ecosystem:** Hypersystem Orchestrator.
- **Package envelope:** a single plugin, a custom multi-plugin bundle or a dynamic full-suite selection.
- **Plugin package:** an independently versioned, licensed, integrity-checked artifact.
- **Platform adapter:** maps the package to a target host's supported integration format.
- **Installation manifest / lock:** records requested selection and exact resolved plugin versions, source commits, artifact digests and exclusions.

A bundle is an installation envelope, not a source-code merger.

### 3.2 Runtime hierarchy

~~~text
AI Host
  └── Platform Adapter
       └── Hypersystem Gateway / Registry Client
            └── Identity + Entitlement + Authorization
                 └── Plugin Router
                      ├── Plugin A Runtime (isolated identity/version)
                      │    └── skills / tools / references / internal workflows
                      ├── Plugin B Runtime (isolated identity/version)
                      │    └── skills / tools / references / internal workflows
                      └── Plugin N Runtime (isolated identity/version)
                           └── skills / tools / references / internal workflows
~~~

For a host that supports a single application connection, the gateway may expose multiple namespaced plugin tools through one logical connection. For a host that expects separate MCP servers or plugin installations, the adapter may expose separate logical endpoints or host packages. The physical connection count is a host-adapter decision; plugin identity remains separate in either case.

## 4. One gateway, multiple logical plugin surfaces

The preferred service topology is one managed gateway with independently addressable plugin routes:

- **/mcp/<plugin-key>** — one logical plugin surface.
- **/mcp/bundles/<bundle-id>** — explicitly selected bundle surface.
- **/mcp/full-suite** — dynamically resolved eligible suite surface.

These paths are proposed route conventions, not deployed endpoints. The production gateway must enforce authorization on the server for every route and tool call. Hiding a tool in the client UI is not an access-control boundary.

A unified endpoint is optional, not mandatory. Use it only when the target host can safely represent tool namespaces, authorization context and discovery behavior. Otherwise expose separate logical servers behind the same service.

## 5. Keep four runtime states separate

| State | Meaning | What it does not imply |
|---|---|---|
| Installed | A package artifact is present in a host/workspace installation | It is enabled or authorized |
| Enabled | The user/workspace has activated the package | Every tool call is permitted |
| Authorized | An active entitlement and policy grant permit defined actions | The host can currently execute it |
| Runtime available | The target host and service can discover and invoke the verified capability | That a particular request has succeeded |

The registry must not infer one state from another. Each state needs its own source of truth and evidence.

## 6. Package eligibility gates

A plugin becomes **installable_public** or **installable_private** only when all required gates are satisfied:

1. Canonical source repository and immutable source commit are verified.
2. Source/package version and instruction-content parity are reconciled.
3. License and redistribution rights are explicitly cleared for the target distribution model.
4. A package manifest and release artifact exist, with SHA-256 integrity evidence.
5. Declared dependencies and compatibility ranges are complete and acyclic.
6. Security review and least-privilege tool/permission declarations pass.
7. A platform adapter exists and has host-activation evidence for the named host/version.
8. Installation, update, disable, uninstall and rollback behavior is tested.

Current state on 23 November 2026: **zero plugin packages are marked installable** in the initial distribution registry. Five source submodules are pinned, but source pinning alone is insufficient for redistribution. The hold states and reasons are recorded per plugin.

### Eligibility state vocabulary

- **installable_public:** all release, rights and target gates pass for public distribution.
- **installable_private:** all gates pass for private distribution and access is scoped.
- **review_required:** source exists, but a rights, parity or package-release gate remains open.
- **blocked:** a concrete source, version, rights or package blocker prevents distribution.
- **private_source_restricted:** source access is private and is not cleared for the requested distribution.
- **snapshot_only:** an instruction snapshot exists but no accepted canonical source package exists.
- **candidate_incomplete:** a possible source repository is incomplete and not canonical.
- **legacy_redirect:** compatibility alias only; resolve to its canonical product and never install as a second plugin.

## 7. Platform adapter strategy

The platform registry lists ChatGPT, Claude, Gemini CLI, VS Code/GitHub Copilot and generic MCP-compatible hosts as adapter targets. They are targets, not claims of existing adapters.

Each adapter must declare supported package and transport formats, tool naming, authentication and authorization model, host limitations, exact host/version evidence and lifecycle tests. Its support state is **planned**, **adapter_implemented**, **host_tested** or **runtime_verified**.

MCP is a useful common tool transport, not a universal plugin packaging format. Platform-specific skills, agent manifests, UI affordances, OAuth policies and execution models still require adapters. Never assume that one host's import workflow works on another host.

## 8. Authentication, entitlement and authorization

Treat these as separate controls:

- **Authentication:** establish which user, workspace, tenant or service account is calling.
- **Entitlement:** determine which plugin products the subject is allowed to access.
- **Authorization:** determine which tools/actions/scopes that subject may invoke for a specific plugin and resource.
- **Quota/policy:** enforce rate, usage, environment and risk limits.

Use OAuth/OIDC or host-managed credentials where supported. API keys are scoped service credentials, not user entitlements. Store secrets only in a credential vault or host secret manager. Never place access tokens, API keys, OAuth refresh tokens or private credentials in Git manifests, installation files, examples or Notion documentation.

## 9. Dependency, version and change control

- Child plugin versions remain independent from the ecosystem version.
- Bundles use a lockfile that pins plugin version, source commit and artifact digest.
- A parent catalog change does not silently upgrade an installed child.
- Updates are per plugin unless a dependency or compatibility rule requires a coordinated bundle update.
- Rollback is per plugin and must restore a known artifact plus its matching manifest.
- Dependencies must be explicit, version-constrained and acyclic.
- Related-plugin routing and optional handoffs are not automatically hard installation dependencies.
- Removing a plugin must not silently remove another plugin's data or configuration.

## 10. Resolver baseline

The initial CLI resolver is intentionally a **plan generator**, not an installer:

~~~bash
python tools/validate_distribution.py
python tools/resolve_distribution.py --manifest distribution/manifests/manifest.example.json
~~~

The example manifest is a dry-run multi-selection. The resolver reports each plugin's eligibility, target adapter blockers, excluded catalog rows and whether the request is ready for a future installer. It does not download, install, enable, authorize or execute anything.

A blocked result is expected today because no platform adapter has host-tested status and no plugin package has a released artifact.

## 11. Governance and acceptance

The distribution owner must reject installing an alias as an independent plugin; treating snapshots as canonical package releases; installing candidate or rights-uncleared source; merging independent plugin instructions or authority; claiming host activation based on registry presence; claiming runtime verification based on static CI; selecting every catalog identity as a Full Suite shortcut; or cross-tenant credential/entitlement leakage.

A release is accepted only with source provenance, rights evidence, immutable artifact digest, platform host/version evidence, test results, rollback instructions and a clear support owner.

## 12. Related engineering artifacts

- [Plugin identity catalog](../catalog/plugins.json)
- [Distribution eligibility registry](../catalog/distribution-registry.json)
- [Platform adapter registry](../catalog/platform-registry.json)
- [Installation manifest schema](../contracts/installation-manifest.schema.json)
- [Plugin package schema](../contracts/plugin-package.schema.json)
- [Entitlement grant schema](../contracts/entitlement-grant.schema.json)
- [Distribution resolver lock schema](../contracts/distribution-lock.schema.json)
- [Installation and runtime hierarchy](INSTALLATION-AND-RUNTIME-HIERARCHY.md)
- [Platform adapter matrix](PLATFORM-ADAPTER-MATRIX.md)
