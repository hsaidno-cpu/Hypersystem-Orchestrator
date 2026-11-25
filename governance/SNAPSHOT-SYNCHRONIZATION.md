# Instruction Snapshot and Synchronization Governance

## 1. Purpose

This repository exposes a central, segregated view of the installed plugin instructions without turning the ecosystem into a single source-code monorepo.

Each plugin has its own directory under plugin-instructions. The bundle contains the complete available skill instructions for that plugin at the recorded capture date. The bundle is a read-only convenience copy, not the canonical package source.

## 2. Current source classes

- Source-backed official plugins: point to their independent Git submodule/source repository.
- Not-identified plugins: store a complete installed-skill instruction snapshot, with source URI for each skill.
- Photo Fixer and PVEE: separate snapshots available, but their explicitly referenced GitHub repositories remain CANDIDATE_INCOMPLETE until complete manifests, skill trees and tests are restored.
- SDO: official public source is pinned at promkespkmbinuang-coder/SPDO commit 9d3c4bc09179ff857df4f3819be83e1847571add; the parent also retains the Plugin Creator instruction snapshot, which must be compared for drift.
- A.S.F.R.E.E Legacy: redirect-only snapshot linked to A.S.F.R.E.E Canonical.

## 3. Synchronization contract

Every snapshot should record plugin key and package display name; exact source URI of each skill; snapshot date; source repository, visibility, branch and immutable commit (when one exists); package release version, target version, installed header version and their evidence; license classification and required notices; content digest and bundle path; last reviewed compatibility state.

Refresh steps:
1. Re-read the installed skill registry.
2. Identify additions, removals and renamed skills.
3. Read the complete skill bodies; do not reconstruct missing content from descriptions.
4. Compare against canonical source where a repository exists.
5. Preserve the plugin directory boundary and metadata.
6. Record source drift, version conflicts, license and privacy issues.
7. Rebuild the bundle and index.
8. Run static validation, structural checks and relevant contract tests.
9. Update the parent commit and Notion status.

## 4. Authority policy

A child repository is authoritative for its own implementation. A runtime skill snapshot is authoritative only as evidence of the instructions visible through the connected skill registry at the capture date.

The parent catalog/positioning controls cross-plugin ownership and handoff expectations. It cannot silently overwrite a child plugin's internal implementation. Conflicts between parent positioning and child instruction text become explicit source-alignment tasks.

## 5. Security, privacy and licensing

- Do not copy private plugin source into a public snapshot without explicit owner approval.
- Do not assume the parent Apache-2.0 license applies to child content.
- The A.S.F.R.E.E source remains under PolyForm Noncommercial 1.0.0 with its required notice.
- SKILL ANALYZER and Anatomi Prompt repository root LICENSE paths were not found during this audit; preserve their source pointers and do not infer a license.
- Never place secrets, credentials, personal data or private runtime state inside a snapshot.

## 6. Current completeness declaration

The index contains 265 skill records across 23 plugin identities. Five official plugin source repositories are pinned; the SDO runtime snapshot is now accompanied by a verified canonical source pointer:
- Runtime instruction snapshots remain segregated for 15 NOT_IDENTIFIED packages and two CANDIDATE_INCOMPLETE packages. Video Explainer and SDO keep separate Plugin Creator snapshots with official Git submodules;
- Source-backed plugin packages are represented by their independent submodules/source pointers (SKILL ANALYZER, A.S.F.R.E.E, Anatomi Prompt, Video Explainer and SDO);
- 1 skill document represents the A.S.F.R.E.E Legacy redirect.

This is a complete snapshot of the skill definitions visible to the current connected registry at capture time, not proof that hidden, inaccessible, unpublished or future package files are included.


## Video Explainer current release exception

The Video Explainer instruction bundle is captured from current Plugin Creator release 4.1.12 (release ID pluginrel_6b02a0f630208191b71ad994703aed68). Scope USER and discoverability PRIVATE. At the owner's explicit request, the parent contains only 16 SKILL.md instruction files, not binary assets or unrelated package files. The public GitHub source is pinned at 4.1.9; source/deployment parity is not claimed.


## Additional source reconciliation

- SDO source repository: promkespkmbinuang-coder/SPDO, commit 9d3c4bc09179ff857df4f3819be83e1847571add, source version 0.1.0, Apache-2.0, signature-verified. Its runtime snapshot remains for current Plugin Creator read-back; canonical source is the independent Git submodule. Compare content hashes before declaring exact instruction parity.
- PVEE declared source pointer: promkespkmbinuang-coder/CL-VAEPPC, observed commit 1ab0c41081ccdbb91cc9dec0a2864acd0de00d54. It is registered as CANDIDATE_INCOMPLETE because the current tree does not contain a package manifest or skill source tree.
- Counts: five official source submodules, two incomplete source candidates, fifteen NOT_IDENTIFIED plugin sources, one legacy redirect and 256 skill records across 22 plugin identities.


## SDO source/snapshot drift (2026-11-22)

SDO is an official source submodule, but the canonical Git master SKILL.md and the current Plugin Creator master SKILL.md differ in content and length (10,573 vs 23,651 characters). Package manifests both report 0.1.0. This is version metadata match with instruction-content drift, not full source parity.

- Keep the Plugin Creator snapshot and Git source submodule as separate evidence.
- Do not overwrite either file automatically.
- Have the SDO source owner review the semantic diff, decide the canonical body, update changelog/package version if required, and verify read-back before changing source_instruction_parity_status to MATCH.
- Until then, source_sync_status remains SOURCE_INSTRUCTION_DRIFT_DETECTED.


### Ponytail Engineering System snapshot boundary (2026-11-25)

The Ponytail Engineering System derivative is a Plugin Creator USER/PRIVATE release (0.1.0), not a public source package. No dedicated canonical Git source or redistribution licence has been accepted. Keep its instruction content in the authorized private package; the public parent catalog may retain only provenance metadata and routing summaries.