# Progressive Ecosystem Roadmap

## Latest addendum — Ponytail Engineering System, 23 November 2026

**Status:** PACKAGE_CREATED / PRIVATE / REGISTERED_ON_PR_BRANCH / HSO_ROUTE_DECLARED / PLUGIN_DISPATCH_BLOCKED

- Parent inventory on the integration branch: 23 plugin identities and 265 indexed skill records. The main branch remains unchanged until PR review and merge.
- New private package: `ponytail-engineering-optimizer`, Plugin Creator v0.1.0, release `pluginrel_6b044f37640081918df7f449298d72cf`, nine subskills.
- Canonical Git source: NOT_IDENTIFIED. Upstream Ponytail is provenance only; it is not added as a child source submodule for this derivative.
- Distribution: `snapshot_only`; package-level license clearance, public artifact and tested host adapter are not established.
- HSO route: `plugin.engineering_method` selects Ponytail as primary, SDO and Evaluator Team as bounded supporting owners; `plugin.skill.invoke` is still NOT_CONFIGURED, so dispatch is blocked.
- New Ponytail → SDO Engineering Dossier schema, synthetic example, and Ponytail → SDO C2/C3 contract passed on PR head `4474dc0aff727605bc53a6b02c161419ed272b06`, CI [run #45201188300](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/45201188300): 103 tests passed, including 15 handoff fixtures and four dossier schema/authority tests. C4/C5 remain NOT_RUN.

Historical checkpoints below are retained as records of the earlier 22-plugin baseline.


This roadmap is staged by evidence and dependencies, not by arbitrary calendar promises.

## Stage E0 — Central foundation

**Objective:** Establish the central repository, identity catalog, source provenance, responsibility matrix, governance and roadmap.

**Deliverables:** 23 plugin records; 265 indexed skill records; source/rights registry (PR #12 pending merge); five immutable source pins; architecture and responsibility boundaries; versioned handoff contracts; local validators; CI catalog gate; Notion documentation.

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

### CP-05 — Deterministic plan-only workflow compiler

**Status:** IMPLEMENTED_ON_PR_BRANCH / NOT_MERGED / NO_RUNTIME_DISPATCH

A bounded planner converts an explicitly declared work-package graph into a deterministic topological order and readiness report. It checks catalog owner identity, legacy redirects, duplicate/unknown dependencies, dependency cycles, supplied capability state/evidence, authority level and approval requirements. Upstream blockers propagate to dependent work packages.

**Artifacts:** `contracts/hso-workflow-plan.schema.json`, `tools/plan_hso_workflow.py`, `examples/hso-workflow-plan.example.json`, `docs/HSO-PLAN-ONLY-ORCHESTRATOR.md` and `tests/test_hso_workflow_planner.py`.

**Boundary:** no natural-language route inference, specialist invocation, capability probe, persistent queue/state, host adapter, runtime dispatch or side effect. The planner is a plan-validation tool, not an operational service. It remains in the open PR branch until reviewed and merged.


### Controlled Super-Orchestrator runtime pilot — 23 November 2026

**Status:** IMPLEMENTED_ON_PR_BRANCH / GITHUB_HOSTED_SANDBOX_PILOT / NOT_MERGED / NOT_PRODUCTION_READY

A real, restricted runtime has been added beside the existing plan-only compiler. It performs live discovery of registered sandbox handlers, deterministic primary-owner/specialist routing, schema-validated DAG ordering, deny-by-default authority checks, trusted adapter dispatch, bounded idempotent retry, local SQLite run-state tracking, independent target-side SHA-256 verification, conditional compensation and hash-chained audit logging.

**Acceptance evidence required from exact-head CI:** (1) create a real file in an isolated hosted-runner workspace; (2) execute its dependent verification package; (3) recover from one injected transient failure in a test-only adapter; (4) verify audit hash chains; (5) retain capability, run and target receipts as CI artifacts.

**Hard boundary:** the always-on CI workflow proves only sandbox dispatch. A distinct P0 SKILL ANALYZER Remote MCP adapter is registered but remains blocked until public endpoint/OIDC preflight and a live host invocation pass. Generic plugin dispatch, generic multi-server MCP, arbitrary APIs, child repositories, staging and production remain unavailable. SQLite is not distributed state; the local hash chain is not an independently signed immutable audit log. C4/C5 for named plugin hosts remain NOT_RUN until a live receipt is independently verified.

**Artifacts:** `tools/hso_super_orchestrator.py`, `catalog/hso-runtime-capabilities.json`, `catalog/hso-routing-policy.json`, `governance/hso-execution-policy.json`, `contracts/hso-runtime-workflow.schema.json`, runtime examples, `docs/HSO-SUPER-ORCHESTRATOR-RUNTIME.md` and the runtime regression suite.

## P0 — one-host / one-skill invocation pilot

**Status:** IMPLEMENTED_ON_PR_BRANCH / MOCK_HOST_CONTRACT_TESTED / LIVE_PAID_INVOCATION_NOT_RUN

- Host: Codex CLI 0.171.0 via codex exec, model gpt-6.2-sol.
- Target: SKILL ANALYZER 1.3.0 canonical source at pinned SHA c469af7977c9bf6dcb3f5ab7b085a6de20d87004.
- Route: one primary owner (skill-analyzer), no extra specialist for the first vertical slice.
- Access: CODEX_API_KEY plus HSO_APPROVAL_HMAC_KEY in a protected GitHub environment; manual workflow dispatch; S4 scoped five-minute receipt; first-attempt-only; single execution attempt.
- Guardrails: explicit $skill-analyzer reference, temporary copies into .agents/skills (symlink-free and hash-verified), immutable source/manifest check, read-only sandbox, ephemeral session, disabled web search, minimal environment and secret filtering; HSO-verified approver/run/nonce-hash binding included in the invocation receipt.
- Output: strict JSON schema, invocation envelope, host receipt, thread/turn IDs, CLI/model/source versions, token usage, output hash and audit receipt.
- Recovery: billable non-idempotent work; ambiguous post-dispatch failure becomes OUTCOME_UNKNOWN, not auto-replayed.

**Acceptance status:** exact-head CI [run #45209121971](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/45209121971) passed 120 tests on commit 0974efa58f0308ed87390546cadc28818bd928d2. Unit tests exercise a fake Codex CLI and verify the host protocol contract, source pin, secret filtering, schema, event receipt, HMAC approval binding and failure behaviour. They do not make a paid inference request. Live C4/C5 evidence remains NOT_RUN until the protected manual workflow is approved after the PR is accepted on main.

**Attestation limit:** current Codex CLI JSONL provides thread/turn/item events but no dedicated skill-loaded attestation that this adapter can verify. Receipt records the exact skill reference and source hash but does not rely on a model-generated self-claim as proof.

**Scope limit:** generic plugin invocation, other Agent Skills, other AI hosts, remote MCP, HTTP API, P1 gateway, P2 distributed runtime and P3–P5 controls remain separate and NOT_CONFIGURED/NOT_IMPLEMENTED.

**Artifacts:** tools/codex_skill_host_adapter.py, approval/workflow preparation scripts, runtime capability/route/policy changes, P0 output schema, manual-only workflow, P0 docs and regression tests.


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
| P0 | Resolve the 15 NOT_IDENTIFIED sources and two incomplete candidates; SDO is already pinned as an official source | Source inventory and owner decision | Accepted canonical source or explicit pending/deprecated disposition, complete manifest/tree and rights evidence |
| P1 | Verify Photo-Fixer candidate repository content | Source inspection | Correct source tree and ownership |
| P1 | Identify repository sources for remaining plugins | Source inventory | Approved source URL and provenance |
| P1 | Decide if PVEE and Video Explainer are distinct products or release generations | Source comparison | Comparative dossier and decision record |
| P1 | Complete named-host and runtime assurance for the 14 defined handoff edges | A compatible host, adapter and authorized test scope | C4 host activation and C5 runtime traces plus artifact read-back |
| P2 | Add compatible source/host test suites | E3 tools and test environment | Exact test reports |
| P2 | Define release and deprecation ownership | Governance decision | Named accountable owners and policy |

## Progress semantics

Use PLANNED, IN_PROGRESS, BLOCKED, PARTIAL, VERIFIED and ACCEPTED with evidence. A roadmap item is not complete because a document was written. Each stage requires its own exit evidence and accountable human acceptance.


## E0.1 — Instruction vault and responsibility positioning

**Status:** Central catalog, responsibility model and instruction index are merged to main. Source-level alignment and redistribution rights remain incomplete.

- Twenty-two plugin identities have explicit positioning and primary/negative routing triggers.
- A segregated instruction vault now has one directory per plugin.
- 256 installed skill definitions are indexed. Seventeen packages have complete runtime instruction bundles; three source-backed packages remain represented by canonical submodules; A.S.F.R.E.E Legacy is redirect-only.
- The catalog distinguishes canonical source, runtime snapshot, incomplete candidate and legacy redirect.
- Static validation now checks snapshot paths, counts, source classifications and routing boundaries.

**Exit evidence:** complete instruction snapshot index, per-plugin isolation, catalog validation and unit tests. This does not establish host/runtime activation.

## E1.1 — Positioning-to-source alignment

Use [PLUGIN-SOURCE-ALIGNMENT-BACKLOG.md](PLUGIN-SOURCE-ALIGNMENT-BACKLOG.md) as the single prioritized backlog. The central responsibility decisions are accepted as the parent baseline, but source-level alignment remains pending until each canonical child repository is identified and changed.

## E1.2 — Version source reconciliation

Video Explainer V4.1.12 is the target selected over installed M00 header v4.0.9. Source synchronization remains pending because the canonical V4.1.12 repository and manifest are not verified. See [VERSION-RECONCILIATION.md](../docs/VERSION-RECONCILIATION.md).


## E0.2 — People & Business Competency Academy registration

**Status:** REGISTRATION_MERGED / SNAPSHOT_VERIFIED / SOURCE_AND_RIGHTS_PENDING

- Private Plugin Creator package People & Business Competency Academy version 0.1.0; exact release pluginrel_6b039efc6dfc81919fffbe265e8f84c9.
- Nine skill procedures and a source-labelled catalog of 20 competency domains / 100 title-author references are captured in a segregated parent instruction bundle.
- Catalog and index totals are now 22 plugin identities and 256 skill records. The plugin is explicitly pending_repository; no canonical child source repository or license decision is inferred.
- This snapshot preserves the user's requested public parent-repository inventory but is not a source-of-truth repository, installable bundle from the parent, host activation proof or persistent learner tracker.
- Agent Skills Atlas remains owner of AI-capability inventory; GrowthForge remains owner of business decisions/deliverables; the Academy owns human competency development and learning-to-work transfer.

**Exit evidence:** branch content read-back, central catalog validator, unit tests and PR CI checks. Host activation, production integrations and learning outcomes require separate evidence.


## Current evidence checkpoint — 23 November 2026

**Authoritative parent snapshot:** `main` at `e967758dbfb76f98c80b5ab9e1ccee15177bbc5d` (CI run [#45155019177](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/45155019177) completed successfully).

| Dimension | Verified state | Interpretation |
|---|---|---|
| E0 — Central foundation | **PASS** | 22 plugin identities, 256 indexed skill records, five pinned source repositories, catalog/routing governance and static CI are present on main |
| E1 — Canonical source onboarding | **PARTIAL / BLOCKED** | Five pinned sources; 14 Git sources not identified; two candidates incomplete; one legacy redirect. USER/PRIVATE package inventories are not canonical Git source releases |
| E2 — Contract definition | **BASELINE ESTABLISHED / ACCEPTANCE PARTIAL** | Fourteen producer-consumer edges and versioned handoff contracts are defined |
| E3 — Integration assurance | **PARTIAL** | C0/C1 static checks pass; C2 schema and C3 mock behavior passed 14/14. C4 host activation and C5 live runtime execution remain NOT_RUN |
| E4 — Governed operations | **NOT ESTABLISHED** | Parent GitHub CI exists; no operational package registry service, installer, gateway, managed runtime, synchronization service or production observability is evidenced |
| E5 — Productization | **NOT STARTED** | No installable package is currently eligible; business/product, support and production operating model remain unapproved |

### Current source and parity baseline

- 22 plugin identities / 256 skill instruction records.
- Five official Git source repositories pinned; 14 canonical Git sources remain NOT_IDENTIFIED; Photo Fixer and PVEE remain incomplete candidates; A.S.F.R.E.E Legacy remains redirect-only.
- Exact instruction parity: Anatomi Prompt 9/9 MATCH; SKILL ANALYZER 11/12 with one drift; A.S.F.R.E.E 5/13 with eight differences; SDO 0/4 despite matching version labels; Video Explainer NOT_COMPARED because package/source files do not map one-to-one.
- Source parity is separate from redistribution rights. Current main's distribution registry records zero installable packages.

### Current change vehicle

[PR #12 — source and redistribution-rights registry](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/12) remains OPEN and NOT MERGED. Its latest head `779891f30eb27b1bd1cb19bd5e9dfce91e38746c` passed [CI run #45180949595](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/45180949595), including source/rights schema validation and 54 tests. Three review threads were addressed and resolved. Human/Code Owner review and merge remain separate gates.

### Next execution order

1. Obtain the required human/Code Owner review for PR #12; merge only after that decision.
2. Resolve canonical source ownership, repository visibility and rights for the 14 NOT_IDENTIFIED packages and two incomplete candidates.
3. Reconcile exact content for the four drifted/uncompared source-backed packages; never overwrite competing instruction bodies automatically.
4. Choose one named host, model/provider and version for a limited C4/C5 pilot only after source rights, adapter and authorization gates pass.
5. Build package artifacts, installers or a managed runtime only after the pilot establishes demand, operator ownership, permissions, rollback and security requirements.

Progress is reported by dimension and gate, not by a single weighted percentage. A merged document, indexed skill, passing mock, or completed roadmap item does not imply a live capability.
