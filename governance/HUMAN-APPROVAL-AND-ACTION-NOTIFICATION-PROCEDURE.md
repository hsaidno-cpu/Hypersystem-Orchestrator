# Human Approval, Manual Action & Notification Procedure (HAP-01)

**Document ID:** HSO-GOV-HAP-01  
**Version:** 1.0.0-draft  
**Date:** 2026-11-25  
**Canonical owner:** HSO Governance / UEDE Governance Guard  
**Human decision authority:** GOV-01 (the project owner only)  
**Applies to:** HSMART, HSO, UEDE, PRE, their GitHub repositories, Notion project records, integrations and future execution runtimes.

> **Status and activation boundary:** This procedure is being introduced through the open HSO UEDE architecture PR and its HSMART integration counterpart. It is immediately used as the response/interaction contract in this project conversation. Repository-wide enforcement, event-driven delivery and automated notification are not claimed active until the relevant PRs are accepted, the implementation is deployed, and live acceptance tests pass.

## 1. Purpose

Prevent AI workflows from silently stopping at a human-only gate, and prevent the owner from having to guess which GitHub or Notion button to press.

Whenever human approval or a manual action is necessary, the system must produce a traceable action notice that tells the owner:

1. exactly **what** decision or action is required;
2. **why** it is required and what risk it controls;
3. the exact project, repository, PR/issue, branch and commit SHA involved;
4. a direct URL to the exact page or location;
5. the exact UI position and button/menu to use;
6. numbered instructions and the expected result;
7. what must not be clicked or changed;
8. how to report completion and what evidence closes the request.

No workflow may depend on the owner guessing, searching across tabs, or interpreting an unexplained notification.

## 2. Authority and terminology

### 2.1 One human decision authority

- **GOV-01 is the sole human approval authority** for HSMART–HSO–UEDE ecosystem decisions that require owner approval.
- No second human engineering reviewer, security approver or proxy approver is introduced by this procedure.
- AI review, tests, CI, security analysis, static analysis and evidence checks are technical evidence. They are not human approval and must never be represented as a GitHub-native human APPROVED review.
- The owner may delegate bounded execution to AI, but that does not delegate the owner's decision authority.
- Silence, elapsed time, a green check, a draft PR, a comment reaction, or an AI statement is never approval.

### 2.2 Approval versus manual action

**Human approval** is a decision: approve, reject, or request changes to a defined action/scope.

**Manual human action** is an operation the connected AI/tooling cannot safely or technically complete, such as enabling a GitHub setting, configuring OIDC, supplying a credential, completing an external login, or pressing a GitHub UI control when the integration cannot do it.

One request may require both: first owner approval, then a manual UI action. They must be listed as separate steps.

### 2.3 Action classes

| Class | Examples | Default handling |
|---|---|---|
| Routine automation | Read status, create isolated branch, commit scoped documentation, draft PR, run tests, retry a failed CI job | AI/tooling may execute within granted scope and policy |
| Bounded manual operation | Set a documented low-risk project preference or complete a non-sensitive UI step | AI prepares exact instructions; owner performs it if connector permissions are absent |
| Owner approval | Merge when owner approval is required, change protected branch rules, accept architecture/gates, change PRE baseline or acceptance criteria, enable higher autonomy | Pause and request GOV-01 decision |
| Critical/destructive action | Delete a branch with dependents, delete data, rotate/revoke credentials, change identity/access/security/audit, production migration/deployment, disable recovery controls | Fail closed; explicit GOV-01 approval and verified rollback/evidence required |

The action class must be determined from impact and reversibility, not from the name of a GitHub button.

## 3. Mandatory approval gates

Request GOV-01 approval before executing any of the following unless a specific, recorded policy already authorizes that exact low-risk action:

- merging a change into a protected or canonical branch where owner disposition is required;
- changing branch protection, repository rulesets, permissions, GitHub App access, OIDC trust, secrets or credential scope;
- enabling production access, production deployment or a new autonomy tier;
- destructive migrations, data deletion, irreversible changes, or deleting a branch that may be a dependency;
- changing identity, authorization, policy, audit, recovery or security controls;
- changing PRE roadmap baseline, approved objective, priority authority, acceptance criteria, milestone acceptance or closure;
- changing plugin source ownership, license/usage rights, publication or distribution policy;
- accepting a new cross-repository architecture or modifying canonical ownership;
- changing the approval mechanism, GOV-01 identity or the rights of the owner.

A manual login, secret entry or account-level configuration step must be requested as a separate manual action. The AI must never ask the owner to paste secrets, recovery codes, private keys, passwords or tokens into a chat or Notion record.

## 4. Actions AI may ordinarily perform

Within the configured tool permissions, approved scope and autonomy tier, AI may:

- inspect repositories, PRs, checks, commits, review threads and dependencies;
- create isolated feature branches and scoped commits;
- open or update draft PRs;
- run tests and exact-head CI, analyze failures and prepare fixes;
- update project documentation and create/update action records;
- rerun eligible failed CI jobs;
- resolve a review thread only after the issue has been materially fixed and verified;
- delete a merged branch only when repository policy permits, the branch is confirmed unused, no open PR depends on it, and cleanup is explicitly within the authorized automation policy.

AI must not merge, approve its own work, dismiss a blocking review, bypass a failed check, alter acceptance criteria to make a test pass, or delete a branch merely to clear a notification.

## 5. Human Action Inbox and durable record

The canonical owner-action register is the Notion database:

**UEDE Human Action & Approval Inbox**  
https://app.notion.com/p/42399868397f8152b2b7d1bf8cc15712

Every actionable request must have one record, not multiple duplicate tickets. Use the database fields as follows:

- **Action / Action ID:** short verb-led title and generated unique ID.
- **Status:** Needs owner action, Awaiting evidence, In progress, Completed, Cancelled, Stale, or Blocked.
- **Action Type / Priority / Project:** classification and urgency.
- **Repository / PR or Issue / Exact Head SHA:** immutable target context.
- **Action URL:** direct page or UI entry point.
- **UI Location:** exact tab, panel, section, menu and button name.
- **Instructions:** numbered, executable steps and expected result.
- **Reason and Risk:** why the gate exists and consequence of action/inaction.
- **Required Decision:** precise choice or approval scope.
- **Decision Receipt:** owner's explicit disposition or evidence URL.
- **Notified At / Completed At:** notification and closure timestamps.
- **Stale Condition:** events that invalidate this request.

Create/update one record idempotently. A retry must update the existing action rather than create a duplicate. Keep one record open until every linked step is complete.

### 5.1 Status meanings

| Status | Meaning |
|---|---|
| Needs owner action | Instructions and evidence are complete; owner decision/action is now required |
| Awaiting evidence | A gate exists, but CI, review, security or other prerequisite evidence is not ready; do not ask owner to approve yet |
| In progress | Owner has started the requested manual task |
| Blocked | A prerequisite, permission, integration or policy conflict prevents progress |
| Stale | Target SHA, base branch, dependency, policy or UI state changed; prior instructions/approval must not be reused |
| Completed | Required action and its evidence are verified and recorded |
| Cancelled | Request was explicitly withdrawn or rejected |

A request must not be marked Completed solely because the owner says "done"; verify the repository or system state where possible, then record the evidence.

## 6. Notification contract

### 6.1 Immediate interaction channel

At the end of every project/ecosystem response, the assistant must state one of:

- **HUMAN ACTION REQUIRED** — at least one approval or manual action is pending; include the complete action notice and Notion Inbox record.
- **AWAITING EVIDENCE** — a human gate is foreseeable, but the system must first finish technical checks; do not ask the owner to approve prematurely.
- **NO HUMAN ACTION REQUIRED** — the workflow can continue within authorized scope; say this explicitly.

If more than one action is needed, order them by dependency and mark which must happen first.

### 6.2 Durable notification channels

- **Now:** the current assistant response plus the Notion Human Action & Approval Inbox.
- **GitHub:** once event-driven integration is deployed, create/update a single linked issue or PR comment and notify/assign the owner where the authenticated GitHub identity and notification behavior have been verified.
- **Notion push/other channels:** only after an authorized integration and delivery test exist.

Do not claim that a push notification, webhook, GitHub mention, email or background alert is live unless a real event has been received and delivery has been verified. Creating the Notion database does not by itself create push notifications.

### 6.3 Required message format

Every notification must use this structure:

**[HUMAN ACTION REQUIRED | Action ID | Priority]**

- **Project / repository:** ...
- **Action type:** Approval decision or Manual action
- **Why now:** ...
- **Target:** PR/issue, branch, base, exact head SHA, and relevant CI/review state
- **Direct link:** ...
- **Exact UI position:** e.g. PR page → Conversation tab → Merge box at the bottom; or Settings → Branches → Branch protection rules
- **Action to perform:** ...
- **Steps:** numbered and specific to the current UI
- **Expected result:** ...
- **Do not:** forbidden or premature actions
- **Stale when:** exact conditions that invalidate the request
- **Record:** link to the Notion Inbox row
- **Owner response:** exact response syntax/evidence needed

Never give a bare link without describing where to click and what the button does. If the UI cannot be confirmed, say so and provide the nearest verified page plus navigation path; do not invent button positions.

## 7. Owner response and approval protocol

Supported owner responses:

- `APPROVE <Action ID> <Exact Head SHA>` — approve only the action and scope described in that record.
- `REJECT <Action ID> — <reason>` — reject that request; downstream work remains stopped.
- `CHANGE <Action ID> — <requested change>` — return it for replanning; previous approval is not implied.
- `DONE <Action ID> <evidence URL or verified result>` — report a manual action completed.

Approval is valid only for the recorded repository, PR/operation, exact SHA, base branch, scope and policy version. It does not authorize adjacent changes, later commits, a new merge target or a different operation.

After the approval is recorded, AI must re-read the target state before acting. If the SHA, base, dependency graph or required checks change, mark the request Stale and ask for a fresh decision.

An owner approval recorded in chat or Notion is not automatically a GitHub native review approval. If repository protection requires a native review event or a credential unavailable to the AI, request the exact manual action and show its location. Never fabricate or impersonate that event.

## 8. GitHub-specific operating rules

| GitHub event/control | Required treatment |
|---|---|
| PR opened/updated | AI inspects and reports; no owner action unless a decision gate exists |
| CI failed | AI diagnoses and fixes within scope; do not request merge approval |
| CI passed | Evidence only; not an approval or merge authorization |
| Review requested | Identify whether it is technical evidence or GOV-01 decision; do not add another human reviewer requirement |
| Approve button | Use only when the owner is explicitly providing a review decision; AI never clicks it on the owner's behalf |
| Merge button | Request approval when policy requires; verify exact head, base, checks, reviews and dependencies immediately before merge |
| Resolve conversation | Resolve only after the finding is addressed; preserve unresolved status when work remains |
| Update branch/rebase | Re-check dependency graph and exact-head CI after the operation |
| Delete branch | Check merged state, open PR dependencies, stacked PRs and recovery path; ask GOV-01 if any dependency or irreversibility is unclear |
| Close PR | Never use as a substitute for resolving technical findings; request owner approval if closure changes the approved plan |

For stacked PRs, a parent/base branch change invalidates downstream assumptions. Retarget downstream PRs only in the approved dependency order, then rerun all required checks on their exact new heads.

## 9. Staleness, deduplication and safe stopping

An action request becomes **Stale** if any of the following changes after notification:

- PR head SHA or base SHA;
- target base branch or PR state;
- dependency/stacked-PR graph;
- required CI result or review disposition;
- repository rules, permissions, approval policy or autonomy tier;
- UI control path or provider access;
- PRE revision, acceptance criteria or authorized scope.

On staleness: stop the gated operation, invalidate the old approval, refresh evidence, update the existing Inbox record, and issue a new notice. Never carry an approval across a changed SHA unless the policy explicitly defines and verifies that equivalence.

Use idempotency keys derived from repository + action type + target PR/issue + exact SHA + policy version. One unresolved action per identical key; status changes update the same record.

## 10. Required implementation architecture for automated notification

The future UEDE implementation should add a **Human Action Notification & Approval Gate** under the Governance Guard / Workflow Controller, with these bounded components:

1. **GitHub Event Adapter:** observes relevant pull-request, review, check/workflow, issue-comment, push and branch events.
2. **Event Verifier:** verifies webhook signature, delivery ID, repository allowlist and event authenticity; rejects untrusted payloads.
3. **State Snapshotter:** reads current PR/base/head, checks, review threads, branch dependencies and policy revision from GitHub; never trusts stale event payload alone.
4. **Policy Classifier:** determines AUTO_ALLOWED, AWAITING_EVIDENCE, HUMAN_APPROVAL_REQUIRED, MANUAL_ACTION_REQUIRED, BLOCKED or STALE.
5. **Action Record Writer:** idempotently creates/updates the Notion Inbox record and a durable machine-readable action receipt.
6. **Notification Dispatcher:** posts a scoped GitHub issue/PR comment and owner notification only when the account identity and delivery route are verified; the assistant surfaces the same action in its response.
7. **Approval Receipt Verifier:** validates owner identity, exact action ID, scope, SHA, expiry and one-time use before releasing a gated workflow.
8. **Audit/Reconciler:** appends outcome, actor, timestamp, evidence URLs and final state; never overwrites historical decisions.

Minimum event controls: signed webhooks, delivery deduplication, replay protection, least-privilege GitHub App permissions, secret-manager storage, bounded retries, dead-letter handling, no secret values in notifications, and append-only audit.

**Current implementation boundary:** the Notion Inbox exists. This document does not claim that the GitHub Event Adapter, webhook verifier, notification dispatcher, approval receipt verifier or live push notifications have been deployed. The present interaction-level notification is the assistant's explicit action block plus the Notion record. Automated channels require a separately tested implementation.

## 11. Required end-of-response contract for all ecosystem prompts

Every substantive response or completed prompting task concerning HSMART, HSO, UEDE, PRE, their repositories, integrations, governance or project execution must end with these sections, in this order:

1. **Hasil dan status:** what was actually done, what was not done, and current state.
2. **Evidence and links:** exact repository, file, PR/issue, commit SHA, CI run and Notion record as applicable.
3. **Human action status:** HUMAN ACTION REQUIRED / AWAITING EVIDENCE / NO HUMAN ACTION REQUIRED. If required, include every field in Section 6.3.
4. **Risks and stop conditions:** what must not be clicked, merged, deleted, retargeted, deployed or assumed.
5. **Saran pengerjaan berikutnya:** one dependency-aware recommended next work item, with rationale.
6. **Prompt selanjutnya:** one ready-to-copy Indonesian prompt that continues from the verified state, names the exact scope and evidence, preserves all gates and explicitly prohibits unauthorized actions.

If no implementation action took place, say "analysis/design only". If a tool action failed, state the failure and its effect. Never imply that a PR was merged, service deployed, notification delivered or approval recorded without evidence.

## 12. Acceptance criteria

HAP-01 is not considered operationally implemented until all of the following are evidenced:

- [ ] Owner-only GOV-01 authority is represented consistently across HSMART, HSO and UEDE.
- [ ] Every human action notification contains a direct target link, exact UI position, instructions, expected result, risks and stale conditions.
- [ ] A single Notion Inbox row is created/updated idempotently for each active action.
- [ ] The owner can distinguish an approval decision from a manual UI operation.
- [ ] A changed head/base invalidates the old action request and approval.
- [ ] AI cannot approve its own work or fabricate a native GitHub review.
- [ ] GitHub events are authenticated, deduplicated and reconciled against current repository state.
- [ ] Notification delivery is tested end to end for the configured channel; untested channels are explicitly NOT_CONFIGURED.
- [ ] A rejected/expired/stale approval does not release the workflow.
- [ ] Every ecosystem response includes next-work advice and a ready-to-copy next prompt.

**Core rule:** AI performs bounded engineering work. GitHub records and validates repository changes. Notion preserves the owner-action ledger. UEDE coordinates and verifies. GOV-01 alone makes owner-level decisions.
