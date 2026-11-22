# Responsibility & Routing Matrix

## Primary orchestrator selection

Select exactly one primary orchestrator for a case. Supporting systems are selected only when they have a distinct required output or control.

| User's dominant intent | Primary plugin | Supporting plugin(s) when useful | Do not route to |
|---|---|---|---|
| Analyze a complex non-technical or cross-domain issue | SKILL ANALYZER | Evaluator Team, GrowthForge, Atlas | A.S.F.R.E.E unless technical-system forensics is required |
| Forensic audit or supervised engineering of software/AI system | A.S.F.R.E.E Canonical | SKILL ANALYZER, Agent Jailbreak DS, SDO | A.S.F.R.E.E Legacy |
| Create or improve a skill/plugin repository | Skill Developer Orchestrator | SKILL ANALYZER, Anatomi Prompt, Evaluator Team | Multiple simultaneous write owners |
| Independently score/evaluate a skill or redesign instructions | Evaluator Team | SKILL ANALYZER, Anatomi Prompt | SDO as independent judge of its own changes |
| Build/refine/audit a master prompt | Anatomi Prompt V3 — Octa-Prompt | Prompt Finder for reference reconstruction | Downstream executor when task is prompt-design only |
| Reconstruct prompt from image/video reference | AI Prompt Finder & Creator | Anatomi Prompt for structural hardening | Claiming hidden original prompt recovered |
| Design/build/run/manage AI agents | Plugin Agent Orchestrator | Agent Jailbreak DS, Workflow Systems | Generic SDO unless the object is a skill/plugin package |
| Threat-model an agent or audit injection/tool abuse | Agent Jailbreak Skill DS | A.S.F.R.E.E, Plugin Agent Orchestrator | Offensive/live unauthorized target testing |
| Design a reusable AI workflow or modular project system | AI Workflow Systems Orchestrator | Cortex, Plugin Agent Orchestrator | All plugins by default |
| Learning, research, writing, thinking or coding command workflow | Cortex Workbench | SKILL ANALYZER, CommandCraft | GrowthForge except business-domain intent |
| Use a specific text command profile | CommandCraft 56 | Cortex or GrowthForge where domain warrants | Assuming a native slash-command interface exists |
| Inventory, map or stage adoption of skill capabilities | Agent Skills Atlas | SKILL ANALYZER, Workflow Systems | Calling mapped assets executable without testing |
| Business model, brand, product, marketing, sales or finance | GrowthForge Business OS | CommandCraft, Cortex | General workflow route when business domain is dominant |
| Edit/retouch/composite general photo | Photo Fixer | Master Photo Restoration for damaged portraits | Rendering claims without image tool evidence |
| Conservatively restore a portrait/photo | Master Photo Restoration | Photo Fixer | Creative changes that alter identity without request |
| Create a voice-over-led motion-graphics production | GODEX Motion Audio | Motion Graphic | Promkes unless health communication is the target |
| Create a general motion-graphics/explainer project | Motion Graphic by arifanara | GODEX, Prompt Finder | Promkes unless health evidence is in scope |
| Produce a health-promotion explainer | PVEE or Video Explainer Promkes selected by source/version mandate | GODEX, Motion Graphic, Prompt Finder | General creative pipeline bypassing health fact checks |
| Access old A.S.F.R.E.E identifier | A.S.F.R.E.E Canonical | None | Legacy execution |

## Routing rules

1. Dominant intent determines one primary orchestrator.
2. A second plugin is added only for a separate specialist deliverable, hard control or required adapter.
3. Supporting plugin output must be handed back to the primary orchestrator with source and version.
4. If two plugins claim the same final decision, use the ownership matrix in architecture/ECOSYSTEM-ARCHITECTURE.md.
5. If the intended plugin source or version is unknown, mark it unresolved; do not choose by name similarity.
6. Do not assume tool invocation or persistent context from skill documentation alone.
7. A plugin's presence in the registry is not a permission to access its external source or execute its tools.

## Decision ownership

| Decision | Owner |
|---|---|
| Ecosystem identity/catalog schema | Hypersystem Orchestrator repository maintainer |
| Plugin implementation and release | Each plugin's own source repository maintainer |
| Cross-plugin interface contract | Ecosystem architecture owner, with affected plugin owners |
| Plugin internal method/workflow | Plugin's primary orchestrator |
| Independent evaluation disposition | Evaluator Team / designated independent evaluator |
| Technical change authorization | Target repository owner/authorized human |
| Security and privacy acceptance | Named accountable human; security plugins advise |
| Production/publication approval | Authorized human and relevant domain authority |

## Unresolved routing cases

- Whether Video Explainer Promkes V4.1.12 and PVEE represent separate products, release branches or overlapping plugin generations requires source and manifest reconciliation.
- Photo Fixer and Master Photo Restoration share a domain; source and artifact boundaries remain to be inspected.
- Evaluator Team and SDO both expose controlled implementation capabilities; task-level single-writer policy is mandatory.
