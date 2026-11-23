# Plugin Source and Positioning Alignment Backlog

**Baseline date:** 2026-11-22  
**Parent branch:** ecosystem/foundation-v1-20261122  
**Status convention:** ACCEPTED, IN_PROGRESS, BLOCKED, NOT_STARTED, VERIFIED

## Priority P0 — Source identity and version integrity

### SRC-001 — Locate official source repositories for 13 NOT_IDENTIFIED plugins
**Status:** BLOCKED_ON_SOURCE_EVIDENCE  
**Affected plugins:** Evaluator Team, Master Photo Restoration, GODEX Motion Audio, AI Prompt Finder & Creator, Agent Jailbreak Skill DS, Motion Graphic by arifanara V.01, Plugin Agent Orchestrator, Cortex Workbench, CommandCraft 56, Agent Skills Atlas, AI Workflow Systems Orchestrator, GrowthForge Business OS and People & Business Competency Academy.

The two incomplete candidates (Photo Fixer and PVEE) remain tracked separately. Video Explainer and SDO have already been identified as source repositories and are not part of this NOT_IDENTIFIED list.

**Acceptance**
- Correct owner and repository identity confirmed.
- Plugin Creator ID reconciled with repository manifest.
- README, source tree, manifest, version, changelog, license and required notices inspected.
- Canonical/prototype/mirror/legacy relationship classified.
- Exact source commit recorded.
- Source added as submodule only after provenance and license gates pass.

Do not create repository URLs by slug guessing or adopt name-similar repositories owned by unrelated users.

### SRC-002 — Reconcile Video Explainer public source with current deployment V4.1.12
**Status:** SOURCE_REPOSITORY_IDENTIFIED_DEPLOYMENT_VERIFIED_SOURCE_BEHIND  
**Decision:** Plugin Creator release 4.1.12 is verified by exact plugin ID and release ID; the public GitHub source is pinned at 4.1.9. Installed M00 header v4.0.9 is a stale runtime observation.  
**Blocker:** GitHub source tree/manifest remains 4.1.9; full parity with private 4.1.12 deployment is not established.

**Acceptance**
- Official source and package manifest for V4.1.12 found.
- Release/changelog and source commit confirm that version.
- Versioned instructions and tests are reconciled.
- Parent pin is updated to reviewed source commit.
- Target status may be promoted to RELEASE_VERSION_VERIFIED only after read-back and checks.

### SRC-003 — Confirm Photo-Fixer source package
**Status:** CANDIDATE_INCOMPLETE  
**Evidence:** existing repository root inspected with only README.md and LICENSE. Installed instruction bundle contains 12 skill definitions, but this does not prove they are present in that Git repository.

**Acceptance**
- Full source tree, manifest, skill instructions, tests and version are present and verified.
- If this repository is only a placeholder, decide whether to build it out or designate a different canonical repository.
- Do not promote by repository name alone.


### SRC-004 — Establish canonical source repository and license for People & Business Competency Academy
**Status:** NOT_STARTED  
**Evidence:** Plugin Creator private package 0.1.0 and release ID are read back; the parent repo contains a segregated 9-skill instruction snapshot and source-labelled 100-title catalog. No canonical child Git repository, source version, or independent license decision is yet recorded.

**Acceptance**
- The owner confirms the canonical source repository and its visibility.
- The root manifest, nine skill files, references, schema, tests and changelog are committed there.
- A license and notices appropriate to the source assets are selected and reviewed.
- Package version, source version, instruction content and immutable commit are compared.
- Only after all checks pass may the parent registry move from pending_repository / NOT_IDENTIFIED to an official source classification and submodule pin.

## Priority P1 — Remove residual responsibility overlap

### ALIGN-001 — SKILL ANALYZER vs A.S.F.R.E.E
**Central decision:** general analytical methodology vs technical anatomy of AI plugins/skills/agents and supervised reconstruction.

**Acceptance**
- Analyzer instructions explicitly scope general methods and analytical dossiers.
- A.S.F.R.E.E remains the primary technical forensic case owner.
- Cross-use is a bounded method handoff, not competing M00 ownership.

### ALIGN-002 — Evaluator Team vs SDO
**Central decision:** independent quality judgement vs engineering lifecycle.

**Acceptance**
- Evaluator owns rubrics, evidence, scoring, finding severity and acceptance recommendation.
- SDO owns intake, baseline, accepted-change implementation, regression, source integration and release preparation.
- Evaluator implementation helper is restricted to a delegated bounded patch; SDO remains lifecycle owner.
- Single writer and independent verifier are identified for every source change.

### ALIGN-003 — Anatomi Prompt vs AI Prompt Finder & Creator
**Central decision:** eight-pillar prompt anatomy vs content/reference-to-prompt reconstruction.

**Acceptance**
- Anatomi starts from prompt/task brief and audits/builds its eight pillars.
- Finder starts from source content/reference and derives a prompt approximation/new prompt.
- Finder → Anatomi handoff is explicit and optional.

### ALIGN-004 — Photo Fixer vs Master Photo Restoration
**Central decision:** general photo editing vs restoration-only specialist.

**Acceptance**
- Photo Fixer remains default for normal editing/retouch/compositing.
- Master Photo Restoration is triggered only by old/damaged/degraded/archival restoration.
- Restoration-only negative triggers are reflected in its source instruction package.

### ALIGN-005 — GODEX vs Motion Graphic vs PVEE vs Video Explainer
**Central decision:**
- GODEX owns audio/voice-over provenance, timing and audio post.
- Motion Graphic owns generic visual-first motion production.
- PVEE owns health claims, Fact Lock, safe messaging, governance and audience impact.
- Video Explainer owns technical Promkes production compilation after PVEE approval.

**Acceptance**
- PVEE supplies approved Fact-Locked Production Brief.
- GODEX supplies audio dossier/timing and audio package only when needed.
- Motion Graphic supplies generic visual language/motion work when selected.
- Video Explainer compiles the approved Promkes production package and returns renderer/QA evidence.
- No child source instruction may silently override another domain's canonical decision.

## Priority P1 — Complete source packages and ownership metadata

### PKG-001 — Build or identify source packages for runtime snapshots
**Status:** NOT_STARTED  
For each of the 15 unverified plugins and Photo Fixer candidate, compare the parent runtime snapshot to the eventual canonical source package. Do not treat the snapshot as a published release.

### PKG-002 — License and notice verification
**Status:** PARTIAL  
- A.S.F.R.E.E: PolyForm Noncommercial 1.0.0; preserve required notice.
- SKILL ANALYZER: repository-root LICENSE was not found; do not infer a license.
- Anatomi Prompt: private source; repository-root LICENSE was not found; keep private and do not infer a license.
- Photo-Fixer candidate: Apache-2.0 LICENSE observed.
- Other pending sources: license unknown until source repo is identified.

## Priority P2 — Contract and compatibility testing

### QA-001 — Cross-plugin handoff contract fixtures
**Status:** NOT_STARTED  
Create deterministic producer/consumer fixtures for:
- Analyzer method blueprint → A.S.F.R.E.E forensic case.
- Evaluator findings → SDO change plan.
- Prompt Finder output → Anatomi eight-pillar refinement.
- PVEE Fact-Locked Production Brief → Video Explainer production compiler.
- GODEX audio dossier → Motion Graphic/Video Explainer timing adapter.
- Photo Fixer vs restoration routing negatives.

### QA-002 — Routing collision regression
**Status:** NOT_STARTED  
Test positive and negative trigger cases for every adjacent pair listed in PLUGIN-POSITIONING.md. Record false-positive and false-negative routing.

### QA-003 — Host and runtime compatibility
**Status:** NOT_STARTED  
Static catalog checks are not host activation. Test the target host, product surface, model/provider and plugin versions explicitly. Runtime tests require observable invocation evidence.

## Priority P2 — Continuous synchronization

### SYNC-001 — Snapshot drift check
**Status:** NOT_STARTED  
Compare each runtime snapshot against the installed instruction registry and canonical source when available. Report added/removed/modified skill definitions and route changes.

### SYNC-002 — Source pin freshness
**Status:** NOT_STARTED  
Review submodule updates through PRs, changelogs, immutable SHAs and compatibility checks. Do not update to a branch head without reviewing the source delta.

## Global completion rule

A task is complete only when the source or snapshot, catalog, version/commit provenance, ownership boundary, validation evidence and Notion record agree. A roadmap row marked PLANNED or BLOCKED is not complete merely because its plan exists.
