# HSO Ecosystem Development — Board Operating Contract

**Version:** 1.0.0  
**Baseline date:** 28 November 2026  
**Canonical board:** HSO Ecosystem Development  
**Seed manifest:** `examples/hso-ecosystem-development-board-seed.v1.json`

## 1. Purpose and system boundaries

This board is the shared operational surface for development progress across HSMART-HSO. It coordinates work; it does not replace the source-of-truth systems.

| Domain | Canonical authority | Board responsibility |
|---|---|---|
| Source code, Issue/PR, commits, CI, release | GitHub | Link and summarize current work |
| Roadmap R0–R9, gates and milestone acceptance | PRE | Show execution state without mutating PRE authority |
| Component anatomy and architecture knowledge | HSAR | Track inventory, evidence and sync work |
| Structured ecosystem entities/relationships | Universal Ecosystem Atlas | Track completeness/freshness validation |
| Work coordination and card state | HSO Workboard | Board, column, assignment, labels and task visibility |
| Decisions and documentation projections | Approved governance/Notion records | Link decisions and read-back evidence |

A status change on this board is not proof that the underlying implementation or deployment changed.

## 2. Workflow columns

The order is normative:

1. **Intake** — incoming work with a canonical source reference; not yet prioritized.
2. **Backlog** — accepted work waiting for a deliberate execution slot.
3. **Ready** — scope, owner, dependencies and acceptance criteria are explicit.
4. **In Progress** — active implementation or investigation.
5. **Blocked** — a named blocker prevents progress; the card must record its cause and next unblock action.
6. **Review & Verification** — code exists and is waiting for independent review, CI, integration, runtime or read-back evidence.
7. **Done** — all acceptance criteria pass and the independent completion-evidence gate passes.
8. **Archive** — visible workflow parking for cancelled, superseded or intentionally retained work.

The visible `Archive` column is different from database soft-archive (`is_archived`) and the `kanban.card.archive` tool. Do not hide a card merely to move it to the visible Archive state.

## 3. Card contract

Every card must contain:

- A canonical GitHub Issue or PR URL as its stable `source_work_item_id`.
- Exact source revision: commit SHA for a PR/commit source or observed `updated_at` for an Issue.
- Outcome-focused title and bounded description.
- Explicit acceptance criteria that can be checked.
- Priority and one workflow semantic key.
- Evidence references (canonical GitHub, CI, deployment, Notion or source-document links).
- Dependency identifiers using canonical source URLs.
- Structured extra metadata: workstream, observed state, observation date, reason for initial column, authority boundary and next action.

Never fabricate a GitHub Issue/PR or source revision. A card sourced from documentation but lacking a ticket must first receive a tracking Issue; the seed uses Issues #62–#64 for HSAR, Atlas and the Done gate.

## 4. Initial board population

The source-backed seed contains twelve initial cards:

| Workstream | Canonical reference | Initial column | Why |
|---|---|---|---|
| HSO native Kanban backend/MCP | PR #59 | In Progress | Source implementation and CI exist; database migration, deployment and runtime acceptance are not complete |
| PRE–RPEDS federation | Issue #55 | Blocked | No accepted release/adoption receipts; publisher and host configuration remain blockers |
| Super-Orchestrator remote invocation | PR #20 | Blocked | Protected credentials, reviewer controls, public MCP endpoint, live invocation and WORM receipt are not provisioned |
| HSAR / GitHub-to-Notion pilot | Issue #62 | Blocked | Notion integration scope, protected token and live create/update/read-back receipt are pending |
| Universal Ecosystem Atlas | Issue #63 | Intake | Schema migrations exist; source completeness, pagination exhaustion and graph integrity still need acceptance |
| Plugin/Skill migration closure | Issue #44 | Blocked | Source/runtime parity and unresolved source mapping remain; the 869-vs-864 path denominator requires reconciliation |
| Distribution and adapter rights | PR #12 | Blocked | Recorded rights/source baseline has zero installable packages; independent rights and host evidence are required |
| Mission Control OIDC/Vault sync | PR #58 | In Progress | Code repair is proposed; deploy/read-back and live event/reconciliation evidence remain |
| Webhook signature/replay hardening | PR #29 | Blocked | Draft/non-mergeable security work; protected secret provisioning and live replay acceptance are absent |
| Source ledger and 289-skill crosswalk | PR #47 | Blocked | +5 path denominator discrepancy and content parity/source identity work remain |
| HSMART–HSO UEDE contract | PR #25 | Review & Verification | Architecture contract exists; GOV-01 disposition is required |
| Independent Done evidence gate | Issue #64 | Blocked | UI/MCP guards exist in source, but database-level enforcement is not implemented |

These are **initial observed columns**, not verified live task status. Re-read GitHub before every import/reconciliation. The manifest explicitly records the observation date and status rationale.

## 5. Done policy — hard gate, currently not production-ready

At the current source revision, the UI and MCP tool paths reject direct transitions/creation into semantic `done`, and source-sync previews targeting `done` are marked as conflicts. This is an interim fail-closed guard only.

The PostgreSQL database-level gate remains **NOT IMPLEMENTED**. A direct Data API write may bypass UI/MCP checks. Therefore:

- Do not deploy the current branch as a production completion authority.
- Do not manually set `is_archived`, metadata or a card column to imply completion.
- Do not move any initial seed card into Done.
- Do not claim Done acceptance until Issue #64's migration, RLS policies, trigger/function checks, actor/verifier separation and negative test suite are implemented and independently verified.

The final gate must bind a PASS evidence record to the exact card revision and source revision. It must carry a canonical HTTPS evidence locator, source commit/release/workflow identity, SHA-256 digest, observed result, verifier identity and timestamp. The verifier must be independent of the AI/card actor. Missing, stale, mismatched or non-PASS evidence must reject every route into Done, including MCP, UI, sync RPC and direct Data API writes.

PRE milestone acceptance remains a separate authority and is never implied by Kanban Done.

## 6. Synchronization policy

Initial imports use the native source-to-board contract:

1. Re-read canonical GitHub Issues/PRs and their current revisions.
2. Construct a normalized source payload matching `syncItemSchema`.
3. Call `kanban.sync.preview`; preview must not mutate cards.
4. Inspect CREATE/UPDATE/NOOP/CONFLICT counts and all conflict details.
5. Apply only the exact stored preview digest with explicit `confirm_apply=true`.
6. Run `kanban.sync.read_back` and record the verified count and issues.

The source digest must include `extra` metadata as well as title, description, acceptance criteria, priority, target column, evidence refs and dependencies. Board edits since the last source sync must become conflicts; they must not be overwritten silently.

Board-to-source sync remains a separate, controlled outbox adapter task. An outbox acknowledgement is not an independent cryptographic verification of the external source receipt.

## 7. WIP and review discipline

- Keep the number of In Progress cards deliberately small; prioritize unblocking rather than starting more work.
- A Blocked card must state one concrete blocker, its owner/system, and the exact next action.
- Review & Verification requires evidence from an actor or system independent of the implementer where the risk level warrants it.
- Static CI, source files, draft PRs and migration history are not runtime deployment evidence.
- Archive only after the source is cancelled/superseded or explicitly retained for traceability.

## 8. Deployment boundary

The seed file is a proposal and does not contain workspace or board UUIDs. It is not a live board export. Import it only after:

- PR #59 passes exact-head review and is approved/merged under repository governance.
- Migrations are generated through the Supabase CLI, tested on a disposable/development project and independently read back.
- OAuth/PKCE, consent, redirect allowlist, RLS roles and MCP Inspector tests pass.
- The frontend is separately deployed and its environment variables use only the publishable key.
- Issue #64's database-level Done gate passes its positive and negative tests.

The current live HSO Supabase project was inspected on 28 November 2026: it has no `kanban_*` tables and no PRE Kanban migrations in migration history. No live workspace, board, MCP endpoint or card import is claimed.

## 9. Canonical tracking references

- [Native HSO Kanban backend/MCP PR #59](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/59)
- [HSAR pilot Issue #62](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/issues/62)
- [Atlas acceptance Issue #63](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/issues/63)
- [Done evidence gate Issue #64](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/issues/64)
- [PRE–RPEDS federation Issue #55](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/issues/55)
- [Plugin migration closure Issue #44](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/issues/44)
