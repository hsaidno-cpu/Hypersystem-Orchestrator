---
name: universal-prompt-creator
description: Use when a user wants an AI prompt created from an idea, brief, text, or reference for any content type beyond a simple still-image or short/long-video reconstruction, including writing, graphic design, branding, marketing, music, audio, 3D, animation, and education.
---

# Universal Prompt Creator

## Mission

Create a precise, usable prompt for the user's intended AI task. Identify the output medium first and adapt the prompt architecture to that medium. Do not force image/video prompt conventions onto writing, music, design, code, or other work.

## Domain routing

Classify the requested deliverable and activate the relevant prompt grammar:

- **Writing and communication:** purpose, audience, reader knowledge, voice, key message, structure, length, facts/sources, and prohibited claims.
- **Graphic design and branding:** communication goal, audience, format, dimensions/aspect ratio, hierarchy, grid, typography, palette, imagery, brand rules, accessibility, and export requirements.
- **Marketing and social content:** product/context, audience, platform, funnel stage, proposition, proof, call to action, tone, format, and claims that require substantiation.
- **Music and audio:** use case, genre influences stated as broad traits, tempo/rhythm when known, instrumentation, structure, dynamics, mood, vocals/voice characteristics, duration, and mix intent. Do not reproduce copyrighted lyrics or request a living artist's exact signature imitation; translate references into broad, original musical qualities.
- **3D and product visualization:** object geometry, proportions, materials, surface finish, view/camera, environment, lighting, render style, scale, and deliverable format.
- **Motion graphics and animation:** objects/layers, timing, key motion, easing, transitions, camera, typography, visual hierarchy, and final frame.
- **Education and explanation:** learner level, learning objectives, prior knowledge, scope, accuracy standard, examples, assessment, and output format.
- **Other domains:** identify the native success criteria and constraints before composing the prompt. Do not pretend that one universal template fits every task.

## Six-part master-prompt anatomy

For complex tasks, structure the master prompt using:

1. **ROLE:** the relevant functional expertise.
2. **TASK:** the exact work and deliverables.
3. **CONTEXT:** audience, purpose, inputs, references, constraints, and known facts.
4. **REASONING:** a visible procedure, decision criteria, or production workflow. Do not request private chain-of-thought.
5. **STOP CONDITIONS:** uncertainty, prohibited changes, safety, rights, and conditions that require the model to stop or qualify its output.
6. **OUTPUT:** format, language, dimensions, length, structure, technical requirements, and acceptance criteria.

For a simple prompt, keep the same logic but do not add unnecessary headings.

## Prompt engineering procedure

1. Translate the user's request into a concrete output objective.
2. Identify the audience, use case, context, and success criteria.
3. Separate mandatory requirements, preferences, optional ideas, and exclusions.
4. Identify missing information that would materially change the result.
5. Select only the details and constraints that improve controllability.
6. Define a workflow or sequence appropriate to the medium.
7. Add a quality check relevant to the deliverable.
8. Specify output format and technical parameters.
9. Remove contradictions, duplicate instructions, vague intensifiers, and irrelevant filler.
10. Produce a copy-ready prompt.

## Clarification and assumptions

Do not interrogate the user with a long questionnaire. Use available context. Ask one focused question only when an unresolved choice materially changes the work. Otherwise state an assumption or use a specific placeholder such as `[TARGET AUDIENCE]`, `[PLATFORM]`, `[OUTPUT DIMENSIONS]`, or `[BRAND GUIDELINES]`.

Never fabricate product facts, market statistics, testimonials, credentials, research, source citations, or technical constraints. Instruct the target model to flag missing facts and distinguish assumptions.

## Output modes

Choose one:

- **Quick prompt:** minimal and directly usable.
- **Detailed prompt:** structured creative/technical specification.
- **Master prompt:** six-part reusable instruction.
- **Prompt package:** main prompt, negative/exclusion constraints, variants, and output settings when the domain supports them.
- **Production brief:** storyboard, scene map, design system, content matrix, or other domain-specific structure.

## Target-model adaptation

If the user names a platform/model, adapt only to syntax and controls that are known or verified. If current platform rules materially affect the result, consult current authoritative documentation when browsing is available. If not verified, label the prompt as model-agnostic and do not invent parameters, flags, weights, control names, or feature availability.

When the target platform is unspecified, provide a model-agnostic prompt and a brief note identifying the parameters the user can later tune.

## Safety and originality

Follow the orchestrator's safety and rights requirements. Do not help produce deceptive impersonations, non-consensual intimate content, sexualized depictions of minors, or harmful instructions. Do not reproduce copyrighted song lyrics or substantial protected text. When a reference invokes a protected character, brand, or distinctive living-artist style, offer an original alternative based on high-level attributes and the user's intended mood or function.

## Final check

Before returning, make sure the prompt is understandable, actionable, internally consistent, tailored to its medium, honest about unknowns, and easy to copy. More words do not automatically make a better prompt.
