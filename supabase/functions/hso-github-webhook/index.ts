import { createClient } from "npm:@supabase/supabase-js@2.57.0";
import { verifyGitHubActionsOidc } from "../_shared/github_oidc.ts";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type, authorization, x-hso-signature, x-hso-delivery, x-hso-event, x-hub-signature-256, x-github-delivery, x-github-event",
  "access-control-allow-methods": "POST, OPTIONS",
};

async function hmacHex(secret: string, raw: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"],
  );
  const out = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(raw));
  return [...new Uint8Array(out)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return result === 0;
}
async function sha256Hex(value: string): Promise<string> {
  const bytes = new TextEncoder().encode(value);
  const copy = new ArrayBuffer(bytes.byteLength);
  new Uint8Array(copy).set(bytes);
  const digest = await crypto.subtle.digest("SHA-256", copy);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function resolveVaultSecret(supabase: any, name: string): Promise<string | null> {
  const { data, error } = await supabase.rpc("pre_federation_get_secret", { secret_name: name });
  if (error) {
    console.error("vault_secret_lookup_failed", { name, message: error.message });
    return null;
  }
  return typeof data === "string" && data.length > 0 ? data : null;
}

function compactPayload(event: Record<string, any>) {
  const repo = event.repository ?? {};
  const pr = event.pull_request ?? {};
  const run = event.workflow_run ?? {};
  return {
    action: event.action ?? null,
    repository: { full_name: repo.full_name ?? null, html_url: repo.html_url ?? null },
    ref: event.ref ?? null,
    before: event.before ?? null,
    after: event.after ?? null,
    number: event.number ?? null,
    pull_request: Object.keys(pr).length ? {
      number: pr.number ?? null, title: pr.title ?? null, html_url: pr.html_url ?? null,
      state: pr.state ?? null, head_sha: pr.head?.sha ?? null, base_ref: pr.base?.ref ?? null,
    } : null,
    workflow_run: Object.keys(run).length ? {
      id: run.id ?? null, name: run.name ?? null, html_url: run.html_url ?? null,
      head_sha: run.head_sha ?? null, conclusion: run.conclusion ?? null,
      status: run.status ?? null, event: run.event ?? null,
    } : null,
    sender: event.sender?.login ?? null,
  };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return Response.json({ error: "method_not_allowed" }, { status: 405, headers: cors });

  const url = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !serviceKey) return Response.json({ error: "integration_not_configured" }, { status: 503, headers: cors });

  const supabase = createClient(url, serviceKey, { auth: { persistSession: false } });
  const hsoSecret = await resolveVaultSecret(supabase, "HSO_SYNC_TOKEN") ?? Deno.env.get("HSO_SYNC_TOKEN") ?? null;
  const githubSecret = Deno.env.get("GITHUB_WEBHOOK_SECRET");
  const raw = await req.text();
  const eventType = req.headers.get("x-github-event") ?? req.headers.get("x-hso-event") ?? "repository_event";
  const delivery = req.headers.get("x-github-delivery") ?? req.headers.get("x-hso-delivery");
  if (!delivery || delivery.length > 200) return Response.json({ error: "delivery_id_required_or_invalid" }, { status: 400, headers: cors });

  const oidcClaims = await verifyGitHubActionsOidc(req, {
    audience: url + "/functions/v1/hso-github-webhook",
    repository: "hsaidno-cpu/Hypersystem-Orchestrator",
    repositoryId: "1467501661",
    workflowRef: "hsaidno-cpu/Hypersystem-Orchestrator/.github/workflows/hso-mission-control-sync.yml@refs/heads/main",
    allowedEvents: ["push", "pull_request_target", "workflow_run"],
  });
  const oidcAuthenticated = Boolean(oidcClaims && oidcClaims.event_name === eventType);
  const hsoSig = (req.headers.get("x-hso-signature") ?? "").replace(/^sha256=/i, "").trim().toLowerCase();
  const githubSig = (req.headers.get("x-hub-signature-256") ?? "").replace(/^sha256=/i, "").trim().toLowerCase();
  const hsoHmacAuthenticated = Boolean(hsoSecret && hsoSig && safeEqual(hsoSig, await hmacHex(hsoSecret, raw)));
  const githubHmacAuthenticated = Boolean(githubSecret && githubSig && safeEqual(githubSig, await hmacHex(githubSecret, raw)));
  if (!oidcAuthenticated && !hsoHmacAuthenticated && !githubHmacAuthenticated) {
    return Response.json({ error: "authentication_failed" }, { status: 401, headers: cors });
  }

  let event: Record<string, any>;
  try { event = JSON.parse(raw); } catch { return Response.json({ error: "invalid_json" }, { status: 400, headers: cors }); }

  const compact = compactPayload(event);
  const payloadHash = await sha256Hex(JSON.stringify(compact));
  const { data: insertedEvents, error } = await supabase.from("hso_integration_events").upsert({
    provider: "github",
    delivery_id: delivery,
    event_type: eventType,
    external_subject: compact.repository.full_name ?? null,
    payload_hash: payloadHash,
    payload: compact,
    processing_state: "received",
  }, { onConflict: "provider,delivery_id", ignoreDuplicates: true }).select("id");
  if (error) return Response.json({ error: "event_store_failed", detail: error.message }, { status: 500, headers: cors });
  const duplicateDelivery = !insertedEvents || insertedEvents.length === 0;

  const failedCi = eventType === "workflow_run" && compact.workflow_run?.conclusion === "failure";
  const pullRequestChanged = eventType === "pull_request";
  const changeTitle = failedCi
    ? "CI failed: " + (compact.workflow_run?.name ?? "workflow")
    : pullRequestChanged
      ? "Pull request changed: " + (compact.pull_request?.title ?? ("#" + compact.number))
      : "GitHub event: " + eventType;
  const changeImpact = failedCi ? "HIGH" : pullRequestChanged ? "MEDIUM" : "UNKNOWN";
  const changeFollowUp = failedCi ? "INVESTIGATE_AND_RECOMPUTE" : pullRequestChanged ? "REVALIDATE_EXACT_HEAD" : "RECONCILE";
  const { error: changeError } = await supabase.from("hso_change_events").upsert({
    provider: "github",
    delivery_id: delivery,
    event_type: eventType,
    external_subject: compact.repository.full_name ?? null,
    title: changeTitle,
    impact: changeImpact,
    follow_up: changeFollowUp,
    before_state: {},
    after_state: compact,
    source_url: compact.pull_request?.html_url ?? compact.workflow_run?.html_url ?? compact.repository.html_url,
    event_at: new Date().toISOString()
  }, { onConflict: "provider,delivery_id", ignoreDuplicates: true });
  if (changeError) return Response.json({ error: "change_event_store_failed", detail: changeError.message }, { status: 500, headers: cors });

  const { error: sourceError } = await supabase.from("hso_sources").update({
    last_event_at: new Date().toISOString(), updated_at: new Date().toISOString(),
  }).eq("source_key", "github-hso-parent");
  if (sourceError) return Response.json({ error: "source_event_update_failed", detail: sourceError.message }, { status: 500, headers: cors });
  // Trigger near-real-time source reconciliation after event intake.
  let syncTriggered = false;
  const syncToken = hsoSecret;
  if (syncToken) {
    try {
      const syncResponse = await fetch(url + "/functions/v1/hso-reconcile", {
        method: "POST",
        headers: { "content-type": "application/json", "x-hso-sync-token": syncToken },
        body: JSON.stringify({ trigger_kind: "webhook", provider: "github", delivery_id: delivery }),
        signal: AbortSignal.timeout(55000),
      });
      syncTriggered = syncResponse.ok;
    } catch { /* Event is persisted; scheduled reconciliation is the recovery path. */ }
  }

  return Response.json({ accepted: true, provider: "github", delivery_id: delivery, duplicate: duplicateDelivery, oidc_authenticated: oidcAuthenticated, sync_triggered: syncTriggered }, { status: 202, headers: cors });
});
