# Vibe Coding Mentor — Canonical Private Source Pointer

**Plugin key:** vibe-coding-mentor  
**Plugin Creator ID:** `plugins_6b0744bffe9c8191a5eb9c932fcc3f24`  
**Plugin Creator release:** `pluginrel_6b0744c2806481919620bdf8b8719f57`  
**Package version:** `0.1.0` · USER / PRIVATE  
**Canonical repository:** https://github.com/hsaidno-cpu/vibe-coding-mentor  
**Pinned source commit:** `84214752bb298002b96f9ff1c60e16b7a09e99d7`  
**Package parity:** `MATCH — 18/18 files byte-for-byte`  
**Package CI:** [run 45701037593](https://github.com/hsaidno-cpu/vibe-coding-mentor/actions/runs/45701037593) — validator and 4 unit tests passed  
**License status:** `NOT_ASSESSED / UNASSIGNED`  
**Distribution status:** `private_source_restricted`

The canonical private repository is the source authority for this package. The public HSO parent intentionally stores only a metadata pointer and concise skill routing index. The private skill instruction bodies remain in the private repository; they are not mirrored into public HSO.

## Verified source inventory

- 2 manifests
- 6 reference files
- 10 skill instruction files
- 18/18 files compared byte-for-byte against Plugin Creator release `pluginrel_6b0744c2806481919620bdf8b8719f57`
- Pinned repository main commit: `84214752bb298002b96f9ff1c60e16b7a09e99d7`

## HSO runtime boundary

HSO has a declarative route named `plugin.vibe_coding_mentor_prd`, with Vibe Coding Mentor as the primary owner. Its action requires generic capability `plugin.skill.invoke`, which remains `NOT_CONFIGURED`. The route can be selected by HSO and must be blocked before dispatch. No VCM host invocation, Remote MCP endpoint, authentication, authorization or invocation receipt is claimed.

Do not add an enabled runtime capability until a named VCM endpoint is deployed, its identity and TLS/OIDC authorization are verified, the tool allowlist is restricted to the VCM skill, and a real invocation is independently read back.

## Rights and distribution

No public license, redistribution permission or publication approval has been recorded. Keep this source private. Do not publish or install a public package until rights, attribution, source provenance, package artifact and platform adapter gates pass.
