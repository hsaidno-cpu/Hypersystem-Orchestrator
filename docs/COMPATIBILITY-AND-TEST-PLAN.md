# Plugin Compatibility and Progressive Test Plan

**Version:** 1.1.0  
**Matrix:** catalog/compatibility-matrix.json  
**Handoff schema:** contracts/plugin-handoff.schema.json  
**Matrix schema:** contracts/plugin-compatibility.schema.json

## 1. What compatibility means

Compatibility is not a binary property of two plugin names. It is specific to a handoff contract, version pair, artifact, data format, scope and test environment.

The matrix records:
- producer and consumer;
- exact purpose and allowed handoff type;
- input/output artifacts;
- owner of the produced artifact, consumed artifact and canonical truth;
- whether the relationship is optional, a routing override or a domain gate;
- separate static-routing, schema-contract, host-activation and runtime-execution statuses.

A declared handoff does not mean that the platform can invoke either plugin programmatically.

## 2. Fifteen defined integration edges — current matrix

1. SKILL ANALYZER → A.S.F.R.E.E: method blueprint to technical anatomy case.
2. A.S.F.R.E.E → Evaluator Team: evidence-backed anatomy dossier to independent scoring.
3. Evaluator Team → SDO: accepted findings and criteria to the sole engineering write owner.
4. SDO → Evaluator Team: implementation/regression evidence for independent retest.
5. AI Prompt Finder → Anatomi Prompt: reconstructed prompt to eight-pillar hardening.
6. Anatomi Prompt → SDO: accepted instruction architecture to controlled implementation.
7. Photo Fixer → Master Photo Restoration: archival restoration routing override.
8. GODEX → Motion Graphic: audio/VO/timing manifest to visual synchronization.
9. GODEX → Video Explainer: Promkes audio/transcript/timing package to production.
10. PVEE → Video Explainer: approved Fact Lock and campaign brief to technical production.
11. Motion Graphic → Video Explainer: optional visual style and art-direction support.
12. Video Explainer → PVEE: technical production QA and delivery evidence.
13. Agent Jailbreak DS → Plugin Agent Orchestrator: threat model and security-control handoff.
14. Workflow Systems → Plugin Agent Orchestrator: workflow/SOP architecture for an AI-agent runtime.
15. Ponytail Engineering Optimizer → SDO: a bounded minimal-complete engineering dossier; SDO remains the sole source-write, regression, pull-request and release-preparation owner.

These are interface definitions and routing constraints. They are not hard runtime dependencies unless the matrix explicitly says so.

## 3. Progressive verification gates

| Gate | What is checked | Minimum evidence | Current status |
|---|---|---|---|
| C0 — Identity | Producer/consumer exist, source/version identity is known | Plugin catalog and source registry | STATIC_VALIDATED by parent CI |
| C1 — Routing | Positive/negative trigger and primary owner are correct | Routing contract and regression assertions | STATIC_VALIDATED by parent CI |
| C2 — Schema | Synthetic payloads validate against the handoff JSON Schema | Historical 14 fixtures on 23 Nov; current 15 fixtures and negative schema cases; CI run #45698994293 | PASS — 15/15 current |
| C3 — Contract behavior | Producer artifact can be accepted or rejected by consumer using mock/fixture data | Historical 14 mock acceptances on 23 Nov; current 15 strict mock receiver acceptances plus negative mismatch cases; CI run #45698994293 | PASS — 15/15 current (mock) |
| C4 — Host activation | Named host, model/provider and release select the expected plugin route | Host/version test evidence | NOT_RUN |
| C5 — Runtime | Actual end-to-end handoff/execution and artifact read-back | Trace, output artifact, timestamps and failure evidence | NOT_RUN |

A static PASS must never be copied into C2–C5. NOT_RUN is a valid status.


### Historical executed C2/C3 evidence — 23 November 2026 (14-edge baseline)

- PR: [#8 — C2/C3 handoff assurance fixtures](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/8)
- Tested commit: `3bd10b5f550a3ac6994a4c4fa792e62f7513fd25`
- CI: [run #45149817422](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/45149817422) — `completed/success`
- Test suite: `Ran 33 tests — OK`; includes 14/14 schema-valid synthetic payloads, 14/14 mock receiver acceptances, and expected rejection tests for invalid/mismatched payloads.
- Matrix disposition: `CONTRACT_TESTED`; `schema_contract_test=PASS`; `contract_behavior_test=PASS` for all 14 edges.
- Boundary: this evidence is limited to JSON Schema and deterministic mock receiver behavior. No real producer/consumer plugin was invoked. C4 host activation and C5 runtime execution remain `NOT_RUN`.

### Current 15-edge C2/C3 evidence — 26 November 2026

The current machine-readable matrix contains `integration_count=15`, including `INT-PONYTAIL-SDO-001`. The current test module `tests/test_contract_assurance.py` now verifies:
- fixture inventory covers all 15 matrix edges;
- C2 validates all 15 synthetic payloads against the handoff schema;
- C3 accepts all 15 exact producer/consumer/output/acceptance contracts through a strict mock receiver;
- negative producer, recipient, contract-version and output-artifact mismatch cases are rejected;
- fixture metadata and matrix states do not claim host/runtime execution.

The latest post-merge HSO catalog/distribution validation [run 45698994293](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/45698994293) passed its `validate` job; the log records `Ran 142 tests — OK`, including the 15-edge C2/C3 tests. This is current repository CI evidence for schema and mock contract behavior, not a real plugin invocation. All 15 matrix rows remain `CONTRACT_TESTED`; C4 host activation and C5 runtime execution remain `NOT_RUN`.

## 4. Required test cases per edge

For every handoff:
- positive test: correct intent reaches the intended primary plugin;
- negative test: adjacent plugin does not capture out-of-scope work;
- schema test: required handoff fields, enum values, unknown/missing data and provenance;
- version test: compatible producer/consumer contract versions and explicit mismatch behavior;
- authorization test: least-privilege action and no implicit permission escalation;
- failure test: missing artifact, stale source version, malformed handoff, partial success, timeout and fallback;
- acceptance test: receiver accepts/rejects with evidence and does not assume the producer's claims are true.

## 5. Highest-risk integration gates

### PVEE → Video Explainer
- PVEE Fact Lock is the authoritative health-content input.
- Video Explainer must reject or flag unsupported/changed health claims.
- Technical renderer QA does not equal clinical, legal or publication approval.

### Evaluator Team → SDO
- Evaluator Team cannot write/merge the same source while SDO is the assigned engineering owner.
- SDO cannot independently approve its own quality score.
- Retest must trace to the original acceptance criteria.

### GODEX → Motion Graphic/Video Explainer
- Timing precision must retain provenance (word/phrase/segment/estimated/none as applicable).
- Visual timing must not silently upgrade estimated audio timestamps into exact word timing.
- Audio mix and visual choreography remain separate artifact owners.

### Photo Fixer → Master Photo Restoration
- Old, damaged, faded or archival restoration goes to Master Photo Restoration.
- Routine editing remains with Photo Fixer.
- The internal Photo Fixer restoration subskill needs a source-level trigger narrowing before its package can be described as fully aligned.

## 6. Current compatibility status

The parent CI validates the existence of each plugin identity, unique integration IDs, allowed producer/consumer relationships, owner fields and explicit test states. The 23 November PR #8 evidence is a historical 14-edge baseline. On the current 26 November matrix, C2 schema fixtures and C3 mock receiver behavior pass for all 15 edges (including Ponytail→SDO) in the latest catalog-validation run 45698994293. Host activation and runtime execution remain NOT_RUN.

The next test implementation step is to add representative valid/invalid handoff fixtures for the highest-risk edges, beginning with PVEE→Video Explainer and Evaluator Team→SDO. Host testing follows only when a host supports distinct plugin dispatch and read-back evidence is available.
