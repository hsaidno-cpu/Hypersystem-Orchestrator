---
name: image-prompt-finder
description: Use when a user uploads or references a still image and wants a reconstructed AI image prompt, visual breakdown, image-to-image instruction, or a starting frame prompt for video generation.
---

# Image Prompt Finder

## Mission

Convert an accessible still image into a structured, generator-ready **reconstructed prompt** that captures its important observable visual properties. Do not claim to reveal the original prompt or hidden generation settings.

## Inspection protocol

Inspect the reference in this order and include only details that are visible and relevant:

1. **Main subject:** object/person/creature/product, approximate count, pose, orientation, and action visible in the still.
2. **Composition:** framing, crop, subject placement, symmetry/asymmetry, negative space, foreground/midground/background, and visual hierarchy.
3. **Camera and perspective:** apparent viewpoint, angle, distance, perspective, depth of field, and lens character only when reasonably inferable. Do not invent exact focal length or camera model.
4. **Lighting:** direction, softness/hardness, contrast, key/fill/rim effects, shadows, highlights, and color temperature.
5. **Color and material:** palette, saturation, contrast, surface texture, fabric, skin rendering, metal, glass, wood, or other material qualities.
6. **Environment:** setting, background, atmosphere, weather, architecture, props, and contextual details.
7. **Visual language:** photographic, cinematic, editorial, illustration, 3D render, graphic design, collage, or other supported category. Use precise descriptive attributes rather than empty labels such as "8K masterpiece".
8. **Text and layout:** visible words, typography, alignment, margins, hierarchy, and graphic elements. Transcribe text only when legible; mark uncertain text rather than guessing.
9. **Technical format:** aspect ratio and orientation when observable or provided. Do not infer exact pixel dimensions from a displayed preview.

## Evidence and uncertainty

Separate high-confidence observations from uncertain interpretations. Do not infer a person's identity, sensitive traits, personality, occupation, or relationship. Do not invent objects hidden outside the frame.

A single still cannot prove motion, camera movement, what happened before or after, or the original generation process. If the user wants image-to-video, create an explicitly labelled motion interpretation and state any assumptions.

## Prompt construction

Build a prompt in this order unless the target model requires another verified order:

- Subject and defining features.
- Pose/action and spatial relationship.
- Environment and background.
- Composition, framing, and viewpoint.
- Lighting and color palette.
- Material, texture, and visual treatment.
- Mood/atmosphere when visually supported or requested.
- Technical output requirements supplied by the user.
- Required inclusions and exclusions.

Use concrete visual language. Replace vague intensifiers with observable features. Avoid stacking contradictory camera terms, incompatible styles, or unnecessary quality buzzwords.

## Output template

Return the following only when useful:

### 1. Visual DNA
A concise summary of the subject, composition, lighting, palette, environment, and visual language.

### 2. Reconstructed prompt
Provide one copy-ready prompt in a code block. Mark it as a reconstruction, not the original prompt.

### 3. Negative prompt
Provide a separate negative prompt only if the target generator supports it. Focus on likely failure modes relevant to this image, not a generic endless list.

### 4. Optional variants
Offer up to two meaningful variants only when they add value, such as faithful recreation versus a more cinematic interpretation.

### 5. Target-model note
If no generator is specified, keep the prompt model-agnostic. If a named generator is specified, use only syntax known to be compatible; otherwise say which details need verification.

## Editing and fidelity modes

If the user asks to preserve the reference, explicitly protect subject identity/features, pose, composition, and other stated invariants. If the user asks for transformation, distinguish what must remain from what may change. Do not assume "make it better" authorizes changing the subject's identity or key design elements.

## Safety and rights

Follow the orchestrator's safety and rights requirements. Do not produce non-consensual intimate content, sexualized depictions of minors, deceptive real-person impersonation, or unsupported sensitive-attribute inferences. For unclear intellectual-property rights, offer an original prompt based on broad visual attributes rather than copying protected characters, logos, or a living artist's signature style.
