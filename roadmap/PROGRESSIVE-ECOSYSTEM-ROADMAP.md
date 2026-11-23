# Progressive Ecosystem Roadmap

This roadmap is staged by evidence and dependencies, not by arbitrary calendar promises.

## Stage E0 — Central foundation

**Objective:** Establish the central repository, identity catalog, source provenance, responsibility matrix, governance and roadmap.

**Deliverables:** 21 plugin records; source registry; initial verified submodule pins; architecture and overlap arbitration; JSON schema; local validator; CI catalog gate; Notion documentation.

**Exit criteria:** unique plugin IDs and keys; every source reference has a real URL and status; all current submodule SHAs are immutable; private repository access is clearly documented; static checks pass.

## Stage E1 — Source repository reconciliation

**Objective:** Identify or create canonical source repositories for every plugin that does not yet have a verified source repository.

**Work:**
- inspect existing candidate repositories and confirm their plugin identity;
- identify source owners, visibility and license;
- find the exact canonical plugin package/skill sources and manifests;
- distinguish product source from prototypes, mirrors, unrelated app code and legacy redirects;
- create new repositories only when the owner explicitly decides the source location and license;
- pin verified sources as submodules after review.

**Exit criteria:** every registry record has a verified source repository or an explicitly accepted pending/deprecated disposition. No guessed URLs or empty placeholder submodules remain.

## Stage E2 — Canonical interface and contract layer

**Objective:** Define the minimum interfaces needed for interoperable cross-plugin handoffs.

**Work:**
- finalize plugin registration and handoff schemas;
- standardize source/version/evidence/capability metadata;
- define error, partial completion and stop states;
- build a consumer/provider matrix;
- define contract versioning and backwards-compatibility rules.

**Exit criteria:** each declared integration has an owner, contract version, dependency classification and acceptance test. No unowned final decision or unresolved dependency cycle.

## Stage E3 — Compatibility and integration assurance

**Objective:** Prove what can interoperate and where, without confusing static metadata with live capability.


**Evidence checkpoint — 23 November 2026:** C2 schema validation and C3 mock receiver contract behavior have passed for all 14 declared edges in [PR #8](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/8), commit `3bd10b5f550a3ac6994a4c4fa792e62f7513fd25`, CI [run #45149817422](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/45149817422). The matrix now records `CONTRACT_TESTED`. These are synthetic fixtures and mock receiver tests only. C4 named-host activation and C5 real runtime invocation remain `NOT_RUN`; E3 is therefore PARTIAL, not complete.


**Work:**
- static validation of manifests and package structure;
- contract tests using fixtures and mocks;
- host-specific skill discovery/routing tests;
- safe dynamic integration tests where tools and permissions exist;
- independent evaluation of outputs and error paths;
- compatibility matrix with tested host, model/provider, plugin version and commit.

**Exit criteria:** test results are reproducible and linked to exact versions/commits. NOT_RUN and BLOCKED remain visible.

## Stage E4 — Governed ecosystem operations

**Objective:** Establish the minimum operational controls justified by real usage.

**Candidate capabilities:**
- registry update automation;
- dependency drift detection;
- scheduled submodule freshness checks;
- release notes aggregation;
- compatibility and security issue routing;
- integration dashboards.

**Gate:** implement only when there is a real runtime/service and an identified operator. GitHub catalog documentation alone does not require microservices, Kubernetes or a separate orchestration backend.

## Stage E5 — Scale and productization

**Objective:** Decide whether the ecosystem becomes a distributable platform, not merely a source portfolio.

**Prerequisites:** actual demand/use cases, ownership and licensing, access control, costs, support, privacy/security model, runtime design and independent production verification.

**Exit criteria:** explicit business/product approval and tested operating model. Marketplace, billing, multi-tenancy and universal gateway features remain out of scope until justified and implemented.

## Initial priority backlog

| Priority | Work item | Dependency | Acceptance evidence |
|---|---|---|---|
| P0 | Validate central catalog and submodule pins | E0 source data | Validator and read-back |
| P0 | Reconcile Video Explainer V4.1.12 vs observed master skill header v4.0.9 | Source package discovery | Authoritative manifest and commit |
| P0 | Confirm canonical source repository for SDO and Evaluator Team | Source inventory | Repository, manifest, README and access status |
| P1 | Verify Photo-Fixer candidate repository content | Source inspection | Correct source tree and ownership |
| P1 | Identify repository sources for remaining plugins | Source inventory | Approved source URL and provenance |
| P1 | Decide if PVEE and Video Explainer are distinct products or release generations | Source comparison | Comparative dossier and decision record |
| P1 | Formalize integration and handoff contracts | E2 | JSON schemas and examples |
| P2 | Add compatible source/host test suites | E3 tools and test environment | Exact test reports |
| P2 | Define release and deprecation ownership | Governance decision | Named accountable owners and policy |

## Progress semantics

Use PLANNED, IN_PROGRESS, BLOCKED, PARTIAL, VERIFIED and ACCEPTED with evidence. A roadmap item is not complete because a document was written. Each stage requires its own exit evidence and accountable human acceptance.


## E0.1 — Instruction vault and responsibility positioning

**Status:** Central design and snapshot capture implemented in the working branch; PR review pending.

- Twenty-one plugin identities have explicit positioning and primary/negative routing triggers.
- A segregated instruction vault now has one directory per plugin.
- 247 installed skill definitions are indexed. Seventeen packages have complete runtime instruction bundles; three source-backed packages remain represented by canonical submodules; A.S.F.R.E.E Legacy is redirect-only.
- The catalog distinguishes canonical source, runtime snapshot, incomplete candidate and legacy redirect.
- Static validation now checks snapshot paths, counts, source classifications and routing boundaries.

**Exit evidence:** complete instruction snapshot index, per-plugin isolation, catalog validation and unit tests. This does not establish host/runtime activation.

## E1.1 — Positioning-to-source alignment

Use [PLUGIN-SOURCE-ALIGNMENT-BACKLOG.md](PLUGIN-SOURCE-ALIGNMENT-BACKLOG.md) as the single prioritized backlog. The central responsibility decisions are accepted as the parent baseline, but source-level alignment remains pending until each canonical child repository is identified and changed.

## E1.2 — Version source reconciliation

Video Explainer V4.1.12 is the target selected over installed M00 header v4.0.9. Source synchronization remains pending because the canonical V4.1.12 repository and manifest are not verified. See [VERSION-RECONCILIATION.md](../docs/VERSION-RECONCILIATION.md).


## E0.2 — People & Business Competency Academy registration

**Status:** PACKAGE_CREATED / PLUGIN_CREATOR_READBACK_VERIFIED / PARENT_REGISTRY_BRANCH_UPDATED / PR_AND_CI_PENDING

- Private Plugin Creator package People & Business Competency Academy version 0.1.0; exact release pluginrel_6b039efc6dfc81919fffbe265e8f84c9.
- Nine skill procedures and a source-labelled catalog of 20 competency domains / 100 title-author references are captured in a segregated parent instruction bundle.
- Catalog and index totals advance to 21 plugin identities and 247 skill records. The plugin is explicitly pending_repository; no canonical child source repository or license decision is inferred.
- This snapshot preserves the user's requested public parent-repository inventory but is not a source-of-truth repository, installable bundle from the parent, host activation proof or persistent learner tracker.
- Agent Skills Atlas remains owner of AI-capability inventory; GrowthForge remains owner of business decisions/deliverables; the Academy owns human competency development and learning-to-work transfer.

**Exit evidence:** branch content read-back, central catalog validator, unit tests and PR CI checks. Host activation, production integrations and learning outcomes require separate evidence.
