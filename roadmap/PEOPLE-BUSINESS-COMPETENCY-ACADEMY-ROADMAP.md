# People & Business Competency Academy — Progressive Development Roadmap

**Baseline date:** 2026-11-23  
**Plugin identity:** people-business-competency-academy  
**Plugin Creator package:** 0.1.0 / pluginrel_6b039efc6dfc81919fffbe265e8f84c9  
**Parent repository:** hsaidno-cpu/Hypersystem-Orchestrator  
**Current governance state:** PACKAGE_CREATED / PARENT_REGISTRATION_IN_REVIEW / CANONICAL_SOURCE_NOT_IDENTIFIED / HOST_RUNTIME_NOT_TESTED

## 1. Mission and scope

Develop observable human capabilities across 12 People Skills and 8 Business Skills. The system links a competency gap to a tailored learning path, deliberate practice, realistic simulation, real-world transfer and evidence-led evaluation.

The 100 title-author entries are transcribed from the user-supplied image. The numbering is preserved as source order, not a quality ranking, prerequisite sequence or verified reading order. Bibliographic details have not been independently checked. No book text, chapter summaries, quotations or pirated substitutes are included.

## 2. Canonical capability model

INTENT / ROLE CONTEXT → COMPETENCY DIAGNOSIS → PRIORITY SELECTION → LEARNING PATH → PRACTICE → SIMULATION → WORKPLACE TRANSFER → EVIDENCE REVIEW → ADAPT / ADVANCE

The nine package skills are:
1. academy-orchestrator — primary routing and learner pathway controller.
2. competency-diagnostic — baseline, context and evidence quality.
3. curriculum-path-architect — staged learning path and workload.
4. people-skills-coach — observable interpersonal behaviors.
5. business-skills-coach — applied business competencies.
6. simulation-roleplay-lab — realistic rehearsal and feedback.
7. deliberate-practice-designer — structured repetition and difficulty progression.
8. workplace-transfer-coach — real-context action and evidence capture.
9. progress-evaluation-engine — formative checks, milestone decisions and adaptive planning.

## 3. Staged roadmap and exit evidence

| Stage | Focus | Current state | Exit evidence |
|---|---|---|---|
| PBCA-0 | Source image intake and taxonomy transcription | VERIFIED_WITH_SCOPE_LIMITS | 20 domains, split 12/8; 100 title-author records; source order and verification caveat preserved |
| PBCA-1 | Product architecture and skill package | PACKAGE_CREATED / READBACK_VERIFIED | Plugin Creator private package 0.1.0; nine skill files; manifest, schema, instruction bundle and book catalog read back with no missing paths |
| PBCA-2 | Parent ecosystem registration | BRANCH_UPDATED / PR_AND_CI_PENDING | Registry 21 identities; snapshot index 247 skills; validator, unit tests and PR CI must pass against the exact branch head SHA |
| PBCA-3 | Canonical source ownership and licensing | NOT_STARTED | Owner-approved child repository, explicit license/notices, source manifest, tests, changelog and immutable commit |
| PBCA-4 | Host activation and runtime compatibility | NOT_RUN | Named host/version, actual invocation evidence for relevant workflows, negative-route checks and runtime limitations |
| PBCA-5 | Learner progress operations and outcome evaluation | NOT_STARTED | Baseline and repeated assessment records, observable behavior artifacts, feedback, retention checks and explicit privacy/consent model |
| PBCA-6 | Automation and service integration | DEFERRED | Stable repeatable process, chosen data owner/store, security and retention policy, idempotency/recovery tests, operator and approval model |

Stages are sequential only where dependency requires it. Completing a static package does not close host runtime, data operations or behavior outcomes.

## 4. Monitoring and evaluation register

| Indicator | Operational definition | Baseline at this checkpoint | Interpretation guardrail |
|---|---|---|---|
| Taxonomy coverage | Number of indexed competency domains / 20 | 20 / 20 | Counts source categories, not mastery |
| Reference transcription coverage | Number of title-author entries preserved / 100 | 100 / 100 | Does not imply bibliographic verification or book quality |
| Package skill coverage | Read-back skill instructions / 9 | 9 / 9 | Proves package file presence only |
| Learner baseline coverage | Competencies with a documented baseline / competencies selected by a learner | NOT_STARTED | Do not invent a learner baseline |
| Practice evidence coverage | Completed practice events with feedback/artifact / planned practice events | NOT_STARTED | Track quality and context, not only volume |
| Workplace transfer evidence | Target behaviors observed in a real context with dated evidence | NOT_STARTED | A simulated roleplay is not workplace transfer |
| Retention / durability | Repeat observation at agreed later checkpoints | NOT_STARTED | Do not infer retention from immediate post-test |
| Outcome contribution | Change in a predefined work outcome with context and alternative explanations | NOT_STARTED | Avoid unsupported causal attribution |

No numeric learner progress score is released until the underlying evidence, scoring rubric and missing-data rules are defined. Avoid aggregating unlike competencies into a misleading single mastery number.

## 5. Competency maturity and milestone logic

Use behaviorally anchored maturity descriptions rather than a reading-completion counter:
- AWARE: can explain the concept and recognize when it matters.
- GUIDED: can attempt the behavior with a prompt, script or coach support.
- APPLIED: demonstrates the behavior independently in a defined real context with supporting evidence.
- ADAPTIVE: selects and adapts the behavior across changing contexts, can explain trade-offs and sustains performance.
- NOT_ASSESSED: no adequate evidence yet; it is not a low score.

Each milestone records the target behavior, context, evidence artifact, observation method, assessor/source, date, limitations and next review trigger. Self-report is useful context, not sufficient proof by itself.

## 6. Adversarial risk register and controls

| Risk | Failure mechanism | Preventive / detective control |
|---|---|---|
| Reading list treated as validated curriculum | Source order is mistaken for evidence-based sequence or a verified bibliography | Preserve original order, mark bibliographic status unknown, research editions/authors separately before prescribing an order |
| Reading completion mistaken for competence | Knowledge exposure is used as a proxy for behavioral performance | Require practice, simulation, real-context behavior and evidence review |
| Self-rating bias | Learner confidence substitutes for observed performance | Triangulate self-reflection, artifact quality, simulation and external feedback where appropriate |
| Body-language overclaim | Isolated gestures are treated as lie/intent detectors | No inference of deception, intent or personality from nonverbal cues alone; use contextual, probabilistic observation |
| Influence skills used manipulatively | Persuasion/negotiation becomes coercion or deception | Require consent, transparency, truthful claims, fair dealing and explicit harm boundaries |
| Emotional intelligence mistaken for therapy | Coaching drifts into diagnosis or treatment | Keep scope educational; refer clinical needs to qualified professionals |
| Financial learning treated as personal investment advice | Educational concepts become individualized regulated recommendations | Teach concepts and assumptions; disclose limitations and avoid personal securities instructions |
| Workplace feedback violates privacy | Sensitive people/performance data is collected without a valid basis | Data minimization, consent, role-based access and user-controlled evidence retention |
| Progress automation creates duplicate or false records | Retries or stale state create inconsistent learner history | Defer automation until idempotency keys, audit records, recovery and ownership are defined |
| Snapshot treated as source repository | A parent copy is mistaken for canonical implementation | Keep pending_repository until owner, source, version, license and commit are verified |

## 7. Source and release governance

- Plugin Creator package is private (USER scope / PRIVATE discovery). Its exact package identity and release are recorded above.
- The public parent repository stores a clearly labelled instruction snapshot and source-reference catalog because ecosystem registration was explicitly requested. It does not inherit the private package's release authority.
- The Academy has no canonical child Git repository recorded yet. Do not add a guessed URL or submodule.
- Parent catalog and snapshot changes do not constitute source-level implementation migration.
- The plugin's behavior has not been host-activated or runtime-tested in this checkpoint.

## 8. Decision backlog

1. Confirm canonical GitHub source repository ownership, visibility and license.
2. Independently verify all 100 bibliographic records (titles, authors, editions and publication data) before recommending a mandatory reading sequence.
3. Decide whether learner tracking is conversational/manual first or requires a persistent external service; define data privacy/retention before implementation.
4. Define the first target learner cohort and role-context scenarios so the pathway can be evaluated against real needs.
5. Select host platforms and test actual discovery, invocation and failure behavior.

## 9. Completion semantics

PLANNED, IN_PROGRESS, BLOCKED, PARTIAL, VERIFIED and ACCEPTED are evidence-backed states. Package creation, parent registration, PR approval, source integration, host activation, runtime execution and measured learner outcomes are distinct states. A later state is never inferred from an earlier one.
