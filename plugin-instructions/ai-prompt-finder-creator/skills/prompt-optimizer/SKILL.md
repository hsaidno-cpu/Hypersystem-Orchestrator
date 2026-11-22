---
name: prompt-optimizer
description: Use when a user provides an existing prompt and wants it audited, debugged, shortened, expanded, translated, modularized, or adapted to a target AI generator.
---

# Prompt Optimizer

## Mission

Improve an existing prompt without losing the user's intended outcome. Diagnose the mechanism behind each important weakness, then produce a revised prompt and a concise change log.

## Audit dimensions

Inspect only the dimensions relevant to the task:

1. **Objective clarity:** is the requested result observable and specific?
2. **Context sufficiency:** does the prompt provide the information the model needs without irrelevant detail?
3. **Instruction hierarchy:** are priorities and non-negotiable constraints clear?
4. **Specificity:** are subject, action, style, audience, format, or technical requirements sufficiently defined?
5. **Consistency:** are there contradictions, mutually incompatible styles, camera directions, or output demands?
6. **Control and flexibility:** does the prompt lock essential elements while leaving creative room where appropriate?
7. **Evidence discipline:** does it require the target model to invent unsupported facts or infer unavailable details?
8. **Output contract:** are format, language, length, dimensions, scenes, or deliverables explicit?
9. **Target compatibility:** does it use syntax and controls supported by the named generator?
10. **Efficiency:** can filler, repetition, overlong negative prompts, or redundant adjectives be removed?
11. **Safety and rights:** does the prompt cross privacy, consent, safety, or intellectual-property boundaries?

## Optimization workflow

1. Preserve the core objective and any explicit invariant.
2. Identify the highest-impact problems. Do not pad the audit with cosmetic criticism.
3. Explain what each problem causes in model behavior or output quality.
4. Rewrite the prompt with a clear hierarchy and appropriate structure.
5. Retain useful original phrasing when it is already precise.
6. Replace vague terms with observable constraints or examples where possible.
7. Resolve conflicting requirements explicitly; if no valid resolution exists, state the conflict.
8. Adapt for the target model only when compatibility is known or verified.
9. Run the quality-control checklist.

## Optimization modes

- **Repair:** fix defects while preserving most of the original prompt.
- **Rebuild:** reconstruct the prompt architecture when the original is structurally weak.
- **Compress:** shorten without removing critical constraints.
- **Expand:** add missing context, workflow, and acceptance criteria.
- **Platform adaptation:** translate to another generator, clearly identifying features that may not transfer.
- **A/B variants:** create 2–3 materially different prompt strategies for comparison.

## Output format

1. **Verdict:** one-paragraph assessment of the current prompt.
2. **Priority issues:** problem, why it matters, and fix. Omit minor issues.
3. **Optimized prompt:** complete copy-ready version in a code block.
4. **Change log:** key changes and their intended effect.
5. **Limitations:** uncertain platform syntax, missing inputs, or results that require empirical testing.

If the user asks for only the rewritten prompt, omit the audit and return only the revised prompt.

## Testing discipline

Do not claim that a revision is empirically better without comparable outputs. Recommend a controlled test when quality differences are uncertain: keep the generator, settings, and source constant, change one prompt variable at a time, and compare against explicit criteria. Treat the result as an observation, not universal proof.

Do not request or expose private chain-of-thought. Summarize the editing rationale instead. Follow the orchestrator's safety, privacy, and rights requirements.
