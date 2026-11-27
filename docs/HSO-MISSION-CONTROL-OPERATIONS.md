# HSO Mission Control — Operator Runbook

## Security model

Mission Control has two separate inbound authentication patterns:

1. GitHub Actions → HSO GitHub webhook/reconciler: short-lived GitHub Actions OIDC JWT, with different audiences for each endpoint.
2. Notion → HSO Notion webhook: Notion HMAC signature over the raw request body.

The OIDC verifier accepts only the canonical HSO repository, repository ID, main branch, exact workflow_ref, permitted event names, endpoint audience and a valid RS256 signature under GitHub JWKS. Supabase platform verify_jwt remains disabled for these provider/service endpoints because GitHub OIDC is not a Supabase Auth user JWT; the handler is the authentication boundary.

HSO_SYNC_TOKEN remains an internal server-to-server credential stored in Supabase Vault. Edge Functions retrieve it via pre_federation_get_secret using service-role access. Never copy it into GitHub Actions secrets, issue comments, Notion, browser code or logs. The GitHub Actions workflow requires id-token: write; it must not require an HSO shared token.

## Initial setup / migration gates

1. Merge the Mission Control OIDC/Vault source-repair PR only after Python contract tests and Deno checks pass.
2. Deploy hso-github-webhook, hso-reconcile, hso-notion-webhook and hso-decision-engine from the reconciled, source-controlled files. Never redeploy a stale source snapshot.
3. Confirm each deployed version and source hash against the merged main revision.
4. Confirm HSO_SYNC_TOKEN remains in Vault and that pre_federation_get_secret is callable only by service_role/owner. Do not read its value into logs or a report.
5. Confirm GitHub Actions has the OIDC permission, trusted-main checkout, expected workflow_ref and no HSO token secret reference.
6. Provision Notion API credentials and Notion webhook subscription separately, using least-privilege access to HSO source pages/data sources only.
7. Configure Vercel server-side environment separately; never use a NEXT_PUBLIC_ prefix for privileged credentials.
8. Complete admin allowlist onboarding through the controlled procedure. Never auto-promote the first authenticated user.

## Event ingestion and reconciliation

- GitHub push, PR-target metadata and Catalog validation workflow completion are observed via the canonical Actions workflow.
- The workflow checks out main only; the PR payload is data, not executable input.
- GitHub webhook event IDs must be stable for retries of the same Actions run.
- The inbox and change-event tables have unique (provider, delivery_id) indexes. A replay must not create duplicate rows.
- The 15-minute scheduled job uses a distinct OIDC audience for hso-reconcile.
- Reconciliation re-reads authoritative GitHub/Notion data; it never treats webhook payload order as canonical state.
- Inspect hso_sync_runs, hso_sources, hso_source_snapshots, freshness/completeness fields, record counts and errors. A partial or incomplete run is not PASS.
- The reconciler can call the decision engine internally using the Vault-backed service credential; failure of the decision engine must remain visible.

## Manual refresh

- Sign in as an active HSO member.
- Use Refresh sources.
- Confirm a new row in public.hso_sync_runs.
- Check source status, last_sync_at, last_error, snapshots and pagination completeness.
- Missing Notion credentials must show not_configured, not a successful empty sync.

## Incident handling

- OIDC 401: check workflow_ref, repo ID/name, ref, event name, audience, token expiry and JWKS availability. Never disable signature verification.
- Notion 401/403: inspect the connection token and page/data-source sharing; do not broaden workspace access.
- Duplicate delivery: verify the unique provider/delivery key and check that retry is a no-op.
- GitHub 403/429: use a least-privilege read token if provisioned; respect rate limits, then reconcile.
- Partial sync: inspect source_results and repair only the failed source.
- Stale source: do not decide from stale state; restore the connection and reconcile.
- Source/deployment drift: compare the active deployed function body and import files against the exact main commit; do not overwrite a richer deployment with an older repository version.
- Conflicting records: source authority matrix wins; do not overwrite source records.

## Rollback

- Disable the GitHub Actions event/schedule workflow first if authentication or payload validation regresses.
- Redeploy the last known-good Edge Function version from its source-controlled immutable commit.
- Keep the internal Vault secret available for rollback-compatible function-to-function calls; never expose or rotate it casually during an incident.
- Do not drop HSO tables, event inboxes or snapshots to roll back; preserve sync runs and evidence.
- Disable Preview deployment without changing source repositories or Notion records.

## Acceptance checklist

- [ ] Python OIDC emitter unit tests pass.
- [ ] Edge Function Deno checks pass for shared OIDC helper, GitHub webhook, reconciler, Notion webhook and decision engine.
- [ ] Exact OIDC audience/repository/ref/workflow/event checks pass; invalid or wrong-audience token is denied.
- [ ] GitHub push, PR metadata and exact workflow run are reflected in Supabase with provenance.
- [ ] Replaying the same delivery ID creates one inbox row and one change-event row.
- [ ] Scheduled reconciliation succeeds and creates complete, fresh source snapshots.
- [ ] Reconciliation status and per-source errors are preserved.
- [ ] Notion Roadmap, Execution Ledger, Evidence Registry and Control Center are re-read only when credentials and page access are valid.
- [ ] Manual refresh is membership-gated.
- [ ] No HSO shared secret is referenced by GitHub Actions or exposed client-side.
- [ ] Supabase RLS and security review complete.
- [ ] Vercel Preview build and smoke test pass.
- [ ] No automation changes approval, source authority or release/adoption state.
