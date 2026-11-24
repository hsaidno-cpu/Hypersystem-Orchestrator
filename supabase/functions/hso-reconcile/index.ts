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
  return p;
}
function titleOf(props: Record<string, any>) {
  for (const [name, value] of Object.entries(props ?? {})) {
    if ((value as any)?.type === "title" || (value as any)?.title) return richText((value as any).title) ?? name;
  }
  return "Untitled source record";
}
function mapPage(page: any, kind: string, sourceKey: string) {
  const p = page.properties ?? {};
  const title = titleOf(p);
  if (kind === "work_items") return {
    source_key: sourceKey, external_id: page.id, title,
    execution_state: prop(p, "Delivery State") ?? prop(p, "Status") ?? "UNKNOWN",
    verification_state: prop(p, "Verification State") ?? "UNKNOWN",
    gate_state: prop(p, "Gate State") ?? "NOT_ASSESSED",
    priority: prop(p, "Priority"), pre_stage: prop(p, "PRE Stage"),
    ecosystem_stage: prop(p, "Ecosystem Stage"),
    dependencies: prop(p, "Dependencies") ?? [],
    next_action: prop(p, "Next Action"), blocker: prop(p, "Blocker / Risk"),
    source_url: page.url, source_updated_at: page.last_edited_time,
    observed_at: new Date().toISOString(), raw_properties: p,
  };
  if (kind === "executions") return {
    source_key: sourceKey, external_id: page.id,
    run_name: title, correlation_id: prop(p, "Case / Correlation ID"),
    owner_role: prop(p, "Primary Owner"), pre_stage: prop(p, "PRE Stage"),
    status: prop(p, "Status") ?? "UNKNOWN", github_run_id: prop(p, "GitHub Run ID"),
    github_workflow_url: prop(p, "GitHub Workflow URL"),
    execution_receipt_url: prop(p, "Execution Receipt URL"), audit_url: prop(p, "Audit URL"),
    failure_recovery_summary: prop(p, "Failure / Recovery Summary"),
    retry_count: Number(prop(p, "Retry Count") ?? 0), completed_at: prop(p, "Completed At"),
    source_url: page.url, observed_at: new Date().toISOString(), raw_properties: p,
  };
  return {
    source_key: sourceKey, external_id: page.id, title,
    evidence_type: prop(p, "Evidence Type") ?? "External Source",
    evidence_state: prop(p, "Evidence State") ?? "UNKNOWN",
    freshness: prop(p, "Evidence Freshness") ?? "UNKNOWN",
    repository_url: prop(p, "Repository URL"), branch_ref: prop(p, "Branch / Ref"),
    commit_sha: prop(p, "Commit SHA"), pr_url: prop(p, "PR URL"),
    ci_run_url: prop(p, "CI Run URL"), artifact_url: prop(p, "Artifact URL"),
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
async function queryNotion(dataSource: string, token: string) {
  const results: any[] = [];
  let cursor: string | undefined;
  for (let i = 0; i < 6; i++) {
    const response = await fetch(`https://api.notion.com/v1/data_sources/${dataSource}/query`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}`, "Notion-Version": NOTION_VERSION, "Content-Type": "application/json" },
      body: JSON.stringify({ page_size: 100, ...(cursor ? { start_cursor: cursor } : {}) }),
      signal: AbortSignal.timeout(15000),
    });
    if (!response.ok) throw new Error(`Notion query failed: HTTP ${response.status}`);
    const data = await response.json();
    results.push(...(data.results ?? []));
    if (!data.has_more || !data.next_cursor) break;
    cursor = data.next_cursor;
  }
  return results;
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
      const [repo, prs, runs] = await Promise.all([
        getJson(`https://api.github.com/repos/${PROJECT}`, ghHeaders),
        getJson(`https://api.github.com/repos/${PROJECT}/pulls?state=all&per_page=50`, ghHeaders),
        getJson(`https://api.github.com/repos/${PROJECT}/actions/runs?per_page=50`, ghHeaders),
      ]);
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
      const ghSnapshot = { repository: { full_name: repo.full_name, html_url: repo.html_url, default_branch: repo.default_branch }, pulls: prs.map((p: any) => ({ number: p.number, state: p.state, title: p.title, html_url: p.html_url, head_sha: p.head?.sha })), workflow_runs: (runs.workflow_runs ?? []).map((w: any) => ({ id: w.id, name: w.name, status: w.status, conclusion: w.conclusion, head_sha: w.head_sha, html_url: w.html_url })) };
      const { error: snapError } = await db.from("hso_source_snapshots").insert({
        source_key: "github-hso-parent", sync_run_id: run.id, content_hash: await digest(ghSnapshot),
        freshness: "FRESH", record_count: evidence.length, snapshot: ghSnapshot,
      });
      if (snapError) throw snapError;
      await db.from("hso_sources").update({ status: "connected", last_sync_at: new Date().toISOString(), last_success_at: new Date().toISOString(), last_error: null }).eq("source_key", "github-hso-parent");
      results.github = { status: "connected", pull_requests: prs.length, workflow_runs: (runs.workflow_runs ?? []).length, evidence_upserted: evidence.length };
    } catch (error) {
      const message = error instanceof Error ? error.message : "GitHub sync failed";
      errors.push(`github: ${message}`); results.github = { status: "degraded", error: message };
      await db.from("hso_sources").update({ status: "degraded", last_sync_at: new Date().toISOString(), last_error: message }).eq("source_key", "github-hso-parent");
    }

    if (!notionToken) {
      results.notion = { status: "not_configured", reason: "NOTION_API_TOKEN secret is missing" };
    } else {
      for (const source of notionSources) {
        try {
          const pages = await queryNotion(source.dataSource, notionToken);
          const rows = pages.map((p) => mapPage(p, source.kind, source.key));
          if (rows.length) {
            const table = source.kind === "work_items" ? "hso_work_items" : source.kind === "executions" ? "hso_executions" : "hso_evidence_records";
            const conflict = "source_key,external_id";
            const { error } = await db.from(table).upsert(rows, { onConflict: conflict });
            if (error) throw error;
          }
          const snapshot = { data_source_id: source.dataSource, kind: source.kind, page_count: pages.length, page_ids: pages.map((p) => p.id) };
          const { error: snapError } = await db.from("hso_source_snapshots").insert({
            source_key: source.key, sync_run_id: run.id, content_hash: await digest(snapshot),
            freshness: "FRESH", record_count: pages.length, snapshot,
          });
          if (snapError) throw snapError;
          await db.from("hso_sources").update({ status: "connected", last_sync_at: new Date().toISOString(), last_success_at: new Date().toISOString(), last_error: null }).eq("source_key", source.key);
          seen += pages.length; upserted += rows.length;
          results[source.key] = { status: "connected", records_seen: pages.length, records_upserted: rows.length };
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
    return jsonResponse({ run_id: run.id, status, records_seen: seen, records_upserted: upserted, sources: results, errors });
  } catch (error) {
    const message = error instanceof Error ? error.message : "unexpected_sync_failure";
    await db.from("hso_sync_runs").update({ status: "failed", finished_at: new Date().toISOString(), error_summary: message }).eq("id", run.id);
    return jsonResponse({ run_id: run.id, status: "failed", error: message }, 500);
  }
});
