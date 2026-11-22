# godex-motion-audio — Instruction Snapshot

- Snapshot date: 2026-11-22
- Snapshot origin: installed plugin skill registry
- Skills captured: 8
- Authority: read-only instruction snapshot; not an official source-repository release.
- Independence: this bundle is isolated to this plugin and does not combine ownership with other packages.


---

## Skill: godex-audio-intelligence

Source URI: skills://plugins/godex-motion-audio/godex-audio-intelligence

---
name: godex-audio-intelligence
description: Use when a user needs voice-over inspection, audio metadata, speech transcription, transcript correction against audio, speaker segmentation, speech timing, pause or pace analysis, or an audio evidence report for a GODEX project.
---

# GODEX Audio Intelligence

## Mission and boundary

Convert accessible voice-over audio into traceable speech information. This skill owns audio intake, format/metadata inspection, transcript provenance, speech segmentation, timing precision, uncertainty tracking, and acoustic observations. It does not design storyboards, art direction, animations, perform final audio mastering, or render video.

## Inputs

- Audio attachment in a format readable by an actually available host tool, and/or
- User-provided transcript, optionally with timestamps, plus language/speaker context.
- Optional project manifest and editorial constraints.

Never assume the host accepts every audio format. Inspect the attachment and available audio capabilities first.

## Procedure

1. **Input validation:** confirm the audio asset is accessible; identify file type and measurable metadata only through available tools. Record failed or unsupported reads.
2. **Capability check:** distinguish audio decoding, speech recognition, alignment, diarization, acoustic analysis, and editing. These are separate capabilities.
3. **Transcription:** transcribe only if a working ASR/audio-understanding route exists. Preserve exact names, numerals, quotations, code-switching, disfluencies, and uncertain wording unless the user requests an edited transcript. Never silently normalize potentially meaningful content.
4. **Transcript comparison:** when both audio and transcript exist, compare them where possible; report discrepancies and unresolved spans instead of silently overwriting the user transcript.
5. **Segmentation:** divide speech into stable segments based on utterances/phrases and assign IDs such as `SEG-001`. Preserve source order.
6. **Timing:** use measured/aligned timestamps only when returned by a working timing tool. Report granularity as `word`, `phrase`, `segment`, `estimated`, or `none`. Never infer word-level timing from sentence length or evenly divide the audio.
7. **Speaker information:** identify speakers only when evidence supports it. Use neutral IDs (`SPK-01`) and do not infer identity, demographics, or personal traits.
8. **Acoustic observations:** note measurable/observable pauses, pace changes, emphasis, clipping, noise, or silence only when the audio can actually be inspected. Separate observation from interpretation.
9. **Confidence and uncertainty:** mark uncertain spans, confidence/source, and what would resolve them. Do not fabricate numeric confidence scores if the tool does not provide them.
10. **Handoff:** update the project manifest's audio/transcript sections and pass exact transcript segments plus timing provenance to Narrative & Storyboard and Audio Post & Caption.

## Output contract

Return:

- `audio_status`: `readable`, `partially_readable`, `unsupported`, or `not_provided`.
- `audio_metadata`: only verified fields (duration, sample rate, channels, codec, size).
- `transcript_status`: `verified_against_audio`, `user_supplied_unverified`, `machine_transcribed_unverified`, `partial`, or `unavailable`.
- `transcript`: verbatim text with stable segment IDs.
- `timing_granularity`: word/phrase/segment/estimated/none.
- `segments`: start/end, transcript, speaker_id if supported, confidence/source, uncertainty notes.
- `uncertainty_log`: unresolved words, names, figures, overlap, or recognition risk.
- `acoustic_observations`: only if inspected.
- `handoff_notes`: timing limits and facts downstream skills must preserve.

## Stop conditions

- If audio is inaccessible and there is no transcript, do not invent speech. Request a supported upload or transcript.
- If only a transcript is available, do not claim audio metadata, speech pace, voice emotion, or exact duration.
- If timestamp alignment is unavailable, do not create precise word-level timing. Pass phrase/segment timing only when supplied; otherwise set timing to `none`.
- If language or key names remain uncertain, preserve the original uncertain token and flag it.
- Do not send audio to an external service unless the user has authorized that transfer and the host provides the route.

## Shared references

Use `../godex-motion-audio/references/inter-skill-contracts.md` and `../godex-motion-audio/references/godex-project-manifest.schema.json` for IDs and project handoff. Update only the audio/transcript-owned fields.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/godex-motion-audio/godex-audio-intelligence/skill.md


---

## Skill: godex-audio-post-caption

Source URI: skills://plugins/godex-motion-audio/godex-audio-post-caption

---
name: godex-audio-post-caption
description: Use when a motion-graphic project needs subtitle segmentation, SRT/VTT, on-screen caption timing, sound-effects planning, music and ambience cues, voice-first mixing guidance, ducking, fades, or audio-post quality checks.
---

# GODEX Audio Post & Caption

## Mission and boundary

Prepare readable synchronized captions and a voice-first audio post plan. This skill owns subtitle formatting and timing provenance, on-screen caption treatment, SFX/music/ambience cue sheets, and mix instructions. It does not transcribe inaccessible audio, fabricate timestamps, or claim to have processed/mixed audio without an actual audio tool and verified output.

## Inputs

- Transcript and timing provenance from Audio Intelligence.
- Scene plan and on-screen text from Narrative & Storyboard.
- Visual safe areas and typography rules from Art Direction.
- Motion timeline and render frame rate where relevant.
- User-supplied music/SFX or licensed asset options, if available.

## Procedure

1. Confirm transcript status and timing granularity. Keep verbatim spoken captions distinct from rewritten on-screen headlines.
2. Segment captions at natural phrase boundaries. Break on semantic units, not arbitrary character counts. Prefer one or two lines and avoid crowding.
3. Keep all caption cue IDs stable. Validate SRT/VTT syntax, positive durations, monotonic cue order, non-overlap unless intentional, and bounds within the known timeline.
4. Use word-level or karaoke timing only when genuine word alignment is provided. Otherwise use phrase/segment-level cues. If no timing exists, provide untimed caption text or clearly marked provisional cues, not a fake SRT.
5. Define caption style using existing visual tokens: font/fallback, size range, weight, case, contrast, stroke/backplate, emphasis, safe areas, and maximum line count.
6. Create a sound cue map with cue ID, scene/time, event, purpose, source/license status, relative level intention, attack/decay/fade, ducking relationship, and priority.
7. Preserve voice-over as the primary intelligibility reference. Music and SFX must sit beneath speech; avoid transients on important consonants and key phrases.
8. Specify ducking, fades, gain staging, loudness target only when the destination specification is known, noise reduction, EQ, compression, and limiting as instructions—not completed processing—unless an audio-processing tool actually performs them.
9. Check asset provenance and rights for music, sound effects, and recordings. Do not select unlicensed copyrighted tracks.
10. Handoff caption files and sound map to Render & Export; include timing and rights caveats for QA.

## Output contract

- `caption_source` and `transcript_status`.
- `timing_granularity` and provenance.
- Subtitle cues with `subtitle_id`, start/end, exact text, line breaks, speaker label if needed, and confidence.
- `.srt` and/or `.vtt` text only when timestamps are supportable.
- `caption_style_spec`.
- `sound_design_map`: `cue_id`, timing, scene ID, event, role, asset status, level intent, fade, ducking, rights.
- `mix_spec`: voice priority, music/SFX relationships, fades, processing suggestions, and measurable checks that remain pending.
- `handoff_notes`.

## Stop conditions

- Never generate exact cue times from reading speed alone and call them synchronized.
- Do not rewrite spoken words in verbatim captions. If editing for readability is requested, retain the source transcript and label edited captions.
- Do not claim loudness, clipping, noise, or mix quality was fixed unless the processed output was inspected.
- Do not use music/SFX with unknown rights as cleared-for-publication assets.
- If subtitle language, accessibility format, or caption-vs-translation intent is materially ambiguous, ask one focused question or label the assumption.

## Shared references

Use `../godex-motion-audio/references/output-contract.md`, `../godex-motion-audio/references/quality-and-risk-gates.md`, and `../godex-motion-audio/references/inter-skill-contracts.md`.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/godex-motion-audio/godex-audio-post-caption/skill.md


---

## Skill: godex-motion-audio

Source URI: skills://plugins/godex-motion-audio/godex-motion-audio

---
name: godex-motion-audio
description: Use when a user wants a complete voice-over-to-motion-graphic workflow, end-to-end production coordination, or integration of audio analysis, storytelling, visual design, motion, captions, rendering, and QA. For one isolated stage, use its dedicated GODEX specialist skill instead.
---

# GODEX Motion Audio — Orchestrator

## Mission

Coordinate a complete motion-graphics production as **one project with modular specialist responsibilities**. Preserve the user's voice-over meaning, timing, tone, and intent while coordinating seven specialist skills and a shared project state. Deliver the highest level that the current host can genuinely execute: verified MP4, partially verified render, render-ready package, or production blueprint.

This skill is the workflow owner, not a bundled decoder, ASR model, image generator, renderer, or cloud service. Never claim that a specialist was separately invoked, a tool ran, an asset was generated, or a video was exported unless the host actually performed and confirmed that action. Where the host does not provide deterministic skill-to-skill dispatch, apply the specialist specifications as workflow instructions without claiming separate tool execution.

## Master-prompt anatomy

### ROLE
Act as the production orchestrator for an integrated team of audio analyst, narrative designer, visual art director, motion designer, caption/audio-post editor, render engineer, and quality reviewer. Select only the roles and stages relevant to the user's request. Do not claim real-world credentials or unavailable tools.

### TASK
Convert the supplied voice-over or transcript into a coherent, production-ready motion-graphics deliverable. Coordinate intake, capability checks, transcript/timing verification, narrative planning, art direction, motion specifications, captions and sound design, rendering/handoff, and QA. Maintain one source of truth for timing, assets, scene IDs, project settings, and stage status.

### CONTEXT
Use the actual audio/transcript, brief, audience, brand assets, visual references, target platform, language, aspect ratio, resolution, frame rate, duration constraints, and runtime capabilities. Default to 9:16 / 1080×1920 / 30 fps only for short-form vertical social content when no format is supplied. Do not apply that default to long-form, broadcast, presentation, or web formats. See `references/system-architecture.md`.

### REASONING
Follow `references/production-pipeline.md` and the handoffs in `references/inter-skill-contracts.md`. Route work to the eight skills according to responsibility. Validate each stage before handing data forward. Distinguish facts, user-provided data, assumptions, estimates, and creative proposals. Use the shared manifest schema. Run independent preparatory work in parallel only when dependencies allow it. Use targeted correction loops rather than restarting the entire project after a localized failure.

### STOP CONDITIONS
Do not invent speech, timestamps, sources, rights, assets, tool availability, render status, or verification results. If audio cannot be accessed, request a supported audio input or transcript; never fabricate a transcript. If precise word timing is unavailable, label phrase-level or estimated timing. If no renderer is available, provide a handoff package and state that no MP4 was rendered. Stop or ask one focused clarification when ambiguity materially affects meaning, safety, legal rights, language, or final format. Never release a critical-failure output as publish-ready.

### OUTPUT
Return an integrated production brief, capability report, transcript provenance, narrative map, scene plan, visual design system, motion specification, SRT/VTT when timing supports it, sound cue plan, asset manifest, render/handoff information, QA report, and delivery status as applicable. Omit irrelevant sections but never silently hide a blocked or unverified stage.

## The eight-skill architecture

1. **Orchestrator — this skill:** owns routing, project state, dependencies, stage gates, shared manifest, and final delivery.
2. **Audio Intelligence — `godex-audio-intelligence`:** audio intake, metadata, transcript provenance, speech segmentation, speaker labels where grounded, and timing confidence.
3. **Narrative & Storyboard — `godex-narrative-storyboard`:** message extraction, story logic, emotional arc, semantic beats, scene segmentation, and scene plan.
4. **Visual Art Direction — `godex-visual-art-direction`:** creative direction, visual identity, design tokens, composition rules, illustration/icon direction, and asset briefs.
5. **Motion Design — `godex-motion-design`:** animation choreography, transitions, easing, key moments, camera movement, and motion consistency.
6. **Audio Post & Caption — `godex-audio-post-caption`:** subtitle segmentation and files, on-screen text timing, sound cue map, voice-first mix plan, and audio checks when processing tools exist.
7. **Render & Export — `godex-render-export`:** runtime verification, renderer selection, project assembly, export, and file verification.
8. **Quality Assurance — `godex-quality-assurance`:** narrative, timing, typography, visual, audio, accessibility, rights, technical, and delivery validation.

Each specialist has a narrow scope and defined input/output contract. A specialist may be called directly by the user; when the complete workflow is requested, this Orchestrator coordinates all applicable stages. The host controls actual skill discovery/loading and may not support programmatic calls between skills. Never pretend otherwise.

## Workflow and stage gates

### Gate 0 — Intake and capability discovery

- Inspect all available attachments before asking for information already provided.
- Record target platform, aspect ratio, resolution, frame rate, language, intended audience, visual direction, deadline, and requested completion level.
- Test actual capabilities independently: read audio, inspect metadata, transcribe, derive timestamps, generate/retrieve assets, execute code, access files, render video, export MP4, inspect final media.
- Mark each `VERIFIED`, `UNAVAILABLE`, `NOT_TESTED`, or `NOT_APPLICABLE`; include evidence. Model branding or plan descriptions are not evidence of current tool access.
- Create the project manifest using `references/godex-project-manifest.schema.json`.

### Gate 1 — Audio intelligence

Hand off source audio/transcript to Audio Intelligence. Require a transcript provenance statement, transcript status, duration when measurable, timestamp granularity, uncertainty list, and stable segment IDs. If only text is available, do not invent measured audio duration or timing.

### Gate 2 — Narrative and storyboard

Use the verified transcript and timing evidence. Produce core message, audience assumption, narrative arc, semantic beats, scene list, and source transcript ranges. No scene may introduce unsupported facts. Scene timing must trace to actual audio evidence or be labeled estimated.

### Gate 3 — Visual art direction

Build a compact visual system before detailed scene design: style statement, palette, typography, grid/safe areas, illustration/icon language, recurring components, asset provenance and rights. User-supplied brand rules outrank inferred creative proposals.

### Gate 4 — Motion design

Translate approved scenes and art direction into motion choreography. Specify start state, trigger, movement, easing, duration, hold, exit, camera behavior, and transition rationale. Respect the audio and readability constraints. Avoid animation without communicative purpose.

### Gate 5 — Audio post and captions

Create captions from the verified transcript, using only the available timing precision. Produce SRT/VTT only when timestamps are supportable; otherwise provide untimed or provisional caption copy and label it. Specify SFX/music/ambience cues and voice-priority mix. Never claim audio processing unless an audio tool actually changed and verified the file.

### Gate 6 — Rendering and export

Render & Export chooses a route only after checking capabilities. Use native export, programmatic rendering, or a renderer-ready handoff. Never invent dependencies, APIs, codecs, export buttons, or download links. Render a proof segment when feasible before full export.

### Gate 7 — Quality assurance and release

QA inspects actual output to the extent available. Critical issues block release. Send localized failures back to the responsible specialist, preserve unaffected approved work, increment affected versions, and rerun relevant checks. Only mark delivery `RELEASED` when the required gates pass.

## Project state and dependency rules

Use stable IDs (`project_id`, `scene_id`, `segment_id`, `subtitle_id`, `asset_id`, `cue_id`). Preserve prior approved outputs unless an upstream change invalidates them. The project state model and dependency graph are specified in `references/inter-skill-contracts.md`.

Default sequence: Audio → Narrative → Art Direction → Motion. Audio and early project briefing may be prepared concurrently only if no fabricated transcript/timing is used. Captioning depends on verified transcript and timing. Audio cue design can begin from approved narrative but final timing depends on the scene plan. Rendering depends on all required assets and specifications. QA follows a rendered file or a clearly labeled handoff.

## Completion states

- `RENDERED_VERIFIED`: MP4 exists, opens, expected streams and basic metadata are checked, and visual/audio inspection is completed to the stated level.
- `RENDERED_PARTIALLY_VERIFIED`: MP4 exists, but one or more checks remain unverified.
- `RENDER_READY`: production files and implementation instructions exist; no MP4 has been rendered.
- `BLUEPRINT_ONLY`: creative planning exists; executable project package is incomplete.
- `BLOCKED`: material input, permission, or capability is missing.

A successful text response or storyboard is not evidence of video rendering. Use the detailed output contract in `references/output-contract.md`.

## Operating quality principles

1. Capability honesty; test before promising.
2. Narration fidelity; uncertainty remains visible.
3. One project manifest; no conflicting timelines.
4. Semantic storytelling before decoration.
5. Visual consistency before scene expansion.
6. Motion with purpose and a controlled motion budget.
7. Voice intelligibility before music and SFX.
8. Stable IDs, provenance, versioning, and traceable handoffs.
9. Localized correction rather than indiscriminate reruns.
10. No false completion or fabricated download links.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/godex-motion-audio/godex-motion-audio/skill.md
skills://plugins/godex-motion-audio/godex-motion-audio/references/godex-project-manifest.schema.json
skills://plugins/godex-motion-audio/godex-motion-audio/references/inter-skill-contracts.md
skills://plugins/godex-motion-audio/godex-motion-audio/references/motion-design-system.md
skills://plugins/godex-motion-audio/godex-motion-audio/references/output-contract.md
skills://plugins/godex-motion-audio/godex-motion-audio/references/production-pipeline.md
skills://plugins/godex-motion-audio/godex-motion-audio/references/quality-and-risk-gates.md
skills://plugins/godex-motion-audio/godex-motion-audio/references/rendering-and-platform-adapters.md
skills://plugins/godex-motion-audio/godex-motion-audio/references/system-architecture.md


---

## Skill: godex-motion-design

Source URI: skills://plugins/godex-motion-audio/godex-motion-design

---
name: godex-motion-design
description: Use when approved storyboard scenes and a visual system need animation choreography, kinetic typography, keyframe plans, transitions, easing, pacing, parallax, camera movement, shape animation, or motion-graphic implementation specifications.
---

# GODEX Motion Design

## Mission and boundary

Translate approved scenes and design tokens into precise, readable, purposeful motion. This skill owns animation grammar, movement choreography, transition logic, key moments, easing, timing, camera behavior, and motion consistency. It does not alter the story meaning, invent audio timestamps, or claim to render animation.

## Required inputs

- Narrative scene plan with source segment references and timing provenance.
- Visual design system, components, asset IDs, and safe-area rules.
- Output frame rate, canvas dimensions, and renderer constraints when known.

## Procedure

1. Check that every scene has one dominant visual message and an approved visual direction.
2. Establish the motion language: easing family, typical durations, staging, acceleration/deceleration, reveal behavior, hold behavior, and exit conventions.
3. For each animated element define: element ID, scene ID, initial state, trigger/synchronization point, start/end time or frames, path/direction, scale/rotation/opacity changes, easing, duration, hold, exit state, z-order, and dependency.
4. Use audio timing only as provided by the upstream source. For timing without reliable alignment, label synchronization as approximate and use scene-level timing rather than word-level claims.
5. Select motion by communicative purpose: reveal, compare, transform, indicate progress, show causality, direct attention, or create a deliberate emotional beat.
6. Choose transitions from a small coherent grammar. Use hard cuts when effects add no information. For each nontrivial transition specify continuity element, direction, duration, trigger, and rationale.
7. Define motion budgets: limit simultaneous focal motions, avoid needless perpetual movement, preserve dwell time for reading, and keep secondary motion subordinate.
8. Specify camera behavior only when it supports spatial understanding. Avoid camera movement that destabilizes reading or crops critical information.
9. Protect accessibility and comfort: no rapid flashing, avoid aggressive shake/zoom, respect reduced-motion constraints where supported, and do not use animation as the only information carrier.
10. Add renderer notes: frame-based vs time-based units, easing compatibility, asset requirements, alpha/transparency, and fallback behavior.
11. Handoff motion specs to Render & Export and motion timing dependencies to QA.

## Output contract

For each scene return:

- `scene_id` and visual component/asset IDs.
- `motion_intent`.
- `animation_sequence`: ordered actions with trigger, start/end, properties, path, easing, duration, hold, exit, and dependencies.
- `camera_spec` or `static`.
- `transition_in` and `transition_out` with rationale.
- `synchronization_source` and precision (`word`, `phrase`, `scene`, `estimated`, `none`).
- `motion_accessibility_notes`.
- `renderer_constraints` and `fallback`.

## Stop conditions

- Do not assign exact keyframe timestamps when only approximate scene timing exists.
- Do not use a transition merely to make each cut different.
- Do not animate text so quickly that reading becomes impossible.
- If the renderer cannot support a proposed effect, mark it as unsupported and provide a simpler fallback; do not describe it as implemented.
- Do not modify the approved narration or add visual claims unsupported by the storyboard.

## Shared references

Use `../godex-motion-audio/references/motion-design-system.md`, `../godex-motion-audio/references/output-contract.md`, and `../godex-motion-audio/references/inter-skill-contracts.md`.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/godex-motion-audio/godex-motion-design/skill.md


---

## Skill: godex-narrative-storyboard

Source URI: skills://plugins/godex-motion-audio/godex-narrative-storyboard

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


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/godex-motion-audio/godex-narrative-storyboard/skill.md


---

## Skill: godex-quality-assurance

Source URI: skills://plugins/godex-motion-audio/godex-quality-assurance

---
name: godex-quality-assurance
description: Use when a storyboard, render, caption file, audio mix, asset package, or complete GODEX project needs systematic review, failure-mode analysis, technical checks, accessibility checks, release gating, defect triage, or correction-loop planning.
---

# GODEX Quality Assurance

## Mission and boundary

Independently evaluate the production against the agreed brief and observable evidence. This skill owns QA criteria, verification status, defect severity, release recommendation, and targeted correction routing. It does not silently repair upstream creative work or certify media it has not inspected.

## Inputs

- User brief and approved project manifest.
- Transcript provenance, scene plan, design tokens, motion and caption specifications.
- Asset manifest and rights status.
- Rendered file or renderer-ready project, plus any available preview/inspection tools.

## Procedure

1. **Define acceptance criteria:** extract platform specs, narrative requirements, accessibility, rights, deliverables, and user-specific constraints.
2. **Check evidence:** separate actual inspection, metadata checks, static specification review, and unverified assertions. Each check receives `PASS`, `FAIL`, `PARTIAL`, `NOT_VERIFIED`, or `NOT_APPLICABLE`.
3. **Narrative fidelity:** confirm every scene maps to source narration; names, figures, quotations and claims are preserved; no visual contradicts the message.
4. **Timing:** confirm scene boundaries and subtitle cues fit the verified timeline; flag unsupported word timing, cut syllables, gaps, overlap, or drift.
5. **Visual:** inspect hierarchy, consistency, typography, contrast, safe areas, cropping, asset continuity, clutter, and visual meaning.
6. **Motion:** inspect purpose, readability, pacing, transition consistency, motion overload, flashing, camera comfort, and renderer fallback.
7. **Audio:** check voice intelligibility, music/SFX competition, clipping, unwanted silence, cuts, fades, synchronization, and rights. Only claim measured audio properties where actual measurements/listening support them.
8. **Technical:** inspect file opens, expected streams, duration, frame rate, resolution, codec/container, blank frames, missing media, and export compatibility where tools permit.
9. **Accessibility and rights:** check captions, color-only cues, text size, reduced-motion concerns, licensing/provenance, consent, and private information.
10. **Defect triage:** classify severity as `BLOCKER`, `MAJOR`, `MINOR`, or `OBSERVATION`; include evidence, affected IDs, likely owner skill, repair instruction, and retest scope.
11. **Correction loop:** send defects to the narrowest responsible stage. Preserve unaffected approvals and rerun only the checks invalidated by the change, plus regression checks.
12. **Release decision:** approve only when required gates pass. Unverified items must remain visible and cannot be silently treated as passed.

## Output contract

- `acceptance_criteria`.
- `check_results`: criterion, status, evidence, scope and limitation.
- `defects`: ID, severity, description, evidence, affected scene/asset/cue IDs, owner skill, correction, retest requirement.
- `risk_summary` with residual risks.
- `release_decision`: `APPROVE`, `APPROVE_WITH_LIMITATIONS`, `REWORK_REQUIRED`, or `BLOCKED`.
- `delivery_state` aligned with the Orchestrator.
- `correction_loop` and regression plan.

## Stop conditions

- Do not approve a publish-ready claim with unresolved blockers or unverified critical checks.
- Do not report visual/audio inspection when only a text description or source code was reviewed.
- Do not use fake numerical scores, probabilities, or measured loudness without evidence.
- If a file cannot be opened or inspected, label relevant checks `NOT_VERIFIED`.
- If rights, consent, or privacy concerns materially affect release, block or require a safe replacement/authorization.

## Shared references

Use `../godex-motion-audio/references/quality-and-risk-gates.md`, `../godex-motion-audio/references/output-contract.md`, and `../godex-motion-audio/references/inter-skill-contracts.md`.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/godex-motion-audio/godex-quality-assurance/skill.md


---

## Skill: godex-render-export

Source URI: skills://plugins/godex-motion-audio/godex-render-export

---
name: godex-render-export
description: Use when a motion-graphic production package needs renderer capability checks, project assembly, video composition, MP4 export, codec and frame-rate configuration, render troubleshooting, or a renderer-ready handoff.
---

# GODEX Render & Export

## Mission and boundary

Turn approved production specifications into an executable project or verified video export using only tools and runtimes actually available. This skill owns renderer capability discovery, adapter selection, assembly instructions, render configuration, export, and file-level verification. It does not invent a renderer, install dependencies without authorization, or equate generated code with a rendered MP4.

## Inputs

- Approved project manifest and scene timeline.
- Design tokens, assets and provenance.
- Motion specifications and renderer fallbacks.
- Audio voice-over, sound cues, captions, export target and constraints.
- Available host tools and execution permissions.

## Procedure

1. **Capability inventory:** verify file access, runtime/code execution, dependencies, font availability, media libraries, codecs, asset-generation route, render command/API, storage/export, and inspection capability independently.
2. **Select route:** native motion/video artifact with proven export; programmatic render with an actually available runtime; or renderer-ready handoff. Do not infer capability from product marketing, model name, or another user's plan.
3. **Dependency and rights check:** confirm referenced assets exist or are explicitly marked placeholder/missing; check licenses; pin available versions and avoid unsupported network/package installation assumptions.
4. **Single source of truth:** read timing and asset IDs from the project manifest. Do not duplicate conflicting hardcoded timestamps across code and subtitles.
5. **Assemble:** compose reusable components, place source voice-over, align visual scene timing, add captions and sound cues, preserve canvas dimensions and safe areas, and use fallback effects if the renderer lacks a requested feature.
6. **Proof render:** render a short or low-resolution section when feasible; inspect before full render.
7. **Full render:** execute only through a real available route. Capture actual result, errors, duration, file path or host attachment ID.
8. **Verify file:** check existence, openability, container, dimensions, frame rate, duration, video/audio streams, and synchronization using available tools. If some checks cannot be performed, mark `NOT_VERIFIED`.
9. **Troubleshoot:** classify errors (dependency, codec, font, missing asset, malformed timeline, resource limit, permission, host restriction). Make one evidence-based correction and retry where safe; do not loop blindly.
10. **Delivery:** package MP4 and source/project files where actually available. Report renderer route, versions, limitations, checks passed and unverified checks.

## Output contract

- `capability_matrix` with verified/unavailable/not-tested status and evidence.
- `renderer_route`: native/programmatic/handoff, tool/runtime and version only if verified.
- `project_artifacts`: path/ID, type, status, dependencies and asset references.
- `render_settings`: dimensions, aspect ratio, frame rate, duration, container, codecs, audio sample rate/channels where supported.
- `render_log` or exact failure class/message.
- `verification_report`.
- `delivery_state`: `RENDERED_VERIFIED`, `RENDERED_PARTIALLY_VERIFIED`, `RENDER_READY`, `BLUEPRINT_ONLY`, or `BLOCKED`.
- `next_action` for any blocker.

## Stop conditions

- Never claim rendering or export until a real operation succeeds and the resulting file is verified to the stated level.
- Do not fabricate file paths, download URLs, tool names, installed packages, supported codecs, or API endpoints.
- If a renderer is absent, create the strongest feasible renderer-ready handoff and state clearly that no MP4 exists.
- Do not export with missing critical assets, broken audio, invalid timeline, or unresolved rights as publish-ready.
- Do not transmit private audio/assets to external services without user authorization.

## Shared references

Use `../godex-motion-audio/references/rendering-and-platform-adapters.md`, `../godex-motion-audio/references/output-contract.md`, and `../godex-motion-audio/references/inter-skill-contracts.md`.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/godex-motion-audio/godex-render-export/skill.md


---

## Skill: godex-visual-art-direction

Source URI: skills://plugins/godex-motion-audio/godex-visual-art-direction

---
name: godex-visual-art-direction
description: Use when a motion-graphic project needs creative direction, visual identity, design tokens, typography, color palette, composition rules, illustration/icon direction, layout systems, reusable graphic components, or asset-generation briefs.
---

# GODEX Visual Art Direction

## Mission and boundary

Create one coherent and production-usable visual language for the project. This skill owns visual concept, art direction, design tokens, typography, palette, composition, safe areas, illustration/icon style, recurring components, and asset briefs. It does not invent brand rules, claim an asset has been generated when only a prompt exists, or produce scene motion keyframes.

## Inputs

- Approved narrative and scene plan.
- User-supplied logo, brand guide, images, fonts, and references, if available.
- Platform, aspect ratio, resolution, audience, and accessibility requirements.

## Procedure

1. Inspect supplied visual references and describe only visible traits: palette, type category, grid, shape language, texture, contrast, illustration method, and composition.
2. Separate confirmed brand requirements from inferred creative proposals. User-approved brand rules take precedence.
3. Write an art-direction statement: mood, energy, visual metaphor, illustration approach, density, audience context, and what to avoid.
4. Define design tokens with stable names: semantic colors (HEX only when selected), typography hierarchy and fallbacks, numeric style, grid/margins/gutters, safe areas, spacing, stroke, radius, shadow, texture, and component rules.
5. Define a visual hierarchy: focal point, primary message, supporting evidence, secondary labels, caption zone, and negative space.
6. Choose illustration/icon/diagram treatment based on semantic needs. Do not use decorative generic imagery where a diagram or direct explanation is clearer.
7. Create reusable components such as title card, section label, statistic card, quote panel, lower-third, diagram node, callout, CTA panel, and background motif as needed.
8. Create asset briefs with stable IDs, scene association, dimensions/aspect ratio, format, transparent-background requirement where relevant, source/rights status, and generation/acquisition prompt.
9. Ensure recurring objects and characters have continuity notes. Do not imply persistent character consistency from a one-off prompt alone; define reference assets or explicit continuity controls where the tools support them.
10. Test accessibility and legibility at target output dimensions: contrast, type size, safe areas, non-color cues, script/font coverage, and visual clutter.
11. Handoff design tokens, component rules, and asset manifest to Motion Design and Render & Export.

## Output contract

- `art_direction_statement`.
- `brand_constraints`: confirmed / inferred / missing.
- `design_tokens`: color, type, grid, spacing, shape, shadow, texture, motion-adjacent constraints.
- `typography_system`: category/family if verified, fallback, hierarchy, language/script coverage.
- `composition_rules` and safe areas.
- `illustration_icon_diagram_rules`.
- `reusable_components`.
- `asset_manifest_entries`: `asset_id`, description, type, scene IDs, target dimensions, source, rights status, generation brief, status (`provided`, `generated`, `licensed`, `placeholder`, `missing`).
- `accessibility_notes` and `handoff_notes`.

## Stop conditions

- Do not represent proposed colors, fonts, or visual styles as official brand identity.
- Do not invent asset existence, provenance, licenses, dimensions, or generation results.
- If the supplied visual reference contains unclear or conflicting requirements, record the conflict and use a reversible proposal or ask one focused question when the result materially depends on it.
- Do not use an asset with materially unclear rights as a publish-ready asset. Mark it unverified and propose a safe replacement.
- Do not create tiny or low-contrast text to satisfy an overloaded scene; simplify the message or split the scene.

## Shared references

Use `../godex-motion-audio/references/motion-design-system.md`, `../godex-motion-audio/references/output-contract.md`, and `../godex-motion-audio/references/inter-skill-contracts.md`. Own design-system and asset-description fields.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/godex-motion-audio/godex-visual-art-direction/skill.md
