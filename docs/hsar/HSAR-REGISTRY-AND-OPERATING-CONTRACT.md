# HSAR — HSO System Anatomy & Architecture Registry

**Version:** 0.1.0  
**Status:** Initial architecture proposal, not yet accepted into `main`  
**Owner boundary:** HSO ecosystem knowledge and forensic documentation  
**Related platform:** HSMART, maintained as a separate system and repository

## 1. Purpose

HSAR is the technical encyclopedia and evidence-backed structural knowledge layer for HSO and explicitly authorized connected systems, including HSMART. It documents entities from ecosystem and platform level down to plugins, agents, orchestrators, skills, sub-skills, modules, scripts, functions, interfaces, contracts, workflows, data stores, policies, tests, dependencies and runtime evidence.

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

A Notion page or inventory row is not proof that code exists, can be invoked, or is deployed. GitHub remains authoritative for engineering implementation. Notion is the documentation and navigation surface.

## 3. Entity hierarchy

The registry supports the following entity types:

1. Ecosystem and platform
2. System and subsystem
3. Plugin, agent and orchestrator
4. Skill and sub-skill
5. Module, script and function
6. API, MCP server and connector
7. Data store and schema
8. Contract, workflow and policy
9. Role, test, evidence, release and external dependency

Entities have stable IDs and typed relationships. A parent-child edge expresses structural composition; dependency, invokes, consumed-by, provides, governed-by and evidence-for are different relationship types and must not be conflated.

## 4. Component record requirements

Each record documents applicable fields:

- Stable identity, name, aliases, entity type, layer, version and lifecycle state.
- Purpose, rationale, primary duties, capabilities, non-goals and authority boundary.
- Composition, parent/children, dependencies, callers/callees and integration edges.
- Inputs, schemas, parameters, processing logic, outputs and side effects.
- Source repository, branch, exact commit SHA, file path, symbol, blob SHA and license/rights state.
- Script/function signatures, algorithm, important branches, errors, security, tests and operational constraints.
- Invocation mechanism, host/version, permission scope, approval behavior and execution receipt.
- State transitions, retry, timeout, idempotency, recovery, compensation and rollback behavior.
- Verification state, confidence, evidence links, limitations, reviewer decision and change history.

Do not duplicate full source code as a second canonical copy. Keep code in its authoritative repository and document it with stable path, symbol, immutable commit and blob hash.

## 5. Anatomy and physiology

Anatomy must answer: what components exist, how are they composed, who owns them, how are they related, and where is the implementation?

Physiology must answer: what triggers the component, what inputs are accepted, what processing occurs, which dependencies are called, what state changes, what outputs are emitted, and what happens when it fails?

Document runtime flows with sequence diagrams or state diagrams when they materially clarify behavior. Distinguish designed flow from behavior observed in a named host.

## 6. Fullscan contract

Every scan must declare:
- Target systems, repositories, Notion sources and allowed paths.
- Exact branch/tag/commit or snapshot revision.
- Scan level and depth.
- Source allowlist, explicit exclusions, privacy/licensing boundaries and denied paths.
- Discovered, read, analyzed, skipped and error counts.
- Findings, confidence, unresolved gaps and evidence references.

Coverage denominators must be explicit. Discovered does not mean read; read does not mean analyzed; analysis does not mean behavior tested. An excluded or inaccessible path is not silently counted as inspected.

Suggested scan levels:

| Level | Scope |
|---|---|
| L0 | Identity and capability inventory |
| L1 | Documentation, manifests and metadata |
| L2 | Structure, files, schemas and dependency graph |
| L3 | Behavioral logic, calls, state transitions and tests |
| L4 | Named host, runtime and end-to-end invocation |

## 7. Controlled reconstruction

Reconstruction has five distinct fidelity classes:

- Knowledge reconstruction
- Structural reconstruction
- Behavioral reconstruction
- Source reconstruction
- Environment/runtime reconstruction

Source reconstruction and cloning are limited to user-owned or explicitly authorized material with suitable rights. Never copy credentials, secrets, private instructions, personal data, or restricted third-party code. Record source-to-target traceability, fidelity tests, known deviations and missing dependencies. A reconstruction is not an operational clone until its behavior and environment are independently verified.

## 8. Mandatory Trilogy Analysis

Every substantial forensic review uses three separate passes:

1. **Positive analysis:** identify strengths, useful design decisions, capabilities, resilience and value worth preserving.
2. **Negative analysis:** identify weaknesses, defects, risks, missing evidence, failure modes and root causes.
3. **Negative-to-positive conversion:** convert each actionable negative into a concrete improvement, preventive/detective control, owner role, test, indicator, acceptance condition and residual-risk statement.

Use complementary methods when relevant, such as systems thinking, SWOT, FMEA, fault-tree analysis, threat modeling, dependency analysis, data-flow analysis, interface contract review, causal analysis and cost/benefit assessment. Do not invent metrics or force irrelevant frameworks.

## 9. Improvement adoption

Validated improvement candidates may be proposed for HSO and HSMART, but implementation must preserve source ownership, repository boundaries, API contracts, licensing, governance, backward compatibility and rollback. Cross-system changes require explicit interface changes and separate evidence in each repository. Do not copy specialist plugin code into the parent repository merely to centralize documentation.

## 10. Lifecycle and evidence states

Keep the following dimensions separate:

- Lifecycle: PROPOSED, SPECIFIED, IMPLEMENTED, VERIFIED, DEPLOYED, PRODUCTION_READY, DEPRECATED, RETIRED, UNKNOWN.
- Maturity: DISCOVERED, CATALOGUED, SOURCE_VERIFIED, PACKAGED, HOST_TESTED, EXECUTABLE, DEPLOYED, PRODUCTION_READY, UNKNOWN.
- Runtime evidence: NOT_CONFIGURED, NOT_RUN, MOCK_TESTED, SANDBOX_TESTED, HOST_TESTED, INVOCATION_VERIFIED, PRODUCTION_OBSERVED, UNKNOWN.
- Evidence status: SUPPORTED, PARTIALLY_SUPPORTED, UNVERIFIED, STALE, CONTRADICTED, NOT_APPLICABLE.

A state in one dimension must not be inferred from another. A route or skill catalog entry is not proof of dispatch. A passing static test is not production evidence.

## 11. Documentation synchronization

Session-scoped HSAR workflows can update Notion and GitHub when connectors, permissions and required evidence are available. GitHub changes should normally be made on an authorized feature branch and submitted through a pull request. Notion rows should use stable IDs, exact source SHAs, content hashes and idempotent upserts.

True event-driven synchronization requires a separately deployed and tested integration:
- GitHub Actions or webhooks on the intended event classes.
- Notion internal integration shared only with the three HSAR data sources it needs.
- Credentials in GitHub Actions secrets or a secret manager, never in source code or Notion text.
- Stable IDs, content hashes, pagination, rate-limit handling, retries and reconciliation.
- Redaction of credentials and sensitive data.
- Dead-letter/error tracking, audit receipts and read-back verification.

The plugin itself is not a background daemon. Do not claim continuous or automatic production synchronization until the event-driven workflow is configured and end-to-end acceptance tests pass.

## 12. Acceptance gates

An HSAR work item is complete only when:
- Its scope, target baseline and exclusions are recorded.
- Applicable source claims have immutable evidence.
- Structural and behavioral findings are distinguished.
- Trilogy Analysis is complete when substantial analysis is required.
- Proposed improvements have acceptance criteria and residual-risk statements.
- Notion records and GitHub artifacts are reconciled with exact URLs/SHAs.
- Required approval and source-owner boundaries are respected.
- No unsupported PASS, runtime, parity or production claim remains.

## 13. Initial connected registries

The Notion HSAR hub maintains three structured data sources:
- Component Registry
- Scan & Coverage Ledger
- Change & Evidence Ledger

The registries are separate from the SDGDS terminology registry and linked by stable relations.