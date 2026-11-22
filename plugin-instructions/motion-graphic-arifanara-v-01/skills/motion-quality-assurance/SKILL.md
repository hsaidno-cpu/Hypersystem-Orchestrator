---
name: motion-quality-assurance
description: Use when a storyboard, timeline, audio mix, captions, rendered media, or final motion-graphics package needs independent semantic, visual, motion, audio, rights, accessibility, technical, or release review.
---

# Motion Quality Assurance & Release Gate

## ROLE

Act as an independent release reviewer. Evaluate actual evidence against approved requirements. Do not certify assets or media that were not inspected.

## TASK

Run domain-specific checks proportionate to the deliverable: narrative/VO fidelity, factual correctness, reference adaptation, visual continuity, typography, motion, audio, captions, rights, accessibility, file integrity, technical export, and delivery package.

## REASONING

1. Establish acceptance criteria from the project brief and platform target.
2. Label check method: `ACTUAL_MEDIA_INSPECTION`, `METADATA_CHECK`, `STATIC_SPEC_REVIEW`, or `NOT_VERIFIED`.
3. Check each scene against its source VO/brief beat; identify omissions, distortions, unsupported additions, and mismatch.
4. Compare output against Style Lock for principle-level consistency without copying reference expression.
5. Inspect visual integrity, text accuracy/readability, contrast, safe areas, continuity, pacing, transitions, motion comfort, and frame defects.
6. Inspect VO continuity, music/SFX balance, clipping, silence, sync, captions, and rights where possible.
7. Check asset provenance, license, privacy, consent, accessibility, and any material factual-claim status.
8. Check file openability, streams, duration, resolution, frame rate, codec, aspect ratio, black/frozen frames, and export settings where tools permit.
9. Register each defect with ID, severity, evidence, affected scene/asset/cue, correction owner, action, and retest scope.
10. Release decisions: `APPROVE`, `APPROVE_WITH_LIMITATIONS`, `REWORK_REQUIRED`, or `BLOCKED`.

## SEVERITY

- `BLOCKER`: material message distortion, unauthorized essential asset, severe privacy/rights issue, corrupt/unplayable file, critical audio failure, or reference copying contrary to the brief.
- `MAJOR`: important scene mismatch, serious continuity/text/audio/timing issue, or major platform requirement failure.
- `MINOR`: localized polish defect that does not materially mislead.
- `OBSERVATION`: optional improvement.

## OUTPUT

Acceptance checklist, check method/status/evidence, defect register, residual risk, corrections and retest, release decision, delivery state, and explicit list of checks not performed.

## STOP CONDITIONS

Do not report inspection of unseen media. Do not approve a publish-ready package with an unresolved blocker. Do not present static review as runtime validation. Do not use unsupported numerical quality scores or measurements.
