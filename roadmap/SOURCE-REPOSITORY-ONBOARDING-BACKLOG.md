# Canonical Plugin Repository Onboarding Backlog

**As-of:** 2026-11-22  
**Parent:** Hypersystem Orchestrator  
**Current verified source repositories:** 4 plugin sources  
**Not identified at GitHub-source level:** 14 plugin identities  
**Candidate incomplete:** Photo Fixer

## 1. Source classifications

- OFFICIAL_PUBLIC_SOURCE: canonical source identity and source artifacts inspected; public source.
- OFFICIAL_PRIVATE_SOURCE: canonical source inspected; private access applies.
- OFFICIAL_PUBLIC_SOURCE_LAGGING: official source is confirmed but behind a separately verified deployment.
- PROTOTYPE: explicitly identified prototype with owner and relationship; not a release source.
- MIRROR: confirmed mirror of another canonical source; upstream identity must be recorded.
- CANDIDATE_INCOMPLETE: name appears relevant but source artifacts are incomplete.
- NOT_IDENTIFIED: no canonical GitHub source accepted yet.
- LEGACY_REDIRECT: redirect-only identity, never a second product source.
- RELATED_PLATFORM: related platform, not a plugin source.

## 2. Verified source pins

| Plugin | Repository | Classification | Pin / version |
|---|---|---|---|
| SKILL ANALYZER | hsaidno-cpu/skill-analyzer | OFFICIAL_PUBLIC_SOURCE | c469af7977c9bf6dcb3f5ab7b085a6de20d87004; source 1.3.0 |
| A.S.F.R.E.E Canonical | hsaidno-cpu/A.S.F.R.E.E | OFFICIAL_PUBLIC_SOURCE | a5eb55db0f6c2c6126a7fbcba645caf44c660c93; source 0.5.0-rc.1; PolyForm Noncommercial |
| Anatomi Prompt V3 | hsaidno-cpu/anatomi-prompt-strategis | OFFICIAL_PRIVATE_SOURCE | 06b46b88ed7eddc437792fae715f255cbe4eb13d; source 3.0.0 |
| Video Explainer Promkes | promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR | OFFICIAL_PUBLIC_SOURCE_LAGGING | f8f8c0f29ff9d851fa75eba764978c24bdd79416; source 4.1.9; deployed 4.1.12 |

## 3. Candidate and related repositories

| Repository | Classification | Next action |
|---|---|---|
| hsaidno-cpu/Photo-Fixer | CANDIDATE_INCOMPLETE | Add the complete source package, manifest, skill tree, tests and provenance in the owning repository before promoting it |
| hsaidno-cpu/HSMART | RELATED_PLATFORM | Keep separate; define an approved interface only if platform integration is required |
| hsaidno-cpu/Hypersystem-Orchestrator | CENTRAL_ECOSYSTEM | Parent registry/architecture/governance only |

## 4. Fourteen NOT_IDENTIFIED plugin repositories

The following package identities are present as separate instruction snapshots in plugin-instructions/, but no canonical independent GitHub source was verified in this inventory:

1. Skill Developer Orchestrator — Plugin Creator package 0.1.0
2. Evaluator Team — 1.0.0
3. Master Photo Restoration — 1.0.0
4. GODEX Motion Audio — 2.0.0
5. AI Prompt Finder & Creator — 1.0.0
6. Agent Jailbreak Skill DS — 0.2.0
7. Motion Graphic by arifanara V.01 — 0.2.0
8. Plugin Agent Orchestrator — 2.0.0
9. Cortex Workbench — 1.0.0
10. CommandCraft 56 — 0.1.0
11. Agent Skills Atlas — 0.3.1
12. AI Workflow Systems Orchestrator — 0.2.0
13. GrowthForge Business OS — 1.1.1
14. PVEE Promkes Super Orchestrator — 2.0.2

The Plugin Creator version is verified platform metadata, not a Git source release. Do not invent repository URLs from plugin slugs.

## 5. Repository creation and onboarding acceptance

For every NOT_IDENTIFIED source, the independent source repository must contain at minimum:
- maintainer/ownership statement and canonical plugin identity;
- README with scope, license, installation and status;
- plugin manifest with stable ID/name/version and repository URL;
- all current master/subskill instructions and references;
- tests/acceptance suite and validation instructions;
- changelog and release/version authority;
- attribution, license and source provenance for all copied/generated material;
- no secrets, credentials or private runtime data.

The parent repository can register and pin a canonical child source only after:
1. source URL and owner are confirmed;
2. repository identity matches the Plugin Creator package ID;
3. manifest and source tree are read;
4. license/rights boundary is verified;
5. current release/version and source history are recorded;
6. source commit is pinned;
7. parent catalog and instruction index are reconciled;
8. static, contract and compatibility tests pass or are explicitly marked not run.

## 6. Prototype, mirror and legacy controls

- A prototype is not canonical source until the owner explicitly promotes it and evidence is reconciled.
- A mirror must name its upstream canonical repository and sync strategy; never pin both as independent plugins.
- A legacy package is a redirect-only compatibility entry; it must not own new functionality.
- A repository with only a README/license or placeholder structure stays candidate/incomplete.
- A private source repository remains private and must not be copied into a public parent without explicit authorization.

## 7. Cross-plugin source-alignment tasks

- SDO / Evaluator Team: make the Evaluator Team implementation helper handoff-only; SDO is the sole engineering write owner.
- Photo Fixer / Master Photo Restoration: restrict Photo Fixer's internal restoration subskill to localized ordinary-photo cleanup; archival restoration routes to Master Photo Restoration.
- PVEE / Video Explainer: PVEE owns health truth, communication governance, campaign decision and outcome evaluation; Video Explainer owns Promkes technical production compilation.
- GODEX / Motion Graphic: maintain audio-source/timing ownership separately from visual-art/motion/timeline ownership.
- Anatomi Prompt / AI Prompt Finder: keep prompt-structure work separate from content/reference-to-prompt reconstruction.

