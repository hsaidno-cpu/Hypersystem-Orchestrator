# Hypersystem Orchestrator — Ecosystem Architecture

**Architecture baseline:** v1.0.0  
**Architecture type:** Hybrid multi-repository with central ecosystem registry  
**Parent repository:** https://github.com/hsaidno-cpu/Hypersystem-Orchestrator

## 1. Purpose and boundary

Hypersystem Orchestrator coordinates a portfolio of independently developed AI plugins. It is the control and governance home for their shared architecture, not a runtime that automatically invokes the plugins.

The central repository owns:
- plugin identity and catalog records;
- source repository and immutable commit references;
- domain and responsibility boundaries;
- cross-plugin dependency declarations and integration contracts;
- shared version compatibility and deprecation policy;
- ecosystem governance, risk, roadmap and integration evidence;
- static validation of central catalog artifacts.

Each plugin source repository owns:
- its own README, plugin manifest, skill/subskill instructions and references;
- its tests, examples, release metadata, changelog and issue history;
- its package-specific compatibility, licenses and implementation artifacts;
- its internal architecture and release decisions, subject to ecosystem-level interface contracts.

## 2. Non-goals

This repository does not, by itself:
- create or update ChatGPT plugin packages;
- provision cloud services, databases, MCP servers, APIs or credentials;
- make all plugins callable as one runtime;
- guarantee cross-platform compatibility;
- merge or relicense the child repositories;
- replace HSMART's separate platform architecture;
- create autonomous agent execution or background synchronization;
- approve a production deployment or public release.

A catalog record is metadata. A submodule is a source pin. Neither is proof of runtime availability.

## 3. Logical architecture

### L0 — Human intent and governance

The human project owner supplies goals, scope, approvals and risk tolerance. Human decisions remain authoritative for consequential, legal, security, privacy, commercial and production matters.

### L1 — Ecosystem registry and control documentation

The parent repository maintains catalog/plugins.json, catalog/repositories.json, the registration schema and shared governance. It resolves identity, ownership and compatibility metadata. It does not execute the registered capabilities.

### L2 — Domain orchestrators

The registered plugins route work within their domains. Select one primary orchestrator based on the dominant intent. Supporting plugins contribute bounded outputs through explicit handoffs; they do not all activate by default.

### L3 — Specialist capabilities

Subskills and specialist instructions remain inside their owning plugin. They are not automatically split into separate repositories or independent agents.

### L4 — Tools, adapters and execution environments

External models, image/audio/video tools, code runners, MCP servers, APIs, cloud runtimes and GitHub/Notion connectors are separate dependencies. Their readiness and permissions must be checked at the point of use.

### L5 — Assurance and lifecycle

Static checks, contract tests, host-activation tests, runtime tests, release approvals and rollback evidence are distinct assurance layers. Passing an earlier layer does not imply later-layer success.

## 4. Relationship model

Human Owner → Central Ecosystem Registry → Primary Domain Orchestrator → Supporting Plugin(s) → Specialist Procedures / External Tools → Evidence & Handoff → Human Decision

The arrows indicate governed work routing and information handoff. They do not claim that this GitHub repository currently performs programmatic invocation.

## 5. Primary ownership and overlap arbitration

| Domain | Primary owner | Supporting systems | Boundary rule |
|---|---|---|---|
| Cross-domain analysis and method selection | SKILL ANALYZER | A.S.F.R.E.E, Evaluator Team | Analyzer owns analytical methodology; A.S.F.R.E.E owns technical case control and engineering assurance. |
| Technical forensics and supervised engineering | A.S.F.R.E.E Canonical | SKILL ANALYZER, Agent Jailbreak DS | A.S.F.R.E.E coordinates authorized technical cases; security specialists own their defensive assessment. |
| Skill/plugin lifecycle engineering | Skill Developer Orchestrator | SKILL ANALYZER, Octa-Prompt, Evaluator Team | SDO owns lifecycle coordination and change delivery; supporting evaluators do not create competing write authorities. |
| Independent skill evaluation | Evaluator Team | SKILL ANALYZER, Octa-Prompt, SDO | Evaluator Team owns independent evaluation/design review; accepted source changes have one implementation owner. |
| Prompt architecture | Anatomi Prompt V3 — Octa-Prompt | AI Prompt Finder & Creator | Octa-Prompt structures instructions; Prompt Finder reconstructs/optimizes prompts from references. |
| Agent lifecycle | Plugin Agent Orchestrator | Agent Jailbreak DS, Workflow Systems | Agent Orchestrator owns agent design/build/operate/ecosystem lifecycle; security review remains independently scoped. |
| Workflow and project architecture | AI Workflow Systems Orchestrator | Cortex Workbench, Agent Orchestrator | Workflow Systems owns reusable process/system architecture, not every knowledge-work or agent implementation. |
| General knowledge work | Cortex Workbench | CommandCraft 56, SKILL ANALYZER | Cortex routes broad learning/research/writing/coding work; CommandCraft owns its 56 command aliases. |
| Domain-specific business operations | GrowthForge Business OS | CommandCraft 56, Cortex Workbench | GrowthForge owns business-domain deliverables; general command tools provide optional support. |
| Capability inventory and staged adoption | Agent Skills Atlas | SKILL ANALYZER, Workflow Systems | Atlas owns catalog/adoption lifecycle and provenance; registration does not imply installation or execution. |
| General photo editing | Photo Fixer | Master Photo Restoration | Photo Fixer owns broad editing workflow; restoration specialist owns conservative identity-preserving restoration. |
| Portrait/photo restoration | Master Photo Restoration | Photo Fixer | Preserve source identity and document limits of reconstructed detail. |
| General motion-graphics workflow | Motion Graphic by arifanara | GODEX | Motion Graphic owns general explainer project routing and creative delivery workflow. |
| Voice-over-led audio/motion production | GODEX Motion Audio | Motion Graphic, Promkes | GODEX owns audio/timing/narrative-led coordination; shared output contracts avoid duplicated scene state. |
| Health-promotion video | PVEE Promkes / Video Explainer Promkes | GODEX, Motion Graphic, Prompt Finder | Health facts, source provenance and safe wording remain under health evidence gates and human clinical approval. |
| Legacy A.S.F.R.E.E access | A.S.F.R.E.E Legacy | A.S.F.R.E.E Canonical | Legacy is redirect-only. It is never a second master orchestrator or fallback implementation. |

## 6. Critical overlap decisions

### 6.1 A.S.F.R.E.E Canonical vs Legacy

The canonical source is hsaidno-cpu/A.S.F.R.E.E. The legacy package is a compatibility redirect to the canonical plugin. It must not be developed as a second product. Version 1.0.4 of the legacy redirect does not define canonical product version.

### 6.2 Skill Developer Orchestrator vs Evaluator Team

SDO is the lifecycle controller for skill/plugin development. Evaluator Team is an independent evaluation and redesign system. A task may use both, but the evaluation result must be accepted before implementation, and only one workstream may own writes to a given source repository/branch.

### 6.3 SKILL ANALYZER vs A.S.F.R.E.E

SKILL ANALYZER contributes reusable analytical methodology, evidence, comparison and evaluation procedures. A.S.F.R.E.E controls the authorized technical case lifecycle, authority gates, engineering change and independent verification. Avoid copying the whole analysis engine into A.S.F.R.E.E.

### 6.4 Photo Fixer vs Master Photo Restoration

Both operate in image editing. Keep general-purpose photo editing distinct from conservative identity-preserving restoration. Their source relationship is not yet confirmed; do not merge them or share code until their source repositories and licensing are inspected.

### 6.5 Promkes, GODEX and Motion Graphic

These plugins overlap in video/audio production but have different domain contracts. Health claims and Fact Lock belong to Promkes. Audio provenance, voice analysis and audio post belong to GODEX. General motion-graphics intake, style, choreography and delivery belong to Motion Graphic. Share assets or manifests only through explicit contracts and provenance.

## 7. Dependency policy

- Prefer directed, versioned handoffs over hard runtime dependencies.
- A soft integration means a plugin may contribute when available; it does not block the primary workflow.
- A hard dependency must be declared with a minimum compatible version and a testable acceptance contract.
- No plugin may depend on the parent repository as a runtime service unless an actual service is designed and deployed.
- No dependency cycles. Each change affecting an interface must update its consumer matrix and tests.
- Unknown dependencies remain UNVERIFIED; do not infer them from product names or common subject matter.

## 8. Source integration strategy

The parent uses Git submodules only for source repositories whose identity and content have been inspected. Submodules are pinned to commit SHAs and must be updated through reviewed changes.

Initial source pins:
- plugins/skill-analyzer → public SKILL ANALYZER repository.
- plugins/asfree → public canonical A.S.F.R.E.E repository.
- plugins/anatomi-prompt-strategis → private Anatomi Prompt repository.

Photo-Fixer is listed as a candidate repository only because its current root is minimal. Other plugins remain pending_repository until a correct source repository is identified and inspected.

## 9. Integration contract

Every cross-plugin handoff should carry:
- handoff_id and case_id (stable within the task);
- source plugin key and source version/commit;
- receiving plugin key and required contract version;
- user objective, scope and non-goals;
- input artifact references and provenance;
- relevant findings/requirements with stable IDs;
- epistemic statuses (observed, verified source, claim, assumption, inference, hypothesis, unknown);
- constraints, authority level and permission assumptions;
- dependency status and capability-readiness status;
- expected output and acceptance criteria;
- error/partial status, residual risk and next owner.

Never copy secrets, access tokens, private keys, passwords or raw credentials into handoff payloads.

## 10. Status model

Use the following independently observable states:

REGISTERED → SOURCE_REPO_IDENTIFIED → SOURCE_VERIFIED → SUBMODULE_PINNED → CONTRACT_DEFINED → STATIC_VALIDATED → CONTRACT_TESTED → HOST_TESTED → RUNTIME_VERIFIED → RELEASED

A source may be private or unavailable at any stage. BLOCKED, UNKNOWN, NOT_RUN, PARTIAL, UNVERIFIABLE and DEPRECATED are valid explicit states. Do not skip stages or infer later status from earlier completion.

## 11. Architecture decision record

**ADR-001 — Hybrid Multi-Repository + Central Ecosystem Repository**

- Status: Accepted as the baseline architecture for this parent repository.
- Decision: keep every independently useful plugin in its own source repository; use Hypersystem Orchestrator as central catalog, architecture, governance, contract, compatibility and roadmap repository.
- Alternatives rejected: copying all plugin source into one monorepo; leaving repositories uncoordinated without a central registry.
- Consequences: independent releases and permissions; stronger central integration governance; submodule pins require periodic updates; private source repositories may prevent public full-clone.
