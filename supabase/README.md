# HSO Mission Control Supabase deployment

Canonical platform display name: `Hypersystem-Orchestrator` (rename pending Management API write access).\n\nProject ref: `ehgmtkkppmceaffhwcpc` (immutable Supabase project identity; do not rename or rotate).

## Canonical identity\n\nSee [HSO Canonical Identity & Nomenclature Contract](../docs/HSO-CANONICAL-IDENTITY-AND-NOMENCLATURE.md) and [machine-readable registry](../config/hso-identity-registry.json). Use immutable Supabase `project_ref` and API URL for integrations. Only the provider display name is intended to change.\n\n## Applied migrations

- `20261124063356_hso_mission_control_foundation_v1.sql`
- `20261124063509_hso_mission_control_member_access_v1.sql`
- `20261124073651_hso_mission_control_hardening_and_notion_field_parity_v1.sql`
- `20261124112912_hso_mission_control_intelligence_model_v2.sql`
- `20261124113659_hso_mission_control_history_and_milestone_links_v1.sql`
- `20261124114137_hso_mission_control_milestone_target_and_execution_link_v1.sql`
- `20261124114745_hso_completion_criteria_baseline_v1.sql`
- `20261125010950_hso_measurement_integrity_and_scope_governance_v1.sql`
- `20261125023645_hso_notion_webhook_vault_bootstrap_v1.sql`

All Mission Control tables use the `hso_*` prefix. RLS is enabled and forced; browser access is limited to active allowlisted members. The `hso_integration_events` table is backend-only. The HSO Supabase project is distinct from the separate HSMART repository/project. Migrations do not modify unrelated HSMART tables or legacy functions.

## Edge Functions

- `functions/hso-notion-webhook` — deployed v5 (initial challenge bootstrap + Vault-backed HMAC verification)
- `functions/hso-github-webhook` — deployed v4
- `functions/hso-reconcile` — deployed v8 (complete pagination, snapshot proofs, source membership fingerprint)
- `functions/hso-decision-engine` — deployed v7 (same-run completeness gates, scope integrity, weighted-evidence-v2)

### Edge Function secrets

Set these secrets through Supabase Dashboard > Edge Functions > Secrets:

- Required: `HSO_SYNC_TOKEN`, `NOTION_API_TOKEN`
- Required for direct GitHub webhook signature validation: `GITHUB_WEBHOOK_SECRET`
- Recommended for GitHub API rate-limit resilience: least-privilege `GITHUB_TOKEN`
- Optional local/legacy override: `NOTION_WEBHOOK_VERIFICATION_TOKEN`

`SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are automatically injected by the Supabase Edge Runtime. Do not copy them into dashboard/browser variables or commit them to source control.

The initial Notion webhook challenge sends `verification_token` in its request body before normal signed event delivery starts. The Notion webhook function stores this token once in Supabase Vault under `hso_notion_webhook_verification_token`; subsequent events are validated using HMAC-SHA256 over the raw request body and `X-Notion-Signature`. The token is never printed to logs or returned in the HTTP response. After Notion sends the challenge, retrieve it in Supabase SQL Editor for the Notion Webhooks verification modal:

```sql
select decrypted_secret
from vault.decrypted_secrets
where name = 'hso_notion_webhook_verification_token';
```

The Vault RPCs are executable only by the trusted `service_role`; the browser's `anon` and `authenticated` roles cannot retrieve this token. If a webhook subscription must be recreated, an owner must delete the existing Vault row first, then create a new subscription:

```sql
delete from vault.secrets
where name = 'hso_notion_webhook_verification_token';
```

## Operational status

Deployed functions are not proof of live integration. The project currently has five source records in `not_configured` state and no successful sync run. Complete the credentials, Notion internal connection/webhook subscription and GitHub Actions variables before treating sync as live.

## Measurement Integrity

See [HSO Mission Control Measurement Integrity Contract](../docs/HSO-MISSION-CONTROL-MEASUREMENT-INTEGRITY-CONTRACT.md) for the complete measurement and decision contract.

Project-wide weighted progress is publishable only when the five mandatory sources have one complete, fresh snapshot in the same successful sync run; Roadmap membership matches the Supabase projection; every Work Item has an owner/date/rationale scope decision; all in-scope Task IDs are unique; and every in-scope Work Item has a positive, approved Scope Weight with rationale, approver and approval timestamp.

Formula:

`SUM(approved Scope Weight for independently Verified IN_SCOPE items) / SUM(approved Scope Weight for all IN_SCOPE items) × 100`

Partial weighted ratios are diagnostic only and must never populate the project headline percentage. Empty data or missing denominator is `UNMEASURED`, not 0%. Zero percent is valid only after a complete baseline exists and no in-scope item is independently Verified.

## Owner-approved baseline (2026-11-25)

The owner approved four terminal Roadmap Work Items (#10–#13) as `IN_SCOPE`, each weighted 25, for a total denominator of 100. Conditional P2 Work Item #14 remains `OUT_OF_SCOPE` until a named-host pilot proves production hardening is required. Program/Phase/Milestone roll-ups and the separate Ponytail pointer are excluded to avoid double-counting and cross-source scope drift. Equal weights are neutral v1 because the Roadmap contains no effort estimates or complete scoring inputs for differentiated weights.

This denominator is approved but not yet measured: no complete source sync has projected the Roadmap records into Supabase, and no verified numerator may be claimed.

## Current live state (2026-11-25)

- `hso-reconcile` v8 and `hso-decision-engine` v7 are ACTIVE.
- All five mandatory sources are still `not_configured`; no Work Items, executions, evidence, sync runs, progress snapshots, decisions or active HSO members are present.
- Credentials and first administrator still need to be configured directly on their platforms. Edge Function deployment is not evidence of source connectivity.
- No progress percentage or Primary Next Action is currently publishable.
- Do not use the service-role key in browser configuration or expose any secret in the repository.
