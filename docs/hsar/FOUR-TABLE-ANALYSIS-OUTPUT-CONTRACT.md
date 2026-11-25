# HSAR Four-Table Analysis Output Contract

**Contract version:** 0.2.0  
**Status:** Proposed in PR; not merged

## Mandatory order

Every substantive HSAR analysis must produce four separate tables in this order. They must not be collapsed into a generic SWOT, scorecard, or findings table.

## Table 1 — Cross-method analysis

| Method ID | Methodology | Question addressed | Why selected | Evidence/input | Result/insight | Limitation/assumption | Confidence |
|---|---|---|---|---|---|---|---|

Select methods according to the question, system boundary, risk, and evidence. Candidate methods include first principles, systems thinking, causal-loop analysis, functional decomposition, MECE issue trees, morphology, root-cause analysis, 5 Whys, Ishikawa, dependency/data-flow/state-machine analysis, SWOT, PESTLE, capability mapping, value-stream analysis, FMEA/FMECA, fault-tree, bow-tie, STRIDE-style threat modeling, premortem, reliability engineering, architecture fitness functions, test-pyramid/contract testing, usability/cognitive-load analysis, and provenance/supply-chain analysis.

For every selected method, explain the question, fit, input evidence, applied procedure, insight, limitations, assumptions, and confidence. Cross-check material/high-impact findings with an independent method when evidence allows. Candidate methods not selected are not reported as applied.

## Table 2 — Positive analysis

| Positive ID | Strength/advantage | Evidence | Mechanism/source of value | Benefit/potential leverage | Reuse boundary | Confidence |
|---|---|---|---|---|---|---|

Assess strengths, differentiators, successful mechanisms, resilience, maintainability, scalability, reusable assets, operational leverage, positive side effects, attractiveness, strategic value, bargaining power, and future optionality where supported. Separate observed strengths from potential benefits and hypotheses.

## Table 3 — Negative analysis

| Negative ID | Weakness/failure | Symptom | Direct/root cause | Vulnerability or worst credible scenario | Impact/loss | Severity | Evidence/confidence |
|---|---|---|---|---|---|---|---|

Separate symptom, direct cause, root cause/hypothesis, contributing condition, credible failure path, affected party, and impact. Classify evidence as `PROVEN`, `SUPPORTED`, `HYPOTHESIS`, `UNKNOWN`, or `CONTRADICTED`. Worst credible scenarios require a plausible trigger and failure chain. Never fabricate likelihood, financial loss, or numeric risk scores.

## Table 4 — Negative-to-positive conversion

| Negative ID | Positive opportunity | Corrective solution | Preventive control | Mitigative/recovery control | Anticipatory/detective control | Evaluation measure | Acceptance test | Efficiency/effectiveness rationale | Residual risk |
|---|---|---|---|---|---|---|---|---|---|

Every material negative must map to a testable intervention or an explicit disposition (`ACCEPTED_RISK`, `DEFERRED`, `REJECTED_WITH_REASON`, or `NEEDS_DECISION`). Include owner role, dependency, reversibility, rollout, and rollback in the table or linked change record.

## Severity and prioritization

- `P0 CRITICAL`: severe security/safety/privacy/integrity failure, unauthorized side effect, or irreversible data loss.
- `P1 HIGH`: core function or essential control cannot be trusted.
- `P2 MEDIUM`: material reliability, quality, operational, or maintainability weakness.
- `P3 LOW`: limited-impact clarity, consistency, or polish issue.

Numerical scores require a defined scale, formula, source data, uncertainty, and sensitivity. Otherwise use qualitative assessments with explicit rationale.

## Traceability

Use `MTH-###`, `POS-###`, `NEG-###`, `CVT-###`, `RSK-###`, `REC-###`, `REQ-###`, `TST-###`, and `VFY-###`.

Each conversion links to its Negative ID; each acceptance test links to a requirement; each verification links to an exact evidence locator. If a table has no rows, include the table and mark `NONE_FOUND_WITHIN_DECLARED_SCOPE` with scan level and evidence limitations.

## Report close

After the four tables, include critical notes, trade-offs, recommendations, evaluation, prioritized development roadmap, acceptance criteria, residual risks, human decision gates, and Notion/GitHub evidence receipts or precise blockers.
