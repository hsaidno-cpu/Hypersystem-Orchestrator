const MAX_BODY_BYTES = 1_048_576;
const MAX_SKEW_SECONDS = 300;
const SIGNATURE_RE = /^[a-f0-9]{64}$/i;
const DELIVERY_RE = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$/;

export type IntegrationEventRow = {
  provider: "github";
  delivery_id: string;
  event_type: string;
  external_subject: string | null;
  payload_hash: string;
  payload: Record<string, unknown>;
  processing_state: "received";
};

export type ChangeEventRow = {
  provider: "github";
  delivery_id: string;
  event_type: string;
  external_subject: string | null;
  title: string;
  impact: "HIGH" | "MEDIUM" | "UNKNOWN";
  follow_up: "INVESTIGATE_AND_RECOMPUTE" | "REVALIDATE_EXACT_HEAD" | "RECONCILE";
  before_state: Record<string, never>;
  after_state: Record<string, unknown>;
  source_url: string | null;
  event_at: string;
};

export type WebhookDependencies = {
  getSigningSecret: () => string | undefined;
  getSyncToken: () => string | undefined;
  now?: () => number;
  persistIntegrationEvent: (row: IntegrationEventRow) => Promise<{ id?: string; duplicate: boolean }>;
  persistChangeEvent: (row: ChangeEventRow) => Promise<void>;
  touchSource: (at: string) => Promise<void>;
  triggerReconciliation: (deliveryId: string, token: string) => Promise<{
    runId: string;
    status: string;
    githubStatus: string;
  }>;
  linkSyncRun: (runId: string, deliveryId: string) => Promise<void>;
  updateIntegrationEvent: (
    id: string,
    state: "processed" | "failed",
    processedAt: string | null,
    lastError: string | null,
  ) => Promise<void>;
};

function response(body: Record<string, unknown>, status: number) {
  return Response.json(body, {
    status,
    headers: {
      "access-control-allow-origin": "*",
      "access-control-allow-headers": "content-type, x-hso-signature, x-hso-delivery, x-hso-event, x-hso-timestamp",
      "access-control-allow-methods": "POST, OPTIONS",
      "cache-control": "no-store",
    },
  });
}

function constantTimeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let mismatch = 0;
  for (let i = 0; i < a.length; i++) mismatch |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return mismatch === 0;
}

async function hmacHex(secret: string, message: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signed = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return Array.from(new Uint8Array(signed), (b) => b.toString(16).padStart(2, "0")).join("");
}

async function sha256Hex(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

function compactPayload(event: Record<string, any>): Record<string, any> {
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
      number: pr.number ?? null,
      title: pr.title ?? null,
      html_url: pr.html_url ?? null,
      state: pr.state ?? null,
      head_sha: pr.head?.sha ?? null,
      base_ref: pr.base?.ref ?? null,
    } : null,
    workflow_run: Object.keys(run).length ? {
      id: run.id ?? null,
      name: run.name ?? null,
      html_url: run.html_url ?? null,
      head_sha: run.head_sha ?? null,
      conclusion: run.conclusion ?? null,
      status: run.status ?? null,
      event: run.event ?? null,
    } : null,
    sender: event.sender?.login ?? null,
  };
}

export function createWebhookHandler(deps: WebhookDependencies) {
  return async (req: Request): Promise<Response> => {
    if (req.method === "OPTIONS") return response({ ok: true }, 200);
    if (req.method !== "POST") return response({ error: "method_not_allowed" }, 405);

    const signingSecret = deps.getSigningSecret() ?? "";
    const syncToken = deps.getSyncToken() ?? "";
    if (new TextEncoder().encode(signingSecret).byteLength < 32) {
      return response({ error: "webhook_signing_secret_not_configured" }, 503);
    }
    if (syncToken && constantTimeEqual(signingSecret, syncToken)) {
      return response({ error: "webhook_and_reconciliation_secrets_must_be_distinct" }, 503);
    }

    const contentLength = req.headers.get("content-length");
    if (contentLength !== null && Number(contentLength) > MAX_BODY_BYTES) {
      return response({ error: "payload_too_large" }, 413);
    }
    if (!(req.headers.get("content-type") ?? "").toLowerCase().startsWith("application/json")) {
      return response({ error: "application_json_required" }, 415);
    }

    const timestampText = req.headers.get("x-hso-timestamp") ?? "";
    const timestamp = Number(timestampText);
    const nowSeconds = Math.floor((deps.now?.() ?? Date.now()) / 1000);
    if (!/^\d{10}$/.test(timestampText) || !Number.isSafeInteger(timestamp) ||
      Math.abs(nowSeconds - timestamp) > MAX_SKEW_SECONDS) {
      return response({ error: "stale_or_missing_timestamp" }, 401);
    }

    const deliveryId = req.headers.get("x-hso-delivery") ?? "";
    if (!DELIVERY_RE.test(deliveryId)) {
      return response({ error: "delivery_id_required_or_invalid" }, 400);
    }

    const rawBody = await req.text();
    if (new TextEncoder().encode(rawBody).byteLength > MAX_BODY_BYTES) {
      return response({ error: "payload_too_large" }, 413);
    }

    const supplied = (req.headers.get("x-hso-signature") ?? "")
      .replace(/^sha256=/i, "")
      .trim()
      .toLowerCase();
    if (!SIGNATURE_RE.test(supplied)) return response({ error: "invalid_signature" }, 401);

    const expected = await hmacHex(signingSecret, timestampText + "." + deliveryId + "." + rawBody);
    if (!constantTimeEqual(supplied, expected)) return response({ error: "invalid_signature" }, 401);

    let event: Record<string, any>;
    try {
      const parsed: unknown = JSON.parse(rawBody);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
        return response({ error: "event_object_required" }, 400);
      }
      event = parsed as Record<string, any>;
    } catch {
      return response({ error: "invalid_json" }, 400);
    }

    const eventType = req.headers.get("x-hso-event") ?? "repository_event";
    if (!/^[A-Za-z0-9_.-]{1,100}$/.test(eventType)) {
      return response({ error: "event_type_invalid" }, 400);
    }

    const compact = compactPayload(event);
    const repoName = compact.repository.full_name;
    const sourceUrl = compact.pull_request?.html_url ?? compact.workflow_run?.html_url ??
      compact.repository.html_url ?? null;
    const receivedAt = new Date(deps.now?.() ?? Date.now()).toISOString();
    let eventId: string | undefined;

    try {
      const inserted = await deps.persistIntegrationEvent({
        provider: "github",
        delivery_id: deliveryId,
        event_type: eventType,
        external_subject: typeof repoName === "string" ? repoName : null,
        payload_hash: await sha256Hex(JSON.stringify(compact)),
        payload: compact,
        processing_state: "received",
      });
      if (inserted.duplicate) return response({ error: "duplicate_delivery", accepted: false }, 409);
      if (!inserted.id) throw new Error("integration_event_id_missing");
      eventId = inserted.id;

      const failedCi = eventType === "workflow_run" && compact.workflow_run?.conclusion === "failure";
      const changedPr = eventType === "pull_request";
      await deps.persistChangeEvent({
        provider: "github",
        delivery_id: deliveryId,
        event_type: eventType,
        external_subject: typeof repoName === "string" ? repoName : null,
        title: failedCi
          ? "CI failed: " + (compact.workflow_run?.name ?? "workflow")
          : changedPr
          ? "Pull request changed: " + (compact.pull_request?.title ?? ("#" + compact.number))
          : "GitHub event: " + eventType,
        impact: failedCi ? "HIGH" : changedPr ? "MEDIUM" : "UNKNOWN",
        follow_up: failedCi
          ? "INVESTIGATE_AND_RECOMPUTE"
          : changedPr
          ? "REVALIDATE_EXACT_HEAD"
          : "RECONCILE",
        before_state: {},
        after_state: compact,
        source_url: typeof sourceUrl === "string" ? sourceUrl : null,
        event_at: receivedAt,
      });
      await deps.touchSource(receivedAt);
    } catch (error) {
      if (eventId) {
        const message = error instanceof Error ? error.message : "event_persistence_failed";
        try {
          await deps.updateIntegrationEvent(eventId, "failed", null, message.slice(0, 500));
        } catch {
          // Preserve the original persistence failure.
        }
      }
      return response({ error: "event_persistence_failed" }, 500);
    }

    if (!syncToken) {
      return response({
        accepted: true,
        delivery_id: deliveryId,
        change_event_persisted: true,
        sync_triggered: false,
        sync_successful: false,
        processing_state: "received",
      }, 202);
    }

    let result: { runId: string; status: string; githubStatus: string } | undefined;
    try {
      result = await deps.triggerReconciliation(deliveryId, syncToken);
      if (!result.runId) throw new Error("sync_run_id_missing");
      await deps.linkSyncRun(result.runId, deliveryId);
    } catch (error) {
      const message = error instanceof Error ? error.message : "reconciliation_failed";
      try {
        await deps.updateIntegrationEvent(eventId!, "failed", null, message.slice(0, 500));
      } catch {
        // Persisted event remains available for scheduled/manual recovery.
      }
      return response({
        accepted: true,
        delivery_id: deliveryId,
        change_event_persisted: true,
        sync_triggered: Boolean(result?.runId),
        sync_successful: false,
        sync_run_id: result?.runId ?? null,
        sync_status: result?.status ?? "failed",
        github_source_status: result?.githubStatus ?? "unknown",
        processing_state: "failed",
      }, 202);
    }

    const successful = ["succeeded", "partial"].includes(result.status) &&
      result.githubStatus === "connected";
    const processedAt = successful ? new Date(deps.now?.() ?? Date.now()).toISOString() : null;
    await deps.updateIntegrationEvent(
      eventId!,
      successful ? "processed" : "failed",
      processedAt,
      successful ? null : "github_source_not_connected_or_sync_failed",
    );

    return response({
      accepted: true,
      delivery_id: deliveryId,
      change_event_persisted: true,
      sync_triggered: true,
      sync_successful: successful,
      sync_run_id: result.runId,
      sync_status: result.status,
      github_source_status: result.githubStatus,
      processing_state: successful ? "processed" : "failed",
    }, 202);
  };
}
