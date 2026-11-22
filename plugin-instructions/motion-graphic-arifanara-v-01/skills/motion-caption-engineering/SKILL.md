---
name: motion-caption-engineering
description: Use when a motion-graphics project requires subtitles, captions, SRT/VTT files, word/phrase segmentation, translation/localization, speaker labels, safe-area placement, or caption timing and QA.
---

# Motion Caption & Subtitle Engineering

## ROLE

Create readable, synchronized captions from verified speech or user-approved copy. Do not invent transcript text or precision timestamps.

## TASK

Prepare caption copy, line segmentation, timing, speaker labels, SRT/VTT or renderer-ready caption data, localization, and caption quality checks.

## REASONING

1. Use the verified transcript and timing evidence from Audio Intelligence.
2. Preserve wording, numbers, names, and terminology. Mark uncertain transcript spans.
3. Segment captions by readable phrases, speech rhythm, syntactic units, and screen space; avoid splitting names or tightly linked phrases.
4. Use exact timecodes only when actual alignment evidence supports them. Label provisional timing where estimated.
5. Respect requested caption style, language, accessibility, safe areas, contrast, line length, and platform constraints.
6. For translation, preserve meaning and note adaptation decisions; do not claim certified translation.
7. Generate SRT/VTT only when the output file can actually be created; otherwise return structured caption data.

## OUTPUT

Caption plan, subtitle text, segment IDs, in/out times and timing status, SRT/VTT or structured file if created, localization notes, and readability/accessibility QA.

## STOP CONDITIONS

Do not invent transcript, speaker names, or word-perfect timecodes. Do not add captions when explicitly forbidden unless the platform/legal/accessibility context requires a disclosed recommendation. Do not let captions obscure essential visuals.
