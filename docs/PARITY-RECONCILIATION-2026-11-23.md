# Source and Instruction Parity Reconciliation

**Checkpoint:** 23 November 2026  
**Parent baseline:** `hsaidno-cpu/Hypersystem-Orchestrator` main @ `e5242797a2481018a9758f7cf8689856015b3083`  
**Method:** compare every corresponding `SKILL.md` file available in the current Plugin Creator USER/PRIVATE package against the exact pinned Git source. Normalize CRLF to LF and compare trimmed UTF-8 text. Exactness is reported per file; it does not imply license clearance or runtime compatibility.

## 1. Results

| Plugin | Plugin Creator package | Pinned Git source | File-level result | Disposition |
|---|---:|---:|---|---|
| Anatomi Prompt V3 | 3.0.0 | 3.0.0 | **9/9 exact** (master + 8 specialists) | Instruction parity MATCH |
| SKILL ANALYZER | 1.0.0 | 1.3.0 | **11/12 exact**; `platform-compatibility` differs | Source ahead; parity DRIFT_DETECTED |
| A.S.F.R.E.E Canonical | 0.3.2 | 0.5.0-rc.1 | **5/13 exact**; 8 files differ (master + O03/O04/O05/O06/O09/O11/O12) | RC source ahead; parity DRIFT_DETECTED |
| Skill Developer Orchestrator | 0.1.0 | 0.1.0 | **0/4 exact** (master + 3 references) | Same version label, different content; DRIFT_DETECTED |
| Video Explainer Promkes | 4.1.12 | 4.1.9 | Not directly comparable at skill-file level: Plugin Creator archive inventory contains no `SKILL.md` files while Git source has 14 | Deployment ahead; parity NOT_COMPARED |
| Progressive Roadmap Evaluator (PRE) | 0.1.1 | Not identified | No canonical Git source | Package verified; parity NOT_COMPARED |

## 2. Detailed findings

### 2.1 Anatomi Prompt V3 — exact skill-file parity

All nine files match after line-ending normalization:
- `anatomi-prompt/SKILL.md`
- `p1-role-persona-architect/SKILL.md`
- `p2-objective-task-architect/SKILL.md`
- `p3-context-variable-architect/SKILL.md`
- `p4-reasoning-workflow-architect/SKILL.md`
- `p5-constraints-guardrails-architect/SKILL.md`
- `p6-edge-case-recovery-architect/SKILL.md`
- `p7-stop-completion-architect/SKILL.md`
- `p8-output-schema-architect/SKILL.md`

Package and source versions are both 3.0.0. This is the only fully matching source-backed skill set in this comparison. It remains private and has no root LICENSE in the inspected Git source; exact content parity does not clear redistribution rights.

### 2.2 SKILL ANALYZER — 11/12 exact, Git source ahead

Eleven skill bodies match exactly. The single difference is `skills/platform-compatibility/SKILL.md`: Plugin Creator v1.0.0 contains 71 lines, while Git source 1.3.0 contains 81 lines and appends a `HOSTED GATEWAY PROFILE` section for endpoint/TLS/OIDC/provider/quota/audit/negative-control verification.

The canonical Git source is version 1.3.0; the Plugin Creator package remains version 1.0.0. Do not mark the files MATCH or silently relabel the package. Recommended direction is a controlled platform-package reconciliation to the approved 1.3.0 source, followed by package read-back and regression. The Git repository has no root LICENSE, so redistribution remains blocked.

### 2.3 A.S.F.R.E.E — source 0.5.0-rc.1 ahead of platform 0.3.2

Only five of thirteen skill bodies match exactly: O01, O02, O07, O08 and O10. Eight differ: the master orchestrator and O03/O04/O05/O06/O09/O11/O12. The Git source bodies contain substantial expansions relative to the platform package.

The Git source version 0.5.0-rc.1 is a release candidate, not a stable release. Keep the RC label and PolyForm Noncommercial 1.0.0 obligations. A platform update must wait for explicit RC acceptance, compatibility regression and license/distribution review; do not downgrade or overwrite the Git source to match the older 0.3.2 package.

### 2.4 SDO — version match does not mean content parity

The package and Git source manifests both say 0.1.0, but none of the four instruction/reference files match exactly:

| File | Plugin Creator | Git source |
|---|---:|---:|
| Master `SKILL.md` | 23,651 chars | 10,573 chars |
| `audit-matrix.md` | 4,874 chars | 3,111 chars |
| `github-change-protocol.md` | 4,596 chars | 2,497 chars |
| `regression-and-release-gates.md` | 4,500 chars | 3,030 chars |

The Plugin Creator package is USER/PRIVATE; the Git repository is public and Apache-2.0. Publishing the private package bodies into the public Git repository is not an automatic repair. Keep both copies intact until the source owner approves an explicit canonical-body decision, publication rights and version/release plan.

### 2.5 Video Explainer — version gap and non-comparable file inventory

Plugin Creator package metadata/manifest report 4.1.12; its README heading says V4.1.11. The public Git source manifest/README report 4.1.9. The Plugin Creator package archive file inventory does not expose the 16 current runtime instruction files as `SKILL.md` files, while the Git source tree contains 14 `skills/*/SKILL.md` files. Therefore a direct one-to-one instruction-body parity comparison cannot be claimed from the available file trees. The source tree must be reconciled against the actual 4.1.12 instruction snapshot, docs, scripts, schemas and assets before advancing the public Git source.


### 2.6 Progressive Roadmap Evaluator — private package verified, no Git source

The Plugin Creator USER/PRIVATE package is verified at v0.1.1, release `pluginrel_6b0385d7a4488191a681997c0d9ae531`, with 23 package files and nine skill procedures. No canonical Git child repository or independently declared distribution license has been accepted. Therefore there is no Git baseline to compare; retain `NOT_IDENTIFIED` / `NOT_COMPARED` and `snapshot_only`. Package existence is not canonical Git source integration.

## 3. Rights and publication gate

- Existing source-backed repositories: SDO is Apache-2.0; A.S.F.R.E.E is PolyForm Noncommercial; SKILL ANALYZER and Video Explainer have no root LICENSE found; Anatomi Prompt is private and has no root LICENSE found.
- The 14 Plugin Creator packages without Git source repositories are USER/PRIVATE. Their package manifests omit a license field and no package-root LICENSE/NOTICE was found. Agent Skills Atlas contains upstream MIT attribution/notice material, which does not license the wrapper package as a whole.
- Photo Fixer and PVEE Plugin Creator archives contain complete private package trees, but their Git candidate repositories remain incomplete. Their platform package does not inherit any Git candidate repository license automatically.

**Rule:** no private package is copied to a public child repository or marked distributable until canonical source ownership, third-party attribution, license and target distribution rights are explicitly reviewed and approved. No package in the distribution registry is promoted by this report.

## 4. Next controlled changes

1. Anatomi: keep synchronized; add parity regression checks to future releases.
2. SKILL ANALYZER: reconcile the single platform-compatibility skill and platform version 1.0.0 → approved 1.3.0, then read back and test.
3. A.S.F.R.E.E: keep Git 0.5.0-rc.1 as candidate; owner acceptance and noncommercial rights review before platform republish.
4. SDO: choose one canonical 0.1.0 content body; preserve private-package boundary; implement source sync through an authorized private source or an explicitly approved public publication.
5. Video Explainer: map runtime instruction snapshots to the package archive and update public source only after complete source/asset/license reconciliation.
6. 14 unintegrated Git sources and two incomplete Git candidates: establish independent Git repositories under an explicitly approved visibility/license policy; current Plugin Creator packages remain private attestation sources only.

## 5. Evidence links

- [Parent source inventory](SOURCE-REPOSITORY-STATUS.md)
- [Version reconciliation policy](VERSION-RECONCILIATION.md)
- [Package version matrix](PACKAGE-VERSION-MATRIX.md)
- [Compatibility and test plan](COMPATIBILITY-AND-TEST-PLAN.md)
