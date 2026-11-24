import { createClient } from "npm:@supabase/supabase-js@2.57.0";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type, x-hso-signature, x-hso-delivery, x-hso-event, x-hub-signature-256, x-github-delivery, x-github-event",
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

  const raw = await req.text();
  const hsoSecret = Deno.env.get("HSO_SYNC_TOKEN");
  const githubSecret = Deno.env.get("GITHUB_WEBHOOK_SECRET");
  const hsoSig = (req.headers.get("x-hso-signature") ?? "").replace(/^sha256=/i, "").trim().toLowerCase();
  const githubSig = (req.headers.get("x-hub-signature-256") ?? "").replace(/^sha256=/i, "").trim().toLowerCase();
  let valid = false;
  if (hsoSecret && hsoSig) valid = safeEqual(hsoSig, await hmacHex(hsoSecret, raw));
  if (!valid && githubSecret && githubSig) valid = safeEqual(githubSig, await hmacHex(githubSecret, raw));
  if (!valid) return Response.json({ error: "invalid_signature" }, { status: 401, headers: cors });

  let event: Record<string, any>;
  try { event = JSON.parse(raw); } catch { return Response.json({ error: "invalid_json" }, { status: 400, headers: cors }); }

  const delivery = req.headers.get("x-github-delivery") ?? req.headers.get("x-hso-delivery");
  const eventType = req.headers.get("x-github-event") ?? req.headers.get("x-hso-event") ?? "repository_event";
  if (!delivery) return Response.json({ error: "delivery_id_required" }, { status: 400, headers: cors });

  const compact = compactPayload(event);
  const payloadHash = await hmacHex(hsoSecret ?? githubSecret ?? "", JSON.stringify(compact));
  const supabase = createClient(url, serviceKey, { auth: { persistSession: false } });
  const { error } = await supabase.from("hso_integration_events").upsert({
    provider: "github",
    delivery_id: delivery,
    event_type: eventType,
    external_subject: compact.repository.full_name ?? null,
    payload_hash: payloadHash,
    payload: compact,
    processing_state: "received",
  }, { onConflict: "provider,delivery_id", ignoreDuplicates: true });
  if (error) return Response.json({ error: "event_store_failed", detail: error.message }, { status: 500, headers: cors });

  await supabase.from("hso_sources").update({
    last_event_at: new Date().toISOString(), status: "connected", last_error: null, updated_at: new Date().toISOString(),
  }).eq("source_key", "github-hso-parent");
  return Response.json({ accepted: true, provider: "github", delivery_id: delivery }, { status: 202, headers: cors });
});
