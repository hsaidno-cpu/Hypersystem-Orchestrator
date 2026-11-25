import { createClient } from "npm:@supabase/supabase-js@2.57.0";
import { createWebhookHandler, type ChangeEventRow, type IntegrationEventRow } from "./handler.ts";

let client: ReturnType<typeof createClient> | undefined;
function db() {
  const url = Deno.env.get("SUPABASE_URL");
  const key = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !key) throw new Error("supabase_service_configuration_missing");
  client ??= createClient(url, key, { auth: { persistSession: false } });
  return client;
}

const handler = createWebhookHandler({
  getSigningSecret: () => Deno.env.get("HSO_WEBHOOK_SIGNING_SECRET"),
  getSyncToken: () => Deno.env.get("HSO_SYNC_TOKEN"),
  async persistIntegrationEvent(row: IntegrationEventRow) {
    const { data, error } = await db().from("hso_integration_events").insert(row).select("id").single();
    if (error?.code === "23505") return { duplicate: true };
    if (error) throw error;
    return { id: data?.id as string | undefined, duplicate: false };
  },
  async persistChangeEvent(row: ChangeEventRow) {
    const { error } = await db().from("hso_change_events")
      .upsert(row, { onConflict: "provider,delivery_id", ignoreDuplicates: true });
    if (error) throw error;
  },
  async touchSource(at: string) {
    const { data, error } = await db().from("hso_sources")
      .update({ last_event_at: at, updated_at: at })
      .eq("source_key", "github-hso-parent").select("source_key").maybeSingle();
    if (error) throw error;
    if (!data) throw new Error("github_source_not_registered");
  },
  async triggerReconciliation(deliveryId: string, token: string) {
    const url = Deno.env.get("SUPABASE_URL");
    if (!url) throw new Error("supabase_url_missing");
    const response = await fetch(url + "/functions/v1/hso-reconcile", {
      method: "POST",
      headers: { "content-type": "application/json", "x-hso-sync-token": token },
      body: JSON.stringify({ trigger_kind: "scheduled", provider: "github", delivery_id: deliveryId, correlation_id: deliveryId }),
      signal: AbortSignal.timeout(55_000),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error("hso_reconcile_http_" + response.status);
    return {
      runId: typeof result.run_id === "string" ? result.run_id : "",
      status: typeof result.status === "string" ? result.status : "unknown",
      githubStatus: typeof result.sources?.github?.status === "string" ? result.sources.github.status : "unknown",
    };
  },
  async linkSyncRun(runId: string, deliveryId: string) {
    const { data, error } = await db().from("hso_sync_runs")
      .update({ trigger_kind: "webhook", correlation_id: deliveryId })
      .eq("id", runId).select("id").maybeSingle();
    if (error) throw error;
    if (!data) throw new Error("sync_run_correlation_update_missing");
  },
  async updateIntegrationEvent(id, state, processedAt, lastError) {
    const { data, error } = await db().from("hso_integration_events")
      .update({ processing_state: state, processed_at: processedAt, last_error: lastError })
      .eq("id", id).select("id").maybeSingle();
    if (error) throw error;
    if (!data) throw new Error("integration_event_state_update_missing");
  },
});

Deno.serve(async (request: Request) => {
  if (request.method !== "OPTIONS" &&
      (!Deno.env.get("SUPABASE_URL") || !Deno.env.get("SUPABASE_SERVICE_ROLE_KEY"))) {
    return Response.json({ error: "supabase_service_configuration_missing" }, {
      status: 503,
      headers: { "cache-control": "no-store" },
    });
  }
  return await handler(request);
});
