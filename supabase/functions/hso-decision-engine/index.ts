import { createClient } from "npm:@supabase/supabase-js@2.57.0";
const POLICY = "strategic-priority-v1";
const ENGINE = "hso-decision-engine-v1";
import { PRIORITY_WEIGHTS as WEIGHTS, normalizeWorkKey, taskId, calculatePriorityScore, calculateWeightedProgress, hasScopeDecision } from "./policy.mjs";
const REQUIRED = ["notion-control-center","notion-roadmap","notion-execution-ledger","notion-evidence-registry","github-hso-parent"];

function reply(data: unknown, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}
function equal(a: string, b: string) {
  if (a.length !== b.length) return false;
  let x = 0;
  for (let i = 0; i < a.length; i++) x |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return x === 0;
}
function fresh(value: string | null, maxSeconds: number) {
  if (!value) return false;
  const t = Date.parse(value);
  return Number.isFinite(t) && Date.now() - t <= maxSeconds * 1000 && Date.now() >= t - 60000;
}
function arr(value: unknown): string[] {
  if (Array.isArray(value)) return value.map((x) => String(x).trim()).filter(Boolean);
  if (typeof value !== "string" || !value.trim()) return [];
  try {
    const v = JSON.parse(value);
    if (Array.isArray(v)) return v.map((x) => String(x).trim()).filter(Boolean);
  } catch { /* use delimiter form */ }
  return value.split(/[\n,;]+/).map((x) => x.trim()).filter(Boolean);
}
async function fetchAllRows(db: any, table: string, columns = "*", configure?: (query: any) => any) {
  const output: any[] = [];
  const pageSize = 500;
  const maxPages = 10000;
  for (let page = 0; page < maxPages; page++) {
    let query: any = db.from(table).select(columns);
    if (configure) query = configure(query);
    const { data, error } = await query.range(page * pageSize, (page + 1) * pageSize - 1);
    if (error) return { data: output, error };
    const rows = data ?? [];
    output.push(...rows);
    if (rows.length < pageSize) return { data: output, error: null };
  }
  return { data: output, error: new Error(`Pagination limit exceeded while reading ${table}; refusing truncated decision input`) };
}
async function digest(value: unknown) {
  const bytes = new TextEncoder().encode(JSON.stringify(value));
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(hash)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function verified(item: any, evidence: any[]) {
  if (!["Verified", "Accepted"].includes(item.execution_state) || item.gate_state !== "PASS") return false;
  if (!item.source_verified_at || !fresh(item.source_verified_at, 604800)) return false;
  return evidence.some((ev) =>
    ev.source_key === "notion-evidence-registry" &&
    ev.related_work_item === item.external_id &&
    ["PASS","VERIFIED","ACCEPTED"].includes(String(ev.evidence_state).toUpperCase()) &&
    ev.freshness === "FRESH" &&
    ((ev.verified_at && fresh(ev.verified_at, 604800)) ||
      (["Acceptance Test","Human Review","Release Verification"].includes(ev.evidence_type) && fresh(ev.observed_at, 604800))) &&
    (!item.ci_commit_sha || ev.commit_sha === item.ci_commit_sha) &&
    (!item.head_commit_sha || ev.commit_sha === item.head_commit_sha)
  );
}
function severity(reason: string, risk: string | null) {
  if (risk === "CRITICAL" || /CI_FAILED|SOURCE_CONFLICT|SECURITY_DISPOSITION_FAILED/.test(reason)) return "CRITICAL";
  if (risk === "HIGH" || /APPROVAL|DEPENDENCY|BRANCH|HEAD_SHA|CI_NOT|SOURCE_FRESHNESS/.test(reason)) return "HIGH";
  if (/WEIGHT|PRIORITY|GATE|EVIDENCE/.test(reason)) return "MEDIUM";
  return "LOW";
}
function compilePrompt(item: any, ctx: any) {
  const steps = [
    "Re-read the canonical sources and confirm their versions still match this decision snapshot.",
    "Re-check every prerequisite, approval and security disposition immediately before execution.",
    "Inspect the exact target branch and HEAD commit. Do not silently switch targets.",
    "Execute only the authorized scope and follow dependency order.",
    "Run the required tests and validate against the actual target system.",
    "Record changed files, commit, PR, exact-head CI, test results, acceptance evidence and limitations.",
    "Update the execution ledger factually. Completed does not mean Verified until acceptance evidence exists."
  ];
  const payload = {
    prompt_version: "hso-ready-prompt-v1",
    task_id: taskId(item),
    context: {
      project: "Hypersystem Orchestrator",
      decision_run_id: ctx.runId,
      snapshot_ids: ctx.snapshotIds,
      generated_at: new Date().toISOString(),
      status: item.execution_state,
      milestone: item.milestone_key,
      source_url: item.source_url,
      source_updated_at: item.source_updated_at
    },
    objective: item.next_action || item.title,
    evidence: ctx.evidence,
    scope: {
      change_surface: item.change_surface,
      execution_target: item.execution_target,
      acceptance_criteria: item.acceptance_criteria,
      excluded: ["Unapproved policy changes","Unrelated repositories or Notion sources","Unapproved merge, release or production deployment"]
    },
    dependencies: ctx.dependencies,
    execution_steps: steps,
    authorization: {
      required: item.requires_human_approval === true,
      approval_state: item.approval_state,
      security_disposition: item.security_disposition,
      accountable_role: item.accountable_role,
      target_branch: ctx.branch,
      head_commit_sha: ctx.headSha,
      reviewed_commit_sha: item.reviewed_commit_sha
    },
    acceptance_criteria: item.acceptance_criteria ? [item.acceptance_criteria] : [],
    validation: {
      required_ci_commit_sha: ctx.headSha,
      required_ci_run_url: ctx.ciUrl,
      require_actual_target_validation: true
    },
    stop_conditions: [
      "Source authority conflict or stale source.",
      "Missing or unresolved dependency.",
      "Missing, rejected or wrong-commit approval.",
      "Security disposition is pending, HOLD or FAIL when required.",
      "Target branch or HEAD changes after compilation.",
      "Required CI is not PASS on the exact target SHA.",
      "Acceptance cannot be demonstrated with target-system evidence."
    ],
    reporting: {
      required_fields: ["task_id","decision_run_id","source_versions","branch","commit_sha","pull_request","changed_files","ci_run","test_results","acceptance_evidence","known_limitations","root_causes","recovery_actions","next_recommendation"],
      execution_and_verification_must_be_separate: true
    }
  };
  const text = [
    "# HSO READY-TO-EXECUTE PROMPT",
    "Perform " + payload.task_id + " — " + item.title + ".",
    "",
    "## Context\n" + JSON.stringify(payload.context, null, 2),
    "## Objective\n" + String(payload.objective),
    "## Evidence\n" + JSON.stringify(payload.evidence, null, 2),
    "## Scope\n" + JSON.stringify(payload.scope, null, 2),
    "## Dependencies\n" + JSON.stringify(payload.dependencies, null, 2),
    "## Execution steps\n" + steps.map((x, i) => (i + 1) + ". " + x).join("\n"),
    "## Authorization\n" + JSON.stringify(payload.authorization, null, 2),
    "## Acceptance criteria\n" + JSON.stringify(payload.acceptance_criteria, null, 2),
    "## Validation\n" + JSON.stringify(payload.validation, null, 2),
    "## Stop conditions\n" + payload.stop_conditions.map((x) => "- " + x).join("\n"),
    "## Reporting\n" + JSON.stringify(payload.reporting, null, 2)
  ].join("\n\n");
  return { payload, text };
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return reply({ error: "method_not_allowed" }, 405);
  const token = Deno.env.get("HSO_SYNC_TOKEN") || "";
  const supplied = req.headers.get("x-hso-sync-token") || "";
  if (!token || !equal(token, supplied)) return reply({ error: "unauthorized" }, 401);
  const url = Deno.env.get("SUPABASE_URL");
  const key = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !key) return reply({ error: "backend_not_configured" }, 503);
  const db = createClient(url, key, { auth: { persistSession: false } });
  let requestBody: any = {};
  try { requestBody = await req.json(); } catch { /* body is required below */ }
  const syncRunId = typeof requestBody.sync_run_id === "string" ? requestBody.sync_run_id : null;
  if (!syncRunId) return reply({ error: "sync_run_id_required", message: "Decision runs must bind to one explicit completed sync_run_id." }, 400);

  const [sq, iq, eq, snq, cq, syncQ] = await Promise.all([
    fetchAllRows(db, "hso_sources", "*", (q: any) => q.eq("enabled", true)),
    fetchAllRows(db, "hso_work_items"),
    fetchAllRows(db, "hso_evidence_records"),
    fetchAllRows(db, "hso_source_snapshots", "*", (q: any) => q.eq("sync_run_id", syncRunId).order("observed_at", { ascending: false })),
    fetchAllRows(db, "hso_completion_criteria", "*", (q: any) => q.eq("project_key", "hso").eq("required", true)),
    db.from("hso_sync_runs").select("*").eq("id", syncRunId).maybeSingle()
  ]);
  const errs = [sq.error, iq.error, eq.error, snq.error, cq.error, syncQ.error].filter(Boolean);
  if (errs.length) return reply({ error: "decision_inputs_unavailable", details: errs.map((x: any) => String(x.message ?? x)) }, 500);
  if (!syncQ.data) return reply({ error: "sync_run_not_found", sync_run_id: syncRunId }, 404);

  const sources = sq.data || [];
  const allRoadmapRows = iq.data || [];
  const roadmapRows = allRoadmapRows.filter((x: any) => x.source_key === "notion-roadmap");
  const items = roadmapRows.filter((x: any) => x.record_type === "Work Item");
  const milestoneRows = roadmapRows.filter((x: any) => ["Milestone","Phase"].includes(String(x.record_type)));
  const evidence = eq.data || [], snapshots = snq.data || [], criteria = cq.data || [];
  const syncRun = syncQ.data;
  const milestoneById = new Map(milestoneRows.filter((x: any) => x.item_key !== null && x.item_key !== undefined).map((x: any) => [String(x.item_key), x]));
  const sourceMap = new Map(sources.map((s: any) => [s.source_key, s]));
  const sourceHealth: Record<string, any> = {};
  const staleSources: any[] = [];
  const snapshotBySource = new Map<string, any>();
  const duplicateSnapshotSources: string[] = [];
  const incompleteSnapshotSources: string[] = [];
  for (const sourceKey of REQUIRED) {
    const src: any = sourceMap.get(sourceKey);
    const matches = snapshots.filter((snap: any) => snap.source_key === sourceKey);
    if (matches.length === 1) snapshotBySource.set(sourceKey, matches[0]);
    else if (matches.length > 1) duplicateSnapshotSources.push(sourceKey);
    const snap: any = matches.length === 1 ? matches[0] : null;
    const maxAge = Number(src?.freshness_seconds || 1800);
    const age = src?.last_success_at ? Math.max(0, Math.round((Date.now() - Date.parse(src.last_success_at)) / 1000)) : null;
    const completeSnapshot = Boolean(snap && snap.is_complete === true && snap.pagination_complete === true &&
      snap.completeness_state === "COMPLETE" && snap.freshness === "FRESH" && snap.content_hash &&
      snap.scope_hash && fresh(snap.observed_at, maxAge));
    if (!completeSnapshot) incompleteSnapshotSources.push(sourceKey);
    const isFresh = Boolean(src && src.status === "connected" && age !== null && age <= maxAge &&
      src.last_complete_at && fresh(src.last_complete_at, maxAge) && completeSnapshot);
    sourceHealth[sourceKey] = {
      status: src?.status || "missing", last_success_at: src?.last_success_at || null,
      last_complete_at: src?.last_complete_at || null, age_seconds: age,
      freshness_seconds: src?.freshness_seconds || null, fresh: isFresh,
      snapshot_count: matches.length, complete_snapshot: completeSnapshot,
      snapshot_id: snap?.id || null, last_error: src?.last_error || null
    };
    if (!isFresh) staleSources.push({
      source_key: sourceKey, reason: matches.length > 1 ? "DUPLICATE_SNAPSHOT" : !completeSnapshot ? "SNAPSHOT_INCOMPLETE_OR_MISSING" : "SOURCE_STALE",
      ...sourceHealth[sourceKey]
    });
  }
  const syncSucceeded = syncRun.status === "succeeded";
  if (!syncSucceeded) staleSources.push({ source_key: "sync-run", reason: "SYNC_RUN_NOT_SUCCEEDED", status: syncRun.status });
  const roadmapSnapshot: any = snapshotBySource.get("notion-roadmap");
  const expectedRoadmapIds = Array.isArray(roadmapSnapshot?.snapshot?.page_ids)
    ? roadmapSnapshot.snapshot.page_ids.map((x: any) => String(x)).sort() : [];
  const actualRoadmapIds = roadmapRows.map((x: any) => String(x.external_id)).sort();
  const expectedUnique = new Set(expectedRoadmapIds);
  const roadmapMembershipMismatch = !roadmapSnapshot ||
    expectedRoadmapIds.length !== expectedUnique.size ||
    Number(roadmapSnapshot?.source_total_count) !== expectedRoadmapIds.length ||
    JSON.stringify(expectedRoadmapIds) !== JSON.stringify(actualRoadmapIds) ||
    roadmapSnapshot.scope_hash !== await digest(expectedRoadmapIds);
  const scopeDrift = roadmapMembershipMismatch;
  if (scopeDrift) staleSources.push({
    source_key: "notion-roadmap", reason: "ROADMAP_MEMBERSHIP_MISMATCH",
    expected_count: expectedRoadmapIds.length, actual_count: actualRoadmapIds.length,
    expected_scope_hash: roadmapSnapshot?.scope_hash || null
  });
  const decisionInputsComplete = syncSucceeded && staleSources.length === 0 && !scopeDrift;
  const snapshotCoverage = {
    sync_run_id: syncRunId, sync_run_status: syncRun.status,
    required_sources: REQUIRED,
    observed_sources: [...new Set(snapshots.map((snap: any) => snap.source_key))],
    missing_sources: REQUIRED.filter((sourceKey) => !snapshotBySource.has(sourceKey)),
    duplicate_sources: duplicateSnapshotSources,
    incomplete_sources: incompleteSnapshotSources,
    roadmap_expected_record_count: expectedRoadmapIds.length,
    roadmap_actual_record_count: actualRoadmapIds.length,
    roadmap_membership_match: !scopeDrift,
    decision_inputs_complete: decisionInputsComplete,
    stale_reasons: staleSources,
  };

  const evidenceByTask = new Map<string, any[]>();
  for (const ev of evidence) if (ev.related_work_item) evidenceByTask.set(ev.related_work_item, [...(evidenceByTask.get(ev.related_work_item) || []), ev]);
  const itemByKey = new Map<string, any>();
  const duplicateKeys = new Set<string>();
  for (const item of items) if (item.item_key !== null && item.item_key !== undefined && String(item.item_key).trim()) {
    const k = normalizeWorkKey(item.item_key);
    if (itemByKey.has(k)) duplicateKeys.add(k); else itemByKey.set(k, item);
  }
  const verifiedById = new Map(items.map((x: any) => [x.id, verified(x, evidenceByTask.get(x.external_id) || [])]));
  const blocked: any[] = [], pending: any[] = [], eligible: any[] = [];

  for (const item of items) {
    const reasons: string[] = [];
    const status = String(item.execution_state || "UNKNOWN");
    const code = item.change_surface === "CODE";
    const normalizedKey = normalizeWorkKey(item.item_key);
    if (!["Ready","Not started","In progress"].includes(status)) reasons.push("STATUS_NOT_ACTIONABLE");
    if (item.gate_state !== "PASS") reasons.push("GATE_NOT_PASS");
    if (!decisionInputsComplete) reasons.push("SOURCE_COMPLETENESS_GATE");
    if (staleSources.length) reasons.push("SOURCE_FRESHNESS_GATE");
    if (!normalizedKey) reasons.push("STABLE_TASK_ID_MISSING");
    if (duplicateKeys.has(normalizedKey)) reasons.push("DUPLICATE_TASK_ID");
    if (!hasScopeDecision(item)) reasons.push("SCOPE_DECISION_INCOMPLETE");
    else if (item.scope_inclusion_state === "OUT_OF_SCOPE") reasons.push("WORK_ITEM_OUT_OF_SCOPE");
    const proseDeps = arr(item.dependencies);
    const depIds = arr(item.dependency_work_item_ids);
    if (proseDeps.length && !depIds.length) reasons.push("DEPENDENCY_IDS_UNMAPPED");
    const resolvedDeps: any[] = [];
    for (const depId of depIds) {
      const dependencyKey = normalizeWorkKey(depId);
      if (duplicateKeys.has(dependencyKey)) reasons.push("DEPENDENCY_ID_AMBIGUOUS:" + depId);
      const dep = duplicateKeys.has(dependencyKey) ? null : itemByKey.get(dependencyKey);
      if (!dep) reasons.push("DEPENDENCY_NOT_FOUND_OR_AMBIGUOUS:" + depId);
      else {
        resolvedDeps.push({ task_id: taskId(dep), title: dep.title, status: dep.execution_state });
        if (!verifiedById.get(dep.id)) reasons.push("DEPENDENCY_NOT_VERIFIED:" + depId);
      }
    }

    const prEvidence = evidence.find((ev: any) => ev.evidence_type === "Pull Request" && item.pr_url && ev.pr_url === item.pr_url);
    const headSha = item.head_commit_sha || prEvidence?.commit_sha || null;
    const branch = item.target_branch || prEvidence?.branch_ref || null;
    if (!item.change_surface) reasons.push("CHANGE_SURFACE_UNSET");
    if (!item.execution_target) reasons.push("EXECUTION_TARGET_UNSET");
    let ci: any = null;
    if (code) {
      if (!branch || !headSha) reasons.push("BRANCH_OR_HEAD_SHA_UNIDENTIFIED");
      ci = evidence.find((ev: any) => ev.evidence_type === "CI Run" && ev.commit_sha === headSha && ev.evidence_state === "PASS" && ev.freshness === "FRESH" && (!item.ci_run_url || ev.ci_run_url === item.ci_run_url));
      if (!ci) reasons.push("CI_NOT_PASS_ON_EXACT_HEAD");
      if (item.ci_commit_sha && item.ci_commit_sha !== headSha) reasons.push("CI_COMMIT_SHA_MISMATCH");
    }
    if (item.requires_human_approval === true) {
      if (item.approval_state !== "APPROVED") reasons.push("APPROVAL_NOT_APPROVED");
      if (code && (!item.reviewed_commit_sha || item.reviewed_commit_sha !== headSha)) reasons.push("REVIEW_NOT_BOUND_TO_HEAD_SHA");
    } else if (item.requires_human_approval === null || item.requires_human_approval === undefined) {
      if (["HIGH","CRITICAL"].includes(item.execution_risk) || ["CODE","INTEGRATION","OPERATIONS"].includes(item.change_surface)) reasons.push("APPROVAL_POLICY_UNSET");
    } else if (item.requires_human_approval === false && item.approval_state !== "NOT_REQUIRED") {
      reasons.push("APPROVAL_STATE_NOT_EXPLICIT");
    }
    if (["HIGH","CRITICAL"].includes(item.execution_risk) && !["PASS","NOT_REQUIRED"].includes(item.security_disposition)) reasons.push("SECURITY_DISPOSITION_NOT_PASS");
    if (["HOLD","FAIL"].includes(item.security_disposition)) reasons.push("SECURITY_DISPOSITION_BLOCKS");
    const priority = calculatePriorityScore(item);
    if (priority === null) reasons.push("PRIORITY_INPUTS_INCOMPLETE");

    if (item.approval_state === "PENDING" || (item.requires_human_approval === true && item.approval_state !== "APPROVED")) {
      pending.push({ task_id: taskId(item), title: item.title, approval_state: item.approval_state || "UNSET", source_url: item.source_url });
    }
    if (reasons.length) {
      blocked.push({ task_id: taskId(item), title: item.title, status, reasons: [...new Set(reasons)], source_url: item.source_url, milestone_key: item.milestone_key });
    } else {
      eligible.push({
        item,
        score: priority!,
        breakdown: Object.fromEntries(Object.entries(WEIGHTS).map(([k, w]) => [k, { value: Number(item[k]), weight: w, contribution: Number(item[k]) * w }])),
        context: {
          branch, headSha, ciUrl: ci?.ci_run_url || item.ci_run_url,
          dependencies: resolvedDeps,
          evidence: [
            { type: "Roadmap", url: item.source_url, updated_at: item.source_updated_at },
            ...(item.pr_url ? [{ type: "Pull Request", url: item.pr_url, branch, head_sha: headSha }] : []),
            ...(ci ? [{ type: "CI Run", url: ci.ci_run_url, commit_sha: ci.commit_sha, state: ci.evidence_state }] : []),
            ...(evidenceByTask.get(item.external_id) ?? []).map((ev: any) => ({
              type: ev.evidence_type, title: ev.title,
              url: ev.source_url || ev.source_locator || ev.artifact_url,
              commit_sha: ev.commit_sha, state: ev.evidence_state,
              freshness: ev.freshness, verifier_role: ev.verifier_role,
              verified_at: ev.verified_at, known_limitation: ev.known_limitation
            }))
          ]
        }
      });
    }
  }
  eligible.sort((a, b) => b.score - a.score || String(a.item.item_key).localeCompare(String(b.item.item_key)));

  const now = new Date().toISOString();
  const snapshotIds = [...new Set(snapshots.map((snap: any) => snap.id))];
  const groups = new Map<string, any[]>();
  const groupLabels = new Map<string, { title: string; group_type: string }>();
  groups.set("__GLOBAL__", items);
  for (const item of items) {
    const parentId = item.parent_milestone_id ? String(item.parent_milestone_id) : null;
    const parent = parentId ? milestoneById.get(parentId) : null;
    const key = parent ? "MILESTONE:" + parentId : "STAGE:" + (item.ecosystem_stage || "UNASSIGNED");
    groups.set(key, [...(groups.get(key) || []), item]);
    groupLabels.set(key, parent
      ? {
          title: parent.title,
          group_type: "MILESTONE",
          expected_progress_pct: parent.expected_progress_pct ?? null,
          baseline_start_date: parent.baseline_start_date ?? null,
          target_date: parent.target_date ?? null
        }
      : {
          title: item.ecosystem_stage || "Unassigned stage",
          group_type: "ECOSYSTEM_STAGE",
          expected_progress_pct: null,
          baseline_start_date: null,
          target_date: null
        });
  }
  const progressRows: any[] = [];
  for (const [key, group] of groups) {
    const verifiedIds = new Set(group.filter((x) => verifiedById.get(x.id)).map((x) => String(x.id)));
    const progress = calculateWeightedProgress(group, verifiedIds, {
      sourceComplete: decisionInputsComplete, scopeDrift
    });
    const scopeRows = group.map((item: any) => ({
      external_id: item.external_id, item_key: item.item_key,
      scope_inclusion_state: item.scope_inclusion_state,
      scope_decision_by: item.scope_decision_by, scope_decision_at: item.scope_decision_at,
      scope_decision_rationale: item.scope_decision_rationale,
      scope_weight: item.scope_weight, weight_rationale: item.weight_rationale,
      scope_weight_approval: item.scope_weight_approval,
      scope_weight_approved_by: item.scope_weight_approved_by,
      scope_weight_approved_at: item.scope_weight_approved_at,
    })).sort((a: any, b: any) => String(a.external_id).localeCompare(String(b.external_id)));
    const progressScopeHash = await digest(scopeRows);
    progressRows.push({
      project_key: "hso", source_sync_run_id: syncRunId, scope_hash: progressScopeHash,
      milestone_key: key === "__GLOBAL__" ? null : key,
      milestone_title: key === "__GLOBAL__" ? "All work items" : (groupLabels.get(key)?.title ?? key),
      group_type: key === "__GLOBAL__" ? "GLOBAL" : (groupLabels.get(key)?.group_type ?? "ECOSYSTEM_STAGE"),
      expected_progress_pct: key === "__GLOBAL__" ? null : (groupLabels.get(key)?.expected_progress_pct ?? null),
      baseline_start_date: key === "__GLOBAL__" ? null : (groupLabels.get(key)?.baseline_start_date ?? null),
      target_date: key === "__GLOBAL__" ? null : (groupLabels.get(key)?.target_date ?? null),
      ...progress,
      is_publishable: progress.is_publishable && decisionInputsComplete && !scopeDrift,
      measurement_reasons: progress.measurement_reasons,
      methodology_version: "weighted-evidence-v2",
      computed_at: now
    });
  }
  const prog = await db.from("hso_progress_snapshots").insert(progressRows);
  if (prog.error) return reply({ error: "progress_write_failed", detail: prog.error.message }, 500);

  const evidenceById = new Map(evidence.map((ev: any) => [String(ev.id), ev]));
  const criterionIsVerified = (criterion: any) => {
    const ev: any = criterion.evidence_record_id ? evidenceById.get(String(criterion.evidence_record_id)) : null;
    return ["VERIFIED","ACCEPTED"].includes(String(criterion.state).toUpperCase()) &&
      Boolean(criterion.last_evaluated_at && fresh(criterion.last_evaluated_at, 604800)) &&
      Boolean(ev && ["PASS","VERIFIED","ACCEPTED"].includes(String(ev.evidence_state).toUpperCase()) &&
        ev.freshness === "FRESH" && ev.verified_at && fresh(ev.verified_at, 604800));
  };
  const primary = decisionInputsComplete ? (eligible[0] || null) : null;
  const verifiedCriteria = criteria.filter(criterionIsVerified);
  const completionGap = {
    required_criteria_count: criteria.length,
    verified_criteria_count: verifiedCriteria.length,
    incomplete_criteria: criteria.filter((c: any) => !criterionIsVerified(c)).map((c: any) => ({
      key: c.criterion_key, title: c.title, state: c.state,
      evidence_state: c.evidence_record_id ? (evidenceById.get(String(c.evidence_record_id))?.evidence_state ?? "EVIDENCE_NOT_FOUND") : "EVIDENCE_NOT_LINKED",
    })),
    baseline_state: criteria.length ? "CONFIGURED" : "NOT_CONFIGURED"
  };
  const state = primary ? "PRIMARY_SELECTED" : !decisionInputsComplete ? "SOURCE_STALE" : "NO_ELIGIBLE_ACTION";
  const run = await db.from("hso_decision_runs").insert({
    engine_version: ENGINE, policy_version: POLICY, decision_state: state,
    source_sync_run_id: syncRunId, snapshot_coverage: snapshotCoverage,
    decision_inputs_complete: decisionInputsComplete,
    primary_work_item_id: primary?.item.id || null, source_health: { ...sourceHealth, snapshot_coverage: snapshotCoverage },
    primary_action: primary ? {
      task_id: taskId(primary.item), title: primary.item.title, score: Math.round(primary.score * 100) / 100,
      score_breakdown: primary.breakdown, reasons: ["All hard eligibility gates passed","Highest weighted priority score among eligible work items"],
      prerequisites: primary.context.dependencies, expected_outcome: primary.item.acceptance_criteria, source_url: primary.item.source_url
    } : null,
    supporting_actions: eligible.slice(1,4).map((x) => ({ task_id: taskId(x.item), title: x.item.title, score: x.score })),
    blocked_actions: blocked, pending_decisions: pending,
    ranking_snapshot: eligible.map((x,i) => ({ rank:i+1, task_id:taskId(x.item), score:x.score, breakdown:x.breakdown })),
    completion_gap: completionGap, computed_at: now
  }).select("id").single();
  if (run.error || !run.data) return reply({ error: "decision_run_failed", detail: run.error?.message }, 500);

  const issueGroups = new Map<string, any>();
  for (const stale of staleSources) {
    const key = "SOURCE_FRESHNESS:" + stale.source_key;
    issueGroups.set(key, {
      source_key: stale.source_key, external_id: "root:" + key, root_cause_key: key,
      issue_type: "SOURCE_FRESHNESS", severity: "HIGH", location: stale.source_key,
      root_cause: "Source is disconnected or beyond freshness SLA.",
      root_cause_state: "UNCONFIRMED",
      impact: "Strategic recommendations are suppressed until this source is reconciled.",
      affected_work_items: items.map((x) => taskId(x)), affected_milestones: [],
      verification_state: "OPEN", occurrence_count: items.length, last_seen_at: now
    });
  }
  for (const entry of blocked) {
    const item = items.find((x) => taskId(x) === entry.task_id);
    for (const reason of entry.reasons) {
      if (reason === "SOURCE_FRESHNESS_GATE") continue;
      const key = reason;
      const issue = issueGroups.get(key) ?? {
        source_key: "notion-roadmap", external_id: "root:" + key, root_cause_key: key,
        issue_type: reason, severity: severity(reason, item?.execution_risk),
        location: null, root_cause: reason.toLowerCase().replaceAll("_"," "),
        root_cause_state: "UNCONFIRMED",
        impact: "A shared eligibility condition is blocking one or more work items.",
        affected_work_items: [], affected_milestones: [],
        resolution: "Resolve the underlying condition, then recompute the decision engine.",
        verification_state: "OPEN", occurrence_count: 0, last_seen_at: now
      };
      issue.affected_work_items = [...new Set([...issue.affected_work_items, entry.task_id])];
      issue.affected_milestones = [...new Set([...issue.affected_milestones, entry.milestone_key].filter(Boolean))];
      issue.occurrence_count = issue.affected_work_items.length;
      if (!issue.location) issue.location = item?.pr_url || item?.source_url || null;
      if (severity(reason, item?.execution_risk) === "CRITICAL") issue.severity = "CRITICAL";
      else if (severity(reason, item?.execution_risk) === "HIGH" && issue.severity !== "CRITICAL") issue.severity = "HIGH";
      issueGroups.set(key, issue);
    }
  }
  const issues = [...issueGroups.values()];
  if (issues.length) {
    const written = await db.from("hso_issue_records").upsert(issues, { onConflict: "source_key,external_id" });
    if (written.error) return reply({ error: "issue_write_failed", detail: written.error.message }, 500);
  }

  let promptId: string | null = null;
  if (primary) {
    const p = compilePrompt(primary.item, {
      runId: run.data.id, snapshotIds,
      evidence: primary.context.evidence, dependencies: primary.context.dependencies,
      branch: primary.context.branch, headSha: primary.context.headSha, ciUrl: primary.context.ciUrl
    });
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(p.text));
    const hash = [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2,"0")).join("");
    const artifact = await db.from("hso_prompt_artifacts").insert({
      work_item_id: primary.item.id, snapshot_id: roadmapSnapshot?.id || null,
      prompt_version: "hso-ready-prompt-v1", prompt_text: p.text,
      prompt_payload: p.payload, context_hash: hash, task_key: taskId(primary.item),
      prompt_state: "generated", created_from_decision_run: run.data.id
    }).select("id").single();
    if (artifact.error) return reply({ error: "prompt_compile_failed", detail: artifact.error.message }, 500);
    promptId = artifact.data.id;
    await db.from("hso_decision_runs").update({ prompt_artifact_id: promptId }).eq("id", run.data.id);
  }

  const dec = await db.from("hso_decisions").insert(primary ? [{
    work_item_id: primary.item.id, decision_type: "PRIMARY_NEXT_ACTION", eligibility_state: "ELIGIBLE",
    priority_score: primary.score, policy_version: POLICY,
    rationale: { decision_run_id: run.data.id, score_breakdown: primary.breakdown, reasons: ["hard_gates_passed","highest_ranked"] }
  }] : [{
    decision_type: "NO_ELIGIBLE_ACTION", eligibility_state: !decisionInputsComplete ? "SOURCE_STALE" : "NONE_ELIGIBLE",
    policy_version: POLICY, rationale: { decision_run_id: run.data.id, stale_sources: staleSources, blocked_count: blocked.length, decision_inputs_complete: decisionInputsComplete }
  }]);
  if (dec.error) return reply({ error: "decision_projection_failed", detail: dec.error.message }, 500);

  return reply({
    decision_run_id: run.data.id, sync_run_id: syncRunId, snapshot_coverage: snapshotCoverage, decision_state: state,
    primary_action: primary ? { task_id: taskId(primary.item), title: primary.item.title, priority_score: primary.score } : null,
    eligible_count: eligible.length, blocked_count: blocked.length,
    pending_approval_count: pending.length, progress: progressRows[0],
    progress_milestones: progressRows.slice(1), completion_gap: completionGap, prompt_artifact_id: promptId
  });
});
