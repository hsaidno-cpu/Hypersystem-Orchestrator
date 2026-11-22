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
