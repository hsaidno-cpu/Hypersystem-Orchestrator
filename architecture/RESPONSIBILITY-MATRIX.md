# Responsibility and Routing Matrix

This matrix is normative for ecosystem-level routing. The detailed product philosophies, non-ownership boundaries and handoff rules are in [PLUGIN-POSITIONING.md](PLUGIN-POSITIONING.md).

## 0. Ecosystem-level control-plane boundary (outside the plugin catalog)

**Hypersystem Orchestrator (HSO) is the parent ecosystem control plane, not an additional plugin identity or a domain-specialist substitute.** It coordinates the use of the registered plugin portfolio; it does not duplicate their internal expertise or claim that a runtime dispatcher is deployed.

HSO owns the cross-ecosystem control concerns:

- request intake, scope and authority classification;
- catalog/source/version/provenance lookup;
- selection of exactly one primary plugin owner for each work package;
- dependency ordering and construction of explicit handoff plans;
- enforcement of shared contract, evidence, status and stop semantics;
- aggregation of results, test evidence, unresolved risks and roadmap handoffs;
- parent-repository governance, source pins, compatibility and distribution eligibility records.

HSO does **not** own the specialist decisions below: general analytical method selection (SKILL ANALYZER), plugin technical forensics (A.S.F.R.E.E), independent quality judgement (Evaluator Team), skill/plugin source engineering (SDO), reusable workflow design (AI Workflow Systems Orchestrator), roadmap progression/adaptation (PRE), or agent runtime implementation/operation (Plugin Agent Orchestrator). It does not override domain truth owners such as PVEE.

Routing invariant: HSO may coordinate several work packages, but every package has one primary decision owner. Supporting specialists are added only when they produce a distinct required artifact or control. A registry record, instruction snapshot, or declared handoff is not proof that a host can invoke the named plugin.

For the intended operating sequence and maturity gates, see [SUPER-ORCHESTRATOR-CONTROL-PLANE.md](SUPER-ORCHESTRATOR-CONTROL-PLANE.md).


## 1. Primary route by dominant intent

| Dominant user intent | Primary plugin | Supporting plugin when needed | Do not route to |
|---|---|---|---|
| General analytical methodology for a business, policy, organization, social, strategic, technical or decision problem | SKILL ANALYZER | Evaluator Team, GrowthForge, A.S.F.R.E.E for a plugin anatomy case | A.S.F.R.E.E solely because the word “system” appears |
| Forensic anatomy and reconstruction of an AI plugin/skill/agent | A.S.F.R.E.E Canonical | SKILL ANALYZER for methods; Agent Jailbreak DS for security; SDO for engineering lifecycle | A.S.F.R.E.E Legacy |
| Independent skill/plugin evaluation, scoring, ranking or redesign | Evaluator Team | SKILL ANALYZER for analytical methods; Anatomi Prompt for eight-pillar structure | SDO as independent judge of its own implementation |
| Build, modify, reconstruct, test or release an AI skill/plugin | Skill Developer Orchestrator | A.S.F.R.E.E, Evaluator Team, Anatomi Prompt | Multiple simultaneous write owners |
| Audit or construct a prompt using eight Octa-Prompt pillars | Anatomi Prompt V3 — Octa-Prompt | AI Prompt Finder before it when a prompt must first be reconstructed from content | Prompt Finder as a substitute for eight-pillar structural audit |
| Analyze image/video/document/design/content and turn it into a prompt | AI Prompt Finder & Creator | Anatomi Prompt for optional eight-pillar hardening | Anatomi Prompt alone when the source content itself must be analyzed |
| General photo edit, retouch, object/background, product photo or visual enhancement | Photo Fixer | Master Photo Restoration only when restoration is the actual task | Master Photo Restoration for ordinary editing |
| Restore an old/damaged/faded/blurred/archival photo | Master Photo Restoration | Photo Fixer only for separate general-editing work requested in addition | Photo Fixer as the primary restoration specialist |
| Audio/VO analysis, transcript provenance, timing, caption timing, sound and mix | GODEX Motion Audio | Motion Graphic or Video Explainer for visual/renderer work | Motion Graphic as owner of audio provenance |
| General visual-first motion graphics/explainer production | Motion Graphic by arifanara | GODEX for audio/VO; Prompt Finder for references | PVEE unless the work is health communication |
| Health-promotion campaign, claim verification, Fact Lock, safe wording or audience impact | PVEE Promkes Super Orchestrator | Video Explainer, GODEX, Motion Graphic | Generic motion/audio plugin as health-truth authority |
| Renderer-neutral technical production of an approved health explainer | Video Explainer Promkes | PVEE for approved health package; GODEX for audio; Motion Graphic for visual language where needed | PVEE as the renderer/production-code executor |
| Defensive jailbreak, prompt-injection, context-poisoning and agent tool-security work | Agent Jailbreak Skill DS | A.S.F.R.E.E for broader technical forensics; Plugin Agent Orchestrator for agent context | Offensive unauthorized target testing |
| Design, build, deploy, operate or scale an AI agent | Plugin Agent Orchestrator | Agent Jailbreak DS, Workflow Systems, GrowthForge | SDO unless the target object is a plugin/skill package |
| Design reusable workflows, SOPs, modular skill systems and project orchestration | AI Workflow Systems Orchestrator | Cortex Workbench, Plugin Agent Orchestrator | Plugin Agent Orchestrator unless an agent product is actually required |
| General learning, research, writing, thinking, productivity or coding | Cortex Workbench | SKILL ANALYZER, CommandCraft 56 | GrowthForge unless the main goal is business |
| Use a compact named command mode from the 56-command catalog | CommandCraft 56 | Cortex or GrowthForge as domain support | Assuming text aliases create native UI commands or runtime tools |
| Discover, inventory, map, classify or stage adoption of a skill/capability library | Agent Skills Atlas | SKILL ANALYZER, Workflow Systems | Treating a discovered/mapped skill as executable |
| Develop or evaluate a person's/team's observable People Skills or Business Skills, including learning practice and transfer | People & Business Competency Academy | GrowthForge for a distinct business deliverable; Agent Skills Atlas only for an AI-capability inventory | Routing individual competency development to GrowthForge or treating reading completion as mastery |
| Business model, market/customer, product, brand, finance, marketing, sales or operations | GrowthForge Business OS | Cortex, CommandCraft | General knowledge-work routing when business is dominant |
| Access the retired A.S.F.R.E.E identity | A.S.F.R.E.E Canonical via Legacy redirect | None | Legacy execution or Legacy fallback |

## 2. Hard ownership boundaries

| Decision / artifact | Single owner | Handoff contract |
|---|---|---|
| General analytical method selection | SKILL ANALYZER | Method Blueprint with question, assumptions, evidence needs and method limits |
| Plugin/package anatomy and forensic reconstruction case | A.S.F.R.E.E | Evidence dossier, component map, dependency/permission map and change assurance |
| Independent evaluation score and acceptance recommendation | Evaluator Team | Scoring rubric, findings, evidence, severity, recommendation and acceptance criteria |
| Integrated skill/plugin engineering lifecycle | SDO | Requirement trace, change manifest, tests, read-back, PR and release evidence |
| Eight-pillar prompt architecture | Anatomi Prompt | Octa-Prompt master prompt and structural validation |
| Source-content analysis and reconstructed prompt | AI Prompt Finder & Creator | Observation/inference/unknown map and target-generator prompt package |
| General photo-edit operation | Photo Fixer | Scoped edit plan and QA result |
| Archival/photo restoration operation | Master Photo Restoration | Restoration plan, identity-preservation constraints and reconstruction uncertainty |
| Audio/transcript/VO provenance and audio-post specification | GODEX | Audio dossier, timing classes, caption/audio plan and mix handoff |
| Generic visual design and motion package | Motion Graphic | Visual bible, storyboard, motion/timeline and render handoff |
| Health truth, claims, Fact Lock and campaign governance | PVEE | Approved Fact-Locked Production Brief |
| Promkes media production compiler and renderer-ready package | Video Explainer | Production manifest, media/render QA and technical handoff |
| Defensive AI-agent threat assessment | Agent Jailbreak DS | Threat model, safe test plan, finding register and layered mitigations |
| AI-agent product/runtime lifecycle | Plugin Agent Orchestrator | Agent Definition Package, deployment/operations and ecosystem state |
| Reusable workflow/process architecture | Workflow Systems Orchestrator | Workflow graph, SOP, role/contract/dependency map |
| Broad knowledge-work command routing | Cortex Workbench | Task contract and integrated knowledge-work deliverable |
| 56 text command alias semantics | CommandCraft 56 | Command profile and resolution |
| Capability inventory and adoption maturity | Agent Skills Atlas | Registry record, provenance and lifecycle state |
| Human competency development and learning-to-work transfer | People & Business Competency Academy | Baseline, deliberate practice, simulation, workplace evidence and milestone assessment |
| Business-domain decision/deliverable | GrowthForge Business OS | Business analysis, plan, model, experiment and operating deliverable |
| Legacy A.S.F.R.E.E compatibility | A.S.F.R.E.E Legacy | Canonical migration pointer only |

## 3. Adjacent-domain arbitration

### SKILL ANALYZER vs A.S.F.R.E.E

- Analyzer owns general analytical methodology and how to analyze an issue.
- A.S.F.R.E.E owns technical anatomy of plugins/skills/agents and supervised engineering.
- Analyzer can be a supporting method provider in an A.S.F.R.E.E case, but not a second case orchestrator.

### Evaluator Team vs SDO

- Evaluator Team assesses, scores, judges, challenges and recommends.
- SDO converts accepted requirements into controlled engineering changes, regression, integration and release preparation.
- Evaluator Team may prepare a narrowly scoped patch only when delegated; SDO remains lifecycle owner. One target repository/branch/path has one write owner at a time.

### Anatomi Prompt vs AI Prompt Finder

- Anatomi inspects the prompt as an instruction object and enforces eight pillars.
- Finder inspects source content/reference and turns it into a reconstructed/new prompt.
- Finder → Anatomi is a valid sequence when both content reconstruction and structural hardening are required.

### Photo Fixer vs Master Photo Restoration

- Photo Fixer is the default for ordinary editing.
- Master Photo Restoration is invoked only where deterioration/restoration is the actual purpose.
- Do not route ordinary retouch or background editing to Master Photo Restoration merely because it can improve a portrait.

### GODEX vs Motion Graphic vs PVEE vs Video Explainer

- GODEX owns audio and voice-over truth, timing and audio post.
- Motion Graphic owns general visual-first animation and visual production.
- PVEE owns health information truth, Fact Lock, campaign safety and audience evaluation.
- Video Explainer owns the Promkes production compiler after PVEE approval.
- These systems exchange artifacts; none inherits another's final decision.

## 4. Single-primary and supporting-route policy

1. Pick exactly one primary orchestrator for a task's dominant outcome.
2. Add a supporting plugin only if it owns a distinct output, control or required dependency.
3. Identify who owns the final decision before dispatch.
4. Handoffs must include source/version, input provenance, scope, constraints, capability status, expected output and acceptance criteria.
5. No plugin may override another plugin's domain truth registry or human approval authority.
6. Never infer an actual separate-agent invocation or runtime action from an instruction snapshot.

## 5. Unresolved source-alignment work

The positions above are the central ecosystem's accepted responsibility baseline. Some installed plugin instruction bundles still contain broad orchestrator scopes that overlap adjacent systems. Until their canonical source repositories are identified and their source instructions are reconciled, record those as POSITIONING_ACCEPTED_SOURCE_ALIGNMENT_PENDING. Do not claim each child plugin has already been rewritten.
