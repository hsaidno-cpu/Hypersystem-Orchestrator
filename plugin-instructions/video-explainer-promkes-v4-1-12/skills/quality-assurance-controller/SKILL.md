---
name: quality-assurance-controller
description: Use when independently auditing Promkes content integrity, health facts, references, motion/cinematic contracts, continuity, audio/subtitle timing, renderer handoff, actual media and release readiness.
---

# S12 — Dual-Layer Quality Assurance Controller

## Mission and independence

Independently inspect the agreed production against source records, Health Truth Registry, approved brief, MCG/Guide locks, timing provenance, motion contracts, adapter evidence, output contract and observable artifacts. QA reports/routes defects; it does not silently rewrite another domain's deliverable or certify media it has not inspected.

## QA levels

1. Package/prompt/reference/static schema QA.
2. Actual generated reference asset inspection.
3. Target renderer mapping/integration QA.
4. Actual rendered video/audio/subtitle/overlay QA.
5. Human clinical/institutional/legal/rights/privacy/brand/accessibility/publication approval (separate authority).

A text manifest or a valid JSON Schema cannot prove a property of a rendered file. No higher level PASS is implied by lower level PASS.

## Layer A — Content, health and creative package QA

- Source fidelity: poster/caption/transcript values, names, numbers, locations and wording preserved.
- Health integrity: material claims trace to S02 claim/evidence records; no stronger claim, diagnosis, treatment, prevention guarantee or unsupported causal statement.
- Campaign/story: audience, objective, key message and CTA are coherent and source-safe.
- Script/VO: verbatim supplied narration and edited script remain separate; every factual line maps to claim IDs.
- Visual/continuity: design tokens, character/environment/prop identity, MCG and Guide lock versions match affected scenes.
- Reference engineering: prompt type is correct, exact typography is overlay data, asset lifecycle/rights are truthful, and target capability is evidence-bound.
- Motion contract: `schemas/v4/motion-record.schema.json` validity; stable element IDs; half-open frame arithmetic; fps/timebase/source precision; keyframe order/range; phase bounds; units; easing params; motion path; negative constraints; camera refs point to S06; and renderer targets are not overclaimed.
- Beat/shot: beat purpose and message refs align with scene/shot; camera intent traces to S06; motion references to S07; audio timing to S09; overlay refs remain claim-bound.
- Accessibility: reading time, reduced-motion fallback, text contrast/legibility and flicker/flash risk are considered at the level actually observable.
- Renderer-neutral handoff: scene/asset/layer/overlay/subtitle/audio mappings and assumptions are explicit; canonical record is not confused with target-specific output.

## Cinematic/animation acceptance rubric

Use criterion-level evidence, not aesthetic adjectives or a single averaged “beauty” score:

1. **Narrative function:** each shot/beat serves the approved message and is not decorative motion that obscures health comprehension.
2. **Framing/composition:** subject and approved overlay remain inside declared safe areas; focus/hierarchy/readability are observable.
3. **Camera/shot continuity:** camera move is traceable to S06; axis, scale, direction and transition do not create unexplained discontinuity.
4. **Motion readability:** action, anticipation, follow-through, settle and hold are sufficiently distinct for the stated action; path/transform values have units.
5. **Timing/arithmetic:** beat/shot/motion/audio ranges agree within declared source precision; no invented exact sync.
6. **Continuity:** character, prop, environment and approved visual locks remain intact; scene in/out states reconcile with MCG.
7. **Visual artifacts:** inspect deformation, flicker, clipping, missing objects, unwanted text/logo changes and inconsistent assets only when actual frames/assets are available.
8. **Accessibility:** readable text/hold duration, non-flashing transitions and reduced-motion fallback where applicable.
9. **Audio/subtitle alignment:** inspect only with source audio/subtitle/artifact and appropriate playback/analysis capability.
10. **Target compliance:** supported controls and model/version are traceable; unsupported controls are disclosed.

Each check must have `criterion_id`, scope, oracle/method, expected result, observed result, status, evidence refs, limitation and defect owner. No subjective rating without operational definition and evidence.

## Layer B — Actual audio, render and artifact QA (conditional)

Only run when actual media exists and inspection capability is available. Check:
- audio/transcript correspondence and timing precision;
- SRT/VTT syntax, cue bounds, ordering, overlap and sync;
- voice intelligibility vs music/SFX, clipping/noise/silence only when heard/measured;
- file openability, container, video/audio streams;
- dimensions, fps, duration and codec where metadata tools permit;
- blank/frozen frames, artifacts, crop/safe area, contrast, text legibility and continuity when inspected;
- A/V sync and shot timing when playback/frame/audio inspection is possible;
- rights/consent, privacy and release-critical overlays.

If no output file is supplied/created, artifact QA is `NOT_RUN`. If a property cannot be inspected, use `NOT_VERIFIED`.

## Status, severity and correction

Statuses: `PASS`, `FAIL`, `PARTIAL`, `NOT_VERIFIED`, `NOT_RUN`, `NOT_APPLICABLE`. Defects use `BLOCKER`, `MAJOR`, `MINOR`, `OBSERVATION`, with `DEF-ID`, affected IDs, evidence, owner, correction, retest and invalidation scope. Never average a critical failure away with high scores elsewhere.

Route source/claim issue to S01/S02; story to S03/S04; visual/canon to S05/S13; shot/camera to S06; motion to S07; reference/video adapter to S08; transcript/audio/subtitle to S09; composition/render/export to S10; social accessibility/distribution to S11; context/release parity to S14. Preserve unaffected approvals but rerun affected regression and dependency closure.

## Output contract

- scope, acceptance criteria and test level;
- per-criterion check matrix with oracle, status, evidence and limitation;
- source/health/reference/motion/cinematic QA findings;
- audio/subtitle/render/media findings or `NOT_RUN`/`NOT_VERIFIED`;
- defect register and retest plan;
- residual risk/unknowns;
- release recommendation `APPROVE`, `APPROVE_WITH_LIMITATIONS`, `REWORK_REQUIRED` or `BLOCKED`;
- technical delivery state and human approval state reported separately.

## Stop conditions

Do not pass health claims without evidence; do not claim actual inspection from text; do not approve missing/unknown rights; do not claim A/V sync or output metadata without observation; do not conflate technical QA with clinical/institutional approval or publication permission. No publish-ready recommendation with unresolved blockers or unverified critical checks.

## Remotion pattern and encoded-media QA (S12)

For Remotion pattern adoption, use `skills/animation-motion-design/references/remotion-pattern-adoption-v4.1.11.md` as the pattern-specific acceptance reference. Check pattern purpose, units, half-open frame ranges, easing intent, reduced-motion/readability, source timing precision and target mapping. Report composition-frame QA separately from encoded-MP4 QA; a source `still` does not validate the encoded export. Missing actual media or inspection capability remains `NOT_RUN`/`NOT_VERIFIED`.
