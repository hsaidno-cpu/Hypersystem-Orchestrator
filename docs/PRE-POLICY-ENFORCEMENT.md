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

Every evidence entry must include a stable evidence ID, type, project and scope binding, state, freshness, verifier subject and role, identity-verification assertion, verification time, trusted issuer, canonical HTTPS source locator, source SHA-256 digest, and Ed25519 signature. The signature covers all of those fields. The policy engine checks allowed issuer/role, scope binding, verifier independence, timestamp freshness, digest shape and signature using a public key. Only accepted states and FRESH evidence count. Skipped, unknown, stale, unsigned, unverified or source-less evidence never counts as pass.

The private key belongs only to the trusted evidence issuer. The PRE worker receives the public key and cannot sign or mint evidence receipts. The issuer must authenticate the verifier (for example with a validated OIDC identity) and independently verify the source before signing; merely setting `identity_verified=true` is not sufficient unless it is protected by that issuer signature.

## Approval contract

Approval receipts are Ed25519 signed by a trusted approval issuer and bound to the project scope, exact from/to stage, immutable approver subject, authority role, issuer, issue/expiry time, and nonce. The evaluator verifies the signature using `HSO_PRE_APPROVAL_PUBLIC_KEY`; only the public key is available to the worker. The private key remains in the external approval issuer. The evaluator rejects self-approval, unverified identity, untrusted issuer, role mismatch, signature mismatch, future/expired receipt, excessive validity window and nonce replay.

The issuer must authenticate the approver through a real identity provider and apply the required role/scope policy before it signs. The GitHub workflow and the PRE evaluator must not generate human approvals. The SQLite nonce store included here is for tests and a single persistent service instance only. Multi-worker production requires a shared transactional nonce store. A GitHub-hosted ephemeral runner is not a durable replay-prevention service.

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
- The GitHub Actions environment `hso-pre-runtime` must be created and provisioned with `HSO_PRE_NOTION_API_KEY`; repository/environment variables `HSO_PRE_APPROVAL_PUBLIC_KEY` and `HSO_EVIDENCE_ISSUER_PUBLIC_KEY` must be set to the Ed25519 public keys; `HSO_PRE_NOTION_DATA_SOURCE_ID` and `HSO_PRE_NONCE_STORE_PATH` must also be configured.
- The Notion integration must be shared with the PRE Transition Queue and have only the permissions required to read/update that queue. It must not have unrestricted permission to update canonical Work Item stage fields.
- Ed25519 private keys for evidence and approval receipts must remain in separate trusted issuer services or a secrets manager/HSM. Only public keys are provided to the PRE worker. A production identity issuer must authenticate the approver and bind its immutable subject, role, scope, transition, expiry and nonce into the signed receipt. An evidence issuer must authenticate the verifier and verify the source before signing. These issuer services are not deployed by this PR.
- SQLite nonce storage is appropriate only for one persistent worker. Multi-worker production requires a shared transactional nonce store.
- The current GitHub connector cannot configure repository secrets, variables, environments, self-hosted runners, or Notion integration sharing.
- Therefore this branch is **not** a claim that live Notion enforcement is activated. It is a tested worker and scheduled-service implementation awaiting environment provisioning, runner registration, integration sharing, and live controlled acceptance. It evaluates gates and writes decision receipts; it does not automatically apply PRE Stage transitions.

## Commands

```bash
python -m pip install --requirement requirements-pre.txt
HSO_EVIDENCE_ISSUER_PUBLIC_KEY=<base64-ed25519-public-key> \
  python -m tools.pre_policy_engine evaluate \
  --request-file signed-request.json \
  --output /tmp/pre-evaluation.json
```

For approval-gated transitions, supply the issuer's public key and a persistent nonce-store path:

```bash
HSO_PRE_APPROVAL_PUBLIC_KEY=<base64-ed25519-public-key> \
HSO_EVIDENCE_ISSUER_PUBLIC_KEY=<base64-ed25519-public-key> \
  python -m tools.pre_policy_engine evaluate \
  --request-file signed-request.json \
  --nonce-store /var/lib/hso/pre-nonces.sqlite \
  --output evaluation.json
```

Do not run approval-gated production transitions on ephemeral CI storage.
