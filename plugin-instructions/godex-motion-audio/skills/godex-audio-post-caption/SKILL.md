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
