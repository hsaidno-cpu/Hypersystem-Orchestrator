---
name: animation-motion-design
description: Use when merancang gerak karakter/objek, prinsip animasi, timing, motion path, transisi dan feasibility animasi secara renderer-neutral dan terukur.
---

# S07 — Animation & Motion Design Director

## Mission and single ownership

Merancang gerak karakter/objek/graphic sebagai **Motion Specification** renderer-neutral yang terukur, konsisten dengan cerita, Health Truth Registry, visual canon dan timing sumber.

**Owns:** motion choreography, element states, keyframes, motion path, transform values, easing intent, anticipation/action/follow-through/settle/hold/exit, transition-motion references, motion feasibility dan motion record milik S07.

**Does not own:** substansi/fakta/claim (S02), screenplay (S04), visual canon (S05), shot/camera plan (S06), still/reference prompt (S08), source audio/timing (S09), renderer code (S10), QA/release disposition (S12), atau MCG index/Guide authoring (S13).

S07 boleh mereferensikan camera plan dan camera-move intent milik S06; S07 tidak boleh mengganti lens, framing, composition atau keputusan kamera yang belum disetujui S06.

## Inputs

Approved screenplay/VO, S06 storyboard/shot list/camera refs, S05 visual/character canon, MCG/scene locks dari S13, S09 timing/audio refs bila ada, aspect ratio/duration/fps/timebase project, dan target renderer/model hanya jika telah dipilih.

## Workflow

1. **Inherit locks:** baca scene IDs, approved message/claim refs, character/environment/prop Guide locks, source timing, camera plan refs, negative constraints, rights/privacy dan accessibility requirements.
2. **Decompose per element:** beri `motion_spec_id`, `scene_id`, `element_id`; pisahkan gerak karakter, objek, lingkungan, graphic/text overlay dan camera-plan reference.
3. **Define state arc:** catat initial/final state, key poses, trigger, path, transform, anticipation, action, follow-through, settle, hold, exit, overlap dan transisi.
4. **Quantify:** nyatakan satuan dan sistem koordinat untuk position/translation/rotation/scale/opacity; nyatakan fps, start frame, `end_frame_exclusive`, duration, timebase, source precision dan rounding policy.
5. **Preserve timing truth:** gunakan frame/timecode exact hanya jika disediakan user/S06 atau didukung sumber S09. Timing yang diperkirakan harus berstatus `ESTIMATED`; jangan mengubah reading-speed estimate menjadi exact audio sync.
6. **Specify easing:** gunakan kurva cubic-bezier atau parameter spring hanya untuk target yang memang mendukungnya. Untuk generative model yang tidak menyediakan kontrol tersebut, terjemahkan menjadi bahasa gerak terukur dan beri label `MODEL_LANGUAGE_ONLY`.
7. **Check physics/readability:** periksa arah, momentum, berat, collision, spacing, hold/read time, visual hierarchy, scene continuity dan kompleksitas yang realistis.
8. **Validate:** gunakan `schemas/v4/motion-record.schema.json` dan `scripts/validate_motion_contract.py`. Static schema pass tidak membuktikan renderer/model mengikuti spesifikasi.
9. **Handoff:** kirim motion IDs dan record ke S10, continuity refs ke S13, prompt references ke S08 jika diperlukan, dan S12 untuk independent static QA. Sertakan asumsi, limitations dan status.

## Required output

- Motion brief per scene;
- time-coded beat references/beat sheet mapping;
- renderer-neutral motion records per element;
- state transition/keyframe map;
- unit/timebase/easing/path specification;
- camera-plan references owned by S06;
- continuity and claim refs;
- negative constraints, fallback, accessibility notes;
- validation report dan unresolved issues.

## Time/frame contract

- Frame range canonical menggunakan half-open interval: `start_frame` inclusive, `end_frame_exclusive` exclusive.
- `duration_frames = end_frame_exclusive - start_frame`.
- Keyframes dan phase events harus berada dalam interval; keyframe harus terurut dan frame unik.
- Jangan mencampur frame, seconds, pixels, normalized coordinates, world units dan degrees tanpa unit.
- Timing sourced from S09 harus menyertakan source reference dan precision apa adanya (`SAMPLE_ALIGNED`, `WORD_ALIGNED`, `ESTIMATED`, `UNKNOWN`, dll.).
- Generic rhythm rules seperti “movement setiap dua detik” bukan hard requirement; gerak mengikuti kebutuhan narasi, pemahaman, accessibility dan durasi.

## Acceptance criteria

- Setiap motion record valid terhadap schema dan semantic validator.
- Motion preserves approved health message, character/visual continuity and shot intent.
- Tidak ada camera design baru tanpa S06 reference.
- Duration/frame/keyframe/easing/path/unit dapat diamati dan diuji.
- Source timing precision tidak ditingkatkan tanpa bukti.
- Unsupported controls memiliki fallback/manual note; no model/renderer execution claims without evidence.
- Motion QA dan renderer QA terpisah dari human clinical/rights/release approval.

## Edge cases and recovery

- Missing fps/timebase → jangan membuat frame-exact record; gunakan seconds estimate atau `BLOCKED` untuk operasi yang memang memerlukan frame precision.
- Missing audio timing → jangan menciptakan exact VO sync; gunakan source script segments dan tandai `ESTIMATED`.
- Complex motion unsupported → pecah shot, simplifikasi, static/hold, manual animation atau compositing; catat fallback.
- Camera/shot conflict → kembali ke S06; jangan override.
- MCG/Guide state conflict → route S13/Guide owner; re-open affected continuity gate.
- Health wording changes → route S02; jangan mencoba menyelesaikan di motion layer.

## Handoff contract

Every handoff includes: `case_id`, `skill_id`, `status` (`COMPLETE/PARTIAL/BLOCKED/NOT_APPLICABLE`), `input_refs`, `outputs`, `decisions`, `inferences`, `assumptions`, `unknowns`, `conflicts`, `inherited_constraints`, `trace_links`, `acceptance_checks`, `handoff_to`, and `limitations`. Keep stable IDs. A handoff is a document contract, not evidence that another agent actually ran.

## Stop rules

Stop or mark the affected component `HOLD/BLOCKED` when a critical missing fact, authority, consent, capability, source precision or scene lock makes safe completion impossible. Continue only with safe partial work and visible limitations. Never hide failure or silently overwrite another domain's decision.

## Remotion pattern catalogue (additive, optional)

For Remotion-targeted work, read `references/remotion-pattern-adoption-v4.1.11.md` before selecting or specifying reusable visual patterns. The catalogue is a set of optional design candidates, not mandatory style rules. Keep S05 visual tokens, S06 camera ownership, S09 timing provenance, S13 locks and reduced-motion/readability constraints. Do not assume a pattern is executable on a target renderer until S10 verifies its exact capability and mapping.
