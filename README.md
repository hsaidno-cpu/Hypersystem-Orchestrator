# Hypersystem Orchestrator

**A governed hybrid multi-repository ecosystem for independently developed AI plugins, skills, agents and specialized workflow systems.**

[![Catalog validation](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/workflows/catalog-validation.yml/badge.svg)](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/workflows/catalog-validation.yml)

## Mission

Hypersystem Orchestrator is the **central ecosystem repository** for a portfolio of independently maintained AI plugin projects.

Its operating rule is:

> **One plugin, one independent source repository. One ecosystem, one central architecture and governance repository.**

The parent repository owns the ecosystem catalog, architecture boundaries, cross-project contracts, dependency and compatibility policy, governance, integration evidence, and progressive roadmap. Each plugin's own repository remains the canonical source of its implementation, skills, manifests, references, tests and release history.

This is a hybrid multi-repository architecture. It is not a monorepo, does not silently absorb child source code, and does not make plugin capabilities executable merely by listing them.

## What is included now

The registry contains **20 plugin identities** supplied for this ecosystem.

Four verified source repositories are pinned as Git submodules (one public source remains behind its current Plugin Creator deployment):

| Plugin / source | Repository | Visibility | Pinned source |
|---|---|---|---|
| SKILL ANALYZER | [skill-analyzer](https://github.com/hsaidno-cpu/skill-analyzer) | Public | plugins/skill-analyzer |
| A.S.F.R.E.E (Canonical) | [A.S.F.R.E.E](https://github.com/hsaidno-cpu/A.S.F.R.E.E) | Public | plugins/asfree |
| Anatomi Prompt V3.0 — Octa-Prompt | [anatomi-prompt-strategis](https://github.com/hsaidno-cpu/anatomi-prompt-strategis) | Private | plugins/anatomi-prompt-strategis |

The Anatomi Prompt submodule requires permission to the private source repository. Public readers can inspect this parent repository's registry and architecture but cannot clone the private submodule without access.

Other plugin identities are recorded in catalog/plugins.json with explicit source states. They are not represented as migrated source code. The Photo-Fixer repository is currently only a candidate: its root contains a minimal README and a license, not a verified plugin source package.

## The 20 registered plugins

1. Video Explainer Promkes V4.1.12
2. Skill Developer Orchestrator
3. Evaluator Team
4. Master Photo Restoration
5. Anatomi Prompt V3.0 — Octa-Prompt
6. SKILL ANALYZER
7. GODEX Motion Audio
8. AI Prompt Finder & Creator
9. Agent Jailbreak Skill DS
10. Motion Graphic by arifanara V.01
11. Plugin Agent Orchestrator
12. Photo Fixer
13. A.S.F.R.E.E (Canonical)
14. A.S.F.R.E.E Legacy (redirect-only)
15. Cortex Workbench
16. CommandCraft 56
17. Agent Skills Atlas
18. AI Workflow Systems Orchestrator
19. GrowthForge Business OS
20. PVEE Promkes Super Orchestrator

The machine-readable identities and statuses are in [catalog/plugins.json](catalog/plugins.json).

## Repository map

- catalog/ — plugin identity, source repository inventory and lifecycle state.
- plugins/ — pinned Git submodules; source code remains in each independent repository.
- architecture/ — system boundary, responsibility matrix, positioning, routing and integration topology.
- contracts/ — registration schema and standard handoff expectations.
- governance/ — contribution, authority, security, versioning and release rules.
- roadmap/ — progressive stages, source-repository onboarding backlog and evidence-based exit criteria.
- tools/ — repository-local validation scripts.
- tests/ — standard-library checks for catalog integrity.
- .github/workflows/ — automated static catalog checks.
- plugin-instructions/ — one isolated instruction bundle or source pointer per plugin (20 plugin folders, 238 skill records indexed).

## Complete plugin instruction vault

The parent now includes an isolated instruction boundary for every registered plugin:

- 16 complete runtime instruction bundles for packages whose canonical Git source repository has not yet been verified or whose repository is an incomplete candidate.
- 4 official source repositories are pinned as Git submodules; the Video Explainer source pin is explicitly marked behind its current 4.1.12 deployment.
- 1 A.S.F.R.E.E Legacy redirect-only snapshot points to the canonical package.
- The machine-readable index records **238 skill definitions** across the 20 plugin identities.

Start at [plugin-instructions/README.md](plugin-instructions/README.md) and inspect the [instruction snapshot index](catalog/instruction-snapshots.json). Each bundle is kept in its own plugin directory. These snapshots do not merge source ownership or replace the canonical plugin repository. See [snapshot synchronization governance](governance/SNAPSHOT-SYNCHRONIZATION.md).

## Distinct plugin positioning

The normative responsibility boundaries are in [PLUGIN-POSITIONING.md](architecture/PLUGIN-POSITIONING.md) and [ROUTING-AND-NON-DUPLICATION-OVERRIDES.md](architecture/ROUTING-AND-NON-DUPLICATION-OVERRIDES.md). Cross-plugin interfaces are tracked in [catalog/compatibility-matrix.json](catalog/compatibility-matrix.json), and progressive verification is in [COMPATIBILITY-AND-TEST-PLAN.md](docs/COMPATIBILITY-AND-TEST-PLAN.md). Core separations:

- SKILL ANALYZER owns general analytical methodology; A.S.F.R.E.E owns forensic anatomy of AI plugins and controlled reconstruction.
- Evaluator Team owns independent quality judgement; SDO owns the engineering lifecycle and accepted implementation.
- Anatomi Prompt audits/designs prompts using eight Octa-Prompt pillars; AI Prompt Finder & Creator analyzes source content and turns it into a prompt.
- Photo Fixer owns general photo editing; Master Photo Restoration is reserved for restoration of old/damaged photographs.
- GODEX owns audio/voice-over truth and post; Motion Graphic owns general visual-first animation; PVEE owns health communication truth/governance; Video Explainer owns the technical production engine after PVEE approval.

The central catalog includes positive and negative routing triggers for all 20 plugins. Overlap is resolved by a single owner for each final decision and explicit handoffs.

## Version reconciliation

The repository records Plugin Creator package versions separately from canonical Git source versions and embedded skill-header versions. Verified mismatches: Video Explainer deployment 4.1.12 vs Git source 4.1.9 (M00 internal header v4.0.9); SKILL ANALYZER Git source 1.3.0 vs Plugin Creator package 1.0.0; A.S.F.R.E.E Git source 0.5.0-rc.1 vs Plugin Creator package 0.3.2. Anatomi Prompt is aligned at 3.0.0. See [PACKAGE-VERSION-MATRIX.md](docs/PACKAGE-VERSION-MATRIX.md) and [VERSION-RECONCILIATION.md](docs/VERSION-RECONCILIATION.md).

## Source inventory

The connected owner account exposes six repositories; four canonical plugin sources are verified/pinned, including the externally owned official Video Explainer source. Photo-Fixer remains an incomplete candidate, HSMART is a related platform, and 14 plugin source repositories remain unidentified at GitHub-source level. See [SOURCE-REPOSITORY-STATUS.md](docs/SOURCE-REPOSITORY-STATUS.md) and [SOURCE-REPOSITORY-ONBOARDING-BACKLOG.md](roadmap/SOURCE-REPOSITORY-ONBOARDING-BACKLOG.md). An instruction snapshot is not a canonical source repository.

## Architecture principles

1. **Single source of truth:** plugin implementation stays in its own repository; the parent records identity, exact source URL, branch, version and pinned commit.
2. **One owner per concern:** each plugin retains a bounded responsibility; overlapping capabilities are resolved by explicit primary ownership and handoff contracts.
3. **No false execution claims:** discovery, inventory, mapping, submodule pinning, host activation, runtime invocation and production deployment are different lifecycle states.
4. **No dependency cycles:** integrations are directed, contract-based and reviewed before acceptance.
5. **Least privilege:** source repository access, credentials, connector permission and consequential actions remain scoped and explicit.
6. **Reproducibility:** source integrations are pinned to immutable commit SHAs; updating a submodule is a reviewed change.
7. **Independent releases:** child plugin versions are independent from the parent ecosystem version.
8. **Preserve provenance and license:** do not copy source files from a child repository into this parent without a specific need, license/provenance review and approved change.

## Clone

~~~bash
git clone --recurse-submodules https://github.com/hsaidno-cpu/Hypersystem-Orchestrator.git
cd Hypersystem-Orchestrator
~~~

If cloning without submodules:

~~~bash
git clone https://github.com/hsaidno-cpu/Hypersystem-Orchestrator.git
cd Hypersystem-Orchestrator
git submodule update --init --recursive
~~~

The private Anatomi Prompt submodule is available only to users who have access to its private repository. A public clone may therefore require initializing only accessible submodules.

## Validate the ecosystem catalog

Requires Python 3.10+ and no third-party packages.

~~~bash
python tools/validate_catalog.py
python -m unittest discover -s tests -v
~~~

The workflow validates JSON syntax, unique identities, repository references, source-state consistency, alias targets and submodule declarations. These are static repository checks; they do not test whether ChatGPT discovers a plugin, whether an AI host routes correctly, or whether a runtime integration executes.

## Notion project documentation

Read the [Notion project documentation](docs/NOTION-DOCUMENTATION.md) for the detailed ecosystem architecture, plugin inventory, source-state register, responsibility matrix, decisions, roadmap and operational procedures. The detailed Notion knowledge page is a private draft in the connected workspace. GitHub remains authoritative for versioned engineering artifacts; Notion is the project knowledge and navigation layer.

## Status language

- REGISTERED — plugin identity exists in the central catalog.
- SOURCE_REPO_IDENTIFIED — a possible or confirmed source repository has been identified.
- SUBMODULE_PINNED — an exact source commit is linked from this parent.
- SOURCE_VERIFIED — relevant source artifacts were inspected.
- HOST_TESTED — actual activation/routing was tested on a named host and version.
- RUNTIME_VERIFIED — an actual integration/execution was observed and evidenced.
- RELEASED — a specific source release was published.

A repository entry or submodule pin does not imply host testing, runtime verification or release readiness.

## Related but separate platform

[HSMART](https://github.com/hsaidno-cpu/HSMART) is tracked as a related platform repository, not merged into this plugin portfolio. Its platform-level charter, logical planes and KM roadmap remain under its own source of truth. Any future integration must be specified through an explicit interface contract and an approved architecture decision record.

## License and source rights

The parent repository's license governs only material authored in this repository. It does not relicense submodules, plugins or third-party assets. Each child repository's own license and usage terms continue to apply.