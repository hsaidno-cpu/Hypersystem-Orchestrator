# HSAR Adaptive Methodology Registry and Evolution Contract

**Version:** 0.3.0  
**Status:** Proposed in PR; not merged

## 1. Open methodology scope

HSAR does not use a closed methodology whitelist. The current catalogue is a starter collection, not a boundary on future methods. HSAR may discover and evaluate new or more effective methodologies when a real analytical gap exists, and may screen, pilot, validate, adopt, extend, version, reject, defer, retire or supersede methods.

Examples include First Principles, Systems Thinking, MECE, Functional Decomposition, Root Cause Analysis, 5 Whys, Ishikawa, SWOT, PESTLE, FMEA/FMECA, Fault Tree, Bow-tie, STRIDE-style threat modelling, dependency/data-flow/call-graph/state-machine analysis, reliability engineering, architecture fitness functions, test-pyramid/contract/property/differential/fuzz testing, morphology, capability mapping, value-stream analysis, premortem, ATAM-style trade-off analysis, horizon scanning, scenario planning, backcasting, usability/accessibility/cognitive-load analysis, provenance/supply-chain analysis, and applicable domain-specific standards or newer evidence-backed methods.

This list is illustrative and non-exhaustive. New discovery does not make a method valid, superior or suitable by itself.

## 2. Method lifecycle

CANDIDATE → SCREENED → PILOTED → VALIDATED → ADOPTED

Alternative dispositions: REJECTED, DEFERRED, RETIRED, SUPERSEDED.

A method must not be presented as validated/adopted until its domain fit, source, repeatable procedure, evidence, comparison baseline, limitations, resource costs and decision record are available.

## 3. Method card

Every maintained method record should include:
- Stable ID, canonical name, aliases, version/revision and lifecycle status.
- Origin/author/publisher, primary source URL/DOI/repository, publication and retrieval dates.
- Intended domain, questions, inclusion/exclusion criteria, assumptions and known misuse conditions.
- Required inputs, data quality, sample/coverage assumptions and preconditions.
- Reproducible stepwise procedure, decision rules and expected outputs.
- Strengths, weaknesses, bias risks, failure modes and limitations.
- Complexity, time, compute, skill, operational cost and observed/estimated label.
- Evidence quality, benchmark/comparator, test protocol and results.
- Compatibility, tool/dependency/licensing constraints.
- Acceptance criteria, reviewer disposition, confidence, residual uncertainty and next review trigger.

## 4. Discovery, screening and pilot

1. State the analytical gap that motivates discovery.
2. Search authoritative primary sources first: research publications, standards bodies, specifications and maintained technical documentation.
3. Record publication date separately from discovery/retrieval date. Distinguish new method from a newly found or renamed variant.
4. Screen domain fit, assumptions, evidence quality, reproducibility, data requirements, legal/ethical boundaries, implementation cost and operational feasibility.
5. Pilot against a baseline method on the same input/sample and common outcomes.
6. Compare coverage, discrimination, robustness, counterexample sensitivity, reproducibility, time/compute, cognitive load, bias and decision value.
7. Adopt only when a repeatable benefit is demonstrated for the stated use case, or when a distinct complementary value is clearly justified.
8. Version the method card and preserve earlier revisions and decisions.
9. Re-evaluate when sources, domains, datasets, model/tool versions or assumptions materially change.

## 5. Method conflict and governance

When methods disagree:
- Preserve each method's conclusion and its assumptions.
- Identify divergent constructs, scope, input quality and evidence.
- Seek counterevidence and a discriminating test.
- Record whether the conflict is resolved, conditional or inconclusive.
- Do not erase dissent by averaging incompatible scores.

Avoid novelty bias and unsupported claims such as “latest”, “best” or “more efficient” without dated sources and comparator evidence. Missing evidence remains UNKNOWN or NOT_ASSESSED. A method recommendation does not grant authority to change a system or waive human approval.
