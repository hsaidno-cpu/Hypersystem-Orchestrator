import { createClient } from "npm:@supabase/supabase-js@2.57.0";

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type, x-notion-signature",
  "access-control-allow-methods": "POST, OPTIONS",
};

async function hmacHex(secret: string, body: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  return [...new Uint8Array(signature)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return result === 0;
}

function isVerificationChallenge(event: Record<string, unknown>): event is Record<string, unknown> & { verification_token: string } {
  return typeof event.verification_token === "string"
    && event.verification_token.length >= 16
    && event.verification_token.length <= 512
    && !("id" in event)
    && !("event_id" in event)
    && !("type" in event);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return Response.json({ error: "method_not_allowed" }, { status: 405, headers: cors });

  const url = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !serviceKey) {
    return Response.json({ error: "integration_not_configured" }, { status: 503, headers: cors });
  }

  const raw = await req.text();
  let event: Record<string, unknown>;
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return Response.json({ error: "invalid_payload" }, { status: 400, headers: cors });
    }
    event = parsed as Record<string, unknown>;
  } catch {
    return Response.json({ error: "invalid_json" }, { status: 400, headers: cors });
  }

  const supabase = createClient(url, serviceKey, { auth: { persistSession: false } });
  const envSecret = Deno.env.get("NOTION_WEBHOOK_VERIFICATION_TOKEN");

  // Notion's initial subscription challenge is an unsigned one-time POST containing
  // only verification_token. Store it once in Vault; do not log or echo the secret.
  if (isVerificationChallenge(event)) {
    if (envSecret && !safeEqual(envSecret, event.verification_token)) {
      return Response.json({ error: "verification_token_conflict" }, { status: 409, headers: cors });
    }
    const { error } = await supabase.rpc("hso_register_notion_webhook_verification_token", {
      p_token: event.verification_token,
    });
    if (error) {
      const conflict = String(error.code ?? "") === "23505";
      return Response.json(
        { error: conflict ? "verification_token_already_registered" : "verification_token_store_failed" },
        { status: conflict ? 409 : 500, headers: cors },
      );
    }
    return Response.json({ verification_token_received: true }, { status: 200, headers: cors });
  }

  let secret = envSecret ?? "";
  if (!secret) {
    const { data, error } = await supabase.rpc("hso_get_notion_webhook_verification_token");
    if (error) {
      return Response.json({ error: "verification_token_lookup_failed" }, { status: 500, headers: cors });
    }
    secret = typeof data === "string" ? data : "";
  }
  if (!secret) {
    return Response.json({ error: "verification_token_not_configured" }, { status: 503, headers: cors });
  }

  const supplied = (req.headers.get("x-notion-signature") ?? "").replace(/^sha256=/i, "").trim().toLowerCase();
  if (!supplied) return Response.json({ error: "signature_required" }, { status: 401, headers: cors });
  const expected = await hmacHex(secret, raw);
  if (!safeEqual(supplied, expected)) return Response.json({ error: "invalid_signature" }, { status: 401, headers: cors });

  const eventId = String(event.id ?? event.event_id ?? "");
  const eventType = String(event.type ?? "unknown");
  const entity = (event.entity && typeof event.entity === "object") ? event.entity as Record<string, unknown> : {};
  const externalSubject = String(entity.id ?? event.page_id ?? event.data_source_id ?? "");
  if (!eventId) return Response.json({ error: "event_id_required" }, { status: 400, headers: cors });

  const payload = {
    event_id: eventId,
    type: eventType,
    timestamp: event.timestamp ?? null,
    entity: { id: externalSubject, type: entity.type ?? null },
    workspace_id: event.workspace_id ?? null,
  };
  const payloadHash = await hmacHex(secret, JSON.stringify(payload));
  const { error } = await supabase.from("hso_integration_events").upsert({
    provider: "notion",
    delivery_id: eventId,
    event_type: eventType,
    external_subject: externalSubject || null,
    payload_hash: payloadHash,
    payload,
    processing_state: "received",
  }, { onConflict: "provider,delivery_id", ignoreDuplicates: true });

  if (error) return Response.json({ error: "event_store_failed", detail: error.message }, { status: 500, headers: cors });

  await supabase.from("hso_change_events").upsert({
    provider: "notion",
    delivery_id: eventId,
    event_type: eventType,
    external_subject: externalSubject || null,
    title: "Notion source changed: " + eventType,
    impact: "UNKNOWN",
    follow_up: "RECONCILE",
    before_state: {},
    after_state: payload,
    event_at: event.timestamp ? new Date(String(event.timestamp)).toISOString() : new Date().toISOString()
  }, { onConflict: "provider,delivery_id", ignoreDuplicates: true });

  await supabase.from("hso_sources").update({
    last_event_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }).eq("provider", "notion").eq("enabled", true);

  // Trigger a near-real-time canonical reconciliation. The 15-minute scheduled run
  // remains the recovery path if this request cannot be made.
  let syncTriggered = false;
  const syncToken = Deno.env.get("HSO_SYNC_TOKEN");
  if (syncToken) {
    try {
      const syncResponse = await fetch(url + "/functions/v1/hso-reconcile", {
        method: "POST",
        headers: { "content-type": "application/json", "x-hso-sync-token": syncToken },
        body: JSON.stringify({ trigger_kind: "webhook", provider: "notion", delivery_id: eventId }),
        signal: AbortSignal.timeout(55000),
      });
      syncTriggered = syncResponse.ok;
    } catch { /* Event is already safely recorded; scheduled reconciliation repairs it. */ }
  }

  return Response.json({ accepted: true, provider: "notion", delivery_id: eventId, sync_triggered: syncTriggered }, { status: 202, headers: cors });
});
