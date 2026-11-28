# HSO LokalBoards deployment

This directory contains a deployment template for running the upstream
[ L o k a l B o a r d s ](https://github.com/florian-strasser/LokalBoards)
application as a separate HSO work-management service.

**This is deployment configuration, not a live installation.** A persistent
container host, public HTTPS domain, and operational owner must be provisioned
before the service can be started for HSO.

## Why this is separate from Mission Control

LokalBoards is a long-running Node.js application with Socket.IO real-time
updates, a built-in MCP endpoint, a MySQL database, and uploaded-file storage.
HSO Mission Control is a Vercel Next.js application and its existing Supabase
database is PostgreSQL. Do not deploy this Compose stack as a Vercel function
or point LokalBoards at the HSO PostgreSQL database.

Keep the responsibility split:

- GitHub remains authoritative for source code, schemas, tests, issues, PRs,
  governance and release history.
- LokalBoards owns work state, board columns, card assignment and coordination.
- HSO/PRE evaluate actual progress from evidence; a Kanban status alone is not
  proof that code is implemented or a deployment is healthy.
- Notion remains a documentation and knowledge surface, not a competing
  implementation source of truth.

## Requirements

- A persistent Docker Engine host with Docker Compose v2.
- A public DNS name and HTTPS reverse proxy (Caddy, Nginx, Traefik, or the
  hosting provider's managed ingress).
- Persistent Docker volumes for MySQL data and `/app/public/uploads`.
- Backups and a tested restore procedure.
- A secrets facility or protected host-level `.env` file. Never store real
  secrets in this repository.

The HSO Vercel team currently has Next.js projects, not a verified long-running
Docker host. Provisioning a new paid service or VPS requires an explicit
infrastructure/billing decision.

## Deploy

1. Copy `.env.example` to `.env`.
2. Set a real HTTPS `NUXT_BOARDS_URL`, administrator e-mail/password, and a
   different strong `MYSQL_PASSWORD`. Generate passwords with a secure random
   generator; do not reuse GitHub, Supabase, or personal credentials.
3. Configure the public reverse proxy to forward HTTPS traffic to
   `http://127.0.0.1:3000`. Keep the raw application port off the public
   Internet. Configure `NUXT_TRUST_PROXY` to match the actual proxy topology.
4. Check the rendered configuration and start the stack:

   ```bash
   docker compose --env-file .env config --quiet
   docker compose --env-file .env pull
   docker compose --env-file .env up -d
   docker compose ps
   ```

5. Verify the instance from the host and through the public HTTPS address:

   ```bash
   curl -fsS http://127.0.0.1:3000/api/health
   curl -fsS "${NUXT_BOARDS_URL}/api/health"
   ```

   The expected response is HTTP 200 with application and database status
   reported as `ok`. Do not mark the deployment ready until it survives a
   restart and the data volumes have been backed up.

The application creates its database tables on first startup. The bootstrap
administrator credentials are consumed only while no administrator exists.
Public sign-up is disabled in the supplied configuration.

## Initial HSO board

Create one board named **HSO Ecosystem Development** with these areas:

1. Intake
2. Backlog
3. Ready
4. In Progress
5. Blocked
6. Review & Verification
7. Done
8. Archive

Seed cards from verified HSO GitHub issues, pull requests, roadmap artifacts and
architecture documents. Each card should include:

- A concise outcome and acceptance criteria.
- Canonical GitHub issue/PR and repository links.
- Relevant Notion documentation links, when present.
- Dependencies and blocker references.
- Verification evidence required before moving to Done.

LokalBoards cards support Markdown descriptions and comments. Keep dependency
relationships explicit as linked references until a dedicated dependency model
is implemented and tested; do not assume a native dependency graph exists.

## MCP access and operating controls

The upstream application exposes Streamable HTTP at `/mcp`. Its MCP tools can
list boards, inspect a complete board tree, search cards, create/update/move
cards, comment, and atomically claim/release work.

After deployment:

1. Sign in as the administrator and verify the canonical instance URL.
2. Create a separate account marked as an AI agent; do not share a human
   administrator's session or credentials.
3. Invite the agent only to the HSO board(s) it needs.
4. Create an agent API key with read-only scope for the initial inspection
   phase. Upgrade to full access only after authorization and write tests pass.
5. Verify `whoami`, `listBoards`, `getBoardTree`, and a controlled test
   create/update/move/read-back cycle. Revoke the test key afterward.
6. Enable board webhooks only after a receiving HSO worker exists and validates
   requests, deduplicates events, and records audit receipts.

ChatGPT's custom MCP connector uses OAuth, not a pasted API key. Current
OpenAI documentation limits custom MCP connections and full write support to
supported Business and Enterprise/Edu workspaces. The currently connected
ChatGPT Free plan cannot activate this connector. Other MCP clients and an
OpenAI API/Responses API integration can use the endpoint with an appropriate
API-key or bearer-token flow; those are separate from ChatGPT's custom
connector feature.

## Persistence, backup and upgrades

The stack stores state in two named volumes:

- `database`: MySQL data.
- `uploads`: uploaded files under `/app/public/uploads`.

Back up both. Use a consistent database dump and archive the uploads volume.
Run a restore drill before accepting production data. Do not assume a container
restart or image rollback restores deleted data.

The upstream security policy currently supports only the latest release. The
Compose template pins a reviewed release for reproducibility; periodically
review upstream releases and security notes, update `LOKALBOARDS_VERSION`,
pull the new image, and verify the health endpoint plus MCP read/write tests.

## Current status

- Upstream repository/license and Docker/MCP requirements inspected.
- Deployment Compose and environment templates prepared.
- **Not deployed:** persistent runtime, DNS/HTTPS, production secrets, and
  backup/restore operations are not provisioned or verified.
- **Not connected:** no MCP client has been authorized against a live instance.
- **Not seeded:** the canonical HSO board and its cards will be created only
  after the service passes health, persistence, identity and MCP acceptance.

Tracking issue: https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/issues/60
