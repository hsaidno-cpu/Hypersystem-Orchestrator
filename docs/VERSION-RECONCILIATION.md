# Version Reconciliation and Adoption Policy

## 1. Adopt the highest verified compatible version

“Latest” is determined from authoritative release evidence, not the largest string found in a display name.

Evidence priority:
1. canonical source manifest at the inspected commit;
2. tagged/released source package and changelog;
3. approved release artifact or immutable deployment metadata;
4. package README/version notes;
5. installed skill header;
6. user-provided label or conversation claim.

Compare versions using the package's declared scheme (SemVer when applicable). A higher version is not automatically adoptable if it is incompatible, withdrawn, untested or only a proposed target.

## 2. Video Explainer Promkes reconciliation

Observed evidence on 2026-11-22:
- User-specified plugin identity: Video Explainer Promkes V4.1.12.
- Installed M00 skill header: v4.0.9.
- Canonical GitHub source repository for the V4.1.12 package: not identified.
- Source manifest/changelog for V4.1.12: not available for verification.

Comparison: 4.1.12 is semantically higher than 4.0.9.

**Decision:** select **4.1.12 as the target version** and use that identity in ecosystem planning and source reconciliation. Do not mark the installed/source package as upgraded, released or synchronized until the official 4.1.12 source and manifest are found, the change is applied to the owning repository, and the relevant tests/compatibility checks are read back.

Catalog state:
- release_version: null (source-verified release not established);
- target_version: 4.1.12;
- observed_skill_version: v4.0.9;
- version_reconciliation_status: TARGET_SELECTED_SOURCE_SYNC_PENDING.

## 3. Versions with stronger source evidence

| Plugin | Version | Evidence | State |
|---|---|---|---|
| SKILL ANALYZER | 1.3.0 | README.md and plugin.json in canonical repository | Source verified |
| Anatomi Prompt V3 | 3.0.0 | README.md in private canonical repository | Source verified; repository remains private |
| A.S.F.R.E.E | 0.5.0-rc.1 | plugin/plugin.json and README in canonical repository | Release candidate, not stable release |
| Video Explainer Promkes | Target 4.1.12; observed v4.0.9 | User label vs installed M00 header; source repository absent | Source synchronization pending |

## 4. Labels that are not source-verified versions

- Motion Graphic by arifanara V.01: label retained; not a verified package version.
- Plugin Agent Orchestrator 2.0: skill instruction identifies 2.0, but no source manifest was identified.
- A.S.F.R.E.E Legacy 1.0.4: redirect-shell version only; not the canonical A.S.F.R.E.E version.
- Master Photo Restoration preset v3.0: a preset label, not proof of package release 3.0.0.
- Other plugins: use null for release_version until authoritative evidence is available.

## 5. Synchronization workflow

DISCOVER → READ SOURCE MANIFEST → COMPARE RELEASES → CHECK COMPATIBILITY → SELECT TARGET → UPDATE SOURCE REPOSITORY → RUN TESTS → UPDATE PARENT PIN → UPDATE CATALOG → VERIFY READ-BACK

A catalog target-version change alone is not a package upgrade. The parent must never claim that the source plugin was updated simply because its intended version changed.
