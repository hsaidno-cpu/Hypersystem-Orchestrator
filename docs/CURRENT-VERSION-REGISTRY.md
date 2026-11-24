# Current Plugin Version Registry

> **GENERATED FILE. DO NOT EDIT BY HAND.** Source: catalog/plugins.json and catalog/repositories.json. Regenerate with python tools/render_package_version_matrix.py --write; CI verifies it with --check.

**Registry revision:** 2026-11-24  
**Plugin identities:** 23 / 23  
**Plugin Creator release-metadata read-back:** 2026-11-24  
**Instruction snapshot index capture:** see catalog/instruction-snapshots.json

## Version authority model

The following values are independent and must never be collapsed into one generic version:

1. **Plugin Creator package version and current release ID** — the installed/deployed package metadata in ChatGPT.
2. **Canonical Git source version and immutable commit** — the source manifest version and pinned commit recorded by the parent repository.
3. **Instruction-content parity** — direct file-level comparison of package files against the canonical source; matching version strings do not prove matching content.
4. **Internal skill-header version / product label** — may be a separate label (for example v4.0.9 or V.01), not a package release.
5. **Contract/schema version and runtime/adapter version** — separately governed interface and execution planes.
6. **Instruction snapshot capture date and metadata observation date** — evidence timestamps, not software versions.

## Current matrix

| Plugin | Plugin Creator package | Current release ID | Git source version | Canonical source / pinned commit | Version alignment | Instruction parity | Source state | Metadata observed | Snapshot captured |
|---|---:|---|---:|---|---|---|---|---|---|
| Video Explainer Promkes V4.1.12 | 4.1.12 | pluginrel_6b02a0f630208191b71ad994703aed68 | 4.1.9 | promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR @ f8f8c0f29ff9d851fa75eba764978c24bdd79416 | DEPLOYMENT_AHEAD_OF_SOURCE | NOT_COMPARED | integrated_submodule | 2026-11-24 | 2026-11-22 |
| Skill Developer Orchestrator | 0.1.0 | pluginrel_6afdee10a5688191ad8fc37a9d0d827b | 0.1.0 | promkespkmbinuang-coder/SPDO @ 9d3c4bc09179ff857df4f3819be83e1847571add | SOURCE_AND_PLATFORM_MATCH | DRIFT_DETECTED | integrated_submodule | 2026-11-24 | 2026-11-22 |
| Evaluator Team | 1.0.0 | pluginrel_6afdee5a10108191a38e1ee7f84f7524 | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| Master Photo Restoration | 1.0.0 | pluginrel_6ae29cf38e4881918f892e746050891d | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| Anatomi Prompt V3.0 — Octa-Prompt | 3.0.0 | pluginrel_6af18ad1d81481919e4c6fa6d512d0ee | 3.0.0 | hsaidno-cpu/anatomi-prompt-strategis @ 06b46b88ed7eddc437792fae715f255cbe4eb13d | SOURCE_AND_PLATFORM_MATCH | MATCH | integrated_submodule | 2026-11-24 | 2026-11-22 |
| SKILL ANALYZER | 1.0.0 | pluginrel_6af1a98cdbe881918f30895f5af93afc | 1.3.0 | hsaidno-cpu/skill-analyzer @ c469af7977c9bf6dcb3f5ab7b085a6de20d87004 | SOURCE_AHEAD_OF_PLATFORM | DRIFT_DETECTED | integrated_submodule | 2026-11-24 | 2026-11-22 |
| GODEX Motion Audio | 2.0.0 | pluginrel_6ae56ef615688191ba0b357fc7b1fd32 | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| AI Prompt Finder & Creator | 1.0.0 | pluginrel_6ae57d451eac81918ae3d05fd7bb0a85 | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| Agent Jailbreak Skill DS | 0.2.0 | pluginrel_6ae8691261c08191a69065ccbea28965 | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| Motion Graphic by arifanara V.01 | 0.2.0 | pluginrel_6ae97fb29a408191b4ce949723bc460d | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| Plugin Agent Orchestrator | 2.0.0 | pluginrel_6afdff8b11848191be8765373812262f | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| Photo Fixer | 1.0.0 | pluginrel_6afeb1f735888191b1d25574f336661b | — | hsaidno-cpu/Photo-Fixer (candidate; not pinned) | CANDIDATE_SOURCE_INCOMPLETE | NOT_APPLICABLE | candidate_repository | 2026-11-24 | 2026-11-22 |
| A.S.F.R.E.E | 0.3.2 | pluginrel_6b00fc6b23bc8191a5930132969e52c2 | 0.5.0-rc.1 | hsaidno-cpu/A.S.F.R.E.E @ a5eb55db0f6c2c6126a7fbcba645caf44c660c93 | SOURCE_AHEAD_OF_PLATFORM | DRIFT_DETECTED | integrated_submodule | 2026-11-24 | 2026-11-22 |
| A.S.F.R.E.E Legacy | 1.0.4 | pluginrel_6b01644d66bc819197d7331d823a8619 | — | Redirect only → A.S.F.R.E.E | LEGACY_REDIRECT_VERSION | NOT_APPLICABLE | canonical_redirect | 2026-11-24 | 2026-11-22 |
| Cortex Workbench | 1.0.0 | pluginrel_6aff571bb43c819192f2dad006d28d3d | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| CommandCraft 56 | 0.1.0 | pluginrel_6aff5856da608191b6451e8d19a7b44a | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| Agent Skills Atlas | 0.3.1 | pluginrel_6b000c2b186c819199e6bf1e08d4b646 | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| People & Business Competency Academy | 0.1.0 | pluginrel_6b039efc6dfc81919fffbe265e8f84c9 | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-23 |
| AI Workflow Systems Orchestrator | 0.2.0 | pluginrel_6b015fe943608191b46d0a439dd4f55e | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| GrowthForge Business OS | 1.1.1 | pluginrel_6b023e6d011481919323471664b9d286 | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-22 |
| PVEE Promkes Super Orchestrator | 2.0.2 | pluginrel_6b029dfa21e88191957129cfce63353f | — | promkespkmbinuang-coder/CL-VAEPPC (candidate; not pinned) | CANDIDATE_SOURCE_INCOMPLETE | NOT_APPLICABLE | candidate_repository | 2026-11-24 | 2026-11-22 |
| Progressive Roadmap Evaluator (PRE) | 0.1.1 | pluginrel_6b0385d7a4488191a681997c0d9ae531 | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_COMPARED | pending_repository | 2026-11-24 | 2026-11-23 |
| Ponytail Engineering System | 0.1.0 | pluginrel_6b044f37640081918df7f449298d72cf | — | NOT_IDENTIFIED | PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED | NOT_APPLICABLE | pending_repository | 2026-11-24 | 2026-11-23 |

## Reconciliation findings requiring explicit disposition

The following entries are not automatically repaired by changing a version string. Each requires the action listed below.

### Video Explainer Promkes V4.1.12

- Plugin Creator: 4.1.12 / pluginrel_6b02a0f630208191b71ad994703aed68.
- Git source: 4.1.9.
- Alignment: DEPLOYMENT_AHEAD_OF_SOURCE; parity: NOT_COMPARED.
- Version evidence: Current Plugin Creator deployment 4.1.12; official public GitHub source is 4.1.9. Embedded M00 header v4.0.9 is an internal skill version, not the package version. Source parity is pending.
- Parity evidence: The Plugin Creator USER/PRIVATE archive is verified at 4.1.12, but its complete file inventory exposes no SKILL.md files for a direct file-level comparison against the 14 Git source skill files at 4.1.9. Plugin Creator plugin.json reports 4.1.12 while its README heading is V4.1.11; Git plugin.json and README report 4.1.9. Keep source_instruction_parity_status NOT_COMPARED and source sync blocked until the actual deployment skill files, package assets, manifest and source are mapped one-to-one.

### Skill Developer Orchestrator

- Plugin Creator: 0.1.0 / pluginrel_6afdee10a5688191ad8fc37a9d0d827b.
- Git source: 0.1.0.
- Alignment: SOURCE_AND_PLATFORM_MATCH; parity: DRIFT_DETECTED.
- Version evidence: Canonical Git source manifest and current Plugin Creator package both identify 0.1.0, but their master SKILL.md bodies differ substantially. Version metadata is aligned; instruction-content synchronization remains pending.
- Parity evidence: Full 4-file instruction/reference comparison against Plugin Creator USER/PRIVATE v0.1.0 and pinned Git source v0.1.0: 0/4 files match exactly. Master SKILL.md is 23,651 vs 10,573 chars; audit-matrix.md 4,874 vs 3,111; github-change-protocol.md 4,596 vs 2,497; regression-and-release-gates.md 4,500 vs 3,030. Plugin Creator bodies are longer; package and source versions match but content does not. Preserve both until the source owner selects the canonical body and updates/tests the other side.

### Evaluator Team

- Plugin Creator: 1.0.0 / pluginrel_6afdee5a10108191a38e1ee7f84f7524.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### Master Photo Restoration

- Plugin Creator: 1.0.0 / pluginrel_6ae29cf38e4881918f892e746050891d.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### SKILL ANALYZER

- Plugin Creator: 1.0.0 / pluginrel_6af1a98cdbe881918f30895f5af93afc.
- Git source: 1.3.0.
- Alignment: SOURCE_AHEAD_OF_PLATFORM; parity: DRIFT_DETECTED.
- Version evidence: Canonical public GitHub README and manifest identify 1.3.0; current Plugin Creator package metadata reports 1.0.0. Parent source baseline is 1.3.0; platform republishing is a separate action.
- Parity evidence: Full 12-file skill comparison against Plugin Creator USER/PRIVATE v1.0.0 release and pinned Git source 1.3.0: 11/12 SKILL.md files are exact after CRLF normalization. The only mismatch is skills/platform-compatibility/SKILL.md: Plugin Creator has 71 lines; Git source has 81 lines and appends a HOSTED GATEWAY PROFILE section. Git source is ahead; do not auto-overwrite or relabel the package. Version alignment remains SOURCE_AHEAD_OF_PLATFORM.

### GODEX Motion Audio

- Plugin Creator: 2.0.0 / pluginrel_6ae56ef615688191ba0b357fc7b1fd32.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### AI Prompt Finder & Creator

- Plugin Creator: 1.0.0 / pluginrel_6ae57d451eac81918ae3d05fd7bb0a85.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### Agent Jailbreak Skill DS

- Plugin Creator: 0.2.0 / pluginrel_6ae8691261c08191a69065ccbea28965.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### Motion Graphic by arifanara V.01

- Plugin Creator: 0.2.0 / pluginrel_6ae97fb29a408191b4ce949723bc460d.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: V.01 is a product label, not SemVer; the current Plugin Creator package version is 0.2.0.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### Plugin Agent Orchestrator

- Plugin Creator: 2.0.0 / pluginrel_6afdff8b11848191be8765373812262f.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### Photo Fixer

- Plugin Creator: 1.0.0 / pluginrel_6afeb1f735888191b1d25574f336661b.
- Git source: NOT_IDENTIFIED.
- Alignment: CANDIDATE_SOURCE_INCOMPLETE; parity: NOT_APPLICABLE.
- Version evidence: Plugin Creator package 1.0.0 is verified; the similarly named GitHub repository is incomplete and is not accepted as canonical source.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### A.S.F.R.E.E

- Plugin Creator: 0.3.2 / pluginrel_6b00fc6b23bc8191a5930132969e52c2.
- Git source: 0.5.0-rc.1.
- Alignment: SOURCE_AHEAD_OF_PLATFORM; parity: DRIFT_DETECTED.
- Version evidence: Public Git source is 0.5.0-rc.1 and is ahead of Plugin Creator package 0.3.2. It is a release candidate, not a stable production release.
- Parity evidence: Full 13-file skill comparison against Plugin Creator USER/PRIVATE v0.3.2 and pinned Git source 0.5.0-rc.1: 5/13 SKILL.md files match exactly; 8/13 differ, including the master orchestrator and O03/O04/O05/O06/O09/O11/O12. The Git source is materially longer in every differing file and is a release candidate. Treat the platform package as behind; do not promote RC or overwrite without owner review and release decision.

### A.S.F.R.E.E Legacy

- Plugin Creator: 1.0.4 / pluginrel_6b01644d66bc819197d7331d823a8619.
- Git source: NOT_IDENTIFIED.
- Alignment: LEGACY_REDIRECT_VERSION; parity: NOT_APPLICABLE.
- Version evidence: Version 1.0.4 belongs only to the compatibility redirect shell and is not the canonical A.S.F.R.E.E product version.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### Cortex Workbench

- Plugin Creator: 1.0.0 / pluginrel_6aff571bb43c819192f2dad006d28d3d.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### CommandCraft 56

- Plugin Creator: 0.1.0 / pluginrel_6aff5856da608191b6451e8d19a7b44a.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### Agent Skills Atlas

- Plugin Creator: 0.3.1 / pluginrel_6b000c2b186c819199e6bf1e08d4b646.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### People & Business Competency Academy

- Plugin Creator: 0.1.0 / pluginrel_6b039efc6dfc81919fffbe265e8f84c9.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Plugin Creator package version 0.1.0 and release are verified. No independent canonical Git repository/version exists; the parent repository can store a read-only instruction snapshot and catalog record but is not the child source of truth.
- Parity evidence: No independent Git source exists for a source/snapshot parity comparison. Reassess after a canonical child repository and license are established.

### AI Workflow Systems Orchestrator

- Plugin Creator: 0.2.0 / pluginrel_6b015fe943608191b46d0a439dd4f55e.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### GrowthForge Business OS

- Plugin Creator: 1.1.1 / pluginrel_6b023e6d011481919323471664b9d286.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: Current Plugin Creator version verified on 2026-11-22; canonical GitHub source release has not yet been identified.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### PVEE Promkes Super Orchestrator

- Plugin Creator: 2.0.2 / pluginrel_6b029dfa21e88191957129cfce63353f.
- Git source: NOT_IDENTIFIED.
- Alignment: CANDIDATE_SOURCE_INCOMPLETE; parity: NOT_APPLICABLE.
- Version evidence: A declared repository pointer is verified, but the repository is an incomplete legacy/source stub. Do not assign a Git source version or integrate as a submodule until the complete PVEE 2.0.2 source package is restored.
- Parity evidence: No independent source/snapshot content comparison applies while no canonical source package is integrated.

### Progressive Roadmap Evaluator (PRE)

- Plugin Creator: 0.1.1 / pluginrel_6b0385d7a4488191a681997c0d9ae531.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_COMPARED.
- Version evidence: Plugin Creator version 0.1.1 is verified. No canonical independent Git source repository has been identified; the parent repository stores only a public instruction snapshot.
- Parity evidence: No canonical PRE source repository exists in the registry to compare against the current Plugin Creator skill snapshot.

### Ponytail Engineering System

- Plugin Creator: 0.1.0 / pluginrel_6b044f37640081918df7f449298d72cf.
- Git source: NOT_IDENTIFIED.
- Alignment: PLATFORM_ONLY_SOURCE_NOT_IDENTIFIED; parity: NOT_APPLICABLE.
- Version evidence: The private Plugin Creator release is verified at 0.1.0. No dedicated canonical Git source for this derivative package has been accepted. Upstream Ponytail v5.3.3 is methodology provenance, not this package's source release.
- Parity evidence: No independent canonical Git source exists for parity comparison. The full USER/PRIVATE instruction files remain in the private Plugin Creator package; the public parent repository stores only a metadata pointer and concise skill index.

## Canonical source manifest evidence

| Repository | Manifest path | Manifest version | Manifest blob SHA | Pinned commit | Verified at |
|---|---|---:|---|---|---|
| hsaidno-cpu/skill-analyzer | plugin.json | 1.3.0 | 743b2c91339d19a9c915a8decad264092e2725c5 | c469af7977c9bf6dcb3f5ab7b085a6de20d87004 | 2026-11-24 |
| hsaidno-cpu/A.S.F.R.E.E | plugin/plugin.json | 0.5.0-rc.1 | f0211b1dc94fb61efe1b7aa011cec7018a7e4c07 | a5eb55db0f6c2c6126a7fbcba645caf44c660c93 | 2026-11-24 |
| hsaidno-cpu/anatomi-prompt-strategis | .agents/skills/anatomi-prompt/package/plugin.json | 3.0.0 | e3781f3d9d257da6092807e3b565dda251cb5f8b | 06b46b88ed7eddc437792fae715f255cbe4eb13d | 2026-11-24 |
| promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR | plugin.json | 4.1.9 | c16b81bbf8a30eda93ed0c3e6223748d6cb13466 | f8f8c0f29ff9d851fa75eba764978c24bdd79416 | 2026-11-24 |
| promkespkmbinuang-coder/SPDO | plugin.json | 0.1.0 | 3be086c8917cdd5e77b1d051042359e9b300792a | 9d3c4bc09179ff857df4f3819be83e1847571add | 2026-11-24 |

## Interpretation and release gates

- SOURCE_AHEAD_OF_PLATFORM means the Git source manifest is ahead of the current ChatGPT package; the package remains at its observed release until an authorized package update is completed and read back.
- DEPLOYMENT_AHEAD_OF_SOURCE means the current ChatGPT package is ahead of the canonical Git source. Do not rewrite source metadata to mimic the package; reconcile the complete package/source contents first.
- SOURCE_AND_PLATFORM_MATCH describes version metadata only. DRIFT_DETECTED still blocks a claim of content parity.
- NOT_IDENTIFIED and CANDIDATE_SOURCE_INCOMPLETE are intentional unknown/blocked states. Never fabricate a Git version from a package label.
- NOT_COMPARED is not a pass. It means a defensible one-to-one file comparison was not available.
- A release candidate remains an RC. It is not promoted to stable by being the highest source version.
- Private packages stay private. A source version match does not grant redistribution or publication rights.

## CI and freshness boundary

tools/validate_catalog.py checks that every Plugin Creator metadata observation is at most 30 days old, that each integrated source manifest is pinned to the registered commit, and that the actual parent Git tree gitlink SHA equals catalog/repositories.json. tools/render_package_version_matrix.py --check ensures this document is generated from the canonical registry.

**Important limitation:** the public GitHub Actions workflow does not query the private Plugin Creator service. The 30-day gate checks the recorded read-back date; it cannot independently prove that the date or external metadata is current. An authorized connector read-back must precede updates to the catalog.

A green static CI run does not prove live ChatGPT host activation, package deployment, runtime execution, licensing clearance or human release approval.

## Evidence snapshot

- Parent catalog revision: 2026-11-24.
- Platform metadata read-back dates represented: 2026-11-24.
- Parent source inventory date: 2026-11-24.
- Source pins are immutable commit identifiers; source manifest blob SHA identifies the exact version manifest inspected.
