# Hypersystem Orchestrator

**A governed hybrid multi-repository ecosystem for independently developed AI plugins, skills, agents and specialized workflow systems.**

[![Catalog validation](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/workflows/catalog-validation.yml/badge.svg)](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/workflows/catalog-validation.yml)

## Mission

Hypersystem Orchestrator is the **central ecosystem repository** for a portfolio of independently maintained AI plugin projects.

Its operating rule is:

> **One plugin, one independent source repository. One ecosystem, one central architecture and governance repository.**

The parent repository owns the ecosystem catalog, architecture boundaries, cross-project contracts, dependency and compatibility policy, governance, distribution eligibility, platform adapter contracts and progressive roadmap. Each plugin's own repository remains the canonical source of its implementation, skills, manifests, references, tests and release history.

This is a hybrid multi-repository architecture. It is not a monorepo, does not silently absorb child source code, and does not make plugin capabilities executable merely by listing them.

## What is included now

The registry contains **24 plugin identities** supplied for this ecosystem.

Five verified official plugin source repositories are pinned as Git submodules:

| Plugin / source | Repository | Visibility | Pinned source |
|---|---|---|---|
| SKILL ANALYZER | [skill-analyzer](https://github.com/hsaidno-cpu/skill-analyzer) | Public | plugins/skill-analyzer |
| A.S.F.R.E.E (Canonical) | [A.S.F.R.E.E](https://github.com/hsaidno-cpu/A.S.F.R.E.E) | Public | plugins/asfree |
| Anatomi Prompt V3.0 — Octa-Prompt | [anatomi-prompt-strategis](https://github.com/hsaidno-cpu/anatomi-prompt-strategis) | Private | plugins/anatomi-prompt-strategis |
| Video Explainer Promkes | [VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR](https://github.com/promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR) | Public | plugins/video-explainer-promkes (source 4.1.9; deployment 4.1.12) |
| Skill Developer Orchestrator | [SPDO](https://github.com/promkespkmbinuang-coder/SPDO) | Public | plugins/skill-developer-orchestrator (0.1.0) |

The other plugin identities remain recorded with explicit source states. Instruction snapshots and candidate repositories are not treated as canonical distributable source packages.

## The 24 registered plugins

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
18. People & Business Competency Academy
19. AI Workflow Systems Orchestrator
20. GrowthForge Business OS
21. PVEE Promkes Super Orchestrator
22. Progressive Roadmap Evaluator (PRE)
23. Ponytail Engineering System
24. Executive Workday Orchestrator

The machine-readable identities and statuses are in [catalog/plugins.json](catalog/plugins.json).

## Distribution and cross-platform installation

The ecosystem supports three selection modes at the contract level:

- **Single:** select exactly one plugin.
- **Multi:** select two or more explicit plugins.
- **Full Suite:** dynamically resolve every package currently eligible for the selected platform, not every catalog identity.

The distribution registry separates package readiness from source registration. It explicitly excludes snapshot-only packages, incomplete candidates, rights-uncleared packages and legacy redirects. A bundle is an installation envelope; it does not merge plugin source, ownership, permissions or versions.

The current change adds:
- [Distribution eligibility registry](catalog/distribution-registry.json)
- [Platform adapter registry](catalog/platform-registry.json)
- [Distribution architecture](docs/DISTRIBUTION-ARCHITECTURE.md)
- [Installation and runtime hierarchy](docs/INSTALLATION-AND-RUNTIME-HIERARCHY.md)
- [Cross-platform adapter matrix](docs/PLATFORM-ADAPTER-MATRIX.md)
- [Package and installation contracts](contracts/)

**Implementation status:** this is a versioned architecture, schema, static eligibility registry and dry-run resolver baseline. No production installer, remote MCP gateway or platform adapter is implemented by this change. At the initial baseline, zero plugin packages are marked installable. The resolver returns blockers rather than pretending that registered identities or instruction snapshots are ready for installation.

Run:

~~~bash
python tools/validate_distribution.py
python tools/resolve_distribution.py --manifest distribution/manifests/manifest.example.json
~~~

The resolver is plan-only. It does not download, install, enable, authorize or execute plugins. See [distribution/README.md](distribution/README.md) for the operational boundary.

## Ponytail Engineering System

[Ponytail integration and ownership contract](docs/PONYTAIL-ENGINEERING-INTEGRATION.md). The package is USER/PRIVATE; only its metadata pointer is kept here. The upstream Ponytail repository is cited as methodology provenance, not as the derivative package's canonical source.

## Repository map

- catalog/ — plugin identity, source inventory, compatibility, distribution eligibility and platform adapter registry.
- plugins/ — pinned Git submodules; source code remains in each independent repository.
- plugin-instructions/ — isolated instruction bundles or source pointers; snapshots do not become distributable source.
- distribution/ — dry-run installation manifests and package selection examples.
- contracts/ — registration, handoff, package, installation, entitlement and lock schemas.
- architecture/ — system boundary, responsibility matrix, positioning, routing, integration topology and the ecosystem control-plane operating contract.
- governance/ — contribution, authority, security, versioning, release and snapshot rules.
- roadmap/ — progressive stages, source-repository onboarding backlog and evidence-based exit criteria.
- tools/ — repository-local validators, dry-run resolver, plan compiler and supervised sandbox runtime.
- tests/ — catalog/distribution/eligibility regressions, C2/C3 contract assurance, planning and runtime recovery/security tests.
- .github/workflows/ — automated static validation.

## Plugin instruction registry

The parent maintains an isolated instruction boundary for every registered plugin. The machine-readable index records **265 skill definitions** across 24 plugin identities. These snapshots do not merge source ownership or replace canonical plugin repositories. Start at [plugin-instructions/README.md](plugin-instructions/README.md) and inspect [catalog/instruction-snapshots.json](catalog/instruction-snapshots.json).

## Distinct plugin positioning

The normative responsibility boundaries are in [PLUGIN-POSITIONING.md](architecture/PLUGIN-POSITIONING.md) and [ROUTING-AND-NON-DUPLICATION-OVERRIDES.md](architecture/ROUTING-AND-NON-DUPLICATION-OVERRIDES.md). Cross-plugin interfaces are tracked in [catalog/compatibility-matrix.json](catalog/compatibility-matrix.json), and progressive verification is in [COMPATIBILITY-AND-TEST-PLAN.md](docs/COMPATIBILITY-AND-TEST-PLAN.md).

- SKILL ANALYZER owns general analytical methodology; A.S.F.R.E.E owns forensic anatomy of AI plugins and controlled reconstruction.
- People & Business Competency Academy owns the development and evidence-based transfer of human People/Business Skills; Agent Skills Atlas owns AI capability inventory, while GrowthForge owns business-domain decisions and deliverables.
- Evaluator Team owns independent quality judgement; SDO owns the engineering lifecycle and accepted implementation.
- Anatomi Prompt audits/designs prompts using eight Octa-Prompt pillars; AI Prompt Finder & Creator analyzes source content and turns it into a prompt.
- Executive Workday Orchestrator owns workday-level task, project, meeting, communication, focus and review coordination; it delegates generic workflow architecture to WSO, agent-product lifecycle to Plugin Agent Orchestrator, source engineering to SDO, independent judgement to Evaluator Team and universal prompt architecture to Anatomi Prompt.
- Photo Fixer owns general photo editing; Master Photo Restoration is reserved for restoration of old/damaged photographs.
- GODEX owns audio/voice-over truth and post; Motion Graphic owns general visual-first animation; PVEE owns health communication truth/governance; Video Explainer owns the technical production engine after PVEE approval.

## Version reconciliation

Plugin Creator package versions, canonical Git source versions and embedded skill-header versions remain distinct. Verified mismatches include Video Explainer deployment 4.1.12 versus source 4.1.9, SKILL ANALYZER source 1.3.0 versus package 1.0.0, and A.S.F.R.E.E source 0.5.0-rc.1 versus package 0.3.2. SDO's package version matches at 0.1.0 but instruction content drift remains unresolved. See [PACKAGE-VERSION-MATRIX.md](docs/PACKAGE-VERSION-MATRIX.md) and [VERSION-RECONCILIATION.md](docs/VERSION-RECONCILIATION.md).

## Source inventory

Five official source repositories are pinned, two candidate/incomplete sources are tracked, fourteen plugin identities remain NOT_IDENTIFIED and one identity is a legacy redirect. See [SOURCE-REPOSITORY-STATUS.md](docs/SOURCE-REPOSITORY-STATUS.md). An instruction snapshot is not a canonical source repository.

## Skill migration audit

The date-bound, evidence-backed migration baseline is documented in [SKILL-MIGRATION-FORENSIC-BASELINE-2026-11-23.md](docs/SKILL-MIGRATION-FORENSIC-BASELINE-2026-11-23.md). It separates catalog coverage, canonical source onboarding, source-content parity, compatibility testing and distribution readiness. An indexed instruction is not proof of canonical source synchronization.

The ecosystem-level operating model, route arbitration, authority boundaries and execution gates are specified in [SUPER-ORCHESTRATOR-CONTROL-PLANE.md](architecture/SUPER-ORCHESTRATOR-CONTROL-PLANE.md). This is a design/control-plane contract, not a claim that a hosted runtime or automatic plugin dispatcher is deployed. The portable eight-pillar operating instruction is [HSO-SUPER-ORCHESTRATOR-MASTER-PROMPT.md](prompts/HSO-SUPER-ORCHESTRATOR-MASTER-PROMPT.md); it remains a draft until target-host testing and owner release.

A bounded [plan-only workflow planner](docs/HSO-PLAN-ONLY-ORCHESTRATOR.md) now validates declared owners, capability states, authority, approvals and DAG dependencies. It returns an ordered plan and blockers; it does not invoke plugins or dispatch work.

A controlled [Super-Orchestrator runtime](docs/HSO-SUPER-ORCHESTRATOR-RUNTIME.md) probes registered capabilities, arbitrates one primary owner plus bounded specialists, enforces policy, executes dependency-ordered work, verifies actual targets and records a hash-chained audit. The always-on CI path proves the sandbox runtime only. A separate P0 Remote MCP adapter for one SKILL ANALYZER tool is registered on the PR branch, but its public endpoint/OIDC configuration is not yet verified; no live plugin invocation is claimed. Generic plugin dispatch, generic multi-server MCP and staging/production remain blocked.

The next step is a deliberately narrow [P0 Codex CLI host invocation pilot](docs/HSO-P0-CODEX-SKILL-INVOCATION-PILOT.md): one pinned SKILL ANALYZER source, one Codex CLI host, one approval-gated synthetic task and one invocation receipt. Its live paid call is manual-only and remains NOT_RUN until the protected default-branch workflow is explicitly approved; it does not enable generic plugin dispatch.

## Architecture principles

1. **Single source of truth:** plugin implementation stays in its own repository; the parent records exact source URL, branch, version and pinned commit.
2. **One owner per concern:** each plugin retains a bounded responsibility; overlapping capabilities are resolved by explicit primary ownership and handoff contracts.
3. **No false execution claims:** discovery, inventory, mapping, submodule pinning, installation, host activation, runtime invocation and production deployment are different lifecycle states.
4. **No dependency cycles:** integrations are directed, contract-based and reviewed before acceptance.
5. **Least privilege:** source repository access, credentials, connector permission and consequential actions remain scoped and explicit.
6. **Reproducibility:** source integrations are pinned to immutable commit SHAs; updates are reviewed changes.
7. **Independent releases:** child plugin versions are independent from the parent ecosystem version.
8. **Preserve provenance and license:** child licenses and terms continue to apply; the parent license does not relicense them.

## Validate

Requires Python 3.10+. Catalog and distribution validation and the plan-only planner use the Python standard library. Contract/regression tests also use the pinned test dependencies in `requirements-test.txt`.

~~~bash
python -m pip install -r requirements-test.txt
python tools/validate_catalog.py
python tools/validate_distribution.py
python tools/plan_hso_workflow.py examples/hso-workflow-plan.example.json
python tools/hso_super_orchestrator.py discover --output /tmp/hso-capabilities.json
python tools/hso_super_orchestrator.py run examples/hso-runtime-execution.example.json --workspace /tmp/hso-target --ledger /tmp/hso-ledger.sqlite --audit /tmp/hso-audit.jsonl --receipt /tmp/hso-receipt.json
python tools/hso_super_orchestrator.py verify-audit /tmp/hso-audit.jsonl
python -m unittest discover -s tests -v
~~~

The example intentionally reports blockers for capability states marked `NOT_CHECKED`; the planner exits successfully only because the declared plan is structurally valid. A blocker is not silently promoted to readiness. Static CI checks and plan generation do not prove that ChatGPT, Claude, Gemini or Copilot can install or run a plugin. Host activation and real runtime invocation require separate evidence for each target.

## Notion project documentation

Read [docs/NOTION-DOCUMENTATION.md](docs/NOTION-DOCUMENTATION.md) for the Notion knowledge hub. GitHub remains authoritative for versioned engineering artifacts, schemas, tests, governance files and release history; Notion explains the architecture, decisions and operating procedures.

## Related but separate platform

[HSMART](https://github.com/hsaidno-cpu/HSMART) is tracked as a related platform repository, not merged into this plugin portfolio. Any future integration requires an explicit interface contract and approved architecture decision record.

## License and source rights

The parent repository's license governs only material authored in this repository. It does not relicense submodules, plugins or third-party assets. Each child repository's own license and usage terms continue to apply.
