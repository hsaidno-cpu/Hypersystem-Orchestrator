# Modular Distribution Architecture

**Status:** Architecture and static registry baseline. No production installer or runtime gateway is claimed.  
**Revision:** 1.0.0 — 23 November 2026.

## Decision

Hypersystem uses a **central registry with selective distribution and independently addressable plugin modules**.

> One ecosystem. Multiple plugins. Selective installation. Unified access. Independent execution.

The parent repository owns identity, distribution eligibility, package contracts, platform adapter declarations, governance and compatibility evidence. Each child repository remains canonical for its own implementation and release lifecycle. Packaging convenience never transfers source ownership, authority, versioning or runtime boundaries.

## Distribution modes

| Mode | Request shape | Resolution |
|---|---|---|
| Single | Exactly one plugin key | Resolve only that plugin and declared hard dependencies |
| Multi | Two or more explicit keys | Resolve each selected plugin independently |
| Full Suite | Empty explicit plugin list | Dynamically select all packages eligible for the target platform |
| Custom Bundle | Explicit profile or set | Resolve a versioned profile; retain per-plugin identity |

**Full Suite does not mean all catalog rows.** It means every package that passes source, version/parity, license, artifact, dependency, security and host-adapter gates at resolution time. Snapshots, candidates, blocked packages, private-restricted packages and legacy redirects are excluded. If none is eligible, resolution must be BLOCKED.

The plugin catalog is the identity/ownership authority. The distribution registry is the eligibility authority. Neither is an installer.

## Package hierarchy versus runtime hierarchy

Distribution hierarchy:

- Ecosystem: Hypersystem Orchestrator.
- Package envelope: one plugin, custom bundle or dynamic Full Suite.
- Plugin package: independently versioned, licensed and integrity-checked artifact.
- Platform adapter: maps the package into a host's supported format.
- Installation manifest/lock: records request and exact resolved versions, source commits, digests and exclusions.

Runtime hierarchy:

~~~text
AI Host
  └── Platform Adapter
       └── Hypersystem Gateway / Registry Client
            └── Identity + Entitlement + Authorization
                 └── Plugin Router
                      ├── Plugin A Runtime (isolated identity/version)
                      │    └── skills / tools / references / workflows
                      ├── Plugin B Runtime (isolated identity/version)
                      │    └── skills / tools / references / workflows
                      └── Plugin N Runtime (isolated identity/version)
                           └── skills / tools / references / workflows
~~~

One host-visible application may contain several plugin modules if the host supports that shape. Another host may require separate MCP server registrations or native package entries. The adapter decides the physical connection shape. Plugin identity must remain separate.

## Unified gateway, logical plugin surfaces

Preferred topology: one managed gateway service with independently addressable plugin surfaces. Proposed routes (not deployed):

- /mcp/plugin-key
- /mcp/bundles/bundle-id
- /mcp/full-suite

A unified endpoint is optional, not mandatory. Use it only if the host supports safe tool namespacing, discovery and authorization context. Otherwise expose several logical servers behind the same gateway service.

Authorization must be enforced server-side during discovery and each tool call. Hiding a tool in client UI is not a security boundary.

## Four separate runtime states

| State | Meaning |
|---|---|
| Installed | Package artifact is present in the host/workspace |
| Enabled | User/workspace activated the package |
| Authorized | Principal has valid entitlement and action scopes |
| Runtime available | Host/backend can discover and invoke the verified capability |

No state implies another. Each requires its own source of truth and evidence.

## Current eligibility baseline

As of 26 November 2026 the 24 plugin identities map to these distribution states. The current instruction snapshot registry contains 279 skill records across these 24 identities (capture date 2026-11-26). Source ownership states are 5 integrated submodules, 16 pending Git source identities, 2 candidates and 1 canonical redirect. The newly registered Executive Workday Orchestrator is a USER/PRIVATE package pointer with 14 private instruction files but no canonical child Git source; it remains pending_repository and snapshot_only.

| State | Count |
|---|---:|
| review_required | 2 |
| blocked | 2 |
| private_source_restricted | 1 |
| snapshot_only | 16 |
| candidate_incomplete | 2 |
| legacy_redirect | 1 |
| **Installable** | **0** |


People & Business Competency Academy, Ponytail Engineering System, Progressive Roadmap Evaluator and Executive Workday Orchestrator are among the snapshot_only records: each has a private or incomplete package/source boundary, no fully eligible public release artifact and unresolved release or rights evidence. EWO specifically has a verified USER/PRIVATE Plugin Creator package 0.1.0, but no canonical child source repository, independent license clearance, public artifact or host-tested adapter. It remains non-installable and is not a host/runtime activation claim.

Five source submodules are pinned, but source pinning alone is insufficient for redistribution. Examples: SKILL ANALYZER has no root license identified; A.S.F.R.E.E has PolyForm Noncommercial terms requiring distribution review; Anatomi Prompt is private and has no license cleared; Video Explainer source 4.1.9 lags deployment 4.1.12; SDO has instruction-content drift despite package version 0.1.0 matching.

Eligibility states:
- installable_public / installable_private: all gates pass.
- review_required: rights, parity or package-release gate remains open.
- blocked: concrete source/version/rights/package blocker.
- private_source_restricted: private source not cleared for requested distribution.
- snapshot_only: instructions only, no canonical source package.
- candidate_incomplete: candidate repository is not a complete canonical package.
- legacy_redirect: redirect only; do not install as a second plugin.

## Required release gates

1. Canonical source identity and immutable commit verified.
2. Source/package version and instruction-content parity reconciled.
3. License and redistribution rights cleared for the target distribution model.
4. Package manifest and release artifact published with SHA-256 digest.
5. Dependencies complete, version-constrained and acyclic.
6. Security review and least-privilege permissions pass.
7. Platform adapter exists and has named host/version activation evidence.
8. Install, update, disable, uninstall and rollback tested.

## Platform adapter strategy

Targets recorded in the platform registry: ChatGPT, Claude, Gemini CLI, VS Code/GitHub Copilot and generic MCP hosts. All are currently PLANNED; host activation and runtime execution are NOT_RUN.

The compatibility matrix records 15 plugin handoff edges as of this snapshot. Current C2 schema and C3 mock receiver tests pass for all 15 edges in catalog validation run 45699714030; C4 host activation and C5 runtime remain NOT_RUN. This matrix does not include EWO as a plugin-to-plugin handoff; EWO has a separate private routing-contract catalogue.

MCP is a common tool transport where supported, not a universal plugin package format. Native skills, agent manifests, hooks, UI, auth policies and lifecycle still need host-specific adapters. Adapter records must specify supported formats/transports, exact host/version, tool namespace mapping, auth/entitlement policy, secret references, lifecycle operations and test evidence.

## Authentication, entitlement and authorization

- Authentication identifies a user, workspace, tenant or service account.
- Entitlement determines which plugin products a principal may access.
- Authorization determines which tools/actions/scopes are allowed for a plugin/resource.
- Quota/policy controls rate, usage, environment and risk boundaries.

Use OAuth/OIDC or host-managed credentials where supported. API keys are scoped service credentials, not user entitlements. Secrets belong in a secret manager or credential vault, never in Git manifests or documentation.

## Version and lifecycle rules

- Child plugin versions remain independent from the ecosystem version.
- Bundle lockfiles pin child version, source commit and artifact digest.
- Parent catalog changes do not silently upgrade installed children.
- Updates and rollbacks are per plugin unless a hard dependency requires coordinated change.
- Compatibility handoffs are not automatically hard installation dependencies.
- Uninstalling one plugin must not silently remove another plugin's data/configuration.

## Resolver baseline

The new resolver generates a dry-run plan only. It does not download, install, enable, authorize or execute packages.

~~~bash
python tools/validate_distribution.py
python tools/resolve_distribution.py --manifest distribution/manifests/manifest.example.json
python -m unittest discover -s tests -v
~~~

A blocked result is expected until installable package artifacts and host-tested adapters exist.

## Acceptance and governance

Reject installing a legacy alias as an independent plugin; treating snapshots as canonical releases; distributing rights-uncleared or incomplete source; merging plugin instructions/authority; claiming host activation from registry presence; or claiming runtime verification from static CI.

Release acceptance requires provenance, rights evidence, immutable artifact digest, exact host/version evidence, tests, rollback procedure and accountable support ownership.
