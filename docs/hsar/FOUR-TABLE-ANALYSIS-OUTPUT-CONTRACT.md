# HSAR Four-Core-Table Analysis Output Contract

**Contract version:** 0.3.0  
**Status:** Proposed in PR; not merged

## Mandatory four-table order

Every substantive HSAR analysis must produce four separate tables in this order. They must not be collapsed into a generic SWOT, scorecard or findings table.

## Table 1 — Cross-method analysis

| Method ID | Methodology | Question addressed | Why selected | Evidence/input | Result/insight | Limitation/assumption | Confidence |
|---|---|---|---|---|---|---|---|

The methodology registry is open-ended. Starter examples include First Principles, Systems Thinking, MECE, functional decomposition, causal-loop/root-cause analysis, 5 Whys, Ishikawa, morphology, dependency/data-flow/state-machine analysis, SWOT, PESTLE, FMEA/FMECA, Fault Tree, Bow-tie, STRIDE-style threat modelling, premortem, reliability engineering, Architecture Fitness Functions, ATAM-style trade-offs, test-pyramid/contract/property/fuzz testing, provenance/supply-chain analysis, usability/cognitive-load analysis, and later evidence-backed methods. For every selected method explain fit, required input, procedure, insight, assumptions, limitations and confidence. Candidate methods not selected are not reported as applied. A method must pass screening/pilot/validation before adoption as a standard.

## Table 2 — Positive analysis

| Positive ID | Target object | Strength/advantage | Evidence | Mechanism/source of value | Benefit/potential leverage | Reuse boundary | Confidence |
|---|---|---|---|---|---|---|---|

Assess strengths, differentiators, working mechanisms, resilience, maintainability, scalability, reusable assets, operational leverage, side effects, attractiveness, strategic value, bargaining power and future optionality where supported. Separate observed strengths from hypotheses and potential benefits.

## Table 3 — Negative analysis

| Negative ID | Target object | Weakness/failure | Symptom | Direct/root cause | Vulnerability or worst credible scenario | Impact/loss | Severity | Evidence/confidence |
|---|---|---|---|---|---|---|---|---|

Separate symptom, direct cause, root-cause hypothesis, contributing condition, plausible failure chain, affected party and impact. Classify evidence as PROVEN, SUPPORTED, HYPOTHESIS, UNKNOWN or CONTRADICTED. Do not fabricate likelihood, financial loss or numerical risk.

## Table 4 — Negative-to-positive conversion

| Negative ID | Target object | Positive opportunity | Corrective solution | Preventive control | Mitigative/recovery control | Anticipatory/detective control | Evaluation measure | Acceptance test | Efficiency/effectiveness rationale | Residual risk |
|---|---|---|---|---|---|---|---|---|---|---|

Every material negative maps to a testable intervention or explicit disposition: ACCEPTED_RISK, DEFERRED, REJECTED_WITH_REASON or NEEDS_DECISION. Include owner role, dependency, reversibility, rollout and rollback in the table or linked change record.

## Severity and traceability

- P0 CRITICAL: severe security/safety/privacy/integrity failure, unauthorized side effect or irreversible data loss.
- P1 HIGH: core function or essential control cannot be trusted.
- P2 MEDIUM: material reliability, quality, operations or maintainability weakness.
- P3 LOW: limited-impact clarity, consistency or polish issue.

Numerical severity/risk scores require defined scale, formula, source data and uncertainty. Use IDs MTH, POS, NEG, CVT, RSK, REC, REQ, TST and VFY. Every conversion links to its Negative ID; every test links to a requirement; every verification links to exact evidence. Empty tables remain present and state NONE_FOUND_WITHIN_DECLARED_SCOPE with coverage and limitations.

## Comparative expansion: activate two additional tables

When the user explicitly requests comparison, benchmarking, ranking, alternatives or feature comparison, append Table 5 and Table 6 after the four core tables. The full 4+2 criteria, rubric and fairness controls are defined in COMPARATIVE-4PLUS2-OUTPUT-CONTRACT.md.

- **Table 5 — Comparative scorecard:** compare the four analytical dimensions across every target object and include value, anchored 0–5 score or N/A, classification, evidence coverage, confidence, positive/negative evidence, conversion progress, comparative delta and caveat.
- **Table 6 — Feature-gap/evaluative recommendation:** include current state, target/benchmark, gap, current score, target score, gap score, value/opportunity, evaluative suggestion, priority/classification, effort/cost basis, acceptance test/indicator and residual risk.

Unknown evidence is N/A, not zero. Never rank incomparable scope/version/sample data. Composite scores are not aggregated by default and cannot override a hard P0/P1 gate.

## Report close

After the four tables, or six tables in comparison mode, include critical notes, counterevidence, trade-offs, recommendations, evaluation, prioritized roadmap, acceptance criteria, residual risks, human decision gates and Notion/GitHub receipts or precise blockers.
