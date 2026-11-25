# HSO Mission Control — Measurement Integrity & Decision Eligibility Contract

**Contract version:** `measurement-integrity-v2`  
**Date:** 25 November 2026  
**Scope:** Supabase source reconciliation, verified-progress publication, strategic action eligibility, prompt provenance, dashboard disclosure  
**Status:** Implemented in PR #22 branch; migration applied to Supabase; live connectors remain unconfigured.

## 1. Non-claim rule

HSO must never manufacture a progress percentage or a Primary Next Action from incomplete, stale, ambiguous, partially paginated, or unverified data.

The dashboard distinguishes four things that are often incorrectly collapsed into one number:

1. **Observed work:** records currently read from sources.
2. **Scope baseline:** work items explicitly included or excluded by an accountable human.
3. **Execution state:** work recorded as started, implemented, or completed.
4. **Verified completion:** work accepted against fresh, linked evidence and the applicable gate.

A successful code build is not a live integration. A deployed Edge Function is not proof that its source credentials work. A completed task is not a verified task. A partial denominator is not a project percentage.

## 2. Source-completeness contract

Every decision run is bound to exactly one `sync_run_id`. The engine rejects missing or unknown sync-run IDs and does not fall back to the latest arbitrary snapshot.

The five mandatory sources are:

- `notion-control-center`
- `notion-roadmap`
- `notion-execution-ledger`
- `notion-evidence-registry`
- `github-hso-parent`

A sync run is decision-capable only when **all** of the following are true:

1. The referenced `hso_sync_runs` row has status `succeeded`.
2. Exactly one snapshot exists for each required source in that same sync run.
3. Each snapshot has `is_complete = true`, `pagination_complete = true`, `completeness_state = COMPLETE`, a content hash, a scope hash, and a fresh observation timestamp.
4. Each source registry entry is `connected`; its last successful and last complete timestamps both satisfy its freshness SLA.
5. Pagination is demonstrably exhausted. A result is never marked connected merely because the fetch loop stopped.
6. For Notion Roadmap, the sorted page-ID set in the complete source snapshot exactly equals the sorted `external_id` set in the Supabase projection. Missing, duplicated, or orphaned rows create `SCOPE_DRIFT` and suppress project-wide progress and action recommendations.

### 2.1 Pagination requirements

- Notion data-source queries continue until `has_more = false`. A missing or repeated cursor is an error.
- Notion Control Center block children are paginated recursively, including child blocks. The snapshot contains block identity, type, structure, and block payload.
- GitHub pull-request and Actions-run endpoints are fetched with 100 records per page until an endpoint returns fewer than 100 records.
- The current hard safety ceiling is 1,000 pages per paginated endpoint, 20 levels of Notion block nesting, and 20,000 Control Center blocks. Exceeding a ceiling is a hard error, never a successful partial read.
- Large Notion and GitHub upserts are sent in batches of 500; batching must not reduce the record set.

`hso_source_snapshots.scope_hash` fingerprints the sorted source membership IDs. `content_hash` fingerprints the full source snapshot and mapped source payload. These are different checks and are not interchangeable.

## 3. Explicit scope baseline

Only records whose `Record Type = Work Item` participate in the work-progress denominator. Program, Phase, Milestone, Decision, and Evaluation records are not silently counted as work items.

Every Work Item must have an explicit scope decision:

| Roadmap property | Required condition |
|---|---|
| Scope Inclusion State | `IN_SCOPE` or `OUT_OF_SCOPE`; `PENDING` is unresolved |
| Scope Decision By | Exactly one accountable human identity |
| Scope Decision At | Non-empty decision date |
| Scope Decision Rationale | Non-empty reason tied to scope |

No AI process may infer that a task is in scope or out of scope. An unresolved scope decision suppresses project-wide measurement and the Primary Next Action.

For all `IN_SCOPE` work items:

- Stable Task ID is mandatory.
- The normalized Task ID must be unique within the in-scope set. Numeric forms such as `10`, `010`, and `HSO-010` resolve to the same key and therefore conflict if duplicated.
- Missing or duplicated IDs create `SCOPE_CONFLICT`; the engine does not silently choose one record.

An `OUT_OF_SCOPE` item is excluded only when its owner, date, and rationale are present. It is not treated as completed and does not add weight to the denominator.

## 4. Scope-weight approval

A numeric `Scope Weight` is valid only when all of the following are true:

- Weight is a positive number.
- `Weight Rationale` is populated.
- `Scope Weight Approval = APPROVED`.
- `Scope Weight Approved By` identifies exactly one human approver.
- `Scope Weight Approved At` is populated.

A value that is present but pending, rejected, ownerless, or undated is **not an approved weight**. AI may explain the weighting criteria, but it may not invent, auto-fill, or approve Scope Weight.

The denominator includes every `IN_SCOPE` work item with an approved positive weight. The weight-approval coverage denominator is the number of all `IN_SCOPE` work items, not all Roadmap records.

## 5. Verified-progress mathematics

### 5.1 Publishable project progress

`Verified Weighted Progress` is:

`SUM(Scope Weight for independently Verified IN_SCOPE items) / SUM(Scope Weight for all IN_SCOPE items) × 100`

This is a publishable project percentage **only** when:

- all mandatory source snapshots are complete and fresh in the same successful sync run;
- Roadmap source membership exactly matches the database projection;
- every Work Item has an explicit scope decision;
- all in-scope Task IDs are present and unique;
- every in-scope item has a positive, approved weight with rationale, approver, and date; and
- the numerator uses independently verified items only.

If all denominator gates pass but no task has been verified, **0% is a valid measured result**. If no work items exist, no item is in scope, or no approved denominator exists, the result is `UNMEASURED`, not 0% and not 100%.

### 5.2 Partial diagnostics

When the source and scope decisions are complete but only some in-scope weights are approved:

- `weighted_progress_pct` remains `null`;
- `partial_weighted_progress_pct` may show the verified ratio among the approved-weight subset;
- `weight_coverage_pct` exposes the share of in-scope tasks whose weights are approved;
- the state is `PARTIAL_COVERAGE`; and
- the dashboard must label the partial ratio as **non-publishable**, never as project completion.

A partial ratio is useful for diagnostics. It is not an acceptable headline KPI.

### 5.3 Coverage and state semantics

| State | Meaning | Project percentage |
|---|---|---|
| `MEASURED` | Complete source, complete scope, unique IDs, all in-scope weights approved | Publishable |
| `PARTIAL_COVERAGE` | Source and scope complete; some in-scope weights remain unapproved/unweighted | Null; partial diagnostic only |
| `SCOPE_UNCONFIRMED` | At least one Work Item has no complete owner/date/rationale decision | Null |
| `SCOPE_CONFLICT` | Missing or duplicate in-scope Task ID | Null |
| `SCOPE_DRIFT` | Complete Notion Roadmap membership differs from the canonical database projection | Null |
| `SOURCE_INCOMPLETE` | One or more required sources, snapshots, pagination proofs, or sync-run conditions fail | Null |
| `UNMEASURED` | No work items, no in-scope work, or no approved weights exist | Null |

Scope-decision coverage and weight-approval coverage are diagnostic ratios, not substitutes for the project-progress percentage.

## 6. What counts as Verified

A task is included in the progress numerator only when:

- execution state is `Verified` or `Accepted`;
- gate state is `PASS`;
- the last evaluation is no older than seven days;
- linked Evidence Registry record exists for that exact Roadmap item;
- evidence state is `PASS`, `VERIFIED`, or `ACCEPTED`;
- evidence freshness is `FRESH`;
- verification timestamp is present and fresh (or a supported acceptance-evidence type has a fresh observation); and
- when commit SHA is declared, evidence SHA matches the declared CI/HEAD commit.

A task state of `Completed` or `Implemented` without that independent evidence is not counted as Verified.

Required deliverable criteria are evaluated separately from work-item progress. The dashboard may show `verified criteria / required criteria`, but it must not blend this count with weighted work-item progress or invent a combined completion percentage.

## 7. Primary Next Action eligibility

The engine may publish at most one Primary Next Action. Scoring is applied **after** all hard gates pass.

Global gates:

- same-run source completeness and freshness;
- successful sync-run status;
- exact Roadmap membership reconciliation;
- complete scope decisions for the whole Work Item inventory;
- unique stable Task IDs for every in-scope item.

Per-candidate gates:

- stable Task ID exists and is unique;
- scope is explicitly `IN_SCOPE`;
- status is `Ready`, `Not started`, or `In progress`;
- gate is `PASS`;
- dependencies are represented as stable IDs, resolve unambiguously, and are independently Verified;
- change surface and execution target are explicit;
- for CODE work, target branch and HEAD SHA are identified; if a PR is declared, fresh source evidence must match its URL, branch, and HEAD SHA;
- CI evidence is fresh, `PASS`, and bound to the exact HEAD SHA;
- required human approval is `APPROVED` and review SHA equals the target HEAD;
- security disposition is `PASS` or `NOT_REQUIRED` where policy requires it; and
- the six priority factors are present and within 0–100.

Priority is a ranking rule, not a permission override:

| Factor | Weight |
|---|---:|
| Dependency unlock value | 25% |
| Risk reduction | 25% |
| Critical path impact | 20% |
| Urgency | 15% |
| Effort efficiency | 10% |
| Evidence confidence | 5% |

If sources are incomplete, the result is `SOURCE_STALE`. If sources are complete but no candidate passes the gates, the result is `NO_ELIGIBLE_ACTION`. A high score cannot override missing data, unresolved scope, dependency failure, an exact-commit mismatch, approval, or security policy.

## 8. Decision and prompt provenance

Every progress snapshot carries:

- `source_sync_run_id`;
- a scope fingerprint;
- methodology version;
- publishability flag;
- measurement state and reason codes;
- weight, scope-decision, and weight-approval coverage; and
- computation timestamp.

Every decision run carries the same `source_sync_run_id`, snapshot coverage, and `decision_inputs_complete` flag. The Primary Action and prompt artifact may only be generated when the relevant source and scope gates pass.

The prompt is versioned and bound to the decision run and exact source snapshot IDs. A changed source snapshot, branch, HEAD SHA, dependency, approval, security disposition, or scope invalidates the old context and requires recomputation.

## 9. Trend comparability

`hso_progress_snapshots.scope_hash` fingerprints the ordered scope decisions and weights used in the calculation. Trend points are comparable only when:

- `is_publishable = true`;
- methodology version is `weighted-evidence-v2`; and
- scope hash matches the current publishable baseline.

If the latest snapshot is unpublishable or scope hash changes, the dashboard breaks the trend rather than drawing a continuous line across different denominators. Historic values remain in the database for audit, not for misleading visual continuity.

Milestone progress is tied to the same sync run as the global snapshot. Milestones without an explicit parent milestone relation are grouped as ecosystem stage, never silently promoted to formal milestones.

## 10. Reconciliation state machine

`REFRESH & RECOMPUTE` executes the following order:

1. Pull all five mandatory sources.
2. Exhaust all pagination cursors and recursively fetch Control Center child blocks.
3. Normalize, deduplicate, and batch-upsert source rows with provenance.
4. Create one complete/incomplete snapshot per source for the same sync run.
5. Mark the run `succeeded` only when every mandatory source completed; otherwise mark it partial/failed.
6. Reconcile Roadmap source membership against the canonical Supabase projection.
7. Evaluate source freshness, scope decisions, stable IDs, evidence and dependencies.
8. Calculate publishable progress or a non-publishable measurement state.
9. Apply action hard gates, then rank only eligible candidates.
10. Compile a snapshot-bound prompt only for a valid Primary Next Action.
11. Persist audit, diagnostics, progress, decision and prompt records.

Webhook events are low-latency triggers. The scheduled 15-minute reconciliation is recovery, not a substitute for completeness checks. Manual refresh forces backend reconciliation; browser reload does not.

## 11. Adversarial acceptance tests

Before production approval, verify at minimum:

1. More than six Notion pages and more than 100 GitHub records are fully paginated.
2. A pagination cursor repeats or the configured ceiling is reached: source must be degraded, never connected.
3. One required source snapshot is absent, duplicated, stale, or incomplete: no progress percentage and no Primary Action.
4. A Roadmap source page is missing from Supabase or an orphan remains in Supabase: `SCOPE_DRIFT`, no percentage/action.
5. One Work Item has `PENDING` scope, a missing owner/date/rationale, or an ambiguous identity: no project percentage and no Primary Action.
6. A duplicate normalized Task ID such as `10` and `HSO-010` exists in scope: `SCOPE_CONFLICT`.
7. One in-scope weight is null, unapproved, rejected, or missing rationale/approver/date: no project-wide percentage; partial diagnostic only if allowed by the state rules.
8. All approved weights exist but no item is independently Verified: a measured 0% is permitted.
9. A task is `Completed` without fresh acceptance evidence: it remains outside the verified numerator.
10. A dependency ID is missing, duplicated, or not Verified: that candidate is blocked.
11. CI is successful on a different SHA, stale, or belongs to a different declared PR/branch: that candidate is blocked.
12. Required approval is missing, rejected, or attached to a different SHA: that candidate is blocked.
13. Security disposition is `HOLD` or `FAIL`: that candidate is blocked.
14. Scope hash or methodology changes: historic trend is not joined across the break.
15. RLS tests prove anonymous denial, inactive-member denial, and authenticated active-member read-only behavior.

## 12. Current operational truth

At the time of this contract update, the production database still reports five required sources as `not_configured`, zero synchronized Work Items, zero execution rows, zero evidence rows, zero sync runs, zero progress snapshots, zero decision runs, and zero active HSO members. The 12 required completion criteria have no approved weights.

Therefore the only valid current project-progress result is **UNMEASURED**, and the only valid current strategic-action result is **no data-backed Primary Next Action**. This is an intentional safety state, not a failure to display a number.

PR #22 remains subject to exact-head CI, technical/security review, live integration tests, and Vercel Preview acceptance. These foundations do not authorize a production-ready claim by themselves.
