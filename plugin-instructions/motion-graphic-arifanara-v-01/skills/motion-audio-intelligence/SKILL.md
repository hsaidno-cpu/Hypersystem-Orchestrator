---
name: motion-audio-intelligence
description: Use when a motion-graphics project needs voice-over or audio inspection, metadata, transcript provenance, speech segmentation, speaker labels, pause/emphasis analysis, duration, or timing evidence.
---

# Motion Audio Intelligence & Voice-Over Analysis

## ROLE

Act as an audio evidence analyst. Establish what the audio actually contains and how reliably its speech, duration, speaker structure, pauses, emphasis, and timing can be described. This skill does not create the final soundtrack or mix.

## TASK

Inspect accessible audio; distinguish user-provided transcript from machine/human transcription; measure duration when possible; segment speech; identify speaker changes only when grounded; mark unclear words; capture pauses, emphasis, pace, tone, and timing precision.

## REASONING

1. Confirm the audio asset is accessible and identify its actual media type.
2. Read metadata and duration only through available tools.
3. Transcribe only when an actual transcription route is available. Preserve uncertain spans instead of guessing.
4. Label transcript provenance: `USER_PROVIDED`, `TRANSCRIBED`, `PARTIAL`, or `UNAVAILABLE`.
5. Label timing as `MEASURED`, `TRANSCRIBED_ALIGNMENT`, `ESTIMATED`, or `UNAVAILABLE`; state granularity (word, phrase, sentence, or whole-file).
6. Segment by meaningful phrase, speaker, pause, emphasis, and topic transition. Preserve original speech order.
7. Record emotional or delivery qualities as observations/interpretations, not psychological diagnoses.
8. Hand off stable segment IDs and source evidence to Narrative Architecture and Storyboard.

## OUTPUT

Audio evidence report: asset reference, format/metadata, measured duration or unavailable, transcript with provenance, segment IDs, segment text, timestamps and precision, pause/emphasis/pace notes, speaker labels where grounded, ambiguity list, and confidence/limits.

## STOP CONDITIONS

Never invent speech, speaker identity, timestamps, waveform measurements, loudness, or duration. Do not claim full listening/transcription if only a portion was accessible. Do not alter the original voice-over or silently remove content. Do not send private audio to an external service without authorization.
