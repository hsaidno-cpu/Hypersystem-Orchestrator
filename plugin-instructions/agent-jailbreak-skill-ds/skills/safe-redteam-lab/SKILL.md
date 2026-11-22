---
name: safe-redteam-lab
description: Use when creating safe, authorized, reproducible adversarial test cases, fixtures, benchmark matrices, or regression suites for AI-agent security.
---
# Safe Red-Team Lab

## Purpose
Design controlled tests for defensive validation. This skill authors test specifications; it does not execute tests against external agents.

## Test-case contract
Each test includes: ID/version; objective; scope and authorization; preconditions; trusted task; inert untrusted fixture; expected behavior; failure conditions; evidence to capture; severity rationale; reset procedure; repeatability notes; coverage tags.

## Test families
1. Authority hierarchy and role spoofing.
2. Refusal suppression and policy-boundary preservation.
3. Secret non-disclosure using mock values.
4. Tool-call authorization and side-effect prevention.
5. RAG corpus poisoning and retrieval citation integrity.
6. Memory write integrity and persistence boundaries.
7. Multimodal OCR/audio/video instruction handling using harmless fixtures.
8. Transformation/translation laundering and final semantic checks.
9. Cross-agent handoff and provenance preservation.
10. Context-length, truncation and multi-turn task integrity.
11. Evaluator contamination and benchmark-oracle independence.
12. Benign-use calibration and false-positive controls.
13. Tool result spoofing and action confirmation.
14. Recovery, logging and rollback behavior.

## Test matrix dimensions
Vary source channel, trust level, modality, agent component, attack family, task type, context length, privilege level, side-effect class, expected outcome and severity. Include negative controls and benign near-neighbor cases.

## Test quality
- Expected outcomes must be defined independently of adversarial fixture.
- Use synthetic documents, mock secrets, fake identities and inert destinations.
- Include at least one control case for benign content to measure overblocking.
- Define observable evidence and deterministic pass/fail criteria.
- Separate unit, integration, end-to-end and tabletop tests.
- Record model/version/configuration, prompt version, tool schema, corpus snapshot, test date and run conditions when supplied.
- Do not overgeneralize from a small sample.

## Coverage and reporting
Report tested/not-tested coverage by attack family and component. Identify sampling gaps, flaky outcomes, environment mismatch and repeat runs. Do not invent statistical confidence or claim benchmark representativeness without a sampling design.

## Output
Versioned test plan, test-case catalog, coverage matrix, expected outcomes, evidence schema, reset instructions and regression triggers.

## Safety boundary
No deployable bypass payloads, real secrets, live unauthorized targets, malware, credential theft, covert persistence or harmful execution. Keep tests inert and scoped.
