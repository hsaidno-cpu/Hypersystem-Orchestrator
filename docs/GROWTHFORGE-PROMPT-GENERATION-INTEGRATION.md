# GrowthForge Business OS v1.2.0 — 120-Prompt Catalog and Business Prompt Architect

**Status:** Plugin Creator package release verified; HSO integration proposed through a reviewable pull request  
**Plugin key:** `growthforge-business-os`  
**Plugin Creator ID:** `plugins_6b01ce5f6c388191816eaee46f4598a2`  
**Plugin Creator release:** `pluginrel_6b067b63b4e88191aeeb74fb6b87f2dd`  
**Version:** `1.2.0`  
**Scope / discoverability:** `USER / PRIVATE`

## 1. Architecture decision

GrowthForge already exists as an HSO plugin identity. This change extends that identity; it does not add a duplicate plugin record.

The supplied 120-entry image is a use-case catalogue, not an architecture of 120 independent agents or executable tools. Use cases route to the smallest sufficient existing GrowthForge specialist. A new cross-cutting `business-prompt-architect` specialist creates reusable business-task prompt artifacts without taking ownership of the underlying business deliverable.

## 2. Category coverage

| Category | Use cases | Primary capabilities |
|---|---:|---|
| C01 — Strategy & Intelligence | 17 | Business strategy, market/customer intelligence, data and financial modeling |
| C02 — Brand & Product | 14 | Brand positioning, product/offer innovation |
| C03 — Demand Generation | 49 | Marketing campaigns, content studio, conversion copy |
| C04 — Revenue & Customer Lifecycle | 24 | Sales, customer experience/community, CRM and growth experiments |
| C05 — Operations & Enablement | 16 | Operations automation, learning products and business documents |
| C06 — Personal Development | 0 | No explicit personal-growth request appears in the supplied image |
| **Total** | **120** | |

Image entries are indexed as `IMG-001`–`IMG-120`, separate from the existing legacy `#1`–`#100` task catalogue. Exact duplicate pairs are retained for source fidelity: `IMG-002/IMG-112` and `IMG-029/IMG-106`. Related variants remain distinct when they change horizon, channel or output.

The six business categories remain intact. Prompt design is a cross-cutting capability, not a seventh business category.

## 3. Prompt-vs-deliverable routing

| Dominant intent | Primary owner | Supporting handoff |
|---|---|---|
| Build a business deliverable | Relevant GrowthForge domain specialist | Only material upstream evidence or dependencies |
| Create/refine/audit/adapt a reusable business-task prompt | GrowthForge Business Prompt Architect | Anatomi only when Octa-Prompt hardening is explicitly requested |
| Analyze supplied media/reference and reconstruct a prompt | AI Prompt Finder & Creator | Anatomi for a later structural hardening step |
| Build/audit the prompt under the eight Octa-Prompt pillars | Anatomi Prompt V3.0 | GrowthForge provides bounded domain context if needed |
| Design generic workflow/SOP/automation architecture | AI Workflow Systems Orchestrator | GrowthForge only for business-domain decisions/deliverables |
| Engineer or release a plugin source package | Skill Developer Orchestrator | Evaluator Team provides independent acceptance judgement; A.S.F.R.E.E supplies technical anatomy when needed |

The Prompt Architect supports BUILD, REFINE, AUDIT, ADAPT, TRANSLATE and LIBRARY modes, with COMPACT, STANDARD and ADVANCED depth. Creating the prompt never executes it. Execution requires a separate user request and separately authorized capability.

## 4. Octa-Prompt interface

When requested, the optional handoff to Anatomi Prompt preserves the exact eight-pillar order:

1. ROLE & PERSONA ARCHETYPE
2. CORE OBJECTIVE & TASK MATRIX
3. CONTEXT & VARIABLE ANCHORS
4. COGNITIVE REASONING & WORKFLOW
5. CONSTRAINTS & NEGATIVE GUARDRAILS
6. EDGE CASES & ERROR HANDLING
7. STOP & COMPLETION CRITERIA
8. OUTPUT SCHEMA & FORMATTING SPEC

GrowthForge owns business context and task intent. Anatomi owns the eight-pillar prompt structure and structural audit. AI Prompt Finder remains the source-content-to-prompt owner.

## 5. HSO integration and private-package boundary

The public parent repository stores only package metadata and concise skill descriptions under `plugin-instructions/growthforge-business-os/SOURCE-POINTER.md`. The older 1.1.1 instruction bundle is historical; no full 1.2.0 prompt contents, prompt templates, private skill instructions or assets are copied here.

The existing 23 plugin identities remain unchanged. The catalog and snapshot index add one skill record, bringing the portfolio total from 265 to 266. GrowthForge now has 19 skill records (18 domain specialists and one master orchestrator). The compatibility matrix adds one optional GrowthForge→Anatomi interface, bringing the declared edge count from 15 to 16.

## 6. Verification and release boundaries

| Plane | State | Evidence / boundary |
|---|---|---|
| Plugin Creator package | **VERIFIED** | Version 1.2.0 and current release metadata read back |
| Package manifests / selected files | **VERIFIED** | 1.2.0 manifests, new prompt skill, 120-use-case catalogue and 42 specification-level acceptance cases read back |
| HSO catalog/snapshot consistency | **TO BE CI-VALIDATED** | New pointer path and 19 GrowthForge skill records |
| Existing 15 HSO handoff edges | **C2/C3 TESTED** | Synthetic schema + mock receiver evidence on PR #15 head; not live plugin execution |
| New GrowthForge→Anatomi edge | **INTERFACE_DEFINED_NOT_EXECUTED** | Static route defined; C2/C3 fixtures not yet added |
| Host activation | **NOT_RUN** | No verified host adapter/selection proof for this edge |
| Runtime execution | **NOT_RUN** | No live plugin-to-plugin invocation or artifact read-back |
| Canonical source repository | **NOT_IDENTIFIED** | No independent GrowthForge Git source designated |
| Source/package parity | **NOT_VERIFIED** | Public pointer is metadata-only; no full source tree to compare |
| Distribution/license | **SNAPSHOT_ONLY / NOT_ASSESSED** | USER/PRIVATE package; no installable HSO package or rights grant |

A successful parent CI run can establish repository and test consistency. It cannot establish host activation, plugin invocation, source parity, rights clearance or business outcomes.

## 7. Acceptance gates

1. The catalog contains exactly 23 plugin identities; no duplicate GrowthForge identity is introduced.
2. The catalog and instruction snapshot both report 19 GrowthForge skill records and a total of 266.
3. Plugin Creator metadata in HSO matches the private package version and release identifier above.
4. The public pointer contains metadata and concise descriptions only; no full private prompt or instruction payload.
5. GrowthForge owns business-task prompt creation; Anatomi owns Octa-Prompt structural hardening; AI Prompt Finder owns source-content reconstruction.
6. The new compatibility edge remains `INTERFACE_DEFINED_NOT_EXECUTED` until dedicated C2/C3 fixtures and mock receiver tests exist.
7. GrowthForge distribution remains `snapshot_only` with private-scope, source-identification and license blockers.
8. No host/runtime test, installation, release or business impact is reported without corresponding evidence.


## 8. v1.3.0 amendment — 26 November 2026

The existing GrowthForge plugin identity was updated in Plugin Creator; this is not a second plugin.

| Field | Verified value |
|---|---|
| Plugin Creator ID | `plugins_6b01ce5f6c388191816eaee46f4598a2` |
| Package version | `1.3.0` |
| Current release | `pluginrel_6b073d4b53588191a4a8fc858381ae65` |
| Scope / discoverability | `USER / PRIVATE` |
| Domain specialists | 18 |
| Master orchestrator | 1 |
| Skill records | 19, unchanged |
| Legacy task namespace | `#1–#100`, unchanged |
| Image-sourced namespace | `IMG-001–IMG-120`, unchanged |
| New guide namespace | `BPG-001–BPG-050`, 50 normalized patterns |

The BPG guide preserves its five source categories: Marketing & Positioning (9), Content & Social Media (10), Sales & Copywriting (9), Email & Customer Relationships (8), and Strategy, Operations & Growth (14). Its overlap classification against the IMG catalogue is 22 DIRECT_MATCH, 17 RELATED_VARIANT and 11 ADDITIONAL_PATTERN. The crosswalk routes the 50 patterns to 13 existing primary domain skills. The cross-cutting Business Prompt Architect remains the prompt-artifact owner; each mapped domain specialist retains ownership of the underlying business task.

The updated package adds:
- A machine-readable BPG pattern catalogue and a private crosswalk with normalized task descriptions, primary owners, supporting skills and overlap classes.
- Prompt-architect instructions for BPG source IDs and separate namespace handling.
- Eight BPG-specific acceptance specifications (GF-BPG-01 through GF-BPG-08). These are specifications, not evidence that target-runtime tests were executed.

The compact R-C-F intake (Role, Context, Format) remains available for simple prompts. Advanced prompts add requirement traceability, evidence and source labels, workflow/dependencies, negative guardrails, edge cases/recovery, stop conditions and acceptance criteria. Full eight-pillar Octa-Prompt structural hardening remains owned by Anatomi Prompt V3.0 when explicitly requested. Reference-media-to-prompt reconstruction remains owned by AI Prompt Finder & Creator.

### Updated verification boundary

| Plane | State | Evidence / limitation |
|---|---|---|
| Plugin Creator v1.3.0 package | VERIFIED | Current release, scope and selected updated files read back after update |
| BPG catalogue | VERIFIED (static/read-back) | 50 unique BPG IDs; category totals 9/10/9/8/14; overlap totals 22/17/11 |
| BPG acceptance cases | SPECIFICATION_PRESENT / NOT_RUN | Eight cases are packaged; no target-host run claimed |
| HSO catalog metadata | PENDING PR #24 | Parent catalog and source pointer must match v1.3.0 release metadata |
| HSO distribution | SNAPSHOT_ONLY | Private USER/PRIVATE package, source repo not identified, rights not assessed, no package artifact |
| GrowthForge canonical Git source | NOT_IDENTIFIED | HSO pointer is not the canonical package source |
| Source/package parity | NOT_VERIFIED | No independent canonical child source exists to compare |
| Host activation and runtime | NOT_RUN | No plugin-to-plugin runtime evidence |

The detailed forensic audit, positive/negative/conversion tables, HSO comparison and complete BPG crosswalk are documented in [Notion — GrowthForge Business OS v1.3.0 forensic audit](https://app.notion.com/p/42399868397f811aaf81c288e7fac26e).
