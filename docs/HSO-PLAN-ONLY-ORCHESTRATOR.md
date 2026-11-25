# HSO Plan-Only Workflow Orchestrator

**Status:** IMPLEMENTED_ON_PR_BRANCH / PLAN_ONLY / NOT_MERGED / NO_RUNTIME_DISPATCH  
**Contract:** \`contracts/hso-workflow-plan.schema.json\` v1.0.0  
**Planner:** \`tools/plan_hso_workflow.py\` v0.1.0

## Purpose

The planner turns an explicitly declared set of HSO work packages into a deterministic dependency order and a readiness report. It closes the gap between an architecture-level dependency DAG and a repeatable plan-validation tool.

The planner is deliberately narrow. It does not infer a primary owner from natural-language prompts, choose a specialist by keyword, call skills, invoke tools, contact hosts, authorize actions, persist workflow state, or dispatch work. The caller declares ownership, scope, capability state and approval evidence. The planner checks the declaration against the parent plugin catalog and the plan contract.

## Input and execution

The input is a JSON object conforming to \`contracts/hso-workflow-plan.schema.json\`. Each work package must declare exactly one \`primary_owner\`, zero or more distinct \`supporting_specialists\`, dependencies, a capability state, requested write scope, approval state, expected output and acceptance criteria.

Run from the repository root:

~~~bash
python tools/plan_hso_workflow.py examples/hso-workflow-plan.example.json
~~~

Write the result to a separate file:

~~~bash
python tools/plan_hso_workflow.py examples/hso-workflow-plan.example.json --output /tmp/hso-plan-result.json
~~~

The planner exits with code \`0\` when the declared plan is structurally valid and returns a JSON disposition. Invalid declarations (unknown owner, duplicate package, missing dependency, self-dependency, duplicate dependency or dependency cycle) exit with code \`2\` and a diagnostic on stderr.

## Readiness semantics

- \`READY_FOR_REVIEW\`: supplied capability is \`READY\`, authority meets the declared write-scope minimum, and no approval blocker remains. This is not permission to dispatch.
- \`READY_WITH_LIMITATIONS\`: supplied capability is \`READY_WITH_LIMITATIONS\` and no blocker remains. Limitations remain visible.
- \`BLOCKED\`: capability, approval, authority or upstream dependency is unresolved or denied.
- \`BLOCKED_DISPATCH_UNAVAILABLE\`: dispatch was requested, but this planner has no runtime dispatcher. No attempt is made to dispatch.

\`READY\` and \`READY_WITH_LIMITATIONS\` require a non-empty \`capability_evidence\` string. This is a caller-supplied assertion and locator; the planner does not independently probe or authenticate the underlying host/tool.

The declared action-authority scale follows the HSO control-plane contract. Read-only and preparation work require lower levels than branch writes, child-repository changes, external side effects and production release. Approval state and action authority are independent: approval does not compensate for insufficient authority, and authority does not replace a required approval.

## Determinism and safety

- A stable topological sort preserves input order where dependencies do not constrain order.
- Unknown owners and legacy redirect identities are rejected as primary/supporting owners.
- Dependency cycles and references to unknown work packages are rejected.
- Upstream blockers propagate to dependent work packages.
- The tool never modifies the catalog, source repositories, Notion, or external systems.
- The tool never creates a persistent queue, run record, lease, or execution state.

## Acceptance boundary

This is a local deterministic planning/validation utility. Passing its tests proves only that the declared input contract and planner behavior pass those tests. It does not prove natural-language routing, skill invocation, platform compatibility, C4 host activation, C5 runtime execution, installer behavior, service availability, or production readiness.
