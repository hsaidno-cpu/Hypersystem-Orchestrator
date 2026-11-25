# Unified HSMART–HSO Ecosystem and UEDE Integration Contract

**Status:** Proposed architecture amendment; requires GOV-01 disposition.  
**Date:** 2026-11-25  
**Canonical HSO repository:** `hsaidno-cpu/Hypersystem-Orchestrator`  
**Related foundation repository:** `hsaidno-cpu/HSMART`

## 1. Architecture amendment

HSO and HSMART are to be treated as **one unified, mutually developing ecosystem**, while retaining separate canonical repositories and explicit implementation boundaries.

This amendment supersedes any interpretation that HSMART is merely an unrelated/adjacent platform. It does not silently rewrite previously accepted architecture decisions or merge source repositories. The change requires a recorded architecture decision and compatibility review.

- HSMART owns shared platform foundation services and governance.
- HSO owns the ecosystem capability portfolio, catalog, plugin/skill/subskill/script/agent orchestration, routing and engineering capabilities.
- UEDE is the shared autonomous development control plane that coordinates roadmap-directed development across both.
- PRE is the authoritative roadmap direction, baseline, evaluation and adaptation system.
- HSO capabilities can be selected to implement changes in either HSO or HSMART, through scoped repository workspaces and PRs.
- HSMART platform services support HSO through versioned, authenticated contracts as those services pass their own acceptance gates.

## 2. Why repositories remain separate

HSO already uses a hybrid multi-repository model: plugin source remains in each canonical child repository, while HSO centralizes ecosystem catalog, architecture, compatibility, distribution policy, governance and roadmap. HSMART is independently progressing through its own foundation milestones and has unresolved operational/acceptance gates.

A wholesale merge now would:
- blur independent source, license and release boundaries;
- couple HSO's active ecosystem engineering to unfinished HSMART foundation work;
- make HSMART's platform lifecycle and HSO's plugin lifecycle harder to validate independently;
- increase migration and rollback risk without delivering a necessary runtime benefit.

Therefore, use a hybrid/federated model. One ecosystem identity does not require one repository, one database or one deployment.

## 3. UEDE responsibilities and modules

UEDE coordinates:
1. PRE roadmap read/eligibility adapter;
2. HSO capability discovery and routing adapter;
3. task decomposition and dependency planner;
4. workflow controller and durable execution state;
5. isolated engineering worker adapter (OpenHands initially);
6. CI/test/security/quality verification coordinator;
7. evidence and roadmap reconciliation;
8. capability-gap detection and capability evolution proposals;
9. policy, approval, audit and recovery guard.

UEDE is not a new authority over PRE or HSMART security. It cannot change its own privileges, rewrite acceptance criteria, self-approve critical changes, or turn its own execution report into independent verification.

## 4. HSO capability contract

UEDE may use an HSO capability only when the catalog provides sufficient evidence for:
- canonical capability ID and source repository;
- version and immutable source/package reference;
- declared owner and responsibility boundary;
- input/output contract and compatibility;
- execution host/runtime requirements;
- permissions, secrets and data classification;
- source/license/rights and distribution status;
- verification status, acceptance evidence and known blockers.

Catalog presence, instruction snapshot, submodule pin, successful static test or sandbox result are not proof of live host activation or production execution. NOT_IDENTIFIED, snapshot_only, rights_uncleared, NOT_CONFIGURED, NOT_RUN and NOT_VERIFIED states must remain explicit blockers.

HSO remains the owner of plugin identities and child source pointers. UEDE must not copy private plugin instructions or child source into HSMART merely to make a task executable.

## 5. PRE contract

UEDE reads a specific PRE roadmap ID and revision, including approved scope, objectives, work items, dependency graph, priorities, risk, acceptance criteria and approval rules.

Execution updates are evidence facts: branch, commit SHA, PR, CI run, test result, review disposition, blocker and artifact reference. Any strategic replan or baseline/acceptance change must be proposed as a new PRE revision and pass its designated authority. No invented progress or implicit acceptance.

## 6. Runtime and FLOSS selection

Initial candidate runtime:
- Kestra (Apache-2.0) for event/schedule-driven workflow orchestration.
- OpenHands (MIT) as an isolated engineering worker.
- LangGraph (MIT) only if stateful multi-step reasoning needs justify it.
- GitHub Actions for exact-head repository validation.

These are replaceable runtime integrations. They do not own HSO's canonical catalog, PRE state, HSMART policy, identity or audit authority. Deployment and live integration are not yet claimed.

## 7. Autonomy stages

- A0 Observe: read-only roadmap, catalog, repository and CI observation.
- A1 Prepare: task decomposition, execution brief, test plan and proposed changes.
- A2 Execute: isolated branch/workspace, scoped changes, tests and draft PR.
- A3 Controlled delivery: only pre-authorized low-risk merge/release after all required gates.
- A4 Critical governance: human approval required for identity, access, secrets, audit, protected branches, production, destructive migrations and roadmap baseline/acceptance changes.

Start at A0/A1. A2 must begin with one synthetic task and one end-to-end acceptance test. Do not enable broad autonomous merge.

## 8. HSO implementation obligations

- Maintain the canonical capability catalog and accurate readiness states.
- Expose a versioned capability-discovery interface suitable for UEDE.
- Expose invocation only for capabilities with verified host/runtime contracts.
- Keep plugin source ownership, provenance, rights and version pins intact.
- Provide repository/task adapters without bypassing HSMART policy boundaries.
- Record compatibility and execution evidence; distinguish plan-only, sandbox, host-live and production states.
- Preserve existing PR sequencing and governance constraints; UEDE architecture work must not be used to bypass unrelated open PR gates.

## 9. HSMART integration obligations

HSMART remains canonical for its foundation services, policy and identity contracts. HSO/UEDE integrations must use accepted APIs and least-privilege credentials. Until a HSMART service is operational and accepted, UEDE must use an explicitly marked adapter stub/read-only mode or a separately approved temporary integration; it must not assume a planned gateway, registry, runtime, secret vault or audit service is live.

## 10. Initial acceptance path

1. Inventory PRE roadmap schema and exact revision.
2. Inventory HSO catalog readiness and invocation evidence.
3. Define versioned UEDE task and execution receipt schemas.
4. Implement read-only PRE and HSO adapters.
5. Test dependency eligibility and capability selection.
6. Add Kestra adapter for deterministic workflow execution.
7. Add OpenHands adapter for one isolated synthetic repository task.
8. Run repository CI and verification on exact PR head.
9. Record evidence and proposed roadmap status without self-accepting milestone completion.
10. Obtain GOV-01 disposition before enabling broader execution.

## 11. Compatibility with existing HSO operating model

This contract does not replace HSO's existing central ecosystem repository model, plugin ownership rules, plan-only workflow planner, sandbox runtime, source rights controls, compatibility matrix, or existing PR governance. It adds a cross-ecosystem development responsibility and a versioned integration boundary.

The HSO repository's existing statement that HSMART is only a "related but separate platform" must be interpreted as historical repository separation, not ecosystem independence. The intended state is separate source repositories within one ecosystem.

## 12. Explicit non-claims

This document does not claim:
- that UEDE is deployed;
- that PRE has a live shared API/runtime;
- that HSMART platform services are all operational;
- that generic HSO plugin invocation works in live hosts;
- that Kestra or OpenHands is deployed or connected;
- that any HSMART/HSO roadmap item is completed;
- that the repositories have been merged.

**Recommended architecture:** hybrid/federated repositories, shared ecosystem identity, UEDE modular control plane, HSMART platform services, HSO capability supply, PRE roadmap authority, replaceable FLOSS workflow/engineering runtimes.


## 13. UEDE P0–P9 delivery contract and existing-gate alignment

This order is the single authorized UEDE workstream. UEDE orchestrates the existing HSMART, HSO, PRE, GitHub and Notion authorities; it must not create a parallel roadmap, merge lane, catalog, approval ledger or shadow runtime.

| Priority | Deliverable | Contract boundary | Exit evidence |
|---|---|---|---|
| P0 | Review/establish architecture in HSMART PR #32 and HSO PR #25 | Documentation and contract reconciliation only; draft until owner disposition | Cross-repo consistency, exact-head checks, preserved PR graph and exact-head GOV-01 decision |
| P1 | Audit all HSO capabilities that can develop HSMART/HSO | Read-only audit of owner, source, version, skill, rights, parity, host, permissions, invocation status and tests | Capability readiness ledger distinguishes design/snapshot/source/rights/host/invocation states |
| P2 | Audit PRE schema/API/runtime | Read-only inspection of PRE specification, actual roadmap source, transition queue, Mission Control mappings, endpoint and deployment evidence | PRE source-of-authority map, schema/revision inventory and explicit NOT_DEPLOYED/NOT_CONFIGURED states |
| P3 | Define UEDE Core Contracts and adapter interfaces | Versioned contract files/schemas in owning repositories; no schema migration yet | Contract tests, compatibility rules, event/versioning model and authority mapping |
| P4 | PRE Read-only Adapter | Read-only, source-pinned, complete and digest-bound snapshot reader | Reproducible read of an approved roadmap revision, pagination completeness, freshness and no-mutation tests |
| P5 | HSO Capability Discovery Adapter | Read-only adapter over catalog, instruction, rights, distribution, compatibility and runtime readiness | Deterministic capability descriptors with source/version/rights/host/permission/evidence fields |
| P6 | Deterministic task planner | Extend the existing plan-only HSO planner; it remains the only canonical planner | Stable ordering and explicit blocker reasons; no execution side effects |
| P7 | Kestra + OpenHands adapters | Replaceable orchestration/worker integrations; disabled by default and isolated | Retry, idempotency, cancellation and recovery tests; one bounded worker task without approval or production authority |
| P8 | One end-to-end autonomous engineering workflow | Synthetic target only, no production/HSMART foundation write | PRE read → HSO discovery → plan → worker → exact-head CI → artifact read-back → evidence receipt → GOV-01 decision |
| P9 | Progressive autonomy | Risk-based enablement only after P8 evidence | Per-tier policy, rollback, cost/resource caps, observability and explicit owner authorization |

### 13.1 Audited readiness baseline (2026-11-25)

The HSO parent catalog contains 23 plugin identities and 265 indexed skill definitions. Neither metric is an execution count. Capability eligibility is the intersection of source provenance, rights, current instruction parity, version, host adapter, permissions, tests and exact execution evidence.

| Capability | Source/skill evidence | Rights/parity status | UEDE eligibility |
|---|---|---|---|
| SDO | Canonical SPDO source v0.1.0, one master skill | Apache-2.0; source/package version aligned, but 0/4 instruction files exactly match | Candidate skill/plugin engineering worker after parity remediation; no assumed HSMART code runtime |
| A.S.F.R.E.E | Canonical private source v0.5.0-rc.1, 13 skills | PolyForm Noncommercial; package 0.3.2 is behind and instruction drift is recorded | Technical forensics/repair/QA only within non-commercial rights and after parity review |
| SKILL ANALYZER | Source v1.3.0, 12 skills | No source license declaration; package v1.0.0 behind and instruction drift | Analytical/evidence support only; no generic invoke authority |
| Plugin Agent Orchestrator | 44 indexed skills, including code/test/runtime/security | Canonical source repo not identified; platform-only snapshot | Not executable or eligible for autonomous dispatch |
| Ponytail Engineering System | 9 indexed skills for software engineering/review method | Canonical source repo not identified; no write/commit/PR ownership | Method reference only |
| PRE | v0.1.1 spec, 1 master + 8 specialists, 32 behavioral specs | Canonical source repo not identified; license undeclared; shared runtime not deployed | Roadmap contract, not an available runtime or capability invoker |

The existing HSO plan-only planner can validate owners, capability states, authority, approvals and dependency DAGs. The controlled runtime proves only the allowlisted sandbox actions `sandbox.write_text` and `sandbox.verify_sha256`. Generic `plugin.skill.invoke` and `mcp.remote.invoke` remain NOT_CONFIGURED. A plugin identity, instruction snapshot or mocked Remote MCP test does not establish a live host invocation.

### 13.2 PRE and Mission Control observed state

- PRE is recorded as package/specification v0.1.1 with 1 master skill, 8 specialists and 32 behavioral acceptance specifications. Package structure/schema/local tests are not equivalent to executing the 32 behavioral cases.
- PRE's independent canonical Git repository is NOT_IDENTIFIED; its license is NOT_DECLARED; shared runtime and capability-learning federation are SPECIFIED_NOT_DEPLOYED.
- HSO Master Roadmap & Milestones is the currently observed Notion roadmap source with 20 records and R0–R9 lifecycle, approval, dependency, gate and evidence fields. Its record revision and source completeness must be captured by the adapter before planning.
- HSO Supabase contains Mission Control tables, not an independently deployed PRE database. Five source registrations are marked `not_configured`; `hso_work_items` contains zero imported records; no successful synchronization timestamp or complete snapshot is present.
- Existing PRE transition policy work on PR #17 is a gated queue-evaluation slice. It does not provide the read-only roadmap adapter, does not run engineering tests, and does not mutate canonical Work Item PRE Stage. It remains subject to PR #15 dependency and live activation blockers.

### 13.3 Existing PR/KM gate interlock

1. UEDE is not a new PR train. Its changes must be placed in HSMART or HSO according to source ownership and must respect the current PR base/dependency graph.
2. HSO PR #15 and its upstream corrective/security findings remain a prerequisite in the existing HSO merge sequence. PR #24, PR #16 and PR #17 remain stacked on the #15 branch and cannot be silently retargeted or merged early. Existing PR descriptions and PRE records must be reconciled to the owner's latest explicit sequence before any base change.
3. HSMART KM 0 remains OPEN and KM 1 remains IN_PROGRESS in the latest project record. KM 2+ remain BLOCKED pending formal KM 1 acceptance. HSMART PR #30/#31 remain independent changes and are not absorbed into UEDE.
4. PR #32 and PR #25 remain architecture proposals until their exact-head checks and GOV-01 decision pass. Their documentation cannot authorize code execution, merge, migration, production deployment or KM advancement.
5. GOV-01 is the sole human approval authority. No second human engineering reviewer or separate human security approver is required. Automated review, security analysis, AI assurance, regression tests and exact-head evidence are technical inputs, never a substitute for GOV-01 and never a fabricated GitHub-native APPROVED review.
6. The PR #25 baseline currently has a compatibility-matrix unit assertion conflict: the test expects `INTERFACE_DEFINED_NOT_EXECUTED` while the matrix records `CONTRACT_TESTED`. Do not edit the matrix or assertion to force a green check without reconciling the approved baseline and source evidence.
7. HSMART services remain unavailable to UEDE until each service has passed its own KM/acceptance and live contract test. No planned gateway, identity, policy, secrets, runtime or audit service may be treated as provisioned.

### 13.4 Adapter and execution rules

**PRE Read-only Adapter**
- Reads only an owner-authorized source and returns a typed roadmap snapshot with source ID, exact revision/observation time, schema version, pagination completion, canonical payload digest and freshness.
- Fails closed on partial pages, duplicate identifiers, missing approval/baseline state, ambiguous source authority, stale revision or changed content during a read.
- Cannot write PRE Stage, approval, scope, priority, baseline, acceptance criteria or progress.
- Until a shared PRE API exists, any Notion bridge must explicitly identify itself as a read-only Notion source adapter, not a live PRE API implementation.

**HSO Capability Discovery Adapter**
- Reads the canonical catalog, skill index, source-rights, compatibility/distribution and runtime readiness records.
- Returns capability ID, owner, source repository, immutable commit, source/package versions, instruction parity, license/rights, host, permission scope, risk, tests, freshness and evidence.
- Treats NOT_IDENTIFIED, rights-uncleared, instruction-drifted, NOT_CONFIGURED, NOT_RUN and NOT_VERIFIED as blockers.
- Does not execute a skill or claim invocation readiness.

**Deterministic Task Planner**
- Extends the existing plan-only planner, rather than creating a second engine.
- Computes a stable topological plan from one immutable roadmap snapshot and one capability inventory digest.
- Blocks dependency cycles, unknown work items, stale/partial sources, unresolved scope/approval, unsupported host, missing rights and missing acceptance evidence.
- Emits a canonical plan digest and blocker list; does not dispatch jobs.

**Kestra/OpenHands**
- Kestra owns workflow state, schedule, retry, timeout and cancellation only.
- OpenHands receives a disposable workspace, one task-specific branch, minimal repository-scoped short-lived credentials and explicit resource/network limits.
- The worker cannot read production secrets, modify approval policies, change protected branches, edit the PRE baseline, approve itself or merge.
- GitHub Actions remains the authoritative repository CI evidence. Every test must bind to the exact candidate commit SHA.

### 13.5 Stop conditions and P0 exit

Execution stops whenever the approved PRE revision cannot be proven; source pagination is incomplete; dependency, scope or approval is unresolved; a capability lacks canonical source/rights/host evidence; a KM/PR gate is unmet; credentials exceed the declared scope; exact-head CI is absent/stale; or evidence reconciliation disagrees with the source.

**P0 is complete only when** PR #32 and PR #25 describe the same authority model and staged sequence, their exact-head checks pass, the current PR/KM graph remains unchanged, and GOV-01 records the decision against the final exact heads. Architecture acceptance does not itself merge either PR or activate runtime.
