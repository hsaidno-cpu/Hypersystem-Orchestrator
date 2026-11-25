# Vibe Coding Mentor — HSO Integration Record

**Catalog key:** `vibe-coding-mentor`  
**Plugin Creator:** [Private package](https://chatgpt.com/plugins/plugins_6b0744bffe9c8191a5eb9c932fcc3f24)  
**Package:** `0.1.0` · `USER / PRIVATE` · release `pluginrel_6b0744c2806481919620bdf8b8719f57`  
**HSO dependency baseline:** [PR #33](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/33), head `cda66a02988f2754ca8a15a134e097e4c674c380`  
**Integration branch:** `feat/vibe-coding-mentor-20261126`

## 1. Purpose and HSO position

Vibe Coding Mentor helps a non-IT project owner convert an idea for a digital product into a Product Requirements Document (PRD) that an AI coding builder can interpret. It separates MVP from future scope, identifies actors and user flows, describes product logic and conceptual data, adds testable acceptance criteria, and compiles a sufficiently stable PRD into staged prompts for Cursor, Bolt.new, Lovable, or a vendor-neutral builder.

It is a **domain-specialist product discovery and PRD plugin** inside the HSO portfolio. It is not an application builder, IDE, code execution environment, hosting provider, database service, or deployment agent.

## 2. Functional architecture

One M00 master orchestrator coordinates nine specialist skills:

| Category | Skill | Responsibility |
|---|---|---|
| Core orchestration | `vibe-coding-mentor` | Mode selection, evidence labels, specialist routing, PRD structure, prompt-only boundary and completion gate |
| Discovery | `idea-intake-discovery` | Normalize rough ideas, preserve original intent, capture constraints, assumptions and unknowns |
| Problem / audience | `problem-user-audience-architect` | Problem statement, actors, user goals, use cases, audience and permissions |
| Requirements / MVP | `mvp-requirements-scope-architect` | Requirement IDs, priority, MVP, future scope and non-goals |
| UX / flows | `user-flow-ux-spec-architect` | User journeys, screen inventory, interaction, states, validation and error paths |
| Product logic / data | `product-logic-data-architect` | Business rules, conceptual entities, lifecycle, access and integration contracts |
| Stack / cost | `stack-cost-advisor` | Conditional technology choice, pricing/limits verification, total cost and migration/lock-in |
| Builder adaptation | `builder-platform-adapter` | Platform-specific prompt constraints based on current official documentation |
| Prompt compilation | `prd-to-builder-prompt-compiler` | Compile an accepted PRD into staged planning, implementation, QA and handoff prompts |
| Quality gate | `prd-quality-gate` | Completeness, consistency, assumptions, traceability, risk and acceptance readiness |

Six support references are included: PRD template, builder prompt patterns, platform adaptation matrix, free-tier verification, acceptance case matrix and non-IT glossary.

## 3. Primary ownership and non-duplication

| Existing HSO component | Owns | Vibe Coding Mentor boundary |
|---|---|---|
| Anatomi Prompt V3.0 — Octa-Prompt | Universal prompt anatomy and eight-pillar structural design/audit | May use Octa-Prompt quality principles, but does not own universal prompt architecture |
| AI Prompt Finder & Creator | Analyze supplied image/video/document/design/content/references and reconstruct a prompt | Vibe Coding Mentor starts from product intent/PRD; it is not a source-media prompt reconstruction engine |
| Executive Workday Orchestrator | Workday tasks, projects, meetings, communication, notes and domain-specific prompt generation | EWO's `prompt-generator` remains workday-specific; VCM's `prd-to-builder-prompt-compiler` requires a product PRD and emits builder implementation prompts |
| AI Workflow Systems Orchestrator | Reusable workflow, SOP, modular skills and project/workspace architecture | VCM defines a software product's user flows and requirements, not general workflow architecture |
| GrowthForge Business OS | Business strategy, customer/market, business model, finance and commercial decisions | GrowthForge owns business validation; VCM converts an approved product intent/brief into application requirements |
| Skill Developer Orchestrator | Plugin/skill source engineering, tests, GitHub changes and release lifecycle | VCM owns PRD artifacts only; SDO owns implementation of VCM's own plugin/skill source |
| Evaluator Team | Independent quality judgement and acceptance recommendation | VCM's PRD self-check is not independent certification |

### Routing rule

Choose Vibe Coding Mentor when the desired deliverable is a PRD for a digital product or a prompt that compiles that PRD for an AI coding builder. Choose Anatomi Prompt for universal prompt design, AI Prompt Finder for reference/content-to-prompt reconstruction, WSO for reusable workflows, EWO for workday operations, and GrowthForge for business decisions.

## 4. Core operating safeguards

- Missing facts remain explicit placeholders such as `[Target pengguna belum ditentukan]`; assumptions and proposals are labelled separately.
- Login, dashboard, admin panel, payment, notifications and other common features are not forced into a PRD without an evidenced requirement.
- MVP, future scope and out-of-scope are separated.
- Every material MVP requirement is linked to an ID and observable acceptance criteria.
- The builder prompt preserves requirement IDs, scope boundaries, unresolved decisions and tests.
- Prompt-only output does not claim builder execution, code changes, testing, deployment or publication.
- Cost and free-tier claims are checked against official pricing/product documentation at recommendation time. A zero-price plan is not treated as unlimited or guaranteed free forever.
- Destructive migrations, data deletion, paid service activation, deployment and publication remain human-approved external actions.

## 5. Evidence and maturity

| Evidence item | Observed state |
|---|---|
| Plugin Creator package | Created; version 0.1.0; USER/PRIVATE |
| Package file inventory | Read back: 10 `SKILL.md` files, 6 references, no missing paths reported |
| Current Plugin Creator release | `pluginrel_6b0744c2806481919620bdf8b8719f57` |
| HSO catalog registration | Implemented on this dependent branch; PR review/merge pending |
| Private source pointer | Added; full private instructions not mirrored into public GitHub |
| Canonical child Git source | `NOT_IDENTIFIED` |
| License / distribution rights | `NOT_ASSESSED` |
| Distribution state | `snapshot_only`, not installable |
| Compatibility contract edge | Not added; no verified inter-plugin executable handoff has been established |
| HSO runtime dispatch / named-host activation | `NOT_RUN` / `NOT_CONFIGURED` |
| Cursor/Bolt/Lovable target behavior | `NOT_RUN` |
| Production readiness | `NOT_ESTABLISHED` |

## 6. HSO registration and runtime boundary

The catalog, instruction pointer, distribution registry, and responsibility/routing documentation establish **static ecosystem registration**. They do not activate a dispatch route. The runtime routing policy is intentionally unchanged because no Vibe Coding Mentor host adapter or executable invocation contract has been verified. The compatibility matrix remains unchanged because no tested cross-plugin handoff is being claimed.

The parent HSO repository remains an ecosystem control plane, not a monorepo. A future canonical child Git source must be separately identified and approved. The USER/PRIVATE Plugin Creator package remains the current package authority until source provenance, license, parity and release reconciliation are established.

## 7. Acceptance criteria for future maturity

1. Establish a canonical child Git source repository and confirm ownership/provenance/license.
2. Reconcile all 10 skill files and 6 references to the source, pin an immutable commit and verify package/source parity.
3. Run positive, negative, missing-input, contradictory-requirement, boundary and adversarial routing cases.
4. Test PRD quality with requirement-to-acceptance traceability and no fabricated assumptions.
5. Test generated builder prompts on named Cursor/Bolt/Lovable versions and plans, including inspection-first, no-scope-creep, safe-migration and evidence-reporting cases.
6. Verify pricing, free-tier limits, commercial-use terms and cost estimates against official provider sources at point of recommendation.
7. Define HSO host adapter/contract before adding executable runtime routing or compatibility edges.
8. Run independent Evaluator Team review and regression before any public distribution/production-ready claim.

## 8. Current disposition

`PACKAGED_PRIVATE / HSO_REGISTRATION_PENDING_PR / SNAPSHOT_ONLY / HOST_TEST_NOT_RUN`.

This integration does not claim a merged HSO plugin, public installability, host activation, AI builder execution, tested application output, deployment or production readiness.
