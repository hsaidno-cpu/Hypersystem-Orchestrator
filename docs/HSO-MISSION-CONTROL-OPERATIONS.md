# HSO Mission Control — Operator Runbook

## Initial setup gate

1. Add Edge Function secrets in Supabase.
2. Add `HSO_GITHUB_WEBHOOK_URL` repository variable and matching `HSO_SYNC_TOKEN` secret in GitHub.
3. Create a Notion internal connection, grant least-privilege access to the HSO source pages/data sources, then register its connection webhook.
4. Authorize the Vercel team connection and set the project's environment variables in Preview first.
5. Sign in and add the first administrator to `public.hso_members` under controlled SQL.

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

- [ ] Webhook HMAC positive and negative tests pass.
- [ ] Duplicate event creates one inbox row.
- [ ] GitHub push, PR update and exact-head workflow run are reflected in Supabase.
- [ ] Notion Roadmap, Execution Ledger and Evidence Registry are re-read.
- [ ] Manual refresh is membership-gated.
- [ ] Scheduled reconciliation runs every 15 minutes.
- [ ] Source failures are surfaced; stale data is never called fresh.
- [ ] Supabase RLS and advisor review complete.
- [ ] Vercel Preview build and smoke test pass.
- [ ] No automation changes approval, source authority or release state.
