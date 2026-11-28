# PRE Kanban Backend, MCP Server & Board UI

## Decision and ownership

This is a new HSO-owned Kanban service. It is not a fork of Safrow Kanban and does not depend on Safrow's read-only MCP server. The HSO repository owns the cross-platform integration service; PRE remains the canonical owner of roadmap stages, milestone acceptance, gates and evidence disposition.

No Safrow code, logos, stylesheets, images, or proprietary assets are copied. The interface uses generic Kanban interaction patterns only. Any future reuse of Safrow source or distinctive assets requires a separate license review and explicit approval.

## Source status

This change introduces source artifacts on branch `feat/pre-kanban-mcp-backend-20261128`. It does **not**:
- apply a migration to the production Supabase database;
- deploy the MCP Edge Function;
- configure Supabase OAuth provider settings, client registration, consent or redirect URIs;
- deploy the board frontend;
- create a production workspace or PRE board;
- enable automatic PRE source writes.

The service must be tested in a development Supabase branch/project first. A source merge is not a deployment or runtime acceptance.

## Architecture

- **Database:** Supabase Postgres stores workspaces, members, boards, columns, cards, labels, sync bindings, sync runs, sync events, outbox events and append-only audit metadata.
- **MCP endpoint:** Supabase Edge Function `pre-kanban-mcp`, using MCP TypeScript SDK v2 and Streamable HTTP.
- **Identity:** Supabase Auth OAuth 2.1 / PKCE with the MCP Protected Resource metadata middleware. Every MCP request passes through `withSupabase({ auth: "user" })`; each tool receives a caller-scoped Supabase client.
- **Authorization:** workspace membership roles and Postgres RLS. The MCP request path does not use a service-role key.
- **UI:** React/Vite frontend uses the same Auth and RLS-protected Postgres tables as MCP clients. A human and an AI client therefore see the same records and revisions.
- **PRE adapter:** the adapter is the controlled bridge that translates canonical PRE work items to Kanban bindings and consumes board-originated outbox events.

## MCP endpoint and transport

After deployment, the endpoint will be:

`https://<project-ref>.supabase.co/functions/v1/pre-kanban-mcp/mcp`

Protocol package: `@modelcontextprotocol/server@2.4.0`, which supports the 2026-07-28 MCP protocol revision through `createMcpHandler`. The handler is stateless per HTTP request; durable state is in Postgres, not an Edge Function isolate.

Supabase Auth OAuth must be explicitly enabled and configured before clients can connect. Configure the authorization UI/consent flow, PKCE, trusted redirect URIs, client registration policy, and user approval. Do not enable open dynamic registration without monitoring and consent controls.

The function has `verify_jwt = false` only because OAuth protected-resource discovery must be reachable before a bearer token exists. The function itself is protected by `withSupabase({ auth: "user" })`; tool calls are not anonymous. Do not remove that middleware or change its mode to `none`.

Set `PRE_KANBAN_ALLOWED_ORIGINS` to a comma-separated allowlist of trusted browser origins. Non-browser MCP clients without an Origin header are allowed through to the OAuth/JWT layer.

## MCP tool registry

### Workspace bootstrap
- `kanban.workspace.list`
- `kanban.workspace.create`
- `kanban.workspace.add_member`

### Board Manager
- `kanban.board.list`
- `kanban.board.get`
- `kanban.board.create`
- `kanban.board.update`

### Column Manager
- `kanban.column.list`
- `kanban.column.create`
- `kanban.column.reorder`

### Card Manager
- `kanban.card.list`
- `kanban.card.get`
- `kanban.card.create`
- `kanban.card.update`
- `kanban.card.move`
- `kanban.card.archive`

### Label Manager
- `kanban.label.create`
- `kanban.label.assign`
- `kanban.label.remove`

### Synchronization
- `kanban.sync.preview`
- `kanban.sync.apply`
- `kanban.sync.read_back`
- `kanban.sync.status`
- `kanban.sync.outbox.list`
- `kanban.sync.outbox.acknowledge`
- `kanban.sync.outbox.conflict`

### Audit Manager
- `kanban.audit.list`
- `kanban.audit.get`

## Data and synchronization contract

### Authority

- PRE owns canonical R0–R9 stage, roadmap progress, acceptance gates, milestone decisions and evidence disposition.
- GitHub owns repository/PR/commit/CI state.
- Notion/HSO ledgers own their canonical decision and evidence records.
- Kanban owns board layout, columns, card presentation, labels and visual work state.
- The adapter owns synchronization bindings, run state, conflict records and receipts.

A Kanban card moving to Done never implies that PRE accepted a milestone or advanced an R-stage.

### Source to board

1. The adapter sends a normalized PRE/HSO snapshot to `kanban.sync.preview`.
2. PREVIEW is read-only with respect to cards and returns a digest-bound plan.
3. `kanban.sync.apply` requires the exact preview digest and explicit `confirm_apply=true`.
4. A Postgres row lock claims the sync run. Stale APPLYING runs can be reclaimed after the configured five-minute recovery window.
5. Each item is applied by `kanban_apply_sync_item` in a single Postgres transaction: card + source binding + sync event commit or roll back together.
6. A read-back checks the persistent binding, source digest, card existence and recorded board revision.

The source-to-board operation is idempotent for unchanged source digests. Revisions changed by a board user create a conflict rather than silently overwriting the user's edit.

### Board to source

For a `bidirectional` binding, user-originated card updates create a transactional row in `kanban_sync_outbox`. The outbox event is inserted in the same database transaction as the card update. Changes applied by the source-to-board RPC suppress outbox capture, preventing echo loops.

The PRE/HSO adapter consumes `kanban.sync.outbox.list`, applies the change to the canonical source through its authorized source API, performs source read-back, then calls `kanban.sync.outbox.acknowledge` with the source revision, HTTPS receipt locator and digest. Conflicts are preserved using `kanban.sync.outbox.conflict`.

**Important boundary:** this repository change implements the persistent outbox and MCP consumption/acknowledgment contract. The external PRE/HSO adapter dispatch into canonical PRE and its independent receipt verification are a separate integration workstream. An acknowledgment stores the supplied receipt reference and digest; the MCP server does not independently cryptographically verify the external receipt. Do not call end-to-end two-way synchronization production-ready until the adapter and source-side acceptance tests are complete.

## Security and audit

- Every public data table has RLS enabled and explicit grants.
- Roles: owner, admin, editor, member and viewer. Workspace membership is the tenant boundary.
- The MCP function uses the authenticated user's Supabase client; it does not elevate to service_role.
- Mutations on cards/boards/columns use server-side revisions and expected-revision checks.
- Sync preview has a digest and expiry. Apply has an explicit confirmation flag and atomic claim.
- Audit records store entity/action/actor/revision/request metadata, not complete card descriptions or secrets.
- Audit rows reject UPDATE/DELETE through a trigger.
- PostgreSQL append-only metadata is not equivalent to cryptographic immutability or external WORM storage. External signed audit anchoring remains a later assurance control.
- Never put Supabase secret/service-role keys, OAuth client secrets, issuer private keys or API credentials in browser code, Git, audit payloads, or MCP tool arguments.

## Frontend

The UI source lives under `apps/pre-kanban/`. Set:
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY`

The UI uses Supabase Auth email OTP and RLS. It provides workspace/board selection, board creation, six default columns, card creation, drag-and-drop movement, and sign-out. No user identity or board ID is hardcoded.

## Migrations

Apply the migrations in order to a disposable/development Supabase branch first:

1. `20261128020000_pre_kanban_backend_v1.sql`
2. `20261128020100_pre_kanban_sync_atomic_claim_v1.sql`
3. `20261128020200_pre_kanban_sync_outbox_v1.sql`
4. `20261128020300_pre_kanban_outbox_ack_v1.sql`

Run SQL validation, RLS role tests (viewer/member/editor/admin/owner), Supabase Security Advisors, Edge Function type checks, MCP Inspector tests and browser UI tests before any production application.

## Required acceptance tests

- OAuth discovery and user-consented login work for each intended MCP client.
- Unauthenticated tool calls are rejected; no anonymous or service-role bypass exists.
- A viewer cannot create/update/move cards or mutate workspace membership.
- A member can create/move cards but cannot manage board configuration or audit.
- An editor can manage board/card/sync and read operational audit, but cannot change PRE lifecycle authority.
- A duplicate source event produces no duplicate card.
- Simultaneous apply requests cannot claim one sync run twice.
- A crashed worker can reclaim a stale run; replayed items are idempotent.
- Source updates cannot overwrite a card changed since the last binding revision.
- A bidirectional card edit creates one outbox item; source-originated updates do not create echo events.
- The outbox is acknowledged only after source-side application and read-back evidence exists.
- Audit rows are readable only by owner/admin and cannot be changed by authenticated workspace members.
- MCP Inspector confirms tool discovery and schemas.
- Frontend and MCP operations read/write the same persisted database records.

## Release boundary

Keep this feature behind a separate deployment. Do not change or redeploy `pre-core-federation`, do not activate the PRE R0–R9 enforcement worker, and do not mutate canonical PRE stages as part of Kanban CRUD.
