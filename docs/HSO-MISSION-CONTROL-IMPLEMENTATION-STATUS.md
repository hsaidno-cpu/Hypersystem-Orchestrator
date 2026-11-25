# HSO Mission Control implementation status

Updated: 2026-11-24

## Current implementation

- Canonical repository: `hsaidno-cpu/Hypersystem-Orchestrator`.
- Feature branch: `feat/hso-mission-control-foundation-20261124`.
- Draft PR: #21.
- Next.js app: `apps/mission-control`.
- Supabase project: `ehgmtkkppmceaffhwcpc`.
- Applied migration versions: `20261124063356`, `20261124063509`, `20261124074200`.
- Edge Functions: `hso-notion-webhook` v3, `hso-github-webhook` v3, `hso-reconcile` v3.
- GitHub app build/typecheck exact-head CI: passed on `6858d77c810a0785d14aa7acef363dc42a03c730`.
- Integration workflow: passed in NOT_CONFIGURED skip mode; no claim of live sync.
- Catalog validation: fails on pre-existing compatibility status assertion mismatch; isolated from this dashboard build.

## Current gate state

| Gate | State | Notes |
|---|---|---|
| Repository implementation | READY FOR REVIEW | Draft PR only |
| Database foundation | APPLIED | HSO tables + RLS |
| Edge Function deployment | ACTIVE | v3; secrets still required |
| Dashboard build | PASS | Typecheck + Next build |
| Live GitHub events | BLOCKED | Repository variable/secret absent |
| Live Notion events | BLOCKED | Notion internal connection/token/webhook absent |
| Scheduled reconciliation | BLOCKED | Workflow must be merged to default branch and secrets configured |
| First admin access | BLOCKED | No active row in `hso_members` yet |
| Vercel project | BLOCKED | Waiting for team consent; no deployment created |

## Edge Function behavior (v3)

- Notion webhook supports signed verification challenge and event HMAC verification.
- Both Notion and GitHub event endpoints persist an idempotent event then attempt immediate reconciliation using `HSO_SYNC_TOKEN`.
- Failed immediate invocation does not discard the inbox event; the 15-minute scheduled reconciler is the recovery mechanism.
- Reconciler reads latest source state and maps actual Notion schema properties into normalized fields. Missing integration credentials remain explicitly not configured.
- Event ingestion alone never promotes a source to connected.

## Required external configuration

1. Supabase Edge Function secrets: `HSO_SYNC_TOKEN`, `NOTION_API_TOKEN`, `NOTION_WEBHOOK_VERIFICATION_TOKEN`; optional `GITHUB_TOKEN` and `GITHUB_WEBHOOK_SECRET`.
2. GitHub Actions variable `HSO_GITHUB_WEBHOOK_URL` and secret `HSO_SYNC_TOKEN`.
3. Notion internal connection shared only with the four HSO source pages/databases, plus its webhook subscription.
4. Vercel team consent, Git link, project environment variables.
5. Add the first administrator to `public.hso_members` after Supabase Auth sign-in.

Do not merge or deploy production based only on app build success. Complete data mapping, security, sync, access and preview acceptance first.


## Operational security update — 2026-11-26

- PR #29 introduces a dedicated `HSO_WEBHOOK_SIGNING_SECRET`; it is distinct from `HSO_SYNC_TOKEN` and is required by both the Supabase GitHub webhook Edge Function and the GitHub Actions event emitter.
- The event signature binds the timestamp, delivery ID, event type, and exact raw body. Timestamps outside the five-minute acceptance window are rejected. Duplicate provider/delivery IDs return HTTP 409 without triggering reconciliation again.
- Legacy raw-body `GITHUB_WEBHOOK_SECRET` signature fallback has been removed from the PR handler. The previous deployed v4 runtime still had this fallback at the time of this update; production runtime replacement remains a separate deployment gate.
- Catalog validation now runs Deno type-check and the Edge Function handler test suite. The sync workflow fails closed when any of the three event configuration values is absent; scheduled reconciliation requires the endpoint and dedicated sync token.
- Live acceptance remains BLOCKED until the PR changes are accepted and deployed, the three webhook configuration values are installed, Notion/GitHub source credentials are authorized, and live event/scheduled reconciliation read-back is complete.
- Database baseline read-back at update time: `hso_integration_events=0`, `hso_change_events=0`, `hso_sync_runs=0`, `hso_source_snapshots=0`; all five source definitions are `not_configured`. These are observed counts, not seeded or simulated test rows.