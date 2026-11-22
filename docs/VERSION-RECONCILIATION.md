# Version Reconciliation and Adoption Policy

## 1. Version authority

The highest version is adopted from authoritative release evidence, not from the largest string in a display name. Distinguish:
1. canonical Git source manifest/version at an immutable commit;
2. current Plugin Creator release metadata and manifest;
3. tagged source package/changelog;
4. installed skill header;
5. user-provided version label.

A deployment and a source repository can be on different versions. The catalog records them separately until source parity is proven.

## 2. Video Explainer Promkes — current deployment 4.1.12

### Verified Plugin Creator deployment

- Exact Plugin Creator ID: Plugin_2c5d40bf09dc8191baf81bad205c8e41
- Current deployed version: **4.1.12**
- Current release ID: pluginrel_6b02a0f630208191b71ad994703aed68
- Release created: 2026-11-22T07:59:50.188086Z
- Scope: USER
- Discoverability: PRIVATE
- Current Plugin Creator plugin.json manifest reports 4.1.12.

### Verified public GitHub source

- Repository: https://github.com/promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR
- Pinned commit: f8f8c0f29ff9d851fa75eba764978c24bdd79416
- GitHub main plugin.json: 4.1.9
- GitHub README: V4.1.9
- Root LICENSE: not found during inspection.

### Older runtime registry observation

The connected installed M00 header previously showed v4.0.9. This is an older runtime observation, not the current Plugin Creator deployment.

### Decision

**4.1.12 is adopted as the verified current Plugin Creator deployment.** The public GitHub source remains 4.1.9 and is classified OFFICIAL_PUBLIC_SOURCE_LAGGING. Do not claim source parity until the complete source tree, manifest, changelog, tests, references, schemas and licensing/provenance are reconciled with the private 4.1.12 deployment.

The parent contains the 16 current SKILL.md instruction files from Plugin Creator release 4.1.12 at the owner's explicit request. This is an instruction-only snapshot, not a complete package mirror. Binary assets and unrelated runtime materials are excluded.

| Version plane | Version | Status |
|---|---|---|
| Plugin Creator deployment | 4.1.12 | Verified current |
| Public GitHub source | 4.1.9 | Official source, behind deployment |
| Installed skill registry header | v4.0.9 | Older runtime observation |
| Parent Git submodule pin | f8f8c0f29ff9d851fa75eba764978c24bdd79416 | Immutable source commit |

## 3. Other source-backed versions

| Plugin | Version | Evidence | Status |
|---|---|---|---|
| SKILL ANALYZER | 1.3.0 | README/package metadata at canonical source | Source verified |
| Anatomi Prompt V3 | 3.0.0 | README at private canonical source | Source verified, private |
| A.S.F.R.E.E | 0.5.0-rc.1 | plugin/plugin.json and README | Release candidate, not stable |
| Video Explainer Promkes | Plugin Creator 4.1.12; Git source 4.1.9 | Current release and public source manifest | Deployment verified; source lagging |

## 4. Labels that are not source-verified releases

- Motion Graphic by arifanara V.01 is a label, not a verified package version.
- Plugin Agent Orchestrator 2.0 is an instruction label; its source manifest is not identified.
- A.S.F.R.E.E Legacy 1.0.4 belongs to the redirect shell only.
- Master Photo Restoration preset v3.0 is a preset label, not proof of package version 3.0.0.
- Other package release versions remain unknown until authoritative evidence is available.
