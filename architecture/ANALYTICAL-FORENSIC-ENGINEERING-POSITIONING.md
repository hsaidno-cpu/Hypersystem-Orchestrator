# SKILL ANALYZER, A.S.F.R.E.E and SDO — Positioning Contract
**26 November 2026.** This contract preserves method overlap while separating decision rights.

## Core distinction
- **SKILL ANALYZER (SA): analytical method authority.** Decides how to reason: method selection, evidence quality, comparative analysis, hypotheses, risk and evaluation criteria. It owns analytical judgement, not repository writes.
- **A.S.F.R.E.E: technical forensic authority.** Establishes what the actual source/package/runtime contains, provenance, structure, dependencies, behavior, integrity and defects. It owns forensic findings and authorized reconstruction plans, not release approval.
- **Skill Developer Orchestrator (SDO): engineering lifecycle authority.** Converts accepted findings into bounded code changes, controls the single-writer workflow, edits source, runs tests, prepares PR/release evidence. It cannot independently approve its own implementation.
- **Evaluator Team: independent challenge.** Tests counter-evidence and acceptance criteria. The builder cannot self-certify.
- **HSO: ecosystem arbitration.** Owns cross-plugin routing and compatibility, not every specialist's domain truth.

## Positioning matrix

| Decision/work | SKILL ANALYZER | A.S.F.R.E.E | SDO |
|---|---|---|---|
| Primary question | Which reasoning/evaluation method is justified? | What is actually present in source/package/runtime? | What bounded change safely closes the accepted gap? |
| Inputs | Problem, claims, hypotheses, evidence, context | Exact repo/commit, package release, file manifest, dependencies, logs, tests | Approved change brief, baseline SHA, criteria, authority |
| Owns | Analytical decomposition, method selection, evidence grading, alternatives, risk, evaluation criteria | Component anatomy, provenance, structural/behavioral analysis, root-cause evidence, integrity, reconstruction plan | Single-writer branch/change, implementation, tests, regression, PR/release handoff |
| Must not own | Canonical source writes, package publication, release rights | General domain methodology, lifecycle merge/release, rights it does not hold | Independent acceptance, clinical/legal decisions, self-certification |
| Output | Method matrix, evidence ledger, competing explanations, confidence, decision brief | File/component map, dependency graph, source-target diff, defect/root-cause dossier | Patch/branch/commit, test report, PR, release and rollback receipt |
| Useful overlap | Evidence audit, root cause, comparison, validation | Evidence audit, root cause, structure, comparison | Tests, verification, remediation, quality gates |

## Handoff sequence
1. SA frames scope, hypotheses, methods, evidence quality, counter-evidence and acceptance criteria. No writes.
2. A.S.F.R.E.E inspects the exact authorized artifact; pins commit/release; maps files, skills, tools, references, dependencies, permissions and behavior.
3. Evaluator Team independently challenges the findings, root cause and test design.
4. SDO implements the smallest accepted change on one branch under a single writer lease; runs regression; opens PR. No self-approval.
5. A.S.F.R.E.E rechecks source integrity and behavior; Evaluator Team independently accepts/rejects.
6. HSO arbitrates plugin ownership, route priority, non-duplication, dependencies and handoff contracts.

## Handoff envelope
case ID; plugin/capability ID; decision owner; source repository/commit/path/blob SHA; package ID/release/version/file digest; target repo/branch/path/blob SHA; finding/root-cause/parity/risk; positive/negative test IDs; approval state; writer lease; reviewer; evidence digest; receipt URI.

Unknown or NOT_RUN is never PASS. A commit is not an acceptance receipt.

## Measured drift baseline
| Plugin | Plugin Creator | Canonical source | Earlier exact file parity | Rights evidence | Risk |
|---|---:|---:|---:|---|---|
| SKILL ANALYZER | 1.0.0 | 1.3.0 @ c469af7977c9bf6dcb3f5ab7b085a6de20d87004 | 11/12 | No root LICENSE located | Package behind source; one known instruction drift |
| SDO | 0.1.0 | 0.1.0 @ 9d3c4bc09179ff857df4f3819be83e1847571add | 0/4 | Apache-2.0 | Version labels match but content does not |
| A.S.F.R.E.E | 0.3.2 | 0.5.0-rc.1 @ a5eb55db0f6c2c6126a7fbcba645caf44c660c93 | 5/13 | PolyForm Noncommercial 1.0.0 | Source RC ahead; retain license restriction |

These are earlier file-level results, not proof of current runtime or whole-package parity. Re-run against current Plugin Creator release IDs and pinned commits before closing drift.

## Non-overlap rules
- SA says **how to reason**; A.S.F.R.E.E proves **what exists**; SDO performs **the approved change**.
- SDO is the only writer for a given change surface. Do not run simultaneous writers.
- Evaluator Team owns independent challenge and acceptance recommendation.
- HSO owns ecosystem arbitration, not clinical or other specialist truth.
- PRE owns roadmap gate interpretation; HSO consumes approved evidence but does not silently take over its decisions.
- PVEE owns health-claim Fact Lock and qualified human health-content approvals.
