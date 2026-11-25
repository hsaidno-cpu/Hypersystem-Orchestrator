# Portfolio Routing and Non-Duplication Contract

**Normative scope:** ecosystem-level routing, domain ownership and handoff boundaries for all 21 plugin identities.

**Core principle:** related work is not duplicated work. Plugins may touch the same object only when they own different questions, artifacts, decisions or technical layers.

> One plugin = one distinctive responsibility. One final decision = one accountable owner. One case = one primary orchestrator.

The parent registry governs cross-plugin routing. Each child plugin remains authoritative for its own internal implementation. When a child instruction bundle still has a broader trigger than this positioning contract, the parent records a source-alignment task rather than pretending the package has already been changed.

## 1. Mandatory routing algorithm

1. Classify the requested outcome, not just the nouns. Determine whether the user wants general analysis, technical plugin anatomy, independent quality judgement, engineering implementation, prompt architecture, content-to-prompt reconstruction, ordinary photo editing, archival restoration, audio engineering, visual motion production, health communication governance or health media compilation.
2. Choose one primary plugin that owns the requested final artifact or decision.
3. Apply negative triggers before selecting support. A broad keyword match never overrides a clear negative trigger or domain owner.
4. Add supporting plugins only for a separate deliverable or mandatory control. Do not invoke every adjacent plugin as a committee.
5. Keep final-decision ownership singular. A supporting plugin may provide evidence, design or a technical artifact; it does not silently take over the primary plugin's final decision.
6. Create a versioned handoff with producer, receiver, source version/commit, expected artifact, authority boundary, evidence and acceptance criteria.
7. If a source capability is unavailable, state that it is not installed/verified and proceed with a bounded alternative. A registry row or instruction snapshot is not runtime availability.

## 2. The five critical separations

### 2.1 SKILL ANALYZER vs A.S.F.R.E.E

| Dimension | SKILL ANALYZER | A.S.F.R.E.E Canonical |
|---|---|---|
| Philosophy | Choose and apply the right analytical methodology to understand a problem | Expose the technical anatomy of a plugin/system and establish how it is built, behaves, fails and can be reconstructed |
| Primary object | Any suitable topic, decision, organization, strategy, policy, market, risk or general system | Plugin, skill, subskill, agent, orchestrator, software package, API/MCP/tooling and related technical system |
| Owns | Method selection, method blueprint, analytical decomposition, evidence reasoning, root-cause hypotheses, comparative analysis, foresight, risk and solution methodology, general evaluation methods | Manifest/package identity, skill tree, tool/action surfaces, schemas, permissions, dependencies, provenance, tests, failure paths, authorized reverse engineering, controlled repair and independent technical verification |
| Output | Analytical dossier, method blueprint, causal/risk analysis, alternatives, evaluation framework and recommendations | Technical anatomy map, component/dependency inventory, authority and permission map, defect/attack-surface register, reconstruction plan, verified engineering evidence |
| Negative boundary | Does not become the technical case controller merely because the object is a plugin | Does not replace general-purpose method selection across unrelated domains |

**Routing rule:** if the question is “metode apa yang tepat untuk menganalisis topik ini?”, call SKILL ANALYZER. If the question is “bedah anatomi plugin ini sampai manifest, skill tree, tools, permission, dependencies, source dan failure path”, call A.S.F.R.E.E. SKILL ANALYZER may supply a method to A.S.F.R.E.E when useful, but A.S.F.R.E.E retains the technical case.

### 2.2 Evaluator Team vs Skill Developer Orchestrator (SDO)

| Dimension | Evaluator Team | SDO |
|---|---|---|
| Philosophy | Judge the quality of a system independently | Engineer an accepted change through a controlled lifecycle |
| Primary question | Is this skill/plugin good, sufficient, effective, safe and acceptable? | How do we create/change, test, integrate and prepare the approved result for release? |
| Owns | Evaluation mandate, rubric, scoring, benchmarking, comparative quality judgement, evidence gaps, independent findings, recommendations and acceptance disposition | Intake, capability gate, source baseline, change plan, implementation ownership, repository writes, branch/PR, regression, provenance, release preparation and engineering handoff |
| Must not own | Final source repository lifecycle, merge authority or self-approval of its implementation | Independent scoring/approval of its own engineering result |

**Single-writer rule:** SDO is the canonical repository-change and engineering-lifecycle owner. Evaluator Team's embedded implementation specialist is treated as a patch-planning/handoff helper when SDO is also engaged; it must not create a competing write owner, branch or release authority. Evaluator Team produces the acceptance recommendation and independent retest criteria; SDO implements accepted work; an independent evaluator verifies the result.

**Default sequence for a material skill change:**

A.S.F.R.E.E anatomy (when technical dissection is needed) → Evaluator Team (independent judgement) → SDO (controlled implementation) → independent verification.

SKILL ANALYZER may contribute general methods, but does not take over the source-write lifecycle.

### 2.3 Anatomi Prompt vs AI Prompt Finder & Creator

| Dimension | Anatomi Prompt V3 — Octa-Prompt | AI Prompt Finder & Creator |
|---|---|---|
| Philosophy | Inspect and engineer the prompt as an instruction object | Inspect the supplied content/reference and infer a usable prompt representation |
| Input | Existing prompt, task brief, explicit objective or rough instruction | Image, video, audio, document, design, example, URL/content or concept available for inspection |
| Owns | Diagnosis/refinement/build under exactly eight pillars: role/authority; objective/task; context/variables; reasoning/workflow; constraints; edge cases/recovery; stop/completion; output schema | Content/reference decomposition, observable attribute extraction, scene/subject/style/action analysis, prompt reconstruction/approximation, target-generator adaptation and prompt-quality checks |
| Negative boundary | Does not claim to recover hidden details from a media reference or execute the task described by a prompt-only request | Does not own the eight-pillar structural audit as its default specialty |

**Routing rule:** “audit prompt ini menurut 8 pillar” → Anatomi Prompt. “Analisis gambar/video/dokumen/desain ini dan buatkan prompt yang mewakilinya” → AI Prompt Finder & Creator. If the produced prompt then needs structural hardening, Finder hands the draft to Anatomi.

A reconstructed prompt is an evidence-based approximation. It is not the recovered hidden original prompt, model, seed or generator settings.

### 2.4 Photo Fixer vs Master Photo Restoration

| Dimension | Photo Fixer | Master Photo Restoration |
|---|---|---|
| Philosophy | Edit a photograph toward the requested visual outcome | Recover the integrity and legibility of an old/damaged photograph while preserving identity and historical character |
| Owns | General retouch, exposure, white balance, color, lighting, object/background edits, compositing, product/vehicle photography, detail enhancement, crop and social formatting | Aged, faded, scratched, torn, cracked, noisy, blurred or degraded photograph restoration; conservative reconstruction, restoration-specific deblur and provenance/identity constraints |
| Negative boundary | Does not become the primary archival-restoration specialist because a request contains the word “repair” | Does not own general beauty retouch, product photography, creative compositing or ordinary background replacement |

**Routing rule:** general edit, retouch, object removal, color/light or product photo → Photo Fixer. Old/damaged/archival photograph restoration → Master Photo Restoration.

**Source-level overlap to resolve:** Photo Fixer currently includes a subskill named photo-fixer-photo-restoration. Until its owning package is revised, ecosystem routing restricts that subskill to localized cleanup of ordinary contemporary photos as part of a general edit. Full old/damaged/archival restoration is routed exclusively to Master Photo Restoration. This is a parent-level routing override; the child package has not yet been rewritten.

### 2.5 GODEX vs Motion Graphic vs PVEE vs Video Explainer Promkes

These products can contribute to one health-video project but they own different layers of truth.

| Dimension | GODEX Motion Audio | Motion Graphic by arifanara | PVEE Promkes Super Orchestrator | Video Explainer Promkes |
|---|---|---|---|---|
| Philosophy | Preserve and engineer what is heard, spoken and timed | Shape visual language and animation into a coherent visual experience | Decide what health information may be communicated, why and how safely; evaluate communication outcomes | Compile an approved health-content package into a technically coherent explainer production package |
| Primary object | Audio, VO, transcript, speakers, speech timing, sound and audio post | General motion-graphics and visual-first explainer | Health source, health claim, audience, behavior objective, safe message, risk and evaluation | Promkes scene, visual continuity, motion, prompt references, manifest, renderer and technical QA |
| Owns | Audio inspection/provenance, transcript and speaker segmentation where accessible, timing precision, VO pace/pronunciation, SFX/BGM/ambience/mix, audio-linked captions and audio QA | Visual concept, art direction, style, palette, typography, visual narrative, storyboard, motion choreography, kinetic type, visual timeline, renderer preparation and visual QA | Health-source inventory, claim evidence, Health Truth Registry, Fact Lock, safe wording, audience/behavior objective, campaign message, health communication risk/privacy/rights/stigma/accessibility, human approval tracking, audience outcome evaluation | Technical production compilation after approved health-content handoff: visual/continuity implementation, scene/storyboard contracts, motion and timing specification, production prompts/references, renderer-neutral manifest/adapters, technical production QA and handoff |
| Does not own | Final health truth, full generic art direction or all visual production decisions | Audio-source truth, transcript provenance, health Fact Lock or clinical approval | Generic renderer engineering, MP4 export or full audio-post production | Final health claim truth, clinical decisions, behavior-change policy or institutional publication approval |

**Promkes production sequence:**

PVEE Fact Lock + approved campaign brief → Video Explainer technical production.

Supporting handoffs:
- GODEX provides audio/VO/transcript/timing and audio-post artifacts when audio is part of the project.
- Motion Graphic provides visual-art-direction or generic motion-design artifacts when that distinct support is needed.
- Video Explainer compiles the approved health-content and production inputs into Promkes-specific technical artifacts.
- PVEE receives production QA and audience-evaluation evidence, but does not take over renderer code or audio mix.
- Clinical, legal, institutional and publication approvals remain with authorized humans.

**Non-health motion project:** Motion Graphic is normally primary for visual-first animation. GODEX becomes primary when the dominant deliverable is audio/VO engineering or the project is genuinely voice-over-first. Do not route to PVEE or Video Explainer without a Promkes health-communication scope.

**Important:** PVEE's current master skill still orchestrates a broad Promkes pipeline. The ecosystem contract narrows its final ownership to health truth, communication governance, campaign decision and evaluation. Its technical production handoff to Video Explainer is a source-alignment requirement, not a claim that the Plugin Creator source has already been modified.


### 2.6 People & Business Competency Academy vs Agent Skills Atlas vs GrowthForge

| Dimension | People & Business Competency Academy | Agent Skills Atlas | GrowthForge Business OS |
|---|---|---|---|
| Primary object | Human learner/team capability and observable behavior | AI skills, plugins, tools, agents and capability-library records | Business context, commercial decisions and operating deliverables |
| Owns | Competency baseline, learning pathway, deliberate practice, simulation, workplace transfer and learner outcome evidence | Discovery, inventory, taxonomy, provenance, dependencies and adoption maturity of AI capabilities | Business strategy, market/customer decisions, brand/product, finance, marketing, sales, operations and commercial execution |
| Does not own | AI package/source engineering, portfolio inventory, business decision ownership, therapy or regulated professional advice | Human learner coaching or proof of real-world behavior transfer | Generic learner assessment or the engineering lifecycle of AI skill packages |
| Routing test | “Can this person/team perform this behavior better in a real context?” | “What AI capability exists, where is its source, and how ready is it?” | “What should the business decide, build, sell, finance or operate?” |

The Academy may use a real business task as a transfer context, but the learning objective and learner evidence remain its responsibility. A commercial recommendation remains GrowthForge's responsibility. A mapped AI skill remains Atlas inventory data, not an executable learning intervention.

## 3. Remaining portfolio positioning

| Plugin | Sole primary responsibility | Explicit non-ownership |
|---|---|---|
| Agent Jailbreak Skill DS | Defensive agent security, threat models, injection/context integrity, tool/action abuse, safe red-team and incident response | General plugin anatomy, normal engineering lifecycle or unauthorized offensive testing |
| Plugin Agent Orchestrator | AI-agent product lifecycle: design, build/operate, deployment, runtime, access, tenant/ecosystem and scaling | Skill/plugin package lifecycle (SDO) or generic reusable workflow architecture |
| AI Workflow Systems Orchestrator | Reusable workflow, SOP, project, modular skill/workspace and automation architecture | AI-agent product lifecycle or direct source implementation |
| Executive Workday Orchestrator | Workday operations: daily planning, task intake/prioritization, projects, meetings, communication drafts, notes, adaptive scheduling and outcome reviews | Generic reusable workflow/SOP architecture (WSO), AI-agent product/runtime lifecycle (Plugin Agent Orchestrator), plugin source engineering (SDO), independent evaluation (Evaluator Team) or universal prompt architecture (Anatomi Prompt) |
| Vibe Coding Mentor | Non-IT software-product discovery, requirements/MVP, PRD quality and PRD-to-builder prompt compilation | Universal prompt architecture (Anatomi Prompt), reference-to-prompt reconstruction (AI Prompt Finder), workday prompt generation (EWO), generic reusable workflow/SOP architecture (WSO), business strategy (GrowthForge), or application code execution/deployment |
| Cortex Workbench | General knowledge-work routing for understanding, learning, research, writing, thinking, productivity and code workflows | Business OS ownership or native slash-command UI |
| CommandCraft 56 | Registry and resolution of 56 text-command aliases/task profiles | Native platform command menu, case-level orchestration or persistent automation |
| Agent Skills Atlas | Capability inventory, provenance, taxonomy, compatibility mapping and staged adoption | Claiming mapped/discovered assets are installed, callable or executable |
| People & Business Competency Academy | Human competency development: diagnose, learn, practise, simulate, transfer to workplace/business behavior and evaluate evidence | AI-skill inventory, generic workflow architecture, business consulting deliverables, therapy or reading-completion-as-mastery claims |
| GrowthForge Business OS | Business strategy, market, finance, brand, product, marketing, sales, lifecycle and operations | Generic knowledge work, technical plugin anatomy or engineering source lifecycle |
| A.S.F.R.E.E Legacy | Redirect and migration identity only | New execution, analysis, engineering or fallback authority |
| HSMART | Separate ecosystem infrastructure platform | Not a plugin in the 21-record catalog and not a child source of this portfolio |

## 4. Central routing decision matrix

| Dominant user intent | Primary plugin | Supporting plugin only when needed |
|---|---|---|
| Analyze a general issue using methods | SKILL ANALYZER | Evaluator Team for independent evaluation; GrowthForge for business-domain outputs |
| Forensic dissection of an AI/plugin architecture | A.S.F.R.E.E | SKILL ANALYZER for method selection; Agent Jailbreak DS for security-specific analysis |
| Score, rank or judge plugin quality | Evaluator Team | SKILL ANALYZER for broad analytical methods; Anatomi Prompt for eight-pillar redesign |
| Create/change/test/release a plugin or skill | SDO | A.S.F.R.E for anatomy; Evaluator Team for independent evaluation; Anatomi Prompt for instruction design |
| Audit/build a prompt structurally under eight pillars | Anatomi Prompt | Finder only when source content first needs to be analyzed |
| Turn an image/video/document/reference into a prompt | AI Prompt Finder & Creator | Anatomi Prompt for subsequent eight-pillar hardening |
| Turn a non-IT app/product idea into an MVP-scoped PRD, product requirements, or a staged AI-builder prompt | Vibe Coding Mentor | GrowthForge for a separate business brief; Anatomi Prompt for universal prompt structure; AI Prompt Finder only for analysis of supplied source content |
| General photo edit | Photo Fixer | Master Photo Restoration only if the actual task changes into archival restoration |
| Old/damaged/archival photo restoration | Master Photo Restoration | Photo Fixer is not the primary restoration route |
| Audio, transcript, VO timing, SFX/BGM, mix or audio QA | GODEX | Motion Graphic/Video Explainer only for separate visual/renderer artifacts |
| General visual motion/explainer production | Motion Graphic | GODEX for audio engineering |
| Health claim, Fact Lock, campaign message, health risk or audience outcome | PVEE | Video Explainer for technical production; GODEX audio and Motion Graphic visual support as required |
| Compile approved Promkes material into scene/renderer/production package | Video Explainer Promkes | PVEE Fact Lock is upstream; GODEX/Motion Graphic support distinct artifacts |
| Defensive AI-agent threat model or prompt-injection review | Agent Jailbreak Skill DS | A.S.F.R.E.E for overall technical case when required |
| Design/build/operate/scale an AI agent | Plugin Agent Orchestrator | Jailbreak DS for security; Workflow Systems for reusable process architecture |
| Design reusable workflow/SOP/modular work system | AI Workflow Systems Orchestrator | Cortex for knowledge-work usage; Plugin Agent Orchestrator only if an AI agent is actually being engineered |
| Organize an individual's workday, workload, meetings, messages and follow-ups | Executive Workday Orchestrator | WSO for generic reusable workflow architecture; Plugin Agent Orchestrator only for AI-agent product/runtime work |
| General learning/research/writing/critical thinking/coding | Cortex Workbench | CommandCraft for explicit alias workflows |
| Use a specific text command profile | CommandCraft 56 | Cortex or GrowthForge only where a distinct domain output is required |
| Inventory and stage skill/capability adoption | Agent Skills Atlas | A.S.F.R.E.E for technical verification |
| Develop a human competency through a measured learning/practice/transfer path | People & Business Competency Academy | GrowthForge only for a separate business-domain decision/deliverable; Agent Skills Atlas only for AI capability inventory |
| Business model, finance, market, marketing, brand, sales or operations | GrowthForge | Cortex or CommandCraft for separate work products |
| Access legacy A.S.F.R.E.E identity | A.S.F.R.E.E Canonical | Legacy redirect only |

## 5. Handoff and authority contract

Every cross-plugin handoff carries:
- handoff_id, case_id and contract_version;
- source plugin key, package version, source authority and commit/snapshot digest;
- recipient plugin key and requested specialist artifact;
- objective, scope, non-goals and explicit user constraints;
- input artifact IDs and provenance;
- epistemic state (OBSERVED, VERIFIED_SOURCE, USER_CLAIM, SOURCE_CLAIM, ASSUMPTION, INFERENCE, HYPOTHESIS, UNKNOWN);
- capability and permission readiness;
- decision/artifact owner and allowed receiving action;
- expected output, acceptance criteria and test/evidence locator;
- blockers, residual unknowns and next owner.

A supporting plugin may return a recommendation or artifact. It may not overwrite the primary owner's canonical registry, make the owner's final decision, publish, merge source or grant access by implication.

## 6. Source-alignment backlog generated by this positioning

The parent-level routing contract is normative for this ecosystem. The following child-package changes remain separate tasks because the current Plugin Creator package content still contains overlapping broader triggers:

1. Evaluator Team: make its embedded implementation specialist a handoff-only interface to canonical SDO; remove competing repository write/lifecycle authority from its triggers.
2. Photo Fixer: narrow/deprecate its photo-restoration subskill for archival/old/damaged photo restoration and route those requests to Master Photo Restoration.
3. PVEE: clarify that its output authority ends at approved health-truth/campaign/governance artifacts and a production handoff; Video Explainer owns Promkes technical production compilation and renderer package.
4. Video Explainer: explicitly declare PVEE Fact Lock and approved campaign brief as upstream content authority; do not claim clinical or institutional decision ownership.
5. GODEX / Motion Graphic: ensure audio provenance/timing/mix and visual-art-direction/motion/timeline are separate deliverable owners with explicit timing and scene handoff.
6. Anatomi Prompt / AI Prompt Finder: retain negative triggers in each package so prompt-structure work and content/reference-to-prompt reconstruction do not compete for the same default request.

Do not mark these child-source alignment tasks complete until the respective canonical package source is changed, validated and read back. Parent routing rules already apply to ecosystem-level selection in the meantime.

## 7. Non-duplication acceptance gates

- Every plugin has at least one positive and one negative trigger.
- Each final artifact and canonical decision has exactly one owner.
- Supporting plugins are selected only for distinct artifacts/controls.
- No active legacy redirect competes with a canonical package.
- No plugin source is rewritten implicitly by a parent overlay.
- Every source-level overlap has an explicit alignment task and an owner.
- Compatibility testing checks both intended routing and rejected/negative routing cases.
- A static registry pass does not prove runtime host routing; host-specific tests remain separate.
