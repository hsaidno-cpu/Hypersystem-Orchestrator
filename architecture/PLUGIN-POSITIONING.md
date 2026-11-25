# Plugin Positioning, Philosophy and Responsibility Ownership

**Baseline:** ecosystem positioning v1.1  
**Rule:** every plugin has one distinctive reason to exist, one primary responsibility owner and explicit non-ownership boundaries.

A domain overlap is acceptable. Duplicate ownership of the same final decision is not. The system is composed by handoff, not by activating every plugin in the portfolio.

## 1. Four distinct forms of work: analysis, forensics, evaluation and engineering

### 1.1 SKILL ANALYZER — general analytical methodology

**Philosophy:** choose the right way to think about a problem.

SKILL ANALYZER is a methodology engine usable across many domains: business, organization, policy, social issues, strategy, economics, technology, risk, evaluation and decisions.

It owns analytical method selection, method blueprints, problem/system decomposition, root-cause hypotheses, evidence audit, comparative analysis, risk challenge, strategic foresight, solution conversion, evaluation and traceability.

It does not specialize in the technical anatomy of AI plugin packages. It may provide methods to A.S.F.R.E.E, but it does not take over the technical forensic case.

**Call it when:** the central question is how to analyze a topic/problem and which analytical methods should be applied.

**Do not call it merely because:** the target happens to be a plugin. If the main task is a forensic dissection of its manifest, skill tree, tools, code, permissions and dependency architecture, A.S.F.R.E.E owns the case.

### 1.2 A.S.F.R.E.E — forensic anatomy of AI plugins and technical systems

**Philosophy:** expose how the target is built, what it contains, how its parts interact, where its failure paths are, and how to reconstruct it safely.

A.S.F.R.E.E is the specialist for the technical anatomy of plugins, skills, subskills, agents, orchestrators and related software systems.

It owns manifest and package identity inspection; skill/subskill topology and instruction logic; tool/action surfaces, API/MCP contracts, permissions and trust boundaries; dependencies, schemas, references, tests, source and version provenance; failure modes, reverse-engineering depth and implementation evidence; authorized change plans, supervised reconstruction and independent verification.

It does not own general-purpose analytical method selection. It may consume SKILL ANALYZER methods, but A.S.F.R.E.E retains the technical case, authority checks and assurance.

**Call it when:** the object is a plugin/system and the user wants its architecture, components, dependencies, defects, behavior, or rebuild path dissected down to technical detail.

### 1.3 Evaluator Team — independent quality judgement

**Philosophy:** judge the quality of a system, not own its everyday construction.

Evaluator Team independently evaluates an existing skill/plugin/prompt package against explicit criteria. It exposes strengths, weaknesses, score, evidence gaps, architecture risks, benchmark results, recommendations and measurable acceptance conditions.

It owns evaluation frameworks and rubrics, independent scoring, ranking and comparative judgement, quality/effectiveness analysis, evidence review, redesign recommendations, Octa-Prompt architecture proposal, acceptance recommendation and residual-risk judgement.

It does not own the full development lifecycle, repository integration strategy, release management or final merge/release authority. Its implementation helper may prepare or apply a bounded, explicitly accepted patch, but that is not a second lifecycle controller. A single write owner must be assigned.

**Call it when:** the primary deliverable is a judgement about quality, maturity, performance, gaps, score or acceptance.

### 1.4 Skill Developer Orchestrator (SDO) — engineering lifecycle controller

**Philosophy:** turn an accepted requirement or evaluation into a controlled, tested and maintainable engineering change.

SDO owns intake and capability readiness, source baseline, architecture intake and change planning, orchestration of analysis and prompt architecture when needed, controlled source implementation and dependency updates, regression, authentication, evidence and repository handoff, and release preparation.

It does not act as the independent evaluator of its own work. Evaluator Team supplies independent assessment when requested; SDO owns the integrated engineering lifecycle that implements accepted findings.

**Call it when:** a skill/plugin must be created, modified, reconstructed, migrated, tested, versioned or prepared for release.

### The strict separation

| Question | Primary owner |
|---|---|
| Which methodology should analyze this issue? | SKILL ANALYZER |
| What is the technical anatomy of this plugin and how can it be safely reconstructed? | A.S.F.R.E.E |
| Is this skill/plugin good, complete, effective and acceptable? | Evaluator Team |
| How do we implement, test, integrate and prepare the accepted change for release? | SDO |

Typical sequence for a complex plugin change:

A.S.F.R.E.E (technical anatomy, if needed) → Evaluator Team (independent judgement) → SDO (implementation lifecycle) → independent verification

SKILL ANALYZER may supply analytical methods to any stage when method selection is materially needed. It does not become a second technical case controller.

## 2. Prompt anatomy vs content-to-prompt reconstruction

### 2.1 Anatomi Prompt V3.0 — Octa-Prompt

**Philosophy:** inspect the prompt as an engineered instruction object.

It takes an existing prompt or task brief and examines it under eight pillars: role/persona/authority; core objective and task matrix; context and variables; reasoning and workflow; constraints and negative guardrails; edge cases and error handling; stop and completion criteria; output schema and formatting.

It owns structural prompt diagnosis, eight-pillar compliance, master prompt construction, prompt refinement and consistency across pillars.

It does not primarily inspect an image, video, document or other source artifact to infer what prompt could produce it.

### 2.2 AI Prompt Finder & Creator — content/reference to prompt

**Philosophy:** understand the supplied content, extract its meaningful attributes and turn those attributes into a usable prompt.

It accepts accessible images, video, documents, designs, concepts, examples or existing content. It identifies observable content, separates observation from inference and unknowns, then creates or reconstructs a prompt approximation for the intended target generator.

It owns content/reference breakdown, content-to-prompt reconstruction, scene/subject/style/composition/action extraction where evidence permits, prompt creation/optimization/translation and generator adaptation, plus prompt quality checks relevant to fidelity and target-platform use.

It does not own eight-pillar structural auditing as its core responsibility. Anatomi Prompt can receive a Finder-produced prompt for structural refinement when the user needs that additional assurance.

| Input | User intent | Primary plugin |
|---|---|---|
| Existing prompt text | Audit its structure against eight pillars | Anatomi Prompt |
| Idea/task brief | Engineer a structured master prompt | Anatomi Prompt |
| Image/video/document/design/reference | Analyze content and construct an approximate/new prompt | AI Prompt Finder & Creator |
| Prompt generated from a reference, then needs structural hardening | Content analysis first, prompt anatomy second | Finder → Anatomi |

## 3. Photo Fixer vs Master Photo Restoration

### 3.1 Photo Fixer — general photo editing

**Philosophy:** edit the photograph for the user's requested visual outcome.

It owns everyday/professional photo editing: retouching, exposure, white balance, color, lighting, background and object editing, compositing, product/vehicle photography, detail enhancement, crop and social-format preparation.

It does not become the specialist for archival damage restoration simply because the request contains the word “repair”.

### 3.2 Master Photo Restoration — photo restoration only

**Philosophy:** recover the integrity and legibility of an old or damaged photograph while preserving its original identity and historical character.

It owns old/aged/faded/scratched/torn/noisy/blurred/degraded photo restoration, conservative reconstruction, restoration-specific deblur and restoration quality boundaries.

It does not own general beauty retouch, product editing, background replacement, creative compositing or ordinary photo correction when no restoration problem exists.

| Request | Primary plugin |
|---|---|
| Remove a person/object from an ordinary photo | Photo Fixer |
| Change lighting, color, background or composition | Photo Fixer |
| Retouch portrait or improve a product photo | Photo Fixer |
| Restore an old scanned photo with scratches/fading | Master Photo Restoration |
| Repair a damaged archival portrait while preserving identity | Master Photo Restoration |

## 4. GODEX vs Motion Graphic vs PVEE vs Video Explainer

These products may contribute to one media project, but they do not own the same truth or production decision.

### 4.1 GODEX Motion Audio — audio/voice-over-first production

**Philosophy:** preserve and engineer what is heard, how it is spoken, when it happens and how sound supports the narrative.

It owns audio asset inspection and provenance; transcript and speaker segmentation where accessible; word/phrase/segment timing precision and uncertainty labels; voice-over pace, pauses, pronunciation and performance direction; audio-led narrative segmentation and timing handoff; captions/subtitle synchronization tied to audio timing; SFX, BGM, ambience, ducking, mix and audio post; audio quality assurance and renderer/audio handoff.

GODEX may contribute motion/storyboard specifications needed to synchronize visuals to approved audio, but it does not own the overall visual art-direction system for a general explainer.

### 4.2 Motion Graphic by arifanara — visual-first motion production

**Philosophy:** transform a brief or message into a coherent visual language, visual narrative and animated experience.

It owns visual concept and art direction; style, palette, typography, shape language and composition; visual narrative, beat-to-scene and storyboard; motion choreography, keyframes, transitions and kinetic typography; timeline and visual assembly; renderer capability mapping, export planning and visual QA.

It may consume approved VO/audio from GODEX. It does not own authoritative transcript, speaker/timing provenance or audio mix. It also does not own Promkes health-truth decisions.

### 4.3 PVEE Promkes Super Orchestrator — health communication truth and governance

**Philosophy:** decide what health information may be communicated, why it matters to the audience, how it should be framed safely and how communication impact will be evaluated.

It owns health-source inventory and provenance; health-claim atomization and evidence validation; Health Truth Registry, Fact Lock and safe wording; audience, knowledge/attitude/behavior objectives and campaign message; health communication narrative boundaries; risk, privacy, rights, stigma, accessibility and publication governance; audience outcome evaluation and continuous learning; approval-ready Fact-Locked Production Brief.

PVEE is not a generic motion-graphics renderer or audio-post shop. It uses GODEX and Motion Graphic as production specialists when needed.

### 4.4 Video Explainer Promkes — health explainer production engine

**Philosophy:** compile an already approved health-content package into a technically coherent, renderer-neutral production package.

It owns visual identity and continuity implementation; storyboard, shot and scene contracts; motion specifications and scene timing; prompt/reference engineering for production assets; renderer-neutral manifest and renderer adapter; production-level QA, defect register and technical handoff.

It consumes PVEE's approved Fact Lock and campaign brief. It may run a consistency check and flag an evidence mismatch, but it does not silently redefine PVEE's final Health Truth Registry or take over clinical/institutional approval.

**Critical version decision:** target version is V4.1.12. The installed M00 skill currently observed in the connected registry shows v4.0.9. Until the authoritative V4.1.12 source repository/manifest and tests are located, the catalog records V4.1.12 as the selected target, not as a source-verified released version.

### Four-way ownership matrix

| Decision / artifact | Owner | Supporting handoff |
|---|---|---|
| Health claim truth, evidence and Fact Lock | PVEE | Handoff to Video Explainer |
| Audience, behavior objective, safe message and campaign approval package | PVEE | Handoff to Video Explainer |
| VO/transcript provenance, speakers, exactness and audio timing | GODEX | Handoff to Motion Graphic or Video Explainer |
| SFX/BGM/audio mix/caption timing | GODEX | Audio package to production engine |
| Visual style, visual storytelling and generic motion language | Motion Graphic | May accept PVEE brief or GODEX timing |
| Promkes-specific scene/visual/motion/renderer package | Video Explainer | Consumes PVEE fact lock, GODEX audio and visual references |
| Production artifact QA | Respective production QA owner | PVEE receives the report |
| Clinical, legal, institutional or publication approval | Authorized human authority | AI systems advise; they do not approve |

## 5. Remaining portfolio positioning

| Plugin | Distinctive position | Not its job |
|---|---|---|
| Agent Jailbreak Skill DS | Defensive AI-agent threat modeling, prompt-injection and tool-action security | General software/plugin anatomy or offensive unauthorized testing |
| Plugin Agent Orchestrator | AI-agent lifecycle: design, build/operate, deployment, access and ecosystem | Skill/plugin source lifecycle owned by SDO |
| AI Workflow Systems Orchestrator | Reusable workflow, SOP, project, module and orchestration architecture | Agent product lifecycle or plugin source implementation |
| Cortex Workbench | General knowledge-work command workbench | Business-specific OS or specialized command alias catalog |
| CommandCraft 56 | 56 text command aliases and compact task profiles | Native slash-command UI or general case orchestration |
| Agent Skills Atlas | Capability inventory, provenance, taxonomy and adoption maturity | Claiming every mapped skill is executable |
| Ponytail Engineering System | Minimal-complete software change method, codebase mapping, repository audit, contextual change review, risk-based tests and evidence-led engineering debt | Repository write/release lifecycle (SDO), independent quality judgement (Evaluator Team), technical plugin forensics (A.S.F.R.E.E), reusable workflow architecture (WSO) or ecosystem control-plane routing (HSO) |
| People & Business Competency Academy | Human competency diagnosis, learning pathways, deliberate practice, simulation, workplace transfer and evidence-led learner progress | AI capability inventory/adoption, commercial business decisions/deliverables, psychotherapy or claims of competence based only on reading/self-rating |
| GrowthForge Business OS | Business strategy, commercial decisions and operating deliverables; reusable prompts for business tasks through its Business Prompt Architect | General non-business knowledge work, source-content-to-prompt reconstruction (AI Prompt Finder), Octa-Prompt structural authority (Anatomi Prompt), generic workflow architecture (WSO) or technical plugin engineering (SDO) |
| A.S.F.R.E.E Legacy | Redirect/migration identity only | Any new execution, analysis or engineering |
| HSMART | Separate ecosystem infrastructure/platform project | Not a 21st plugin in this catalog |

### Business-task prompt ownership

GrowthForge Business OS owns reusable prompts whose business task domain is within its specialist catalogue. Its Business Prompt Architect is cross-cutting; it is not a seventh business category and does not execute the generated prompt.

- GrowthForge Business Prompt Architect owns the business-task intent, domain variables and prompt artifact.
- Anatomi Prompt V3.0 owns explicit Octa-Prompt construction, eight-pillar structural audit and hardening.
- AI Prompt Finder & Creator owns reconstruction from supplied images, video, documents or other source material.
- AI Workflow Systems Orchestrator owns generic reusable workflow/SOP architecture, not the business-domain prompt artifact.
- SDO owns source-package engineering; GrowthForge does not own its own source release lifecycle.

A GrowthForge-to-Anatomi handoff is optional and declarative. It is not host activation or a runtime invocation.

## 6. Portfolio routing rule

1. Select one primary plugin by the dominant decision/output requested.
2. Add a supporting plugin only when it owns a distinct artifact or mandatory control.
3. A supporting plugin returns a bounded, versioned handoff; it does not seize the primary orchestrator's final decision.
4. Keep one owner for each truth registry, final judgement, source write, release and human approval.
5. Do not infer tool availability, sub-agent invocation or runtime execution from an instruction snapshot.
6. When a plugin's installed skill text still overlaps another plugin's newly clarified boundary, mark it as a source-level alignment task. Do not claim the instruction package itself has been rewritten until its own source repository is updated and read back.

## 7. Non-duplication acceptance criteria

- Every plugin has a unique primary responsibility and positive trigger.
- Every plugin has negative triggers that explicitly reject adjacent work outside its scope.
- Every shared project has one owner for each final decision and canonical artifact.
- Handoffs identify producer, receiver, input/output, version and acceptance criteria.
- Independent evaluation is not performed by the same workstream that approves its own implementation.
- Health-truth decisions remain with PVEE and qualified human authorities.
- Visual production remains separate from audio truth and from health communication governance.

## Ponytail Engineering System — method specialist, not a global orchestrator

**Philosophy:** solve the confirmed software task with the smallest complete change that preserves correctness, security, reliability, accessibility and maintainability. “Smallest” is a complexity discipline, not code golf.

It owns engineering-method intake, affected-code/context mapping, minimal-change option selection, read-only repository audit, contextual diff review, risk-based regression planning, security/reliability checks and evidence-based technical-debt/efficiency reporting.

It does not own source writes, commits, pull requests, merges or releases. SDO owns the engineering lifecycle. It does not replace SKILL ANALYZER for general methodology, A.S.F.R.E.E for forensic plugin anatomy, Evaluator Team for independent judgement, AI Workflow Systems Orchestrator for reusable process architecture, or HSO for ecosystem-level arbitration. No dispatcher, installer, autonomous test runner or production runtime is included.
