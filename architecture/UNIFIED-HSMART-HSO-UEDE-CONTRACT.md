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
