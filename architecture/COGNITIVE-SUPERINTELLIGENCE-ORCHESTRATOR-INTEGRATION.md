# Cognitive Superintelligence Orchestrator — HSO Integration Contract

**Document status:** Architecture proposal / draft integration contract  
**Revision:** 0.1.0  
**Date:** 2026-11-25  
**Parent ecosystem:** Hypersystem-Orchestrator (HSO)  
**Plugin identity:** `plugins_6b06658b887c8191901493ecd184ab9a`  
**Plugin release:** `pluginrel_6b06658f0acc81918106d8df18a9971c`  
**Plugin Creator URL:** https://chatgpt.com/plugins/plugins_6b06658b887c8191901493ecd184ab9a

## 1. Purpose

Cognitive Superintelligence Orchestrator (CSO) is a specialist cognitive-intelligence plugin for structured thinking, learning design, communication-pattern reflection, adversarial reasoning, behavioral experiments, knowledge synthesis, competitive strategy and multi-perspective review.

CSO is a **domain specialist inside the HSO portfolio**, not a replacement for HSO, SKILL ANALYZER, A.S.F.R.E.E, Evaluator Team, Skill Developer Orchestrator (SDO), AI Workflow Systems Orchestrator or Progressive Roadmap Evaluator (PRE).

The package is currently stored in Plugin Creator as USER / PRIVATE, version 0.1.0. Its file inventory was read back and contains one master orchestrator, eight specialist skills, two reference documents and ten acceptance cases. Package creation and file read-back do not prove host activation, tool invocation or runtime behavior.

## 2. Capability decomposition

The ten source protocols are retained as eight specialist skills. Overlapping responsibilities are combined without deleting the original user-facing intent.

| Source protocol | CSO specialist | Responsibility |
|---|---|---|
| Mind Reader Protocol | `cognitive-pattern-profiler` | Analyze observable communication patterns, decision language and recurring reasoning tendencies. |
| 80/20 Hack | `accelerated-learning-architect` | Design a focused learning path using Pareto analysis as a testable heuristic, deliberate practice, feedback and retention. |
| Extreme Devil's Advocate | `adversarial-thinking-engine` | Attack assumptions, test evidence and construct the strongest fair counterargument. |
| Contrarian Position Builder | `adversarial-thinking-engine` | Build an evidence-aware opposing position; distinguish disagreement from contrarian performance. |
| Deep Psychology Decoder | `behavioral-mechanism-explorer` | Map observable behavior loops and propose explicitly tentative mechanisms. |
| Pattern Interruption | `behavioral-mechanism-explorer` | Design safe, reversible behavior experiments with observable outcomes. |
| Wisdom Extraction Tool | `wisdom-extraction-engine` | Extract high-value principles while separating source-supported claims from interpretation. |
| Competitive Framework | `competitive-strategy-intelligence` | Map the competitive arena, alternatives, constraints and strategic options. |
| Reality Distortion Generator | `perspective-reframing-lab` | Reframe a situation through declared strategic archetypes and alternative assumptions. |
| Expert Panel Simulator | `multidisciplinary-expert-panel` | Simulate distinct disciplinary lenses, disagreements and evidence requests without claiming real expert participation. |

The package contains these nine skills:

1. `cso-master-orchestrator`
2. `cognitive-pattern-profiler`
3. `accelerated-learning-architect`
4. `adversarial-thinking-engine`
5. `behavioral-mechanism-explorer`
6. `wisdom-extraction-engine`
7. `competitive-strategy-intelligence`
8. `perspective-reframing-lab`
9. `multidisciplinary-expert-panel`

## 3. HSO responsibility boundaries

### 3.1 CSO owns

- Structured cognitive reflection when the user explicitly wants to understand observable communication or reasoning patterns.
- Learning-path design, practice sequencing and progress measures for a named skill.
- Adversarial examination of beliefs, arguments and decisions.
- Non-clinical exploration of behavior loops and safe behavioral experiments.
- Evidence-aware knowledge synthesis and strategic perspective reframing.
- Simulated multi-disciplinary review with named lenses, dissent and unresolved questions.

### 3.2 CSO does not own

- General analytical methodology selection across arbitrary domains. **SKILL ANALYZER** owns that responsibility.
- Technical anatomy, reverse engineering or reconstruction of AI plugins and software systems. **A.S.F.R.E.E Canonical** owns that technical case.
- Independent quality scoring or acceptance judgement of CSO or another plugin. **Evaluator Team** owns independent evaluation.
- Prompt engineering under the complete eight-pillar Octa-Prompt structure. **Anatomi Prompt** owns prompt architecture.
- Reusable workflow/SOP/system architecture. **AI Workflow Systems Orchestrator** owns reusable workflow architecture.
- Project-roadmap governance, milestone acceptance and adaptive roadmap evaluation. **PRE** owns those lifecycle decisions.
- Source repository writes, release preparation or implementation of an accepted plugin change. **SDO** owns that engineering lifecycle.
- Business-domain operating decisions or authoritative market facts. **GrowthForge** remains the business-domain owner when business execution is the dominant objective.

### 3.3 Routing precedence

Select one primary owner based on the requested final artifact or decision, not merely on keywords.

| Dominant intent | Primary owner | Optional handoff |
|---|---|---|
| Improve thinking habits, learn a skill, inspect communication patterns, challenge a belief or design a behavior experiment | CSO | SKILL ANALYZER for a general method blueprint; Evaluator Team for independent quality evaluation |
| Analyze an external problem using the best analytical methodology | SKILL ANALYZER | CSO only for a separate cognitive/learning deliverable |
| Inspect a plugin's manifest, skill tree, tools, permissions, dependencies or failure paths | A.S.F.R.E.E | SDO for accepted implementation |
| Engineer or audit a prompt against eight Octa-Prompt pillars | Anatomi Prompt | CSO only if the prompt is itself a cognitive-learning artifact |
| Design reusable workflows, SOPs or modular work systems | AI Workflow Systems Orchestrator | CSO may supply a bounded cognitive practice module |
| Build/evaluate a project roadmap or accept milestones | PRE | CSO may supply learning or behavior-change work packages |
| Independently score a skill/plugin or verify redesign quality | Evaluator Team | SDO implements only accepted findings |
| Modify the CSO package or source repository | SDO | A.S.F.R.E.E, Octa-Prompt and Evaluator Team contribute bounded findings |

Do not activate all adjacent specialists as a default panel. Add a supporting system only when it has a separate required artifact or control. The originator of a handoff remains responsible for the truth of its own output.

## 4. Evidence and epistemic guardrails

Every material claim must be distinguished as one of:

- **OBSERVED** — directly visible in the supplied conversation, artifact or data.
- **SOURCE_SUPPORTED** — supported by an identified source.
- **INFERENCE** — reasoned interpretation from available observations.
- **HYPOTHESIS** — plausible explanation that still requires testing.
- **UNKNOWN** — evidence is insufficient or unavailable.

Non-negotiable constraints:

1. “Mind Reader” is a metaphor, not a capability claim. CSO cannot read private thoughts or infer hidden motives as fact.
2. Psychological language must remain non-diagnostic. CSO must not diagnose mental illness, claim certainty about subconscious causes or replace professional care.
3. Behavioral interventions must be proportionate, reversible and safe. High-risk, coercive or medically significant interventions are outside scope.
4. A Pareto 80/20 split is a heuristic, not a universal law or a guaranteed path to mastery.
5. A simulated expert panel is not a real panel. Do not fabricate expert credentials, interviews, citations or consensus.
6. Named-person reframing is a hypothetical interpretation of publicly documented principles, not a claim about what that person would certainly do.
7. Competitive claims, market share, prices and current market conditions require current evidence. Never invent competitor data.
8. Five insights should not be forced when the source supports fewer distinct insights. Preserve source limitations and counterevidence.

## 5. Standard CSO handoff contract

Each specialist handoff should preserve:

- `request_id`, `plugin_key`, `skill_name`, package version and release ID;
- user intent, desired decision/artifact and declared scope;
- source locators, timestamps and evidence labels;
- assumptions, uncertainties, counterevidence and method limitations;
- specialist output and confidence rationale;
- risks, stop conditions and any required human decision;
- receiving owner, expected artifact and acceptance criteria.

A successful handoff is not proof of execution by the receiving host. Record separately: selected, available, invoked, completed, verified and accepted.

## 6. HSO integration status at this revision

| Integration plane | Current disposition | Evidence / limitation |
|---|---|---|
| Plugin Creator package | **CREATED — USER / PRIVATE — 0.1.0** | Exact plugin ID and release ID recorded above; package file inventory was read back. |
| Independent canonical Git source | **NOT IDENTIFIED** | No dedicated child repository or immutable source commit has been registered. The current GitHub connector exposes repository read/write and PR operations, but no repository-creation operation. |
| HSO catalog registration | **DEFERRED** | Main currently records 23 plugin identities. Active PRs #12, #15, #18 and #22 touch adjacent source-onboarding, catalog/version or regression surfaces. This proposal intentionally avoids overwriting those baselines. |
| Distribution | **NOT ELIGIBLE / PRIVATE SNAPSHOT ONLY** | Canonical source, package-wide licence review, distributable artifact and host-tested adapter are not established. |
| Generic HSO plugin dispatch | **BLOCKED / NOT CONFIGURED FOR CSO** | The current runtime capability registry contains a specifically scoped SKILL ANALYZER Remote MCP adapter; it is not a generic CSO adapter and must not be reused as one. |
| Named-host activation / live runtime | **NOT RUN** | No CSO host activation or live invocation evidence is asserted. |
| Notion / Mission Control automatic sync | **NOT VERIFIED** | This document can be created directly in Notion; that does not establish the separate HSO webhook/reconciliation pipeline, whose connector secrets and source configuration remain outstanding in the HSO runbook. |

This document is an architecture proposal and integration contract. It does not silently add CSO to `catalog/plugins.json`, `catalog/distribution-registry.json`, `catalog/instruction-snapshots.json` or `catalog/compatibility-matrix.json`. Those source-of-truth updates require the pending PR baselines to be reconciled and an independent canonical source decision.

## 7. Progressive integration roadmap

| Stage | Outcome | Exit evidence |
|---|---|---|
| R0 — Intake | Confirm CSO scope, identity and non-ownership boundaries | Owner-reviewed scope and canonical plugin identity |
| R1 — Source baseline | Create/identify a dedicated canonical Git repository; decide visibility, licence and maintainers | Repository metadata, source tree, manifest, licence/NOTICE and immutable commit |
| R2 — Contract design | Register CSO in HSO catalog, source/distribution registries, instruction pointer and routing documentation | Schema validation; no duplicate owner; source/version/provenance fields reconciled |
| R3 — Approval and baseline freeze | Independent technical, rights and security review | Human approval, rights disposition, threat review and frozen baseline SHA |
| R4 — Integration execution | Implement a named, least-privilege host adapter for CSO | Adapter tests, authentication/authorization checks, failure and recovery tests |
| R5 — Formative check | Exercise the eight specialists and all ten original use cases | Acceptance-case results, evidence ledger and regression report |
| R6 — Milestone acceptance | Verify package/source parity and host behavior | Exact-head CI, read-back, named-host activation evidence and independent acceptance |
| R7 — Outcome and impact | Evaluate learning, decision quality and behavior-experiment utility | Baseline-backed outcome measures; no fabricated progress or causal claims |
| R8 — Adaptation | Re-sequence or change modules based on observed evidence | Approved change record, regression and preserved prior baseline |
| R9 — Closure and learning | Approve release disposition or record residual blockers | Signed-off acceptance, release record, rollback plan and lessons learned |

### Immediate blockers

1. A dedicated canonical source repository has not been created or accepted.
2. Source licensing and redistribution rights have not been assessed.
3. HSO catalog and version-reconciliation changes are under active review; no duplicate edits should be made until those PRs are reconciled.
4. HSO does not currently expose a generic, verified CSO skill-invocation adapter.
5. Automatic HSO GitHub-to-Notion reconciliation still requires the external configuration described in the HSO Mission Control runbook.

## 8. Acceptance and release gates

CSO may be described as **package-created** now. It must not be described as HSO-integrated-runtime-ready or distributable until all applicable gates pass.

- **Source gate:** canonical repository, ownership, licence, manifest, release and immutable source commit verified.
- **Catalog gate:** one-to-one catalog, distribution and instruction-index records validated against schemas and regression tests.
- **Parity gate:** all nine package skill files and references compared against the canonical repository; drift is recorded, not hidden.
- **Security gate:** authorization, data privacy, prompt injection, secret handling, untrusted source content and unsafe behavioral advice reviewed.
- **Host gate:** named adapter activation and actual CSO invocation tested on the declared target platform.
- **Acceptance gate:** ten source-use-case tests executed, failures and limitations recorded, and independent evaluation completed.
- **Release gate:** human approval, rollback disposition and exact release artifact verified.

No merge, public publication, installation, host activation, production deployment or automatic approval is implied by this document.
