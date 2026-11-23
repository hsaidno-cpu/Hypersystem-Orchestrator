# Source Repository Classification and Reconciliation

**Inventory date:** 2026-11-23
**Platform package-source attestation:** 13/13 formerly NOT_IDENTIFIED Git sources have a verified current Plugin Creator USER/PRIVATE package manifest and full file inventory. Git child repository status remains NOT_IDENTIFIED until an immutable repository source is accepted.  
**Plugin identities:** 21  
**Verified official plugin source repositories pinned:** 5  
**Candidate/incomplete source repositories:** 2  
**Plugin identities with no accepted GitHub source:** 13  
**Legacy redirect identities:** 1 (A.S.F.R.E.E Legacy; not a second product)

## 1. Search scope and evidence

The connected GitHub owner account hsaidno-cpu exposes six repositories: Hypersystem-Orchestrator, HSMART, skill-analyzer, A.S.F.R.E.E, Photo-Fixer and anatomi-prompt-strategis (private).

The connected GitHub collaborator scope also exposes repositories under promkespkmbinuang-coder. Repository-name and manifest provenance checks identified:
- promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR — official public source for Video Explainer, but behind Plugin Creator deployment 4.1.12.
- promkespkmbinuang-coder/SPDO — official public source for Skill Developer Orchestrator 0.1.0.
- promkespkmbinuang-coder/CL-VAEPPC — explicitly referenced by the current PVEE Plugin Creator manifest, but incomplete at observed HEAD and not eligible for submodule integration.
- promkespkmbinuang-coder/CL2-VAEPPC — not accepted; only a placeholder README and LICENSE, with no package identity or provenance.

Search results with similar names were not accepted as source evidence. A repository is not canonical simply because a query returns a matching phrase.


## 1.1. Private Plugin Creator package-source attestation — 23 November 2026

The previous `NOT_IDENTIFIED` classification refers specifically to the **canonical Git repository**, not to whether a Plugin Creator package exists. A fresh read-back of current Plugin Creator packages now confirms a USER/PRIVATE package manifest and complete file inventory for all 13 identities still lacking a canonical Git repository:

| Plugin package | Platform version | Package file inventory | Git source disposition |
|---|---:|---:|---|
| Evaluator Team | 1.0.0 | 13 files | NOT_IDENTIFIED |
| Master Photo Restoration | 1.0.0 | 4 files | NOT_IDENTIFIED |
| GODEX Motion Audio | 2.0.0 | 19 files | NOT_IDENTIFIED |
| AI Prompt Finder & Creator | 1.0.0 | 12 files | NOT_IDENTIFIED |
| Agent Jailbreak Skill DS | 0.2.0 | 14 files | NOT_IDENTIFIED |
| Motion Graphic by arifanara V.01 | 0.2.0 | 30 files | NOT_IDENTIFIED |
| Plugin Agent Orchestrator | 2.0.0 | 86 files | NOT_IDENTIFIED |
| Cortex Workbench | 1.0.0 | 16 files | NOT_IDENTIFIED |
| CommandCraft 56 | 0.1.0 | 17 files | NOT_IDENTIFIED |
| Agent Skills Atlas | 0.3.1 | 43 files | NOT_IDENTIFIED |
| AI Workflow Systems Orchestrator | 0.2.0 | 17 files | NOT_IDENTIFIED |
| GrowthForge Business OS | 1.1.1 | 31 files | NOT_IDENTIFIED |
| People & Business Competency Academy | 0.1.0 | 14 files | NOT_IDENTIFIED |

This verifies an identifiable private platform package and source tree inventory; it does **not** create a canonical Git source, immutable Git commit, public release, or redistribution right. All 13 package manifests omit a `license` field and the package file inventories contain no package-root LICENSE/NOTICE. Agent Skills Atlas includes upstream MIT license/attribution material, but that is not a package-wide license grant for the wrapper plugin.

The two Git candidate repositories also have complete Plugin Creator package trees:
- Photo Fixer: 19 platform files / 45,649 bytes; the declared Git candidate still contains only README/LICENSE and is not an accepted canonical source.
- PVEE Promkes Super Orchestrator: 37 platform files / 246,675 bytes; the declared Git candidate remains an incomplete legacy/source shell with README/LICENSE/empty marker only.

**Disposition:** source identity and platform-package provenance are now verified; Git-source migration and license/distribution clearance remain open. Keep the packages USER/PRIVATE and non-installable. Do not copy their private files into this public parent repository without a separate explicit publication decision.

## 2. Classification rules

| Classification | Meaning | Allowed action |
|---|---|---|
| OFFICIAL_PUBLIC_SOURCE | Source identity and package structure match; public repo inspected | Pin immutable commit as Git submodule |
| OFFICIAL_PRIVATE_SOURCE | Canonical source inspected and private | Pin only while preserving private access |
| OFFICIAL_PUBLIC_SOURCE_LAGGING | Official source identity confirmed, but source version is behind a separately verified deployment | Pin exact commit; record drift; sync only after full reconciliation |
| PROTOTYPE | Explicitly identified prototype with owner and relationship to intended plugin | Register as prototype; do not represent as release source |
| MIRROR | Confirmed copy of another canonical source | Record upstream and sync provenance; never create a duplicate plugin source |
| CANDIDATE_INCOMPLETE | Source pointer/name is supported, but manifest or package tree is incomplete | Keep separate; do not pin as canonical submodule |
| NOT_IDENTIFIED | No reliable canonical GitHub source accepted | Keep segregated instruction snapshot and source gap |
| LEGACY_REDIRECT | Explicit compatibility redirect to canonical product | Redirect only; no independent product implementation |
| RELATED_UPSTREAM_DATASET | Upstream dataset consumed by a plugin, not the plugin source itself | Record as data provenance; do not treat as the plugin's canonical repository |
| RELATED_PLATFORM | Related platform, not one of the registered plugins | Keep outside plugin source registry |

No confirmed mirror or prototype repository was found in the inspected set. Do not invent those classifications for unknown sources.

## 3. Five verified source repositories

| Plugin | Repository | Classification | Source version / pin | License |
|---|---|---|---|---|
| SKILL ANALYZER | hsaidno-cpu/skill-analyzer | OFFICIAL_PUBLIC_SOURCE | 1.3.0 / c469af7977c9bf6dcb3f5ab7b085a6de20d87004 | No root LICENSE found |
| A.S.F.R.E.E Canonical | hsaidno-cpu/A.S.F.R.E.E | OFFICIAL_PUBLIC_SOURCE | 0.5.0-rc.1 / a5eb55db0f6c2c6126a7fbcba645caf44c660c93 | PolyForm Noncommercial 1.0.0 |
| Anatomi Prompt V3 | hsaidno-cpu/anatomi-prompt-strategis | OFFICIAL_PRIVATE_SOURCE | 3.0.0 / 06b46b88ed7eddc437792fae715f255cbe4eb13d | No root LICENSE found; keep private |
| Video Explainer Promkes | promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR | OFFICIAL_PUBLIC_SOURCE_LAGGING | 4.1.9 / f8f8c0f29ff9d851fa75eba764978c24bdd79416; deployment 4.1.12 | No root LICENSE found |
| Skill Developer Orchestrator | promkespkmbinuang-coder/SPDO | OFFICIAL_PUBLIC_SOURCE | 0.1.0 / 9d3c4bc09179ff857df4f3819be83e1847571add | Apache-2.0 |

The SDO source contains plugin.json version 0.1.0, README, the master SKILL.md, three reference files and tests/acceptance-cases.json. The exact main commit is signature-verified. Plugin Creator current package version is also 0.1.0. The parent pins this commit at plugins/skill-developer-orchestrator. **Important parity finding:** Plugin Creator master SKILL.md (23,651 characters) differs from Git source master SKILL.md (10,573 characters) after normalization. The repo identity, manifest and version are official, but instruction content is not yet synchronized. Keep the installed snapshot and Git source independent until an owner-reviewed reconciliation is completed.

## 4. Two candidate/incomplete repositories

| Plugin | Repository | Evidence | Disposition |
|---|---|---|---|
| Photo Fixer | hsaidno-cpu/Photo-Fixer | Current Plugin Creator manifest declares the repository, but its root contains only README.md and Apache-2.0 LICENSE; no plugin manifest, skills or tests | CANDIDATE_INCOMPLETE; not a submodule |
| PVEE Promkes Super Orchestrator | promkespkmbinuang-coder/CL-VAEPPC | Current Plugin Creator manifest explicitly declares repository/homepage. Observed main commit 1ab0c41081ccdbb91cc9dec0a2864acd0de00d54 is signature-verified, but recursive tree contains only README.md, Apache-2.0 LICENSE and a one-byte empty .claude-plugin marker. No manifest, skill tree, scripts, references or tests are present. README documents an older Video Explainer Promkes V3.0 line, not current PVEE 2.0.2 source parity. | CANDIDATE_INCOMPLETE; source pointer recorded, no submodule |

The CL2-VAEPPC repository is not accepted: only a placeholder README and LICENSE exist, without explicit plugin identity or a full source tree.

People & Business Competency Academy has a verified private Plugin Creator package (0.1.0) and nine skill procedures, but no dedicated canonical GitHub source repository or separate source license decision has been established. The parent repository therefore records it as pending_repository / NOT_IDENTIFIED and stores only a clearly attributed instruction snapshot plus the user-supplied title-author reference catalog. This is not a canonical source integration and does not imply public installation or runtime readiness.

Agent Skills Atlas separately references alirezarezvani/claude-skills as an upstream dataset at commit f8593c4941210a621a6629ce1da9e07897976d5f, package 2.14.14. That repository is upstream inventory data, not the canonical source repository for the Agent Skills Atlas plugin itself.

## 5. Thirteen plugin sources remain NOT_IDENTIFIED

1. Evaluator Team
2. Master Photo Restoration
3. GODEX Motion Audio
4. AI Prompt Finder & Creator
5. Agent Jailbreak Skill DS
6. Motion Graphic by arifanara V.01
7. Plugin Agent Orchestrator
8. Cortex Workbench
9. CommandCraft 56
10. Agent Skills Atlas
11. AI Workflow Systems Orchestrator
12. GrowthForge Business OS
13. People & Business Competency Academy

Together with the two incomplete candidates, there are **15 plugin source identities still not integrated** (13 NOT_IDENTIFIED plus 2 CANDIDATE_INCOMPLETE). The earlier backlog count was 15; SDO has now been identified and integrated as the fifth official source submodule.

## 6. Instruction snapshot inventory

- 13 NOT_IDENTIFIED packages retain separate, read-only runtime instruction snapshots, including People & Business Competency Academy.
- Photo Fixer and PVEE retain separate candidate-source snapshots; neither candidate source is treated as canonical package source.
- Video Explainer and SDO retain current Plugin Creator instruction snapshots while each has its own independently pinned source repository.
- SKILL ANALYZER, A.S.F.R.E.E and Anatomi Prompt are represented by their own source submodules/source pointers.
- A.S.F.R.E.E Legacy remains one redirect-only snapshot.
- 247 skill records are indexed across 21 plugin identities.
- No snapshot merges two plugin packages or transfers implementation ownership to the parent repository.

## 7. Required proof before submodule integration

A source may move from NOT_IDENTIFIED/CANDIDATE to OFFICIAL_SOURCE only after:
- canonical owner and repository identity are confirmed against the Plugin Creator ID/name;
- README, manifest, complete skill/source tree and supporting references are inspected;
- license and attribution notices are reviewed;
- source version, tag/commit history and immutable commit are verified;
- prototype/mirror/legacy relationships are distinguished;
- source/snapshot drift is compared;
- positive, negative and contract compatibility checks pass or have explicit NOT_RUN states.

Do not infer a source version from a product label or README heading. Do not convert a minimal repository into an official source merely because a manifest points to it. No plugin source code is copied into the parent; official implementations remain independent submodules.
