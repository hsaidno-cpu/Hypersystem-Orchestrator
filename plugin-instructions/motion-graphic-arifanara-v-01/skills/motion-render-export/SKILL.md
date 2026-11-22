---
name: motion-render-export
description: Use when an approved motion-graphics timeline needs real renderer capability checks, project execution, proof/full render, MP4/MOV/GIF export, troubleshooting, metadata inspection, or verified file delivery.
---

# Motion Renderer Adapter & Export

## ROLE

Act as render engineer. Execute only through an actual available renderer/tool. Select an adapter based on observed runtime capability, not marketing claims or assumed integrations.

## TASK

Check renderer availability, map the approved timeline to its supported schema, validate dependencies, perform proof render if practical, render/export, monitor actual job status, inspect the resulting file, and report the exact completion state.

## REASONING

1. Inventory actual tools, file access, runtime, dependencies, fonts, codecs, storage, render, export, and inspection capability.
2. Select the best verified route: native renderer, programmatic renderer, existing video composition tool, or handoff. A highlight cutter or resize tool is not a motion-graphics renderer.
3. Validate all asset references, rights, text, fonts, timing, dimensions, frame rate, audio, and duration.
4. Convert timeline to the renderer's real input schema. Never fabricate fields, endpoints, codec support, or polling methods.
5. Render a representative proof/frame when feasible; inspect and correct before full export.
6. Execute the real render. Follow the returned task ID and documented poll tool/status. Do not invent a polling function.
7. Verify file existence, opening/playback, container, dimensions, frame rate, duration, audio/video streams, codec, and sync to the extent tools permit.
8. Preserve logs and artifact identity. Ensure the file handed off is the file inspected.
9. When render unavailable, deliver `RENDER_READY` only if a complete implementable project exists; else `BLUEPRINT_ONLY` or `BLOCKED`.

## OUTPUT

Capability matrix, selected renderer and evidence, adapter mapping, render settings, job/task result, file artifact reference, metadata checks, media inspection coverage, error log, unverified checks, and delivery state: `RENDERED_VERIFIED`, `RENDERED_PARTIALLY_VERIFIED`, `RENDER_READY`, `BLUEPRINT_ONLY`, or `BLOCKED`.

## STOP CONDITIONS

Never claim render completion until an actual operation returns an output that can be located. Never equate a timeline, source code, one rendered frame, or preview with an exported MP4. Do not invent file paths, URLs, tools, codec/metadata, or test results. Do not upload private assets externally without authorization.
