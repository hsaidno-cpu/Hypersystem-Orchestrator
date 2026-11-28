import "jsr:@supabase/functions-js/edge-runtime.d.ts";

import { pipeline } from "npm:@supabase/middleware@1";
import { withOAuthProtectedResource, withSupabase } from "npm:@supabase/server@1";
import { McpServer, createMcpHandler } from "npm:@modelcontextprotocol/server@2.1.2";
import * as z from "npm:zod@4.1.13";

const SERVICE_NAME = "pre-kanban-mcp";
const SERVICE_VERSION = "0.1.0";
const encoder = new TextEncoder();
const DEFAULT_COLUMNS = [
  { name: "Backlog", semantic_key: "backlog", color: "gray" },
  { name: "Ready", semantic_key: "ready", color: "blue" },
  { name: "In Progress", semantic_key: "in_progress", color: "yellow" },
  { name: "Blocked", semantic_key: "blocked", color: "red" },
  { name: "Review & Verification", semantic_key: "review", color: "purple" },
  { name: "Done", semantic_key: "done", color: "green" },
];

function json(body: unknown, status = 200, extra: HeadersInit = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...extra },
  });
}

function corsHeaders(origin: string | null): Record<string, string> {
  const headers: Record<string, string> = {
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "authorization, content-type, accept, mcp-protocol-version, mcp-method, mcp-name, last-event-id, x-request-id",
    "access-control-expose-headers": "www-authenticate, mcp-session-id",
    "cache-control": "no-store",
    "vary": "Origin",
  };
  if (origin) headers["access-control-allow-origin"] = origin;
  return headers;
}

function configuredOrigins(): Set<string> {
  return new Set((Deno.env.get("PRE_KANBAN_ALLOWED_ORIGINS") ?? "")
    .split(",").map((value) => value.trim()).filter(Boolean));
}

function originAllowed(origin: string | null): boolean {
  if (!origin) return true;
  return configuredOrigins().has(origin);
}

function configuredOrigins(): Set<string> {
  return new Set((Deno.env.get("PRE_KANBAN_ALLOWED_ORIGINS") ?? "")
    .split(",").map((value) => value.trim()).filter(Boolean));
}

function originAllowed(origin: string | null): boolean {
  if (!origin) return true;
  return configuredOrigins().has(origin);
}

function stableJson(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(stableJson).join(",") + "]";
  const object = value as Record<string, unknown>;
  return "{" + Object.keys(object).sort().map((key) => JSON.stringify(key) + ":" + stableJson(object[key])).join(",") + "}";
}

async function sha256(value: unknown): Promise<string> {
  const bytes = encoder.encode(stableJson(value));
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(hash)].map((item) => item.toString(16).padStart(2, "0")).join("");
}

function ok(value: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(value) }] };
}

function fail(error: unknown) {
  const message = error instanceof Error ? error.message : String(error);
  return {
    isError: true,
    content: [{ type: "text" as const, text: JSON.stringify({ error: "operation_failed", message: message.slice(0, 500) }) }],
  };
}

function requireData<T>(data: T | null, error: any, label = "database_operation_failed"): T {
  if (error) throw new Error(label + ": " + (error.message ?? "unknown database error"));
  if (data === null) throw new Error(label + ": record not found");
  return data;
}

function makeServer(db: any, userId: string) {
  const server = new McpServer({ name: SERVICE_NAME, version: SERVICE_VERSION });

  function register(name: string, description: string, inputSchema: any, handler: (args: any) => Promise<unknown>) {
    server.registerTool(name, { description, inputSchema }, async (args: any) => {
      try {
        return ok(await handler(args));
      } catch (error) {
        return fail(error);
      }
    });
  }

  const uuid = z.string().uuid();
  const shortText = (max = 160) => z.string().trim().min(1).max(max);
  const objectSchema = z.record(z.string(), z.unknown());

  // Workspace bootstrap and membership.
  register("kanban.workspace.list", "List workspaces the authenticated user belongs to.", z.object({}), async () => {
    const { data, error } = await db.from("kanban_workspaces")
      .select("id,name,slug,description,revision,created_at,updated_at").order("name");
    return requireData(data, error);
  });

  register("kanban.workspace.create", "Create a persistent workspace and become its owner.", z.object({
    name: shortText(120),
    slug: z.string().trim().regex(/^[a-z0-9][a-z0-9-]{1,62}$/),
    description: z.string().max(2000).optional(),
  }), async (args) => {
    const { data, error } = await db.from("kanban_workspaces")
      .insert({ name: args.name, slug: args.slug, description: args.description ?? null, created_by: userId })
      .select("id,name,slug,description,created_at").single();
    return requireData(data, error, "workspace_create_failed");
  });

  register("kanban.workspace.add_member", "Add an existing Supabase Auth user to a workspace. Only workspace owners/admins can do this.", z.object({
    workspace_id: uuid,
    user_id: uuid,
    role: z.enum(["admin", "editor", "member", "viewer"]),
  }), async (args) => {
    const { data, error } = await db.from("kanban_workspace_members").upsert({
      workspace_id: args.workspace_id, user_id: args.user_id, role: args.role,
      status: "active", added_by: userId,
    }, { onConflict: "workspace_id,user_id" }).select("id,workspace_id,user_id,role,status").single();
    return requireData(data, error, "workspace_member_upsert_failed");
  });

  // Board Manager.
  register("kanban.board.list", "List boards in a workspace. Archived boards are excluded unless requested.", z.object({
    workspace_id: uuid,
    include_archived: z.boolean().default(false),
  }), async (args) => {
    let query = db.from("kanban_boards")
      .select("id,workspace_id,name,slug,description,position,is_archived,revision,created_at,updated_at")
      .eq("workspace_id", args.workspace_id).order("position").order("name");
    if (!args.include_archived) query = query.eq("is_archived", false);
    const { data, error } = await query;
    return requireData(data, error);
  });

  register("kanban.board.get", "Get a board, its ordered columns, and card count.", z.object({
    board_id: uuid,
  }), async (args) => {
    const { data: board, error } = await db.from("kanban_boards").select("*").eq("id", args.board_id).maybeSingle();
    requireData(board, error, "board_get_failed");
    const [{ data: columns, error: columnsError }, { count, error: countError }] = await Promise.all([
      db.from("kanban_columns").select("*").eq("board_id", args.board_id).order("position"),
      db.from("kanban_cards").select("id", { count: "exact", head: true }).eq("board_id", args.board_id).eq("is_archived", false),
    ]);
    requireData(columns, columnsError, "board_columns_read_failed");
    if (countError) throw new Error("board_card_count_failed: " + countError.message);
    return { board, columns, active_card_count: count ?? 0 };
  });

  register("kanban.board.create", "Create a board and its initial columns in one database transaction.", z.object({
    workspace_id: uuid,
    name: shortText(160),
    slug: z.string().trim().regex(/^[a-z0-9][a-z0-9-]{1,62}$/),
    description: z.string().max(4000).optional(),
    columns: z.array(z.object({
      name: shortText(80),
      semantic_key: z.string().regex(/^[a-z][a-z0-9_-]{1,47}$/),
      color: z.enum(["gray", "blue", "green", "yellow", "orange", "red", "purple", "pink"]).default("gray"),
    })).min(1).max(20).optional(),
  }), async (args) => {
    const { data, error } = await db.rpc("kanban_create_board", {
      p_workspace_id: args.workspace_id, p_name: args.name, p_slug: args.slug,
      p_description: args.description ?? null, p_columns: args.columns ?? DEFAULT_COLUMNS,
    });
    return requireData(data, error, "board_create_failed");
  });

  register("kanban.board.update", "Update board metadata using optimistic revision control.", z.object({
    board_id: uuid,
    expected_revision: z.number().int().positive(),
    name: shortText(160).optional(),
    description: z.string().max(4000).nullable().optional(),
    position: z.number().int().optional(),
    is_archived: z.boolean().optional(),
    metadata: objectSchema.optional(),
  }), async (args) => {
    const patch: Record<string, unknown> = { updated_by: userId };
    for (const key of ["name", "description", "position", "is_archived", "metadata"]) {
      if (args[key] !== undefined) patch[key] = args[key];
    }
    const { data, error } = await db.from("kanban_boards").update(patch)
      .eq("id", args.board_id).eq("revision", args.expected_revision).select("*").maybeSingle();
    if (error) throw new Error("board_update_failed: " + error.message);
    if (!data) throw new Error("revision_conflict: board changed since it was read");
    return data;
  });

  // Column Manager.
  register("kanban.column.list", "List a board's columns in visual order.", z.object({
    board_id: uuid,
    include_archived: z.boolean().default(false),
  }), async (args) => {
    let query = db.from("kanban_columns").select("*").eq("board_id", args.board_id).order("position");
    if (!args.include_archived) query = query.eq("is_archived", false);
    const { data, error } = await query;
    return requireData(data, error);
  });

  register("kanban.column.create", "Create a column in an existing board.", z.object({
    workspace_id: uuid,
    board_id: uuid,
    name: shortText(80),
    semantic_key: z.string().regex(/^[a-z][a-z0-9_-]{1,47}$/),
    position: z.number().int().optional(),
    color: z.enum(["gray", "blue", "green", "yellow", "orange", "red", "purple", "pink"]).default("gray"),
    wip_limit: z.number().int().positive().nullable().optional(),
  }), async (args) => {
    const { data: last, error: lastError } = await db.from("kanban_columns")
      .select("position").eq("board_id", args.board_id).order("position", { ascending: false }).limit(1).maybeSingle();
    if (lastError) throw new Error("column_position_read_failed: " + lastError.message);
    const { data, error } = await db.from("kanban_columns").insert({
      workspace_id: args.workspace_id, board_id: args.board_id, name: args.name,
      semantic_key: args.semantic_key, position: args.position ?? ((last?.position ?? 0) + 1000),
      color: args.color, wip_limit: args.wip_limit ?? null,
    }).select("*").single();
    return requireData(data, error, "column_create_failed");
  });

  register("kanban.column.reorder", "Atomically reorder every active column in a board.", z.object({
    board_id: uuid,
    ordered_column_ids: z.array(uuid).min(1).max(20),
  }), async (args) => {
    const { data, error } = await db.rpc("kanban_reorder_columns", {
      p_board_id: args.board_id, p_column_ids: args.ordered_column_ids,
    });
    return requireData(data, error, "column_reorder_failed");
  });

  // Card Manager.
  register("kanban.card.list", "List cards with optional board, column, priority, text and archive filters.", z.object({
    board_id: uuid,
    column_id: uuid.optional(),
    priority: z.enum(["critical", "high", "medium", "low"]).optional(),
    search: z.string().trim().max(120).optional(),
    include_archived: z.boolean().default(false),
    limit: z.number().int().min(1).max(100).default(50),
  }), async (args) => {
    let query = db.from("kanban_cards").select("*").eq("board_id", args.board_id)
      .order("position").limit(args.limit);
    if (args.column_id) query = query.eq("column_id", args.column_id);
    if (args.priority) query = query.eq("priority", args.priority);
    if (args.search) query = query.ilike("title", "%" + args.search.replace(/[%_]/g, "\\$&") + "%");
    if (!args.include_archived) query = query.eq("is_archived", false);
    const { data, error } = await query;
    return requireData(data, error);
  });

  register("kanban.card.get", "Get one card and its labels.", z.object({ card_id: uuid }), async (args) => {
    const { data: card, error } = await db.from("kanban_cards").select("*").eq("id", args.card_id).maybeSingle();
    requireData(card, error, "card_get_failed");
    const { data: relations, error: labelError } = await db.from("kanban_card_labels")
      .select("label_id,kanban_labels(id,name,color)").eq("card_id", args.card_id);
    requireData(relations, labelError, "card_labels_read_failed");
    return { card, labels: relations };
  });

  register("kanban.card.create", "Create a card atomically under the board lock with revision and WIP controls.", z.object({
    workspace_id: uuid, board_id: uuid, column_id: uuid, title: shortText(240),
    description: z.string().max(12000).optional(),
    priority: z.enum(["critical", "high", "medium", "low"]).default("medium"),
    acceptance_criteria: z.string().max(8000).optional(),
    due_date: z.string().date().optional(),
    metadata: objectSchema.optional(),
  }), async (args) => {
    const { data, error } = await db.rpc("kanban_create_card", {
      p_workspace_id: args.workspace_id,
      p_board_id: args.board_id,
      p_column_id: args.column_id,
      p_title: args.title,
      p_description: args.description ?? null,
      p_priority: args.priority,
      p_acceptance_criteria: args.acceptance_criteria ?? null,
      p_due_date: args.due_date ?? null,
      p_metadata: args.metadata ?? {},
    });
    return requireData(data, error, "card_create_failed");
  });

  register("kanban.card.update", "Update card fields with an expected revision. Column movement is handled by kanban.card.move.", z.object({
    card_id: uuid, expected_revision: z.number().int().positive(),
    title: shortText(240).optional(),
    description: z.string().max(12000).nullable().optional(),
    priority: z.enum(["critical", "high", "medium", "low"]).optional(),
    acceptance_criteria: z.string().max(8000).nullable().optional(),
    due_date: z.string().date().nullable().optional(),
    metadata: objectSchema.optional(),
  }), async (args) => {
    const patch: Record<string, unknown> = { updated_by: userId };
    for (const key of ["title", "description", "priority", "acceptance_criteria", "due_date", "metadata"]) {
      if (args[key] !== undefined) patch[key] = args[key];
    }
    const { data, error } = await db.from("kanban_cards").update(patch)
      .eq("id", args.card_id).eq("revision", args.expected_revision).select("*").maybeSingle();
    if (error) throw new Error("card_update_failed: " + error.message);
    if (!data) throw new Error("revision_conflict: card changed since it was read");
    return data;
  });

  register("kanban.card.move", "Move a card atomically with expected-revision and WIP-limit checks.", z.object({
    card_id: uuid, target_column_id: uuid, expected_revision: z.number().int().positive(),
  }), async (args) => {
    const { data, error } = await db.rpc("kanban_move_card", {
      p_card_id: args.card_id,
      p_target_column_id: args.target_column_id,
      p_expected_revision: args.expected_revision,
    });
    return requireData(data, error, "card_move_failed");
  });

  register("kanban.card.archive", "Archive a card without deleting its history.", z.object({
    card_id: uuid, expected_revision: z.number().int().positive(),
  }), async (args) => {
    const { data, error } = await db.from("kanban_cards").update({
      is_archived: true, archived_at: new Date().toISOString(), updated_by: userId,
    }).eq("id", args.card_id).eq("revision", args.expected_revision).select("*").maybeSingle();
    if (error) throw new Error("card_archive_failed: " + error.message);
    if (!data) throw new Error("revision_conflict: card changed since it was read");
    return data;
  });

  // Label Manager.
  register("kanban.label.create", "Create a board-scoped label.", z.object({
    workspace_id: uuid, board_id: uuid, name: shortText(48),
    color: z.enum(["gray", "blue", "green", "yellow", "orange", "red", "purple", "pink"]).default("gray"),
  }), async (args) => {
    const { data, error } = await db.from("kanban_labels").insert({
      workspace_id: args.workspace_id, board_id: args.board_id, name: args.name,
      color: args.color, created_by: userId,
    }).select("*").single();
    return requireData(data, error, "label_create_failed");
  });

  register("kanban.label.assign", "Assign an existing label to a card. Repeated assignment is idempotent.", z.object({
    workspace_id: uuid, board_id: uuid, card_id: uuid, label_id: uuid,
  }), async (args) => {
    const { data, error } = await db.from("kanban_card_labels").upsert({
      workspace_id: args.workspace_id, board_id: args.board_id, card_id: args.card_id,
      label_id: args.label_id, assigned_by: userId,
    }, { onConflict: "card_id,label_id", ignoreDuplicates: true }).select("*").maybeSingle();
    if (error) throw new Error("label_assign_failed: " + error.message);
    return { assigned: true, relation: data ?? null };
  });

  register("kanban.label.remove", "Remove a label assignment from a card without deleting the label.", z.object({
    card_id: uuid, label_id: uuid,
  }), async (args) => {
    const { error, count } = await db.from("kanban_card_labels")
      .delete({ count: "exact" }).eq("card_id", args.card_id).eq("label_id", args.label_id);
    if (error) throw new Error("label_remove_failed: " + error.message);
    return { removed: (count ?? 0) > 0 };
  });

  // PRE/HSO synchronization. Preview is read-only; apply requires the preview digest and explicit confirmation.
  const syncItemSchema = z.object({
    source_work_item_id: shortText(240),
    source_revision: z.string().max(200).optional(),
    title: shortText(240),
    description: z.string().max(12000).optional(),
    acceptance_criteria: z.string().max(8000).optional(),
    priority: z.enum(["critical", "high", "medium", "low"]).default("medium"),
    column_semantic_key: z.string().regex(/^[a-z][a-z0-9_-]{1,47}$/),
    evidence_refs: z.array(z.string().url()).max(30).default([]),
    dependencies: z.array(z.string().max(240)).max(50).default([]),
    extra: objectSchema.optional(),
  });

  register("kanban.sync.preview", "Build a non-mutating PRE/HSO synchronization plan. Returns a digest required by the apply step.", z.object({
    workspace_id: uuid, board_id: uuid,
    source_system: z.enum(["pre", "hso", "notion", "github"]),
    direction: z.enum(["source_to_board", "bidirectional"]).default("source_to_board"),
    items: z.array(syncItemSchema).min(1).max(100),
  }), async (args) => {
    const ids = args.items.map((item: any) => item.source_work_item_id);
    if (new Set(ids).size !== ids.length) throw new Error("duplicate_source_work_item_id_in_payload");
    const { data: board, error: boardError } = await db.from("kanban_boards")
      .select("id,workspace_id").eq("id", args.board_id).eq("workspace_id", args.workspace_id).maybeSingle();
    requireData(board, boardError, "sync_board_lookup_failed");
    const { data: bindings, error: bindingError } = await db.from("kanban_sync_bindings")
      .select("id,card_id,source_work_item_id,last_source_digest,last_board_revision")
      .eq("workspace_id", args.workspace_id).eq("source_system", args.source_system).in("source_work_item_id", ids);
    requireData(bindings, bindingError, "sync_binding_lookup_failed");
    const bindingMap = new Map((bindings ?? []).map((row: any) => [row.source_work_item_id, row]));
    const planItems: any[] = [];
    for (const item of args.items as any[]) {
      const sourceDigest = await sha256({
        source_work_item_id: item.source_work_item_id, source_revision: item.source_revision ?? null,
        title: item.title, description: item.description ?? null,
        acceptance_criteria: item.acceptance_criteria ?? null, priority: item.priority,
        column_semantic_key: item.column_semantic_key, evidence_refs: item.evidence_refs,
        dependencies: item.dependencies,
      });
      const { data: column, error: columnError } = await db.from("kanban_columns")
        .select("id,semantic_key").eq("board_id", args.board_id)
        .eq("semantic_key", item.column_semantic_key).eq("is_archived", false).maybeSingle();
      if (columnError) throw new Error("sync_column_lookup_failed: " + columnError.message);
      if (!column) {
        planItems.push({ action: "CONFLICT", reason: "target_column_not_found", ...item, source_digest: sourceDigest });
        continue;
      }
      const binding = bindingMap.get(item.source_work_item_id) as any;
      if (!binding) {
        planItems.push({ action: "CREATE", reason: "no_existing_binding", ...item, source_digest: sourceDigest, column_id: column.id });
        continue;
      }
      const { data: card, error: cardError } = await db.from("kanban_cards")
        .select("id,revision,is_archived").eq("id", binding.card_id).maybeSingle();
      if (cardError) throw new Error("sync_card_lookup_failed: " + cardError.message);
      if (!card || card.is_archived) {
        planItems.push({ action: "CONFLICT", reason: "bound_card_missing_or_archived", ...item, source_digest: sourceDigest });
      } else if (binding.last_source_digest === sourceDigest) {
        planItems.push({ action: "NOOP", reason: "source_digest_unchanged", ...item, source_digest: sourceDigest, card_id: card.id });
      } else if (card.revision !== binding.last_board_revision) {
        planItems.push({ action: "CONFLICT", reason: "board_card_changed_since_last_sync", ...item, source_digest: sourceDigest, card_id: card.id, current_revision: card.revision });
      } else {
        planItems.push({ action: "UPDATE", reason: "source_changed_board_unchanged", ...item, source_digest: sourceDigest, card_id: card.id, expected_revision: card.revision, column_id: column.id, binding_id: binding.id });
      }
    }
    const preview = {
      workspace_id: args.workspace_id, board_id: args.board_id, source_system: args.source_system,
      direction: args.direction, items: planItems,
    };
    const digest = await sha256(preview);
    const counts = planItems.reduce((acc: Record<string, number>, item: any) => {
      acc[item.action] = (acc[item.action] ?? 0) + 1;
      return acc;
    }, {});
    const { data: run, error: runError } = await db.from("kanban_sync_runs").insert({
      workspace_id: args.workspace_id, board_id: args.board_id, source_system: args.source_system,
      direction: args.direction, status: "PREVIEWED", payload_digest: digest,
      preview_plan: preview, source_count: planItems.length, initiated_by: userId,
      expires_at: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
    }).select("id,status,payload_digest,source_count,expires_at,created_at").single();
    requireData(run, runError, "sync_preview_persist_failed");
    return { run, counts, plan: planItems };
  });

  register("kanban.sync.apply", "Apply a stored sync preview only when its digest matches and confirm_apply=true. Repeated apply is idempotent.", z.object({
    sync_run_id: uuid,
    expected_preview_digest: z.string().regex(/^[a-f0-9]{64}$/),
    confirm_apply: z.literal(true),
  }), async (args) => {
    const { data: run, error: runError } = await db.from("kanban_sync_runs")
      .select("*").eq("id", args.sync_run_id).maybeSingle();
    requireData(run, runError, "sync_run_lookup_failed");
    const previousFailures = Number(run.result_summary?.failed ?? 0);
    if (run.status === "APPLIED" || (run.status === "PARTIAL" && previousFailures === 0)) {
      return { run_id: run.id, status: run.status, idempotent_replay: true, result: run.result_summary };
    }
    if (run.status !== "PREVIEWED") throw new Error("sync_run_not_applicable:" + run.status);
    if (run.payload_digest !== args.expected_preview_digest) throw new Error("preview_digest_mismatch");
    if (Date.parse(run.expires_at) <= Date.now()) {
      await db.from("kanban_sync_runs").update({ status: "EXPIRED" }).eq("id", run.id);
      throw new Error("sync_preview_expired");
    }
    const planItems = run.preview_plan?.items;
    if (!Array.isArray(planItems)) throw new Error("stored_sync_plan_invalid");
    const { data: claimed, error: beginError } = await db.rpc("kanban_claim_sync_run", {
      p_sync_run_id: run.id,
      p_expected_digest: args.expected_preview_digest,
    });
    if (beginError) throw new Error("sync_run_claim_failed: " + beginError.message);
    if (!claimed || claimed.status !== "APPLYING") throw new Error("sync_run_claim_not_acquired");
    // The database claim uses SELECT FOR UPDATE to prevent concurrent duplicate applies.

    let created = 0, updated = 0, noop = 0, conflicts = 0, failed = 0;
    const outcomes: any[] = [];
    for (const item of planItems) {
      try {
        if (item.action === "NOOP") { noop++; outcomes.push({ source_work_item_id: item.source_work_item_id, disposition: "NOOP" }); continue; }
        if (item.action === "CONFLICT") { conflicts++; outcomes.push({ source_work_item_id: item.source_work_item_id, disposition: "CONFLICT", reason: item.reason }); continue; }
        const { data: applied, error: applyError } = await db.rpc("kanban_apply_sync_item", {
          p_sync_run_id: run.id,
          p_item_payload: item,
        });
        if (applyError) throw new Error("sync_item_apply_failed: " + applyError.message);
        if (!applied) throw new Error("sync_item_apply_returned_empty_result");
        if (applied.disposition === "CREATED") created++;
        else if (applied.disposition === "UPDATED") updated++;
        else if (applied.disposition === "NOOP") noop++;
        else if (applied.disposition === "CONFLICT") conflicts++;
        else throw new Error("sync_item_unrecognized_disposition");
        outcomes.push({ source_work_item_id: item.source_work_item_id, ...applied });
      } catch (error) {
        failed++;
        outcomes.push({ source_work_item_id: item.source_work_item_id, disposition: "FAILED", reason: String(error).slice(0, 300) });
      }
    }
    const status = conflicts || failed ? "PARTIAL" : "APPLIED";
    const summary = { created, updated, noop, conflicts, failed, outcomes };
    const { error: finishError } = await db.from("kanban_sync_runs").update({
      status, applied_count: created + updated, conflict_count: conflicts,
      result_summary: summary, applied_at: new Date().toISOString(),
    }).eq("id", run.id);
    if (finishError) throw new Error("sync_run_finalize_failed: " + finishError.message);
    return { run_id: run.id, status, ...summary };
  });

  register("kanban.sync.read_back", "Read back persisted cards and bindings for a sync run and compare source digest and recorded board revision.", z.object({
    sync_run_id: uuid,
  }), async (args) => {
    const { data: run, error } = await db.from("kanban_sync_runs").select("*").eq("id", args.sync_run_id).maybeSingle();
    requireData(run, error, "sync_run_lookup_failed");
    const planItems = run.preview_plan?.items ?? [];
    const ids = planItems.filter((item: any) => ["CREATE", "UPDATE", "NOOP"].includes(item.action))
      .map((item: any) => item.source_work_item_id);
    if (!ids.length) return { run_id: run.id, verified: true, checked: 0, issues: [] };
    const { data: bindings, error: bindingError } = await db.from("kanban_sync_bindings")
      .select("source_work_item_id,card_id,last_source_digest,last_board_revision")
      .eq("workspace_id", run.workspace_id).eq("source_system", run.source_system).in("source_work_item_id", ids);
    requireData(bindings, bindingError, "sync_binding_read_back_failed");
    const bindingMap = new Map((bindings ?? []).map((row: any) => [row.source_work_item_id, row]));
    const issues: any[] = [];
    for (const item of planItems) {
      if (!["CREATE", "UPDATE", "NOOP"].includes(item.action)) continue;
      const binding = bindingMap.get(item.source_work_item_id) as any;
      if (!binding) { issues.push({ source_work_item_id: item.source_work_item_id, reason: "binding_missing" }); continue; }
      if (binding.last_source_digest !== item.source_digest) {
        issues.push({ source_work_item_id: item.source_work_item_id, reason: "source_digest_mismatch" }); continue;
      }
      const { data: card, error: cardError } = await db.from("kanban_cards")
        .select("id,revision,is_archived").eq("id", binding.card_id).maybeSingle();
      if (cardError || !card || card.is_archived) {
        issues.push({ source_work_item_id: item.source_work_item_id, reason: "card_missing_or_unreadable" }); continue;
      }
      if (card.revision !== binding.last_board_revision) {
        issues.push({ source_work_item_id: item.source_work_item_id, reason: "board_changed_after_sync", expected_revision: binding.last_board_revision, actual_revision: card.revision });
      }
    }
    const verified = issues.length === 0;
    const { error: eventError } = await db.from("kanban_sync_events").insert({
      workspace_id: run.workspace_id, sync_run_id: run.id, source_system: run.source_system,
      event_type: "READ_BACK", disposition: verified ? "READ_BACK_PASS" : "READ_BACK_FAIL",
      details: { checked: ids.length, issue_count: issues.length }, actor_user_id: userId,
    });
    if (eventError) throw new Error("sync_read_back_event_failed: " + eventError.message);
    return { run_id: run.id, verified, checked: ids.length, issues };
  });

  // Reverse synchronization: board edits are captured by a Postgres outbox trigger
  // when the binding is bidirectional. The PRE adapter applies and reads back the change,
  // then acknowledges the event with its source revision and receipt locator.
  register("kanban.sync.outbox.list", "List pending or historical board-to-PRE/HSO changes for a workspace.", z.object({
    workspace_id: uuid,
    status: z.enum(["PENDING", "ACKNOWLEDGED", "CONFLICT", "DEAD_LETTER"]).optional(),
    limit: z.number().int().min(1).max(100).default(50),
  }), async (args) => {
    let query = db.from("kanban_sync_outbox").select("*")
      .eq("workspace_id", args.workspace_id).order("created_at", { ascending: true })
      .limit(args.limit);
    if (args.status) query = query.eq("status", args.status);
    const { data, error } = await query;
    return requireData(data, error, "sync_outbox_list_failed");
  });

  register("kanban.sync.outbox.acknowledge", "Acknowledge a board-originated change only after the PRE/HSO adapter has applied it and read the canonical source back.", z.object({
    outbox_id: uuid,
    expected_card_revision: z.number().int().positive(),
    resulting_source_revision: z.string().min(1).max(240),
    source_readback_ref: z.string().url().refine((value: string) => value.startsWith("https://"), "HTTPS receipt URL required"),
    source_readback_digest: z.string().regex(/^[a-f0-9]{64}$/),
  }), async (args) => {
    const { data, error } = await db.rpc("kanban_ack_sync_outbox", {
      p_outbox_id: args.outbox_id,
      p_expected_card_revision: args.expected_card_revision,
      p_resulting_source_revision: args.resulting_source_revision,
      p_source_readback_ref: args.source_readback_ref,
      p_source_readback_digest: args.source_readback_digest,
    });
    return requireData(data, error, "sync_outbox_acknowledge_failed");
  });

  register("kanban.sync.outbox.conflict", "Mark an outbound change as conflicted when the canonical source has diverged; preserves the item for reconciliation.", z.object({
    outbox_id: uuid,
    reason: shortText(500),
  }), async (args) => {
    const { data, error } = await db.from("kanban_sync_outbox").update({
      status: "CONFLICT",
      last_error: args.reason,
    }).eq("id", args.outbox_id).eq("status", "PENDING")
      .select("id,status,last_error").maybeSingle();
    if (error) throw new Error("sync_outbox_conflict_update_failed: " + error.message);
    if (!data) throw new Error("outbox_item_not_pending_or_missing");
    return data;
  });

  // Audit Manager.
  register("kanban.audit.list", "List append-only workspace audit metadata. Only workspace owners/admins can read it.", z.object({
    workspace_id: uuid,
    before: z.string().datetime().optional(),
    limit: z.number().int().min(1).max(100).default(50),
  }), async (args) => {
    let query = db.from("kanban_audit_events").select("*")
      .eq("workspace_id", args.workspace_id).order("created_at", { ascending: false }).limit(args.limit);
    if (args.before) query = query.lt("created_at", args.before);
    const { data, error } = await query;
    return requireData(data, error, "audit_list_failed");
  });

  register("kanban.audit.get", "Get one audit event by ID.", z.object({
    audit_event_id: uuid,
  }), async (args) => {
    const { data, error } = await db.from("kanban_audit_events").select("*")
      .eq("id", args.audit_event_id).maybeSingle();
    return requireData(data, error, "audit_get_failed");
  });

  register("kanban.sync.status", "Get recent synchronization runs for a workspace.", z.object({
    workspace_id: uuid,
    limit: z.number().int().min(1).max(50).default(10),
  }), async (args) => {
    const { data, error } = await db.from("kanban_sync_runs").select(
      "id,board_id,source_system,direction,status,payload_digest,source_count,applied_count,conflict_count,result_summary,created_at,applied_at"
    ).eq("workspace_id", args.workspace_id).order("created_at", { ascending: false }).limit(args.limit);
    return requireData(data, error, "sync_status_failed");
  });

  return server;
}

const mcpHandler = pipeline(
  [withOAuthProtectedResource(), withSupabase({ auth: "user" })],
  async (request: Request, context: any) => {
    const url = new URL(request.url);
    const path = url.pathname.endsWith("/") ? url.pathname.slice(0, -1) : url.pathname;
    if (!path.endsWith("/mcp")) return json({ error: "not_found" }, 404);

    const userId = String(context.userClaims?.id ?? context.userClaims?.sub ?? "");
    if (!userId) return json({ error: "authenticated_user_claim_missing" }, 401);

    const handler = createMcpHandler(
      () => makeServer(context.supabase, userId),
      { legacy: "stateless" },
    );
    return handler.fetch(request);
  },
);

Deno.serve(async (request: Request) => {
  const origin = request.headers.get("origin");
  const cors = corsHeaders(origin);
  if (!originAllowed(origin)) return json({ error: "origin_not_allowed" }, 403, cors);
  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

  const requestPath = new URL(request.url).pathname;
  const path = requestPath.endsWith("/") ? requestPath.slice(0, -1) : requestPath;
  if (request.method === "GET" && path.endsWith("/health")) {
    return json({
      service: SERVICE_NAME,
      version: SERVICE_VERSION,
      status: "READY_FOR_AUTHENTICATED_REQUESTS",
      authentication: "SUPABASE_AUTH_OAUTH_USER_JWT",
      authorization: "ROW_LEVEL_SECURITY",
      persistence: "SUPABASE_POSTGRES",
      mcp_path: path.slice(0, path.length - "/health".length) + "/mcp",
    }, 200, cors);
  }

  if (request.method !== "POST" && request.method !== "GET" && request.method !== "DELETE") {
    return json({ error: "method_not_allowed" }, 405, cors);
  }

  const response = await mcpHandler(request);
  const headers = new Headers(response.headers);
  for (const [key, value] of Object.entries(cors)) headers.set(key, value);
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
});
