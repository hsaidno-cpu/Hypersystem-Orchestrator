# AI Prompt Finder & Creator — Cross-Domain Prompt Generator v1.1.0

**Status:** package updated and read back; HSO catalog integration proposed on this branch; not merged.  
**Date:** 26 November 2026  
**Plugin Creator ID:** plugins_6ae57d424a2481918295d281919fbb7d  
**Plugin Creator release:** pluginrel_6b074a37ae8c8191bae7723d715ab713  
**Scope / discoverability:** USER / PRIVATE

## 1. Executive decision

Extend the existing AI Prompt Finder & Creator identity. Do not create another HSO plugin identity and do not split the 50 source patterns into 50 agents. Version 1.1.0 adds an explicit prompt-generator workflow and ten category prompt-grammar specialists. The product remains a prompt-artifact system: it does not run the downstream task by default.

The package has 18 skill definitions: the seven existing multimodal/optimization/QC skills, one prompt-generator, and ten category subskills.

## 2. Source evidence and provenance

The user-provided source has 50 prompt patterns grouped into ten categories, with five patterns per category:

| Category | Source IDs | Count |
|---|---:|---:|
| Business & Strategy | 01–05 | 5 |
| Marketing & Growth | 06–10 | 5 |
| Productivity & Time | 11–15 | 5 |
| Decision-Making | 16–20 | 5 |
| Writing & Communication | 21–25 | 5 |
| Money & Finance | 26–30 | 5 |
| Learning & Skills | 31–35 | 5 |
| Tech & Troubleshooting | 36–40 | 5 |
| Career & Work | 41–45 | 5 |
| Thinking Frameworks | 46–50 | 5 |
| **Total** | **01–50** | **50** |

The package preserves concise titles and normalized intents under its private APFC-001–APFC-050 namespace. It does not copy the complete source prompt wording into the public HSO repository. This namespace is deliberately distinct from GrowthForge's separate BPG-001–BPG-050 business-growth catalogue and IMG-001–IMG-120 image-source catalogue.

**Source rights:** user-provided content is evidence for analysis and personal integration. Redistribution rights for third-party source wording have not been established. Keep the full prompt instructions in the USER/PRIVATE package.

## 3. Cross-domain subskill architecture

| Category | New subskill | Primary prompt grammar | HSO boundary |
|---|---|---|---|
| Business & Strategy | business-strategy-prompts | diagnosis, idea tests, strategy options, pricing hypotheses, positioning | GrowthForge owns business decisions and business-task prompts |
| Marketing & Growth | marketing-growth-prompts | funnel, offer, content, acquisition and ad prompts | GrowthForge owns commercial marketing/growth |
| Productivity & Time | productivity-time-prompts | workload, priorities, time blocks, automation suitability, recurring systems | WSO owns reusable workflow/SOP; EWO remains pending until its HSO dependency is integrated |
| Decision-Making | decision-making-prompts | decisions, pre-mortem, opportunity cost, steelman, uncertainty | SKILL ANALYZER owns method selection and analytical execution |
| Writing & Communication | writing-communication-prompts | emails, documents, editing, difficult conversations, explanation | Cortex/CommandCraft may execute general knowledge work; APFC only creates the prompt |
| Money & Finance | money-finance-prompts | budgets, debt, freelance pricing, cashflow, purchase/investment assessment | GrowthForge owns business finance; personal investment prompts remain informational/non-advisory |
| Learning & Skills | learning-skills-prompts | skill plans, Feynman, hints, summaries, study/interview practice | People & Business Competency Academy owns human competency outcomes; Cortex owns general knowledge work |
| Tech & Troubleshooting | tech-troubleshooting-prompts | debugging, troubleshooting, software comparison, data design, formulas/scripts | Ponytail owns engineering method; Vibe Coding Mentor's special PRD-to-builder scope remains pending |
| Career & Work | career-work-prompts | negotiation, conflict, resume, transition, leadership | People & Business Competency Academy owns human competency development; workday owner remains subject to HSO registration |
| Thinking Frameworks | thinking-frameworks-prompts | first principles, 5 Whys/Fishbone, inversion, simulated viewpoints, problem solving | SKILL ANALYZER owns analytical-method selection and execution |

The ten subskills are not ten autonomous agents. Each supplies a category-specific grammar, variables, output expectations and guardrails to the single prompt-orchestrator.

## 4. Prompt generation pipeline

1. Classify intent: SOURCE_TO_PROMPT, GENERATE_PROMPT, OPTIMIZE_PROMPT, AUDIT_PROMPT, PROMPT_PACKAGE, or separately requested EXECUTE_DOWNSTREAM.
2. Select one primary domain and only distinct supporting specialists.
3. Normalize a prompt brief: role function, task, purpose, audience, context, variables, requirements, constraints, workflow, stop conditions, output contract and acceptance criteria.
4. Select QUICK, STANDARD, or ADVANCED depth proportionate to risk and complexity.
5. Compose a domain-native, copy-ready prompt.
6. Adapt target-model syntax only when verified; otherwise mark model-agnostic or NOT_VERIFIED.
7. Run prompt QC and return complete output plus assumptions and limitations.

The generator does not request private chain-of-thought. It asks for concise, observable methods, assumptions, evidence, calculations and results.

## 5. Cross-method conclusions

| Method | Finding | Design consequence | Limitation |
|---|---|---|---|
| Source decomposition | 50 task patterns span 10 categories, not 50 agents | Keep a versioned pattern index and one orchestrator | Pattern counts do not prove demand or effectiveness |
| Taxonomy / ontology | Category borders overlap, especially business, marketing, finance and productivity | Route by dominant intent and ownership, not keywords alone | Some requests need one focused clarification |
| JTBD | Users seek progress/outcomes, not prompt labels | Classify purpose and deliverable before selecting the skill | User wording can combine prompt creation and task execution |
| First principles | Prompt artefact and downstream execution are separate objects | Enforce explicit PROMPT_ONLY vs separate execution request | Host capability and user authorization still required |
| Octa-Prompt comparison | Source task prompts are not consistently formal eight-pillar instructions | Use prompt-generator for ordinary prompts; Anatomi owns explicit formal Octa construction | Applying all eight headings to trivial prompts adds waste |
| Systems architecture | Existing plugin owners cover most domains | One M00, 11 new skill modules, bounded handoffs | Routing declarations are not live runtime dispatch |
| Root cause / causal analysis | Several source patterns invite root-cause conclusions from limited observations | Require evidence, competing hypotheses and confidence labels | 5 Whys/Fishbone do not prove causality |
| FMEA / threat analysis | Finance, employment, customer and technical data introduce privacy, safety and authorization risks | Add risk-tiered inputs, no-secret handling, stop and recovery rules | Residual risks need real usage/incident data |
| Decision science | Weighted matrices and financial forecasts need explicit units, criteria and formulas | Show arithmetic, assumptions, sensitivity and reversibility | Incorrect or stale input data still invalidates outputs |
| Evidence assurance | Prompt quality is not proof of output quality | Add 15 acceptance specifications and target-run status gates | Target runtime tests remain NOT_RUN |

## 6. Positive analysis

| Strength | Why it matters | Benefit if engineered properly |
|---|---|---|
| Broad ten-category coverage | Covers strategic, operational, cognitive and technical tasks | A reusable prompt entry point across varied work |
| Concrete input placeholders | Prompts ask for relevant context rather than vague instructions | Lower ambiguity and less back-and-forth |
| Observable output shapes | Matrices, tables, plans, scripts and timelines are requested | Easier acceptance checks |
| Built-in analytical variety | Pre-mortem, steelman, inversion and first principles are represented | Better prompt variety and alternative lenses |
| Time horizons | 7-day, 14-day, 30-day and 90-day planning appear in several use cases | More actionable prompt outputs |
| Explicit uncertainty in some prompts | Several patterns request assumptions, evidence or trade-offs | Good foundation for evidence-aware generation |
| Existing multimodal core | Image/video reconstruction, optimization and QC already exist | New work extends the package rather than restarting it |
| HSO alignment available | Existing domain specialists can retain truth/decision ownership | Less duplicated domain logic |
| Reusable patterns | Repeated tasks can be normalized and versioned | Reduced prompt drafting overhead |
| Output-specific workflows | Writing, finance, learning and debugging need different grammars | Better domain fit than one universal prompt template |

## 7. Negative analysis

| ID | Weakness / failure mode | Root cause | Potential impact | Priority |
|---|---|---|---|---|
| N01 | Prompt creation and downstream execution can be confused | No global mode contract in the source guide | False claims of sending, publishing, editing or automation | P0 |
| N02 | No shared variable/provenance schema | Each pattern defines its own input placeholders | Missing or misinterpreted inputs | P1 |
| N03 | Domain ownership is not formalized | Ten categories cross existing HSO specialists | Duplicate routing and conflicting decisions | P0 |
| N04 | Benchmarks may be assumed current or applicable | Funnel prompt asks for typical industry benchmarks | Bad diagnosis based on stale/unsourced numbers | P1 |
| N05 | Marketing outputs can overpromise outcomes | Conversion and growth language can be interpreted as guarantee | Misleading claims and trust loss | P1 |
| N06 | Personal/financial inputs are sensitive | Budget, debt, income, career and workplace context may be included | Privacy exposure or overconfident personal advice | P0 |
| N07 | Investment analysis can look like a recommendation | Purchase/investment prompt asks for ROI and value | Unsupported return claims or unsuitable advice | P0 |
| N08 | Root-cause prompts can overstate causality | 5 Whys/Fishbone can be treated as proof | Incorrect remediation | P1 |
| N09 | Expert panel can misrepresent simulation as real expertise | Multiple personas are requested | False authority or invented consensus | P1 |
| N10 | Technical prompts can imply actual debugging | Code, formulas and troubleshooting outputs look executable | User may assume code was run or system changed | P0 |
| N11 | No universal acceptance contract in the source | Output format differs across patterns | Hard to validate consistency and prompt versions | P1 |
| N12 | Dynamic tool/model features can become stale | Target platform and software requirements change | Broken or fabricated syntax and recommendations | P1 |
| N13 | Some prompts can be over-questioning | Master problem-solver invites up to three clarifications | Excessive friction on simple tasks | P2 |
| N14 | Source rights are unclear | User-supplied source does not prove redistribution license | Public copying risk | P0 |
| N15 | Prompt success is not measured by source itself | No controlled model tests or output benchmark | False belief that a prompt works better | P1 |

## 8. Negative-to-positive conversion

| Negative | Mitigation | Prevention | Anticipation | Evaluation / completion evidence |
|---|---|---|---|---|
| N01 prompt-vs-execution ambiguity | Add explicit intent modes | Generated prompt never auto-runs | Separate downstream request and permission check | Test confirms no side-effect from prompt-only request |
| N02 variable inconsistency | Normalize prompt brief schema | Typed source and variable states | Placeholders and one critical question | Required fields and missing-variable test pass |
| N03 HSO ownership collision | Map one primary owner per category | Negative routing triggers | Conditional handoffs to GrowthForge/WSO/Analyzer etc. | Static route tests assert owner boundaries |
| N04 unsourced benchmarks | Require source/date/industry basis | No fabricated benchmarks | Mark rough estimates or block comparison | Evidence field present or benchmark omitted |
| N05 overpromising | Reframe targets as hypotheses | No guarantee language | Require proof and truthful urgency | QC rejects unsupported promises |
| N06 sensitive inputs | Minimize, redact and localize data | Never request secrets | Explicit consent/privacy guardrails | No secrets in output; sensitivity acknowledged |
| N07 investment risk | Informational framing and verified arithmetic | No personalized investment direction or false ROI | Flag missing rates, fees, taxes, horizon | Calculation inputs, assumptions and caveats shown |
| N08 causality overreach | Use causal hypotheses | Require evidence for root-cause claims | Competing causes and disconfirming tests | Test distinguishes root-cause hypothesis from proven cause |
| N09 simulated authority | Label perspectives as simulated | No claims of actual independent experts | Preserve disagreement and evidence source | QC verifies simulation label |
| N10 fake execution | Separate prompt artifact from execution receipt | No “done” claims without tool evidence | Read-back and permission gate for real actions | Explicit NOT_RUN unless target receipt exists |
| N11 missing acceptance | Add output schema and tests | Versioned rubric | Proportionate QUICK/STANDARD/ADVANCED | 15 acceptance cases implemented as specs; runtime tests pending |
| N12 platform drift | Model-agnostic baseline | No invented flags/settings | Verify current authoritative docs | Target adaptation marked VERIFIED only after check |
| N13 over-questioning | Ask one critical question maximum | Use assumptions for non-critical gaps | Use explicit placeholders | Low-friction intake test |
| N14 rights uncertainty | Keep public HSO metadata-only | Do not redistribute full prompt wording | Rights review before public package/source | Source license recorded before installability |
| N15 untested prompts | Controlled A/B or target test | No quality claims without output evidence | Record model/version/date/settings | TESTED_ON_TARGET only with results |

## 9. Comparative HSO responsibility matrix

| Existing component | Owns | Relationship to APFC 1.1.0 | Non-duplication rule |
|---|---|---|---|
| GrowthForge Business OS | Business strategy, commercial decisions, marketing, finance and business-task prompts | Primary HSO domain owner for three overlapping source categories | APFC can prepare a brief only; GrowthForge owns business prompt/task |
| Anatomi Prompt V3.0 | Formal eight-pillar prompt architecture and audit | Optional formal hardening of APFC-created prompts | Anatomi owns structural compliance |
| SKILL ANALYZER | General analytical method selection and analysis | Owner for decision and thinking-method execution | APFC writes the analytical prompt; Analyzer performs method work |
| AI Workflow Systems Orchestrator | Reusable workflow, SOP and system architecture | Owner for recurring workflow design and automation architecture | APFC prompt may request a workflow; WSO owns workflow blueprint |
| Executive Workday Orchestrator | Workday task/project/meeting/focus coordination | Candidate owner for productivity-time requests | Registration remains pending in PR dependency chain; no live invocation claim |
| Cortex Workbench / CommandCraft 56 | General knowledge-work and command profile routing | Potential destination for writing, explanation, learning or general tasks | APFC owns prompt construction; execution remains with the relevant knowledge-work owner |
| People & Business Competency Academy | Human competency diagnosis, practice and transfer | Owner for human learning/skill development outcomes | APFC creates learning prompt; Academy owns competency evidence |
| Ponytail Engineering System | Engineering method, codebase/diff analysis, risk-based tests | Supports technical troubleshooting prompts | APFC does not write or modify canonical repositories |
| Vibe Coding Mentor | Non-IT digital product discovery, PRD/MVP and PRD-to-builder prompt compilation | Specialized overlap for product-builder prompts | Integration remains pending; it does not own universal prompt architecture |
| Evaluator Team | Independent quality judgement | Can evaluate APFC prompt/package quality | APFC QC is not independent approval |
| A.S.F.R.E.E | Technical plugin/system forensics and supervised reconstruction | Used only when plugin/package anatomy is the target | Not a general prompt/knowledge-work owner |
| Skill Developer Orchestrator | Source implementation, tests, versioning and release preparation | Owns later engineering lifecycle for APFC changes | APFC does not release or modify itself outside SDO gates |
| Hypersystem Orchestrator | Ecosystem registry, arbitration, governance and evidence | Owns catalog and routing metadata | HSO does not become another prompt generator identity |

**Catalogue distinction:** the current HSO GrowthForge branch has a separate BPG-001–BPG-050 source in five business-growth categories. The supplied file is ten cross-domain categories. Similar source counts do not imply identical content, IDs, or ownership. APFC IDs remain distinct.

## 10. Critical evaluation and next development

| Priority | Development | Owner | Completion evidence |
|---|---|---|---|
| P0 | Preserve the single APFC plugin identity and private audience | Plugin Creator / owner | Same plugin ID; USER/PRIVATE; read-back confirms v1.1.0 |
| P0 | Enforce prompt-only vs downstream execution | APFC M00 | Routing cases show generated prompts never cause side effects |
| P0 | Keep ten domain subskills bounded to prompt grammar | APFC M00 + HSO owners | Positive/negative triggers and ownership tests |
| P0 | Keep canonical source, license and distribution status honest | SDO / owner | Repository and rights evidence; until then snapshot_only |
| P1 | Create controlled test corpus from all 50 patterns | Evaluator Team | Test fixtures cover ten categories; target result and limitations recorded |
| P1 | Validate target generators separately | Evaluator Team + owner | Named model/version, settings, source, output, rubric and date |
| P1 | Add structured feedback and prompt version metrics | WSO/SDO after design acceptance | Retrieval/use quality data; no vanity score |
| P1 | Integrate EWO/Vibe only after their HSO PR dependencies merge | HSO/SDO | Catalog admission, route tests, host and runtime evidence |
| P2 | Add multilingual variants and prompt localization | APFC domain specialists | Translation fidelity and target-specific QA |
| P2 | Add prompt-library retrieval/version management if usage justifies it | WSO/SDO | Access control, provenance, duplicate detection and retrieval tests |

## 11. Acceptance gates and current status

| Gate | Acceptance condition | Current state |
|---|---|---|
| Plugin package integrity | Same ID, version 1.1.0, all 18 skills and manifests read back | PASS — package read-back |
| Category coverage | Ten categories, five patterns each, 50 APFC IDs | PASS — static index |
| Domain decomposition | Ten subskills plus one prompt-generator | PASS — package contents verified |
| Existing skills retained | Seven previous skill files remain present | PASS — inventory read-back |
| HSO identity | No new plugin identity; existing record updated | PROPOSED in HSO branch; not merged |
| HSO instruction index | 18 APFC metadata entries and aggregate total 276 | PROPOSED in HSO branch; CI pending |
| Rights/source | Canonical Git repository and distribution rights verified | BLOCKED / NOT_ASSESSED |
| HSO static contract | Existing Finder-to-Anatomi C2/C3 contract remains distinct | Already CONTRACT_TESTED; no new runtime edge claimed |
| Host activation | Named target host route invokes package | NOT_RUN |
| Runtime execution | Real prompt-generation call, returned artifact and receipt | NOT_RUN |
| Independent evaluation | 15 test specifications executed against named targets | NOT_RUN; specifications added to private package |

## 12. Registry and release evidence

- Plugin Creator update: SUCCESS / updated.
- Plugin version: 1.1.0.
- Current release: pluginrel_6b074a37ae8c8191bae7723d715ab713.
- Plugin ID unchanged: plugins_6ae57d424a2481918295d281919fbb7d.
- Scope/discoverability unchanged: USER / PRIVATE.
- HSO public branch: feat/ai-prompt-finder-cross-domain-1-1-0-20261126.
- HSO main remains protected and unchanged by this proposed PR.
- Existing PR #24 GrowthForge and PR #35 Vibe Coding Mentor remain separate pending work; no merge/retarget action is performed here.

**Final disposition:** PASS for private package update and read-back; PASS for source-pattern decomposition; proposed HSO metadata/routing changes await CI and review; HOLD for public distribution, canonical source parity, host activation and runtime readiness.
