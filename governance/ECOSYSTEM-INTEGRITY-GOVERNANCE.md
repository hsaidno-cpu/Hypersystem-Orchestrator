# Ecosystem Configuration & Integrity Governance (ECIG)

**Policy ID:** HSO-ECIG  
**Version:** 1.0.0  
**Status:** PROPOSED NORMATIVE CONTRACT / IMPLEMENTATION NOT YET LIVE  
**Scope:** Canonical source, published and installed packages, effective runtime instructions, and ecosystem documentation across the Hypersystem-Orchestrator (HSO) portfolio.

## 1. Purpose

ECIG prevents four independently changing representations of a plugin from silently diverging:

1. **Source plane** — canonical repository, manifest, immutable commit, source files and tests.
2. **Package plane** — published package/release metadata and the package actually installed in a named platform target.
3. **Instruction plane** — master instructions, subskills, references and the effective content loaded by the runtime.
4. **Documentation plane** — GitHub-generated registries and human-governed Notion architecture, decisions, status and evidence.

The system is not a bidirectional file copier. It is a field-authority-aware observe → normalize → compare → classify → authorize → reconcile → read-back-verify control loop.

### Non-negotiable invariant

A record may be `SYNCED` only when every required plane for its declared target scope has fresh, independently verifiable evidence and all required rights and approval gates are clear. Missing evidence is `UNKNOWN`, not `PASS`. A package release is not proof of installation; matching version labels are not proof of content parity; a documentation link is not proof that documentation is current.

## 2. System-of-record and field authority

The system has no single global writer. Authority is assigned per field:

| Data / claim | Authoritative owner | ECIG behavior |
|---|---|---|
| Plugin implementation, manifest, tests, source release history | Canonical child Git repository | Read and pin immutable commit; propose source changes only through that repository's PR process |
| Ecosystem identity, plugin key, source locator, submodule pin, cross-plugin contracts | HSO parent repository | Validate and index; do not overwrite child-owned implementation |
| Package ID, release ID, package version, package artifact digest and publication state | Actual package registry / Plugin Creator read-back | Observe the real external object; stale catalog values are not live evidence |
| Installed/enabled state and loaded runtime identity | Named target platform / host adapter | Require target-scoped API read-back or signed runtime receipt; never infer from publication |
| Effective instruction content | Canonical source bundle plus actual package/runtime read-back | Compare file-set digests; report `NOT_COMPARED` when the host cannot expose content |
| Generated technical registries and policy contracts | GitHub canonical files and deterministic generators | Regenerate in CI; fail on drift |
| Human decisions, rationale, roadmap governance and workspace knowledge | Approved Notion decision records / control center | Preserve as human-owned content; synchronize only explicitly managed fields |
| Evidence observation and CI receipts | Original GitHub/runtime source, indexed in Notion Evidence Registry | Upsert traceable evidence; never convert evidence presence into approval |

**Conflict rule:** never use last-write-wins. Resolve a conflict using the authority for the affected field. If authority is absent or two authoritative observations conflict, set `BLOCKED` or `UNKNOWN`, preserve both observations and require an owner decision.

## 3. Stable identity and record grain

The canonical identity of an integrity record is:

`plugin_key × platform × target_scope`

- `plugin_key` is immutable, machine-readable and sourced from the parent catalog.
- `platform` identifies the concrete host family (for example ChatGPT, Codex, Claude, Gemini, MCP Host or HTTP Gateway).
- `target_scope` is a non-secret, human-readable alias for the installation boundary (for example `workspace-prod`, `codex-user-profile` or `staging-host-a`). Do not put personal identifiers, tokens or secrets in it.
- One plugin can have multiple integrity records because it can be installed at different versions in different workspaces or hosts.
- A legacy redirect is not a second implementation. Resolve it to its canonical `plugin_key` and preserve the redirect relationship.

The Notion **HSO Ecosystem Integrity Registry** is the materialized current-state view. The existing **HSO Evidence Registry** remains the evidence index / history. Do not collapse these two data roles.

## 4. Required evidence for the four planes

### 4.1 Source plane

Required attributes:

- canonical repository URL and repository owner;
- source ref for context and immutable commit SHA for identity;
- manifest path, manifest blob SHA and declared source version;
- deterministic source-tree digest;
- source ownership, visibility, license/redistribution disposition and observation timestamp.

A branch name is not an immutable source identity. Record the commit SHA. A Git submodule pointer must match the actual mode-160000 gitlink SHA in the parent tree.

### 4.2 Package and installation plane

Keep publication and installation as separate states.

**Package publication evidence:**
- package ID and current release ID;
- package version and artifact digest;
- registry observation timestamp and read-back locator;
- package visibility/entitlement and rights disposition.

**Target installation evidence:**
- platform and target-scope alias;
- installed package/release ID and installed version;
- installed artifact digest when the host exposes it;
- enabled state and effective runtime/plugin identifier;
- target health / activation probe, observation timestamp and verifier identity.

The following are different facts and MUST NOT be conflated:

`REGISTERED ≠ PUBLISHED ≠ INSTALLED ≠ ENABLED ≠ RUNTIME_ACTIVE`

If the target does not expose a trustworthy installed-artifact digest, report that limitation and use the strongest available signed/API read-back. Do not label an unobservable package `MATCH`.

### 4.3 Instruction plane

Build a deterministic manifest for the exact set of instruction files that affect the plugin:

- master instruction / entry skill;
- every declared subskill;
- referenced instruction fragments and policy files;
- required runtime metadata that changes instruction behavior.

For every file, record its normalized relative path, byte length and SHA-256. Sort entries by normalized path and hash a canonical UTF-8 JSON representation of the complete file manifest to obtain the bundle digest. Record individual file digests as well as the aggregate digest so drift can be localized.

Normalization rules:
- paths are relative POSIX paths, UTF-8 NFC normalized, case-preserving and sorted ordinally;
- reject absolute paths, parent traversal, path collisions after normalization and symlinks that escape the package root;
- normalize text line endings from CRLF/CR to LF; do not trim whitespace, rewrite wording, reorder sections or normalize semantic content;
- hash binary assets as raw bytes;
- include the declared file set and file mode where executable behavior depends on it;
- record the algorithm and manifest version with every digest.

Compare the canonical source bundle with the published artifact and, where possible, the target's effective loaded instruction set. If the platform cannot provide an export or trustworthy receipt, set parity to `NOT_COMPARED` or `UNKNOWN`; never infer a match from a release ID or version string.

### 4.4 Documentation plane

Treat documentation as a governed projection, not a verbatim copy of source code.

- GitHub owns generated, versioned technical registries, JSON schemas, policy files, and technical documentation that is built from those inputs.
- Notion owns human decisions, rationale, roadmap governance, operational interpretation and workspace navigation.
- The Notion integrity record is a materialized read model with exact GitHub references, digests, status, limitations and evidence links.
- Each automated Notion page/row must identify the policy version and source commit or observation from which it was derived.
- Compute the documentation digest only over the explicitly sync-managed projection fields. Do not hash or overwrite unrelated narrative blocks, comments, approvals, relations or user-authored decisions.
- Generated GitHub documentation must be reproducible from canonical repository inputs and CI must detect stale generated output.

## 5. Reconciliation algorithm

For every event or scheduled sweep:

1. **Authenticate and scope.** Verify the event origin, repository, actor, target scope, integration permissions and allowed operation.
2. **Resolve identity.** Match the immutable `plugin_key`; reject ambiguous names, duplicate canonical sources and unresolved redirects.
3. **Collect observations.** Read source commit/manifest, package release metadata, target installation/runtime receipt, instruction manifest and documentation projection.
4. **Validate provenance.** Check source owner, repository visibility, commit existence, release identity, rights metadata, receipt issuer, signature (where required) and timestamp.
5. **Normalize and hash.** Generate the source, package, installed and instruction digests with the versioned canonicalization algorithm.
6. **Compare each plane independently.** Version equality is a metadata check; content equality is a digest/file comparison; installation is a target-scoped read-back.
7. **Classify drift.** Produce per-plane states, an overall state, exact mismatches, missing evidence, freshness and required approvals.
8. **Build an action plan.** Choose only an action permitted by the field-authority matrix. Source or instruction changes become GitHub PR proposals; package changes require release authority; installation changes require target-specific authorization.
9. **Apply safely.** Use idempotency keys, bounded retries, per-record concurrency locks, least-privilege credentials and a dead-letter path. Never blindly replay a non-idempotent create or external side effect.
10. **Read back from the target.** Query GitHub, package registry, runtime adapter and Notion after every write. Compare returned identifiers and digests with the requested values.
11. **Commit an audit receipt.** Record the observed facts, before/after values, action, principal, approval, exact commit/release/target, verification method, timestamps and residual limitations.
12. **Recompute state.** Set `SYNCED` only after all required dimensions pass. Any ambiguous write, missing read-back or unresolved conflict remains non-green.

## 6. State model

Each plane uses one of: `MATCH`, `DRIFT`, `STALE`, `UNKNOWN`, `BLOCKED`, `NOT_APPLICABLE`, `NOT_COMPARED` (where supported).

Overall state is derived, never manually typed:

| Overall state | Rule |
|---|---|
| `SYNCED` | Every required plane is MATCH/current; rights are CLEARED; installation/runtime requirements for the target are verified; no approval is pending |
| `DRIFT` | A verified comparison found a content/version/identity mismatch |
| `STALE` | Previously valid evidence exceeded its freshness window |
| `UNKNOWN` | Required evidence is absent, inaccessible or inconclusive |
| `BLOCKED` | Rights, permissions, identity, source, security or a required external dependency prevents safe reconciliation |
| `APPROVAL_REQUIRED` | A proposed action is technically ready but requires a human authority decision |
| `RECONCILING` | A scoped, authorized operation is in progress and no completion claim is made |

`NOT_APPLICABLE` is valid only when the target policy explicitly says the dimension does not apply. It must not be used to hide missing capability or unavailable evidence.

## 7. Event and schedule model

| Trigger | Observation | Permitted automatic response |
|---|---|---|
| Child repository push / release | Source head, manifest, tests and release | Recompute source state; open/update a parent PR when a parent pin or contract needs changing |
| Parent PR / merge / CI completion | Exact PR head, review, checks and generated docs | Upsert evidence; validate generated registry; do not infer human approval from CI |
| Package release/update | Package ID, release ID, version, artifact digest, visibility | Update observed package metadata after external read-back; do not publish |
| Platform install/enable/upgrade | Target receipt and loaded version/digest | Update only that target-scope installation record |
| Instruction bundle change | Per-file and aggregate digest | Recompute parity; block promotion where required; never overwrite package/source automatically |
| Notion managed-field change | Field diff and linked source locator | Reconcile managed fields from their authoritative source; preserve human-owned fields |
| Scheduled reconciliation | Re-read all due observations | Mark expired observations STALE; open drift work items; do not delete history |

Use webhooks where reliable. Use bounded polling for systems without webhooks. Run a full reconciliation at least daily during rollout; tune intervals to the risk and rate limits of each source. Event delivery is at-least-once, so all handlers must be idempotent and tolerate replay and out-of-order delivery.

## 8. Write authority and automation boundary

### Safe to automate after security review

- source, PR, commit, release and CI evidence capture;
- deterministic digest generation and parity comparison;
- generated GitHub documentation and CI drift checks;
- idempotent upsert of explicitly managed Notion properties;
- freshness evaluation and STALE transitions;
- opening or updating a GitHub issue/PR that proposes reconciliation;
- read-back verification and audit receipt creation.

### Human approval required

- selecting or replacing a canonical repository;
- resolving ownership, license or redistribution rights;
- changing a release channel or promoting a release candidate;
- publishing or republishing a package;
- installing, upgrading, enabling, disabling or uninstalling on a target;
- overwriting instructions when source and installed content differ;
- changing production permissions, secrets, scopes or trust policy;
- accepting a milestone, closing a security disposition or declaring production readiness.

### Never automatic

- copy arbitrary Notion prose into canonical source;
- change source or package content to make a checksum pass;
- publish/install a package because a newer Git commit exists;
- treat a successful CI job as human approval or runtime proof;
- delete evidence/history to clear a drift state;
- widen credentials after an authorization failure;
- mark unknown, stale, unobserved or not-compared data as PASS.

Notion-originated technical changes are proposals. A source change must be materialized as a reviewed GitHub PR in the canonical repository. A GitHub merge may update managed Notion projections, but must not rewrite human decision records or approval fields.

## 9. Security and reliability controls

- Use short-lived OIDC-issued credentials where supported; otherwise use dedicated, narrowly scoped tokens in a secret manager / GitHub Actions secrets.
- Never store credentials, private keys, cookies, personal identifiers or sensitive installation details in Git, Notion, logs or artifacts.
- Use read-only GitHub permissions for event collection. Separate evidence writers from source/release/install writers.
- For `pull_request_target`, check out trusted base code only, disable persisted checkout credentials, reject forks unless explicitly reviewed, and never execute PR-head code with privileged secrets.
- Bind Notion writes to the dedicated ECIG data source and explicitly managed property allowlist.
- Use idempotency key `SHA256(policy_version | plugin_key | platform | target_scope | event_locator | desired_digest)`.
- Enforce one active reconciliation lease per record key; do not use a concurrency group that can silently replace an unrelated pending delivery.
- Retry only safe operations with bounded exponential backoff and jitter. For ambiguous non-idempotent creates, query by record key before any retry.
- Preserve before/after snapshots and append-only audit receipts. Use signed receipts and external immutable/WORM storage before claiming tamper-evident audit assurance.
- Apply retention and redaction to target receipts; keep secrets out of the evidence payload.
- Fail closed on duplicate record keys, conflicting authoritative observations, incomplete webhook payloads, missing rights evidence or failed target read-back.

## 10. Notion data model

Use two distinct databases:

1. **HSO Ecosystem Integrity Registry** — one current-state row per `plugin_key × platform × target_scope`. It records plane versions, digests, state, reconciliation time, evidence locator, conflict summary and next action.
2. **HSO Evidence Registry** — event/evidence records such as PRs, commits, workflow runs, artifacts and runtime receipts. It remains the evidence index and history.

The sync worker may update only its allowlisted integrity/evidence properties. Do not let a GitHub evidence event silently mutate Work Item progress, PRE stage/gate, decisions, approvals, ownership or milestone acceptance.

Required configuration is supplied through environment variables / GitHub repository variables, including `HSO_NOTION_API_KEY`, `HSO_ECIG_DATA_SOURCE_ID` and an explicit enable switch. The data source identifier is deployment configuration, not a credential; do not hardcode private workspace identifiers in public source files.

## 11. CI and acceptance requirements

### Static repository checks

- plugin keys are unique and stable;
- every canonical source has an owner, repository, visibility, manifest path, commit pin and rights disposition;
- each parent gitlink equals the declared immutable pin;
- generated registries equal their canonical JSON inputs;
- instruction manifest paths are complete, unique and confined to the package root;
- source/instruction digests are deterministic and change when a relevant byte, file path or file-set membership changes;
- contract/schema versions and required fields are valid;
- no secret or sensitive target data is committed.

### Cross-system integration checks

1. Source push updates only the expected source observation.
2. A package release update is observed independently of source version.
3. A package release is never reported as installed without target read-back.
4. One changed instruction file identifies the exact drifted path.
5. Matching version strings with changed content return DRIFT.
6. Identical content with different display labels can return content MATCH while retaining a version warning.
7. A documentation projection changes when a managed field changes and remains unchanged for unrelated Notion prose.
8. Duplicate record keys fail closed.
9. Replayed and out-of-order events converge to the same state.
10. Notion 429/5xx and transport faults retry safely; permanent 4xx errors stop.
11. An ambiguous create is reconciled by record key and never blindly duplicated.
12. Failed read-back leaves state RECONCILING/UNKNOWN/FAILED, never SYNCED.
13. A missing platform adapter produces NOT_OBSERVED/UNKNOWN, never INSTALLED.
14. An uncleared license or missing human approval blocks release/install.
15. Evidence synchronization cannot mutate roadmap progress, PRE gates, decisions or approvals.
16. Every external write records actor, scope, approval, exact source/target, outcome and rollback reference.

GOV-01 is the sole human decision authority. No second human engineering reviewer, security reviewer or CODEOWNER approver is introduced; technical assurance and cryptographic evidence support the owner's decision but do not impersonate a human review.

A green static CI run proves only the checks executed in that workflow. Live package registry, Notion API and named-host runtime acceptance must be separate, exact-target tests.

## 12. Freshness policy

Initial recommended upper bounds (tune after observing API limits and risk):

| Observation | Maximum age |
|---|---:|
| Source ref / commit observation | 24 hours |
| Package release metadata read-back | 30 days |
| Installed package / runtime receipt | 24 hours |
| Instruction parity comparison | 24 hours |
| Notion managed documentation projection | 7 days |
| Rights / license decision | Until source, license or terms change; otherwise revalidate |

These are policy thresholds, not evidence that an external connector or runtime probe currently exists. A newer commit, release or package event invalidates dependent observations immediately, even when their time window has not expired.

## 13. Rollout and release gates

**Stage 0 — Baseline and identity.** Confirm each canonical plugin key, source repository, source owner, package identity, target scopes, rights and actual instruction file set. Unknowns stay explicit.

**Stage 1 — Static integrity.** Validate catalog, gitlinks, manifests, deterministic digests, generated documentation and attestation schemas in CI. No external writes.

**Stage 2 — Evidence-only Notion sync.** Reuse the bounded GitHub-to-Notion Evidence Registry vertical slice. Complete its dependency/review gates, provision a scoped integration, execute live create/update/no-op/duplicate/retry/stale/read-back tests, then enable event flow.

**Stage 3 — Package and instruction comparison.** Add a real package-registry read-back and package extraction/comparison adapter. Compare the exact published artifact with the canonical Git instruction bundle. No republishing.

**Stage 4 — Target installation attestation.** Implement named-host adapters for install/enabled/runtime-loaded state. Prove the exact host, account/workspace scope and version. No generic claim across untested hosts.

**Stage 5 — Documentation projection and policy enforcement.** Upsert the ECIG current-state rows, generate technical registries, add conflict dashboards and enforce release gates. Keep human decisions human-owned.

**Stage 6 — Controlled promotion.** Only after source, rights, package, instruction, runtime, security, rollback and human approval gates pass may a target-specific install/upgrade be executed.

### Current integration boundary

The existing PR #16 is a bounded GitHub-to-Notion evidence synchronizer, not a four-plane reconciler, and its live workflow remains gated on Notion integration sharing, secret/variable provisioning, GOV-01 exact-head disposition and live API acceptance. No second human reviewer or security approver is required. PR #18 adds version/gitlink/generated-registry controls but explicitly does not resolve instruction-content drift or distribution rights. ECIG does not promote either PR from OPEN to merged or from test-pass to live acceptance.

## 14. Exit criteria for claiming four-plane synchronization

An ecosystem release may be called four-plane synchronized only when:

- every in-scope plugin has one unambiguous canonical identity and source commit;
- package publication and target installation are independently read back;
- package artifact and effective instruction digests match the approved source lock;
- required documentation projections identify that exact source/package/instruction tuple;
- rights and security disposition are clear;
- all freshness windows are valid;
- all automated writes are read back and match;
- required human approvals exist and are linked;
- the audit receipt and rollback reference are retrievable;
- no unresolved blocker, drift, stale observation or unknown required plane remains.

Otherwise publish the exact per-plane state and blocker. Never flatten an incomplete ecosystem into a green badge.

## 15. ECIG signature verification and trust-root provisioning

A `SYNCED` attestation is accepted only when its Ed25519 signature verifies against an active public key in `governance/ecig-trusted-public-keys.json`. The signature covers the complete attestation payload except the root-level `signature` field. The canonical byte representation is UTF-8 JSON with lexicographically sorted object keys, compact separators, Unicode characters emitted without ASCII escaping, and non-finite numbers rejected (`HSO-ECIG-JSON-1`).

The verifier checks the trusted `key_id`, canonical base64 encoding, 32-byte public key, 64-byte signature and cryptographic verification. A syntactically valid signature length is not proof of authenticity. Signature verification is separate from human approval records; neither substitutes for the other.

The checked-in trust registry intentionally begins with zero active keys. Until a public key is added through a reviewed change with an exact-head GitHub PR comment `APPROVE TRUST ROOT <head-sha>` by GOV-01, validated by a trusted-base `pull_request_target` workflow, and documented key custody/rotation/revocation ownership, every `SYNCED` attestation fails closed. Test fixtures may inject ephemeral keys in memory; test keys must never be added to the production trust registry.

A `SYNCED` record must declare `performed_actions`. If an instruction overwrite or cross-plane content replacement occurred, `instruction_overwrite_or_cross_plane_content_replacement` must be present and matched by a GOV-01 approval record. A `SYNCED` record must also carry plane-specific evidence: source commit and manifest, package read-back, installation receipt and runtime probe, instruction comparison, and documentation read-back. The latest observation for each required evidence kind must be no older than the corresponding policy freshness window, and no unresolved or rejected approval may remain. Approval records must be action-specific for canonical source selection, rights disposition, publication and installation where those actions occurred.

The ECIG policy validator enforces the exact read-only GitHub permission allowlist (`contents:read`, `pull-requests:read`, `actions:read`), pull-request-only source changes and the trusted-base-only privileged workflow rule. These checks validate the declared policy; they do not themselves prove GitHub repository rulesets or live runtime permissions.
