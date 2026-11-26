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


## Security migration provenance — 25 November 2026

The deployed Supabase migration ledger was read after applying
`20261125125004_hso_rls_auto_enable_acl_lockdown_v1`. The database returned ten
applied migration records. This repository's `supabase/migrations/` directory
currently contains only three SQL files before this security migration source is
added. The deployed third record is version `20261124073651`, while the similarly
named repository file is timestamped `20261124074200`; this is not exact
filename/version parity.

This PR adds the source SQL for the already-applied ACL lockdown migration. It
does **not** reconstruct missing historical migration files or claim full
migration-ledger parity. Before future production changes, reconcile every
deployed version, migration name, source SQL and repository path against the
database's migration ledger. Do not fabricate historical SQL from schema state.

The ACL migration revokes function execution from `PUBLIC`, `anon`,
`authenticated`, and `service_role`. It leaves the function owned by
`postgres` and preserves the `ensure_rls` event trigger. The live database
verification performed after application is recorded in the HSMART × HSO UEDE
Build Journal.
