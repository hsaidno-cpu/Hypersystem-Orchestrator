# HSO Mission Control Supabase deployment

Project ref: `ehgmtkkppmceaffhwcpc` (HSMART).

## Applied migrations

- `20261124063356_hso_mission_control_foundation_v1.sql`
- `20261124063509_hso_mission_control_member_access_v1.sql`
- `20261124073651_hso_mission_control_hardening_and_notion_field_parity_v1.sql`
- `20261124112912_hso_mission_control_intelligence_model_v2.sql`
- `20261124113659_hso_mission_control_history_and_milestone_links_v1.sql`
- `20261124114137_hso_mission_control_milestone_target_and_execution_link_v1.sql`
- `20261124114745_hso_completion_criteria_baseline_v1.sql`

All Mission Control tables use the `hso_*` prefix. RLS is enabled and forced; browser access is limited to active allowlisted members. The `hso_integration_events` table is backend-only. Migrations do not modify unrelated HSMART tables or legacy functions.

## Edge Functions

- `functions/hso-notion-webhook` — deployed v4
- `functions/hso-github-webhook` — deployed v4
- `functions/hso-reconcile` — deployed v7
- `functions/hso-decision-engine` — deployed v5

Set secrets through Supabase Dashboard > Edge Functions > Secrets:
`HSO_SYNC_TOKEN`, `NOTION_API_TOKEN`, `NOTION_WEBHOOK_VERIFICATION_TOKEN`, optional `GITHUB_WEBHOOK_SECRET`, optional `GITHUB_TOKEN`.

The service-role key is only available to the trusted Edge Function runtime. Never expose it in browser variables or commit it to source control.

## Operational status

Deployed functions are not proof of live integration. The project currently has five source records in `not_configured` state and no successful sync run. Complete the credentials, Notion webhook subscription and GitHub Actions variables before treating sync as live.
