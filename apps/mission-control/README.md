# HSO Mission Control

Next.js dashboard for evidence-based operational visibility across the Hypersystem Orchestrator ecosystem.

## Runtime boundary
- GitHub remains authoritative for source code, branches, commits, PRs, CI and releases.
- Notion remains authoritative for governance, decisions, roadmap and evidence index.
- Supabase stores normalized snapshots/read models, event inbox and sync audit.
- Vercel hosts the dashboard.
- The dashboard is read-only against source systems. It does not approve gates, merge PRs, deploy releases or mutate authority records.

## Local setup
1. Copy `.env.example` to `.env.local`.
2. Add the Supabase project URL and publishable key.
3. Add a server-only `HSO_SYNC_TOKEN` only after the matching Supabase Edge Function secret is configured.
4. Run `npm install`, `npm run dev`.
5. Sign in with Supabase Auth. An administrator must add the authenticated user ID to `public.hso_members` before data is visible.

## Environment
- `NEXT_PUBLIC_SUPABASE_URL`: project API URL.
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`: browser-safe publishable key.
- `HSO_SYNC_TOKEN`: server-only key to invoke manual refresh. Never prefix with NEXT_PUBLIC_.

Never place Supabase secret/service-role keys, Notion tokens, GitHub tokens or webhook secrets in browser variables.

## Vercel
Create/link a Vercel project with Root Directory `apps/mission-control`. Configure the environment variables in Preview first. Production deployment should wait until review and acceptance.
