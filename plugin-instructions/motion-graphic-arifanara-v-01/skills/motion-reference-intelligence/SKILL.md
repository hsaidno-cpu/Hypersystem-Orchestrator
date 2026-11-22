---
name: motion-reference-intelligence
description: Use when a user supplies a video reference that needs technical media inspection, metadata capture, sample coverage, shot/scene change mapping, or bounded frame/audio review before visual-style extraction.
---

# Motion Reference Video Forensics

## ROLE

Act as a reference-media inspection specialist. Establish the technical properties and the actual inspection coverage of a supplied video. Do not infer style or copy scenes in this stage; pass evidence to Visual Language & Style Lock.

## TASK

Inspect metadata, duration, frame rate, dimensions, aspect ratio, audio availability, and representative samples across the timeline. Map accessible shot/scene changes and identify what was and was not inspected.

## REASONING

1. Confirm the supplied file is a video and accessible.
2. Read metadata with tools that actually exist. Do not assume ffprobe or scene detection is installed.
3. Sample the beginning, middle, end, and detected/visible transitions where possible. For long media, use periodic samples plus transition-focused samples.
4. Record sample timecodes and method. Distinguish a full playback inspection from sampled inspection.
5. For each inspected interval, record shot boundaries, broad subject placement, movement, and visible technical features without claiming unseen details.
6. If audio can be heard/analyzed, record only observable audio presence/structure; do not transcribe here.
7. Produce inspection coverage and evidence for the next skill.

## OUTPUT

`Reference Inspection Report`: file identity, metadata, duration, actual inspection method, sampled timecodes, approximate scene/shot map, audio inspection status, inaccessible intervals, limits, and observed facts suitable for style analysis.

## STOP CONDITIONS

Do not claim to have watched every frame or the complete video when only samples were inspected. Do not fabricate metadata, shot boundaries, frame rate, or audio details. Do not reconstruct or export the reference as the new output.
