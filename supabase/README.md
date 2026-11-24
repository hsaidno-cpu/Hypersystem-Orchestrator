# HSO Mission Control Supabase deployment

Project ref: `ehgmtkkppmceaffhwcpc` (HSMART).

## Migrations
- `20261124063356_hso_mission_control_foundation_v1.sql`
- `20261124063509_hso_mission_control_member_access_v1.sql`
- `20261124074200_hso_mission_control_hardening_and_notion_field_parity_v1.sql`

All new data tables use the `hso_*` prefix. The migration sequence does not alter unrelated project functions or schemas.

## Edge Functions
- `functions/hso-notion-webhook`
- `functions/hso-github-webhook`
- `functions/hso-reconcile`

The deployed v3 source is committed in these directories. Secrets are set through the Supabase Dashboard, never committed: `HSO_SYNC_TOKEN`, `NOTION_API_TOKEN`, `NOTION_WEBHOOK_VERIFICATION_TOKEN`, optional `GITHUB_WEBHOOK_SECRET`, optional `GITHUB_TOKEN`.

The service-role key is only available to the trusted Edge Function runtime. Never expose it in browser variables.
