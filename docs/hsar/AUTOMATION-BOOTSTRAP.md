# HSAR documentation automation bootstrap

## Current state

HSAR v0.1.0 and three Notion registries have been created. Session-scoped updates can be performed by an authorized HSAR workflow using the Notion and GitHub integrations. This document defines the production event-driven integration target; it does not claim that target is active.

## Event sources

The intended workflow should consume:
- GitHub `push` on approved default/release branches.
- GitHub `pull_request` events for opened, synchronized, closed/merged and reopened PRs.
- GitHub `workflow_run` completion events for approved CI workflows.
- Explicit manual reconciliation events.

Do not treat a branch push as acceptance or release. PR and CI observations remain separate from human decisions.

## Upsert model

Use stable keys and idempotent operations:
- Component records: `component_id`.
- Scan records: `scan_id`.
- Change records: `change_id`.
- Source snapshot identity: repository + ref/commit + path + blob SHA.
- Content hash: SHA-256 of normalized, redacted canonical payload.

Re-read canonical GitHub state on reconciliation; do not blindly trust webhook delivery order. Duplicate delivery must become a no-op.

## Required configuration

The GitHub Actions workflow requires an internal Notion integration with access only to the HSAR Component Registry, Scan & Coverage Ledger and Change & Evidence Ledger, plus repository secrets/variables for:
- `NOTION_API_TOKEN` (secret).
- `NOTION_HSAR_COMPONENT_DATA_SOURCE_ID`.
- `NOTION_HSAR_SCAN_DATA_SOURCE_ID`.
- `NOTION_HSAR_CHANGE_DATA_SOURCE_ID`.
- Optional sync feature flag and event-signature secret if an external webhook emitter is used.

No token or secret belongs in this repository, a commit, an issue, a PR comment, or Notion record.

## Required safeguards

- Redact tokens, credentials, personal data and restricted content before serialization.
- Enforce repository and path allowlists.
- Respect plugin source ownership, redistribution rights and private-source restrictions.
- Preserve unknown, stale, partial and blocked states.
- Do not auto-approve, merge, release, deploy, change permissions or delete records.
- Retry transient errors with bounded exponential backoff; preserve failed events in an auditable retry/dead-letter queue.
- Run scheduled/manual reconciliation to detect missed or reordered events.
- Record exact source SHAs and sync receipts.

## Acceptance sequence

1. Configure and share the three Notion data sources with the integration.
2. Add secrets and data-source IDs to repository Actions settings.
3. Validate schema, token scope and redaction on a test repository/record.
4. Test create, update, unchanged/no-op, duplicate event, stale source, rate-limit, timeout, invalid-auth and permission-denied cases.
5. Read back the three data sources and compare stable IDs/content hashes.
6. Confirm logs contain no secrets and failed deliveries remain recoverable.
7. Require human approval for production activation and record the accepted workflow revision.

Until all acceptance cases pass, set Notion/GitHub sync state to NOT_CONFIGURED, PARTIAL or BLOCKED as appropriate.

## GOV-01 disposition and controlled pilot (26 Nov 2026)

G0 was completed: HSO PR #30 merged as `42aa2da826ad17f2b9d6a648c118f14c7a0390a0`; HSMART PR #38 merged as `2071bbaa23c3a258189abde074d6436457f84295`. GOV-01 acceptance is recorded in both PR conversations. HSO's Vercel provider rate-limit failures, skipped remote-MCP invocation and skipped scheduled reconciliation remain explicit caveats. HSMART's assurance remains correlation-limited, not independent certification.

The next implementation is deliberately a narrow HSO-only pilot: **HSO → HSAR Change & Evidence Ledger**. Component Registry and Scan & Coverage Ledger are not writable by this pilot; HSMART is excluded until the HSO pilot passes its acceptance suite.

A dedicated machine-owned `Automation Sync Receipt` property stores GitHub observations. Human-managed properties (title after creation, Change Summary, Acceptance Evidence, positive/negative findings, Residual Risks, Conversion Actions, Decision State and any approval/risk-acceptance record) must never be overwritten.

The workflow is disabled by default and also checks `HSAR_NOTION_SYNC_ENABLED` inside the synchronizer. The pilot uses read-only GitHub Actions permissions and only reads canonical repository state. It does not auto-approve, merge, release, deploy or modify permissions.

**Live activation remains NOT_CONFIGURED** until a Notion internal integration is shared only with the Change & Evidence Ledger, its token is stored as GitHub Actions secret `NOTION_API_TOKEN`, the Actions variable `NOTION_HSAR_CHANGE_DATA_SOURCE_ID` is set to `42399868-397f-81a9-a077-000bb6feab76`, and dry-run plus live create/update/no-op/read-back tests pass. Never paste the Notion token into chat or source control.
