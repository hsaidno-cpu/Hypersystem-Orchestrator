# PRE R0-R9 Policy & State Transition Enforcement v1.0

**Implementation status:** policy engine implemented on a PR branch; CI validation required; live Notion enforcement is not activated.  
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
5. The host adapter persists the evaluation receipt in the queue. It may apply stage transition only for ALLOW and only with revision compare-and-swap.
6. Notion receives the applied stage, evaluation digest, source commit, correlation ID, audit receipt and timestamp.
7. PRE schedules the next lifecycle evaluation. It never runs or approves the underlying engineering tests.

## Notion queue

The companion database is **PRE Transition Queue — Policy Evaluations**. It stores each transition request, its related Work Item, Evidence Envelope JSON, Approval Receipt JSON, evaluation digest, decision, blockers, correlation ID and application receipt. It is a queue and evaluation ledger, not an authority source.

## Current limitations and activation gates

- This PR implements the deterministic policy evaluator, schema policy, CLI, unit tests, and CI validation workflow.
- The connected Notion API token is not provisioned as a GitHub Actions secret, and the Notion integration has not been shared with the new queue or the existing Work Item/Evidence data sources.
- There is not yet a deployed persistent PRE worker, webhook subscription, or shared durable nonce store.
- The current GitHub connector cannot configure repository secrets, variables, environments, or Notion integration sharing.
- Therefore this branch is **not** a claim that live Notion stage changes are automatically enforced yet. Production activation requires the queue integration, least-privilege credential provisioning, a durable shared nonce store, service deployment, and live create/evaluate/hold/allow/apply/read-back tests.

## Commands

```bash
python tools/pre_policy_engine.py evaluate \
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
