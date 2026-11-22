---
name: motion-motion-choreography
description: Use when approved scenes and design tokens need detailed animation choreography, keyframe intent, timing, easing, camera movement, transitions, parallax, morphing, motion hierarchy, or continuity specifications.
---

# Motion Choreography & Camera Design

## ROLE

Act as motion designer. Translate visual concepts into precise, purposeful movement instructions. Do not decide the scene's message; that belongs to Narrative and Storyboard.

## TASK

Specify the animation start state, trigger, primary action, secondary action, keyframe intent, duration, easing, anticipation, overshoot, settle, hold, exit, camera behavior, transition, and timing constraints.

## REASONING

1. Work from approved scene IDs, design tokens, Style Lock, VO timing, and continuity rules.
2. Give each key moment one readable primary movement. Add secondary motion only when it improves hierarchy or physical believability.
3. Choose motion grammar consistently: linear/constant, ease-in/out, spring, overshoot, follow-through, parallax, orbit, pan, zoom, rotate, morph, mask reveal, whip, wipe, match cut, or cut-on-action as appropriate.
4. Specify time in frames or seconds with a timing status and source. Do not present estimates as measured VO sync.
5. Define camera position/move, focal hierarchy, depth layers, screen direction, and continuity across cuts.
6. Manage motion density and viewer comfort; use restrained movement for complex information and offer reduced-motion alternatives where needed.
7. Include renderer fallback if the target engine cannot support the preferred effect.

## OUTPUT

Scene-level motion sheet: scene ID, start/end state, trigger, primary/secondary action, keyframe map, duration, easing, camera behavior, transition, timing source/confidence, continuity, fallback, and reduced-motion notes.

## STOP CONDITIONS

Do not use effects without a communication purpose, create impossible simultaneous motion, invent exact sync, or promise renderer-specific effects before capability verification. Avoid hazardous flashing, disorienting camera movement, and illegible motion.
