# HSO Mission Control implementation status

Updated: 2026-11-28

## Executive disposition

**PARTIALLY DEPLOYED.** PRE Federation is active and one PRE v0.1.6 → A.S.F.R.E.E/RPEDS repository/CI acceptance cycle is VERIFIED. HSO Mission Control's GitHub Actions path still has failed ingestion/reconciliation runs pending the OIDC/Vault source repair, merge, deployment and live read-back. These states must not be conflated.

## Canonical environment

- Repository: hsaidno-cpu/Hypersystem-Orchestrator.
- Supabase project: ehgmtkkppmceaffhwcpc (ACTIVE_HEALTHY, Postgres 17.12).
- PRE Federation Edge Function: pre-core-federation ACTIVE v7.
- HSO Mission Control deployed functions observed:
  - hso-github-webhook ACTIVE v4.
  - hso-reconcile ACTIVE v8.
  - hso-notion-webhook ACTIVE v5.
  - hso-decision-engine ACTIVE v7.
- Vault metadata confirms HSO_SYNC_TOKEN exists. Secret contents were not read or exposed. The helper pre_federation_get_secret(text) is SECURITY DEFINER and callable only by service_role and postgres.
- HSO dashboard tables use RLS; service-role access remains server-side.

## P0: source/deployment drift

The deployed Edge Function bodies did not match the HSO GitHub main source:

| Function | Deployed version | Deployed lines | Main source lines | Finding |
|---|---:|---:|---:|---|
| hso-github-webhook | v4 | 128 | 105 | Deployed change-event projection missing in main |
| hso-reconcile | v8 | 511 | 290 | Main source omits pagination, snapshot and richer Notion mappings |
| hso-notion-webhook | v5 | 155 | 98 | Deployed event and recovery logic missing in main |
| hso-decision-engine | v7 | 580 approx. | Not tracked | Deployed function and policy module absent from main |

The remediation branch restores the active deployed implementation as canonical source before introducing OIDC/Vault changes. Do not deploy stale main versions over the active functions.

## P0: Mission Control authentication repair (change branch)

The current main workflow .github/workflows/hso-mission-control-sync.yml expects HSO_GITHUB_WEBHOOK_URL and GitHub Actions secret HSO_SYNC_TOKEN. The scheduled and ingestion runs failed because that legacy configuration was unavailable:

- [Scheduled reconciliation failure — run 46045159313](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/46045159313).
- [Event ingestion failure — run 46037294270](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/46037294270).
- [Event ingestion failure — run 46037257259](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/46037257259).

The repair branch changes this to:
- GitHub Actions OIDC with id-token: write, no long-lived HSO token in GitHub Actions.
- Exact repository ID/name, main ref, workflow_ref, event allowlist, endpoint-specific audience, issuer, expiry and RS256/JWKS verification.
- Trusted main checkout only; pull_request_target event payloads are treated as untrusted data and no PR-head code is executed.
- Server-side Vault retrieval of HSO_SYNC_TOKEN for internal function-to-function calls and compatibility routes.
- SHA-256 canonical event payload hashes and unique (provider, delivery_id) idempotency.
- Restoration of deployed GitHub/Notion webhook and decision-engine source files.
- Unit/contract tests plus Deno type-check coverage for all restored Mission Control functions.

**This branch is not yet a deployed fix.** The workflow and Edge Functions must be merged/deployed before live acceptance is attempted.

## Current gate state

| Gate | State | Evidence / boundary |
|---|---|---|
| Supabase project health | PASS | Project reports ACTIVE_HEALTHY |
| PRE shared-DNA release integrity | PASS | 37 source pins, deterministic archive and independent verifier |
| PRE → RPEDS repository/CI acceptance | VERIFIED | Host receipt, version/digest read-back, AFSA policy and rollback ref |
| Mission Control schema/RLS | APPLIED | Tables and unique provider/delivery indexes present |
| Mission Control workflow on main | BLOCKED | Legacy webhook URL/shared-token configuration failed |
| Mission Control OIDC/Vault source repair | IN REVIEW | Separate branch; not live |
| HSO Edge Functions source parity | BLOCKED until merge | Four deployed/source drifts identified; source recovery in branch |
| Live GitHub event ingestion | NOT VERIFIED | Requires merge, deployment and persisted receipt read-back |
| Duplicate/replay idempotency | PARTIAL | Unique indexes exist; real replay test pending |
| Scheduled reconciliation | NOT VERIFIED | Must run after OIDC deployment and prove sync run/snapshots |
| Notion sync | BLOCKED / UNKNOWN | API connection and complete live source read-back not proven |
| Vercel admin/Preview | NOT VERIFIED | No new production deployment claim |
| PRE Standalone / HSAR / HSO host adoption | PENDING | Each needs distinct auth, profile, acceptance and receipt |
| Live Plugin Creator / remote MCP invocation | NOT VERIFIED | CI contract or skipped job is not runtime proof |

## Non-negotiable interpretation rules

- ACTIVE Edge Function means deployed, not authenticated end-to-end.
- OIDC acceptance requires token signature, issuer, exact audience, expiry, repository identity, main ref, workflow_ref and allowed event to pass.
- Event ingestion is not source reconciliation.
- A 2xx webhook response is not proof that all source snapshots are complete or fresh.
- A successful sync run is not a PRE host-adoption receipt.
- VERIFIED for RPEDS applies only to the documented private, non-commercial repository/CI acceptance boundary. It is not live Plugin Creator deployment, public redistribution or commercial permission.
- Auto-adoption remains disabled.
