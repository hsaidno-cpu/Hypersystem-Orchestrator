# HSO Mission Control — Intelligence Specification v2.0

## Purpose and source authority
Mission Control is HSO's operational observability, reconciliation and decision-support layer. It does not replace existing HSO governance, PRE, roadmap, execution ledger or plugin ownership.

| Platform | Authoritative responsibility |
|---|---|
| GitHub | Code, branch, commit, PR, CI, workflow and release evidence |
| Notion | Governance, decision records, roadmap, execution ledger and evidence index |
| Supabase | Normalized operational projection, snapshots, decision history and sync audit |
| Vercel | Application hosting only |
| Mission Control | Reconciliation, evidence analytics, one primary recommendation, prompts and diagnostics |

No global two-way overwrite is allowed. The dashboard reads projections and links to canonical sources.

## Required dashboard indicators

- **Verified completion:** Status Verified/Accepted, Gate PASS, fresh evaluation, and linked acceptance evidence PASS. CODE work requires matching commit/CI SHA where declared.
- **Active work items:** canonical Roadmap Status = In progress.
- **Open blockers:** grouped root-cause issues still OPEN, rather than a raw count of task failures.
- **Critical issues:** open issue groups with severity CRITICAL.
- **Pending approvals:** required approval not yet APPROVED, or explicit PENDING.
- **Milestone health:** weighted actual vs expected progress, baseline/target dates, blockers, failures and pending approvals.
- **Source freshness:** last successful reconciliation age vs source freshness SLA. A webhook arriving does not mean a source is connected.

Completed != Verified. Execution and verification must be distinct states.

## Weighted progress

`Verified Weighted Progress = (Σ Scope Weight of Verified items / Σ Scope Weight of weighted items) × 100`

`Weight Coverage = (number of weighted work items / total work items) × 100`

Rules:
- Scope Weight must be positive and accompanied by Weight Rationale.
- No default weights are invented by AI.
- Unweighted items are excluded from the denominator and visible in coverage.
- No weights = UNMEASURED, not a fabricated 0% or 100%.
- Partial weights = PARTIAL_COVERAGE.
- Only verified acceptance evidence contributes to verified weight.
- A formal milestone requires an explicit Parent Milestone ID. Otherwise the data is grouped under Ecosystem Stage, not represented as a milestone.
- Expected Progress %, Baseline Start Date and Target Date are owner-set inputs; no planned curve is guessed.

## NEXT STRATEGIC ACTION and priority

The engine emits at most one Primary Next Action. It also returns Supporting Actions, Blocked Actions, Pending Decisions, and NO_ELIGIBLE_ACTION / SOURCE_STALE if nothing is safe to recommend.

### Hard eligibility gate

Block a candidate if:
- Any mandatory source is not connected/fresh.
- Status is not Ready, Not started or In progress.
- Gate is not PASS.
- Stable task key is duplicated or dependency prose has no explicit Dependency Work Item IDs.
- A dependency ID is missing or not Verified.
- Change Surface or Execution Target is undefined.
- For CODE changes, branch/HEAD SHA is unknown or CI PASS is not for the exact same SHA.
- Required approval is not APPROVED or review does not bind to the same SHA.
- HIGH/CRITICAL risk lacks PASS/NOT_REQUIRED security disposition.
- Any of the six scoring factors is absent or outside 0–100.

Ranking occurs only after hard gates pass.

| Priority factor | Weight |
|---|---:|
| Dependency unlock value | 25% |
| Risk reduction | 25% |
| Critical path impact | 20% |
| Urgency | 15% |
| Effort efficiency | 10% |
| Evidence confidence | 5% |
| **Total** | **100%** |

Score = Σ(factor value 0–100 × weight). Version the policy and retain prior decision runs.

## Structured prompt compiler

Prompt sections: Context, Objective, Evidence, Scope, Dependencies, Execution steps, Authorization, Acceptance criteria, Validation, Stop conditions and Reporting.

Production prompt binds Task ID, canonical source IDs/URLs, snapshot/decision run, target branch, HEAD SHA, PR, CI run, dependencies, approvals, security disposition, acceptance criteria and reporting schema. Prompts have context hashes; material context changes make an old prompt stale.

## Project Progress Analytics

Progress trend, milestone actual vs expected, baseline and target, execution health, dependency status, blocker pressure and weight coverage must be visible. A task count chart alone is not sufficient.

## Workflow Execution Tracker

Task detail includes canonical instruction and scope, source URL, start/status history, dependencies, agent/owner, branch, commit, PR, changed files, CI/tests, acceptance evidence, retry count, recovery and audit links. Historical transitions begin at the point history capture was enabled; earlier history must not be fabricated.

## Blockers, Errors & Diagnostics

Each issue records ID, severity, detection time, location, root-cause state, impact, affected items/milestones, resolution and verification. Shared causes are grouped under a stable root_cause_key and list all impacted work items.

## Change Intelligence

Notion and GitHub webhooks record provider, delivery ID, event, source, impact, follow-up, timestamp and before/after data. Event payloads are untrusted; canonical reconciliation retrieves the latest source state. The 15-minute schedule repairs missed/late events.

## Seven-layer architecture

1. Source Connector Layer.
2. Data Ingestion & Normalization.
3. Project State Reconciliation Engine.
4. Dependency & Risk Analysis Engine.
5. Strategic Decision Engine.
6. AI Prompt Compiler.
7. HSO Mission Control Dashboard.

LLM assists explanation and synthesis. Authority, dependency, approval, idempotency, freshness and state gates are deterministic backend rules.

## Refresh & recompute

1. Pull changes from connected sources.
2. Deduplicate and identify events.
3. Validate versions, timestamps and completeness.
4. Reconcile status and evidence.
5. Detect conflicts, dependencies and blockers.
6. Compute weighted progress, milestone health and risk.
7. Apply hard eligibility gates.
8. Rank only eligible tasks; select zero or one Primary Next Action.
9. Compile the prompt from the same source snapshot.
10. Refresh UI, analytics, notifications and audit.

Browser reload only updates the UI. Manual refresh calls the backend; webhooks provide low-latency triggers; the 15-minute schedule is a recovery path.

## Project Completion Intelligence — 12 deliverables

1. Source connectors & authority mapping.
2. Ingestion, normalization & provenance.
3. State reconciliation & freshness.
4. Dependency & risk hard gates.
5. Single primary next-action decision engine.
6. Snapshot-bound prompt compiler.
7. Weighted verified progress & milestone analytics.
8. Workflow execution tracker & history.
9. Diagnostics, root-cause grouping & change intelligence.
10. Mission Control dashboard.
11. Manual, webhook and scheduled synchronization.
12. Security, resilience, recovery and final acceptance.

The 12 required criteria have been seeded in `public.hso_completion_criteria`. Initial states are BUILDING, BUILT_UNVERIFIED and NOT_BUILT. Scope weights remain NULL until owners assess and justify them.

## Current delivery state

The foundation was merged by PR #21. Intelligence v2 is in `feat/hso-mission-control-intelligence-v2-20261124` and is not yet merged. Supabase Edge Functions active: `hso-notion-webhook`, `hso-github-webhook`, `hso-reconcile`, `hso-decision-engine`. Database schemas and required completion criteria are applied.

Live sync is not configured: the source registry currently has five NOT_CONFIGURED entries, zero work items, zero execution/evidence rows and zero sync runs. Supabase secrets, GitHub Actions repository variable/secret, Notion internal connection/webhook and first HSO admin membership are pending. Vercel project/deployment is not created because team authorization is pending.

No automated approval, merge, release, source overwrite or production deployment is enabled. Do not call the system production-ready before Preview, live integration, RLS adversarial tests, webhook replay and end-to-end acceptance pass.


## Measurement integrity contract

The authoritative rules for complete source snapshots, explicit scope decisions, owner-approved weights, publishable weighted progress, Verified evidence, Primary Next Action hard gates, trend comparability, and adversarial acceptance tests are defined in [`HSO-MISSION-CONTROL-MEASUREMENT-INTEGRITY-CONTRACT.md`](./HSO-MISSION-CONTROL-MEASUREMENT-INTEGRITY-CONTRACT.md). This contract supersedes any earlier wording that allowed a partial weighted subset to be presented as project-wide progress.
