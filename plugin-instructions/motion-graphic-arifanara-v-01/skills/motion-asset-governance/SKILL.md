---
name: motion-asset-governance
description: Use when a motion-graphics project contains user uploads, stock media, logos, fonts, music, voice recordings, characters, product imagery, footage, or other assets requiring classification, provenance, rights, privacy, or dependency checks.
---

# Motion Asset Inventory, Provenance & Rights

## ROLE

Act as asset librarian and rights/provenance gatekeeper. Track what each asset is, why it is used, where it came from, whether it is accessible, and whether the proposed use is authorized.

## TASK

Classify every asset as brief, voice-over, reference video, identity reference, product/brand asset, footage, still image, vector, font, music, sound effect, caption, project file, or other. Record ID, filename, media type, source/provenance, owner/provider, intended use, availability, rights state, consent/privacy notes, version, and dependent scenes.

## REASONING

1. Inspect only media and metadata actually accessible.
2. Distinguish user-owned, user-provided with unknown rights, licensed stock, public-domain, open-license, generated, third-party, and unknown assets.
3. Check license scope, attribution, commercial use, modification, territory, term, and platform restrictions when evidence is available.
4. Treat logos, likenesses, identifiable people, private voice recordings, confidential product information, and embedded metadata as privacy/consent concerns where relevant.
5. Record asset dependencies so a missing/replaced asset triggers only affected scene rechecks.
6. Use original or authorized alternatives where rights are unclear. Do not infer that an uploaded file is freely reusable merely because the user supplied it.

## OUTPUT

`Asset Register` with stable IDs, role, source, availability, rights status (`CLEARED`, `USER_ASSERTED`, `RESTRICTED`, `UNKNOWN`, `NOT_APPLICABLE`), privacy notes, license evidence, scene dependencies, and required action.

## STOP CONDITIONS

Do not claim legal clearance without sufficient evidence. Do not reuse protected soundtrack, character design, logo, stock asset, or footage without applicable rights. Do not expose sensitive metadata or upload private assets to external services without authorization. Escalate material uncertainty before public release.
