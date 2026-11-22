---
name: agent-threat-modeler
description: Use when scoping an AI agent security review, mapping assets and trust boundaries, identifying attack surfaces, threat actors, abuse cases, and credible attack paths.
---
# AI Agent Threat Modeler

## Objective
Produce an explicit, revisable threat model before proposing controls. Do not treat a list of scary prompts as a threat model.

## Required inputs
System purpose; architecture/version; model and orchestration layer if known; data classes; users and roles; tools; retrieval/memory; modalities; deployment environment; network boundaries; external dependencies; authorization model; operational impact; test authorization.

## Procedure
1. Define scope, exclusions, assumptions and system boundary.
2. Inventory assets: instructions/configuration, user data, secrets, retrieved corpora, memory, tools, credentials, execution environments, logs, model outputs, external systems and human approvals.
3. Map actors: ordinary users, malicious users, compromised sources, third-party content providers, insiders, compromised tools, adjacent agents and accidental operators. Do not infer real-world intent without evidence.
4. Draw trust zones and data/control flows: ingress, parsing, retrieval, context assembly, reasoning, tool planning, authorization, execution, output, persistence and monitoring.
5. Identify attack surfaces: direct input, multi-turn state, attachments, OCR, audio/video, RAG, vector DB, memory, browser, code interpreter, APIs, plugins, agent handoffs, logs and feedback pipelines.
6. Enumerate abuse cases: authority spoofing, policy evasion, context poisoning, sensitive-data exposure, unauthorized action, tool misuse, denial/degradation, evaluator contamination and supply-chain compromise.
7. For each scenario document preconditions, path, asset, impact, existing controls, detection opportunity, plausible likelihood rationale, and unknowns.
8. Prioritize using impact, exposure, preconditions, privilege, blast radius, detectability, reversibility and recovery capability. Avoid unsupported numeric risk scores.

## Threat-model lenses
Use STRIDE-like categories where useful (spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege), but adapt them to agent-specific control flow. Include the OWASP LLM/agent risk concepts only when the exact framework/version is known and verified; do not fabricate standard mappings.

## Output
- Scope and assumptions.
- Asset inventory and sensitivity.
- Trust-boundary/data-flow map in text or Mermaid.
- Attack-surface inventory.
- Threat scenario register with IDs `THR-###`.
- Existing controls and gaps.
- Prioritized validation questions and handoff to audit/test modules.

## Guardrails
Threat modeling is not proof of exploitability. Mark scenarios as observed, plausible, or hypothetical. Do not provide exploit chains or payloads that enable unauthorized access. Use safe descriptions and mock systems.
