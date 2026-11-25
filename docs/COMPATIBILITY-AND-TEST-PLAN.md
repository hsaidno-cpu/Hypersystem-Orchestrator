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

## 2. Sixteen defined integration edges

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

15. Ponytail Engineering System → SDO: bounded engineering change dossier and controlled source-write handoff.
16. GrowthForge Business Prompt Architect → Anatomi Prompt: optional business-task prompt brief to Octa-Prompt structural specification.

These are interface definitions and routing constraints. They are not hard runtime dependencies unless the matrix explicitly says so.

## 3. Progressive verification gates

| Gate | What is checked | Minimum evidence | Current status |
|---|---|---|---|
| C0 — Identity | Producer/consumer exist, source/version identity is known | Plugin catalog and source registry | STATIC_VALIDATED by parent CI |
| C1 — Routing | Positive/negative trigger and primary owner are correct | Routing contract and regression assertions | STATIC_VALIDATED by parent CI |
| C2 — Schema | Real payload validates against the handoff JSON Schema | 15 synthetic valid fixtures + negative schema cases for established tested edges; GrowthForge→Anatomi remains excluded until its C2 contract fixture exists | PASS — 15/15 established edges; new interface NOT_RUN |
| C3 — Contract behavior | Producer artifact can be accepted or rejected by consumer using mock/fixture data | 15 mock receiver acceptances + negative producer/recipient/version/output cases for established edges; GrowthForge→Anatomi C3 remains NOT_RUN | PASS — 15/15 established edges (mock); new interface NOT_RUN |
| C4 — Host activation | Named host, model/provider and release select the expected plugin route | Host/version test evidence | NOT_RUN |
| C5 — Runtime | Actual end-to-end handoff/execution and artifact read-back | Trace, output artifact, timestamps and failure evidence | NOT_RUN |

A static PASS must never be copied into C2–C5. NOT_RUN is a valid status.


### Executed C2/C3 evidence — 23 November 2026

- PR: [#8 — C2/C3 handoff assurance fixtures](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/8)
- Tested commit: `3bd10b5f550a3ac6994a4c4fa792e62f7513fd25`
- CI: [run #45149817422](https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/45149817422) — `completed/success`
- Test suite: `Ran 33 tests — OK`; includes 14/14 schema-valid synthetic payloads, 14/14 mock receiver acceptances, and expected rejection tests for invalid/mismatched payloads.
- Matrix disposition: `CONTRACT_TESTED`; `schema_contract_test=PASS`; `contract_behavior_test=PASS` for all 14 edges.
- Boundary: this evidence is limited to JSON Schema and deterministic mock receiver behavior. No real producer/consumer plugin was invoked. C4 host activation and C5 runtime execution remain `NOT_RUN`.

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

The parent CI validates the existence of each plugin identity, unique integration IDs, allowed producer/consumer relationships, owner fields and explicit test states. Fifteen established edges have C2 schema and C3 mock-receiver evidence on the PR #15 head; the additional GrowthForge→Anatomi edge is interface-defined only, with C2/C3 NOT_RUN. Host activation and runtime execution remain NOT_RUN for all edges.

The next test implementation step is to add representative valid/invalid handoff fixtures for the highest-risk edges, beginning with PVEE→Video Explainer and Evaluator Team→SDO. Host testing follows only when a host supports distinct plugin dispatch and read-back evidence is available.


### GrowthForge Business Prompt Architect → Anatomi Prompt

This optional handoff is registered as `INT-GROWTHFORGE-ANATOMI-001`. GrowthForge owns business-task intent and domain constraints; Anatomi owns the eight-pillar structural specification. It must not be selected for ordinary business deliverable execution or source-media reconstruction.

Current state: `INTERFACE_DEFINED_NOT_EXECUTED`; static route defined; C2 schema, C3 mock receiver, C4 host activation and C5 runtime execution are all `NOT_RUN`. Add positive and negative contract fixtures, schema validation, mock receiver behavior and failure cases before upgrading its C2/C3 status. Do not treat a prompt build or a declarative route as an invoked plugin.
