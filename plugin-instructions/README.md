# Plugin Instruction Vault

This directory stores every plugin instruction set in an isolated boundary. It is a mirror/inspection layer, **not a merger of plugin ownership**.

## Structure

- Each plugin has its own child directory. A bundle never mixes instructions from other plugins.
- INSTRUCTIONS-BUNDLE.md contains the complete skill instructions retrieved from the installed plugin skill registry at the recorded snapshot date.
- Canonical source-backed plugins are represented by source pointers to the exact submodule/commit, not by copied instructions.
- A legacy compatibility plugin is stored only as a redirect snapshot and points to its canonical plugin.

## Source authority

| Source class | Authority | How to update |
|---|---|---|
| OFFICIAL_SOURCE_SUBMODULE | Child repository pinned to exact commit | Review child source, then update parent submodule SHA |
| RUNTIME_INSTRUCTION_SNAPSHOT | Snapshot of the currently installed skill package; not a release/source authority | Re-capture complete skill files and compare per-skill digests |
| CANDIDATE_INCOMPLETE | Repository exists but is not a complete/verified package | Do not treat as official source until provenance, manifest and content pass |
| LEGACY_REDIRECT | Migration/redirect only | Never develop as a second canonical product |
| NOT_IDENTIFIED | No verified repository source found | Keep snapshot separated and record the gap |
| MIRROR | A copy of another source repository | Never treat as canonical; preserve upstream URL and commit |

## Why snapshots live here

The ecosystem owner requested the complete instructions to be visible from the parent repository while keeping each plugin independently maintainable. Snapshots provide centralized inspection, search and documentation without changing source ownership.

## Non-negotiable rules

1. Do not edit a snapshot and call it a plugin source update. Edit the canonical plugin repository first.
2. Record plugin key, skill URI, source repository, commit/version, capture date, license/provenance, content digest and snapshot status.
3. If a canonical source repository later appears, compare it with the runtime snapshot, reconcile drift, then declare the repository source authoritative.
4. Keep each plugin's license and access boundary. The parent Apache-2.0 license does not override a child plugin license or grant permission to redistribute private content.
5. Do not publish private plugin material in this public parent repository without explicit authorization.
6. A snapshot does not prove ChatGPT host activation, tool execution, runtime behavior or release readiness.

## Synchronization pipeline

DISCOVER → IDENTIFY → CLASSIFY → VERIFY MANIFEST/LICENSE/VERSION/COMMIT → CAPTURE → DIFF → UPDATE SNAPSHOT POINTER → CONTRACT TEST → HOST TEST → RUNTIME TEST

- Source repository unavailable: retain RUNTIME_INSTRUCTION_SNAPSHOT, never invent a repository.
- Source license unknown: preserve the source link, label license NOT_DECLARED_OR_NOT_FOUND, and do not silently relicense the copied content.
- Private source: keep private, or require explicit approval before public mirroring.
- Version conflict: compare semantic version, source authority, changelog, compatibility and tests. Select the highest verified compatible version. A requested target version can be recorded separately from a released/source-verified version.
- Version bump with no source or tests: mark TARGET_SELECTED_SOURCE_SYNC_PENDING, not RELEASED.

## Parent repository ownership boundary

The parent owns only the catalog, routing matrix, contracts, governance, integration compatibility and snapshot index. Child plugin repositories keep their own package implementation, internal architecture and version/release lifecycle.
