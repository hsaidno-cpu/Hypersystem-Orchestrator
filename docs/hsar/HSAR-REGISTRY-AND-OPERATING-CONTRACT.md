# HSAR — HSO System Anatomy & Architecture Registry

**Version:** 0.3.0  
**Status:** Proposed operating contract; PR not merged  
**Owner boundary:** HSO ecosystem knowledge, forensic scanning and controlled improvement  
**Related platform:** HSMART, maintained as a separate system and repository

## 1. Purpose

HSAR is the technical encyclopedia and evidence-backed forensic registry for HSO, HSMART and explicitly authorized connected components in the HSO ecosystem. It must explain what exists, how systems are composed, how components work and interact, why they are needed, what can fail, how weaknesses can be improved and what evidence proves an improvement succeeded.

HSAR records both:

- **Anatomy:** identity, composition, ownership, hierarchy, responsibilities and dependency relationships.
- **Physiology:** invocation, communication, inputs, processing, outputs, state transitions, failures, recovery and audit behavior.

HSAR is separate from SDGDS. SDGDS owns canonical terminology and definitions. HSAR owns component and implementation knowledge and relates to SDGDS through stable Term IDs.

## 2. Source-of-truth boundaries

| Information | Canonical authority | HSAR role |
|---|---|---|
| HSO code, manifests, schemas, tests, workflows, PRs and releases | HSO repository | Explain and index exact revisions |
| HSMART code and platform internals | HSMART repository | Explain authorized HSMART sources without absorbing ownership |
| Plugin source and skill instructions | Each canonical child repository or verified installed source snapshot | Record source identity, rights, parity, path and evidence |
| Terminology and glossary definitions | SDGDS canonical registry | Link to canonical terms; do not create competing definitions |
| Component knowledge, scans and cross-component explanation | HSAR registries and documentation | Maintain structured knowledge and provenance |
| Project decisions, approval, roadmap and evidence controls | Approved governance records and HSO control plane | Link receipts and accepted decisions |

A Notion page or inventory row is not proof that code exists, can be invoked or is deployed. GitHub remains authoritative for engineering implementation. Notion is the documentation and navigation surface.

## 3. Primary spearhead architecture

For HYPERDEEP_FORENSIC and EXTREME_HYPERDEEP modes, six plugins form HSAR's primary forensic spearheads:

1. SKILL ANALYZER — forensic method selection, source/evidence audit, root cause and negative/positive analysis.
2. ANATOMI PROMPT v3.0 — OCTA-PROMPT — eight-pillar instruction and requirement architecture.
3. ASFREE — artifact inventory, atomic deconstruction, provenance and authorized reconstruction.
4. AI Workflow Systems Orchestrator — modular workflow/system design, integration, evaluation and optimization.
5. Evaluator Team — adversarial challenge, counterevidence, cross-evaluation and acceptance assessment.
6. Skill Developer Orchestrator — controlled implementation, regression, packaging and release assurance.

Each role must be resolved and assigned a truthful state: INVOKED, PROCEDURE_APPLIED, UNAVAILABLE or NOT_USED. INVOKED requires an observable distinct call receipt. Record requested and observed versions separately. A lower version is not v3.0 equivalence without compatibility evidence. If a required spearhead is unavailable, use only a documented valid fallback; otherwise preserve partial work and mark BLOCKED.

Additional HSO ecosystem plugins may be activated conditionally when the target or evidence establishes a concrete need. Resolve canonical identity, version, owner, permission, capability, source and invocation receipt first. Plugin catalogue presence is not proof of executability.

## 4. Entity hierarchy

The registry supports:
1. Ecosystem and platform.
2. System and subsystem.
3. Plugin, agent and orchestrator.
4. Skill and sub-skill.
5. Module, script and function.
6. API, MCP server and connector.
7. Data store and schema.
8. Contract, workflow and policy.
9. Role, test, evidence, release and external dependency.

Entities have stable IDs and typed relationships. Parent-child composition, dependency, invokes, consumed-by, provides, governed-by and evidence-for are distinct edge types.

## 5. Component record requirements

Each record documents applicable fields:
- Stable identity, name, aliases, entity type, layer, version and lifecycle.
- Purpose, rationale, duties, capabilities, non-goals and authority boundary.
- Composition, parent/children, dependencies, callers/callees and integration edges.
- Inputs, schemas, parameters, processing, outputs and side effects.
- Source repository, branch, exact commit SHA, path, symbol, blob SHA and licence/rights state.
- Script/function signatures, algorithm, branches, errors, security, tests and operational constraints.
- Invocation mechanism, host/version, permission scope, approval behavior and execution receipt.
- State transitions, retry, timeout, idempotency, recovery, compensation and rollback.
- Verification state, confidence, evidence links, limitations, decisions and change history.

Do not duplicate full source code as a second canonical copy. Keep code in its authoritative repository and document it with exact paths, symbols and immutable revisions.

## 6. Fullscan contract

Every scan declares:
- Target systems, repositories, Notion sources and allowed paths.
- Exact branch/tag/commit or snapshot revision.
- Scan level and depth.
- Source allowlist, exclusions, privacy/licensing boundaries and denied paths.
- Discovered, read, analyzed, skipped and error counts.
- Findings, confidence, unresolved gaps and evidence references.

Coverage denominators are explicit. Discovered does not mean read; read does not mean analyzed; analysis does not mean behavior tested. Unknown denominators remain UNKNOWN.

## 7. L1-L4 scan levels

| Level | Scope | Evidence boundary |
|---|---|---|
| L1 | Documentation, manifests, contracts, policies, plugin/skill inventory, versions, ownership and source baselines | Documentation-level evidence only |
| L2 | Recursive structure, component hierarchy, interfaces, schemas, data stores, scripts/functions inventory and dependency graphs | Source-verified or inferred edges clearly labelled |
| L3 | Script/function implementation, algorithms, control/data flow, branches, state transitions, security, errors, retries, failure handling and tests | Static analysis distinguished from actual executed tests |
| L4 | Named-host/runtime invocation, permissions, side effects, logs, recovery and end-to-end tests | Only with explicit authorization and actual receipts |

Every level has entry/exit criteria and independent coverage denominators. Do not promote an L2 result to L3/L4. Do not infer runtime invocation from a route, manifest, source file or passing static CI.

## 8. Controlled reconstruction

Reconstruction has five fidelity classes: knowledge, structural, behavioral, source and environment/runtime reconstruction.

Source reconstruction/cloning is limited to user-owned or explicitly authorized material with suitable rights. Never copy credentials, secrets, private instructions, personal data or restricted third-party code. Record source-to-target traceability, fidelity tests, deviations and missing dependencies. A reconstruction is not an operational clone until behavior and environment are independently verified.

## 9. Mandatory analytical output: four core tables

Every substantive analysis uses four separate tables:
1. Cross-method analysis.
2. Positive analysis.
3. Negative/root-cause analysis.
4. Negative-to-positive conversion.

Do not collapse these into a generic SWOT. Every material negative maps to a concrete intervention, control, test, evaluation measure and residual-risk disposition, or an explicit reason for deferral/rejection.

## 10. Comparative output: 4+2

When the user explicitly requests comparison, retain the four core tables and append:
5. Comparative scorecard comparing the four analytical dimensions across all target objects.
6. Feature-gap and evaluative recommendation table.

Both comparison tables include value, score, classification, evidence coverage, confidence and caveats. A 0–5 score requires an anchored rubric and comparable evidence. Unknown/inaccessible/untested evidence is N/A, not zero. Composite scores are not aggregated by default; hard P0/P1 gates cannot be offset by an average. See the separate 4+2 output contract.

## 11. Adaptive methodology intelligence

The method set is open-ended. Current methodologies are starter examples, not a permanent whitelist. HSAR may discover new or more effective methods, screen and pilot them against baseline methods, validate reproducibility and domain fit, adopt them with evidence, or reject/defer/retire them. Method cards preserve primary sources, version, assumptions, input quality, procedure, limitations, cost, comparator results and decision history. Novelty alone does not establish superiority.

When methods conflict, preserve their assumptions, evidence and dissent; seek counterevidence and discriminating tests. Do not average incompatible conclusions.

## 12. Improvement adoption

Validated candidates may be proposed for HSO and HSMART, but implementation preserves source ownership, repository boundaries, API contracts, licensing, governance, backward compatibility and rollback. Cross-system changes require explicit contracts/adapters and separate evidence in each repository. Do not copy child plugin source into the parent repository merely to centralize documentation.

## 13. Backup, checkpoint and recovery

Long-running hyperdeep scans preserve versioned checkpoints, immutable IDs, exact source baselines, skill/tool versions, stage status, output hashes and next actions. Keep the last verified checkpoint separate from the latest incomplete attempt.

On specialist/dependency failure: classify the failure; retry only transient failures within bounds; re-read source revisions; resume from a verified checkpoint; replay idempotently; quarantine integrity mismatches; and preserve partial work if no safe fallback exists. Secrets are excluded from checkpoints and logs. Restore must be performed into an isolated target and verified before promotion. Do not invent RPO/RTO.

## 14. Documentation synchronization

Session-scoped HSAR workflows may update Notion and GitHub when connectors, permissions and required evidence are available. GitHub changes normally use authorized feature branches and PRs. Notion records use stable IDs, exact source SHAs, content hashes and idempotent upserts.

True event-driven synchronization requires a separately deployed and tested integration: GitHub Actions/webhooks, scoped Notion integration, protected secrets, redaction, idempotency, bounded retries, reconciliation, dead-letter handling, read-back and audit receipts. The plugin is not a background daemon. Keep sync NOT_CONFIGURED, PARTIAL or BLOCKED until end-to-end acceptance passes.

## 15. Acceptance gates and authority

A work item is complete only when its scope, exact baseline, exclusions, source claims, applicable tests, coverage, recovery evidence and documentation reconciliation are supported by evidence.

Merge, release, production deployment, production permission changes and destructive operations are reserved human actions. AI may prepare evidence and recommendations, but may not create fake approval or infer authorization from a general development request.

## 16. Roadmap and companion contracts

The current roadmap defines:
- G0: review/acceptance of HSO PR #30 and HSMART PR #38.
- G1: authenticated GitHub-to-Notion sync readiness and pilot.
- L1: documentation and capability fullscan.
- L2: architecture/composition/dependency mapping.
- L3: source/script/control-flow/failure forensics.
- L4: authorized named-host/runtime verification.
- G2: four-table analysis, conditional 4+2 comparison, controlled improvement adoption and evidence closeout.

Companion documents:
- METHODOLOGY-REGISTRY-AND-EVOLUTION.md
- COMPARATIVE-4PLUS2-OUTPUT-CONTRACT.md
- EXTREME-HYPERDEEP-L1-L4-ROADMAP.md
- ACCEPTANCE-AND-BACKUP-RECOVERY-SUITE.md

## 17. Canonical registries

The Notion HSAR hub maintains Component Registry, Scan & Coverage Ledger and Change & Evidence Ledger. They remain separate from SDGDS and link to canonical terminology records.
