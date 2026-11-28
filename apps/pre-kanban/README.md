# HSO Workboard UI

Original HSO-owned Kanban interface built with React, Vite and Supabase Auth/Postgres. The canonical board is **HSO Ecosystem Development**.

## Local development

1. Create a local `.env.local` file (never commit it):
   ```env
   VITE_SUPABASE_URL=https://<project-ref>.supabase.co
   VITE_SUPABASE_PUBLISHABLE_KEY=<publishable-key>
   ```
2. Apply the migrations to a development Supabase branch/project.
3. Enable the intended Supabase Auth email OTP provider and configure allowed redirect URLs.
4. For OAuth/MCP authorization, configure the Supabase OAuth Server with Authorization Path `/oauth/consent`, set the Site URL to this frontend origin, and use an asymmetric JWT signing key (ES256 or RS256). Keep dynamic client registration off until the client allow-list/governance policy is ready.
5. Install and run:
   ```bash
   npm install
   npm run dev
   ```

## Build

```bash
npm run build
npm run preview
```

The UI uses the signed-in user's JWT and RLS. Do not add a service-role key to `VITE_*` variables: browser variables are public by design.

The board is an original implementation. No Safrow source, brand assets or proprietary styles are included.


## Canonical workflow columns

The HSO Ecosystem Development board is initialized with these eight columns in this order:

`Intake` → `Backlog` → `Ready` → `In Progress` → `Blocked` → `Review & Verification` → `Done` → `Archive`.

The visible Archive column is a workflow destination. It is not the same as the backend's technical soft-archive flag or the `kanban.card.archive` tool.

A production Done transition must remain blocked until the independent completion-evidence gate described in Issue #64 is implemented, tested and deployed. Do not infer acceptance from a card description or AI comment.
