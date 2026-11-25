# UEDE–HSO Capability Audit — 2026-11-25

**Status:** Catalog-level inventory complete for 23/23 identities. This is not a per-skill behavioral audit, live-host test, rights clearance or invocation certification.  
**Source snapshot:** HSO `main`, `catalog/plugins.json` and `catalog/instruction-snapshots.json`, observed 2026-11-25.  
**Target:** Identify which HSO assets can contribute to roadmap-directed HSMART/HSO development without overstating execution readiness.

## 1. Executive result

HSO contains **23 plugin identities and 265 indexed skill definitions**. The catalog reveals substantial potential engineering and assurance capabilities, but the executable capability supply is much smaller:

- 5 identities are connected to official source submodules.
- 2 identities have candidate/incomplete source state.
- 15 identities have pending repository/source identification.
- 1 identity is a legacy redirect, not an independent capability.
- HSO's plan-only planner is usable for deterministic planning.
- The controlled sandbox proves only local write/read-back actions (`sandbox.write_text`, `sandbox.verify_sha256`).
- Generic `plugin.skill.invoke` and `mcp.remote.invoke` remain `NOT_CONFIGURED`; there is no verified general-purpose HSO plugin execution host.

**Conclusion:** P1 catalog inventory is complete, but P1 operational eligibility is not. The best source-backed engineering candidate is SDO, with A.S.F.R.E.E as a restricted technical-forensics/repair capability. Neither is currently proven as a live HSMART code worker. Most other candidates remain discovery/design support only until source, rights and host evidence exist.

## 2. All 23 plugin identities

The following table covers every identity in the current catalog. Skill counts are indexed definitions, not tested or executable skill counts.

| Plugin identity | Contribution class | Indexed skills | Source state | Source classification | Version planes | HSMART development relevance |
|---|---|---:|---|---|---|---|
| Video Explainer Promkes V4.1.12 | Domain-specific production | 16 | `integrated_submodule` | `OFFICIAL_PUBLIC_SOURCE_LAGGING` | source 4.1.9 / package 4.1.12 | Specialist health-promotion video production, not HSMART platform development. |
| Skill Developer Orchestrator | Direct engineering | 1 | `integrated_submodule` | `OFFICIAL_SUBMODULE` | source 0.1.0 / package 0.1.0 | Engineering lifecycle for skill/plugin source, controlled change, regression and release preparation. Not yet a verified HSMART code-execution host. |
| Evaluator Team | Evaluation/assurance | 4 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 1.0.0 | Evaluation criteria, scoring and redesign recommendations; source and rights remain unidentified. |
| Master Photo Restoration | Domain-specific production | 1 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 1.0.0 | Photo restoration delivery, not HSMART platform development. |
| Anatomi Prompt V3.0 — Octa-Prompt | Prompt architecture | 9 | `integrated_submodule` | `OFFICIAL_PRIVATE_SUBMODULE_LICENSE_NOT_FOUND` | source 3.0.0 / package 3.0.0 | Prompt architecture and instruction design; private source license not found. |
| SKILL ANALYZER | Analysis/assurance | 12 | `integrated_submodule` | `OFFICIAL_SUBMODULE_LICENSE_NOT_FOUND` | source 1.3.0 / package 1.0.0 | Cross-domain analysis and evidence audit; source license undeclared and package/instruction drift unresolved. |
| GODEX Motion Audio | Domain-specific production | 8 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 2.0.0 | Voice/audio-first media production, not HSMART platform development. |
| AI Prompt Finder & Creator | Domain-specific production | 7 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 1.0.0 | Reference-to-prompt creation, not software platform engineering. |
| Agent Jailbreak Skill DS | Security assurance | 11 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 0.2.0 | Defensive agent threat modeling, prompt/tool trust boundaries and safe security testing; no canonical source. |
| Motion Graphic by arifanara V.01 | Domain-specific production | 19 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 0.2.0 | Visual-first motion graphics production, not HSMART platform development. |
| Plugin Agent Orchestrator | Direct engineering | 44 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 2.0.0 | Broad agent code/test/runtime/integration/security skills, but package-only until canonical source and host are identified. |
| Photo Fixer | Domain-specific production | 12 | `candidate_repository` | `CANDIDATE_INCOMPLETE` | source NOT_IDENTIFIED / package 1.0.0 | General photo editing; candidate source incomplete and not software platform engineering. |
| A.S.F.R.E.E | Direct engineering | 13 | `integrated_submodule` | `OFFICIAL_SUBMODULE_POLYFORM_NONCOMMERCIAL` | source 0.5.0-rc.1 / package 0.3.2 | Technical forensics, failure diagnosis, supervised remediation and QA; constrained to non-commercial use under recorded terms. |
| A.S.F.R.E.E Legacy | Legacy redirect only | 1 | `canonical_redirect` | `LEGACY_REDIRECT` | source NOT_IDENTIFIED / package 1.0.4 | Redirect alias only; never count as an independent executable capability. |
| Cortex Workbench | General knowledge work | 8 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 1.0.0 | Broad knowledge/research/coding workflow support; package-only, not a verified software worker. |
| CommandCraft 56 | Command routing | 14 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 0.1.0 | Command normalization and task-profile routing; aliases do not create an automation runtime. |
| Agent Skills Atlas | Capability discovery | 17 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 0.3.1 | Skill taxonomy, provenance and readiness mapping; useful for discovery, not invocation. |
| People & Business Competency Academy | People/business development | 9 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 0.1.0 | People/business skill diagnosis, curriculum and transfer; supports organizational capability, not platform code execution. |
| AI Workflow Systems Orchestrator | Architecture support | 9 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 0.2.0 | Reusable workflow and modular-system design; no source/runtime evidence. |
| GrowthForge Business OS | Business/system development | 18 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 1.1.1 | Business strategy, product, operations, finance and growth decisions; supports business architecture, not platform code execution. |
| PVEE Promkes Super Orchestrator | Domain-specific production | 14 | `candidate_repository` | `CANDIDATE_INCOMPLETE` | source NOT_IDENTIFIED / package 2.0.2 | Health communication truth/governance and campaign evaluation; candidate source incomplete, domain-specific. |
| Progressive Roadmap Evaluator (PRE) | Roadmap governance | 9 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 0.1.1 | Roadmap lifecycle, progressive evaluation and adaptive planning; current package is specification only, not a deployed PRE runtime. |
| Ponytail Engineering System | Direct engineering | 9 | `pending_repository` | `NOT_IDENTIFIED` | source NOT_IDENTIFIED / package 0.1.0 | Read-only codebase audit, minimal-change design and risk-based test planning; explicitly not the source writer or merger. |

## 3. Source, rights and parity disposition

| Identity | Provenance / rights evidence | Version and parity finding | Current use boundary |
|---|---|---|---|
| Skill Developer Orchestrator | Canonical SPDO source; Apache-2.0 recorded | Source/package v0.1.0; 0/4 instruction files exact-match | Candidate for skill/plugin package engineering after instruction parity remediation |
| A.S.F.R.E.E canonical | Canonical private source; PolyForm Noncommercial | Source v0.5.0-rc.1 vs package v0.3.2; instruction drift | Non-commercial technical forensics and supervised repair only; reconcile package/source before execution |
| SKILL ANALYZER | Public source submodule; no source LICENSE declaration found in the inspected baseline | Source v1.3.0 vs package v1.0.0; instruction drift | Analytical support only; resolve rights and version/parity before distribution or autonomous invocation |
| Anatomi Prompt V3 | Private source submodule; LICENSE not found in inspected baseline | Source/package v3.0.0; parity currently MATCH | Prompt architecture support only; clarify rights before redistribution |
| Video Explainer Promkes | Public source submodule | Source v4.1.9 vs deployment/package v4.1.12; parity not compared | Domain-specific media production; source reconciliation required for source changes |
| Photo Fixer / PVEE | Candidate repositories | Source incomplete; rights/parity not established | Quarantined from autonomous selection until source and rights baselines are complete |
| 15 pending-source identities | No canonical source pointer or license/rights baseline recorded in the catalog | Source parity cannot be assessed | Metadata/snapshot-only use; no source editing, distribution or autonomous execution |
| A.S.F.R.E.E Legacy | Canonical redirect to A.S.F.R.E.E | No separate source/version plane | Redirect-only; never selected as a separate worker |

An HSO plugin being public, private or present in a package does not by itself grant the HSMART project permission to redistribute or invoke it. The specific license and actual grant must be verified for the intended use, including whether that use is commercial.

## 4. Capability map for HSMART development

### 4.1 Primary engineering and technical assurance

**SDO — source/skill lifecycle engineering**
- Best fit for developing and maintaining HSO skill/plugin packages, their tests, manifests and release handoffs.
- It is not automatically a general software engineer for the HSMART FastAPI/PostgreSQL codebase.
- Before selection: resolve the 0/4 instruction parity drift, pin an immutable source commit and prove the intended host can invoke the approved skill.

**A.S.F.R.E.E — technical anatomy and supervised remediation**
- Strongest recorded specialist coverage for inspecting plugin/software topology, schemas, dependencies, permissions, failure paths, remediation, integration lab and QA.
- PolyForm Noncommercial is a hard boundary. Do not use it for commercial service delivery unless a separate permission is obtained.
- Package/source drift means the exact content to execute must be settled first.

**Ponytail Engineering System — engineering method**
- Useful for repository mapping, impact analysis, minimal-change design and test/security planning.
- Catalog boundary explicitly denies source writes, commits, PRs, merges and releases.
- No canonical source repository is identified; therefore methodology reference only.

**Plugin Agent Orchestrator — possible engineering workforce**
- Its 44 indexed skills include code engineering, test engineering, CI/CD, runtime engineering, API/MCP connectors, identity policy and credential management.
- No canonical source repository or live host is identified. Do not treat these 44 entries as 44 active agents or route credentials to them.

**Agent Jailbreak Skill DS — defensive security support**
- Relevant to prompt injection, context integrity, tool authorization and agent abuse testing.
- No canonical source or host evidence; use only as a design/test reference until source and rights are established.

### 4.2 Discovery, evaluation and planning support

- **Agent Skills Atlas:** capability taxonomy, provenance, dependency and adoption maturity; strongest conceptual match to P5 discovery, but source and host are missing.
- **Evaluator Team:** quality/evaluation criteria and redesign recommendations; source/rights/host not identified.
- **SKILL ANALYZER:** broad analytical methodology and evidence audit; license and content parity unresolved.
- **PRE:** roadmap intake, R0–R9 lifecycle and adaptive evaluation; package specification only, not a shared runtime.
- **AI Workflow Systems Orchestrator:** workflow/SOP architecture; does not provision workflow services.
- **Anatomi Prompt:** prompt and instruction architecture; private source license unresolved.
- **Cortex Workbench / CommandCraft 56:** general knowledge-work orchestration and command-profile routing; neither is evidence of a live engineering worker or automation runtime.

### 4.3 Business and organizational development support

- **GrowthForge Business OS:** business strategy, market/customer insight, product, finance, marketing, sales and operations. Useful for HSMART product/business decisions, not code execution.
- **People & Business Competency Academy:** people/business competency diagnosis, curriculum and practice. Useful for operator/team capability development, not system implementation.

### 4.4 Domain-specific production

Video Explainer Promkes, GODEX Motion Audio, AI Prompt Finder & Creator, Motion Graphic, Master Photo Restoration, Photo Fixer and PVEE support media, content or health-promotion production. They may build deliverables that run on HSMART, but they are not general HSMART platform engineering capabilities. Photo Fixer and PVEE also remain candidate/incomplete source entries.

## 5. Actual HSO execution plane

| Plane | Observed state | What it proves | What it does not prove |
|---|---|---|---|
| Capability catalog | 23 identities / 265 skill definitions | Discovery metadata exists | Skills are installed, rights-cleared or executable |
| Plan-only planner | Available in HSO repository | Owners, capability states, authority and dependency DAG can be validated into an ordered plan | Plugin invocation, remote execution or roadmap writes |
| Local sandbox | `sandbox.write_text` and `sandbox.verify_sha256` READY | Isolated local artifact write and hash verification | HSMART service access, production worker or general code deployment |
| Generic plugin invocation | `plugin.skill.invoke` NOT_CONFIGURED | No general host dispatch | Any catalog-listed skill can be called |
| Generic remote MCP | `mcp.remote.invoke` NOT_CONFIGURED | No general multi-server remote invocation | A mocked/narrow adapter is a live general MCP platform |
| Narrow SKILL ANALYZER MCP pilot | Specific one-tool adapter has code/test work on an HSO PR branch; live endpoint/OIDC not verified | A bounded adapter design can be validated in tests | Live, generic, production-ready invocation |
| HSMART platform services | KM 0/KM 1 acceptance incomplete; KM 2+ blocked | Roadmap and service contracts are documented | Registry, gateway, managed runtime, secrets or audit are available to UEDE |

## 6. P1 readiness classification

Use these states as separate dimensions; never compress them into one `READY` flag:

1. `DISCOVERED` — identity exists in catalog.
2. `SOURCE_IDENTIFIED` — canonical repository is known.
3. `SOURCE_PINNED` — exact commit is recorded.
4. `RIGHTS_CLEARED` — intended HSMART/HSO use is permitted.
5. `INSTRUCTION_PARITY_VERIFIED` — selected package instructions match the approved source/version.
6. `CONTRACT_TESTED` — I/O, compatibility and permission boundaries pass.
7. `HOST_CONFIGURED` — a named host/adapter and scoped authentication exist.
8. `HOST_ACCEPTANCE_PASSED` — real target-host invocation produces verified output and receipt.
9. `INVOCATION_ELIGIBLE` — every required dimension passes for the requested task and risk tier.
10. `PRODUCTION_ELIGIBLE` — production controls, observability, recovery, audit and security acceptance are separately complete.

A capability can be useful in analysis while remaining blocked from invocation. Eligibility is task- and host-specific, not a permanent property of a plugin name.

## 7. P1 closure work

The catalog-level 23/23 inventory is complete. The remaining P1 closure work is:

- Resolve SDO instruction parity and document its precise allowed write scope.
- Reconcile A.S.F.R.E.E's package/source version and ensure every use respects PolyForm Noncommercial.
- Resolve SKILL ANALYZER's license and package/source parity before any distribution or general invocation.
- Establish source ownership and license evidence for Plugin Agent Orchestrator, Ponytail, Agent Skills Atlas, Agent Jailbreak and Workflow Systems Orchestrator.
- Establish a per-skill input/output schema, secret/data classification, permissions, host support, negative tests and acceptance receipt for each capability selected for the pilot.
- Reconcile source inventory counts in README: the observed catalog has 5 integrated submodules, 2 candidate repositories, 15 pending repositories and 1 legacy redirect. A README statement saying 14 pending identities is stale by one.
- Keep all capability execution blocked until the named host passes real acceptance; do not infer readiness from a skill count or passing catalog validator.

## 8. UEDE recommendation

For the first engineering pilot, use the HSO plan-only planner and a synthetic repository task. SDO may be evaluated for skill/plugin package changes after parity remediation; Ponytail methodology can inform minimal-change planning; A.S.F.R.E.E is restricted to non-commercial forensic/QA use after parity remediation. Do not route actual code-writing to Plugin Agent Orchestrator or any package-only identity until its source, rights and host are verified.

P1 outcome: **the inventory is complete, the capability supply is classified, and the operational blockers are explicit. No generic autonomous engineering workforce is currently certified as live.**
