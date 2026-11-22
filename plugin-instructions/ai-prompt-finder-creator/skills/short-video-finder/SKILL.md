---
name: short-video-finder
description: Use when a user wants to reconstruct an AI video prompt from an accessible reference clip with a duration of 10 seconds or less, including action, camera movement, timing, and transitions.
---

# Short Video Finder

## Mission

Turn an accessible video reference of **10 seconds or less** into a concise, time-aware video prompt. Reconstruct observable visual and temporal information; never claim to know the hidden original prompt, seed, model, or editing parameters.

## Access preflight

Before analysis, confirm that the clip or its frames are actually accessible in the current conversation. If only a filename, link, or verbal reference is present and the media cannot be opened, do not pretend to have inspected it. Ask for the clip to be attached in a supported way or for timestamped keyframes and a short action description.

Do not assume that the environment can decode every frame or audio track. Describe the sampling basis when it materially limits accuracy.

## Temporal analysis

Map the clip using the evidence available:

1. Establish total duration only when supplied or reliably visible.
2. Identify shot boundaries and transitions. If it is one continuous shot, do not invent multiple scenes.
3. Record the main action as a sequence of observable states: start, development, peak, and end.
4. Describe subject movement separately from camera movement.
5. Track camera behavior: static, pan, tilt, dolly, tracking, handheld, orbit, zoom, or other movement only when observable.
6. Record important changes in framing, focus, lighting, environment, and subject orientation.
7. Note pacing and transition style without inventing exact frame rates.
8. Include audio, dialogue, sound effects, and music only if actually accessible or explicitly supplied by the user.

Use timestamps only to the precision supported by the media. If exact cut times are not available, label them approximate. Never fabricate dialogue or claim that an inaudible sound exists.

## Prompt construction

Build one continuous-shot prompt or a compact scene/timeline prompt depending on the clip. Preserve the sequence of actions and the relationship between camera and subject.

Include as relevant:
- Subject and appearance.
- Setting and visual context.
- Opening composition.
- Action progression and timing.
- Subject motion and camera motion as separate instructions.
- Lighting, color, atmosphere, and material detail.
- Shot continuity and transition behavior.
- Audio instructions only when grounded or requested.
- Duration and aspect ratio supplied by the user.

Do not overload a short clip with too many independent actions. If the requested actions cannot plausibly fit within the duration, explain the conflict and simplify or propose a longer clip.

## Output contract

### Reference breakdown
A short summary of the observable subject, setting, action, camera, lighting, and transitions.

### Timeline
Use a table with approximate or verified timestamps, visible action, camera behavior, and transition. For a continuous shot, state that it is one shot.

### Reconstructed video prompt
Provide one copy-ready prompt in a code block, with duration and aspect ratio only when known or specified.

### Negative constraints
List only relevant exclusions, such as unintended cuts, subject morphing, flicker, warped anatomy, inconsistent props, or camera movement that contradicts the reference. Do not assume every generator supports a separate negative-prompt field.

### Continuity notes
Protect the visible identity and attributes that matter between moments. Avoid promising perfect consistency from text alone.

## Limits

A 10-second clip may contain more visual information than can be established from a few sampled frames. State what could not be verified. A reconstructed prompt is an informed approximation, not a recovery of the source prompt or a guarantee of identical motion.

Follow the orchestrator's safety, privacy, and rights requirements.
