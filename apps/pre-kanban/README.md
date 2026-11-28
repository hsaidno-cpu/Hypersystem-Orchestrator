# PRE Kanban UI

Original HSO-owned Kanban interface built with React, Vite and Supabase Auth/Postgres.

## Local development

1. Create a local `.env.local` file (never commit it):
   ```env
   VITE_SUPABASE_URL=https://<project-ref>.supabase.co
   VITE_SUPABASE_PUBLISHABLE_KEY=<publishable-key>
   ```
2. Apply the migrations to a development Supabase branch/project.
3. Enable the intended Supabase Auth email OTP provider and configure allowed redirect URLs.
4. Install and run:
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
