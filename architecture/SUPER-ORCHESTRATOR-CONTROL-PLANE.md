# Hypersystem Orchestrator — Super-Orchestrator Control Plane

**Document status:** ARCHITECTURE_BASELINE / CONTROL_PLANE_SPECIFIED / RUNTIME_NOT_DEPLOYED  
**Checkpoint:** 23 November 2026  
**Main evidence baseline:** `e967758dbfb76f98c80b5ab9e1ccee15177bbc5d`  
**Parent repository:** `hsaidno-cpu/Hypersystem-Orchestrator`

> This document defines the intended ecosystem-level operating contract for Hypersystem Orchestrator (HSO). It does not claim that a hosted dispatcher, installer, API/MCP gateway, shared runtime, or autonomous multi-agent service has been deployed.

## 1. Executive decision

Hypersystem Orchestrator is the **ecosystem-level control plane** for a governed portfolio of independently maintained plugins, skills, agents, and workflow systems.

It is not an additional domain-specialist plugin. It is the parent coordination layer that discovers registered capabilities, chooses one primary owner for each work package, plans explicit handoffs, enforces common evidence and authority rules, aggregates verified results, and records lifecycle state.

The architecture remains:

**Hybrid multi-repository + central ecosystem repository.**

- Each child plugin repository remains canonical for its own implementation, manifest, instructions, tests, license, version, and release history.
- The HSO parent repository remains canonical for ecosystem identity, source pins, responsibility boundaries, shared contracts, compatibility, governance, distribution eligibility, and cross-plugin progress.
- Notion is the knowledge, decision, roadmap, and navigation layer. It does not replace GitHub as engineering source of truth.
- Platform hosts and runtimes are separate execution environments. Registration or a passing mock test does not activate them.

**Key architectural rule:** one ecosystem control plane, one primary decision owner per work package, multiple explicitly bounded specialists when necessary, and no implicit transfer of authority between them.

## 2. Current verified baseline and implementation boundary

The inspected `main` baseline contains:

| Indicator | State at baseline |
|---|---:|
| Plugin identities | 22 |
| Indexed skill instruction records | 256 |
| Official source repositories pinned | 5 |
| Canonical Git sources not identified | 14 |
| Incomplete source candidates | 2 |
| Legacy redirect identities | 1 |
| Installable packages | 0 |
| Declared producer-consumer edges | 14 |
| C0/C1 | Static validation present |
| C2 schema tests | PASS, 14/14 |
| C3 mock receiver behavior | PASS, 14/14 |
| C4 named-host activation | NOT_RUN |
| C5 real runtime execution | NOT_RUN |

C2/C3 evidence is synthetic schema and deterministic mock-receiver assurance. No claim of real plugin invocation, host activation, package installation, production gateway, or runtime interoperability follows from those tests.

The parent can coordinate and validate repository-level work now. Runtime dispatch must remain **specified but unavailable** until an actual adapter, host, permission scope, executable package, and read-back evidence exist.

## 3. System boundary

### 3.1 HSO owns ecosystem coordination

HSO owns these cross-ecosystem concerns:

1. Request intake, objective clarification, scope, constraints, and stop conditions.
2. Catalog and source-provenance lookup.
3. Version, rights, dependency, and distribution-eligibility checks.
4. Selection of one primary plugin owner and any necessary supporting specialists.
5. Dependency ordering, work-package planning, and handoff construction.
6. Shared contract validation, evidence aggregation, and lifecycle state.
7. Ecosystem-level risk, blocker, compatibility, and roadmap reporting.
8. Parent-repository change governance and synchronization records.

### 3.2 HSO does not replace specialist owners

| System | Final responsibility | HSO relationship |
|---|---|---|
| SKILL ANALYZER | Selects general analytical methodologies and evaluates analytical assumptions | Supplies method blueprints when the problem needs analytical methods |
| A.S.F.R.E.E | Owns technical anatomy, forensic decomposition, and supervised reconstruction of AI/software systems | Supplies the technical case dossier; M00 remains its only case-level coordinator |
| Anatomi Prompt V3 — Octa-Prompt | Owns eight-pillar prompt architecture and structural prompt assurance | Receives prompt requirements or reconstructed prompts when structural hardening is needed |
| AI Prompt Finder & Creator | Owns source-content/reference analysis and content-to-prompt reconstruction | Supplies observation/inference/unknown maps and reconstructed prompt artifacts |
| Evaluator Team | Owns independent evaluation, scoring, findings, and acceptance recommendations | Supplies independent judgement; HSO cannot convert its own coordination status into an approval |
| Skill Developer Orchestrator (SDO) | Owns the engineering lifecycle for skill/plugin source changes, tests, PRs, and release preparation | Receives accepted requirements and produces controlled engineering evidence |
| AI Workflow Systems Orchestrator (WSO) | Owns reusable workflow, SOP, modular skill, and process architecture | Designs the workflow mechanics that HSO may adopt; WSO does not own ecosystem catalog truth |
| Progressive Roadmap Evaluator (PRE) | Owns roadmap-specific intake, baseline, milestones, progress evaluation, adaptation, and closure | Receives roadmap work and provides milestone/gate state; HSO does not create a competing roadmap state machine |
| Plugin Agent Orchestrator | Owns the design and lifecycle of AI-agent products and their runtime | Receives agent-specific architecture or operations work; it is not the parent plugin source controller |
| HSMART | Separate platform project for universal AI ecosystem infrastructure | Related platform only; no implicit source, runtime, governance, or service dependency is assumed |

The same distinction applies to domain-truth owners. For example, PVEE owns approved health claims and Fact Lock; Video Explainer owns technical production compilation after that approval. HSO cannot silently promote technical QA into health, legal, clinical, or publication approval.

### 3.3 Non-goals

HSO does not:

- absorb child source code into a monorepo;
- duplicate every specialist as another HSO subskill;
- invent runtime capability from an instruction snapshot;
- bypass source-owner permissions, licensing, or human approval;
- automatically publish, redistribute, install, enable, authorize, or execute every catalog entry;
- create microservices, Kubernetes infrastructure, or an MCP gateway merely to make the architecture look more advanced.

## 4. Logical control-plane responsibilities

The following are **logical responsibilities**, not separate deployed microservices or newly registered plugins.

| Component | Responsibility | Minimum output | Current implementation state |
|---|---|---|---|
| CP-01 Intake & Scope Gate | Define requested outcome, target, scope, non-goals, constraints, and stop rules | Request/case brief | Partially represented in governance and handoff contracts |
| CP-02 Catalog & Provenance Resolver | Resolve plugin identity, source state, version, commit, license and instruction provenance | Capability/source record | Catalog, repository registry and snapshots exist |
| CP-03 Eligibility & Capability Gate | Check actual source, rights, artifact, dependency, host, permission and runtime availability | Eligibility/capability decision | Live probes for registered sandbox handlers; plugin/MCP remain NOT_CONFIGURED |
| CP-04 Route Arbitration | Choose one primary owner and only the specialists needed for distinct outputs/controls | Route receipt | Explicit task-type route registry; unknown routes fail closed |
| CP-05 Plan & Dependency Coordinator | Validate a DAG and execute authorized packages through registered adapters | Plan + execution receipt | Plan compiler plus serial sandbox DAG dispatcher on PR branch; no distributed scheduler/queue |
| CP-06 Handoff & State Manager | Validate workflow envelope, dependency outcomes, idempotency and replay safety | Versioned run receipt + local idempotency ledger | Runtime schema + SQLite single-runner ledger; no distributed transactional state |
| CP-07 Evidence & Quality Gate | Independently read back target state and judge acceptance evidence | Target verification receipt | Real sandbox SHA-256 read-back in CI; plugin-host C4/C5 remain NOT_RUN |
| CP-08 Roadmap & Change Bridge | Hand longitudinal progress and adaptation decisions to PRE; hand source changes to SDO | Roadmap update / engineering change manifest | Procedural integration only; no cross-plugin event service |
| CP-09 Governance & Observability | Record route, policy, attempts, retry, result, verification, compensation and closure | Hash-chained run audit + receipt | JSONL hash chain and CI artifact; no external immutable/WORM audit service |

Do not split these logical responsibilities into independent agents, services, or subskills until an observable bottleneck, repeated use case, clear interface, owner, and acceptance test justify the additional failure domains.

### CP-05 implementation: plan-only workflow compiler

The parent now includes a deterministic plan-only workflow planner, its versioned JSON input contract, a worked example and regression tests:

- `contracts/hso-workflow-plan.schema.json` defines the declared work-package input shape.
- `tools/plan_hso_workflow.py` validates plugin ownership against the catalog, rejects legacy redirects and unknown owners, checks dependency references/cycles, computes a stable topological order, checks declared capability evidence, action-authority level and approval state, and propagates upstream blockers.
- `examples/hso-workflow-plan.example.json` demonstrates an explicitly declared three-stage plan.
- `tests/test_hso_workflow_planner.py` covers schema shape, routing identity, dependency integrity, authority, approval and dispatch boundaries.

This closes the planning/compiler gap only. It does not select owners from free text, invoke specialist skills, probe host capability, persist run state, call a plugin, or perform dispatch. A `READY_FOR_REVIEW` result is a planning disposition, not an execution authorization or runtime proof. The implementation is on this PR branch and is not merged to `main`.


### Controlled runtime implementation: sandbox execution pilot

The plan-only compiler remains useful for validating declared plans without side effects. A separate supervised runtime now closes the execution loop for a deliberately restricted class of actions:

- `catalog/hso-runtime-capabilities.json` registers trusted built-in adapters. The runtime probes handlers in a disposable directory and marks a capability `READY` only after a real action/read-back check.
- `catalog/hso-routing-policy.json` resolves one primary owner and bounded specialists by task type. Artifact creation routes to CP-05 with CP-07 as evidence specialist; independent verification routes to CP-07 with CP-05 as scheduling support.
- `contracts/hso-runtime-workflow.schema.json` defines the execution envelope; DAG cycles, duplicate IDs, unknown dependencies and repeated idempotency keys are rejected.
- `governance/hso-execution-policy.json` is deny-by-default. Sandbox writes require S3. Staging, production, unregistered actions, and unconfigured plugin/MCP capabilities are rejected. Approval receipts for future approval-gated actions are HMAC-checked, time-bounded and scope-bound.
- `tools/hso_super_orchestrator.py` dispatches only fixed, allow-listed Python handlers. It does not accept shell commands, arbitrary URLs, dynamic imports or user-selected callables.
- SQLite stores local idempotency state. Retries are bounded and limited to idempotent actions. Outcome-unknown/manual-review records cannot be automatically replayed.
- A dependent package independently reads the actual file target and verifies SHA-256. Conditional compensation removes only an artifact created by this run whose digest has not changed.
- JSONL audit events are sequence- and hash-chained, secret-like fields are redacted, and CI uploads receipts/target evidence for bounded retention.

The first CI pilot is actual GitHub-hosted sandbox execution, not a mock receiver. It proves only the built-in temporary-file adapter and isolated runner. The route for SKILL ANALYZER/A.S.F.R.E.E is defined but remains blocked because `plugin.skill.invoke` has no verified host bridge. Remote MCP and HTTP API dispatch are also `NOT_CONFIGURED`. The runtime is serial and single-runner; it is not a production service, distributed scheduler, or universal AI-host gateway. See `docs/HSO-SUPER-ORCHESTRATOR-RUNTIME.md`.

## 5. Canonical operating workflow

The default workflow is **evidence-first, one-primary-owner, and human-governed**.

```text
REQUEST
  |
  v
INTAKE & SCOPE
  |
  v
AUTHORITY / RISK PREFLIGHT
  |
  v
CATALOG / SOURCE / CAPABILITY CHECK
  |
  v
SINGLE-PRIMARY ROUTE ARBITRATION
  |
  v
DEPENDENCY DAG + HANDOFF CONTRACTS
  |
  v
AUTHORIZATION GATE
  |
  v
DISPATCH (only when a real adapter and runtime exist)
  |
  v
ARTIFACT / RESULT COLLECTION
  |
  v
CONTRACT + EVIDENCE VALIDATION
  |
  v
INDEPENDENT EVALUATION (when required)
  |
  v
ROADMAP / SOURCE / RELEASE STATE UPDATE
  |
  v
CLOSURE, RESIDUAL RISKS, AND AUDIT RECEIPT
```

### 5.1 Step definitions

1. **Intake:** capture the user's intended outcome, target system, affected repository or package, required deliverables, constraints, and explicit exclusions.
2. **Scope and authority:** identify the human decision owner, authorized environment, permitted action, consequence level, and whether the request permits observation, preparation, sandbox changes, staging, or production action.
3. **Capability preflight:** query the actual catalog and connectors; verify source identity, version, access, package eligibility, target host, tools, and permissions. Unknown capability remains `NOT_CHECKED`, not `READY`.
4. **Route arbitration:** select exactly one primary owner based on the dominant deliverable and the final decision that must be made. Add supporting specialists only for distinct outputs or mandatory controls.
5. **Plan:** create a dependency DAG, work packages, explicit input/output artifacts, owners, stop conditions, and acceptance criteria. Reject unresolved cycles and ambiguous write ownership.
6. **Authorization:** obtain approval at the level required for the exact target/action. Permission to inspect the parent repository does not authorize mutation of child repositories.
7. **Dispatch:** invoke the selected capability only through an actually available and authorized host/connector. A skill's presence in the catalog is not a dispatch mechanism.
8. **Collect:** retain output locators, source/version identity, provenance, timestamps, and partial/failure state.
9. **Validate:** run schema, behavior, compatibility, host, runtime, or independent quality checks appropriate to the claim being made.
10. **Record and close:** update the relevant GitHub artifact, roadmap record, or Notion knowledge page. Record unresolved risks and the exact evidence boundary.

### 5.2 Route selection rules

- Route by the primary deliverable and final decision owner, not by keywords alone.
- Assign one primary orchestrator per work package.
- Use a supporting specialist only when it contributes a distinct artifact, dependency, or required safety/evaluation control.
- Use a sequential handoff where one system's output is a prerequisite for the next; avoid parallel invocation when the second stage could consume an incomplete or unapproved result.
- If ownership is ambiguous, stop and resolve the responsibility matrix. Do not dispatch two plugins to make the same final decision.
- If the capability is absent, private, rights-restricted, host-incompatible, or not authorized, return `BLOCKED` or `UNAVAILABLE` with the reason. Do not silently substitute a weaker tool and call it equivalent.

## 6. Handoff, evidence, and state contracts

### 6.1 Existing handoff schema

The current `contracts/plugin-handoff.schema.json` defines a shared envelope including:

- `handoff_id` and `case_id`;
- source plugin identity and version/commit;
- recipient plugin identity and contract version;
- intent, scope, non-goals, and input locators/provenance;
- findings and `epistemic_status`;
- `capability_status`;
- authority/approval reference and dependencies;
- expected output, acceptance criteria, risk/unknowns, and completion status.

The canonical capability states are:

`READY`, `READY_WITH_LIMITATIONS`, `NOT_CHECKED`, `UNAVAILABLE`, `ACCESS_DENIED`, `EXPIRED`, `BLOCKED`, `OUT_OF_SCOPE`.

The canonical epistemic labels distinguish observed facts, verified source facts, user claims, source claims, assumptions, inferences, hypotheses, and unknowns. A downstream plugin must not upgrade an assumption into a verified fact merely by receiving it in a handoff.

### 6.2 State transitions

The intended work-package state model is:

`RECEIVED → TRIAGED → ROUTED → PLANNED → AUTHORIZATION_PENDING → DISPATCHED → EXECUTING → EVIDENCE_PENDING → VERIFIED → CLOSED`

Terminal or non-success states are:

- `BLOCKED`: a required source, right, permission, dependency, host, or artifact is unavailable.
- `REJECTED`: scope, policy, safety, or authority does not permit the requested action.
- `PARTIAL`: some outputs exist, but one or more acceptance conditions remain unmet.
- `FAILED`: an authorized execution or validation failed.
- `UNVERIFIABLE`: output exists, but the necessary evidence or read-back is unavailable.

These are target semantics. The parent repository does not currently contain a persistent shared runtime state machine.

### 6.3 Evidence depth and integration gates are different dimensions

A.S.F.R.E.E forensic depth levels describe what kind of access/evidence was actually inspected:

- L0 conceptual; L1 artifact; L2 source; L3 dynamic; L4 authorized adversarial; L5 controlled engineering; L6 verified deployment.

The ecosystem integration gates describe how a handoff relationship has been validated:

- C0 identity; C1 routing; C2 schema; C3 mock behavior; C4 named-host activation; C5 real runtime execution.

Never equate L2 source inspection with C4 host activation, or C3 mock behavior with C5 runtime proof.

## 7. Authority, safety, and change control

The default is read-only. The authority level is scoped to the exact target, environment, and action:

| Level | Mode | Permitted work |
|---|---|---|
| S0 | OBSERVE | Read, inventory, inspect, and analyze authorized sources |
| S1 | RECOMMEND | Findings, options, and recommendations |
| S2 | PREPARE | Prepare reversible patches, plans, or artifacts without applying them to the target |
| S3 | SANDBOX_ENGINEERING | Apply and test changes in an authorized isolated environment |
| S4 | STAGING_RELEASE | Change staging only after explicit approval |
| S5 | PRODUCTION_RELEASE | Production change only after explicit approval and recovery planning |

Additional controls:

- A parent-repository write does not authorize a child-repository write.
- Source code, credentials, issue text, imported instructions, and tool outputs are untrusted data until validated.
- Never place credentials, access tokens, private keys, or session material in Git or Notion documentation.
- Publishing private USER/PRIVATE package files to a public repository requires a separate explicit publication decision and rights basis.
- License declarations, repository visibility, and source pins are not interchangeable.
- Merge, release, publication, credential access, permission changes, deletion, external commitments, and production deployment require the appropriate human approval and permission.
- Repository changes follow branch + pull request + CI + review + read-back. No automatic merge is implied by a green check.
- Child plugin maintainers retain authority over their own source and releases.

The HSMART project's GOV role labels and platform governance are not automatically inherited by HSO. HSO uses the parent repository's documented owner/authorized-maintainer model unless a separate decision is recorded.

## 8. Failure handling and recovery

| Failure | Required response |
|---|---|
| Source/version cannot be verified | Preserve current source and snapshot separately; mark `NOT_COMPARED` or `BLOCKED` |
| Rights are absent or unclear | Keep package non-installable; request rights-holder decision; do not infer a license |
| Handoff schema mismatch | Reject the payload, record the schema/version mismatch, and do not silently coerce material fields |
| Access or permission denied | Stop the affected path; record denial; do not switch identity or seek privilege escalation |
| Host/runtime is unavailable | Return `UNAVAILABLE` or `NOT_CHECKED`; retain the unexecuted plan |
| Partial output | Record completed and missing deliverables separately; preserve the original acceptance criteria |
| Stale branch or conflicting write | Re-read repository head, reconcile the minimal patch, and re-run relevant tests |
| Retryable infrastructure error | Retry only with bounded attempts, idempotency, and explicit side-effect semantics |
| Failed release or migration | Stop promotion, preserve prior accepted state, and use the documented rollback path |

No operation should claim success until the target read-back or the host's success evidence is available.

## 9. Evidence and observability record

A future operational trace should record, at minimum:

| Field | Purpose |
|---|---|
| `case_id`, `handoff_id`, `trace_id` | Correlate work packages and execution traces |
| Actor / role / approval reference | Identify who or what acted and under which authority |
| Target repository, plugin key, source commit, package version | Pin the exact capability identity |
| Contract/schema version | Identify the interface that was validated |
| Host, model/provider, adapter version | Bound host compatibility claims |
| Capability and epistemic status | Preserve what was available and how claims were classified |
| Input/output locator and integrity digest | Support provenance and read-back without copying unnecessary sensitive data |
| Test identifiers and results | Make the verification claim reproducible |
| State transitions, timestamps, failure and rollback references | Explain what happened and how it recovered |

A future runtime must add least-privilege access control, redaction, retention limits, tenant isolation where applicable, tamper-evident audit storage, and explicit secret handling before processing sensitive production data.

## 10. Progress measurement without misleading percentages

Report separate denominators rather than one composite score:

- source onboarding: canonical sources accepted / active plugin identities;
- source completeness: complete manifests and trees / accepted sources;
- parity: exact instruction matches / comparable instruction files, with incomparable packages shown separately;
- rights: packages with a verified redistribution basis / requested distribution scope;
- contracts: C2 and C3 pass count / 14 defined edges;
- host activation: C4 pass count / host-targeted edges;
- runtime: C5 pass count / host-targeted edges;
- distribution: eligible packages / 22 catalog identities;
- operations: install/update/disable/uninstall/rollback and recovery tests with explicit pass/fail/not-run states.

Do not average these into a total percentage. A license blocker or missing source is a hard gate, not a small deduction that another passing test can cancel out.

## 11. Progressive implementation roadmap

| Stage | Objective | Exit gate |
|---|---|---|
| CP-0 — Foundation | Catalog, ownership, source provenance, routing, contracts, governance and static CI | Current parent baseline and validators remain green |
| CP-1 — Source and rights closure | Canonical child repositories, complete manifests, immutable pins, parity decisions, redistribution rights | Every active plugin has an accepted source/rights disposition |
| CP-2 — Contract assurance | Schema, negative cases, error semantics, versioning, dependency and authorization contracts | Reproducible C2/C3 evidence for all declared edges |
| CP-3 — Named-host pilot | One narrowly scoped target host, adapter, authorized identity, invocation and read-back | C4/C5 evidence on exact host/version/plugin/commit |
| CP-4 — Controlled package lifecycle | Reproducible artifacts, digests/signatures, dependency lock, install/update/disable/uninstall/rollback | Signed artifact and lifecycle regression evidence |
| CP-5 — Managed operations | Runtime, access policy, audit, monitoring, incident response, restore/DR and operator ownership | Independent production/security acceptance |

CP-3 is blocked until CP-1 and the relevant CP-2 gates pass. CP-4 and CP-5 should not be started as production projects merely because a design can be written.

## 12. Immediate priorities at this checkpoint

1. Complete human/Code Owner review of [PR #12](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/12), which registers source and redistribution-rights evidence. The latest PR head passed 54 tests, but remains open and unmerged.
2. Resolve the 14 unknown canonical Git sources and two incomplete candidates through owner-approved repository/visibility/license decisions.
3. Reconcile the source-content drift and version gaps without automatic overwrites.
4. Select one feasible named-host pilot only after rights, source, adapter, authorization, and test environment are known.
5. Decide later whether a managed gateway/runtime has a real use case, operating owner, support model, cost envelope, security design, and rollback plan.

**Acceptance rule:** the HSO control plane is operational only when real authorization, routing, dispatch, output collection, independent verification, durable state, and recovery have been demonstrated on an identified host and exact release. A complete document, a green static workflow, or a catalog entry alone does not satisfy that rule.
