# HSO Mission Control
Authenticated Next.js dashboard for evidence-based operational visibility.

- GitHub owns source code, refs, commits, pull requests and CI.
- Notion owns governance, roadmap, execution ledger and evidence index.
- Supabase stores normalized read-model projections, webhook inbox and sync audit.
- Vercel hosts the dashboard.
- Dashboard access requires Supabase Auth plus an active row in `public.hso_members`.

## Local setup
1. Copy `.env.example` to `.env.local`.
2. Configure the project URL and publishable key.
3. Add server-only `HSO_SYNC_TOKEN` only after configuring the same secret in Supabase Edge Functions.
4. Run `npm install` then `npm run dev`.
5. Sign in. An administrator must allowlist the authenticated user before any HSO data is exposed.

Do not put a secret/service-role key, Notion token or GitHub token in browser variables. Vercel Root Directory: `apps/mission-control`.
