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

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return Response.json({ error: "method_not_allowed" }, { status: 405, headers: cors });

  const secret = Deno.env.get("NOTION_WEBHOOK_VERIFICATION_TOKEN");
  const url = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!secret || !url || !serviceKey) {
    return Response.json({ error: "integration_not_configured" }, { status: 503, headers: cors });
  }

  const raw = await req.text();
  const supplied = (req.headers.get("x-notion-signature") ?? "").replace(/^sha256=/i, "").trim().toLowerCase();
  if (!supplied) return Response.json({ error: "signature_required" }, { status: 401, headers: cors });
  const expected = await hmacHex(secret, raw);
  if (!safeEqual(supplied, expected)) return Response.json({ error: "invalid_signature" }, { status: 401, headers: cors });

  let event: Record<string, unknown>;
  try { event = JSON.parse(raw); } catch { return Response.json({ error: "invalid_json" }, { status: 400, headers: cors }); }

  const eventId = String(event.id ?? event.event_id ?? "");
  const eventType = String(event.type ?? "unknown");
  const entity = (event.entity && typeof event.entity === "object") ? event.entity as Record<string, unknown> : {};
  const externalSubject = String(entity.id ?? event.page_id ?? event.data_source_id ?? "");
  if (!eventId) return Response.json({ error: "event_id_required" }, { status: 400, headers: cors });

  const supabase = createClient(url, serviceKey, { auth: { persistSession: false } });
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
  await supabase.from("hso_sources").update({
    last_event_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }).eq("provider", "notion").eq("enabled", true);

  return Response.json({ accepted: true, provider: "notion", delivery_id: eventId }, { status: 202, headers: cors });
});
