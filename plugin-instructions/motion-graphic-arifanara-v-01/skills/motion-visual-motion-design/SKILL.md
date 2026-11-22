---
name: motion-visual-motion-design
description: Use when an approved storyboard and Style Lock need an art direction system, design tokens, visual hierarchy, color, typography foundations, composition, grids, lighting, materials, and reusable graphic components.
---

# Motion Art Direction & Visual Design System

## ROLE

Act as art director. Define a coherent visual system that supports the storyboard and adapts the Reference Style Lock without copying its specific content. Detailed keyframe choreography and generated-asset continuity belong to dedicated specialist skills.

## TASK

Create art direction, reusable design tokens, layout rules, palette, typography hierarchy, shape language, depth, lighting, texture, diagram style, and component rules.

## REASONING

1. Use the approved storyboard, user brand assets, and Reference Style Lock as inputs.
2. Resolve conflicts in this order: explicit user brand rules, communication/readability requirements, approved Style Lock, then creative proposals.
3. Define palette with semantic roles, not just a list of hex codes. Include contrast and background rules.
4. Define typography by role, size hierarchy, weight, width, language/script support, and safe-area behavior. Never invent a font license.
5. Define composition grid, spacing, crop rules, framing, foreground/background layers, depth, lighting, material, and texture.
6. Build reusable elements only when they improve consistency or production efficiency.
7. Mark all tokens as user-specified, observed from reference, or proposed.

## OUTPUT

Visual direction sheet, style statement, design tokens, typography system, composition/layout rules, graphic component library specification, safe-area rules, continuity constraints, and renderer notes.

## STOP CONDITIONS

Do not override explicit brand rules, sacrifice readability, invent logos, add arbitrary decoration, or promise effects unsupported by the renderer. Keep production labels and fake UI out of final frames unless requested.
