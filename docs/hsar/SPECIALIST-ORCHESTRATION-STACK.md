# HSAR Combined Specialist Orchestration Stack

**Contract version:** 0.2.0  
**Status:** Proposed in PR; not merged  
**Scope:** HSAR orchestration behavior for substantive forensic analysis, system design, reconstruction, and skill/plugin development.

## 1. Specialist sequence

| Order | Specialist | Primary responsibility | Required handoff artifact |
|---|---|---|---|
| 1 | SKILL ANALYZER | Forensic diagnosis, method selection, evidence audit, root-cause analysis, negative collection, and evaluation | Method blueprint, evidence register, findings dossier, root-cause map |
| 2 | ANATOMI PROMPT v3.0 — OCTA-PROMPT | Instruction/requirement architecture across eight pillars | Octa gap matrix, target instruction architecture, acceptance map |
| 3 | ASFREE | Artifact inventory, provenance, deep deconstruction, and authorized reconstruction | Artifact inventory, deconstruction map, reconstruction specification |
| 4 | AI Workflow Systems Orchestrator | Design, decomposition, construction, integration, evaluation, and optimization of AI work systems | Workflow/system blueprint, interfaces, orchestration and recovery design |
| 5 | Evaluator Team | Independent/adversarial assessment of evidence, design, and implementation | Evaluation dossier, counterexamples, severity-ranked gaps, acceptance disposition |
| 6 | Skill Developer Orchestrator | Controlled implementation, versioning, regression, packaging, and release assurance | Change set, tests, verification report, release/PR handoff |

The order is a logical dependency chain. Iteration is permitted when evaluation exposes a root-cause gap. This contract does not imply that six autonomous agents execute in parallel.

## 2. Invocation and version honesty

Each specialist is recorded with canonical identity, requested version, observed version, host, action, output artifact/evidence, and limitation.

Allowed states:

- `INVOKED`: a distinct plugin/skill/tool call was observed.
- `PROCEDURE_APPLIED`: documented method applied without a separate invocation.
- `UNAVAILABLE`: the required capability could not be invoked or safely substituted.
- `NOT_USED`: intentionally omitted because it is not relevant, with rationale.

A mention, catalog row, installed skill file, app URL, or previous conversation does not prove current invocation. Requested and observed versions remain separate. In particular, access to an Anatomi Prompt v1.x skill does not establish invocation or equivalence of OCTA-PROMPT v3.0.

When an exact version is unavailable, HSAR may apply a compatible documented method and must disclose the fallback, fidelity limitation, and residual uncertainty. Permission denial must never be bypassed by another executor/account.

## 3. Handoff model

`INTENT → ANALYSIS DOSSIER → OCTA GAP MATRIX → ARTIFACT DECONSTRUCTION → WORKFLOW BLUEPRINT → EVALUATION DOSSIER → IMPLEMENTATION PACKAGE → REGRESSION/EVIDENCE → ADOPTION/DOCUMENTATION`

Each artifact receives a stable ID and records upstream inputs, downstream consumers, tests, evidence, and decision.

Recommended identifiers: `MTH-###`, `FND-###`, `RSK-###`, `OCTA-###`, `ART-###`, `WF-###`, `REC-###`, `REQ-###`, `TST-###`, `VFY-###`, and `DEC-###`.

## 4. Design and safety boundaries

- SKILL ANALYZER diagnoses; it does not authorize writes.
- OCTA-PROMPT designs instruction architecture; it does not prove source behavior.
- ASFREE deconstructs and reconstructs only authorized material; it does not override source ownership or licensing.
- AI Workflow Systems Orchestrator designs workflows; a design is not a deployed integration.
- Evaluator Team challenges evidence and acceptance; it does not replace the user's final decision rights.
- Skill Developer Orchestrator manages controlled implementation; it does not imply merge, release, or production deployment.
- HSAR internal skills remain responsible for fullscan, anatomy/physiology, source forensics, controlled reconstruction, Trilogy Analysis, improvement adoption, documentation sync, and evidence assurance.

Stop with `BLOCKED` or `HOLD` when an essential specialist and valid fallback are unavailable, source rights are uncertain, critical evidence is contradictory, or implementation crosses an unapproved authority boundary.
