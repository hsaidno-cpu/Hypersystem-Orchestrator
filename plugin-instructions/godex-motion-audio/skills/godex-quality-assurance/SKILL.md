---
name: godex-quality-assurance
description: Use when a storyboard, render, caption file, audio mix, asset package, or complete GODEX project needs systematic review, failure-mode analysis, technical checks, accessibility checks, release gating, defect triage, or correction-loop planning.
---

# GODEX Quality Assurance

## Mission and boundary

Independently evaluate the production against the agreed brief and observable evidence. This skill owns QA criteria, verification status, defect severity, release recommendation, and targeted correction routing. It does not silently repair upstream creative work or certify media it has not inspected.

## Inputs

- User brief and approved project manifest.
- Transcript provenance, scene plan, design tokens, motion and caption specifications.
- Asset manifest and rights status.
- Rendered file or renderer-ready project, plus any available preview/inspection tools.

## Procedure

1. **Define acceptance criteria:** extract platform specs, narrative requirements, accessibility, rights, deliverables, and user-specific constraints.
2. **Check evidence:** separate actual inspection, metadata checks, static specification review, and unverified assertions. Each check receives `PASS`, `FAIL`, `PARTIAL`, `NOT_VERIFIED`, or `NOT_APPLICABLE`.
3. **Narrative fidelity:** confirm every scene maps to source narration; names, figures, quotations and claims are preserved; no visual contradicts the message.
4. **Timing:** confirm scene boundaries and subtitle cues fit the verified timeline; flag unsupported word timing, cut syllables, gaps, overlap, or drift.
5. **Visual:** inspect hierarchy, consistency, typography, contrast, safe areas, cropping, asset continuity, clutter, and visual meaning.
6. **Motion:** inspect purpose, readability, pacing, transition consistency, motion overload, flashing, camera comfort, and renderer fallback.
7. **Audio:** check voice intelligibility, music/SFX competition, clipping, unwanted silence, cuts, fades, synchronization, and rights. Only claim measured audio properties where actual measurements/listening support them.
8. **Technical:** inspect file opens, expected streams, duration, frame rate, resolution, codec/container, blank frames, missing media, and export compatibility where tools permit.
9. **Accessibility and rights:** check captions, color-only cues, text size, reduced-motion concerns, licensing/provenance, consent, and private information.
10. **Defect triage:** classify severity as `BLOCKER`, `MAJOR`, `MINOR`, or `OBSERVATION`; include evidence, affected IDs, likely owner skill, repair instruction, and retest scope.
11. **Correction loop:** send defects to the narrowest responsible stage. Preserve unaffected approvals and rerun only the checks invalidated by the change, plus regression checks.
12. **Release decision:** approve only when required gates pass. Unverified items must remain visible and cannot be silently treated as passed.

## Output contract

- `acceptance_criteria`.
- `check_results`: criterion, status, evidence, scope and limitation.
- `defects`: ID, severity, description, evidence, affected scene/asset/cue IDs, owner skill, correction, retest requirement.
- `risk_summary` with residual risks.
- `release_decision`: `APPROVE`, `APPROVE_WITH_LIMITATIONS`, `REWORK_REQUIRED`, or `BLOCKED`.
- `delivery_state` aligned with the Orchestrator.
- `correction_loop` and regression plan.

## Stop conditions

- Do not approve a publish-ready claim with unresolved blockers or unverified critical checks.
- Do not report visual/audio inspection when only a text description or source code was reviewed.
- Do not use fake numerical scores, probabilities, or measured loudness without evidence.
- If a file cannot be opened or inspected, label relevant checks `NOT_VERIFIED`.
- If rights, consent, or privacy concerns materially affect release, block or require a safe replacement/authorization.

## Shared references

Use `../godex-motion-audio/references/quality-and-risk-gates.md`, `../godex-motion-audio/references/output-contract.md`, and `../godex-motion-audio/references/inter-skill-contracts.md`.
