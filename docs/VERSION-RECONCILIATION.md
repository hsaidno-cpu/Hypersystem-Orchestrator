# Version Reconciliation and Adoption Policy

## Video Explainer Promkes: current deployment 4.1.12

Verified Plugin Creator evidence:
- Plugin Creator ID: Plugin_2c5d40bf09dc8191baf81bad205c8e41
- Current deployment version: 4.1.12
- Current release ID: pluginrel_6b02a0f630208191b71ad994703aed68
- Created: 2026-11-22T07:59:50.188086Z
- Scope USER; discoverability PRIVATE.
- Current Plugin Creator manifest reports 4.1.12.

Verified GitHub source evidence:
- Repository: https://github.com/promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR
- Pinned source commit: f8f8c0f29ff9d851fa75eba764978c24bdd79416
- GitHub main plugin.json and README: 4.1.9
- Root LICENSE not found.

Earlier installed M00 header showed v4.0.9. That is a stale runtime observation.

**Decision:** adopt 4.1.12 as the verified current deployment. The public source remains 4.1.9 and is classified OFFICIAL_PUBLIC_SOURCE_LAGGING. Do not claim source parity until the complete GitHub source tree, manifest, changelog, tests, references, schemas and rights are reconciled with the private 4.1.12 deployment.

The parent contains the 16 current SKILL.md instruction files from release 4.1.12 at the owner's explicit request, not a full package mirror.

| Plane | Version | Status |
|---|---|---|
| Plugin Creator deployment | 4.1.12 | Verified current |
| GitHub source | 4.1.9 | Official public source, behind |
| Installed skill registry header | v4.0.9 | Older observed header |
| Parent source pin | f8f8c0f29ff9d851fa75eba764978c24bdd79416 | Immutable commit |
