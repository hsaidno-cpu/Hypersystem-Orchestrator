import { createClient } from "npm:@supabase/supabase-js@2.57.0";
import {
  boundedBatchSize,
  gitBlobSha,
  migrationAcceptanceState,
  sha256Hex,
  SOURCE_BOUNDARIES,
  PRIOR_HSAR_PATH_COUNT,
  DIRECT_GITHUB_PATH_COUNT,
  DIRECT_GITHUB_UNIQUE_BLOB_COUNT,
  HSO_PRIOR_REPORTED_BLOB_COUNT,
  HSO_DIRECT_BLOB_COUNT,
  HSO_OMITTED_ADDED_PATHS,
} from "./core.ts";

const HSO_SNAPSHOT_COMMIT = "69479c9fc898d12d6780964fb431fb9a89b1c675";
const CATALOG_BLOB_SHA = "edc1566f41373c00dde45a52474d1e55ace38891";
const INSTRUCTION_SNAPSHOT_BLOB_SHA = "f58ac947a7b5015f67fdaeb5c62b28c238d695b2";
const GITHUB_API = "https://api.github.com";
const MAX_UPSERT_BATCH = 400;

function response(body: Record<string, unknown>, status = 200) {
  return Response.json(body, { status, headers: { "cache-control": "no-store" } });
}

function githubHeaders(token?: string | null): HeadersInit {
  return {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "HSO-Migration-Watchdog/1.0",
    ...(token ? { "Authorization": "Bearer " + token } : {}),
  };
}

async function verifyWatchdogToken(db: any, supplied: string): Promise<boolean> {
  const { data, error } = await db.rpc("hso_verify_migration_token", { p_token: supplied });
  if (error) throw new Error("watchdog_token_verification_failed");
  return data === true;
}

async function getGithubReadToken(db: any): Promise<string | null> {
  const { data, error } = await db.rpc("hso_get_migration_github_read_token");
  if (error) return null;
  return typeof data === "string" && data.length > 0 ? data : null;
}

async function fetchJson(url: string, headers: HeadersInit): Promise<any> {
  const result = await fetch(url, { headers, signal: AbortSignal.timeout(20000) });
  if (!result.ok) {
    const error = new Error("github_http_" + result.status + ":" + new URL(url).pathname);
    (error as any).status = result.status;
    (error as any).rateLimited = result.status === 403 && result.headers.get("x-ratelimit-remaining") === "0";
    throw error;
  }
  return await result.json();
}

async function upsertBatches(db: any, table: string, rows: any[], onConflict: string, ignoreDuplicates = false) {
  for (let i = 0; i < rows.length; i += MAX_UPSERT_BATCH) {
    const batch = rows.slice(i, i + MAX_UPSERT_BATCH);
    const { error } = await db.from(table).upsert(batch, {
      onConflict,
      ...(ignoreDuplicates ? { ignoreDuplicates: true } : {}),
    });
    if (error) throw new Error("upsert_" + table + ":" + error.message);
  }
}

async function upsertCapabilities(db: any, runId: string, apiToken: string | null) {
  const snapshotUrl = "https://raw.githubusercontent.com/hsaidno-cpu/Hypersystem-Orchestrator/" +
    HSO_SNAPSHOT_COMMIT + "/catalog/instruction-snapshots.json";
  const catalogUrl = "https://raw.githubusercontent.com/hsaidno-cpu/Hypersystem-Orchestrator/" +
    HSO_SNAPSHOT_COMMIT + "/catalog/plugins.json";
  const headers: HeadersInit = apiToken ? { "Authorization": "Bearer " + apiToken } : {};
  const [snapshotResponse, catalogResponse] = await Promise.all([
    fetch(snapshotUrl, { headers, signal: AbortSignal.timeout(20000) }),
    fetch(catalogUrl, { headers, signal: AbortSignal.timeout(20000) }),
  ]);
  if (!snapshotResponse.ok || !catalogResponse.ok) {
    throw new Error("capability_snapshot_http_" + snapshotResponse.status + "_catalog_" + catalogResponse.status);
  }
  const [snapshotText, catalogText] = await Promise.all([snapshotResponse.text(), catalogResponse.text()]);
  const snapshot = JSON.parse(snapshotText);
  const catalog = JSON.parse(catalogText);
  if (!Array.isArray(snapshot.plugins) || snapshot.total_skill_records !== 289) {
    throw new Error("unexpected_instruction_snapshot_shape");
  }
  const pluginMap = new Map((catalog.plugins ?? []).map((plugin: any) => [plugin.plugin_key, plugin]));
  const capabilityRows: any[] = [];
  const assessmentRows: any[] = [];
  for (const plugin of snapshot.plugins) {
    const parent: any = pluginMap.get(plugin.plugin_key) ?? {};
    for (const skill of plugin.skills ?? []) {
      capabilityRows.push({
        plugin_key: plugin.plugin_key,
        skill_name: skill.skill_name,
        source_uri: skill.source_uri ?? null,
        description: skill.description ?? null,
        instruction_bundle_path: plugin.instruction_path ?? null,
        snapshot_origin: plugin.origin ?? null,
        package_version: plugin.package_version ?? parent.platform_package_version ?? parent.release_version ?? null,
        git_source_version: plugin.git_source_version ?? parent.source_repository_version ?? null,
        catalog_source_state: parent.source_state ?? "UNSET",
        catalog_parity_state: parent.source_instruction_parity_status ?? "NOT_ASSESSED",
        snapshot_commit: HSO_SNAPSHOT_COMMIT,
        snapshot_blob_sha: INSTRUCTION_SNAPSHOT_BLOB_SHA,
        observed_at: new Date().toISOString(),
      });
      assessmentRows.push({
        plugin_key: plugin.plugin_key,
        skill_name: skill.skill_name,
        source_parity_state: "NOT_ASSESSED",
        contract_test_state: "NOT_RUN",
        route_test_state: "NOT_RUN",
        runtime_state: "NOT_RUN",
        acceptance_state: "OPEN",
        evidence: { seeded_from: "catalog/instruction-snapshots.json", run_id: runId },
      });
    }
  }
  if (capabilityRows.length !== 289) throw new Error("capability_count_mismatch:" + capabilityRows.length);
  await upsertBatches(db, "hso_migration_capabilities", capabilityRows, "plugin_key,skill_name");
  await upsertBatches(db, "hso_migration_capability_assessments", assessmentRows, "plugin_key,skill_name", true);
  const manifestHash = await sha256Hex(new TextEncoder().encode(snapshotText));
  return {
    plugin_count: snapshot.plugins.length,
    capability_count: capabilityRows.length,
    snapshot_commit: HSO_SNAPSHOT_COMMIT,
    instruction_snapshot_blob_sha: INSTRUCTION_SNAPSHOT_BLOB_SHA,
    catalog_blob_sha: CATALOG_BLOB_SHA,
    instruction_snapshot_sha256: manifestHash,
  };
}

async function scanBoundary(db: any, source: (typeof SOURCE_BOUNDARIES)[number], headers: HeadersInit, runId: string) {
  const scannedAt = new Date().toISOString();
  try {
    const tree = await fetchJson(
      GITHUB_API + "/repos/" + source.repository_full_name + "/git/trees/" + source.commit_sha + "?recursive=1",
      headers,
    );
    if (!Array.isArray(tree.tree)) throw new Error("github_tree_missing");
    const blobs = tree.tree.filter((entry: any) => entry.type === "blob");
    const sourceUpsert = await db.from("hso_migration_sources").upsert({
      boundary_key: source.boundary_key,
      repository_full_name: source.repository_full_name,
      commit_sha: source.commit_sha,
      visibility: source.visibility,
      expected_blob_paths: source.expected_blob_paths,
      observed_blob_paths: blobs.length,
      tree_sha: tree.sha ?? null,
      tree_truncated: Boolean(tree.truncated),
      status: tree.truncated ? "tree_truncated" : "scanning",
      last_scanned_at: scannedAt,
      last_error: null,
      latest_run_id: runId,
    }, { onConflict: "boundary_key" });
    if (sourceUpsert.error) throw new Error("source_record_upsert:" + sourceUpsert.error.message);

    const pathRows = blobs.map((entry: any) => ({
      boundary_key: source.boundary_key,
      repository_full_name: source.repository_full_name,
      source_commit: source.commit_sha,
      path: entry.path,
      blob_sha: entry.sha,
      size_bytes: Number(entry.size ?? 0),
      file_mode: entry.mode ?? "100644",
      observed_at: scannedAt,
    }));
    await upsertBatches(db, "hso_migration_paths", pathRows, "boundary_key,path");
    const blobRows = blobs.map((entry: any) => ({
      blob_sha: entry.sha,
      size_bytes: Number(entry.size ?? 0),
      content_status: "pending",
      source_repository_full_name: source.repository_full_name,
      source_boundary_key: source.boundary_key,
      source_path: entry.path,
      source_visibility: source.visibility,
      updated_at: scannedAt,
    }));
    await upsertBatches(db, "hso_migration_blobs", blobRows, "blob_sha", true);
    const status = tree.truncated ? "tree_truncated" : "tree_complete";
    const { error } = await db.from("hso_migration_sources").upsert({
      boundary_key: source.boundary_key,
      repository_full_name: source.repository_full_name,
      commit_sha: source.commit_sha,
      visibility: source.visibility,
      expected_blob_paths: source.expected_blob_paths,
      observed_blob_paths: blobs.length,
      tree_sha: tree.sha ?? null,
      tree_truncated: Boolean(tree.truncated),
      status,
      last_scanned_at: scannedAt,
      last_error: null,
      latest_run_id: runId,
    }, { onConflict: "boundary_key" });
    if (error) throw new Error("source_record_upsert:" + error.message);
    return {
      boundary_key: source.boundary_key,
      repository_full_name: source.repository_full_name,
      expected_blob_paths: source.expected_blob_paths,
      observed_blob_paths: blobs.length,
      tree_truncated: Boolean(tree.truncated),
      status,
      tree_sha: tree.sha ?? null,
      discrepancy: blobs.length - source.expected_blob_paths,
    };
  } catch (error) {
    const status = source.visibility === "private" ? "private_access_pending" : "scan_failed";
    const message = String((error as any)?.message ?? error).slice(0, 500);
    await db.from("hso_migration_sources").upsert({
      boundary_key: source.boundary_key,
      repository_full_name: source.repository_full_name,
      commit_sha: source.commit_sha,
      visibility: source.visibility,
      expected_blob_paths: source.expected_blob_paths,
      status,
      last_scanned_at: scannedAt,
      last_error: message,
      latest_run_id: runId,
    }, { onConflict: "boundary_key" });
    return {
      boundary_key: source.boundary_key,
      repository_full_name: source.repository_full_name,
      expected_blob_paths: source.expected_blob_paths,
      observed_blob_paths: null,
      status,
      error: message,
    };
  }
}

async function readBlobBatch(db: any, headers: HeadersInit, limit: number) {
  const { data: pending, error } = await db.from("hso_migration_blobs")
    .select("blob_sha,size_bytes,source_repository_full_name,source_path,source_visibility,attempt_count")
    .or("content_status.eq.pending,and(content_status.eq.failed,attempt_count.lt.3)")
    .order("size_bytes", { ascending: true })
    .limit(limit);
  if (error) throw new Error("pending_blob_query_failed:" + error.message);
  const results: any[] = [];
  for (const item of pending ?? []) {
    try {
      const blob = await fetchJson(
        GITHUB_API + "/repos/" + item.source_repository_full_name + "/git/blobs/" + item.blob_sha,
        headers,
      );
      if (blob.encoding !== "base64" || typeof blob.content !== "string") {
        await db.from("hso_migration_blobs").update({
          content_status: "too_large_or_unsupported",
          last_error: "GitHub did not return base64 content",
          attempt_count: Number(item.attempt_count ?? 0) + 1,
          last_read_at: new Date().toISOString(),
        }).eq("blob_sha", item.blob_sha);
        results.push({ blob_sha: item.blob_sha, status: "too_large_or_unsupported" });
        continue;
      }
      const normalized = blob.content.replace(/\s/g, "");
      const binary = atob(normalized);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
      const actualGitSha = await gitBlobSha(bytes);
      const contentSha256 = await sha256Hex(bytes);
      const verified = actualGitSha === item.blob_sha && bytes.length === Number(item.size_bytes);
      const state = verified ? "verified" : "mismatch";
      const update = await db.from("hso_migration_blobs").update({
        content_status: state,
        content_sha256: contentSha256,
        actual_git_blob_sha: actualGitSha,
        byte_length: bytes.length,
        sha_verified: verified,
        last_error: verified ? null : "Git blob hash or byte length mismatch",
        attempt_count: Number(item.attempt_count ?? 0) + 1,
        first_read_at: new Date().toISOString(),
        last_read_at: new Date().toISOString(),
        semantic_review_state: "NOT_REVIEWED",
      }).eq("blob_sha", item.blob_sha);
      if (update.error) throw new Error(update.error.message);
      results.push({ blob_sha: item.blob_sha, status: state, content_sha256: contentSha256, byte_length: bytes.length });
    } catch (error) {
      const message = String((error as any)?.message ?? error).slice(0, 500);
      await db.from("hso_migration_blobs").update({
        content_status: "failed",
        last_error: message,
        attempt_count: Number(item.attempt_count ?? 0) + 1,
        last_read_at: new Date().toISOString(),
      }).eq("blob_sha", item.blob_sha);
      results.push({ blob_sha: item.blob_sha, status: "failed", error: message });
      if ((error as any)?.rateLimited || message.includes("github_http_403")) break;
    }
  }
  return results;
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return response({ error: "method_not_allowed" }, 405);
  const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
  if (!supabaseUrl || !serviceRoleKey) return response({ error: "backend_not_configured" }, 503);

  const db = createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const suppliedToken = req.headers.get("x-hso-migration-token") ?? "";
  try {
    if (!suppliedToken || !(await verifyWatchdogToken(db, suppliedToken))) {
      return response({ error: "unauthorized" }, 401);
    }
  } catch {
    return response({ error: "watchdog_secret_unavailable" }, 503);
  }

  let body: any = {};
  try {
    const length = Number(req.headers.get("content-length") ?? "0");
    if (length > 4096) return response({ error: "payload_too_large" }, 413);
    body = await req.json();
  } catch { /* empty scheduled payload is permitted */ }

  const leaseToken = crypto.randomUUID();
  const { data: claimed, error: claimError } = await db.rpc("hso_try_claim_migration_watchdog", {
    p_lease_token: leaseToken,
  });
  if (claimError) return response({ error: "lease_claim_failed", detail: claimError.message }, 503);
  if (claimed !== true) return response({ status: "already_running" }, 202);

  const runStartedAt = new Date().toISOString();
  const triggerKind = body?.trigger_kind === "manual" ? "manual" : "scheduled";
  let runId: string | null = null;
  try {
    const { data: run, error: runError } = await db.from("hso_migration_runs")
      .insert({ trigger_kind: triggerKind, status: "running", started_at: runStartedAt, run_key: leaseToken })
      .select("id").single();
    if (runError || !run) throw new Error("run_record_create_failed:" + (runError?.message ?? "no row"));
    runId = run.id;

    const privateToken = await getGithubReadToken(db);
    const headers = githubHeaders(privateToken);
    const sourceResults = await Promise.all(SOURCE_BOUNDARIES.map((source) => {
      if (source.visibility === "private" && !privateToken) {
        return (async () => {
          await db.from("hso_migration_sources").upsert({
            boundary_key: source.boundary_key,
            repository_full_name: source.repository_full_name,
            commit_sha: source.commit_sha,
            visibility: source.visibility,
            expected_blob_paths: source.expected_blob_paths,
            status: "private_access_pending",
            last_scanned_at: new Date().toISOString(),
            last_error: "hso_github_read_token_not_configured",
            latest_run_id: run.id,
          }, { onConflict: "boundary_key" });
          return {
            boundary_key: source.boundary_key,
            repository_full_name: source.repository_full_name,
            expected_blob_paths: source.expected_blob_paths,
            observed_blob_paths: null,
            status: "private_access_pending",
            error: "hso_github_read_token_not_configured",
          };
        })();
      }
      return scanBoundary(db, source, headers, run.id);
    }));

    let capabilitySummary: any = { plugin_count: 0, capability_count: 0, error: null };
    try {
      capabilitySummary = await upsertCapabilities(db, run.id, privateToken);
    } catch (error) {
      capabilitySummary = { plugin_count: 0, capability_count: 0, error: String((error as any)?.message ?? error) };
    }

    const maxBlobReads = boundedBatchSize(body?.max_blob_reads, 16, 32);
    const blobReadResults = await readBlobBatch(db, headers, maxBlobReads);
    const counts = await Promise.all([
      db.from("hso_migration_paths").select("path", { count: "exact", head: true }),
      db.from("hso_migration_blobs").select("blob_sha", { count: "exact", head: true }),
      db.from("hso_migration_blobs").select("blob_sha", { count: "exact", head: true }).eq("content_status", "verified"),
      db.from("hso_migration_blobs").select("blob_sha", { count: "exact", head: true }).eq("content_status", "pending"),
      db.from("hso_migration_blobs").select("blob_sha", { count: "exact", head: true }).eq("content_status", "failed"),
      db.from("hso_migration_capabilities").select("skill_name", { count: "exact", head: true }),
      db.from("hso_migration_capability_assessments").select("skill_name", { count: "exact", head: true }).eq("acceptance_state", "VERIFIED"),
    ]);
    for (const item of counts) if (item.error) throw new Error("coverage_count_query_failed:" + item.error.message);
    const pathCount = counts[0].count ?? 0;
    const uniqueBlobCount = counts[1].count ?? 0;
    const verifiedCount = counts[2].count ?? 0;
    const pendingCount = counts[3].count ?? 0;
    const failedCount = counts[4].count ?? 0;
    const capabilityCount = counts[5].count ?? 0;
    const acceptedCapabilities = counts[6].count ?? 0;
    const completeTrees = sourceResults.filter((item: any) => item.status === "tree_complete").length;
    const allTreesComplete = completeTrees === SOURCE_BOUNDARIES.length;
    const allContentVerified = uniqueBlobCount > 0 && verifiedCount === uniqueBlobCount;
    const acceptance = migrationAcceptanceState({
      sourceTreesComplete: allTreesComplete,
      allUniqueBlobsVerified: allContentVerified,
      allCapabilitiesParityAccepted: acceptedCapabilities === capabilityCount && capabilityCount > 0,
      allRequiredTestsPassed: false,
      allRuntimeReceiptsPresent: false,
      securityAcceptancePassed: false,
    });
    const pathMetrics = {
      observed_path_rows: pathCount,
      observed_unique_git_blob_shas: uniqueBlobCount,
      duplicate_path_rows: pathCount - uniqueBlobCount,
      content_verified_count: verifiedCount,
      content_pending_count: pendingCount,
      content_failed_count: failedCount,
      content_verified_percent: uniqueBlobCount ? Math.round((verifiedCount / uniqueBlobCount) * 10000) / 100 : 0,
      semantic_review_count: 0,
      semantic_review_state: "NOT_REVIEWED",
      historical_hsar_path_count: PRIOR_HSAR_PATH_COUNT,
      current_direct_github_path_baseline: DIRECT_GITHUB_PATH_COUNT,
      current_direct_github_unique_blob_baseline: DIRECT_GITHUB_UNIQUE_BLOB_COUNT,
      historical_hsar_delta: DIRECT_GITHUB_PATH_COUNT - PRIOR_HSAR_PATH_COUNT,
      hso_l1_count_mismatch: HSO_DIRECT_BLOB_COUNT - HSO_PRIOR_REPORTED_BLOB_COUNT,
      hso_omitted_added_paths: HSO_OMITTED_ADDED_PATHS,
    };
    const summary = {
      trigger_kind: triggerKind,
      source_boundaries: sourceResults,
      source_boundary_count: SOURCE_BOUNDARIES.length,
      complete_tree_count: completeTrees,
      path_metrics: pathMetrics,
      capability_inventory: capabilitySummary,
      blob_read_batch: blobReadResults,
      acceptance_state: acceptance,
      migration_status: "OPEN",
      runtime_invocations_enabled: false,
      public_distribution_enabled: false,
      no_plugin_promoted_to_verified: true,
    };
    const scanState = allTreesComplete && allContentVerified && failedCount === 0 ? "succeeded" : "partial";
    const { error: finishError } = await db.from("hso_migration_runs").update({
      status: scanState,
      finished_at: new Date().toISOString(),
      source_boundary_count: completeTrees,
      path_count: pathCount,
      unique_blob_count: uniqueBlobCount,
      duplicate_path_rows: pathCount - uniqueBlobCount,
      content_verified_count: verifiedCount,
      content_pending_count: pendingCount,
      content_failed_count: failedCount,
      capability_count: capabilityCount,
      accepted_capability_count: acceptedCapabilities,
      summary,
      error_summary: capabilitySummary.error ?? null,
    }).eq("id", run.id);
    if (finishError) throw new Error("run_record_finish_failed:" + finishError.message);
    return response({
      run_id: run.id,
      scan_state: scanState,
      migration_status: "OPEN",
      acceptance_state: acceptance,
      path_metrics: pathMetrics,
      capability_inventory: capabilitySummary,
      source_boundary_count: SOURCE_BOUNDARIES.length,
      complete_tree_count: completeTrees,
      blob_reads_this_run: blobReadResults.length,
      no_plugin_promoted_to_verified: true,
    }, 200);
  } catch (error) {
    const message = String((error as any)?.message ?? error).slice(0, 1000);
    if (runId) await db.from("hso_migration_runs").update({
      status: "failed",
      finished_at: new Date().toISOString(),
      error_summary: message,
      summary: { migration_status: "OPEN", error: message, no_plugin_promoted_to_verified: true },
    }).eq("id", runId);
    return response({ error: "migration_watchdog_failed", run_id: runId, detail: message }, 500);
  } finally {
    try {
      await db.rpc("hso_release_migration_watchdog", { p_lease_token: leaseToken });
    } catch {
      // Lease expiry remains the bounded recovery path if release RPC fails.
    }
  }
});
