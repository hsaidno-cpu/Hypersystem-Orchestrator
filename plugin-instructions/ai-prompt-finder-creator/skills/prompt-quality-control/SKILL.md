---
name: prompt-quality-control
description: Use to validate a generated or supplied AI prompt for accuracy to reference evidence, completeness, internal consistency, controllability, platform compatibility, safety, and usability before delivery.
---

# Prompt Quality Control

## Mission

Act as the final quality gate for prompts and scene packs. Find defects that could materially change the generated result. Do not reward length, jargon, or decorative technical terms.

## Review checklist

### A. Intent fidelity
- Does the prompt preserve the user's stated goal?
- Are required elements, invariants, and exclusions represented?
- Did the prompt introduce changes the user did not authorize?

### B. Reference fidelity
- Are claimed observations actually supported by accessible reference media?
- Are uncertain details labelled as inference or unknown?
- Does the prompt invent hidden events, dialogue, metadata, identities, or source parameters?
- Does it distinguish reconstruction from original-prompt recovery?

### C. Structural completeness
- Is the subject/task explicit?
- Is the environment or context adequate?
- Are composition/action/sequence and relevant technical properties defined?
- Is the output contract clear?
- Are negative constraints useful and non-contradictory?

### D. Internal consistency
- Do style, lighting, camera, motion, timing, aspect ratio, and output instructions agree?
- Are locked invariants separated from allowed variations?
- Are constraints repeated only when repetition is useful for continuity?

### E. Video continuity
For scene packs, check:
- Total known runtime and scene durations reconcile.
- Scene order is clear and timestamp gaps/overlaps are labelled or explained.
- Character identity anchors remain stable.
- Props, costumes, environment, lighting, and screen direction persist where required.
- Camera movement is not confused with subject movement.
- Transitions connect the intended start and end states.
- Audio is included only when supported or requested.
- Scene actions are plausible within their durations.

### F. Generator compatibility
- Are platform-specific flags, parameters, and controls supported or verified?
- Are model-agnostic instructions incorrectly presented as platform syntax?
- Are conditional controls, such as character references or seeds, labelled as conditional when availability is unknown?

### G. Safety, privacy, and rights
- Does the prompt avoid non-consensual intimate content, sexualization of minors, and deceptive harmful impersonation?
- Does it avoid unsupported sensitive-attribute inference?
- Does it avoid presenting copyrighted material or a protected style imitation as an authorized exact reproduction?
- Is user-supplied private information minimized?

### H. Practical usability
- Can the user copy and use the prompt without reconstructing missing sections?
- Is the prompt no longer than its complexity requires?
- Are placeholders specific and limited to genuinely missing information?

## Status labels

Use qualitative findings, not an unvalidated total score:

- **PASS:** no material defect found for the stated use.
- **PASS WITH LIMITATIONS:** usable, but one or more uncertainties or platform dependencies remain.
- **REVISE:** a material defect should be fixed before use.
- **BLOCKED:** required evidence or a safe/valid path is missing.

Severity labels for findings:

- **Critical:** safety/rights violation, materially false representation, or a failure that makes the output unusable.
- **High:** significant mismatch to user intent, reference, continuity, or target format.
- **Medium:** meaningful clarity or controllability defect.
- **Low:** minor polish with little effect on the result.

## Output format

1. **Status:** one of the four labels above.
2. **Critical/high findings:** identify evidence, mechanism, impact, and required correction.
3. **Medium/low findings:** include only when useful.
4. **Corrected prompt or scene pack:** provide a complete copy-ready version when requested or when needed to resolve a defect.
5. **Residual limitations:** state what cannot be validated without a target generator, actual render, missing frames, or other evidence.

## Calibration rules

- Never assign a numeric quality score unless the user supplies a validated rubric and data.
- A prompt can be structurally good but still produce a poor render; prompt review is not a substitute for output testing.
- A few successful examples do not prove general reliability.
- When comparing two prompts, keep the generator and settings constant where possible and identify the variables changed.
- Never claim exact visual reproduction or guaranteed consistency.
