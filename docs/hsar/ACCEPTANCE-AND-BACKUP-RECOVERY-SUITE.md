# HSAR Acceptance, Checkpoint, Backup and Recovery Suite

**Version:** 0.3.0  
**Status:** Contract and static tests added; runtime/integration cases pending named-host execution.

## Acceptance layers

- STATIC_CONTRACT: package/schema/route/output-contract tests.
- INTEGRATION: actual connector/plugin/tool call-through with read/write-scoped sandbox receipts.
- HOST_RUNTIME: named platform, permission, side-effect, end-to-end and recovery tests.

A test definition is not a test execution. A test result must contain case ID, tested version, exact source SHA/package digest, preconditions, expected result, actual result, status, environment, evidence locator and limitations.

## Required suite coverage

The HSAR 0.3.0 package includes 28 case definitions covering:
- Six primary spearhead identity, order, invocation states, version gates and handoff completeness.
- Conditional ecosystem-plugin routing and role/authority collision.
- Adaptive methodology candidate/screen/pilot/validate/adopt/reject/defer/retire lifecycle.
- Method conflicts, counterevidence and no invented “latest/best” claims.
- Four core analytical tables and conditional 4+2 comparative expansion.
- N/A scoring for unknown evidence, anchored classification, fairness and non-compensating hard gates.
- L1–L4 gate boundaries and named-host authorization.
- Specialist outage, checkpoint, manifest/hash, restore, replay, duplicate protection and quarantine.
- Secret redaction, source provenance and no permission-bypass behavior.
- GitHub→Notion create/update/no-op, duplicate/replay, stale source, permission, auth, timeout, rate-limit and read-back.

## Checkpoint and recovery contract

1. Freeze the last verified checkpoint before any specialist handoff or large scan stage.
2. Store immutable checkpoint ID, case/roadmap revision, exact source baselines, skill/plugin versions, stage status, outputs, content hashes and next action.
3. Redact credentials and personal/restricted data before checkpoint serialization. Never include secret values.
4. Keep separate latest_attempt and latest_verified_checkpoint; do not replace a verified state with an incomplete attempt.
5. On outage, classify transient, permanent, permission, version mismatch, integrity or unknown failure.
6. Retry only transient errors within a declared bound. Do not retry permission denial or integrity mismatch as though transient.
7. Resume from last verified checkpoint, re-read source heads and reconcile dependencies before continuing.
8. Replay idempotently using stable operation IDs and content hashes. If an action is not idempotent, require compensation/rollback and human approval before replay.
9. Restore into an isolated target first; verify hashes, schemas, object counts and referential/dependency integrity before promoting the restored state.
10. Record recovery time and data-loss window only when measured. Do not invent RPO/RTO. If no safe recovery path exists, preserve partial state and stop BLOCKED.

## Current static result

The package-local static contract test suite executed against HSAR 0.3.0: **16 passed, 0 failed**. This does not prove external specialist invocation, GitHub/Notion integration, host runtime or restore execution. Those remain NOT_RUN until receipts exist.

## Definition of Done

All applicable static tests must pass. Every integration/host case must either have a genuine receipt or remain explicitly NOT_RUN/BLOCKED. Failed tests have a disposition. Any backup/recovery claim requires actual restore and replay evidence. Record exact release, commit, coverage denominator, human decision and residual risks.
