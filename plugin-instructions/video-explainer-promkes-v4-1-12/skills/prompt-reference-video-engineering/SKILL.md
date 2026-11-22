---
name: prompt-reference-video-engineering
description: Use when compiling renderer-neutral reference prompts, optional AI video prompts and evidence-bound target-model adapters for Promkes scenes.
---

# S08 — AI Video & Reference Prompt Engineering

## Mission and boundaries

Compile approved source, screenplay, storyboard, visual canon, S07 motion records and audio references into coherent still/reference prompt packs and (when requested) optional per-scene AI-video prompts. Keep still prompts, temporal video prompts, motion data and renderer code as four distinct artifact types.

S08 does not own health claims (S02), narrative (S04), visual canon (S05), camera/shot design (S06), motion records (S07), audio source/timing (S09), renderer implementation (S10), final QA (S12), or MCG (S13).

## Compiler A — Still/reference prompts

One prompt = one still asset or one captured keyframe. Types may include STYLE, CHARACTER, EXPRESSION, POSE, ENVIRONMENT, PROP, SCENE_KEYFRAME, OVERLAY_ART and OTHER. Include one captured visual state, composition/viewpoint/light, aspect ratio, Guide/lock versions, source fact refs, identity anchors and negative constraints. Do not describe continuous footage.

Exact dates, health claims, statistics, institutional names, logos, phone numbers and CTA remain verified editable overlay data; do not rely on image-model typography.

## Compiler B — Optional video-generation prompts

Only create when requested/relevant and when the target use is clear. Use one prompt block per scene/shot unless the target explicitly supports another structure. Each block can include subject, action, setting, temporal behavior, camera intent reference, motion references, duration/time precision, continuity, audio direction, negative constraints and output format. Do not place renderer code or Remotion props inside the video prompt.

## Compiler C — Platform dialect adapter

Before emitting target-specific parameters, require exact provider, model name/version, task type (text-to-video/image-to-video), current official documentation reference, supported feature record and any runtime evidence. Use `schemas/v4/video-platform-adapter.schema.json`.

Candidate families for adapter discovery include Sora, Veo, Kling, Runway and Seedance. Candidate names are not support claims. If exact model/version is absent, issue a provider-neutral prompt and mark adapter `NOT_CHECKED`. Unknown support stays UNKNOWN. `DOCS_VERIFIED` is not `RUNTIME_TESTED`; the latter requires exact environment/run evidence.

Map only documented controls. Unsupported controls must be omitted or marked as manual directions. Do not present arbitrary numeric camera, fps, duration, image-reference or audio fields as model-executable unless the exact target supports them. Preserve a loss/approximation report.

## Nine-slot video prompt anatomy

Use these slots as a completeness checklist, not a rigid universal syntax. Omit irrelevant slots with a reason; never invent material:

1. **Subject & factual boundary:** subject/state and approved source/claim refs; no new health fact.
2. **Action/behavior:** one primary observable action/behavior per beat.
3. **Setting & staging:** environment, subject placement, composition; align with S05/S06.
4. **Camera intent:** reference S06 shot/camera plan; do not invent camera controls.
5. **Motion arc:** initial state, action, anticipation/follow-through/settle and S07 refs.
6. **Time & beat:** duration, beat boundary, fps/timebase and source precision; separate exact from estimated.
7. **Visual treatment:** approved visual style/material/light/color/continuity anchors.
8. **Constraints & negatives:** no claim drift, text distortion, logo drift, unsafe action, misleading medical visualization, stigma or fear manipulation.
9. **Audio & accessibility:** VO/audio cues from S09; reading time, subtitles, reduced-motion and accessibility notes where relevant.

## Workflow

1. Read the locks: project ID, MCG version, claim refs, Guide IDs/versions, scene IDs, approved overlays and rights/consent status.
2. Choose reference depth (`LITE`, `STANDARD`, `ADVANCED`) and define stable `ASSET-REF-ID` inventory.
3. Compile master style, character/environment/prop and scene keyframe prompts from accepted S05/S06 sources.
4. Keep motion as S07 references; do not embed continuous movement in an image prompt.
5. For optional video prompts, apply the nine-slot anatomy and exact model adapter only where evidence permits.
6. Keep target model capabilities and prompt dialect in the adapter record, not in unsupported free-text assumptions.
7. Validate prompt completeness, negative constraints, identity, health truth, overlay separation, asset rights and capability status.
8. Hand off references and optional video prompt variants to M00/S10/S12 with limitations and trace IDs.

## Required outputs

1. Master visual reference prompt.
2. Character/expression/pose references.
3. Environment/prop references.
4. Scene keyframe/reference prompts.
5. Reference asset manifest and lifecycle state.
6. Optional provider-neutral/per-platform video prompt pack.
7. Platform adapter record, feature matrix and verification status.
8. Renderer-neutral handoff, open issues and limitations.

## Acceptance and failure rules

PASS only if each prompt is self-contained for its intended asset/task; each reference maps to a Guide/scene/lock; factual text is overlay data; the nine-slot fields are either present or justified as inapplicable; capability claims are evidence-backed; and asset lifecycle differentiates PROMPTED, GENERATED, SELECTED and APPROVED.

If target unknown or unverified, use provider-neutral output and adapter `NOT_CHECKED`. Do not treat prompt generation as model execution or a generated asset as approved. Any health-claim modification returns to S02; camera conflicts return to S06; motion conflicts return to S07; MCG continuity changes return to S13.
