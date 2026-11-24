import { createClient } from "npm:@supabase/supabase-js@2.57.0";
const POLICY = "strategic-priority-v1";
const ENGINE = "hso-decision-engine-v1";
const WEIGHTS = {
  dependency_unlock_value: 0.25,
  risk_reduction: 0.25,
  critical_path_impact: 0.20,
  urgency: 0.15,
  effort_efficiency: 0.10,
  evidence_confidence: 0.05,
};
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
function score(item: any): number | null {
  const keys = Object.keys(WEIGHTS);
  for (const key of keys) {
    const v = item[key];
    if (v === null || v === undefined || !Number.isFinite(Number(v)) || Number(v) < 0 || Number(v) > 100) return null;
  }
  return keys.reduce((sum, key) => sum + Number(item[key]) * WEIGHTS[key as keyof typeof WEIGHTS], 0);
}
function verified(item: any, evidence: any[]) {
  if (!["Verified", "Accepted"].includes(item.execution_state) || item.gate_state !== "PASS") return false;
  if (!item.source_verified_at || !fresh(item.source_verified_at, 604800)) return false;
  return evidence.some((ev) =>
    ev.source_key === "notion-evidence-registry" &&
    ev.related_work_item === item.external_id &&
    ["PASS","VERIFIED","ACCEPTED"].includes(String(ev.evidence_state).toUpperCase()) &&
    ev.freshness === "FRESH" &&
    (ev.verified_at || ["Acceptance Test","Human Review","Release Verification"].includes(ev.evidence_type)) &&
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
function normalizeWorkKey(value: unknown) {
  const raw = String(value ?? "").trim().toUpperCase().replace(/^HSO[-_]?/, "");
  if (!raw) return "";
  if (/^\\d+$/.test(raw)) return String(Number(raw));
  return raw;
}
function taskId(item: any) {
  const raw = normalizeWorkKey(item.item_key);
  if (!raw) return item.external_id;
  return "HSO-" + (/^\\d+$/.test(raw) ? raw.padStart(3, "0") : raw);
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
  try { requestBody = await req.json(); } catch { /* allow explicit re-evaluation without a body */ }
  const syncRunId = typeof requestBody.sync_run_id === "string" ? requestBody.sync_run_id : null;

  const [sq, iq, eq, snq, cq] = await Promise.all([
    db.from("hso_sources").select("*").eq("enabled", true),
    db.from("hso_work_items").select("*").limit(1500),
    db.from("hso_evidence_records").select("*").limit(2000),
    syncRunId
      ? db.from("hso_source_snapshots").select("id,source_key,observed_at,content_hash,sync_run_id").eq("sync_run_id", syncRunId).order("observed_at", { ascending: false })
      : db.from("hso_source_snapshots").select("id,source_key,observed_at,content_hash,sync_run_id").order("observed_at", { ascending: false }).limit(50),
    db.from("hso_completion_criteria").select("*").eq("project_key", "hso").eq("required", true)
  ]);
  const errs = [sq.error, iq.error, eq.error, snq.error, cq.error].filter(Boolean);
  if (errs.length) return reply({ error: "decision_inputs_unavailable", details: errs.map((x: any) => x.message) }, 500);

  const sources = sq.data || [];
  const allRoadmapRows = iq.data || [];
  const items = allRoadmapRows.filter((x: any) => x.record_type === "Work Item");
  const milestoneRows = allRoadmapRows.filter((x: any) => x.record_type === "Milestone");
  const evidence = eq.data || [], snapshots = snq.data || [], criteria = cq.data || [];
  const milestoneById = new Map(milestoneRows.filter((x: any) => x.item_key !== null && x.item_key !== undefined).map((x: any) => [String(x.item_key), x]));
  const sourceMap = new Map(sources.map((s: any) => [s.source_key, s]));
  const sourceHealth: Record<string, any> = {};
  const staleSources: any[] = [];
  for (const sourceKey of REQUIRED) {
    const src: any = sourceMap.get(sourceKey);
    const age = src?.last_success_at ? Math.max(0, Math.round((Date.now() - Date.parse(src.last_success_at)) / 1000)) : null;
    const isFresh = Boolean(src && src.status === "connected" && age !== null && age <= Number(src.freshness_seconds || 1800));
    sourceHealth[sourceKey] = { status: src?.status || "missing", last_success_at: src?.last_success_at || null, age_seconds: age, freshness_seconds: src?.freshness_seconds || null, fresh: isFresh, last_error: src?.last_error || null };
    if (!isFresh) staleSources.push({ source_key: sourceKey, ...sourceHealth[sourceKey] });
  }

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
    if (!["Ready","Not started","In progress"].includes(status)) reasons.push("STATUS_NOT_ACTIONABLE");
    if (item.gate_state !== "PASS") reasons.push("GATE_NOT_PASS");
    if (staleSources.length) reasons.push("SOURCE_FRESHNESS_GATE");
    if (duplicateKeys.has(normalizeWorkKey(item.item_key))) reasons.push("DUPLICATE_TASK_ID");
    const proseDeps = arr(item.dependencies);
    const depIds = arr(item.dependency_work_item_ids);
    if (proseDeps.length && !depIds.length) reasons.push("DEPENDENCY_IDS_UNMAPPED");
    const resolvedDeps: any[] = [];
    for (const depId of depIds) {
      const dep = itemByKey.get(normalizeWorkKey(depId));
      if (!dep) reasons.push("DEPENDENCY_NOT_FOUND:" + depId);
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
    const priority = score(item);
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
    const weighted = group.filter((x) => Number(x.scope_weight) > 0);
    const totalWeight = weighted.reduce((s, x) => s + Number(x.scope_weight), 0);
    const completedWeight = weighted.filter((x) => verifiedById.get(x.id)).reduce((s, x) => s + Number(x.scope_weight), 0);
    const pct = totalWeight ? Math.round(completedWeight / totalWeight * 10000) / 100 : null;
    const coverage = group.length ? Math.round(weighted.length / group.length * 10000) / 100 : null;
    progressRows.push({
      project_key: "hso",
      milestone_key: key === "__GLOBAL__" ? null : key,
      milestone_title: key === "__GLOBAL__" ? "All work items" : (groupLabels.get(key)?.title ?? key),
      group_type: key === "__GLOBAL__" ? "GLOBAL" : (groupLabels.get(key)?.group_type ?? "ECOSYSTEM_STAGE"),
      expected_progress_pct: key === "__GLOBAL__" ? null : (groupLabels.get(key)?.expected_progress_pct ?? null),
      baseline_start_date: key === "__GLOBAL__" ? null : (groupLabels.get(key)?.baseline_start_date ?? null),
      target_date: key === "__GLOBAL__" ? null : (groupLabels.get(key)?.target_date ?? null),
      total_work_items: group.length, weighted_work_items: weighted.length, unweighted_work_items: group.length - weighted.length,
      scope_weight_total: totalWeight, verified_weight: completedWeight, weighted_progress_pct: pct,
      weight_coverage_pct: coverage, verified_count: group.filter((x) => verifiedById.get(x.id)).length,
      active_count: group.filter((x) => x.execution_state === "In progress").length,
      blocked_count: group.filter((x) => x.execution_state === "Blocked" || ["BLOCKED","HOLD","FAIL"].includes(x.gate_state)).length,
      failed_count: group.filter((x) => x.gate_state === "FAIL").length,
      pending_approval_count: group.filter((x) => x.approval_state === "PENDING").length,
      measurement_state: weighted.length === 0 ? "UNMEASURED" : weighted.length === group.length ? "MEASURED" : "PARTIAL_COVERAGE",
      methodology_version: "weighted-evidence-v1",
      computed_at: now
    });
  }
  const prog = await db.from("hso_progress_snapshots").insert(progressRows);
  if (prog.error) return reply({ error: "progress_write_failed", detail: prog.error.message }, 500);

  const snapshotIds = [...new Set(snapshots.map((s: any) => s.id))];
  const snapshotCoverage = {
    sync_run_id: syncRunId,
    observed_sources: [...new Set(snapshots.map((s: any) => s.source_key))],
    missing_sources: REQUIRED.filter((sourceKey) => !snapshots.some((s: any) => s.source_key === sourceKey))
  };
  const primary = eligible[0] || null;
  const completionGap = {
    required_criteria_count: criteria.length,
    verified_criteria_count: criteria.filter((c: any) => ["VERIFIED","ACCEPTED"].includes(c.state) && c.evidence_record_id).length,
    incomplete_criteria: criteria.filter((c: any) => !["VERIFIED","ACCEPTED"].includes(c.state) || !c.evidence_record_id).map((c: any) => ({ key: c.criterion_key, title: c.title, state: c.state })),
    baseline_state: criteria.length ? "CONFIGURED" : "NOT_CONFIGURED"
  };
  const state = primary ? "PRIMARY_SELECTED" : staleSources.length ? "SOURCE_STALE" : "NO_ELIGIBLE_ACTION";
  const run = await db.from("hso_decision_runs").insert({
    engine_version: ENGINE, policy_version: POLICY, decision_state: state,
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
      work_item_id: primary.item.id, snapshot_id: snapshots[0]?.id || null,
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
    decision_type: "NO_ELIGIBLE_ACTION", eligibility_state: staleSources.length ? "SOURCE_STALE" : "NONE_ELIGIBLE",
    policy_version: POLICY, rationale: { decision_run_id: run.data.id, stale_sources: staleSources, blocked_count: blocked.length }
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
