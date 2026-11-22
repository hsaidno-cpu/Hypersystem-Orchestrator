---
name: godex-render-export
description: Use when a motion-graphic production package needs renderer capability checks, project assembly, video composition, MP4 export, codec and frame-rate configuration, render troubleshooting, or a renderer-ready handoff.
---

# GODEX Render & Export

## Mission and boundary

Turn approved production specifications into an executable project or verified video export using only tools and runtimes actually available. This skill owns renderer capability discovery, adapter selection, assembly instructions, render configuration, export, and file-level verification. It does not invent a renderer, install dependencies without authorization, or equate generated code with a rendered MP4.

## Inputs

- Approved project manifest and scene timeline.
- Design tokens, assets and provenance.
- Motion specifications and renderer fallbacks.
- Audio voice-over, sound cues, captions, export target and constraints.
- Available host tools and execution permissions.

## Procedure

1. **Capability inventory:** verify file access, runtime/code execution, dependencies, font availability, media libraries, codecs, asset-generation route, render command/API, storage/export, and inspection capability independently.
2. **Select route:** native motion/video artifact with proven export; programmatic render with an actually available runtime; or renderer-ready handoff. Do not infer capability from product marketing, model name, or another user's plan.
3. **Dependency and rights check:** confirm referenced assets exist or are explicitly marked placeholder/missing; check licenses; pin available versions and avoid unsupported network/package installation assumptions.
4. **Single source of truth:** read timing and asset IDs from the project manifest. Do not duplicate conflicting hardcoded timestamps across code and subtitles.
5. **Assemble:** compose reusable components, place source voice-over, align visual scene timing, add captions and sound cues, preserve canvas dimensions and safe areas, and use fallback effects if the renderer lacks a requested feature.
6. **Proof render:** render a short or low-resolution section when feasible; inspect before full render.
7. **Full render:** execute only through a real available route. Capture actual result, errors, duration, file path or host attachment ID.
8. **Verify file:** check existence, openability, container, dimensions, frame rate, duration, video/audio streams, and synchronization using available tools. If some checks cannot be performed, mark `NOT_VERIFIED`.
9. **Troubleshoot:** classify errors (dependency, codec, font, missing asset, malformed timeline, resource limit, permission, host restriction). Make one evidence-based correction and retry where safe; do not loop blindly.
10. **Delivery:** package MP4 and source/project files where actually available. Report renderer route, versions, limitations, checks passed and unverified checks.

## Output contract

- `capability_matrix` with verified/unavailable/not-tested status and evidence.
- `renderer_route`: native/programmatic/handoff, tool/runtime and version only if verified.
- `project_artifacts`: path/ID, type, status, dependencies and asset references.
- `render_settings`: dimensions, aspect ratio, frame rate, duration, container, codecs, audio sample rate/channels where supported.
- `render_log` or exact failure class/message.
- `verification_report`.
- `delivery_state`: `RENDERED_VERIFIED`, `RENDERED_PARTIALLY_VERIFIED`, `RENDER_READY`, `BLUEPRINT_ONLY`, or `BLOCKED`.
- `next_action` for any blocker.

## Stop conditions

- Never claim rendering or export until a real operation succeeds and the resulting file is verified to the stated level.
- Do not fabricate file paths, download URLs, tool names, installed packages, supported codecs, or API endpoints.
- If a renderer is absent, create the strongest feasible renderer-ready handoff and state clearly that no MP4 exists.
- Do not export with missing critical assets, broken audio, invalid timeline, or unresolved rights as publish-ready.
- Do not transmit private audio/assets to external services without user authorization.

## Shared references

Use `../godex-motion-audio/references/rendering-and-platform-adapters.md`, `../godex-motion-audio/references/output-contract.md`, and `../godex-motion-audio/references/inter-skill-contracts.md`.
