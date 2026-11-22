---
name: defense-architect
description: Use when designing or improving layered AI-agent defenses, trust boundaries, prompt architecture, retrieval and memory controls, tool authorization, monitoring, or secure workflow design.
---
# Defensive Agent Architecture

## Objective
Design defense in depth across model, application, data, tools, infrastructure and human governance. Prompt wording is one layer and cannot replace enforcement outside the model.

## Architecture layers
1. **Instruction and policy:** trusted configuration, explicit scope, separation of user intent and untrusted data, version control, conflict handling.
2. **Input and parsing:** file-type controls, safe parsing, OCR/transcription provenance, content normalization without loss of source identity.
3. **Retrieval and memory:** source allowlists/quality controls, provenance-preserving chunks, scoped retrieval, memory write authorization, expiry and correction.
4. **Context assembly:** trust labels, delimiters, source references, data minimization, injection-resistant summaries, truncation checks.
5. **Planning and agent orchestration:** typed messages, task contracts, delegation limits, provenance and independent validation of downstream agent outputs.
6. **Tool and API execution:** least privilege, server-side authorization, parameter validation, allowlisted destinations, rate limits, approval gates, idempotency and rollback.
7. **Output and data egress:** data-loss controls, recipient validation, scope checks, safe transformations and user-visible provenance where useful.
8. **Monitoring and response:** structured audit logs, anomaly signals, kill switches, credential revocation, containment and recovery.
9. **Governance:** ownership, risk acceptance, change review, testing cadence, incident escalation and evidence retention.

## Design workflow
- Translate findings into explicit security requirements.
- Map each requirement to an enforcement point, owner role, failure mode and verification test.
- Prefer deterministic application/backend controls for permissions and side effects.
- Define fail-safe behavior without unnecessarily blocking legitimate tasks.
- Assess usability, accessibility, privacy, latency, operational burden and residual risk.
- Include change impact for model, prompt, tool, retrieval, memory and corpus updates.

## Deliverables
Threat-model-informed reference architecture; trust-boundary map; control matrix (prevent/detect/contain/recover); revised prompt template if requested; backend requirements; monitoring and incident triggers; test plan; residual risk register.

## Guardrails
Never claim prompt text alone can enforce authorization. Do not recommend exposing secrets to the model. Do not present generic templates as drop-in secure implementations without adapting to actual tools and deployment.
