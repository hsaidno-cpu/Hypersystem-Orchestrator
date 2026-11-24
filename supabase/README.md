# Supabase deployment

Project: `ehgmtkkppmceaffhwcpc` (HSMART).

Migrations in this directory reproduce the HSO Mission Control schema and access model applied to the project. The HSO tables use the `hso_*` prefix; unrelated tables, schemas and functions are not managed by this project.

Deploy Edge Functions:
- `functions/hso-notion-webhook`
- `functions/hso-github-webhook`
- `functions/hso-reconcile`

Configure secrets through Supabase Dashboard > Edge Functions > Secrets:
`HSO_SYNC_TOKEN`, `NOTION_API_TOKEN`, `NOTION_WEBHOOK_VERIFICATION_TOKEN`, optional `GITHUB_WEBHOOK_SECRET`, optional `GITHUB_TOKEN`.

Never commit or expose `SUPABASE_SERVICE_ROLE_KEY`.
