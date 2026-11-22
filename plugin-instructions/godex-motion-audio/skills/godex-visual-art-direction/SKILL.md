---
name: godex-visual-art-direction
description: Use when a motion-graphic project needs creative direction, visual identity, design tokens, typography, color palette, composition rules, illustration/icon direction, layout systems, reusable graphic components, or asset-generation briefs.
---

# GODEX Visual Art Direction

## Mission and boundary

Create one coherent and production-usable visual language for the project. This skill owns visual concept, art direction, design tokens, typography, palette, composition, safe areas, illustration/icon style, recurring components, and asset briefs. It does not invent brand rules, claim an asset has been generated when only a prompt exists, or produce scene motion keyframes.

## Inputs

- Approved narrative and scene plan.
- User-supplied logo, brand guide, images, fonts, and references, if available.
- Platform, aspect ratio, resolution, audience, and accessibility requirements.

## Procedure

1. Inspect supplied visual references and describe only visible traits: palette, type category, grid, shape language, texture, contrast, illustration method, and composition.
2. Separate confirmed brand requirements from inferred creative proposals. User-approved brand rules take precedence.
3. Write an art-direction statement: mood, energy, visual metaphor, illustration approach, density, audience context, and what to avoid.
4. Define design tokens with stable names: semantic colors (HEX only when selected), typography hierarchy and fallbacks, numeric style, grid/margins/gutters, safe areas, spacing, stroke, radius, shadow, texture, and component rules.
5. Define a visual hierarchy: focal point, primary message, supporting evidence, secondary labels, caption zone, and negative space.
6. Choose illustration/icon/diagram treatment based on semantic needs. Do not use decorative generic imagery where a diagram or direct explanation is clearer.
7. Create reusable components such as title card, section label, statistic card, quote panel, lower-third, diagram node, callout, CTA panel, and background motif as needed.
8. Create asset briefs with stable IDs, scene association, dimensions/aspect ratio, format, transparent-background requirement where relevant, source/rights status, and generation/acquisition prompt.
9. Ensure recurring objects and characters have continuity notes. Do not imply persistent character consistency from a one-off prompt alone; define reference assets or explicit continuity controls where the tools support them.
10. Test accessibility and legibility at target output dimensions: contrast, type size, safe areas, non-color cues, script/font coverage, and visual clutter.
11. Handoff design tokens, component rules, and asset manifest to Motion Design and Render & Export.

## Output contract

- `art_direction_statement`.
- `brand_constraints`: confirmed / inferred / missing.
- `design_tokens`: color, type, grid, spacing, shape, shadow, texture, motion-adjacent constraints.
- `typography_system`: category/family if verified, fallback, hierarchy, language/script coverage.
- `composition_rules` and safe areas.
- `illustration_icon_diagram_rules`.
- `reusable_components`.
- `asset_manifest_entries`: `asset_id`, description, type, scene IDs, target dimensions, source, rights status, generation brief, status (`provided`, `generated`, `licensed`, `placeholder`, `missing`).
- `accessibility_notes` and `handoff_notes`.

## Stop conditions

- Do not represent proposed colors, fonts, or visual styles as official brand identity.
- Do not invent asset existence, provenance, licenses, dimensions, or generation results.
- If the supplied visual reference contains unclear or conflicting requirements, record the conflict and use a reversible proposal or ask one focused question when the result materially depends on it.
- Do not use an asset with materially unclear rights as a publish-ready asset. Mark it unverified and propose a safe replacement.
- Do not create tiny or low-contrast text to satisfy an overloaded scene; simplify the message or split the scene.

## Shared references

Use `../godex-motion-audio/references/motion-design-system.md`, `../godex-motion-audio/references/output-contract.md`, and `../godex-motion-audio/references/inter-skill-contracts.md`. Own design-system and asset-description fields.
