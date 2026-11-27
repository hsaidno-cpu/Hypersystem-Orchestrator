# HSO Mission Control — Architecture & Integration Contract v1.0

**Status:** PARTIALLY DEPLOYED — PRE federation is active; Mission Control OIDC migration and source reconciliation are under implementation.  
**Date:** 2026-11-28  
**Repository:** https://github.com/hsaidno-cpu/Hypersystem-Orchestrator

## Purpose

Mission Control is HSO's operational observability and decision-support layer. It does not replace the existing source documents, repositories, governance authorities, PRE or plugin-specific owners.

## Source authority

| System | Authority | Mission Control responsibility |
|---|---|---|
| GitHub | Code, refs, commits, PRs, CI, workflow runs and releases | Observe exact commit/PR/run evidence |
| Notion Control Center | Governance, policies and accountable decisions | Read approved control state |
| Notion Master Roadmap | Milestones, dependencies, priorities and scope | Read the work-item projection |
| Notion Execution Ledger | Actual runs, retries, receipts and recovery | Read execution evidence |
| Notion Evidence Registry | Evidence claims, provenance and limitations | Read and index evidence records |
| Supabase | Operational read model, inbox and snapshots | Never overrides authoritative sources |
| Vercel | Dashboard hosting | Host only; no authority over project state |

No global bidirectional overwrite is allowed. Changes are normalized into Supabase projections. Future write-back must be source-specific, idempotent, evidence-backed and separately authorized.

## Architecture

```text
GitHub push / PR / workflow_run -> GitHub Actions signed event emitter --+
                                                                         +--> Supabase Edge Functions
Notion page/database webhook -------------------------------------------+        |
                                                                                  v
                                                  integration inbox / sync runs / immutable snapshots
                                                  roadmap / execution / evidence projections
                                                                                  |
                                                                                  v
                                                        Next.js Mission Control (Vercel + Supabase Auth)
                                                                                  |
                                                                                  v
                                                         Human review and authorized decisions
```

Webhooks are low-latency change signals. The 15-minute scheduled reconciliation re-reads canonical sources and repairs missed, duplicate or out-of-order deliveries.

## Deployed components

| Component | Supabase slug | Purpose |
|---|---|---|
| Notion webhook | `hso-notion-webhook` | Verify Notion HMAC and record compact event metadata |
| GitHub webhook | `hso-github-webhook` | Verify GitHub/HSO emitter HMAC and record idempotent event |
| Reconciler | `hso-reconcile` | Poll GitHub and Notion; upsert normalized read models |
| Dashboard | `apps/mission-control` | Authenticated source health, latest runs, work items and evidence |

Endpoint URLs:
- https://ehgmtkkppmceaffhwcpc.supabase.co/functions/v1/hso-notion-webhook
- https://ehgmtkkppmceaffhwcpc.supabase.co/functions/v1/hso-github-webhook
- https://ehgmtkkppmceaffhwcpc.supabase.co/functions/v1/hso-reconcile

The webhook functions run with platform JWT verification disabled because GitHub Actions OIDC and provider webhook signatures are not Supabase Auth user JWTs. Each handler must authenticate at application level and fail closed. The Mission Control GitHub path is being migrated to short-lived GitHub Actions OIDC with exact repository, main-branch, workflow_ref, event_name and endpoint-audience checks. The Notion path continues to verify Notion's HMAC signature.

## Data model

| Table | Purpose |
|---|---|
| `hso_sources` | Source registry, authority role, health, freshness |
| `hso_sync_runs` | Run-level outcome, counts, errors |
| `hso_integration_events` | Deduplicated webhook inbox |
| `hso_source_snapshots` | Point-in-time source observations with SHA-256 digest |
| `hso_work_items` | Notion roadmap projection |
| `hso_executions` | Notion execution ledger projection |
| `hso_evidence_records` | Notion and GitHub PR/CI evidence |
| `hso_decisions` | Derived recommendations, not approval records |
| `hso_prompt_artifacts` | Snapshot-bound prompts |
| `hso_notifications` | Operational alerts |
| `hso_members` | Authenticated allowlist and role |

All HSO data tables enable and force RLS. Browser clients use only the Supabase publishable key. Service-role credentials remain server-side. Active membership in `hso_members` is required for dashboard reads.

## Synchronization contract

1. A GitHub event or Notion webhook arrives.
2. GitHub Actions requests a short-lived OIDC JWT for the exact webhook endpoint audience; the Edge Function verifies the JWT signature against GitHub JWKS and checks issuer, audience, expiry, repository ID/name, main ref, workflow_ref and event_name. Direct provider webhooks use their provider HMAC. Notion continues to use its HMAC signature over the exact raw request body.
3. The event is stored with unique `(provider, delivery_id)`; duplicate delivery IDs do not create duplicate inbox or change-event rows.
4. Reconciliation fetches the latest canonical source state rather than trusting event order or user-authored event text.
5. Records are upserted by `(source_key, external_id)`.
6. A source snapshot and sync run capture observed time, hash, counts and source outcomes.
7. Dashboard reads projections under RLS.
8. Scheduled reconciliation repairs missed events.

Webhook payload text is untrusted data. It must never be interpreted as executable instructions.

## Authority and safety gates

- CI evidence applies only to the exact recorded commit SHA.
- PR status does not itself equal milestone acceptance.
- A branch is not main; merge is not production deployment.
- Missing/stale evidence is UNKNOWN/STALE, never inferred PASS.
- Source conflict or stale source blocks derived recommendations.
- No automatic approval, policy change, PR merge, release, deployment, deletion or source-document overwrite.

## Required configuration

### Supabase Edge Function secrets

Set from Supabase Dashboard > Edge Functions > Secrets. Never commit values.

- `HSO_SYNC_TOKEN`: high-entropy shared secret for dashboard/manual refresh and GitHub event emitter.
- `NOTION_API_TOKEN`: internal Notion connection token with access only to the HSO pages and data sources.
- `NOTION_WEBHOOK_VERIFICATION_TOKEN`: verification token used to validate Notion webhook HMAC signatures.
- `GITHUB_WEBHOOK_SECRET`: optional separate secret for direct GitHub webhook delivery.
- `GITHUB_TOKEN`: optional least-privilege read token for GitHub API rate limits.

Supabase supplies `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` to the Edge Function runtime. Never expose the latter in Vercel client variables.

### GitHub Actions — Mission Control event path

The canonical workflow is .github/workflows/hso-mission-control-sync.yml. It uses id-token: write and requests a short-lived GitHub Actions OIDC JWT per request. The audience is endpoint-specific:

- https://ehgmtkkppmceaffhwcpc.supabase.co/functions/v1/hso-github-webhook for event ingestion.
- https://ehgmtkkppmceaffhwcpc.supabase.co/functions/v1/hso-reconcile for scheduled/manual reconciliation.

The Edge Functions trust only repository hsaidno-cpu/Hypersystem-Orchestrator, repository ID 1467501661, refs/heads/main, this exact workflow file on main, and their explicit event allowlists. The workflow checks out trusted main with persisted credentials disabled. Pull request observations use pull_request_target; no PR-head code is checked out or executed.

**Do not configure HSO_SYNC_TOKEN as a GitHub Actions repository secret. Do not configure a webhook URL secret.** Endpoint URLs are fixed non-secret integration constants in tools/emit_hso_oidc_event.py. The OIDC token is short-lived and never logged or persisted.

### Internal HSO service-to-service authentication

HSO_SYNC_TOKEN remains a server-side internal credential for function-to-function calls and compatible manual/server routes. Its canonical secret value is stored in Supabase Vault and retrieved at runtime through pre_federation_get_secret, whose execute grant is restricted to service_role and postgres. Do not copy the value into repository settings, logs, Notion or client-side configuration. During migration, Edge Functions may retain environment fallback for compatibility; Vault is the primary source. GITHUB_WEBHOOK_SECRET remains optional for a separately configured direct GitHub webhook. It is not used by the GitHub Actions OIDC workflow.

### Notion connection

Create an internal Notion connection with read access only to:
- HSO Master Control Center
- HSO Master Roadmap & Milestones
- HSO Workflow Execution Ledger
- HSO Evidence Registry

Register a connection webhook at the Notion endpoint above and store the connection's webhook verification token as `NOTION_WEBHOOK_VERIFICATION_TOKEN`. Webhooks are signals; the reconciler fetches the current canonical state.

### Vercel

Connect the repository using root directory `apps/mission-control`. Configure:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `HSO_SYNC_TOKEN` (server-only, no NEXT_PUBLIC prefix)

Use Preview first; production deploy waits for PR review and acceptance.

## Access onboarding

After the initial administrator signs in, add the user to the member allowlist with this controlled SQL, replacing the email:

```sql
insert into public.hso_members (user_id, role, active)
select id, 'admin', true from auth.users
where email = 'ADMIN_EMAIL@example.com'
on conflict (user_id) do update
set role = excluded.role, active = true;
```

Do not automatically grant admin to the first authenticated user.

## Current implementation status

Implemented:
- feature branch in the canonical HSO repository;
- Supabase schema and member-access migrations applied;
- source registry seeded;
- RLS and active-member read policies;
- three Supabase Edge Functions deployed;
- Next.js dashboard source code;
- GitHub Actions signed event emitter and scheduled sync workflow.

Pending:
- Supabase Edge Function secret provisioning;
- Notion internal connection and webhook subscription;
- GitHub Actions repository variable/secret;
- first admin allowlist membership;
- Vercel team grant and Git project linking;
- Vercel Preview build and acceptance tests.

Until configuration and acceptance complete, synchronization must be reported as NOT_CONFIGURED/BLOCKED, never live.
