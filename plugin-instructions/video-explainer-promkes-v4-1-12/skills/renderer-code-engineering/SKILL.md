---
name: renderer-code-engineering
description: Use when approved Promkes storyboard, assets, motion, audio and subtitles need renderer mapping, project assembly, rendering, export or renderer-ready handoff.
---

# S10 — Editing, Post-Production, Renderer & Code Engineering

## Mission and ownership

Own the path from approved renderer-neutral scene/asset/audio/overlay/motion specifications to a validated renderer adapter, assembled project and actual export only when the exact host/runtime supports it. Preserve S02 health locks, S05/S13 visual canon, S06 shot/camera decisions, S07 motion values, S08 reference records and S09 audio/timing evidence. Do not claim renderer availability/export from a manifest alone.

## Inputs and ownership lanes

S10 receives the production manifest, S06 scene/shot/camera plan, S07 motion records, S08 reference asset manifest, S09 source audio/transcript/subtitle/sound cues, S11 accessibility/overlay requirements and explicit render target/permissions.

S10 combines two complementary lanes under one owner:
1. Editing/post-production: sequencing, pacing, transitions, overlays, captions, subtitles, audio mix, synchronization, finishing and export preparation.
2. Renderer/code engineering: canonical-to-target mapping, adapter code, typed props, project assembly, runtime checks, render/export orchestration and file verification.

S09 retains audio source intelligence and timing provenance. S11 retains accessibility/distribution requirements. S12 independently verifies results.

## Capability readiness

Check file access, code execution, renderer/runtime and exact version, dependencies, fonts, image/video/audio decoders, codecs, memory/runtime, export destination and media inspection. Status `VERIFIED`, `UNAVAILABLE`, `NOT_TESTED` or `NOT_APPLICABLE` with evidence and limits.

## Canonical motion-to-renderer mapping

- Treat `schemas/v4/motion-record.schema.json` as the renderer-neutral motion source contract.
- Convert canonical fields to target-specific properties only through an explicit mapping record for the selected renderer/version.
- Remotion, GSAP, Lottie and HyperFrames are not interchangeable schemas. Document unsupported curves, path semantics, timebase conversion, track ordering and fallbacks.
- Frame conversion uses declared fps and rounding policy. Respect the half-open range: `duration_frames = end_frame_exclusive - start_frame`.
- Keep camera/shot intent from S06; do not add camera design while mapping S07 motion.
- Emit a mapping loss report for any omitted, approximated, quantized or manually implemented property.
- Validate schema, element IDs, scene boundaries, keyframes, track collisions, asset paths, rights, overlays, subtitles, audio cues and renderer capabilities before execution.

## Route selection

- `NATIVE`: an accessible native motion/video workflow can produce the requested composition/export.
- `PROGRAMMATIC`: an authorized, accessible renderer/runtime (e.g. Remotion or FFmpeg) can assemble the manifest and media.
- `HANDOFF`: no usable renderer is available; produce a renderer-neutral handoff and explicitly state no MP4 was created.
- `NONE`: rendering is outside user scope.

Do not assume a model-generated short clip is a deterministic multi-scene renderer or that canonical JSON is automatically valid props/TSX.

## Render workflow

1. Validate manifest and all motion records.
2. Confirm critical assets and rights status.
3. Validate fonts, safe areas, alpha, overlays, subtitle/audio cues and exact renderer support.
4. Assemble using selected route; preserve source assets and IDs.
5. Create proof render when feasible.
6. Inspect crop, legibility, continuity, keyframe timing, sync and missing assets.
7. Correct observed defects with CHG-ID and rerun affected regression; bound retries.
8. Execute full export only after required proof gates pass.
9. Verify actual file existence, openability, dimensions, fps, duration, streams and sync as tools permit.
10. Capture exact route, tool/runtime versions, settings, output artifact, logs and unverified checks.

## Output and stop rules

Output `capability_matrix`, `renderer_route`, exact renderer/version, adapter status, mapping loss report, composition/motion manifest refs, project artifacts, render settings, proof status, render log, actual output only if it exists, per-check verification report and delivery state.

Never invent commands, dependencies, APIs, codecs or paths. Do not install dependencies or transmit private media without authorization. If renderer unavailable, stop at handoff. A project file is not an MP4; an MP4 is not verified until inspected. Missing critical assets, invalid timing, rights issue or failed proof check blocks publish-ready export.

## Remotion motion-pattern adoption (S10 integration)

For Remotion-targeted projects, read `skills/animation-motion-design/references/remotion-pattern-adoption-v4.1.11.md`. Verify exact installed package/runtime versions and supported features before mapping S07 patterns. The current Promkes adapter profile is deliberately limited; unsupported audio, subtitles, crossfades, arbitrary paths and multiple composited references must remain fail-closed or use a separately tested adapter. Report mapping loss and distinguish composition-frame inspection from encoded-MP4 inspection.
