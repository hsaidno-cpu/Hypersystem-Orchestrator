# HSO Canonical Identity & Nomenclature Contract

**Version:** 1.0.0  
**Status:** Approved naming baseline; Supabase display rename remains pending provider write access.  
**Machine-readable registry:** [config/hso-identity-registry.json](../config/hso-identity-registry.json)

## Purpose

Prevent collisions caused by confusing system names, app names, project slugs, provider IDs, Notion titles and source keys. A name is a label. An immutable provider ID or source key is identity.

## Canonical names

| Concept | Canonical value | Boundary |
|---|---|---|
| System / parent repository | `Hypersystem-Orchestrator` | Exact spelling and hyphenation for new labels |
| Acronym | `HSO` | Allowed in prose and technical identifiers |
| Dashboard app | `HSO Mission Control` | Dashboard only, not the whole ecosystem |
| Governance control plane | `HSO Master Control Center` | Notion governance/authorization source |
| Supabase table prefix | `hso_` | HSO-owned tables |
| GitHub repository | `hsaidno-cpu/Hypersystem-Orchestrator` | Canonical source-control repo |

`Hypersystem Orchestrator` without the hyphen is a historical prose/search alias only. `mission-control` is a Vercel project slug, not the product name. `HSMART` is a separate project/repository and must never be used as an HSO alias.

## Cross-platform identity map

| Platform | Role | Stable identity | Display name / status |
|---|---|---|---|
| GitHub | Source control, code, CI, PR, release evidence | Repository ID `1467501661`; `hsaidno-cpu/Hypersystem-Orchestrator` | Already canonical |
| Supabase | Operational data plane, Auth, Edge Functions, sync ledger | Project ref `ehgmtkkppmceaffhwcpc`; URL `https://ehgmtkkppmceaffhwcpc.supabase.co` | Desired: `Hypersystem-Orchestrator`; observed: `hsaidno-cpu's Project`; rename pending |
| Notion | Governance, roadmap, execution, evidence | Stable page IDs and data-source IDs in registry | Titles are descriptive metadata, never integration identity |
| Vercel | Dashboard hosting | Project ID `prj_CCBtxCpsVsY6st4TcmmtjoZiCbml` | Canonical dashboard project; slug `mission-control`; root `apps/mission-control` |
| Vercel secondary | Legacy/root deployment config | Project ID `prj_2lmpZ9CPJI0vjfNl7Ho3CMDVYWbB` | Non-canonical hold; previous `NEXT_NO_VERSION`; do not promote |

## Supabase rename boundary

Only the Supabase project **display name** should change to `Hypersystem-Orchestrator`.

Preserve without modification:
- Project ref: `ehgmtkkppmceaffhwcpc`
- API URL: `https://ehgmtkkppmceaffhwcpc.supabase.co`
- Database host: `db.ehgmtkkppmceaffhwcpc.supabase.co`
- API keys, Auth issuer, Edge Function URLs and database connection configuration

Supabase documents `PATCH /v1/projects/{ref}` with `name` in the request body. It requires Management API `projects:write` / `project_admin_write` permissions. This is provider metadata, not Postgres data, so SQL is not an acceptable rename mechanism. See [Update a project](https://supabase.com/docs/reference/api/v1-update-a-project) and [Management API authentication](https://supabase.com/docs/reference/api/introduction).

**Observed live state:** the display name is still `hsaidno-cpu's Project`. Rename state is therefore `PENDING_PROVIDER_MANAGEMENT_API_WRITE`. After authorization, update the name only, read the project back and verify ref, URL, host, region and service health remain unchanged.

## Identity precedence

Join and route using this order:
1. Immutable provider ID/ref and Notion page/data-source ID.
2. Canonical registry key or source key.
3. Provider display name and slug.
4. Historical aliases for search only.

Examples:
- Supabase: `project_ref`, not display name.
- Vercel: `project_id`, not slug.
- Notion: `page_id` / `data_source_id`, not title.
- GitHub: repository ID plus commit SHA, not repository title alone.
- Roadmap: `Work Item ID` plus source record ID, not task title.

## Canonical operational vocabulary

| Term | Exact meaning | Not interchangeable with |
|---|---|---|
| Work Item | Atomic Roadmap deliverable with Work Item ID | Program/Phase/Milestone roll-up |
| Execution Record | Execution attempt and receipt | Work Item completion |
| Evidence Record | Source-backed support for a claim | Status label |
| Source Snapshot | Source observation tied to one sync run | Last-known count |
| Sync Run | Bounded reconciliation with unique `sync_run_id` | GitHub workflow run or webhook delivery |
| Progress Snapshot | Measurement bound to source and scope snapshot | Displayed dashboard percentage |
| Decision Run | Evidence-bound evaluation of eligible next actions | Ungrounded AI suggestion |
| Verified | Acceptance supported by fresh evidence | Completed, merged, deployed or CI success alone |

Canonical machine values:
- Source: `not_configured`, `connected`, `degraded`
- Snapshot completeness: `UNKNOWN`, `COMPLETE`, `INCOMPLETE`
- Scope: `PENDING`, `IN_SCOPE`, `OUT_OF_SCOPE`
- Weight approval: `PENDING`, `APPROVED`, `REJECTED`
- Measurement: `UNMEASURED`, `PARTIAL_COVERAGE`, `SCOPE_UNCONFIRMED`, `SCOPE_CONFLICT`, `SOURCE_STALE`

UI labels may be friendlier, but persisted machine values must remain canonical.

## Source-of-truth boundaries

| Domain | Authority | Downstream |
|---|---|---|
| Code, branch, commit, PR, CI, release | GitHub | Supabase evidence and Mission Control |
| Scope, roadmap, approval, execution, evidence index | Notion | Supabase projections and Mission Control |
| Event inbox, sync ledger, snapshots, projections, measurements | Supabase | Mission Control |
| Application build and deployment | Vercel | Authorized users |
| Dashboard presentation | HSO Mission Control | Observes/recommends; does not overwrite source records |

There is no global bidirectional overwrite. Notion and GitHub remain authoritative for their own records; Supabase ingests and projects; Vercel hosts; Mission Control observes.

Mandatory source keys:
- `notion-control-center`
- `notion-roadmap`
- `notion-execution-ledger`
- `notion-evidence-registry`
- `github-hso-parent`

A title change does not change a source key.

## Rename/change procedure

1. Identify whether the change concerns a system name, app name, provider display name or provider slug.
2. Read the stable provider ID from the registry and live provider.
3. Change only the requested display field. Preserve refs, IDs, source keys, URLs and credentials unless a separate migration is approved.
4. Read back the provider record and compare immutable identity fields.
5. Update registry, Notion runbook and repository docs with observed name, desired name, state, timestamp and evidence.
6. Run identity validation and exact-head CI.
7. Run source reconciliation and verify that all required connectors still bind to the same IDs.

A slug change is a migration, not cosmetic cleanup. It may change generated URLs and callbacks; require dependency inventory, redirection, redeploy and endpoint acceptance.

## Automated enforcement

`tools/validate_hso_identity.py` checks canonical names, unique platform IDs, Supabase ref-to-URL consistency, Notion source identities, the canonical Vercel dashboard project, the secondary-project hold, HSMART separation and exact machine-state vocabularies. Mission Control CI runs this validator when identity files change.

## Current exceptions

| Item | Status |
|---|---|
| GitHub repository | Aligned |
| Supabase display name | Pending provider Management API write |
| Supabase ref, URL and host | Aligned; immutable |
| Notion page and data-source IDs | Canonical registry recorded |
| Vercel Mission Control project | Identified as the single canonical dashboard deployment |
| Secondary Vercel root project | Hold; not canonical |
| Live source integration | Separate acceptance still required |

Naming alignment is necessary but does not prove authentication, complete source snapshots, scope parity or runtime acceptance.
