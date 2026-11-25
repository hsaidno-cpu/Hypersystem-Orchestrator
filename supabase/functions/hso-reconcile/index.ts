import { createClient } from "npm:@supabase/supabase-js@2.57.0";

const PROJECT = "hsaidno-cpu/Hypersystem-Orchestrator";
const NOTION_VERSION = Deno.env.get("NOTION_API_VERSION") ?? "2025-09-03";
const notionSources = [
  { key: "notion-roadmap", dataSource: "42299868-397f-8166-bc5b-000bad757827", kind: "work_items" },
  { key: "notion-execution-ledger", dataSource: "42299868-397f-8167-b8ea-000b720a9a66", kind: "executions" },
  { key: "notion-evidence-registry", dataSource: "42299868-397f-817c-bb25-000b49b243fa", kind: "evidence" },
];

function jsonResponse(body: unknown, status = 200) {
  return Response.json(body, { status, headers: { "cache-control": "no-store" } });
}
async function digest(value: unknown) {
  const bytes = new TextEncoder().encode(JSON.stringify(value));
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(hash)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function richText(value: any): string | null {
  if (!value) return null;
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map((x) => x.plain_text ?? x.text?.content ?? "").join("");
  return value.plain_text ?? value.name ?? value.url ?? null;
}
function prop(props: Record<string, any>, name: string): any {
  const p = props?.[name];
  if (!p) return null;
  if (p.title) return richText(p.title);
  if (p.rich_text) return richText(p.rich_text);
  if (p.select) return p.select.name ?? null;
  if (p.status) return p.status.name ?? null;
  if (p.url) return p.url;
  if (p.number !== undefined) return p.number;
  if (p.date?.start) return p.date.start;
  if (p.checkbox !== undefined) return p.checkbox;
  if (p.unique_id?.number !== undefined) return p.unique_id.number;
  if (p.relation) return p.relation.map((item: any) => item.id).filter(Boolean);
  if (p.people) return p.people.map((person: any) => person.id).filter(Boolean);
  return p;
}
function singlePerson(value: any): string | null {
  return Array.isArray(value) && value.length === 1 ? String(value[0]) : null;
}
function titleOf(props: Record<string, any>) {
  for (const [name, value] of Object.entries(props ?? {})) {
    if ((value as any)?.type === "title" || (value as any)?.title) return richText((value as any).title) ?? name;
  }
  return "Untitled source record";
}
function stringArray(value: any): string[] {
  if (Array.isArray(value)) return value.map((item) => String(item)).filter(Boolean);
  if (typeof value !== "string" || !value.trim()) return [];
  try {
    const parsed = JSON.parse(value);
    if (Array.isArray(parsed)) return parsed.map((item) => String(item)).filter(Boolean);
  } catch { /* plain-text dependency value */ }
  return value.split(/[\\r\\n,;]+/).map((item) => item.trim()).filter(Boolean);
}
function mapPage(page: any, kind: string, sourceKey: string) {
  const p = page.properties ?? {};
  const title = titleOf(p);
  if (kind === "work_items") {
    const status = prop(p, "Status") ?? "UNKNOWN";
    const gate = prop(p, "Gate State") ?? "NOT_ASSESSED";
    const lastEvaluated = prop(p, "Last Evaluated");
    const verifiedAt = ["Verified", "Accepted"].includes(String(status)) && gate === "PASS" && lastEvaluated
      ? new Date(String(lastEvaluated)).toISOString() : null;
    return {
      source_key: sourceKey, external_id: page.id, title,
      execution_state: status, verification_state: "UNKNOWN",
      gate_state: gate, priority: prop(p, "Priority"), pre_stage: prop(p, "PRE Stage"),
      ecosystem_stage: prop(p, "Ecosystem Stage"), milestone_key: prop(p, "Ecosystem Stage"),
      parent_milestone_id: prop(p, "Parent Milestone ID"),
      item_key: prop(p, "Work Item ID") === null ? null : String(prop(p, "Work Item ID")),
      dependencies: stringArray(prop(p, "Dependencies")),
      dependency_work_item_ids: stringArray(prop(p, "Dependency Work Item IDs")),
      next_action: prop(p, "Next Action"), blocker: prop(p, "Blocker / Risk"),
      project_area: prop(p, "Project Area"), record_type: prop(p, "Record Type"),
      accountable_role: prop(p, "Accountable Role"),
      expected_progress_pct: prop(p, "Expected Progress %"),
      baseline_start_date: prop(p, "Baseline Start Date"),
      acceptance_criteria: prop(p, "Acceptance Criteria"),
      progress_percent: prop(p, "Progress %"), progress_basis: prop(p, "Progress Basis"),
      source_commit: prop(p, "Source Commit"), target_date: prop(p, "Target Date"),
      scope_weight: prop(p, "Scope Weight"), weight_rationale: prop(p, "Weight Rationale"),
      scope_inclusion_state: prop(p, "Scope Inclusion State") ?? "PENDING",
      scope_decision_by: singlePerson(prop(p, "Scope Decision By")),
      scope_decision_at: prop(p, "Scope Decision At"),
      scope_decision_rationale: prop(p, "Scope Decision Rationale"),
      scope_weight_approval: prop(p, "Scope Weight Approval") ?? "PENDING",
      scope_weight_approved_by: singlePerson(prop(p, "Scope Weight Approved By")),
      scope_weight_approved_at: prop(p, "Scope Weight Approved At"),
      estimated_effort_hours: prop(p, "Estimated Effort Hours"),
      dependency_unlock_value: prop(p, "Dependency Unlock Value"),
      risk_reduction: prop(p, "Risk Reduction"),
      critical_path_impact: prop(p, "Critical Path Impact"),
      urgency: prop(p, "Urgency"), effort_efficiency: prop(p, "Effort Efficiency"),
      evidence_confidence: prop(p, "Evidence Confidence"),
      requires_human_approval: prop(p, "Requires Human Approval"),
      approval_state: prop(p, "Approval State"),
      security_disposition: prop(p, "Security Disposition"),
      execution_risk: prop(p, "Execution Risk"),
      target_branch: prop(p, "Target Branch"), head_commit_sha: prop(p, "Head Commit SHA"),
      reviewed_commit_sha: prop(p, "Reviewed Commit SHA"), ci_commit_sha: prop(p, "CI Commit SHA"),
      change_surface: prop(p, "Change Surface"), execution_target: prop(p, "Execution Target"),
      pr_url: prop(p, "PR URL"), ci_run_url: prop(p, "CI Run URL"),
      repository_url: prop(p, "GitHub Repository"),
      source_verified_at: verifiedAt,
      source_url: page.url, source_updated_at: page.last_edited_time,
      observed_at: new Date().toISOString(), raw_properties: p,
    };
  }
  if (kind === "executions") return {
    source_key: sourceKey, external_id: page.id,
    run_name: prop(p, "Run Name") ?? title, correlation_id: prop(p, "Case / Correlation ID"),
    owner_role: prop(p, "Primary Owner"), pre_stage: prop(p, "PRE Stage"),
    status: prop(p, "Run State") ?? "UNKNOWN", github_run_id: prop(p, "GitHub Run ID"),
    github_workflow_url: prop(p, "GitHub Workflow URL"),
    execution_id: prop(p, "Execution ID") === null ? null : String(prop(p, "Execution ID")),
    run_type: prop(p, "Run Type"),
    executing_agent: prop(p, "Executing Agent"),
    target_branch: prop(p, "Target Branch"), head_commit_sha: prop(p, "Head Commit SHA"),
    changed_files: stringArray(prop(p, "Changed Files")),
    validation_summary: prop(p, "Validation Summary"),
    acceptance_result: prop(p, "Acceptance Result"),
    stop_reason: prop(p, "Stop Reason"),
    source_commit: prop(p, "Source Commit"), source_repository: prop(p, "Source Repository"),
    plan_artifact_url: prop(p, "Plan Artifact URL"),
    supporting_evidence: stringArray(prop(p, "Supporting Evidence")),
    supporting_specialists: stringArray(prop(p, "Supporting Specialists")),
    verification_state: prop(p, "Verification State"),
    related_work_item: stringArray(prop(p, "Related Work Item"))[0] ?? null,
    execution_receipt_url: prop(p, "Execution Receipt URL"), audit_url: prop(p, "Audit URL"),
    failure_recovery_summary: prop(p, "Failure / Recovery Summary"),
    retry_count: Number(prop(p, "Retry Count") ?? 0), completed_at: prop(p, "Completed At"),
    source_url: page.url, observed_at: new Date().toISOString(), raw_properties: p,
  };
  return {
    source_key: sourceKey, external_id: page.id, title,
    evidence_id: prop(p, "Evidence ID") === null ? null : String(prop(p, "Evidence ID")),
    title: prop(p, "Evidence Title") ?? title,
    evidence_type: prop(p, "Evidence Type") ?? "External Source",
    evidence_state: prop(p, "Evidence State") ?? "UNKNOWN",
    freshness: prop(p, "Evidence Freshness") ?? "UNKNOWN",
    repository_url: prop(p, "Repository URL"), branch_ref: prop(p, "Branch / Ref"),
    commit_sha: prop(p, "Commit SHA"), pr_url: prop(p, "PR URL"),
    ci_run_url: prop(p, "CI Run URL"), artifact_url: prop(p, "Artifact URL"),
    content_digest: prop(p, "Content Digest"), source_locator: prop(p, "Source Locator"),
    verified_at: prop(p, "Verified At"), verifier_role: prop(p, "Verifier Role"),
    related_work_item: stringArray(prop(p, "Related Work Item"))[0] ?? null,
    claim_supported: prop(p, "Claim Supported"), known_limitation: prop(p, "Known Limitation"),
    observed_at: prop(p, "Observed At") ?? new Date().toISOString(),
    source_url: page.url, payload: p,
  };
}
async function getJson(url: string, headers: Record<string, string>) {
  const response = await fetch(url, { headers, signal: AbortSignal.timeout(15000) });
  if (!response.ok) throw new Error(`HTTP ${response.status} for ${new URL(url).pathname}`);
  return await response.json();
}
const MAX_SOURCE_PAGES = 1000;
async function queryNotion(dataSource: string, token: string) {
  const results: any[] = [];
  const seenCursors = new Set<string>();
  let cursor: string | undefined;
  let pageCount = 0;
  while (pageCount < MAX_SOURCE_PAGES) {
    const response = await fetch(`https://api.notion.com/v1/data_sources/${dataSource}/query`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}`, "Notion-Version": NOTION_VERSION, "Content-Type": "application/json" },
      body: JSON.stringify({ page_size: 100, ...(cursor ? { start_cursor: cursor } : {}) }),
      signal: AbortSignal.timeout(15000),
    });
    if (!response.ok) throw new Error(`Notion query failed: HTTP ${response.status}`);
    const data = await response.json();
    pageCount++;
    results.push(...(data.results ?? []));
    if (!data.has_more) return { results, pageCount, exhausted: true };
    if (!data.next_cursor) throw new Error("Notion pagination incomplete: has_more without next_cursor");
    if (seenCursors.has(data.next_cursor)) throw new Error("Notion pagination cursor repeated; refusing partial source snapshot");
    seenCursors.add(data.next_cursor);
    cursor = data.next_cursor;
  }
  throw new Error(`Notion pagination exceeded ${MAX_SOURCE_PAGES} pages; refusing to mark source connected`);
}
async function queryNotionBlocks(blockId: string, token: string) {
  const results: any[] = [];
  const seenCursors = new Set<string>();
  let cursor: string | undefined;
  let pageCount = 0;
  while (pageCount < MAX_SOURCE_PAGES) {
    const url = new URL(`https://api.notion.com/v1/blocks/${blockId}/children`);
    url.searchParams.set("page_size", "100");
    if (cursor) url.searchParams.set("start_cursor", cursor);
    const response = await fetch(url, {
      headers: { "Authorization": `Bearer ${token}`, "Notion-Version": NOTION_VERSION },
      signal: AbortSignal.timeout(15000),
    });
    if (!response.ok) throw new Error(`Notion block pagination failed: HTTP ${response.status}`);
    const data = await response.json();
    pageCount++;
    results.push(...(data.results ?? []));
    if (!data.has_more) return { results, pageCount, exhausted: true };
    if (!data.next_cursor) throw new Error("Notion block pagination incomplete: has_more without next_cursor");
    if (seenCursors.has(data.next_cursor)) throw new Error("Notion block cursor repeated; refusing partial snapshot");
    seenCursors.add(data.next_cursor);
    cursor = data.next_cursor;
  }
  throw new Error(`Notion blocks exceeded ${MAX_SOURCE_PAGES} pages`);
}
async function collectNotionBlockTree(blockId: string, token: string, depth = 0, budget = { nodes: 0, pages: 0 }): Promise<any[]> {
  if (depth > 20) throw new Error("Notion block nesting exceeded depth 20");
  const page = await queryNotionBlocks(blockId, token);
  budget.pages += page.pageCount;
  const tree: any[] = [];
  for (const block of page.results) {
    budget.nodes++;
    if (budget.nodes > 20000) throw new Error("Notion Control Center exceeded 20000 blocks; snapshot refused");
    const item: any = { id: block.id, type: block.type, has_children: Boolean(block.has_children) };
    if (block.has_children) item.children = await collectNotionBlockTree(block.id, token, depth + 1, budget);
    tree.push(item);
  }
  return tree;
}
async function getAllGitHubPages(url: string, headers: Record<string, string>, unwrapKey?: string) {
  const results: any[] = [];
  let pageCount = 0;
  while (pageCount < MAX_SOURCE_PAGES) {
    const pageUrl = new URL(url);
    pageUrl.searchParams.set("per_page", "100");
    pageUrl.searchParams.set("page", String(pageCount + 1));
    const response = await fetch(pageUrl, { headers, signal: AbortSignal.timeout(20000) });
    if (!response.ok) throw new Error(`GitHub pagination failed: HTTP ${response.status} for ${pageUrl.pathname}`);
    const payload = await response.json();
    const batch = unwrapKey ? payload?.[unwrapKey] : payload;
    if (!Array.isArray(batch)) throw new Error("GitHub pagination returned an unexpected payload");
    pageCount++;
    results.push(...batch);
    if (batch.length < 100) return { results, pageCount, exhausted: true };
  }
  throw new Error(`GitHub pagination exceeded ${MAX_SOURCE_PAGES} pages; refusing partial source snapshot`);
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return jsonResponse({ error: "method_not_allowed" }, 405);
  const syncToken = Deno.env.get("HSO_SYNC_TOKEN");
  const supplied = req.headers.get("x-hso-sync-token") ?? "";
  if (!syncToken || supplied.length !== syncToken.length || !crypto.subtle) {
    return jsonResponse({ error: "sync_not_configured_or_unauthorized" }, 401);
  }
  let mismatch = 0;
  for (let i = 0; i < supplied.length; i++) mismatch |= supplied.charCodeAt(i) ^ syncToken.charCodeAt(i);
  if (mismatch !== 0) return jsonResponse({ error: "unauthorized" }, 401);

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !serviceKey) return jsonResponse({ error: "backend_not_configured" }, 503);
  const notionToken = Deno.env.get("NOTION_API_TOKEN");
  const githubToken = Deno.env.get("GITHUB_TOKEN");
  let triggerKind = "scheduled";
  try {
    const body = await req.json();
    if (["manual", "scheduled", "initial", "recovery"].includes(body?.trigger_kind)) triggerKind = body.trigger_kind;
  } catch { /* no body is permitted for scheduler calls */ }

  const db = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });
  const startedAt = new Date().toISOString();
  const { data: run, error: runError } = await db.from("hso_sync_runs").insert({
    trigger_kind: triggerKind, status: "running", started_at: startedAt,
  }).select("id").single();
  if (runError || !run) return jsonResponse({ error: "sync_run_create_failed" }, 500);

  const results: Record<string, any> = {};
  let seen = 0, upserted = 0;
  const errors: string[] = [];

  try {
    const ghHeaders: Record<string, string> = {
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      ...(githubToken ? { "Authorization": `Bearer ${githubToken}` } : {}),
    };
    try {
      const [repo, prsPage, runsPage] = await Promise.all([
        getJson(`https://api.github.com/repos/${PROJECT}`, ghHeaders),
        getAllGitHubPages(`https://api.github.com/repos/${PROJECT}/pulls?state=all`, ghHeaders),
        getAllGitHubPages(`https://api.github.com/repos/${PROJECT}/actions/runs`, ghHeaders, "workflow_runs"),
      ]);
      const prs = prsPage.results;
      const runs = { workflow_runs: runsPage.results };
      if (!prsPage.exhausted || !runsPage.exhausted) throw new Error("GitHub source pagination is not complete");
      const evidence = [
        ...prs.map((pr: any) => ({
          source_key: "github-hso-parent", external_id: `pr:${pr.number}`,
          title: `PR #${pr.number} — ${pr.title}`, evidence_type: "Pull Request",
          evidence_state: pr.merged_at ? "UNKNOWN" : pr.state === "open" ? "RUNNING" : "UNKNOWN",
          freshness: "FRESH", repository_url: repo.html_url, branch_ref: pr.head?.ref,
          commit_sha: pr.head?.sha, pr_url: pr.html_url, claim_supported: `PR state observed: ${pr.state}`,
          known_limitation: "PR state is metadata only; not proof of accepted delivery or deployment.",
          observed_at: new Date().toISOString(), source_url: pr.html_url, payload: { number: pr.number, state: pr.state, merged_at: pr.merged_at, draft: pr.draft },
        })),
        ...(runs.workflow_runs ?? []).map((wr: any) => ({
          source_key: "github-hso-parent", external_id: `workflow-run:${wr.id}`,
          title: `CI #${wr.run_number} — ${wr.name}`, evidence_type: "CI Run",
          evidence_state: wr.conclusion === "success" ? "PASS" : wr.conclusion === "failure" ? "FAIL" : wr.status === "in_progress" || wr.status === "queued" ? "RUNNING" : "UNKNOWN",
          freshness: "FRESH", repository_url: repo.html_url, branch_ref: wr.head_branch,
          commit_sha: wr.head_sha, ci_run_url: wr.html_url,
          claim_supported: `Workflow ${wr.status}; conclusion ${wr.conclusion ?? "pending"}`,
          known_limitation: "CI result applies only to the recorded head SHA; it does not prove merge, production, or independent acceptance.",
          observed_at: new Date().toISOString(), source_url: wr.html_url,
          payload: { id: wr.id, run_number: wr.run_number, name: wr.name, status: wr.status, conclusion: wr.conclusion, event: wr.event },
        })),
      ];
      seen += prs.length + (runs.workflow_runs ?? []).length + 1;
      if (evidence.length) {
        const { error } = await db.from("hso_evidence_records").upsert(evidence, { onConflict: "source_key,external_id" });
        if (error) throw error;
        upserted += evidence.length;
      }
      const ghScopeHash = await digest({
        pull_ids: prs.map((p: any) => String(p.id)).sort(),
        workflow_ids: (runs.workflow_runs ?? []).map((w: any) => String(w.id)).sort(),
      });
      const ghSnapshot = {
        repository: { full_name: repo.full_name, html_url: repo.html_url, default_branch: repo.default_branch },
        pulls: prs.map((p: any) => ({ id: p.id, number: p.number, state: p.state, title: p.title, html_url: p.html_url, head_sha: p.head?.sha })),
        workflow_runs: (runs.workflow_runs ?? []).map((w: any) => ({ id: w.id, name: w.name, status: w.status, conclusion: w.conclusion, head_sha: w.head_sha, html_url: w.html_url })),
        pagination: { pulls_pages: prsPage.pageCount, runs_pages: runsPage.pageCount, exhausted: true },
        is_complete: true, completeness_state: "COMPLETE", scope_hash: ghScopeHash,
      };
      const { error: snapError } = await db.from("hso_source_snapshots").insert({
        source_key: "github-hso-parent", sync_run_id: run.id, content_hash: await digest(ghSnapshot),
        freshness: "FRESH", record_count: prs.length + runs.workflow_runs.length + 1,
        page_count: prsPage.pageCount + runsPage.pageCount, source_total_count: prs.length + runs.workflow_runs.length + 1,
        pagination_pages: prsPage.pageCount + runsPage.pageCount, pagination_complete: true,
        is_complete: true, completeness_state: "COMPLETE", scope_hash: ghScopeHash, snapshot: ghSnapshot,
      });
      if (snapError) throw snapError;
      await db.from("hso_sources").update({ status: "connected", last_sync_at: new Date().toISOString(),
        last_success_at: new Date().toISOString(), last_complete_at: new Date().toISOString(),
        last_record_count: prs.length + runs.workflow_runs.length + 1, last_scope_hash: ghScopeHash,
        last_error: null }).eq("source_key", "github-hso-parent");
      results.github = { status: "connected", complete: true, pull_requests: prs.length, workflow_runs: runs.workflow_runs.length, evidence_upserted: evidence.length, pagination_pages: prsPage.pageCount + runsPage.pageCount };
    } catch (error) {
      const message = error instanceof Error ? error.message : "GitHub sync failed";
      errors.push(`github: ${message}`); results.github = { status: "degraded", error: message };
      await db.from("hso_sources").update({ status: "degraded", last_sync_at: new Date().toISOString(), last_error: message }).eq("source_key", "github-hso-parent");
    }

    if (!notionToken) {
      results.notion = { status: "not_configured", reason: "NOTION_API_TOKEN secret is missing" };
      errors.push("notion: NOTION_API_TOKEN secret is missing");
      await db.from("hso_sources").update({ status: "not_configured", last_error: "NOTION_API_TOKEN secret is missing" }).eq("provider", "notion");
    } else {
      try {
        const notionHeaders = { "Authorization": "Bearer " + notionToken, "Notion-Version": NOTION_VERSION };
        const controlId = "42299868-397f-81b3-b8a2-d4f936f355cb";
        const controlPage = await getJson("https://api.notion.com/v1/pages/" + controlId, notionHeaders);
        const blockBudget = { nodes: 0, pages: 0 };
        const controlBlocks = await collectNotionBlockTree(controlId, notionToken, 0, blockBudget);
        const blockIds = controlBlocks.map((b: any) => b.id).sort();
        const controlScopeHash = await digest({ page_id: controlPage.id, block_ids: blockIds });
        const controlSnapshot = {
          page_id: controlPage.id, title: titleOf(controlPage.properties ?? {}),
          last_edited_time: controlPage.last_edited_time, url: controlPage.url,
          blocks: controlBlocks, block_count: blockBudget.nodes,
          pagination_pages: blockBudget.pages, pagination_complete: true,
          is_complete: true, completeness_state: "COMPLETE", scope_hash: controlScopeHash,
        };
        const { error: controlSnapError } = await db.from("hso_source_snapshots").insert({
          source_key: "notion-control-center", sync_run_id: run.id,
          content_hash: await digest(controlSnapshot), freshness: "FRESH",
          record_count: blockBudget.nodes + 1, page_count: blockBudget.pages,
          source_total_count: blockBudget.nodes + 1, pagination_pages: blockBudget.pages,
          pagination_complete: true, is_complete: true, completeness_state: "COMPLETE",
          scope_hash: controlScopeHash, snapshot: controlSnapshot,
        });
        if (controlSnapError) throw controlSnapError;
        await db.from("hso_sources").update({ status: "connected", last_sync_at: new Date().toISOString(),
          last_success_at: new Date().toISOString(), last_complete_at: new Date().toISOString(),
          last_record_count: blockBudget.nodes + 1, last_scope_hash: controlScopeHash, last_error: null }).eq("source_key", "notion-control-center");
        results["notion-control-center"] = { status: "connected", complete: true, blocks_observed: blockBudget.nodes, pagination_pages: blockBudget.pages };
      } catch (error) {
        const message = error instanceof Error ? error.message : "Notion Control Center fetch failed";
        errors.push("notion-control-center: " + message);
        results["notion-control-center"] = { status: "degraded", error: message };
        await db.from("hso_sources").update({ status: "degraded", last_sync_at: new Date().toISOString(), last_error: message }).eq("source_key", "notion-control-center");
      }
      for (const source of notionSources) {
        try {
          const pageResult = await queryNotion(source.dataSource, notionToken);
          const pages = pageResult.results;
          if (!pageResult.exhausted) throw new Error("Notion source pagination did not exhaust");
          const rows = pages.map((p) => mapPage(p, source.kind, source.key));
          if (rows.length) {
            const table = source.kind === "work_items" ? "hso_work_items" : source.kind === "executions" ? "hso_executions" : "hso_evidence_records";
            const conflict = "source_key,external_id";
            if (source.kind === "work_items") {
              const ids = rows.map((row: any) => row.external_id);
              const { data: previous, error: previousError } = await db.from("hso_work_items")
                .select("*").eq("source_key", source.key).in("external_id", ids);
              if (previousError) throw previousError;
              const previousById = new Map((previous ?? []).map((row: any) => [row.external_id, row]));
              const history: any[] = [];
              for (const row of rows) {
                const prior: any = previousById.get(row.external_id);
                if (!prior) continue;
                const changedFields = Object.keys(row).filter((key) =>
                  !["raw_properties", "observed_at"].includes(key) &&
                  JSON.stringify(prior[key] ?? null) !== JSON.stringify(row[key] ?? null)
                );
                if (!changedFields.length) continue;
                const transition = {
                  source_key: source.key,
                  external_id: row.external_id,
                  from_execution_state: prior.execution_state,
                  to_execution_state: row.execution_state,
                  from_gate_state: prior.gate_state,
                  to_gate_state: row.gate_state,
                  from_verification_state: prior.verification_state,
                  to_verification_state: row.verification_state,
                  source_updated_at: row.source_updated_at,
                  changed_fields: changedFields
                };
                history.push({
                  work_item_id: prior.id,
                  source_key: source.key,
                  external_id: row.external_id,
                  transition_key: await digest(transition),
                  from_execution_state: prior.execution_state,
                  to_execution_state: row.execution_state,
                  from_gate_state: prior.gate_state,
                  to_gate_state: row.gate_state,
                  from_verification_state: prior.verification_state,
                  to_verification_state: row.verification_state,
                  changed_at: new Date().toISOString(),
                  source_updated_at: row.source_updated_at,
                  source_url: row.source_url,
                  changed_fields: changedFields,
                  observed_payload: Object.fromEntries(changedFields.map((key) => [key, row[key] ?? null]))
                });
              }
              if (history.length) {
                const { error: historyError } = await db.from("hso_work_item_history")
                  .upsert(history, { onConflict: "transition_key", ignoreDuplicates: true });
                if (historyError) throw historyError;
              }
            }
            const { error } = await db.from(table).upsert(rows, { onConflict: conflict });
            if (error) throw error;
          }
          const pageIds = pages.map((p: any) => String(p.id)).sort();
          const scopeHash = await digest(pageIds);
          const snapshot = {
            data_source_id: source.dataSource, kind: source.kind, record_count: pages.length,
            page_count: pageResult.pageCount, source_total_count: pages.length, page_ids: pageIds,
            pagination_complete: pageResult.exhausted, is_complete: true,
            completeness_state: "COMPLETE", scope_hash: scopeHash,
          };
          const { error: snapError } = await db.from("hso_source_snapshots").insert({
            source_key: source.key, sync_run_id: run.id, content_hash: await digest({ snapshot, rows }),
            freshness: "FRESH", record_count: pages.length, page_count: pageResult.pageCount,
            source_total_count: pages.length, pagination_pages: pageResult.pageCount,
            pagination_complete: true, is_complete: true, completeness_state: "COMPLETE",
            scope_hash: scopeHash, snapshot,
          });
          if (snapError) throw snapError;
          await db.from("hso_sources").update({ status: "connected", last_sync_at: new Date().toISOString(),
            last_success_at: new Date().toISOString(), last_complete_at: new Date().toISOString(),
            last_record_count: pages.length, last_scope_hash: scopeHash, last_error: null }).eq("source_key", source.key);
          seen += pages.length; upserted += rows.length;
          results[source.key] = { status: "connected", complete: true, records_seen: pages.length, records_upserted: rows.length, pagination_pages: pageResult.pageCount };
        } catch (error) {
          const message = error instanceof Error ? error.message : "Notion source sync failed";
          errors.push(`${source.key}: ${message}`);
          results[source.key] = { status: "degraded", error: message };
          await db.from("hso_sources").update({ status: "degraded", last_sync_at: new Date().toISOString(), last_error: message }).eq("source_key", source.key);
        }
      }
    }

    const status = errors.length ? (Object.keys(results).some((k) => results[k]?.status === "connected") ? "partial" : "failed") : "succeeded";
    const finishedAt = new Date().toISOString();
    await db.from("hso_sync_runs").update({
      status, finished_at: finishedAt, source_results: results, records_seen: seen, records_upserted: upserted,
      error_summary: errors.length ? errors.join(" | ").slice(0, 4000) : null,
    }).eq("id", run.id);

    let decisionEngine: any = { status: "not_run" };
    if (syncToken) {
      try {
        const decisionResponse = await fetch(supabaseUrl + "/functions/v1/hso-decision-engine", {
          method: "POST",
          headers: { "content-type": "application/json", "x-hso-sync-token": syncToken },
          body: JSON.stringify({ trigger_kind: triggerKind, sync_run_id: run.id }),
          signal: AbortSignal.timeout(55000),
        });
        const decisionBody = await decisionResponse.json();
        decisionEngine = decisionResponse.ok
          ? { status: "computed", ...decisionBody }
          : { status: "failed", detail: decisionBody };
      } catch (error) {
        decisionEngine = { status: "failed", detail: error instanceof Error ? error.message : "decision engine request failed" };
      }
    }
    return jsonResponse({ run_id: run.id, status, records_seen: seen, records_upserted: upserted, sources: results, errors, decision_engine: decisionEngine });
  } catch (error) {
    const message = error instanceof Error ? error.message : "unexpected_sync_failure";
    await db.from("hso_sync_runs").update({ status: "failed", finished_at: new Date().toISOString(), error_summary: message }).eq("id", run.id);
    return jsonResponse({ run_id: run.id, status: "failed", error: message }, 500);
  }
});
