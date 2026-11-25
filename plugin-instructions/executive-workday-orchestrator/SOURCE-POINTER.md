# Executive Workday Orchestrator — private canonical source pointer

**Catalog key:** `executive-workday-orchestrator`  
**Plugin Creator package:** `plugins_6b073a60088081918a8958ab761cb505`  
**Current release:** `pluginrel_6b073a6285d481918d11cdbf1bb7643f`  
**Package version:** `0.1.0`  
**Scope / discoverability:** `USER / PRIVATE`  
**Capture date:** `2026-11-26`  
**Package entry:** [Open the private plugin](https://chatgpt.com/plugins/plugins_6b073a60088081918a8958ab761cb505)

## Canonical source authority

- **Canonical private Git source:** [executive-workday-orchestrator](https://github.com/hsaidno-cpu/executive-workday-orchestrator)
- **Pinned source commit:** `69166133cdc65d1f4f358daec005677db5cd0`
- **Source version:** `0.1.0`
- **Private Plugin Creator artifact:** `USER / PRIVATE`, package version `0.1.0`, release `pluginrel_6b073a6285d481918d11cdbf1bb7643f`

The canonical Git repository contains the 17-file source snapshot under `plugin-source/`: 14 `SKILL.md` files, two manifests, and the package README. The private Plugin Creator release was read back and compared file-by-file. At the pinned source commit, GitHub reports **17/17 exact Git blob SHA matches** against the blobs created from the exact Plugin Creator source contents.

The 17-file match establishes source/package snapshot parity only. It does not establish rights to the third-party source work, grant an open-source license, or authorize public redistribution.

This public HSO repository stores identity, bounded skill descriptions, version/provenance metadata, and this pointer only. It does **not** mirror the private 14 skill instruction bodies. The source repository is not a Git submodule because it is private and must not be treated as a public source artifact.

## Modular skill index

- **`approval-risk-gate`** — Use before an external or consequential action, including sending messages, changing calendar events, publishing, deleting, purchasing, or making commitments on the user's behalf.
- **`automation-integration-architect`** — Use when designing recurring workday automation, connecting task/calendar/email/knowledge systems, or assessing whether a manual process is ready for automation.
- **`calendar-meeting-operations`** — Use when preparing meetings, evaluating calendar conflicts, organizing appointments, extracting decisions, or turning meeting notes into accountable follow-up actions.
- **`daily-planning`** — Use when the user wants to plan a workday, allocate tasks to time blocks, balance capacity, or prepare a realistic daily schedule.
- **`email-communication-operations`** — Use when triaging email or messages, identifying requests and deadlines, drafting replies, or tracking follow-up obligations.
- **`focus-adaptive-scheduling`** — Use when interruptions, unexpected work, overruns, energy changes, or new deadlines require a safe and realistic replan of the remaining workday.
- **`notes-knowledge-management`** — Use when converting unstructured notes, ideas, decisions, or meeting summaries into structured, retrievable knowledge with provenance and action extraction.
- **`performance-review-learning`** — Use at the end of a workday or week to review accomplishments, delays, bottlenecks, outcomes, and improve future planning.
- **`priority-decision-engine`** — Use when the user needs to decide what to do first, compare competing tasks, expose trade-offs, or organize work with the Eisenhower Matrix and additional decision criteria.
- **`project-portfolio-management`** — Use when organizing projects, milestones, workstreams, dependencies, owners, delivery risk, portfolio capacity, or cross-project commitments.
- **`prompt-generator`** — Use when the user asks to create, refine, audit, compare, or explain an AI prompt, especially for workday, task, project, meeting, email, note, or automation workflows.
- **`task-intake-triage`** — Use when the user supplies scattered requests, messages, notes, ideas, or task lists that need to be captured, normalized, classified, deduplicated, or routed.
- **`workday-data-governance`** — Use when the workday assistant depends on durable task state, project memory, shared knowledge, data synchronization, privacy, data retention, or source-of-truth decisions.
- **`workday-orchestrator`** — Use as the master controller when the user wants an AI system to organize daily work, tasks, projects, meetings, communications, notes, focus, reviews, or related automation.

## Runtime and integration boundary

The package provides instruction-level planning, triage, prioritization, project control, meeting and communication preparation, note organization, adaptive replanning, reviews, prompt generation and automation design. It does not provision an external task database, persistent memory, mailbox/calendar connector, event listener or background worker. Live external actions require configured integrations, least-privilege access, specific human authorization, and read-back verification.

## Provenance and distribution gate

- Plugin Creator release and 14-skill inventory observed on 2026-11-26.
- Canonical Git source is pinned at `69166133cdc65d1f4f358daec005677db5cd0`.
- Source-to-package parity: `MATCH`, 17/17 exact blob SHA matches.
- Source rights: `NOT_CLEARED`; supplied source URL, rightsholder identity, and written permission or applicable license have not been established.
- Private repository license notice: interim `NO LICENSE GRANTED / ALL RIGHTS RESERVED`; this is not an open-source license.
- HSO distribution status: `snapshot_only`; package artifact absent; target host adapter not host-tested.
- Public HSO mirror status: `POINTER_AND_METADATA_ONLY`.

Do not publish the private instruction bodies into this public repository until third-party rights clearance and an explicit publication license decision are recorded.
