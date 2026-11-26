import { createClient } from "npm:@supabase/supabase-js@2.57.0";
import {
  constantTimeEqual,
  isFreshSlackTimestamp,
  parseHsoCommand,
  redactLikelySecrets,
  slackSignature,
} from "./core.ts";

const MAX_BODY_BYTES = 32 * 1024;
const corsHeaders = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type, x-slack-request-timestamp, x-slack-signature",
  "access-control-allow-methods": "POST, OPTIONS",
  "cache-control": "no-store",
};

function response(body: Record<string, unknown>, status = 200) {
  return Response.json(body, { status, headers: corsHeaders });
}

async function sha256(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function slackText(text: string) {
  return { response_type: "ephemeral", text };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return response({ error: "method_not_allowed" }, 405);

  const signingSecret = Deno.env.get("SLACK_SIGNING_SECRET") ?? "";
  const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
  if (!signingSecret || !supabaseUrl || !serviceRoleKey) {
    return response({ error: "gateway_not_configured" }, 503);
  }

  const declaredLength = Number(req.headers.get("content-length") ?? "0");
  if (declaredLength > MAX_BODY_BYTES) return response({ error: "payload_too_large" }, 413);
  const rawBody = await req.text();
  if (new TextEncoder().encode(rawBody).length > MAX_BODY_BYTES) {
    return response({ error: "payload_too_large" }, 413);
  }

  const timestamp = req.headers.get("x-slack-request-timestamp") ?? "";
  const suppliedSignature = req.headers.get("x-slack-signature") ?? "";
  if (!isFreshSlackTimestamp(timestamp)) return response({ error: "stale_or_invalid_timestamp" }, 401);
  const expectedSignature = await slackSignature(signingSecret, timestamp, rawBody);
  if (!constantTimeEqual(suppliedSignature, expectedSignature)) {
    return response({ error: "invalid_signature" }, 401);
  }

  const contentType = (req.headers.get("content-type") ?? "").toLowerCase();
  if (!contentType.includes("application/x-www-form-urlencoded")) {
    return response({ error: "unsupported_content_type" }, 415);
  }

  const form = new URLSearchParams(rawBody);
  const command = form.get("command") ?? "";
  const teamId = form.get("team_id") ?? "";
  const channelId = form.get("channel_id") ?? "";
  const userId = form.get("user_id") ?? "";
  const triggerId = form.get("trigger_id") ?? "";
  const text = form.get("text") ?? "";

  if (command !== "/hso") return response(slackText("This endpoint only accepts the /hso command."), 200);
  if (!teamId || !channelId || !userId || !triggerId) {
    return response(slackText("Request rejected: Slack identity/context fields are incomplete."), 200);
  }

  const allowedTeam = Deno.env.get("HSO_SLACK_TEAM_ID") ?? "";
  const allowedChannel = Deno.env.get("HSO_SLACK_CONTROL_CHANNEL_ID") ?? "";
  const gov01UserId = Deno.env.get("HSO_GOV01_SLACK_USER_ID") ?? "";
  if (!allowedTeam || !allowedChannel || !gov01UserId) {
    return response(slackText("HSO control ingress is signed but not yet provisioned. No command was executed."), 200);
  }
  if (teamId !== allowedTeam || channelId !== allowedChannel || userId !== gov01UserId) {
    return response(slackText("Access denied. This command is restricted to the registered GOV-01 identity in the HSO control room."), 200);
  }

  const parsed = parseHsoCommand(text);
  if (!parsed) {
    return response(slackText(
      "Usage: /hso status|help|instruction <brief>|priority <item> <priority>|pause <scope>|stop <run-id>|freeze <reason>|resume <scope>",
    ), 200);
  }

  const db = createClient(supabaseUrl, serviceRoleKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  if (parsed.name === "help") {
    return response(slackText(
      "/hso status reads the current sync baseline.\n" +
      "/hso instruction <brief> records a work request for HSO planning.\n" +
      "/hso priority <item> <priority> records a priority-change request.\n" +
      "/hso pause <scope>, /hso stop <run-id>, /hso freeze <reason>, /hso resume <scope> record operational control requests.\n\n" +
      "Execution and approval are separate gates. This ingress does not execute repository changes or issue approval receipts.",
    ), 200);
  }

  if (parsed.name === "status") {
    const [sourcesResult, runResult, commandResult] = await Promise.all([
      db.from("hso_sources")
        .select("source_key,status,last_success_at,last_error")
        .eq("enabled", true)
        .order("source_key"),
      db.from("hso_sync_runs")
        .select("id,status,trigger_kind,started_at,finished_at,records_seen,records_upserted,error_summary")
        .order("started_at", { ascending: false })
        .limit(1)
        .maybeSingle(),
      db.from("hso_slack_commands")
        .select("id,state,received_at")
        .order("received_at", { ascending: false })
        .limit(1)
        .maybeSingle(),
    ]);
    if (sourcesResult.error || runResult.error || commandResult.error) {
      return response(slackText("HSO status read failed. No operational state was changed."), 200);
    }
    const sourceLines = (sourcesResult.data ?? []).map((source) =>
      "• " + source.source_key + ": " + source.status +
      (source.last_success_at ? " (last success " + source.last_success_at + ")" : "")
    );
    const latest = runResult.data
      ? runResult.data.status + " / " + runResult.data.trigger_kind + " / " + runResult.data.started_at
      : "none recorded";
    const lastCommand = commandResult.data
      ? commandResult.data.id + " / " + commandResult.data.state
      : "none recorded";
    return response(slackText(
      "*HSO live sync status*\n" +
      "Latest sync run: " + latest + "\n" +
      "Latest Slack command: " + lastCommand + "\n" +
      "Sources:\n" + (sourceLines.join("\n") || "• none") + "\n\n" +
      "This is a read-only status snapshot. It is not proof of a successful scheduled run or live Notion/GitHub write.",
    ), 200);
  }

  if (["approve", "reject", "hold"].includes(parsed.name)) {
    return response(slackText(
      "Approval commands are disabled. HSO must first issue and validate a HAP-01 receipt bound to Action ID, operation, scope, base/head SHA, evidence digest, expiry and one-time nonce. No approval decision was recorded.",
    ), 200);
  }

  if (Deno.env.get("HSO_COMMAND_RECEIVE_ENABLED") !== "true") {
    return response(slackText("Command intake is disabled until GOV-01 identity and Slack signing configuration are provisioned. No command was stored."), 200);
  }

  const safeArguments = redactLikelySecrets(parsed.arguments);
  const requestHash = await sha256(JSON.stringify({
    team_id: teamId,
    channel_id: channelId,
    user_id: userId,
    command: parsed.name,
    arguments: safeArguments,
  }));

  const receivedAt = new Date().toISOString();
  const { data: enqueueData, error: enqueueError } = await db.rpc(
    "hso_enqueue_slack_command",
    {
      p_team_id: teamId,
      p_channel_id: channelId,
      p_actor_slack_user_id: userId,
      p_trigger_id: triggerId,
      p_command_name: parsed.name,
      p_arguments: safeArguments,
      p_request_sha256: requestHash,
      p_received_at: receivedAt,
    },
  );
  const created = Array.isArray(enqueueData) ? enqueueData[0] : enqueueData;

  if (enqueueError) {
    if (enqueueError.code === "23505") {
      const { data: existing } = await db.from("hso_slack_commands")
        .select("id,state,request_sha256")
        .eq("team_id", teamId)
        .eq("trigger_id", triggerId)
        .maybeSingle();
      if (existing?.request_sha256 === requestHash) {
        return response(slackText(
          "Duplicate delivery safely deduplicated. Command " + existing.id + " remains " + existing.state + ".",
        ), 200);
      }
      return response(slackText(
        "Duplicate trigger identifier with a different payload rejected. No second command was created.",
      ), 200);
    }
    return response(slackText(
      "Atomic command persistence failed. No command/outbox/audit partial write was committed; HSO did not execute it.",
    ), 200);
  }

  if (!created?.command_id || !created?.outbox_id) {
    return response(slackText(
      "Command persistence returned an incomplete receipt. Treating this request as blocked; no dispatch was performed.",
    ), 200);
  }

  return response(slackText(
    "Command " + created.command_id + " recorded as *pending_worker*.\n" +
    "Outbox item: " + created.outbox_id + "\n" +
    "Dispatch enabled: *no* (v1 has no live command worker).\n" +
    "Command, outbox and ingress audit were committed atomically. No repository, Notion, Supabase business-state or worker operation was executed by this ingress.",
  ), 200);
});
