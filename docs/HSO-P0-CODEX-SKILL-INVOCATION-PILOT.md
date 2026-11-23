# HSO P0 — Codex CLI SKILL ANALYZER invocation pilot

**Status:** IMPLEMENTED_ON_PR_BRANCH / MOCK_HOST_TESTS_PASS / LIVE_PAID_INVOCATION_NOT_RUN / PR_OPEN / NOT_PRODUCTION_READY  
**Purpose:** Prove one controlled, auditable host invocation path for one canonical Agent Skill. This is not the universal plugin dispatcher.

## Pilot boundary

| Dimension | Fixed choice |
|---|---|
| Host | OpenAI Codex CLI, package @openai/codex@0.171.0 |
| Model | gpt-6.2-sol |
| Invocation mode | codex exec, non-interactive JSONL |
| Skill | SKILL ANALYZER master Agent Skill |
| Plugin ID | plugins_6ae2a122f5c881919193c9b0ba51961e |
| Canonical source | hsaidno-cpu/skill-analyzer |
| Source pin | c469af7977c9bf6dcb3f5ab7b085a6de20d87004 |
| Skill path | plugins/skill-analyzer/skills/skill-analyzer/SKILL.md |
| Sandbox | Read-only; ephemeral Codex thread; web search disabled |
| Approval | Manual workflow dispatch + owner guard + S4 HMAC approval receipt |
| Retry | One attempt only; paid invocation is non-idempotent |
| Output | JSON matching contracts/hso-p0-skill-analysis-output.schema.json |

The Plugin Creator package metadata says version 1.0.0 while its canonical Git repository is pinned at version 1.3.0. This pilot deliberately uses the parent repository's source authority and immutable 1.3.0 source pin; it does not silently synchronize or relabel the Plugin Creator package.

## Why Codex CLI, not Codex App Server

Codex App Server authentication is not the approved route for hosted commercial services. This workflow runs on a GitHub-hosted runner, so App Server account authentication is not used. The non-interactive codex exec path is designed for scripts and CI, supports structured JSONL, output schemas, ephemeral threads and read-only sandbox execution. See [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) and [CLI reference](https://learn.chatgpt.com/docs/cli/reference).

## Skill registration and evidence level

The adapter registers the pinned plugin's skill folders under the repository-scoped .agents/skills directory using temporary symlinks, supplies the explicit $skill-analyzer marker, hashes the canonical SKILL.md, verifies the package manifest and submodule commit, then invokes Codex CLI.

**Attestation limitation:** the Codex CLI JSONL stream provides thread/turn/item events but the current adapter does not receive a dedicated, cryptographically verifiable “this exact skill was loaded” event. The receipt therefore records skill_reference_supplied, source pin, skill digest, registration path, thread/turn IDs, completed agent message, structured-output validation and token usage. It explicitly marks skill_load_attestation=NO_DEDICATED_CLI_EVENT_EXPOSED. It does not use a model-generated self-assertion such as activation_confirmed=true as proof.

This is evidence of a host invocation with a pinned skill reference and a completed Codex turn, not an independent attestation from Codex internals that the skill text was applied without omission.

## Security and cost controls

- The live workflow exists only as a manual workflow_dispatch; it is not run by pull-request CI.
- Job condition requires the default main branch, actor hsaidno-cpu, explicit approve_paid_call=true, and run_attempt==1.
- The job uses protected GitHub Environment codex-p0-live. Configure its required reviewer(s) before enabling the workflow.
- Configure these environment secrets in GitHub; never paste them into chat or commit them:
  - CODEX_API_KEY: API credential used by Codex CLI. API model entitlement and billing are determined by the associated API project.
  - HSO_APPROVAL_HMAC_KEY: random high-entropy HMAC key, at least 32 characters.
- The approval script creates a case/action/target/authority/actor/run-bound five-minute HMAC receipt with a random nonce.
- A workflow rerun is rejected. The Codex action is non-idempotent, has max_attempts=1, and a timeout after dispatch is marked OUTCOME_UNKNOWN; HSO will not automatically retry it.
- The CLI receives a minimal environment. HSO_APPROVAL_HMAC_KEY, GitHub tokens and unrelated key/token/secret variables are not passed to model-generated child commands.
- The run uses --ephemeral --sandbox read-only --ask-for-approval never, no user tools, no MCP servers and no web search.
- The task is synthetic and must not contain personal, confidential or production data.

The model gpt-6.2-sol is pinned for reproducibility, but an API project may not be entitled to that model. Preflight checks CLI version/flags and key presence only; it does not issue a paid request or prove model entitlement. The first approved live run is the acceptance test for API authentication, model availability and output generation.

## Files

- tools/codex_skill_host_adapter.py
- tools/issue_p0_skill_approval.py
- tools/prepare_p0_skill_workflow.py
- catalog/hso-runtime-capabilities.json
- catalog/hso-routing-policy.json
- governance/hso-execution-policy.json
- contracts/hso-p0-skill-analysis-output.schema.json
- examples/hso-p0-skill-invocation-request.json
- tests/test_codex_skill_host_adapter.py
- tests/test_p0_approval_workflow.py
- P0 runtime integration tests in tests/test_hso_super_orchestrator.py
- .github/workflows/hso-p0-codex-skill-invocation.yml

## Local zero-inference preflight

After initializing only the approved submodule and installing Codex CLI 0.171.0:

    export CODEX_API_KEY=...
    python tools/hso_super_orchestrator.py discover --output /tmp/hso-p0-capabilities.json

This checks CLI version, required flags, plugin manifest, submodule pin and API key presence. It does not call the model.

## Live acceptance procedure

1. Review and merge PR #13 through the repository's normal review process. The manual workflow is deliberately unavailable until present on the default branch.
2. In GitHub Settings > Environments, create codex-p0-live, add required reviewer protection, and add the two secrets above.
3. Open Actions > P0 Codex CLI SKILL ANALYZER invocation pilot.
4. Select main, set approve_paid_call=true, review the one-call/billing scope, then dispatch once.
5. Accept only a completed artifact where run status and package status are SUCCEEDED, source commit matches the pin, target SHA-256 read-back passes, output schema is valid and the audit chain verifies.
6. If the run becomes OUTCOME_UNKNOWN, inspect the evidence and billing state before any new manual dispatch. Do not use Re-run jobs.

A successful live acceptance does not enable other plugins, other Agent Skills, other host platforms, remote MCP, HTTP APIs or production writes. P1 gateway and P2–P5 controls remain separate roadmap gates.

## Current evidence

Adapter contract/security tests use a fake Codex binary. These tests prove invocation arguments, environment filtering, source pin enforcement, JSONL receipt parsing, schema validation, failure handling, non-overwrite and cleanup. They do not prove a real paid Codex API call. Until the protected manual workflow is run, live host invocation remains NOT_RUN.
