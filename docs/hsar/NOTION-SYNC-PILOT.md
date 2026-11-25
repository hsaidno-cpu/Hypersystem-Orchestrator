# HSAR GitHub → Notion Sync Pilot

**Implementation state:** code scaffold and local contract tests prepared; production write gate disabled by default.  
**Pilot scope:** HSO repository only → HSAR Change & Evidence Ledger only.  
**Not in scope:** HSMART repository, Component Registry writes, Scan & Coverage Ledger writes, human decisions, approvals, merge, releases, deployments, or runtime execution.

## Security boundary

- GitHub remains the canonical source for PR metadata, source refs, changed-file manifest and workflow-run evidence.
- Notion is a projection for navigation and evidence, not a competing source of truth.
- The integration must be shared only with the HSAR Change & Evidence Ledger. Do not share it with the Component Registry or Scan & Coverage Ledger during this pilot.
- The synchronizer reads canonical PR details from GitHub after receiving an event. It never executes code from a PR branch and checks out only the trusted default branch.
- Fork-originated PRs are skipped. Only PRs whose base and head repository are both `hsaidno-cpu/Hypersystem-Orchestrator` are eligible.
- Human-managed fields are immutable to the synchronizer: `Change` title after creation, `Change Summary`, `Acceptance Evidence`, positive/negative findings, `Residual Risks`, `Conversion Actions`, `Decision State`, and approval/risk-acceptance fields are never overwritten.
- Machine observations are stored in the dedicated `Automation Sync Receipt` field, with exact refs, changed-file/blob manifest, and workflow evidence. Only machine-owned fields such as SHAs, branch, changed paths, CI URL, hash and sync statuses may be updated.
- No secrets, credentials, private source content or PR body text are copied into Notion. Common token/private-key patterns are redacted before text is serialized.
- Duplicate stable keys fail closed. The stable identity is the canonical GitHub PR URL. The normalized source projection is SHA-256 hashed; unchanged events become no-ops. Every create/update is read back from Notion and hash-verified before both sync statuses are marked `Synced`.
- Retry is bounded and applies only to transient HTTP/transport failures. A non-idempotent create request is not automatically retried after an ambiguous network/5xx outcome; later reconciliation checks the stable key before creating again.
- Workflow permissions are limited to `contents: read`, `pull-requests: read`, and `actions: read`. No `pull_request_target`, repository write token or deployment permission is used.
- A push to `main` resolves only the PRs associated with the pushed commit SHAs; it does not scan the full PR history. Full repository reconciliation is reserved for the daily schedule or manual dispatch.
- The workflow's write gate is disabled unless `HSAR_NOTION_SYNC_ENABLED` equals `true`.

## One-time account configuration

The connected GitHub/Notion tools do not expose repository-secret management. Configure the following directly in the GitHub and Notion UIs; do not paste the token into chat, a commit, a PR comment or a Notion row.

1. Create an internal Notion integration with read/write access only to **HSAR Change & Evidence Ledger**.
2. Share only the Change & Evidence Ledger database with that integration. Do not share the Component Registry or Scan & Coverage Ledger for this pilot.
3. In the HSO repository, open **Settings → Secrets and variables → Actions → Secrets** and add `NOTION_API_TOKEN` with the integration's secret token.
4. Under **Settings → Secrets and variables → Actions → Variables**, add `NOTION_HSAR_CHANGE_DATA_SOURCE_ID` with the data-source UUID `42399868-397f-81a9-a077-000bb6feab76`.
5. Add `HSAR_NOTION_SYNC_ENABLED` with value `false` initially.
6. Run **Actions → HSAR GitHub to Notion Sync Pilot → Run workflow** with `dry_run=true`. This reads GitHub and calculates hashes but does not read a Notion token or write to Notion.
7. Once the integration permission and secret are configured, manually set `HSAR_NOTION_SYNC_ENABLED=true` and dispatch with `dry_run=false` for the first live pilot. Inspect the GitHub step summary and the Notion row read-back before leaving the gate enabled.

## Acceptance cases

| Case | Expected behavior |
|---|---|
| New PR URL | Create one Change & Evidence Ledger row |
| Existing PR with changed metadata | Update the same row, never create a duplicate |
| Same event delivered again | No-op; no write |
| Duplicate PR URL already exists in Notion | Fail closed; no row changes |
| Changed source ref/file/workflow result | New content hash and same-row update |
| Read-back hash mismatch | Fail; do not claim `Synced` |
| Invalid token / insufficient access | Fail closed; no secret values in logs |
| Transient timeout / rate limit | Bounded retry; fail with sanitized receipt if exhausted |
| Fork-originated PR | Skip |
| Human `Decision State` field | Preserve unchanged; never write it |
| Dry-run | No Notion API request or write |
| Push to main | Resolve pushed commit SHAs to associated PRs only; deduplicate PR numbers |
| Scheduled/manual reconciliation | Re-read current GitHub PR state and reconcile by canonical URL |

Unit-level contract tests run with `python -m unittest discover -s tests -v`. Passing local tests are not a live integration receipt. The pilot remains `NOT_CONFIGURED` / `BLOCKED` until the real Notion credential and narrowly scoped database share exist and a live create/update/no-op/read-back test passes. The script also checks `HSAR_NOTION_SYNC_ENABLED`; workflow gating is not the only control.
