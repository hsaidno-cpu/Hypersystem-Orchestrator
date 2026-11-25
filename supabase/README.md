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
- `20261125010950_hso_measurement_integrity_and_scope_governance_v1.sql`

All Mission Control tables use the `hso_*` prefix. RLS is enabled and forced; browser access is limited to active allowlisted members. The `hso_integration_events` table is backend-only. Migrations do not modify unrelated HSMART tables or legacy functions.

## Edge Functions

- `functions/hso-notion-webhook` — deployed v4
- `functions/hso-github-webhook` — deployed v4
- `functions/hso-reconcile` — deployed v8 (complete pagination, snapshot proofs, source membership fingerprint)
- `functions/hso-decision-engine` — deployed v7 (same-run completeness gates, scope integrity, weighted-evidence-v2)

Set secrets through Supabase Dashboard > Edge Functions > Secrets:
`HSO_SYNC_TOKEN`, `NOTION_API_TOKEN`, `NOTION_WEBHOOK_VERIFICATION_TOKEN`, optional `GITHUB_WEBHOOK_SECRET`, optional `GITHUB_TOKEN`.

The service-role key is only available to the trusted Edge Function runtime. Never expose it in browser variables or commit it to source control.

## Operational status

Deployed functions are not proof of live integration. The project currently has five source records in `not_configured` state and no successful sync run. Complete the credentials, Notion webhook subscription and GitHub Actions variables before treating sync as live.

## Measurement Integrity

See [HSO Mission Control Measurement Integrity Contract](../docs/HSO-MISSION-CONTROL-MEASUREMENT-INTEGRITY-CONTRACT.md) for the complete measurement and decision contract.

Project-wide weighted progress is publishable only when the five mandatory sources have one complete, fresh snapshot in the same successful sync run; Roadmap membership matches the Supabase projection; every Work Item has an owner/date/rationale scope decision; all in-scope Task IDs are unique; and every in-scope Work Item has a positive, approved Scope Weight with rationale, approver and approval timestamp.

Formula:

`SUM(approved Scope Weight for independently Verified IN_SCOPE items) / SUM(approved Scope Weight for all IN_SCOPE items) × 100`

Partial weighted ratios are diagnostic only and must never populate the project headline percentage. Empty data or missing denominator is `UNMEASURED`, not 0%. Zero percent is valid only after a complete baseline exists and no in-scope item is independently Verified.

## Current live state (2026-11-25)

- `hso-reconcile` v8 and `hso-decision-engine` v7 are ACTIVE.
- All five mandatory sources are still `not_configured`; no Work Items, executions, evidence, sync runs, progress snapshots, decisions or active HSO members are present.
- Credentials and first administrator still need to be configured directly on their platforms. Edge Function deployment is not evidence of source connectivity.
- No progress percentage or Primary Next Action is currently publishable.
- Do not use the service-role key in browser configuration or expose any secret in the repository.
