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

## Historical eligibility baseline — 23 November 2026

At the 23 November 2026 checkpoint, the 21 plugin identities mapped to these distribution states:

| State | Count |
|---|---:|
| review_required | 2 |
| blocked | 2 |
| private_source_restricted | 1 |
| snapshot_only | 13 |
| candidate_incomplete | 2 |
| legacy_redirect | 1 |
| **Installable** | **0** |


People & Business Competency Academy is included in snapshot_only: the Plugin Creator package is private, no canonical child source repository or independent license clearance has been established, and no public package artifact is published. This remains non-installable and is not a host/runtime activation claim.

Five source submodules are pinned, but source pinning alone is insufficient for redistribution. Examples: SKILL ANALYZER has no root license identified; A.S.F.R.E.E has PolyForm Noncommercial terms requiring distribution review; Anatomi Prompt is private and has no license cleared; Video Explainer source 4.1.9 lags deployment 4.1.12; SDO has instruction-content drift despite package version 0.1.0 matching.

## Current eligibility snapshot — 26 November 2026

The current HSO main snapshot is pinned at `a0521c896413eb2c3acdc48d67c4be43075bebe4`. The current catalog contains 23 plugin identities and the distribution registry contains the following 23 states:

| State | Count |
|---|---:|
| review_required | 2 |
| blocked | 2 |
| private_source_restricted | 1 |
| snapshot_only | 15 |
| candidate_incomplete | 2 |
| legacy_redirect | 1 |
| **Installable** | **0** |

Source ownership at the same checkpoint: 5 integrated/pinned source submodules, 15 pending repository identities, 2 candidate/incomplete source repositories and 1 canonical redirect. These are identity/source states, not the same as distribution eligibility states.

The compatibility matrix contains 15 integration edges. The current catalog-validation workflow [run 45698994293](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/45698994293) passed its 142-test unit/resolver suite, which includes the current 15-edge C2 schema and C3 mock-receiver contract coverage. All 15 edges remain `CONTRACT_TESTED`; C4 host activation and C5 runtime execution are `NOT_RUN`.

The five platform adapters remain `PLANNED`, with named-host activation and runtime evidence `NOT_RUN`. No package is installable. This is an explicit current snapshot, not a claim that a production installer or runtime gateway exists.

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
