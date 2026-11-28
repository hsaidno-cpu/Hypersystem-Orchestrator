# SDO Source Reconciliation and Independent Evaluation Runtime

**Checkpoint:** 26 November 2026  
**HSO baseline:** \`69479c9fc898d12d6780964fb431fb9a89b1c675\`  
**SDO source:** \`promkespkmbinuang-coder/SPDO\` at \`9d3c4bc09179ff857df4f3819be83e1847571add\`  
**Plugin Creator package:** \`Plugin_a5294996e38c8191b8e20b2d9f61447a\`, release \`pluginrel_6afdee10a5688191ad8fc37a9d0d827b\`, version \`0.1.0\`

## 1. Scope decision

This work is limited to SDO content/capability reconciliation and an HSO-hosted independent evidence gate. HSO distribution eligibility, HSO catalog promotion, public launch, and public/private distribution policy are explicitly out of scope for this checkpoint and remain separate work.

The canonical **repository identity and provenance anchor** is \`promkespkmbinuang-coder/SPDO\` at the immutable commit above. The current Plugin Creator release is treated as the active runtime projection that must be reconciled back to that source. This does not authorize deleting richer runtime procedures. The seven shared files must be merged deliberately so that the repository source retains the complete operational capability set before the runtime projection is rebuilt from it.

## 2. File-level parity result

The audit compares the current Plugin Creator release with the pinned Git source after line-ending normalization. Seven paths are present on both sides; none is identical.

| Shared path | Package size (characters) | Git source size (characters) | Result |
|---|---:|---:|---|
| README.md | 849 | 990 | DRIFT |
| plugin.json | 2,020 | 1,720 | DRIFT |
| skills/skill-developer-orchestrator/SKILL.md | 23,651 | 10,573 | DRIFT |
| skills/skill-developer-orchestrator/references/audit-matrix.md | 4,874 | 3,111 | DRIFT |
| skills/skill-developer-orchestrator/references/github-change-protocol.md | 4,596 | 2,497 | DRIFT |
| skills/skill-developer-orchestrator/references/regression-and-release-gates.md | 4,500 | 3,030 | DRIFT |
| tests/acceptance-cases.json | 3,937 | 1,882 | DRIFT |
| **Total** | **7 paths** | **7 paths** | **0/7 exact matches** |

Additional path asymmetry:

- Plugin Creator only: \`.codex-plugin/plugin.json\`
- Git source only: \`LICENSE\`

The Git master skill is materially shorter than the active runtime master. The package has a richer 11-stage operating procedure, specialist orchestration boundaries, authorization rules, output contract, recovery rules and completion gates. Do not replace it with the shorter source copy without a semantic merge.

## 3. Capability-to-file ownership map

| Capability | Canonical SDO file |
|---|---|
| Plugin identity, manifest, host interface and version | plugin.json |
| User-facing purpose and package inventory | README.md |
| Intake, mode selection, authorization, capability readiness, specialist routing, full-cycle lifecycle and output/stop contract | skills/skill-developer-orchestrator/SKILL.md |
| Audit dimensions, method selection, severity and confidence | .../references/audit-matrix.md |
| Source identity, write readiness, branch strategy, patch application, PR workflow and recovery | .../references/github-change-protocol.md |
| Change impact, test classes, evidence format and release dispositions | .../references/regression-and-release-gates.md |
| Expected behavior and negative/positive acceptance cases | tests/acceptance-cases.json |
| Codex-specific manifest/integration metadata | .codex-plugin/plugin.json |
| License notice and legal attribution | LICENSE |

## 4. Synchronization status and execution boundary

- Source repository identity, pinned commit, plugin identity and current package release have been read back.
- Package-to-source comparison is complete for all seven shared UTF-8 paths in the current package inventory.
- Current parity is 0/7, not the narrower historical 0/4 result.
- The available GitHub connection can read SPDO but reports no push permission for that repository. No source branch, file update, commit or PR on SPDO is claimed by this checkpoint.
- No Plugin Creator mutation is claimed by this checkpoint.
- The next source-writing operation must merge the richer package content into the canonical repository source, preserve both unique files, update acceptance cases and manifest/version, run regression, and then rebuild/update the Plugin Creator package from the reconciled source.

## 5. Independent evaluation runtime

HSO now defines a separate deterministic, read-only evaluation engine. It consumes a frozen evidence dossier, checks that the evaluator identity is separate from builder and approver, calculates a domain-weighted score, emits a PASS, PASS_WITH_CAVEATS, HOLD or FAIL disposition, and writes a SHA-256 sidecar for the report.

Domains and weights:

| Domain | Weight |
|---|---:|
| Provenance | 15 |
| Source parity | 20 |
| Behavior | 20 |
| Security | 15 |
| Runtime | 20 |
| Evaluator independence | 10 |
| **Total** | **100** |

The evaluator runs in a separate GitHub Actions job with contents: read and actions: read; it cannot write the candidate repository. It does not auto-approve, merge, release or deploy. A hard provenance/security/identity-overlap failure returns FAIL. Missing, blocked, unrun or unverifiable required evidence returns HOLD.

A declared evaluator name and a separate read-only job are not sufficient to prove trust independence. The independence domain can return PASS only when the evaluation is executed by the workflow from protected main (push/workflow_dispatch, refs/heads/main, GITHUB_REF_PROTECTED=true, and workflow ref on main). An evaluation executed from a PR-controlled workflow is UNVERIFIABLE, even if the evaluator label differs from builder/approver. This PR is a bootstrap implementation and therefore must not certify its own independence. After trusted code is reviewed and merged, a later main-bound evaluation can establish that domain.

The current SDO dossier intentionally returns HOLD: provenance is recorded, but source parity is 0/7, behavior and security tests are not run against a named target host, and host runtime acceptance remains blocked. A successful CI run of the evaluator proves that the evaluation mechanism executed; it does not mean the SDO candidate passed. While this bootstrap PR executes from a PR-controlled ref, the evaluator-independence domain is UNVERIFIABLE and the expected disposition is HOLD.

## 6. Boundary from Evaluator Team plugin

This HSO evaluator runtime is a deterministic evidence assurance component. It is not a claim that the separate ChatGPT Evaluator Team plugin was invoked. The Evaluator Team catalog entry still has no canonical Git source and no named-host runtime receipt. That plugin must receive its own source/provenance reconciliation and host-activation evidence before it is marked runtime-verified.

## 7. Boundary from Remote MCP plugin invocation

The SKILL ANALYZER Remote MCP vertical slice is already implemented as a manual, approval-gated HSO workflow. It requires a real public HTTPS MCP endpoint, OIDC credentials, OpenAI API key, HMAC approval key and a protected Environment reviewer. The endpoint and credentials were not available in this evaluation checkpoint. Therefore no billable host call, MCP dispatch or invocation receipt is claimed. The workflow remains fail-closed until its external prerequisites and live acceptance checks pass.
