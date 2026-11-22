---
name: incident-response-orchestrator
description: Use when an AI agent may have followed malicious instructions, exposed data, performed an unauthorized action, suffered context or memory poisoning, or requires security incident triage and recovery planning.
---
# AI Agent Security Incident Response

## Objective
Provide a cautious, evidence-preserving response workflow for suspected or confirmed agent security incidents. Do not perform external containment actions unless the operator explicitly authorizes them through an available supported tool.

## Phases
1. **Triage:** classify suspected event, time window, affected agent/version, data and tools involved, observed symptoms, confidence and potential impact.
2. **Preserve evidence:** retain relevant prompts, source documents, retrieval IDs, memory changes, tool arguments/results, authorization records, timestamps and configuration versions. Minimize personal data and protect secrets.
3. **Contain:** recommend scoped actions such as disabling affected tool permissions, pausing workflows, isolating a compromised connector, blocking a poisoned source, freezing risky memory writes or requiring human approval. Consider business continuity and collateral impact.
4. **Eradicate:** remove malicious/poisoned content from controlled stores, revoke exposed credentials, correct authorization, patch vulnerable parsing/retrieval/orchestration logic and verify removal. Do not assume deleting a prompt fixes a backend flaw.
5. **Recover:** restore known-good configuration/data, rotate credentials where needed, validate tool scopes, run regression tests and re-enable capabilities gradually.
6. **Learn:** conduct root-cause review, identify detection gaps, update threat model, controls, test corpus and ownership.

## Incident record
`INC-ID | status | detection time | affected component | evidence | data/action impact | containment | owner | notifications to consider | recovery criteria | residual risk`.

## Decision safeguards
- Distinguish suspected from confirmed compromise.
- Do not destroy evidence before preservation.
- Do not claim regulatory notification obligations without checking applicable jurisdiction and facts.
- Escalate immediately to the system owner/security team for active exposure, real credential compromise, financial action, personal-data disclosure or safety impact.
- Recommend legal/privacy/compliance review when appropriate; do not provide definitive legal determinations.

## Output
Incident classification; timeline; evidence checklist; immediate containment recommendations; recovery plan; communication/escalation considerations; post-incident corrective actions; unresolved questions.
