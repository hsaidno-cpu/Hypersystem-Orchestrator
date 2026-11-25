# Executive Workday Orchestrator — HSO integration record

**Catalog key:** `executive-workday-orchestrator`  
**Plugin Creator:** [Private package](https://chatgpt.com/plugins/plugins_6b073a60088081918a8958ab761cb505)  
**Package:** `0.1.0` · `USER / PRIVATE` · release `pluginrel_6b073a6285d481918d11cdbf1bb7643f`  
**HSO repository baseline:** `main` at `6a5edd556263d0c615a9852a4308e0cf9503a19f` (2026-11-26 observation)  
**Integration branch:** `feat/executive-workday-orchestrator-20261126`

## 1. Purpose and position

Executive Workday Orchestrator (EWO) is a domain-specific operating layer for organizing a person's or operator's workday. It converts scattered tasks, commitments, projects, meetings, messages and notes into a prioritized, feasible and traceable plan, then supports adaptive replanning and outcome reviews. A dedicated `prompt-generator` skill builds and audits workday-domain prompts.

EWO is a child plugin in the HSO portfolio, not a replacement for HSO's ecosystem control plane.

## 2. Functional architecture

One M00 orchestrator coordinates 13 specialist skills:

| Category | Skill | Responsibility |
|---|---|---|
| Core orchestration | `workday-orchestrator` | Mode selection, capability preflight, routing, lifecycle and final workday disposition |
| Intake | `task-intake-triage` | Capture, normalize, classify, deduplicate and route tasks, ideas, commitments and messages |
| Scheduling | `daily-planning` | Capacity-aware day plan, time blocks, buffers and unscheduled-work disclosure |
| Decision | `priority-decision-engine` | Prioritization, cost-of-delay reasoning, trade-offs and Eisenhower view |
| Portfolio | `project-portfolio-management` | Milestones, dependencies, owners, cross-project capacity and delivery risk |
| Calendar / meetings | `calendar-meeting-operations` | Meeting briefs, calendar conflict reasoning, decisions and follow-ups |
| Communication | `email-communication-operations` | Message triage, response drafting and follow-up tracking |
| Knowledge | `notes-knowledge-management` | Structured capture, provenance and actionable knowledge |
| Adaptation | `focus-adaptive-scheduling` | Replanning after interruptions, overruns and changing priorities |
| Learning | `performance-review-learning` | Daily and weekly outcome review and improvement loop |
| Prompt engineering | `prompt-generator` | Build, refine, compare and audit workday-domain prompts using eight-pillar Octa-Prompt structure |
| Automation | `automation-integration-architect` | Automation-readiness assessment, connectors, event/action design and recovery strategy |
| Governance | `workday-data-governance`, `approval-risk-gate` | Source-of-truth, freshness, privacy, state semantics, authorization and action approval |

## 3. Primary ownership and routing boundaries

| System | Owns | EWO boundary |
|---|---|---|
| HSO | Ecosystem registry, primary routing, cross-plugin contracts, governance and evidence aggregation | EWO does not govern the plugin portfolio or route all HSO work |
| AI Workflow Systems Orchestrator | Reusable workflows, SOPs, project/workspace composition and automation architecture | EWO consumes/adapts such patterns for one workday domain; it does not own generic workflow architecture |
| Plugin Agent Orchestrator | AI-agent product lifecycle, runtime, deployment, access, tenant and scaling | EWO is a domain workflow plugin, not a hosted autonomous agent product |
| Skill Developer Orchestrator | Plugin/skill source engineering, tests, repository changes and releases | EWO does not own its own canonical source lifecycle; SDO owns accepted source changes |
| Evaluator Team | Independent quality judgement, benchmarking and acceptance recommendation | EWO's self-checks are not independent certification |
| Anatomi Prompt V3.0 | General eight-pillar prompt architecture, prompt audit and cross-pillar quality | EWO's generator is domain-specific; refer universal/advanced prompt architecture to Anatomi Prompt |

Routing rule: choose EWO when the desired outcome is better day-to-day work execution. Choose Workflow Systems for general reusable workflow design; Plugin Agent Orchestrator for engineering an AI-agent product/runtime; SDO for plugin source changes; Evaluator Team for independent judgement; Anatomi Prompt for universal prompt architecture.

## 4. Capability and authority boundaries

The package supports instruction-level reasoning and artifact preparation. It does not itself provision:

- a canonical task/project database or persistent work state;
- a connected mailbox or permission to send mail;
- a connected calendar or permission to create/update/delete events;
- scheduled triggers, queues, always-on workers or background monitoring;
- Notion/Google/Outlook/Todoist/Trello/Asana synchronization.

Those capabilities require separate integrations, credentials in secure storage, least-privilege scopes, idempotency/replay control, retry/reconciliation behavior, human approval for consequential actions and independent read-back. A prompt or plugin listing is not proof of those integrations.

Default action posture is read/classify/draft/plan. Sending, publishing, purchasing, deleting, external commitments and calendar/task writes require exact target, scope, connector readiness, explicit action-specific approval and verification.

## 5. Evidence and maturity

| Evidence item | Observed state |
|---|---|
| Plugin Creator package | Created; version 0.1.0; USER/PRIVATE |
| Package file inventory | Read back: 14 `SKILL.md` files; no missing paths in returned inventory |
| Canonical Git child source | `NOT_IDENTIFIED`; repository-creation action is not exposed by the current GitHub connector |
| Package LICENSE file / manifest license field | No LICENSE file in current package inventory; neither manifest declares a license |
| Original source URL and redistribution permission | `NOT_ASSESSED`; README only identifies a supplied prompt as derivation input |
| EWO routing contract corpus | 14 positive, 14 negative, 6 ambiguous cases; metadata-only, no private SKILL.md body copied |
| Static contract CI | Run #237 PASSED on `9963011dfb4028ca16d52a79c57134b272f94692`; 155 unit/resolver tests passed |
| Public HSO registration | PR #33 remains draft/open/unmerged; requires review and acceptance |
| Host activation / actual EWO invocation | `NOT_RUN`; P0 remote-MCP invocation job skipped |
| External calendar/mail/task integrations | `NOT_CONFIGURED` in this package |
| Background/event-driven operation | `NOT_IMPLEMENTED` |
| Production readiness | `NOT_ESTABLISHED` |

## 6. Acceptance criteria for future maturity

1. Establish an authorized private canonical child Git repository; record source URL, immutable commit, original-source attribution and redistribution rights. The current connector has no repository-creation action, so this gate is blocked pending an authorized creation path.
2. Add a LICENSE file and explicit license metadata only after the original source terms and derivative rights are assessed; do not assume a license.
3. Reconcile all 14 package skills with canonical source files; capture immutable commit and file-level parity.
4. Execute the 14 positive, 14 negative and 6 ambiguous routing cases on a named host/version. The current 155-test CI validates the static corpus only.
5. Test timezone, capacity overflow, fixed commitments, dependency cycles, duplicate intake and stale updates.
6. Exercise approval-denied, unauthorized write, partial write, timeout, replay/duplicate and outcome-unknown recovery.
7. Integrate one real task/calendar/email provider only after OAuth scopes, secrets, retention and least privilege are approved.
8. Verify host activation and real connector actions on a named host/version; test read-back and audit trail.
9. Run independent evaluation and regression tests before any production-ready claim.

## 7. Current disposition

`PACKAGED / PRIVATE`; HSO catalog change is pending pull-request review. It is not a merged HSO plugin identity, a host-verified skill, an executable background assistant, or a production integration.
