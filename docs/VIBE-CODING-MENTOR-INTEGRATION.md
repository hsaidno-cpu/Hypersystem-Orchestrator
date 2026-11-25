# Vibe Coding Mentor — HSO Integration Record

**Plugin key:** vibe-coding-mentor  
**Plugin Creator:** https://chatgpt.com/plugins/plugins_6b0744bffe9c8191a5eb9c932fcc3f24  
**Package:** 0.1.0 · USER / PRIVATE · release pluginrel_6b0744c2806481919620bdf8b8719f57  
**Canonical source:** https://github.com/hsaidno-cpu/vibe-coding-mentor  
**Pinned commit:** 84214752bb298002b96f9ff1c60e16b7a09e99d7  
**HSO base:** main after PR #33 merge at 0d718fe52e9d16dc95f4a07c0f28aa8285ea952f  
**Integration branch:** feat/vibe-coding-mentor-20261126-r2

## Purpose and boundary

Vibe Coding Mentor translates non-IT product intent into a traceable PRD, MVP scope, user flows, product logic, acceptance criteria and staged prompts for AI coding builders. It produces specifications and prompts; it does not execute, deploy or publish applications.

## Modular architecture

One master orchestrator and nine specialists:
- vibe-coding-mentor — master orchestration and readiness decision
- idea-intake-discovery — idea normalization and unknowns
- problem-user-audience-architect — problem, actors and target audience
- mvp-requirements-scope-architect — requirements, prioritization, MVP and non-goals
- user-flow-ux-spec-architect — user journeys, screens and states
- product-logic-data-architect — business rules, conceptual data and access
- stack-cost-advisor — technology, cost and free-tier limits
- builder-platform-adapter — target builder instruction adaptation
- prd-to-builder-prompt-compiler — accepted PRD to staged builder prompts
- prd-quality-gate — PRD completeness, traceability and risk gate

## Existing HSO ownership boundaries

Anatomi Prompt owns universal Octa-Prompt design. AI Prompt Finder & Creator owns source-content/reference-to-prompt reconstruction. Executive Workday Orchestrator owns workday operations and its workday prompt-generator. AI Workflow Systems Orchestrator owns reusable workflow/SOP architecture. GrowthForge owns commercial strategy and validation. SDO owns plugin source lifecycle. Evaluator Team owns independent acceptance.

VCM's prompt compiler is narrowly PRD-to-builder, not a generic prompt generator.

## Canonical source and parity

| Evidence | State |
|---|---|
| Private repository | Created and verified: hsaidno-cpu/vibe-coding-mentor |
| Canonical source commit | 84214752bb298002b96f9ff1c60e16b7a09e99d7 |
| Plugin Creator release | pluginrel_6b0744c2806481919620bdf8b8719f57, v0.1.0 |
| File parity | PASS — 18/18 manifests, references and skills byte-for-byte identical |
| Source package CI | PASS — run 45701037593; static validator + 4 tests |
| Public license/redistribution rights | NOT_ASSESSED; no license assigned |
| Distribution | private_source_restricted; no artifact published |

## HSO routing and runtime boundary

Route key: `plugin.vibe_coding_mentor_prd`  
Primary owner: `vibe-coding-mentor`  
Action: `plugin.skill.invoke`  
Required capability: `plugin.skill.invoke`

The route is declarative and the planner may select VCM as the correct owner. The generic capability remains `NOT_CONFIGURED`. HSO must block this route with `BLOCKED_CAPABILITY` until a dedicated, authenticated VCM host adapter and endpoint exist. The current HSO Remote MCP adapter is a one-skill pilot for SKILL ANALYZER and must not be reused or relabelled for VCM.

## Acceptance and maturity

| Gate | Evidence / criterion | Current state |
|---|---|---|
| Canonical source | Private repository, immutable commit and version | PASS |
| Package parity | 18/18 files exact-match Plugin Creator release | PASS |
| Static package validation | Exact source commit validator + 4 unit tests | PASS |
| HSO registry | Catalog, repository registry, snapshot index and distribution policy | IMPLEMENTED_ON_BRANCH |
| HSO route selection | VCM is the explicit primary owner for PRD work | IMPLEMENTED_ON_BRANCH |
| HSO invocation | Dedicated host adapter, identity, TLS/OIDC, scopes and invocation receipt | NOT_CONFIGURED / NOT_RUN |
| PRD behavior acceptance | Positive, negative, missing-input, contradiction and boundary prompt behavior | NOT_RUN |
| Cursor | Actual IDE session, generated code, diff and test evidence | NOT_RUN |
| Bolt.new | Actual builder session and result evidence | NOT_RUN |
| Lovable | Actual builder session and result evidence | NOT_RUN |
| License/distribution | Rights, attribution and approved license | NOT_ASSESSED / BLOCKED |
| Production readiness | Independent security/evaluation and real runtime operations | NOT_ESTABLISHED |

## Stop conditions

Do not add VCM to the HSO runtime capability allowlist, publish an installable artifact, or call VCM from HSO until a named private endpoint, authentication mechanism, scope policy and actual invocation receipt are verified. A catalog record or source package alone does not establish runtime execution.
