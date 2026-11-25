# Canonical Plugin Repository Onboarding Backlog

**As-of:** 2026-11-23  
**Parent:** Hypersystem Orchestrator  
**Verified official plugin source repositories:** 5  
**Remaining Git source identities not integrated:** 17 (15 NOT_IDENTIFIED + 2 CANDIDATE_INCOMPLETE)
**Platform package-source provenance:** 15/15 NOT_IDENTIFIED packages have a verified USER/PRIVATE Plugin Creator manifest and file inventory; canonical Git source migration remains pending.

## 1. Source classifications

- OFFICIAL_PUBLIC_SOURCE: canonical source identity and package tree inspected; public source.
- OFFICIAL_PRIVATE_SOURCE: canonical source inspected; private access applies.
- OFFICIAL_PUBLIC_SOURCE_LAGGING: official source confirmed but behind a separately verified deployment.
- PROTOTYPE: explicitly identified prototype with owner and relationship; not a release source.
- MIRROR: confirmed copy of another canonical source; upstream identity and sync strategy must be recorded.
- CANDIDATE_INCOMPLETE: a declared or plausible source exists, but manifest or package tree is incomplete.
- NOT_IDENTIFIED: no canonical GitHub source accepted yet.
- LEGACY_REDIRECT: redirect-only identity, never a second product source.
- RELATED_UPSTREAM_DATASET: upstream dataset used by a plugin, not the plugin's own source.
- RELATED_PLATFORM: related platform, not a plugin source.

## 2. Verified source pins

| Plugin | Repository | Classification | Pin / version | License |
|---|---|---|---|---|
| SKILL ANALYZER | hsaidno-cpu/skill-analyzer | OFFICIAL_PUBLIC_SOURCE | c469af7977c9bf6dcb3f5ab7b085a6de20d87004; 1.3.0 | No root LICENSE found |
| A.S.F.R.E.E Canonical | hsaidno-cpu/A.S.F.R.E.E | OFFICIAL_PUBLIC_SOURCE | a5eb55db0f6c2c6126a7fbcba645caf44c660c93; 0.5.0-rc.1 | PolyForm Noncommercial 1.0.0 |
| Anatomi Prompt V3 | hsaidno-cpu/anatomi-prompt-strategis | OFFICIAL_PRIVATE_SOURCE | 06b46b88ed7eddc437792fae715f255cbe4eb13d; 3.0.0 | No root LICENSE found; private |
| Video Explainer Promkes | promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR | OFFICIAL_PUBLIC_SOURCE_LAGGING | f8f8c0f29ff9d851fa75eba764978c24bdd79416; Git 4.1.9, deployed 4.1.12 | No root LICENSE found |
| Skill Developer Orchestrator | promkespkmbinuang-coder/SPDO | OFFICIAL_PUBLIC_SOURCE | 9d3c4bc09179ff857df4f3819be83e1847571add; 0.1.0 | Apache-2.0 |

## 3. Candidate/incomplete and related repositories

| Plugin / relation | Repository | Classification | Next action |
|---|---|---|---|
| Photo Fixer | hsaidno-cpu/Photo-Fixer | CANDIDATE_INCOMPLETE | Head `95339901f84cdae861efcebd9820cb2e1efdc27d`; root Apache-2.0 is present, but current package source is only README/LICENSE. Restore manifest, master/subskill tree, references and tests before canonical promotion |
| PVEE Promkes Super Orchestrator | promkespkmbinuang-coder/CL-VAEPPC | CANDIDATE_INCOMPLETE | Head `1ab0c41081ccdbb91cc9dec0a2864acd0de00d54`; root Apache-2.0 is present, but current tree contains README/LICENSE/empty marker. Restore complete PVEE 2.0.2 source tree, manifest, scripts, tests and release history |
| HSMART | hsaidno-cpu/HSMART | RELATED_PLATFORM | Keep outside the plugin source registry |
| Agent Skills Atlas upstream dataset | alirezarezvani/claude-skills | RELATED_UPSTREAM_DATASET | Preserve pinned dataset provenance; do not register as Agent Skills Atlas plugin source |
| CL2-VAEPPC | promkespkmbinuang-coder/CL2-VAEPPC | UNVERIFIED_PLACEHOLDER | Not accepted; only README/LICENSE and no package identity or source tree |

## 4. Fourteen NOT_IDENTIFIED plugin repositories

1. Evaluator Team — Plugin Creator package 1.0.0
2. Master Photo Restoration — 1.0.0
3. GODEX Motion Audio — 2.0.0
4. AI Prompt Finder & Creator — 1.0.0
5. Agent Jailbreak Skill DS — 0.2.0
6. Motion Graphic by arifanara V.01 — 0.2.0
7. Plugin Agent Orchestrator — 2.0.0
8. Cortex Workbench — 1.0.0
9. CommandCraft 56 — 0.1.0
10. Agent Skills Atlas — 0.3.1
11. AI Workflow Systems Orchestrator — 0.2.0
12. GrowthForge Business OS — 1.1.1
13. People & Business Competency Academy — 0.1.0
14. Progressive Roadmap Evaluator (PRE) — 0.1.1

Plugin Creator version metadata and a complete USER/PRIVATE package file inventory verify a platform package source, not a canonical Git source release. Do not invent repository URLs from plugin slugs or treat a source dataset as the wrapper plugin's canonical source. For these 15 plugins, Git source migration remains pending and no redistribution license is declared in the current package manifest.

## 5. Repository creation and onboarding acceptance

Every NOT_IDENTIFIED plugin should receive its own independent repository with:
- maintainer/ownership statement and canonical Plugin Creator identity;
- README with purpose, source authority, scope, installation and status;
- plugin manifest and exact package version;
- complete master/subskill instruction tree and references;
- tests/acceptance suite and validation instructions;
- changelog/release authority;
- license and third-party attribution;
- no secrets, credentials or private runtime data.

The parent may register and pin a child source only after:
1. source URL and owner are confirmed;
2. repository identity maps to the Plugin Creator package;
3. manifest and complete source tree are read;
4. license and required notices are reviewed;
5. source version and commit/tag history are confirmed;
6. a specific immutable commit is pinned;
7. parent catalog, .gitmodules and snapshot index are updated;
8. static, contract and compatibility tests pass or are explicitly NOT_RUN.

## 6. Prototype, mirror and legacy controls

- A prototype is not canonical source until the owner explicitly promotes it and provenance is reconciled.
- A mirror must name its upstream canonical source, licensing basis and sync policy; never pin both as independent plugin products.
- A legacy package is redirect-only; A.S.F.R.E.E Legacy remains linked to A.S.F.R.E.E Canonical.
- A minimal README/LICENSE or placeholder repository stays candidate/incomplete.
- A private source remains private and is not copied into a public parent without explicit authorization.
- An upstream dataset used by a package is not automatically that package's canonical repository.


## 7. Cross-plugin source-alignment tasks

- SDO / Evaluator Team: make the Evaluator Team implementation helper handoff-only; SDO is the sole engineering write owner.
- Photo Fixer / Master Photo Restoration: restrict Photo Fixer's internal restoration subskill to localized ordinary-photo cleanup; archival restoration routes to Master Photo Restoration.
- PVEE / Video Explainer: PVEE owns health truth, communication governance, campaign decision and outcome evaluation; Video Explainer owns Promkes technical production compilation.
- GODEX / Motion Graphic: maintain audio-source/timing ownership separately from visual-art/motion/timeline ownership.
- Anatomi Prompt / AI Prompt Finder: keep prompt-structure work separate from content/reference-to-prompt reconstruction.

## 8. Redistribution-rights evidence refresh (2026-11-23)

The machine-readable companion register is `catalog/source-rights-registry.json`; validate it with `python tools/validate_source_rights.py`.

| Source | Current evidence | Rights conclusion | Distribution gate |
|---|---|---|---|
| SKILL ANALYZER | Public repository, pinned at `c469af7977c9bf6dcb3f5ab7b085a6de20d87004`; no LICENSE/COPYING/NOTICE found | No express redistribution licence located | Blocked until owner adds a licence or grants written permission |
| A.S.F.R.E.E Canonical | Public repository, pinned at `a5eb55db0f6c2c6126a7fbcba645caf44c660c93`; PolyForm Noncommercial 1.0.0, NOTICE and licence strategy present | Noncommercial use only under the current baseline; separate written permission for commercial purpose; branding is separately restricted. The documented historical Apache-2.0 snapshot and prior grants need legal review | Review required; do not treat as unrestricted open source |
| Anatomi Prompt V3 | Private repository, pinned at `06b46b88ed7eddc437792fae715f255cbe4eb13d`; no licence file found | Private access plus no declared licence | Keep private; written owner permission and licence decision required for broader distribution |
| Video Explainer | Public repository, pinned at `f8f8c0f29ff9d851fa75eba764978c24bdd79416`; no LICENSE/COPYING/NOTICE found; Git 4.1.9 vs deployed 4.1.12 | Public visibility is not a redistribution grant | Blocked until licence/permission and source parity are resolved |
| Skill Developer Orchestrator | Public repository, pinned at `9d3c4bc09179ff857df4f3819be83e1847571add`; Apache-2.0 root LICENSE | Conditional redistribution permitted under Apache-2.0 obligations | Rights basis cleared; parity drift, signed artifact and host adapter still block distribution |
| Photo Fixer candidate | Public candidate at `95339901f84cdae861efcebd9820cb2e1efdc27d`; Apache-2.0 root LICENSE; source package incomplete | Apache-2.0 applies to repository contents, not proof of complete plugin package identity | Candidate only; no installable package |
| PVEE candidate | Public candidate at `1ab0c41081ccdbb91cc9dec0a2864acd0de00d54`; Apache-2.0 root LICENSE; source package incomplete | Apache-2.0 applies to repository contents, not proof of complete plugin package identity | Candidate only; no installable package |

The remaining 15 NOT_IDENTIFIED Plugin Creator package identities have no accepted canonical Git source or independent redistribution licence in this baseline. Their USER/PRIVATE platform scope is evidence of access/discoverability, not permission to export or republish. Keep them snapshot-only and private-restricted until each owner approves a source repository, visibility, licence and distribution scope. The parent Apache-2.0 licence must not be used as a substitute for child-plugin permission.

**Current verified baseline (2026-11-25):** 23 identities; 5 pinned official sources; 15 source identities not identified; 2 incomplete candidates; 1 legacy redirect; 0 installable packages. Source pinning and licence evidence are separate gates.


### Added pending source identity: Ponytail Engineering System

- Plugin Creator package: `plugins_6b044f34a5a481919ffc95eadee4383b`
- Verified release: `pluginrel_6b044f37640081918df7f449298d72cf`, version `0.1.0`, scope/discoverability `USER / PRIVATE`
- Canonical Git source: `NOT_IDENTIFIED`; the public upstream Ponytail repository is methodology provenance, not the derivative package's source authority.
- Rights: `NOT_ASSESSED`; no package-level redistribution grant has been established.
- Disposition: keep `snapshot_only`, private and non-installable until owner approval, canonical-source decision and independent licence/redistribution decision are recorded.