# Forensic Version Synchronization Audit — Hypersystem Orchestrator

**Audit date:** 2026-11-24  
**Repository:** hsaidno-cpu/Hypersystem-Orchestrator  
**Parent main baseline:** 4fb839a67db79b32f65f82e04c3631ade5d27c9c  
**Scope:** parent registry, five pinned Git sources, 23 Plugin Creator release metadata records, six explicitly requested plugins, and related Notion ecosystem records.  
**Disposition:** CONTROL GAPS CONFIRMED / VERSION METADATA REVERIFIED / CONTENT DRIFT UNRESOLVED / CONTROL PATCH PROPOSED

## 1. Executive findings

The central issue is not that every plugin has the wrong version. The issue is that the ecosystem maintains several independent version planes without a mandatory reconciliation record and without CI enforcing the relationship between the source registry, parent gitlinks, Plugin Creator read-back and generated documentation.

The audit re-read current Plugin Creator release metadata for all **23/23 registered plugin identities**. Every observed package version and current release ID matched the values already stored in catalog/plugins.json; all 23 reported USER / PRIVATE. No Plugin Creator package was modified.

The audit checked the current main head of all five integrated child source repositories. Each current child main SHA exactly matched the source commit pinned in the parent Git tree. The five source manifest versions and manifest blob SHAs were re-read and recorded in catalog/repositories.json. There is no evidence of child branch movement beyond the parent pin at this audit cut-off.

Four source-backed package situations still require separate reconciliation. Equal version strings do not imply instruction parity, and a version gap does not itself justify copying files or republishing a package.

## 2. Current conflict matrix

| Plugin | ChatGPT package | Current release | Canonical Git source | Package/source relation | Instruction parity | Disposition |
|---|---:|---|---:|---|---|---|
| SKILL ANALYZER | 1.0.0 | pluginrel_6af1a98cdbe881918f30895f5af93afc | 1.3.0 | Source ahead | DRIFT_DETECTED (12 package / 20 source; 11/12 shared exact) | Add eight source-only skills, reconcile platform-compatibility and package manifest before private package update |
| A.S.F.R.E.E Canonical | 0.3.2 | pluginrel_6b00fc6b23bc8191a5930132969e52c2 | 0.5.0-rc.1 | Source ahead; RC | DRIFT_DETECTED (13 package / 26 source; 5/13 shared exact) | Add 13 source-only skills and reconcile eight differing shared skills; preserve RC status and PolyForm Noncommercial terms |
| Anatomi Prompt V3.0 | 3.0.0 | pluginrel_6af18ad1d81481919e4c6fa6d512d0ee | 3.0.0 | Version metadata aligned | MATCH (9/9 exact) | Keep current; parity does not grant redistribution rights |
| Skill Developer Orchestrator | 0.1.0 | pluginrel_6afdee10a5688191ad8fc37a9d0d827b | 0.1.0 | Version metadata aligned | DRIFT_DETECTED (0/4 exact) | Do not overwrite either side; choose canonical content with source owner and version decision |
| Video Explainer Promkes | 4.1.12 | pluginrel_6b02a0f630208191b71ad994703aed68 | 4.1.9 | Deployment ahead | DRIFT_DETECTED (16 package / 15 source; 1/11 shared exact) | Five package-only skills, four Git-only skills and ten differing shared skills; full 215-file mapping required before source update |
| Evaluator Team | 1.0.0 | pluginrel_6afdee5a10108191a38e1ee7f84f7524 | Not identified | Platform-only | NOT_APPLICABLE | Preserve private package; establish canonical Git source and rights before claiming parity |
| AI Workflow Systems Orchestrator | 0.2.0 | pluginrel_6b015fe943608191b46d0a439dd4f55e | Not identified | Platform-only | NOT_APPLICABLE | Preserve private package; Git source onboarding and rights review remain separate |

The generated 23-plugin matrix, including every remaining package version, release ID, source state, candidate state, product label and snapshot date, is in docs/CURRENT-VERSION-REGISTRY.md.



## 2A. Supplemental direct content comparison — 2026-11-24

The initial audit compared the files available at the time. A subsequent complete inventory and direct read-back produced more precise parity evidence, now reflected in the catalog and generated matrix:

- **SKILL ANALYZER:** 12 package skills vs 20 Git source skills; 12 shared paths, 11 exact, one differing platform-compatibility skill, eight source-only skills. This confirms that the earlier 11/12 value describes shared-path matching only, not complete package parity.
- **A.S.F.R.E.E:** 13 package skills vs 26 Git source skills; 13 shared paths, five exact and eight differing; 13 Git source-only alias/specialist skills. The source remains 0.5.0-rc.1 under PolyForm Noncommercial 1.0.0.
- **Video Explainer Promkes:** 16 package skills vs 15 Git source skills; 11 shared paths, only one exact, ten differing shared files, five package-only and four Git-only skills. The previous NOT_COMPARED state is superseded by DRIFT_DETECTED. The private package has 215 files, so a skill-only sync would be insufficient.

These comparisons were made by reading the current Plugin Creator release files and exact pinned Git source files; line endings were normalized before exact comparisons. No package files or child Git repositories were modified by this supplemental audit.

## 3. Additional identity and ecosystem findings

- The parent registry has 23 plugin identities. Five child sources are integrated and pinned; two repositories remain incomplete candidates; fifteen identities have no accepted canonical Git source; one identity is a redirect, not a second independent product.
- The parent instruction index records 265 skill definitions. The index and dated instruction snapshots are not equivalent to a live package inventory or proof of exact file parity.
- Motion Graphic V.01 and Plugin Agent Orchestrator 2.0 are display labels; neither substitutes for the package versions 0.2.0 and 2.0.0.
- A.S.F.R.E.E Legacy 1.0.4 applies to the redirect shell only. It is not the canonical A.S.F.R.E.E package version.
- Photo Fixer and PVEE have Git candidates, but those candidates are incomplete and are not canonical package sources.
- All 23 Plugin Creator metadata records re-read during this audit are USER / PRIVATE. No public redistribution or cross-account installation permission is implied.

## 4. Root-cause analysis

### RC-1 — Version authority is split across multiple records

Package version, Plugin Creator release ID, Git manifest version, immutable submodule pin, skill header, display label, compatibility contract and instruction snapshot date are distinct values. Earlier documents grouped some of them under generic version headings. This creates false matches and false mismatches.

### RC-2 — Parent registry did not enforce the actual Git tree pointer

Before this patch, validation checked that repositories.json had a syntactically valid 40-character pin and that .gitmodules named the expected URL. It did not compare that pin with the actual mode-160000 gitlink SHA in the parent commit. A stale or divergent registry could therefore pass that part of validation.

### RC-3 — Documentation was manually maintained

docs/PACKAGE-VERSION-MATRIX.md was dated 2026-11-22, while the parent catalog and plugin identities had advanced. The package matrix did not include every later plugin identity. Manually copying version rows is an avoidable synchronization hazard.

### RC-4 — Metadata freshness was not a CI gate

The previous catalog stored Plugin Creator version and release ID but no per-plugin metadata read-back date. CI could not distinguish a recent observation from an old copied value.

### RC-5 — Version equality was treated too close to content equality

SDO 0.1.0 on both sides has 0/4 files matching. Analyzer has 11/12 matching files. Version labels alone are not a content checksum.

### RC-6 — Private package and source boundaries prevent blind synchronization

Several packages are USER / PRIVATE or have restricted licensing. A public Git repository does not grant publication rights for private package content, and A.S.F.R.E.E 0.5.0-rc.1 is not a stable release.

## 5. Implemented controls in this patch

This patch is limited to the parent repository's registry and static CI. It does not write child sources or deploy Plugin Creator packages.

1. **Per-package metadata observation date:** each of the 23 catalog entries records platform_metadata_observed_at=2026-11-24, following direct current-release metadata read-back.
2. **30-day freshness gate:** validate_catalog.py rejects missing, future-dated or older-than-30-day Plugin Creator metadata observations. The record must be refreshed through an authorized connector.
3. **Actual Gitlink verification:** CI reads each parent tree gitlink with git ls-tree HEAD and compares its SHA with repositories.json pinned_commit.
4. **Source manifest provenance:** each integrated source records manifest path, blob SHA, manifest version, pinned commit and verification date. Catalog source version must correspond to the manifest version.
5. **Generated version matrix:** tools/render_package_version_matrix.py renders the current 23-plugin registry from canonical JSON data. The --check mode makes CI fail when the published document drifts.
6. **Historical-document warning:** the 2026-11-22 package matrix remains available as history and points readers to the current generated registry.
7. **CI regression test:** a unit test verifies generated documentation against source data, and the workflow runs the generated-registry check.

### What this does not automate

GitHub Actions does not have a verified live Plugin Creator metadata API integration in this workflow. The freshness gate checks the recorded read-back date and internal consistency; it does not query Plugin Creator itself. The static gate also does not re-download every private package file or prove host execution. Those checks require authorized read-back and evidence capture.

## 6. Required remediation order

| Priority | Action | Owner | Gate |
|---|---|---|---|
| P0 | Merge version-sync guardrail PR only after exact-head CI and independent human review | Repository owner / reviewer | PR checks + human approval |
| P1 | Resolve Analyzer 1.3.0 to Plugin Creator 1.0.0 through one-file review, package regression and read-back | Analyzer owner | No release until accepted |
| P1 | Resolve SDO 0.1.0 content divergence with source-owner canonical-body decision | SDO owner | Four-file parity + tests |
| P1 | Resolve A.S.F.R.E.E 0.5.0-rc.1 candidate against 0.3.2 package | A.S.F.R.E.E owner / license reviewer | RC acceptance + noncommercial/license review |
| P1 | Map Video Explainer 4.1.12 package contents against Git 4.1.9 and resolve README/skill-header labels | Video Explainer owner | Complete asset/schema/test mapping |
| P2 | Create or accept canonical source repositories for platform-only plugins | Each source owner | Provenance + license + source manifest |
| P2 | Keep Notion version pages as evidence/decision records and link to the current Git registry | HSO knowledge owner | Notion source links + freshness |

## 7. No-go actions

- Do not silently update any USER / PRIVATE Plugin Creator package.
- Do not overwrite the larger SDO runtime instruction body with the shorter public Git copy, or the reverse, without a canonical-body decision.
- Do not promote A.S.F.R.E.E 0.5.0-rc.1 as stable.
- Do not copy private package files into public Git repositories.
- Do not turn incomplete Photo Fixer/PVEE candidates into canonical source pins.
- Do not mark Video Explainer skill parity as MATCH until the package/source file mapping is complete.
- Do not treat a green static CI run as ChatGPT host activation, production readiness or release approval.

## 8. Evidence and related records

- Parent repository baseline: https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/tree/4fb839a67db79b32f65f82e04c3631ade5d27c9c
- Parent source catalog: https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/blob/main/catalog/plugins.json
- Current generated matrix: https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/blob/main/docs/CURRENT-VERSION-REGISTRY.md
- Version governance: https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/blob/main/governance/VERSIONING-AND-RELEASE.md
- Current HSO project control center: https://app.notion.com/p/42299868397f81b3b8a2d4f936f355cb
- Historical migration baseline: https://app.notion.com/p/42199868397f8120823ff7b3da1ced21

**Release disposition: HOLD.** This patch improves detection and traceability. It does not resolve the four content/authority conflicts or authorize any platform release.