# PRE R0-R9 Policy & State Transition Enforcement v1.0

**Implementation status:** deterministic policy engine, Notion queue worker and scheduled self-hosted workflow are implemented on PR #17; exact-head CI and live activation remain gated. No persistent PRE worker is currently deployed.  
**Authority:** PRE evaluates the transition. It does not replace the accountable human decision owner or approve its own implementation.

## Purpose

Replace the manual-only PRE checklist with a deterministic policy evaluator that consumes versioned evidence envelopes and returns one of three outcomes:

- `ALLOW`: every transition requirement is satisfied, required signed approvals verify, and approval nonces are consumed in the configured nonce store.
- `HOLD`: evidence or required authority is missing, stale, or not yet configured.
- `DENY`: transition is illegal, evidence is malformed or invalid, approval is forged/expired/self-approved, or an approval nonce is replayed.

The evaluator does not write the canonical roadmap stage. A trusted host adapter must apply an `ALLOW` result with compare-and-swap against the exact expected source revision, then write back the applied receipt. No event, CI result, or AI assertion may change a gate by itself.

## Transition contract

The machine accepts only adjacent transitions:

`R0 → R1 → R2 → R3 → R4 → R5 → R6 → R7 → R8 → R9`

Every edge has a policy-defined evidence requirement. R2→R3, R5→R6, R7→R8 and R8→R9 require signed approval receipts from the appropriate human authority role. Stage skipping is denied. R9 is terminal; a new planning cycle must use a new scope/revision rather than silently reopening a closed lifecycle.

## Evidence envelope

Every evidence entry must include a stable evidence ID, evidence type, state, freshness, a verifier distinct from the request actor, a canonical HTTPS source locator, and SHA-256 digest. Only accepted states and FRESH evidence count. Skipped, unknown, stale, unsigned, unverified or source-less evidence never counts as pass.

## Approval contract

Approval receipts are HMAC-SHA256 signed by a trusted issuer and bound to the project scope, exact from/to stage, approver identity, role, issue/expiry time, and nonce. The evaluator rejects self-approval, unverified identity, untrusted issuer, role mismatch, signature mismatch, future/expired receipt, excessive validity window and nonce replay.

The key is supplied only as `HSO_PRE_APPROVAL_HMAC_KEY`; it must never be committed or placed in Notion. The SQLite nonce store included here is for tests and a single persistent service instance only. Multi-worker production requires a shared transactional nonce store. A GitHub-hosted ephemeral runner is not a durable replay-prevention service.

## Operational flow

1. Execution plane produces evidence envelopes and execution receipts.
2. A transition request is created in the Notion PRE Transition Queue with project/scope, from/to stages, evidence envelope and approval receipt references.
3. The service loads the canonical PRE policy, resolves the exact work item revision and fetches source evidence.
4. The policy engine evaluates evidence and authority; missing/invalid conditions return HOLD or DENY.
5. The queue worker first claims a PENDING request as EVALUATING, then evaluates policy, persists a decision receipt and reads the row back by page ID, decision, state and digest.
6. The worker sets the queue row to POLICY_PASSED, HOLD or REJECTED only after the evaluation data has been read back. EVALUATING rows are polled again, so a crash after a claim can be resumed. Approval nonce consumption is idempotent only for the exact same logical request and receipt.
7. The worker never updates the canonical Work Item PRE Stage. POLICY_PASSED means the transition contract passed, not that a human accepted a milestone or that the stage has been applied.
8. A separate stage-application service must be designed with identity-bound authorization, source-revision compare-and-swap, signed application receipt and stronger permission isolation before automatic roadmap stage writes are permitted.
9. PRE schedules the next lifecycle evaluation. It never runs or approves the underlying engineering tests.

## Notion queue

The companion database is **PRE Transition Queue — Policy Evaluations**. It stores each transition request, its related Work Item, Evidence Envelope JSON, Approval Receipt JSON, evaluation digest, decision, blockers, correlation ID and application receipt. It is a queue and evaluation ledger, not an authority source.

## Current limitations and activation gates

- This PR implements the deterministic policy evaluator, queue worker, queue schema contract, unit tests, CI validation workflow, and a scheduled polling workflow.
- The polling workflow is gated by repository variable `HSO_PRE_ENFORCEMENT_ENABLED=true` and requires a persistent self-hosted runner labelled `hso-pre-enforcement`; it must use a persistent nonce-store path.
- The GitHub Actions environment `hso-pre-runtime` must be created and provisioned with `HSO_PRE_NOTION_API_KEY` and `HSO_PRE_APPROVAL_HMAC_KEY`; repository variables `HSO_PRE_NOTION_DATA_SOURCE_ID` and `HSO_PRE_NONCE_STORE_PATH` must also be configured.
- The Notion integration must be shared with the PRE Transition Queue and have only the permissions required to read/update that queue. It must not have unrestricted permission to update canonical Work Item stage fields.
- The HMAC key validates receipts from a trusted approval issuer; it must not be used as an ad-hoc key to mint human approvals. A production identity issuer must authenticate the approver and bind its immutable subject, role, scope, transition, expiry and nonce into the signed receipt.
- SQLite nonce storage is appropriate only for one persistent worker. Multi-worker production requires a shared transactional nonce store.
- The current GitHub connector cannot configure repository secrets, variables, environments, self-hosted runners, or Notion integration sharing.
- Therefore this branch is **not** a claim that live Notion enforcement is activated. It is a tested worker and scheduled-service implementation awaiting environment provisioning, runner registration, integration sharing, and live controlled acceptance. It evaluates gates and writes decision receipts; it does not automatically apply PRE Stage transitions.

## Commands

```bash
python -m tools.pre_policy_engine evaluate \
  --request-file examples/pre-transition-r0-r1.example.json \
  --output /tmp/pre-evaluation.json
```

For approval-gated transitions, supply `HSO_PRE_APPROVAL_HMAC_KEY` and a persistent nonce-store path:

```bash
HSO_PRE_APPROVAL_HMAC_KEY=<secret> python tools/pre_policy_engine.py evaluate \
  --request-file request.json \
  --nonce-store /var/lib/hso/pre-nonces.sqlite \
  --output evaluation.json
```

Do not run approval-gated production transitions on ephemeral CI storage.
