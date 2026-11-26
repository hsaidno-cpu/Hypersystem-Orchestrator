# Canonical Source Identity, Admission and Rights Register
**Snapshot:** 26 November 2026 · **HSO main:** 69479c9fc898d12d6780964fb431fb9a89b1c675

## Executive finding
The earlier phrase “16 plugins have no identified source” was imprecise. All 16 Plugin Creator package identities and package versions are now known. Fourteen have direct current package manifests and file inventories; Ponytail and EWO are private release pointers. None of these 16 has yet been admitted as a canonical child Git repository. A private Plugin Creator inventory is not a Git source and is not permission to publish it.

## 1. Sixteen package identities without canonical child Git sources

| Plugin | Plugin Creator ID | Current package | Release ID | Files | Source disposition |
|---|---|---:|---|---:|---|
| Evaluator Team | Plugin_be5d3d62da24819189f807692271c1a2 | 1.0.0 | pluginrel_6afdee5a10108191a38e1ee7f84f7524 | 13 | Private package verified; Git source not admitted |
| Master Photo Restoration | plugins_6ae29cf104e8819195a90b3c2327d83a | 1.0.0 | pluginrel_6ae29cf38e4881918f892e746050891d | 4 | Private package verified; Git source not admitted |
| GODEX Motion Audio | plugins_6ae564da711c8191a4757bbc4cc20a5b | 2.0.0 | pluginrel_6ae56ef615688191ba0b357fc7b1fd32 | 19 | Private package verified; Git source not admitted |
| AI Prompt Finder & Creator | plugins_6ae57d424a2481918295d281919fbb7d | **1.1.0** | pluginrel_6b074a37ae8c8191bae7723d715ab713 | 26 | Private package verified; HSO catalog stale at 1.0.0 |
| Agent Jailbreak Skill DS | plugins_6ae85f228fbc819185f07fe3f8216ea9 | 0.2.0 | pluginrel_6ae8691261c08191a69065ccbea28965 | 14 | Private package verified; Git source not admitted |
| Motion Graphic by arifanara V.01 | plugins_6ae9780e0f5481919ce74d7db24a6870 | 0.2.0 | pluginrel_6ae97fb29a408191b4ce949723bc460d | 30 | Private package verified; Git source not admitted |
| Plugin Agent Orchestrator | plugins_6afdf05931ec8191ac2379c848d4ca10 | 2.0.0 | pluginrel_6afdff8b11848191be8765373812262f | 86 | Private package verified; Git source not admitted |
| Cortex Workbench | plugins_6aff5719a40081919b30cffcfa7f949e | 1.0.0 | pluginrel_6aff571bb43c819192f2dad006d28d3d | 16 | Private package verified; Git source not admitted |
| CommandCraft 56 | plugins_6aff58549e288191a4564e2940493a3b | 0.1.0 | pluginrel_6aff5856da608191b6451e8d19a7b44a | 17 | Private package verified; Git source not admitted |
| Agent Skills Atlas | plugins_6aff5be096648191b70b95d7494684bd | 0.3.1 | pluginrel_6b000c2b186c819199e6bf1e08d4b646 | 43 | Private package verified; upstream MIT only applies to covered upstream material |
| People & Business Competency Academy | plugins_6b039ef9d14c81918f521f6fe56a8ddc | 0.1.0 | pluginrel_6b039efc6dfc81919fffbe265e8f84c9 | 14 | Private package verified; Git source not admitted |
| AI Workflow Systems Orchestrator | plugins_6b014289e4208191bbaa159e5ecf2a22 | 0.2.0 | pluginrel_6b015fe943608191b46d0a439dd4f55e | 17 | Private package verified; Git source not admitted |
| GrowthForge Business OS | plugins_6b01ce5f6c388191816eaee46f4598a2 | **1.3.0** | pluginrel_6b073d4b53588191a4a8fc858381ae65 | 37 | Private package verified; HSO catalog stale at 1.1.1 |
| Progressive Roadmap Evaluator | plugins_6b038580bc488191ac56d9e586071bfc | 0.1.1 | pluginrel_6b0385d7a4488191a681997c0d9ae531 | 23 | Private package verified; Git source not admitted |
| Ponytail Engineering System | plugins_6b044f34a5a481919ffc95eadee4383b | 0.1.0 | pluginrel_6b044f37640081918df7f449298d72cf | 13 | Private release pointer; HSO parent pointer is not a child source; upstream Ponytail is methodology provenance only |
| Executive Workday Orchestrator | plugins_6b073a60088081918a8958ab761cb505 | 0.1.0 | pluginrel_6b073a6285d481918d11cdbf1bb7643f | 17 | Private release pointer; no canonical child source designated |

Package counts are not unique skill counts. A package can include manifests, examples, scripts, assets and references. Current-version drift is already evidenced for AI Prompt Finder (1.1.0 vs HSO 1.0.0) and GrowthForge (1.3.0 vs HSO 1.1.1); reconcile file contents before catalog edits.

## 2. Two incomplete candidate repositories

### Photo Fixer
- Plugin Creator ID: plugins_6afeb1f444d081918e5e191e062b82ad.
- Package 1.0.0; release pluginrel_6afeb1f735888191b1d25574f336661b; 19 files.
- Candidate GitHub repo hsaidno-cpu/Photo-Fixer at 95339901f84cdae861efcebd9820cb2e1efdc27d has only README/LICENSE.
- Target structure:
  - .codex-plugin/plugin.json, plugin.json, README.md, CHANGELOG.md.
  - LICENSE-DECISION.md and THIRD-PARTY-NOTICES.md.
  - skills/photo-fixer/SKILL.md and references/command-catalog.md, original-100-commands.txt, output-presets.md, quality-checklist.md.
  - Ten photo-fixer-* specialist SKILL.md files.
  - tests/fixtures, manifest, skill-link, prompt-contract, routing and negative-trigger tests.
  - .github/workflows/validate.yml.
- Acceptance: package path/hash inventory; original-image/identity preservation tests; bounded upscaling claims; specialist link integrity; positive and negative routing; license and asset audit.

### PVEE Promkes Super Orchestrator
- Plugin Creator ID plugins_6b029d31109c8191b34f7d50723971cb.
- Package 2.0.2; release pluginrel_6b029dfa21e88191957129cfce63353f; 37 files, 14 skill procedures.
- Candidate CL-VAEPPC at 1ab0c41081ccdbb91cc9dec0a2864acd0de00d54 has README/LICENSE/empty marker and describes a legacy V3.0 shell, not current 2.0.2.
- Target structure:
  - manifests, README/CHANGELOG, license decision, third-party notices.
  - docs/architecture-catalog, forensic-audit, Octa-Prompt gap matrix, progressive roadmap, source design review, acceptance matrix.
  - skills/promkes-orchestrator/SKILL.md, references, scripts and 13 remaining promkes-* skill files.
  - schemas, fixtures, and tests for Fact Lock, claim-evidence links, stage gates, state recovery and manifest validation.
  - .github/workflows/validate.yml.
- Acceptance: 37/37 path/hash mapping; Fact Lock and source claim trace; S01-S14 boundaries; recovery; rendering manifest; independent QA; rights/privacy; human release approval.

## 3. Repository creation boundary
The connected GitHub tool exposes branch/blob/tree/file/commit actions in existing repositories but **does not expose repository creation or visibility controls**. The existing Photo Fixer and PVEE candidates are public; Plugin Creator source packages are USER/PRIVATE. No private package content is copied into public GitHub by this PR. Create both destinations as private repos through GitHub UI/API with repo-create permission, then import the exact package release under owner authority and verify hashes.

## 4. Admission gate
A candidate becomes canonical only after owner/repo/visibility are confirmed; package release ID and full path manifest pinned; file hashes match; third-party notices retained; a rights decision and license scope are recorded; tests pass; immutable commit is pinned into HSO; and a named HSO host invocation receipt exists. A matching README or repo slug is insufficient.
