---
name: long-video-engine
description: Use when a user wants a scene-by-scene reconstructed prompt for an accessible reference video longer than 10 seconds and up to 60 seconds, with character continuity and a reusable visual bible.
---

# Long Video Engine

## Mission

Convert an accessible reference video of **more than 10 seconds and up to 60 seconds** into a structured scene pack. The deliverable must preserve the observable story progression, visual language, shot logic, and continuity requirements across scenes.

This workflow creates a **continuity specification**, not a technical guarantee that every image/video generator will preserve the same character. Actual consistency may depend on reference-image support, character-reference features, seed control, model-specific tools, or post-production.

## Preflight and evidence limits

1. Confirm that the video itself, its frames, or a sufficiently detailed storyboard is actually accessible.
2. Establish duration from supplied or reliable evidence. Do not invent it.
3. Determine whether audio is accessible. If not, do not infer dialogue, music, or sound effects.
4. Identify what is directly observed versus inferred.
5. If full clip inspection is unavailable, use supplied keyframes or timestamped screenshots. State the evidence gap and do not claim full temporal coverage.
6. If the video exceeds 60 seconds, divide it into sequential segments of no more than 60 seconds each. Preserve the ending state of one segment as the starting continuity reference for the next.

## Scene segmentation protocol

Segment by meaningful shot or action changes, not by an arbitrary fixed number of scenes. A new scene/shot may be justified by:

- A clear cut, dissolve, wipe, or other transition.
- A major change in location or time.
- A meaningful change of camera setup or composition.
- A new action beat or story beat.
- A change in subject focus or visual point of view.

For every segment, record:

- Scene/shot number.
- Start and end timestamp; mark as approximate when not exact.
- Duration.
- Location and environment.
- Subjects present and their positions.
- Visible action and action progression.
- Camera framing, angle, movement, and focus.
- Lighting, color, atmosphere, and visual treatment.
- Props/costume/environment details that must persist.
- Transition into the next segment.
- Audio only when supplied or genuinely accessible.

Check that segment durations cover the known runtime without unexplained gaps or overlaps. If a timestamp cannot be verified, label it instead of inventing precision.

## Character Identity Blueprint

For each recurring character, create an identity anchor containing only visible, relevant attributes:

- Stable label/name used only as a production reference, not a claim about real identity.
- Approximate age category only when necessary and clearly apparent; do not guess exact age.
- Face shape and distinctive non-sensitive visible features.
- Hair, facial hair, clothing, accessories, and color details.
- Body proportions, posture, and movement style where visible.
- Distinctive props or identifying costume elements.
- Attributes that must not change across scenes.
- Attributes that may change naturally, such as pose, expression, or location.
- Uncertain attributes requiring confirmation.

Do not infer ethnicity, religion, health, sexuality, personality, or other sensitive personal attributes from appearance. Do not identify a real person.

Repeat the most important identity anchors in each scene prompt where a generator may otherwise drift. If the platform supports reference images, character IDs, or seed controls, recommend them as optional controls. Never imply that repeating text alone guarantees an identical face.

## Visual and world continuity bible

Create shared anchors for:

- Overall visual language and rendering approach.
- Color palette and contrast.
- Lighting logic and time-of-day continuity.
- Location geometry and recurring set dressing.
- Costume and prop continuity.
- Camera grammar, movement style, and lens character where supportable.
- Atmosphere and environmental conditions.
- Aspect ratio and other user-specified output settings.

Separate **locked invariants** from **allowed changes**. Do not lock an element that visibly changes in the source.

## Scene prompt construction

Each scene prompt should contain:

1. Global style anchor, concise and consistent.
2. Character identity anchor(s) needed in that scene.
3. Location and spatial arrangement.
4. Exact action beat and its order.
5. Starting composition and intended end state.
6. Camera framing, angle, and movement.
7. Lighting, palette, and atmosphere.
8. Required props/costume details.
9. Transition or connection to the next scene.
10. Negative constraints relevant to that scene.

Do not put mutually incompatible camera instructions in a single prompt. Avoid asking for several unrelated actions within a very short scene. If a scene is too dense, divide it or simplify it while preserving the key action.

## Output contract

### A. Reference analysis
Summarize the story, total duration, visual language, and known limitations of the reference inspection.

### B. Character Identity Blueprint
Give one reusable identity anchor per recurring character. Mark uncertain attributes.

### C. Global Visual Continuity Bible
List locked visual invariants, allowed variations, environment/prop continuity, and platform-dependent controls.

### D. Scene map
Use a table:

| Scene | Time | Duration | Action/Story Beat | Camera | Transition |
|---|---|---|---|---|---|

Use approximate timestamps only when exact timing is unavailable.

### E. Scene-by-scene prompts
Provide a separate copy-ready prompt block for every scene. Keep shared anchors stable and tailor only the scene-specific action, framing, and environment.

### F. Negative constraints and continuity checklist
Include only relevant failure-prevention instructions: character drift, costume changes, face morphing, prop disappearance, location jumps, lighting flicker, unintended cuts, inconsistent screen direction, or other source-specific issues.

### G. Assembly notes
Explain the intended scene order, transition continuity, and which platform controls may help. Do not assume the generator can join clips or preserve state automatically.

## Continuity control hierarchy

Prefer, in order where available:

1. A verified reference image or character reference feature.
2. Reusable character/style assets or supported IDs.
3. Stable prompt anchors repeated across scenes.
4. Matching environment, costume, lighting, and camera constraints.
5. Post-generation review and correction.

The exact availability of these controls varies by generator. If the platform is unknown, describe them as conditional options.

## Stop conditions

Do not produce a falsely precise scene map when the clip or its timestamped frames are unavailable. Do not invent missing scene events, dialogue, sounds, or character details. If the user asks for a perfect clone, explain that prompt reconstruction cannot guarantee identical outputs, and offer a close visual/structural approximation instead.

Follow the orchestrator's safety, privacy, and rights requirements.
