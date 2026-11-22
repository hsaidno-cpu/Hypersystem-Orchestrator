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
