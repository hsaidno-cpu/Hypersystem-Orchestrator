# Instruction Snapshot and Synchronization Governance

## 1. Purpose

This repository exposes a central, segregated view of the installed plugin instructions without turning the ecosystem into a single source-code monorepo.

Each plugin has its own directory under plugin-instructions. The bundle contains the complete available skill instructions for that plugin at the recorded capture date. The bundle is a read-only convenience copy, not the canonical package source.

## 2. Current source classes

- Source-backed official plugins: point to their independent Git submodule/source repository.
- Not-identified plugins: store a complete installed-skill instruction snapshot, with source URI for each skill.
- Photo Fixer: snapshot available, but its GitHub repository remains an incomplete candidate.
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

The index contains 238 skill records across 20 plugin identities:
- 203 skill documents are stored as segregated runtime instruction bundles for the 16 packages without verified official source submodules;
- 34 skill records refer to the three source-backed plugin packages whose canonical sources are in submodules;
- 1 skill document represents the A.S.F.R.E.E Legacy redirect.

This is a complete snapshot of the skill definitions visible to the current connected registry at capture time, not proof that hidden, inaccessible, unpublished or future package files are included.


## Video Explainer current release exception

The Video Explainer instruction bundle is captured from current Plugin Creator release 4.1.12 (release ID pluginrel_6b02a0f630208191b71ad994703aed68). Scope USER and discoverability PRIVATE. At the owner's explicit request, the parent contains only 16 SKILL.md instruction files, not binary assets or unrelated package files. The public GitHub source is pinned at 4.1.9; source/deployment parity is not claimed.
