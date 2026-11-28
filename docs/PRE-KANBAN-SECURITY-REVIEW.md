# PRE Kanban Security Review

Review date: 2026-11-28  
Scope: PR #59 source, Supabase migrations and MCP/UI authorization boundary.  
Disposition: **Source hardening in progress; not production-approved.**

## Security decisions

1. **No service-role path in MCP requests.** Edge Function middleware validates a user JWT and supplies a caller-scoped Supabase client. Data access remains subject to Postgres RLS.
2. **OAuth discovery is not anonymous tool access.** Supabase protected-resource metadata is discoverable before login. Tool requests still pass through `withSupabase({ auth: "user" })`.
3. **Workspace membership is the tenant boundary.** Roles are owner, admin, editor, member and viewer. Only owners can grant owner/admin. Admins cannot promote themselves or other members to owner/admin, and cannot edit their own membership row.
4. **Sync state is RPC-owned.** Authenticated clients cannot directly insert/update/delete sync runs, bindings, events or outbox rows. The preview, claim, item apply, finalize, read-back, acknowledge and conflict RPCs are the only intended state-transition path.
5. **Apply is bound to a stored preview.** A worker-specific claim token fences stale workers; each item must exactly match an item in the approved preview JSON; per-item card/binding/event changes commit in one database transaction.
6. **Outbox is transactional.** A card update and its outbound event are committed together. Source-to-board writes set a transaction-local suppression flag to prevent echo loops.
7. **Audit metadata is append-only at the database role boundary.** Authenticated users cannot update/delete audit rows. This does not make Postgres an independently immutable WORM system.

## OAuth configuration prerequisites

Before enabling the OAuth server:
- Deploy the UI and set the Supabase Site URL to its HTTPS origin.
- Set the Authorization Path to `/oauth/consent`.
- Use an asymmetric JWT signing key (ES256 or RS256).
- Keep PKCE enabled and register exact, trusted redirect URIs for OAuth clients.
- Keep dynamic client registration disabled until a client onboarding and monitoring policy is approved.
- Verify that the consent page preserves `authorization_id` when the user must sign in, and shows the client name, redirect URI and requested identity scopes before approval.
- Test first consent, repeat consent, denial, token refresh, access revocation and unauthenticated tool rejection.

## Current permission model and limitation

Supabase OAuth scopes currently describe identity claims (for example, `openid`, `email`, `profile`), not individual Kanban tools. A client receives the effective permissions of the signed-in user in each workspace. RLS and workspace roles still restrict data access, but this release does **not** implement per-OAuth-client workspace roles or per-tool capabilities. Build a client-grant registry keyed by the OAuth `client_id` before allowing less-trusted AI clients that need narrower permissions.

## Synchronization trust boundary

- The PRE/HSO adapter must apply outbox changes to the canonical PRE/HSO source and perform source-side read-back before it submits an acknowledgment.
- The acknowledgment RPC stores the read-back URL and SHA-256 digest. It does not independently fetch the URL, validate a signed receipt, or verify the digest against the external source.
- Signed receipt verification, anti-replay nonce tracking and external immutable/WORM audit anchoring remain separate controls.
- A Kanban card's column does not mutate PRE R0–R9 stage, gate, milestone acceptance or evidence disposition.

## Validation still required

- Run all six migrations on a dedicated development branch/database.
- Run Supabase Security Advisor and Performance Advisor on that development branch after migrations.
- Test owner/admin/editor/member/viewer and cross-workspace isolation with real authenticated JWTs.
- Test claim-token takeover, concurrent apply, partial retry, duplicate events, source conflict and read-back.
- Run MCP Inspector and multiple intended MCP clients against the deployed development endpoint.
- Deploy the frontend to a separate project/domain and test OAuth consent in a real browser.
- Complete PRE/HSO adapter acceptance and signed receipt verification before loading operational work items.

## Production baseline observed before Kanban migration

The existing main project Security Advisor reported eight pre-existing `rls_enabled_no_policy` informational findings on `hso_migration_*` tables. The Performance Advisor also reported existing unused-index and unindexed-foreign-key findings on unrelated HSO tables. No Kanban migration had been applied when this baseline was read. Re-run advisors on the development branch to distinguish new Kanban findings from the pre-existing baseline; do not silence unrelated findings as part of this PR.
