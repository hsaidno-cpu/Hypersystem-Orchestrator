# HSO Mission Control — Operator Runbook

## Initial setup gate

1. Add Supabase Edge Function secrets `HSO_WEBHOOK_SIGNING_SECRET` and `HSO_SYNC_TOKEN` as separate random values of at least 32 bytes. Also configure `NOTION_API_TOKEN` and any provider tokens required by enabled sources.
2. Add `HSO_GITHUB_WEBHOOK_URL` as a GitHub Actions repository variable, pointing exactly to the deployed `/functions/v1/hso-github-webhook` endpoint. Add matching `HSO_SYNC_TOKEN` and the same `HSO_WEBHOOK_SIGNING_SECRET` as GitHub Actions repository secrets.
3. The HSO Actions event signature covers `timestamp.delivery_id.event_type.raw_body`; the Edge Function rejects timestamps outside a five-minute window, invalid signatures, and duplicate delivery IDs. The legacy raw-body `GITHUB_WEBHOOK_SECRET` signature path is not supported. Never reuse `HSO_SYNC_TOKEN` as the signing secret.
4. Scheduled reconciliation calls `/functions/v1/hso-reconcile` with `X-HSO-Sync-Token`; it does not use the webhook signing secret.
5. Create a Notion internal connection, grant least-privilege access to the HSO source pages/data sources, then register its connection webhook.
6. Authorize the Vercel team connection and set the project's environment variables in Preview first.
7. Sign in and add the first administrator to `public.hso_members` under controlled SQL.

## Manual refresh

- Sign in as an active HSO member.
- Use **Refresh sources**.
- Confirm a new row in `public.hso_sync_runs`.
- Check source `status`, `last_sync_at`, and `last_error`.
- Missing Notion credentials must show `not_configured`, not a successful empty sync.

## Incident handling

- Invalid webhook signature: rotate the secret and inspect provider configuration. Never disable verification.
- Duplicate delivery: verify unique provider/delivery key; duplicate should be a no-op.
- Notion 401/403: inspect the connection token and page/data-source sharing. Do not broaden workspace access unnecessarily.
- GitHub 403/429: use least-privilege token, respect rate limits, then reconcile.
- Partial sync: inspect source_results and repair only the failed source.
- Stale source: do not decide from stale state; restore the connection and reconcile.
- Conflicting records: source authority matrix wins; do not overwrite source records.

## Rollback

- Disable the repository workflow or remove the webhook subscription first.
- Redeploy a previous Edge Function version from source-controlled code.
- Do not drop HSO tables to roll back quickly; preserve sync runs and evidence.
- Disable Preview deployment without changing source repositories or Notion records.

## Acceptance checklist

- [ ] Deno type-check and Edge Function handler tests pass on the exact PR head.
- [ ] Webhook HMAC positive/negative, expired timestamp, and legacy-signature rejection tests pass.
- [ ] Duplicate delivery returns 409 and causes no second side effect.
- [ ] Scheduled reconciliation is tested with the dedicated sync token.
- [ ] Live event is read back from `hso_integration_events` and `hso_change_events`.
- [ ] GitHub push, PR update and exact-head workflow run are reflected in Supabase.
- [ ] Notion Roadmap, Execution Ledger and Evidence Registry are re-read.
- [ ] Manual refresh is membership-gated.
- [ ] Scheduled reconciliation runs every 15 minutes and creates a verified `hso_sync_runs` row.
- [ ] Each configured source has a read-back `hso_sources` status and corresponding complete `hso_source_snapshots` rows for the same `sync_run_id`.
- [ ] Source failures are surfaced; stale data is never called fresh.
- [ ] Supabase RLS and advisor review complete.
- [ ] Vercel Preview build and smoke test pass.
- [ ] No automation changes approval, source authority or release state.
