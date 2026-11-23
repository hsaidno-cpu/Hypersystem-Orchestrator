# Plugin Package Version Matrix and Adoption Decisions

**Inventory date:** 2026-11-22  
**Authority:** exact Plugin Creator IDs/current release metadata plus inspected canonical Git source manifests where available.

## 1. Version planes

Keep these distinct:
1. Plugin Creator package version — current deployed package metadata and release ID.
2. Canonical Git repository version — version in the source manifest at a pinned commit.
3. Internal skill header version — label embedded in a skill instruction; not necessarily the package version.
4. Product/display label — e.g. V.01 or 2.0; may not be SemVer.
5. Parent submodule SHA — exact source commit; immutable provenance, not a semantic version.

An instruction snapshot records what was visible in the Plugin Creator release at capture time. It does not change package version, source version or deployment state.

## 2. Current version matrix

| Plugin | Plugin Creator package | Git source version | Current classification | Adoption decision |
|---|---:|---:|---|---|
| Video Explainer Promkes | 4.1.12 | 4.1.9 | Official public source, behind deployment | Keep deployed target 4.1.12; source sync pending. M00 header v4.0.9 is an internal skill version and must not be overwritten mechanically. |
| Skill Developer Orchestrator | 0.1.0 | 0.1.0 | Official public source, signed commit; instruction-content drift | Manifest/package versions match and source is pinned at 9d3c4bc09179ff857df4f3819be83e1847571add. However, Plugin Creator master SKILL.md (23,651 chars) differs from Git master SKILL.md (10,573 chars). Keep content parity DRIFT_DETECTED until a reviewed reconciliation is completed. |
| Evaluator Team | 1.0.0 | Not identified | Platform release only | Preserve 1.0.0 as platform metadata; source repo onboarding pending. |
| Master Photo Restoration | 1.0.0 | Not identified | Platform release only | Preserve 1.0.0 as platform metadata; source repo onboarding pending. |
| Anatomi Prompt V3 — Octa-Prompt | 3.0.0 | 3.0.0 | Source and platform match | Adopt 3.0.0; private canonical source remains authoritative. |
| SKILL ANALYZER | 1.0.0 | 1.3.0 | Source ahead of platform package | Adopt Git source baseline 1.3.0 in parent; platform package deployment is a separate update and has not been republished here. |
| GODEX Motion Audio | 2.0.0 | Not identified | Platform release only | Preserve 2.0.0; source repo onboarding pending. |
| AI Prompt Finder & Creator | 1.0.0 | Not identified | Platform release only | Preserve 1.0.0; source repo onboarding pending. |
| Agent Jailbreak Skill DS | 0.2.0 | Not identified | Platform release only | Preserve 0.2.0; source repo onboarding pending. |
| Motion Graphic by arifanara V.01 | 0.2.0 | Not identified | Platform release only | Treat V.01 as product label; use 0.2.0 as current package version. |
| Plugin Agent Orchestrator | 2.0.0 | Not identified | Platform release only | Preserve 2.0.0; do not infer source version from older display labels. |
| Photo Fixer | 1.0.0 | Candidate repo incomplete | Candidate source only | Preserve 1.0.0; hsaidno-cpu/Photo-Fixer is not accepted as complete source. |
| A.S.F.R.E.E Canonical | 0.3.2 | 0.5.0-rc.1 | Source ahead of platform package | Adopt 0.5.0-rc.1 as the highest verified source candidate; explicitly retain RC status. Do not label it stable. |
| A.S.F.R.E.E Legacy | 1.0.4 | Not applicable | Legacy redirect | 1.0.4 applies only to redirect shell; canonical version comes from A.S.F.R.E.E. |
| Cortex Workbench | 1.0.0 | Not identified | Platform release only | Preserve 1.0.0; source repo onboarding pending. |
| CommandCraft 56 | 0.1.0 | Not identified | Platform release only | Preserve 0.1.0; source repo onboarding pending. |
| Agent Skills Atlas | 0.3.1 | Not identified | Platform release only | Preserve 0.3.1; source repo onboarding pending. |
| AI Workflow Systems Orchestrator | 0.2.0 | Not identified | Platform release only | Preserve 0.2.0; source repo onboarding pending. |
| GrowthForge Business OS | 1.1.1 | Not identified | Platform release only | Preserve 1.1.1; source repo onboarding pending. |
| PVEE Promkes Super Orchestrator | 2.0.2 | Unknown | Candidate source incomplete | Preserve 2.0.2 as Plugin Creator package metadata. Its declared CL-VAEPPC repository is an incomplete legacy/source shell with no current manifest or skill tree; no Git source version can be asserted. |

## 3. Three substantive mismatches

### 3.1 Video Explainer Promkes

- Exact Plugin Creator ID: Plugin_2c5d40bf09dc8191baf81bad205c8e41
- Current deployment version: 4.1.12
- Current release ID: pluginrel_6b02a0f630208191b71ad994703aed68
- Official public Git source: promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR
- Pinned Git SHA: f8f8c0f29ff9d851fa75eba764978c24bdd79416
- Git source version: 4.1.9
- Embedded M00 skill header: v4.0.9

**Decision:** 4.1.12 remains the highest verified deployed package. GitHub is an official but lagging source. The M00 internal skill header is a separate version plane. Complete source-tree parity, rights/license review, manifest, tests, references and schemas before claiming the Git repository has reached 4.1.12.

### 3.2 SKILL ANALYZER

- Plugin Creator package version: 1.0.0, release pluginrel_6af1a98cdbe881918f30895f5af93afc
- Public Git source version: 1.3.0, commit c469af7977c9bf6dcb3f5ab7b085a6de20d87004

**Decision:** use Git source 1.3.0 as the parent source baseline. The Plugin Creator deployment metadata is behind and is not silently relabeled. Republishing/updating the platform package requires its own source/package parity and verification.

### 3.3 A.S.F.R.E.E Canonical

- Plugin Creator package version: 0.3.2, release pluginrel_6b00fc6b23bc8191a5930132969e52c2
- Public Git source version: 0.5.0-rc.1, commit a5eb55db0f6c2c6126a7fbcba645caf44c660c93
- Source license: PolyForm Noncommercial 1.0.0

**Decision:** source 0.5.0-rc.1 is the highest verified source candidate, but it is a release candidate. The platform package remains 0.3.2 until a separately authorized and validated platform update. Never call 0.5.0-rc.1 a stable release.

## 4. Adoption policy

- Prefer the highest authoritative version within its own plane, not the largest version string across unrelated planes.
- A verified Git source version is the parent source baseline; a current Plugin Creator package is the host deployment baseline.
- If Git source is ahead, mark SOURCE_AHEAD_OF_PLATFORM; do not claim the platform is updated.
- If deployment is ahead of source, mark DEPLOYMENT_AHEAD_OF_SOURCE; do not fabricate source parity.
- If the version is only a product label or skill header, retain it as such and do not coerce it into SemVer.
- If the source repository is unidentified, the platform package version may be recorded but the source version remains null.
- A release candidate remains a release candidate even if it is the highest known version.
- Every update must include package release ID, source commit, manifest path, changelog/test evidence and date.

## 5. Next synchronization sequence

1. Bring SKILL ANALYZER Plugin Creator source/package into parity with canonical Git source 1.3.0, after package read-back and regression.
2. Bring A.S.F.R.E.E Plugin Creator package into parity with canonical source 0.5.0-rc.1 only after release candidate acceptance and the platform package has been reviewed.
3. Synchronize the Video Explainer public Git repository from 4.1.9 to deployment 4.1.12 only after complete source, asset, schema, test and license reconciliation with the current deployment.
4. Reconcile the other 14 GitHub source gaps before publishing parent source pins.

No Plugin Creator package was republished by this parent-repository change.


## 4. Additional source discovery (2026-11-22)

### Skill Developer Orchestrator

- Canonical repository: promkespkmbinuang-coder/SPDO
- Manifest: plugin.json, package skill-developer-orchestrator, version 0.1.0
- Plugin Creator ID: Plugin_a5294996e38c8191b8e20b2d9f61447a; current package 0.1.0
- Pinned commit: 9d3c4bc09179ff857df4f3819be83e1847571add
- Commit signature: verified by GitHub
- LICENSE: Apache-2.0
- The master skill, references, README, manifest and acceptance-case specification are present.

**Decision:** adopt 0.1.0 as source and platform version. No version mismatch remains for SDO. Acceptance cases are specifications; their presence is not evidence of target-host runtime tests.

### PVEE Promkes Super Orchestrator

- Current Plugin Creator manifest explicitly declares promkespkmbinuang-coder/CL-VAEPPC.
- Observed main commit: 1ab0c41081ccdbb91cc9dec0a2864acd0de00d54, signature verified.
- Observed tree: README.md, Apache-2.0 LICENSE and an empty one-byte .claude-plugin marker only.
- Current PVEE package 2.0.2 has no matching source manifest or complete skill tree in that repository.

**Decision:** retain as CANDIDATE_INCOMPLETE. Do not infer a Git source version, create a submodule or equate the historical README's Video Explainer V3.0 with current PVEE 2.0.2.


## SDO instruction-content parity exception

The Plugin Creator release and public Git repository both identify version 0.1.0, but a direct normalized comparison of the master SKILL.md files failed. The current Plugin Creator body is 23,651 characters; the Git source body is 10,573 characters. These are not interchangeable copies.

**Decision:** retain the official Git repository submodule and retain the Plugin Creator current-release snapshot separately. Mark source_instruction_parity_status as DRIFT_DETECTED and source_sync_status as SOURCE_INSTRUCTION_DRIFT_DETECTED. Do not overwrite either body until the SDO source owner reviews the difference, chooses the intended canonical content, increments version if required, and verifies the package read-back.
