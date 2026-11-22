# Source Repository Classification and Reconciliation

**Inventory date:** 2026-11-22  
**Visible repositories under the connected owner account:** 6  
**Plugin identities in the parent catalog:** 20

## 1. Evidence scope

The connected GitHub account exposes these six repositories under hsaidno-cpu:

1. hsaidno-cpu/Hypersystem-Orchestrator
2. hsaidno-cpu/HSMART
3. hsaidno-cpu/skill-analyzer
4. hsaidno-cpu/A.S.F.R.E.E
5. hsaidno-cpu/Photo-Fixer
6. hsaidno-cpu/anatomi-prompt-strategis (private)

Repository-name searches for the remaining plugin labels did not establish additional official source repositories under this account. Search results from other owners or name-similar repositories are not accepted as canonical source evidence.

This is an inventory of repositories visible through the current connection, not a claim that no other repository exists anywhere.

## 2. Classification rules

| Classification | Meaning | Allowed action |
|---|---|---|
| OFFICIAL_PUBLIC_SOURCE | Correct owner/repository, identity and source content inspected | Pin a specific commit; source remains canonical |
| OFFICIAL_PRIVATE_SOURCE | Correct source but private | Pin only with access and preserve privacy |
| PROTOTYPE | Confirmed prototype with a known owner and explicit relationship to the intended plugin | Register as prototype, not release source |
| MIRROR | Confirmed copy of another canonical source | Record upstream and sync provenance; never designate as canonical |
| CANDIDATE_INCOMPLETE | Repository name suggests a plugin but content is incomplete or unverified | Keep candidate; do not mark source verified |
| LEGACY_REDIRECT | Explicit compatibility redirect to another canonical plugin | Redirect only; never create a second active product |
| NOT_IDENTIFIED | No reliable canonical source located | Retain runtime instruction snapshot and source gap |
| RELATED_PLATFORM | Related system, but not a plugin source | Keep separate; integrate only by an approved contract |

## 3. Current source repository records

| Repository | Class | Evidence | Disposition |
|---|---|---|---|
| skill-analyzer | OFFICIAL_PUBLIC_SOURCE | README and plugin.json agree on package 1.3.0; repository source inspected | Official submodule pinned |
| A.S.F.R.E.E | OFFICIAL_PUBLIC_SOURCE | README and plugin/plugin.json identify A.S.F.R.E.E 0.5.0-rc.1; LICENSE is PolyForm Noncommercial 1.0.0 | Official submodule pinned; release remains candidate |
| anatomi-prompt-strategis | OFFICIAL_PRIVATE_SOURCE | README identifies Anatomi Prompt V3.0/3.0.0; repository is private | Private submodule pinned; no public instruction copy |
| Photo-Fixer | CANDIDATE_INCOMPLETE | Root contains only README.md and LICENSE; Apache-2.0 license observed; full plugin source not present in inspected root | Candidate only, not official source |
| HSMART | RELATED_PLATFORM | Separate repository and existing HSMART project headquarters | Keep outside the 20-plugin registry and do not mix as a plugin submodule |
| Hypersystem-Orchestrator | CENTRAL_ECOSYSTEM | Current parent repository | Owns central catalog, contracts, positioning, governance and roadmap |

Video Explainer is classified OFFICIAL_PUBLIC_SOURCE_LAGGING because the public source remains 4.1.9 and the deployment is 4.1.12. No confirmed mirror or prototype repository was found in the inspected set. Do not invent those classifications for unidentified sources.

## 4. Fourteen plugin sources still not identified

The following fourteen plugin identities remain NOT_IDENTIFIED at repository-source level:

2. Skill Developer Orchestrator
3. Evaluator Team
4. Master Photo Restoration
5. GODEX Motion Audio
6. AI Prompt Finder & Creator
7. Agent Jailbreak Skill DS
8. Motion Graphic by arifanara V.01
9. Plugin Agent Orchestrator
10. Cortex Workbench
11. CommandCraft 56
12. Agent Skills Atlas
13. AI Workflow Systems Orchestrator
14. GrowthForge Business OS
15. PVEE Promkes Super Orchestrator

Video Explainer has a verified public GitHub source pinned at 4.1.9 and a current Plugin Creator deployment verified at 4.1.12. The parent includes 16 current SKILL.md instructions from that release. The fourteen NOT_IDENTIFIED packages plus the Photo Fixer candidate have runtime instruction snapshots; these do not replace canonical source.

## 5. Instruction snapshot inventory

- 16 isolated runtime-snapshot bundles cover the 15 NOT_IDENTIFIED plugins plus Photo Fixer (candidate/incomplete source).
- Four source-backed plugins are represented by their own submodules and per-plugin source-pointer records.
- A.S.F.R.E.E Legacy is captured as one redirect-only snapshot.
- 238 skill records are indexed in catalog/instruction-snapshots.json.
- No snapshot merges two plugin packages or changes their independent identity.

## 6. Required proof before submodule integration

A plugin repository may move from NOT_IDENTIFIED/CANDIDATE to OFFICIAL_SOURCE only after:
- canonical owner and repository identity are confirmed;
- plugin identity is reconciled with its Plugin Creator ID;
- README, manifest, source tree and tests are inspected;
- source version and tag/commit history are confirmed;
- license and required notices are reviewed;
- private/public status and collaborator access are recorded;
- mirror, prototype, legacy and canonical relationships are distinguished;
- a specific immutable commit is pinned;
- source/snapshot drift is reviewed and compatibility checks pass.

Do not make a GitHub URL based on a plugin slug and assume it exists. Do not convert a placeholder or minimal repository into an official source merely because the name matches.
