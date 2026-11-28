# Video Explainer — Version and Source Synchronization Decision
**Audit:** 26 November 2026 · **Plugin Creator ID:** Plugin_2c5d40bf09dc8191baf81bad205c8e41 · **Release:** pluginrel_6b02a0f630208191b71ad994703aed68

## Version authorities

| Plane | Version | Evidence | Decision |
|---|---:|---|---|
| Plugin Creator manifest | **4.1.12** | Current private package manifest/read-back | Canonical deployed package release |
| Private README title | 4.1.11 | Current package README | Stale title |
| Private CHANGELOG latest section | 4.1.11 | Current package CHANGELOG | Missing 4.1.12 entry |
| Public Git manifest and README | 4.1.9 | public repo at f8f8c0f29ff9d851fa75eba764978c24bdd79416 | Official source is behind |
| M00 procedure header | 4.0.9 | skills/video-explainer-promkes/SKILL.md | Historical procedure header, not package authority |
| Engine parity/report docs | 4.1.5 | docs/engine-parity-status.md and reports/release-status.json | Historical report, not current release proof |
| Old runtime observation | 4.0.9 | Historical registry | Historical telemetry only |

**Canonical decision:** current deployed package version = 4.1.12. Public Git source remains 4.1.9. README/CHANGELOG are stale at 4.1.11; do not relabel historical audits. Reconcile them in an owner-approved private package release.

## Direct skill source/package comparison

Public Git source has 15 top-level SKILL.md files; private 4.1.12 package has 16. Every source skill was compared with its proposed package counterpart. Exactly 1/15 is byte-identical; 14/15 differ.

| Git 4.1.9 source skill | Private 4.1.12 package counterpart | Byte-identical | Finding |
|---|---|---:|---|
| ai-video-reference-engineering | prompt-reference-video-engineering | No | Renamed role candidate; semantic review required |
| animation-motion-design | animation-motion-design | No | Content drift |
| audience-campaign-strategy | audience-campaign-strategy | No | Content drift |
| continuity-guardian | continuity-guardian | No | Content drift |
| conversation-release-audit | conversation-release-audit | No | Content drift |
| editing-postproduction | renderer-code-engineering | No | Rename/positioning change; semantic review required |
| health-evidence-safety-auditor | health-evidence-safety-auditor | No | Content drift |
| master-orchestrator | video-explainer-promkes | No | Master role rename/expanded responsibility; semantic review required |
| quality-assurance-controller | quality-assurance-controller | No | Content drift |
| social-accessibility-distribution | social-accessibility-distribution | **Yes** | Exact byte match |
| source-asset-intelligence | source-asset-intelligence | No | Content drift |
| story-screenplay-architect | story-screenplay-architect | No | Content drift |
| storyboard-cinematography | storyboard-cinematography | No | Content drift |
| visual-identity-art-direction | visual-identity-art-direction | No | Content drift |
| voice-sound-design | voice-audio-intelligence | No | Rename/positioning change; semantic review required |

Package-only skill: executable-gate-engine. This may represent a newly extracted capability; its source scripts/contracts and changelog provenance must be traced. These 14 diffs are not automatically regressions; they are unresolved semantic changes until compared against acceptance cases and behavior.

## Full-package scope
The private Plugin Creator inventory has 215 paths across three pages. It includes manifests, README/CHANGELOG, demo assets and MP4, guides, schemas, scripts, 16 skills, tests and reports. The public source tree has 177 blob paths. The skill comparison does not prove package-level parity.

The complete sync must perform bidirectional path reconciliation and classify every path as identical, modified, source-only, package-only, renamed, generated or intentionally excluded. Binary paths need byte hashes. Package-only material stays private unless explicitly approved for publication.

## Clean version model
Keep these fields distinct: package_version; package_release_id; source_version; source_commit; source_tree_sha; package_manifest_version; documentation_version; procedure_version; historical_audit_version. No inference from package version to source tag. README, CHANGELOG, root manifest, package release and current implementation report must agree for a given release; historical reports retain their actual audited versions.

## Next safe synchronization sequence
1. Pin release 4.1.12 and source SHA 4.1.9.
2. Compare all 215 package paths against all 177 source paths, including binary hashes.
3. Resolve the 15 skill mappings and executable-gate-engine provenance.
4. Review every changed procedure for S02 Fact Lock, MCG, S14, R0-R3, security, negative triggers and human approval.
5. Owner approves private source reconciliation and rights/publication scope.
6. Update README/CHANGELOG in a private 4.1.12 package release; keep historical reports historical.
7. Only then create a source PR and, after review/tests, publish an appropriate new source tag. No 4.1.12 public source is currently proven.

**Status:** VERSION_DRIFT_CONFIRMED · SOURCE_PACKAGE_PARITY_PARTIAL · FULL_PACKAGE_SYNC_NOT_STARTED · RIGHTS_NOT_CLEARED · RUNTIME_NOT_VERIFIED.
