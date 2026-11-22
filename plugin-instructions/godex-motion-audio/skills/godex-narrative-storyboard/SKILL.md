---
name: godex-narrative-storyboard
description: Use when a verified voice-over transcript needs message analysis, narrative structure, storytelling, emotional arc, semantic segmentation, scene planning, storyboard writing, or a timed motion-graphic scene breakdown.
---

# GODEX Narrative & Storyboard

## Mission and boundary

Transform verified narration into a clear visual story and executable scene plan. This skill owns message architecture, audience framing, narrative flow, semantic beats, scene boundaries, screen-copy proposals, and storyboard logic. It does not transcribe inaccessible audio, invent facts, create the final visual identity, choreograph detailed keyframes, or render video.

## Required inputs

- Transcript with stable segment IDs and transcript provenance.
- Timing and duration evidence, if available.
- Project brief: audience, objective, platform, language, runtime, and CTA constraints.
- Optional brand or editorial requirements.

When required inputs are missing, proceed with explicit assumptions unless the missing item materially changes the message or risk.

## Procedure

1. **Fidelity pass:** identify transcript status and uncertainty. Preserve source wording separately from any proposed on-screen copy.
2. **Message extraction:** write the core message in one sentence; list supporting claims, examples, evidence, caveats, and intended audience action. Mark claims that need fact-checking.
3. **Audience model:** use only supplied or reasonably necessary assumptions. Do not invent demographic traits. State knowledge level and viewing context as assumptions where unknown.
4. **Narrative arc:** select a structure suited to the material (explanation → example → takeaway; problem → cause → solution; question → discovery → evidence; story setup → tension → resolution; or another justified structure). Do not force drama or a CTA into neutral content.
5. **Semantic segmentation:** create scenes around shifts in meaning, argument, example, speaker intent, or visual explanation. Avoid equal-duration cuts and arbitrary scene counts.
6. **Timing:** inherit timing from Audio Intelligence. Scene boundaries must map to source segment IDs. Use exact values only if grounded; otherwise mark as provisional/estimated and retain the source of uncertainty.
7. **Scene specification:** assign stable scene IDs and define purpose, narration range, dominant message, supporting details, proposed screen copy, visual concept, information density, emotional energy, and required assets.
8. **Pacing:** allow enough time to understand labels and diagrams; preserve pauses where they support comprehension; do not cut syllables to force a target runtime.
9. **Narrative red-team:** check repetition, missing transitions in logic, unsupported claims, confusing jargon, accidental change in meaning, and scenes that add no viewer value.
10. **Handoff:** send the approved scene plan and unresolved content questions to Visual Art Direction, Motion Design, and Audio Post & Caption.

## Output contract

- `core_message` and `supporting_messages`.
- `audience_and_context` with assumptions labeled.
- `narrative_arc` and rationale.
- `fact_check_flags` for claims requiring external evidence.
- `scene_plan`: `scene_id`, source segment IDs, in/out/duration with timing provenance, narration, message, screen copy, visual concept, layout intention, emotional/pacing note, asset needs, confidence, open questions.
- `storyboard_summary`: one concise beat per scene.
- `narrative_risks`: ambiguity, unsupported claim, overcrowding, weak transition, factual sensitivity.
- `handoff_notes` for visual and motion stages.

## Stop conditions

- If transcript is unavailable or too uncertain to support faithful scene planning, request it or produce only a clearly labeled structural template.
- Never add factual claims, examples, statistics, named entities, or quotations that are absent from the source without clearly labeling a proposed addition and obtaining verification where needed.
- Never call estimated timing exact.
- Do not rewrite the narration as promotional copy unless the user explicitly asks for adaptation.
- Stop and ask one focused question if the intended audience, message, or regulated/high-stakes context would materially alter content and cannot be safely assumed.

## Shared references

Follow `../godex-motion-audio/references/production-pipeline.md`, `../godex-motion-audio/references/output-contract.md`, and `../godex-motion-audio/references/inter-skill-contracts.md`. Own narrative fields and scene semantics; do not overwrite Audio Intelligence provenance.
