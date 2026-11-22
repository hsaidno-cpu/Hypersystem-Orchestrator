---
name: tool-action-security
description: Use when assessing AI-agent tools, APIs, browser actions, code execution, file operations, transactions, credentials, permissions, or externally visible side effects.
---
# Tool and Action Security Auditor

## Objective
Ensure model-generated plans cannot turn untrusted content or ambiguous intent into unauthorized consequential actions.

## Security invariants
1. Least privilege: tools expose only necessary operations and data.
2. Server-side authorization: the execution service validates identity, scope, object ownership and policy independently of model instructions.
3. Intent binding: action must match the user's authorized task, not instructions embedded in retrieved content.
4. Parameter validation: validate types, ranges, destinations, identifiers and state transitions outside the model.
5. Side-effect control: destructive, financial, privacy-sensitive or externally visible actions require appropriate confirmation and idempotency/rollback controls.
6. Secret minimization: credentials are not placed in prompts or returned in tool output unless strictly necessary.
7. Auditability: record actor, authorization decision, arguments, result and side effect while minimizing sensitive logs.

## Procedure
- Inventory each tool, endpoint, permission, data scope, credential, side effect and failure mode.
- Map model planning to tool execution and locate the actual authorization enforcement point.
- Review confused-deputy risks, overbroad tokens, indirect prompt injection, destination substitution, parameter smuggling, replay, duplicate execution, SSRF-like routing exposure, unsafe file handling and excessive agency at a conceptual defensive level.
- Review human approval, transaction limits, allowlists, rate limits, idempotency, rollback, timeouts and monitoring.
- Verify whether a tool result is authenticated and whether the model can distinguish success, failure and unverified claims.
- Design inert tests with mock accounts, fake tokens and local fixtures.

## Output
Tool inventory; permission matrix; action-flow diagram; authorization gaps; high-risk side effects; controls by enforcement layer; safe tests; incident triggers.

## Boundary
Do not provide instructions to exploit real endpoints, steal credentials, evade monitoring or execute unauthorized actions. Do not test external systems without explicit authorization and an appropriate supported environment. Prompt-only restrictions are not a substitute for backend authorization.
