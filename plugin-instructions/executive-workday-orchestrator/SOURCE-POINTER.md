# Executive Workday Orchestrator — private package pointer

**Catalog key:** `executive-workday-orchestrator`  
**Plugin Creator package:** `plugins_6b073a60088081918a8958ab761cb505`  
**Current release:** `pluginrel_6b073a6285d481918d11cdbf1bb7643f`  
**Package version:** `0.1.0`  
**Scope / discoverability:** `USER / PRIVATE`  
**Capture date:** `2026-11-26`  
**Package entry:** [Open the private plugin](https://chatgpt.com/plugins/plugins_6b073a60088081918a8958ab761cb505)

## Source authority

The current USER/PRIVATE Plugin Creator release is the package authority. Its file inventory was read back and contains 14 skill instruction files. The full instruction bodies, manifests and supporting package files remain in the private package and are **not mirrored in this public HSO repository**.

No canonical child Git repository has been designated. The HSO parent catalog is updated with plugin identity, responsibility boundaries, release metadata and this pointer only. Do not treat this pointer as source parity, a Git submodule, or proof of ChatGPT host activation.

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

## Provenance and next source gate

- Current release metadata and the 14-file inventory were observed on 2026-11-26.
- Canonical Git source: `NOT_IDENTIFIED`.
- Source-to-package parity: `NOT_APPLICABLE` until a canonical source repository is designated.
- Public mirror status: `POINTER_AND_METADATA_ONLY`.
- Do not copy private instruction bodies into this public repository without an explicit publication and rights decision.
