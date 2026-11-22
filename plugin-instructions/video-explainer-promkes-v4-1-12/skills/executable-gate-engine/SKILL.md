---
name: executable-gate-engine
description: "Use when M00 must execute, test, evaluate, report, or troubleshoot the Promkes V4 evidence-contract validator and production gates."
---

# Promkes V4 executable gate engine — private package boundary

The private Plugin Creator package still contains the legacy `scripts/v4_gate_engine.py` implementation with a legacy 21-control `CTRL-*` registry and structural approval records. GitHub PR #14 is MERGED at `0e9c56a0246852d3a36bf1b28b8bb5078cb8bd11`; PR #16 is MERGED at `8330b9e61eb37c94d38630188dce3a75721d1643`. The V4-CTL candidate is in GitHub main, not synchronized into this private package. Exact-main GitHub CI at SHA `8330b9e6...` passed 93 pytest tests (run 43258911702) and Markdown link checking (run 43258911670). No independent review submissions were returned for PR #14/#16. See `docs/engine-parity-status.md`.

## Critical release prohibition

Do not use the private legacy CLI `evaluate` or `--require-release` result as final production authorization. The legacy `evaluate_project()` path does not enforce the newer `project_mode == PRODUCTION` synthetic-fixture guard. Treat every TEST_FIXTURE, sample, demo, mock, incomplete, unsigned or non-production project as BLOCKED regardless of a legacy report. Never describe this private engine as containing GitHub's V4-CTL registry, its synthetic fixture guard or an authenticated real-world approver.

## Execution contract
1. Check whether Python runtime and package files are genuinely available; never claim execution from reading this skill or static code.
2. Install requirements only when network/package installation is permitted.
3. Run `python -m pytest -q`; record exact command, Python/dependency versions, exit code, count and output.
4. Validate claim/artifact records using the actual package commands, not a presumed command path.
5. Use `evaluate` only diagnostically until the private engine is synchronized and validated.
6. Preserve JSON report and input hashes; report every gate/control, reason, evidence and limitation.
7. Compute dependency impact; create a distinct revised snapshot rather than overwrite the source; rebuild downstream artifacts and renew approvals bound to old hashes.

## Legacy gate and control boundaries
The private engine defines eight sequential gates and 21 legacy CTRL controls. This is not GitHub's V4-CTL registry. The 1,000 candidate control definitions are planning candidates, not executed tests: executed_count=0, NOT_RUN=1,000, NOT_VERIFIED=1,000.

## Acceptance suite boundaries
The private package's `tests/acceptance-cases.json` contains 20 records. GitHub main has a separate 45-case suite in its repository file of the same name; IDs AT-001 onward have different meanings. Use PRIVATE-AT-### and GITHUB-AT-### namespaces. Neither suite is PASS from aggregate pytest. Every case requires its own oracle and execution evidence; both suites remain NOT_RUN in the V4.1.5 audit snapshot.

## Approval and evidence boundaries
- Approval registry checks are structural; they do not authenticate a person's identity, clinical license, authority or signature.
- A SHA-256 proves byte identity, not factual accuracy, authority or rights.
- Prompt-injection detection is heuristic and cannot prove model behavior safe.
- Renderer capability records are supplied evidence, not live Remotion invocation.
- Artifact QA does not decode or perceptually inspect a video unless an independent media tool actually runs.
- Synthetic fixtures/local unit tests do not constitute live ChatGPT, external AI/ASR/diarization/TTS, Remotion render, MP4 QA, accessibility testing or institutional approval.

Public/production distribution remains HOLD until independent engine review, exact-head CI, reviewed parity, actual runtime/media evidence and authorized human approvals are complete.
