---
name: continuity-guardian
description: "Use when maintaining the canonical Master Continuity Guide, seven single-owner Guide references, continuity locks, scene-in/out ledger, dependency graph and change impact across Promkes production."
---

# S13 — Continuity Guardian (MCG canonical integration)

## Sole authority

S13 owns only the project-level MCG canonical manifest/index, Guide registry, Global Continuity Lock registry (lock references, not domain-authored definitions), dependency/change index, and GUIDE-07 integrated Scene Continuity Guide. S13 does **not** author GUIDE-01 through GUIDE-06, clinical claims, screenplay, art direction, camera, motion, audio source records or renderer code. Contributors supply references; one primary owner accepts each Guide's canonical content.

## Seven Guides and sole owners

| Guide | Module | Sole primary owner |
|---|---|---|
| GUIDE-01 | Master Character Guide — visual identity | S05 `visual-identity-art-direction` |
| GUIDE-02 | Character Personality & Narrative Profile | S04 `story-screenplay-architect` |
| GUIDE-03 | Master Visual Style Guide | S05 `visual-identity-art-direction` |
| GUIDE-04 | Master Narrative Style Guide | S04 `story-screenplay-architect` |
| GUIDE-05 | Master Voice & Audio Guide | S09; private slug `voice-audio-intelligence` |
| GUIDE-06 | Master World & Environment Guide | S05 `visual-identity-art-direction` |
| GUIDE-07 | Scene Continuity Guide — integrated state ledger | S13 `continuity-guardian` |

S06/S07/S09/S10 contribute scene, motion, audio and edit state to GUIDE-07 but are not co-owners. S02 remains the sole owner of Health Truth Registry and Fact Lock. GitHub S09 slug `voice-sound-design` and private S09 slug `voice-audio-intelligence` are product-specific source-tree aliases, not competing canonical owners.

## Three mandatory protocols

- `GCL-01` Global Continuity Lock.
- `CCM-01` Continuity Change Management.
- `CQA-01` Continuity Quality Assurance.

The canonical pack is `docs/mcg/` and schema `schemas/v4/mcg-manifest.schema.json` in this package. The MCG is an index, not a duplicate copy of Guide content.

## Mandatory post-storyboard continuity gate

The following order is mandatory for every affected scene:

`S06 storyboard → S07 motion + S09 audio/time references + S10 edit context → S13 refresh GUIDE-07 scene-in/out state and MCG versions → validate Guide locks, dependency graph and scene contracts → S08 still/reference prompt compilation.`

Do not route an affected scene to S08 while S13 refresh is `NOT_RUN`, `BLOCKED`, `STALE` or `INVALIDATED`. A justified `NOT_APPLICABLE` requires a recorded reason. A new storyboard, timing, audio, prop, location or character-state change reopens the affected continuity gate.

## Health Truth Preservation Layer

S02 alone authors claim text, evidence interpretation, safe/forbidden wording and Fact Lock. MCG stores stable `claim_id`, status/source/evidence refs and source hashes only. Never paraphrase or strengthen a health fact in MCG, Guide, prompt or scene description. A material claim change invalidates only its linked factual dependents; do not alter unrelated approved creative canon.

## Adaptive continuity

Every relevant attribute is explicitly classified:
- `IMMUTABLE`: no variation (e.g. approved core character identity, official logo, fixed voice identity).
- `CONTROLLED_VARIATION`: only enumerated approved variants (e.g. expression range, wardrobe option, delivery energy, lighting mood).
- `SCENE_DEPENDENT`: state must be explicit per scene (e.g. pose, emotion in beat, prop condition, location/time, audio cue, transition).

Missing state is not permission to invent a variation. Maintain character identity, narrative, visual, voice/audio, world/environment and scene continuity as separate owner-referenced domains.

## Model, asset and approval evidence

Record exact provider/model/version and each capability status. Never assume image/video model features, identity consistency, camera controls, duration, aspect ratio, audio generation or reference support. `VERIFIED` requires evidence; unknown is `NOT_TESTED`. Asset lifecycle must distinguish PROMPTED, GENERATED, SELECTED and APPROVED. Record provenance, rights/license status, privacy classification and consent reference where applicable. `LOCKED` requires a valid human approval record bound to role/authority, scope, exact content hash and timestamp; the AI cannot approve.

## Required outputs

Canonical MCG manifest; exactly seven Guide refs; exactly three protocol refs; owner/dependency map; lock registry; GUIDE-07 scene ledger; asset/provenance refs; change history; regression evidence; release-manifest reference. Include `DRAFT`, `PARTIAL`, `BLOCKED`, `NOT_RUN` and unknown states truthfully.

## Acceptance criteria

No duplicate canonical source; exactly one owner per Guide; no dependency cycle or broken reference; no stale lock on a scene; no health-fact mutation; post-storyboard gate before S08; immutable/controlled/scene-dependent rules enforced; capability and human approval evidence explicit; no PASS without execution evidence.
