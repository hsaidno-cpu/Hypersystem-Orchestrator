---
name: motion-narrative-storyboard
description: Use when a verified voice-over or approved brief must be translated into semantic beats, new visual scene concepts, a scene-by-scene storyboard, and traceable timing without copying reference-video content.
---

# Motion Storyboard & Scene Planner

## ROLE

Turn the narrative map and verified VO segments into a scene plan. This skill owns WHAT each scene communicates and HOW the scene concept explains it; it does not own the detailed design system or keyframe choreography.

## TASK

Segment the narration into semantic beats and plan new scenes with clear purpose, visual concept, action, timing confidence, transition intent, and dependencies.

## REASONING

1. Start from verified VO segments or the approved brief, not from the reference shot order.
2. For each beat record: source phrase/segment, intended understanding, key information, emotional energy, and audience takeaway.
3. Select literal demonstration, metaphor, character action, object animation, environment, diagram, comparison, or typography according to the communication need.
4. Make each scene materially different from the reference's expressive content while remaining compatible with its abstract style rules.
5. One scene may cover multiple coherent phrases; one phrase may need multiple scenes. Scene count follows communication density, not the reference count.
6. Assign stable `SCN` IDs, source VO IDs, timing evidence and confidence, narrative transition, visual dependencies, and open questions.
7. Run a semantic coverage check: every material VO beat must be represented, and every scene must justify itself against a beat or brief objective.

## OUTPUT

Scene-by-scene storyboard with scene ID, source VO/brief span, meaning, communication goal, visual concept, action, emotional energy, time range and timing status, transition intent, assets, and dependencies. Include omitted/combined narration spans with rationale.

## STOP CONDITIONS

Do not change the source VO, invent facts, select visuals only because they appear in the reference, or claim precise timing from text alone. Revise any scene with no clear semantic link to the source.
