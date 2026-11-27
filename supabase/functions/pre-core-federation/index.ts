import { createClient } from "npm:@supabase/supabase-js@2.57.0";

const corsHeaders = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type, x-hso-signature, x-hso-delivery, x-host-id",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "cache-control": "no-store",
};

function reply(body: unknown, status = 200) {
  return Response.json(body, { status, headers: corsHeaders });
}

async function hmacHex(secret: string, raw: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(raw));
  return [...new Uint8Array(signature)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function safeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return result === 0;
}

async function verifyHsoSignature(req: Request, raw: string, secret: string): Promise<boolean> {
  const supplied = (req.headers.get("x-hso-signature") ?? "")
    .replace(/^sha256=/i, "")
    .trim()
    .toLowerCase();
  if (!supplied) return false;
  return safeEqual(supplied, await hmacHex(secret, raw));
}

function validSha256(value: unknown): value is string {
  return typeof value === "string" && /^[a-f0-9]{64}$/.test(value);
}

function validIsoDate(value: unknown): value is string {
  return typeof value === "string" && Number.isFinite(Date.parse(value));
}

function isObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function validateReleaseEvent(value: unknown): string | null {
  if (!isObject(value)) return "event_must_be_object";
  if (value.event_type !== "PRE_SHARED_DNA_RELEASE") return "unsupported_event_type";
  if (value.canonical_identity !== "pre-rpeds-shared-roadmap-dna") return "invalid_canonical_identity";
  if (typeof value.event_id !== "string" || value.event_id.length < 8) return "invalid_event_id";
  if (typeof value.idempotency_key !== "string" || value.idempotency_key.length < 16) return "invalid_idempotency_key";
  if (typeof value.version !== "string" || !/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$/.test(value.version)) return "invalid_semver";
  if (typeof value.release_id !== "string" || value.release_id.length < 8) return "invalid_release_id";
  if (typeof value.source_locator !== "string" || !value.source_locator.startsWith("https://")) return "invalid_source_locator";
  if (!validSha256(value.artifact_sha256)) return "invalid_artifact_sha256";
  if (typeof value.contract_version !== "string" || !value.contract_version) return "invalid_contract_version";
  if (typeof value.compatibility_range !== "string" || !value.compatibility_range) return "invalid_compatibility_range";
  if (!["stable", "candidate", "preview"].includes(String(value.release_channel))) return "invalid_release_channel";
  if (!isObject(value.issuer) || typeof value.issuer.identity !== "string" || typeof value.issuer.key_id !== "string" || typeof value.issuer.signature !== "string" || value.issuer.signature.length < 16) return "invalid_issuer";
  if (!validIsoDate(value.issued_at)) return "invalid_issued_at";
  if (!Array.isArray(value.capability_classes) || value.capability_classes.length === 0 || value.capability_classes.some((x) => !["SHARED_DNA", "HOST_ADAPTATION"].includes(String(x)))) return "invalid_capability_class";
  if (typeof value.is_breaking !== "boolean") return "is_breaking_boolean_required";
  return null;
}

async function parseJson(req: Request) {
  try {
    return { value: await req.json(), error: null };
  } catch {
    return { value: null, error: "invalid_json" };
  }
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  const url = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  const syncToken = Deno.env.get("HSO_SYNC_TOKEN");
  if (!url || !serviceKey || !syncToken) {
    return reply({ error: "federation_not_configured", missing: [
      ...(!url ? ["SUPABASE_URL"] : []),
      ...(!serviceKey ? ["SUPABASE_SERVICE_ROLE_KEY"] : []),
      ...(!syncToken ? ["HSO_SYNC_TOKEN"] : []),
    ] }, 503);
  }

  const supabase = createClient(url, serviceKey, { auth: { persistSession: false } });
  const path = new URL(req.url).pathname.replace(/\/+$/, "").split("/").pop() ?? "";

  if (req.method === "GET" && path === "health") {
    return reply({ service: "pre-core-federation", status: "ACTIVE", signed_transport: true, independent_verifier_configured: Boolean(Deno.env.get("PRE_RELEASE_VERIFIER_TOKEN")), reconciliation_endpoint: "POST /reconcile", persistence: "SUPABASE_POSTGRES" });
  }

  if (req.method === "POST" && path === "release") {
    const raw = await req.text();
    if (!(await verifyHsoSignature(req, raw, syncToken))) return reply({ error: "invalid_signature" }, 401);
    let event: unknown;
    try { event = JSON.parse(raw); } catch { return reply({ error: "invalid_json" }, 400); }
    const invalid = validateReleaseEvent(event);
    if (invalid) return reply({ error: invalid }, 422);

    const e = event as Record<string, any>;
    const { data: inserted, error } = await supabase.from("pre_kernel_releases").insert({
      event_id: e.event_id,
      idempotency_key: e.idempotency_key,
      canonical_identity: e.canonical_identity,
      release_version: e.version,
      release_id: e.release_id,
      source_locator: e.source_locator,
      artifact_sha256: e.artifact_sha256,
      contract_version: e.contract_version,
      compatibility_range: e.compatibility_range,
      release_channel: e.release_channel,
      issuer_identity: e.issuer.identity,
      issuer_key_id: e.issuer.key_id,
      signature_verified: false,
      publisher_hmac_verified: true,
      artifact_digest_verified: false,
      issuer_signature_verified: false,
      contract_validated: false,
      source_commit: typeof e.source_commit === "string" ? e.source_commit : null,
      publisher_run_ref: typeof e.publisher_run_ref === "string" ? e.publisher_run_ref : null,
      origin_lineage: Array.isArray(e.origin_lineage) ? e.origin_lineage : [],
      capability_classes: Array.isArray(e.capability_classes) ? e.capability_classes : [],
      payload: e,
      processing_state: "PUBLISHER_AUTHENTICATED",
      issued_at: e.issued_at,
      processed_at: new Date().toISOString(),
      verification_evidence: {
        transport_hmac: "PASS",
        artifact_digest: "NOT_VERIFIED",
        issuer_signature: "NOT_VERIFIED",
        compatibility_contract: "NOT_VERIFIED"
      }
    }).select("id,event_id,release_version,release_id,artifact_sha256,processing_state,publisher_hmac_verified,artifact_digest_verified,issuer_signature_verified,contract_validated").single();

    if (error) {
      if (error.code === "23505") {
        const { data: existing } = await supabase.from("pre_kernel_releases")
          .select("id,event_id,release_version,release_id,artifact_sha256,processing_state,publisher_hmac_verified,artifact_digest_verified,issuer_signature_verified,contract_validated")
          .or("event_id.eq." + encodeURIComponent(e.event_id) + ",idempotency_key.eq." + encodeURIComponent(e.idempotency_key))
          .maybeSingle();
        if (existing) return reply({ accepted: true, duplicate: true, release: existing }, 200);
      }
      return reply({ error: "release_persistence_failed", detail: error.message }, 500);
    }

    const { data: hosts, error: hostError } = await supabase.from("pre_host_subscriptions")
      .select("host_id,host_name,subscribed_channel,enabled")
      .eq("enabled", true);
    if (hostError) return reply({ error: "host_registry_read_failed", detail: hostError.message }, 500);

    const receipts = [];
    for (const host of hosts ?? []) {
      const channelMatches = host.subscribed_channel === "all" || host.subscribed_channel === e.release_channel;
      if (!channelMatches) continue;
      const { data: receipt, error: receiptError } = await supabase.from("pre_host_adoption_receipts").insert({
        event_id: e.event_id,
        host_id: host.host_id,
        candidate_kernel_version: e.version,
        artifact_sha256: e.artifact_sha256,
        adapter_disposition: "NOT_ASSESSED",
        adoption_state: "HELD",
        reason: "Publisher transport authenticated. Artifact digest, issuer signature and compatibility contract attestation are still pending.",
        receipt_payload: { release_id: e.release_id, host_name: host.host_name, release_channel: e.release_channel }
      }).select("id,host_id,adoption_state,adapter_disposition").single();

      if (receiptError && receiptError.code !== "23505") {
        receipts.push({ host_id: host.host_id, state: "RECEIPT_ERROR", error: receiptError.message });
      } else {
        receipts.push({ host_id: host.host_id, state: receipt?.adoption_state ?? "ALREADY_RECORDED" });
      }
      await supabase.from("pre_host_subscriptions").update({
        last_event_at: new Date().toISOString(),
        sync_state: "RELEASE_ATTESTATION_PENDING",
        updated_at: new Date().toISOString()
      }).eq("host_id", host.host_id);
    }
    return reply({
      accepted: true,
      duplicate: false,
      release: inserted,
      host_receipts: receipts,
      next_required_step: "Independent verifier must POST /attest with matching artifact digest, issuer signature, contract compatibility and evidence references."
    }, 202);
  }

  if (req.method === "POST" && path === "attest") {
    const raw = await req.text();
    const verifierToken = Deno.env.get("PRE_RELEASE_VERIFIER_TOKEN");
    if (!verifierToken) return reply({ error: "release_verifier_not_configured" }, 503);
    if (!(await verifyHsoSignature(req, raw, verifierToken))) return reply({ error: "invalid_verifier_signature" }, 401);

    let body: unknown;
    try { body = JSON.parse(raw); } catch { return reply({ error: "invalid_json" }, 400); }
    if (!isObject(body)) return reply({ error: "body_must_be_object" }, 422);

    const eventId = String(body.event_id ?? "");
    if (!eventId || body.artifact_digest_verified !== true ||
        body.issuer_signature_verified !== true || body.contract_validated !== true ||
        body.compatibility_verified !== true || typeof body.is_breaking !== "boolean" ||
        !Array.isArray(body.evidence_refs) || body.evidence_refs.length === 0 ||
        typeof body.verified_artifact_sha256 !== "string") {
      return reply({ error: "complete_release_attestation_required" }, 422);
    }

    const { data: release, error: releaseError } = await supabase.from("pre_kernel_releases")
      .select("event_id,release_version,artifact_sha256,processing_state,capability_classes,payload")
      .eq("event_id", eventId).maybeSingle();
    if (releaseError || !release) return reply({ error: "release_not_found" }, 404);
    if (release.processing_state !== "PUBLISHER_AUTHENTICATED") {
      return reply({ error: "release_not_in_attestable_state", state: release.processing_state }, 409);
    }
    if (body.verified_artifact_sha256 !== release.artifact_sha256) {
      await supabase.from("pre_kernel_releases").update({
        processing_state: "QUARANTINED",
        last_error: "Verified artifact digest does not match publisher envelope.",
        verification_evidence: { ...body, digest_match: false }
      }).eq("event_id", eventId);
      return reply({ error: "artifact_digest_mismatch_quarantined" }, 409);
    }

    const evidence = {
      artifact_digest: "PASS",
      issuer_signature: "PASS",
      compatibility_contract: "PASS",
      compatibility_verified: true,
      evidence_refs: body.evidence_refs,
      verifier_identity: body.verifier_identity ?? "PRE_RELEASE_VERIFIER",
      verified_at: new Date().toISOString()
    };
    const { error: updateError } = await supabase.from("pre_kernel_releases").update({
      processing_state: "RELEASED",
      signature_verified: true,
      artifact_digest_verified: true,
      issuer_signature_verified: true,
      contract_validated: true,
      source_commit: body.source_commit ?? null,
      publisher_run_ref: body.publisher_run_ref ?? null,
      verification_evidence: evidence,
      processed_at: new Date().toISOString(),
      last_error: null
    }).eq("event_id", eventId);
    if (updateError) return reply({ error: "release_attestation_update_failed", detail: updateError.message }, 500);

    const { data: hosts } = await supabase.from("pre_host_subscriptions")
      .select("host_id,policy_profile_status,auto_adopt_nonbreaking,enabled,subscribed_channel");
    const capabilityClasses = Array.isArray(release.capability_classes) ? release.capability_classes : [];
    const isBreaking = release.payload?.is_breaking === true || body.is_breaking === true;
    const sharedDna = capabilityClasses.length > 0 && capabilityClasses.every((value) => value === "SHARED_DNA");
    const receipts = [];
    for (const host of hosts ?? []) {
      if (host.enabled !== true || (host.subscribed_channel !== "all" && host.subscribed_channel !== release.payload?.release_channel)) continue;
      const eligible = host.policy_profile_status === "VERIFIED" &&
        host.auto_adopt_nonbreaking === true &&
        body.compatibility_verified === true &&
        body.is_breaking === false &&
        !isBreaking && sharedDna;
      const state = eligible ? "QUEUED_FOR_TESTS" : "HELD";
      const disposition = eligible ? "DIRECT_COMPATIBLE" : "NOT_ASSESSED";
      const reason = eligible
        ? "Release attested; host regression and non-regression tests are now required."
        : "Release artifact is attested, but this host is not pre-approved for automatic adoption or the change is not proven additive shared DNA.";
      const { error: receiptError } = await supabase.from("pre_host_adoption_receipts")
        .update({
          adapter_disposition: disposition,
          adoption_state: state,
          reason,
          receipt_payload: { release_id: release.payload?.release_id, attestation: evidence },
          observed_at: new Date().toISOString()
        }).eq("event_id", eventId).eq("host_id", host.host_id);
      if (receiptError) receipts.push({ host_id: host.host_id, state: "UPDATE_ERROR", error: receiptError.message });
      else receipts.push({ host_id: host.host_id, state });
      await supabase.from("pre_host_subscriptions").update({
        sync_state: eligible ? "HOST_TESTS_PENDING" : "RELEASE_VERIFIED_HOST_HELD",
        updated_at: new Date().toISOString()
      }).eq("host_id", host.host_id);
    }
    return reply({ accepted: true, event_id: eventId, processing_state: "RELEASED", host_receipts: receipts }, 200);
  }

  if (req.method === "GET" && path === "latest") {
    const hostId = new URL(req.url).searchParams.get("host_id");
    if (!hostId) return reply({ error: "host_id_required" }, 400);
    const { data: host, error: hostError } = await supabase.from("pre_host_subscriptions")
      .select("*").eq("host_id", hostId).maybeSingle();
    if (hostError || !host) return reply({ error: "host_not_registered" }, 404);
    if (host.host_auth_status !== "CONFIGURED" || !host.host_auth_secret_ref) {
      return reply({ error: "host_auth_not_configured" }, 503);
    }
    const hostSecret = Deno.env.get(host.host_auth_secret_ref);
    const bearer = (req.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "");
    const hostToken = req.headers.get("x-host-token") ?? bearer;
    if (!hostSecret || !safeEqual(hostToken, hostSecret)) return reply({ error: "host_unauthorized" }, 401);
    const { data: release, error: releaseError } = await supabase.from("pre_kernel_releases")
      .select("event_id,release_version,release_id,source_locator,artifact_sha256,contract_version,compatibility_range,release_channel,capability_classes,processing_state,artifact_digest_verified,issuer_signature_verified,contract_validated,source_commit,verification_evidence,issued_at")
      .eq("processing_state", "RELEASED")
      .eq("artifact_digest_verified", true)
      .eq("issuer_signature_verified", true)
      .eq("contract_validated", true)
      .order("received_at", { ascending: false })
      .limit(1).maybeSingle();
    if (releaseError) return reply({ error: "release_lookup_failed", detail: releaseError.message }, 500);
    const { data: receipts } = release ? await supabase.from("pre_host_adoption_receipts")
      .select("*").eq("event_id", release.event_id).eq("host_id", hostId).limit(1) : { data: [] };
    const safeHost = { ...host };
    delete safeHost.host_auth_secret_ref;
    return reply({ host: safeHost, latest_release: release ?? null, adoption_receipt: receipts?.[0] ?? null });
  }

  if (req.method === "POST" && path === "adoption") {
    const raw = await req.text();
    let body: unknown;
    try { body = JSON.parse(raw); } catch { return reply({ error: "invalid_json" }, 400); }
    if (!isObject(body)) return reply({ error: "body_must_be_object" }, 422);
    const eventId = String(body.event_id ?? "");
    const hostId = String(body.host_id ?? "");
    const state = String(body.adoption_state ?? "");
    const allowed = ["QUEUED_FOR_TESTS","PR_OPENED","APPROVAL_PENDING","ADOPTED","VERIFIED","HELD","QUARANTINED","REJECTED","RETRY_PENDING","DEAD_LETTER","ROLLED_BACK","REVOKED"];
    if (!eventId || !hostId || !allowed.includes(state)) return reply({ error: "invalid_adoption_envelope" }, 422);

    const { data: hostAuth } = await supabase.from("pre_host_subscriptions")
      .select("host_auth_secret_ref,host_auth_status,policy_profile_status").eq("host_id", hostId).maybeSingle();
    if (!hostAuth) return reply({ error: "host_not_registered" }, 404);
    if (hostAuth.host_auth_status !== "CONFIGURED" || !hostAuth.host_auth_secret_ref) {
      return reply({ error: "host_auth_not_configured" }, 503);
    }
    const hostSecret = Deno.env.get(hostAuth.host_auth_secret_ref);
    if (!hostSecret || !(await verifyHsoSignature(req, raw, hostSecret))) {
      return reply({ error: "invalid_host_signature" }, 401);
    }

    const { data: release } = await supabase.from("pre_kernel_releases")
      .select("release_id,release_version,artifact_sha256,processing_state,artifact_digest_verified,issuer_signature_verified,contract_validated").eq("event_id", eventId).maybeSingle();
    if (!release) return reply({ error: "release_not_found" }, 404);

    const { data: receipt } = await supabase.from("pre_host_adoption_receipts")
      .select("id").eq("event_id", eventId).eq("host_id", hostId).maybeSingle();
    if (!receipt) return reply({ error: "host_receipt_not_found" }, 404);

    if (state === "VERIFIED") {
      if (hostAuth.policy_profile_status !== "VERIFIED") return reply({ error: "host_policy_profile_not_verified" }, 409);
      if (!["DIRECT_COMPATIBLE", "ADAPTED_COMPATIBLE"].includes(String(body.adapter_disposition))) {
        return reply({ error: "verified_requires_compatible_afsa_disposition" }, 409);
      }
      if (!Array.isArray(body.policy_refs) || body.policy_refs.length === 0 ||
          typeof body.adapter_version !== "string" || !body.adapter_version ||
          typeof body.rollback_ref !== "string" || !body.rollback_ref) {
        return reply({ error: "verified_requires_policy_adapter_and_rollback_evidence" }, 409);
      }
      if (body.adapter_disposition === "ADAPTED_COMPATIBLE" &&
          (!Array.isArray(body.approval_refs) || body.approval_refs.length === 0)) {
        return reply({ error: "adapted_compatibility_requires_approval_reference" }, 409);
      }
      if (release.processing_state !== "RELEASED" || release.artifact_digest_verified !== true || release.issuer_signature_verified !== true || release.contract_validated !== true) {
        return reply({ error: "release_attestation_not_complete" }, 409);
      }
      if (body.readback_version !== release.release_version || body.readback_digest !== release.artifact_sha256) {
        return reply({ error: "readback_does_not_match_release" }, 409);
      }
      if (!Array.isArray(body.test_results) || body.test_results.length === 0 ||
          body.test_results.some((t: any) => t?.status !== "PASS")) {
        return reply({ error: "verified_requires_all_tests_pass" }, 409);
      }
    }

    const updates: Record<string, unknown> = {
      adoption_state: state,
      adapter_disposition: body.adapter_disposition ?? "NOT_ASSESSED",
      adapter_version: body.adapter_version ?? null,
      policy_refs: Array.isArray(body.policy_refs) ? body.policy_refs : [],
      approval_refs: Array.isArray(body.approval_refs) ? body.approval_refs : [],
      test_results: Array.isArray(body.test_results) ? body.test_results : [],
      pull_request_ref: body.pull_request_ref ?? null,
      commit_ref: body.commit_ref ?? null,
      deployment_ref: body.deployment_ref ?? null,
      readback_version: body.readback_version ?? null,
      readback_digest: body.readback_digest ?? null,
      rollback_ref: body.rollback_ref ?? null,
      reason: typeof body.reason === "string" ? body.reason : null,
      residual_risks: Array.isArray(body.residual_risks) ? body.residual_risks : [],
      receipt_payload: body,
      observed_at: new Date().toISOString(),
    };
    const { error } = await supabase.from("pre_host_adoption_receipts").update(updates).eq("id", receipt.id);
    if (error) return reply({ error: "adoption_receipt_update_failed", detail: error.message }, 500);
    await supabase.from("pre_host_subscriptions").update({
      sync_state: state,
      current_kernel_version: state === "VERIFIED" ? release.release_version : undefined,
      current_release_id: state === "VERIFIED" ? release.release_id : undefined,
      last_adopted_at: state === "VERIFIED" ? new Date().toISOString() : undefined,
      updated_at: new Date().toISOString(),
    }).eq("host_id", hostId);
    return reply({ accepted: true, host_id: hostId, event_id: eventId, adoption_state: state });
  }

  if (req.method === "POST" && path === "reconcile") {
    const raw = await req.text();
    if (!(await verifyHsoSignature(req, raw, syncToken))) return reply({ error: "invalid_signature" }, 401);
    let body: unknown = {};
    if (raw.trim()) { try { body = JSON.parse(raw); } catch { return reply({ error: "invalid_json" }, 400); } }
    if (!isObject(body)) return reply({ error: "body_must_be_object" }, 422);
    const eventId = typeof body.event_id === "string" ? body.event_id : null;
    const hostId = typeof body.host_id === "string" ? body.host_id : null;
    let releaseQuery = supabase.from("pre_kernel_releases")
      .select("event_id,release_version,release_id,artifact_sha256,release_channel,capability_classes,payload")
      .eq("processing_state", "RELEASED").eq("artifact_digest_verified", true)
      .eq("issuer_signature_verified", true).eq("contract_validated", true)
      .order("received_at", { ascending: false }).limit(100);
    if (eventId) releaseQuery = releaseQuery.eq("event_id", eventId);
    const { data: releases, error: releaseError } = await releaseQuery;
    if (releaseError) return reply({ error: "reconcile_release_lookup_failed", detail: releaseError.message }, 500);
    let hostQuery = supabase.from("pre_host_subscriptions")
      .select("host_id,host_name,subscribed_channel,enabled,current_kernel_version,adapter_version,policy_profile_status,auto_adopt_nonbreaking")
      .eq("enabled", true);
    if (hostId) hostQuery = hostQuery.eq("host_id", hostId);
    const { data: hosts, error: hostError } = await hostQuery;
    if (hostError) return reply({ error: "reconcile_host_lookup_failed", detail: hostError.message }, 500);
    const outcomes = [];
    let created = 0, alreadyRecorded = 0, held = 0;
    for (const release of releases ?? []) {
      for (const host of hosts ?? []) {
        if (host.subscribed_channel !== "all" && host.subscribed_channel !== release.release_channel) continue;
        const { data: existing, error: existingError } = await supabase.from("pre_host_adoption_receipts")
          .select("id,adoption_state").eq("event_id", release.event_id).eq("host_id", host.host_id).maybeSingle();
        if (existingError) return reply({ error: "reconcile_receipt_lookup_failed", detail: existingError.message }, 500);
        if (existing) {
          alreadyRecorded++;
          outcomes.push({ event_id: release.event_id, host_id: host.host_id, state: "UNCHANGED", existing_state: existing.adoption_state });
          continue;
        }
        const classes = Array.isArray(release.capability_classes) ? release.capability_classes : [];
        const sharedDnaOnly = classes.length > 0 && classes.every((value) => value === "SHARED_DNA");
        const nonBreaking = release.payload?.is_breaking === false;
        const eligible = sharedDnaOnly && nonBreaking && host.policy_profile_status === "VERIFIED" && host.auto_adopt_nonbreaking === true;
        const state = eligible ? "QUEUED_FOR_TESTS" : "HELD";
        const disposition = eligible ? "DIRECT_COMPATIBLE" : "NOT_ASSESSED";
        const reason = eligible
          ? "Verified non-breaking shared-DNA release reconciled; host tests and target read-back are required before adoption."
          : "Release is verified but this host is not pre-approved, the change is not explicitly non-breaking shared DNA, or AFSA/policy review remains outstanding.";
        const { error: insertError } = await supabase.from("pre_host_adoption_receipts").insert({
          event_id: release.event_id, host_id: host.host_id, previous_kernel_version: host.current_kernel_version,
          candidate_kernel_version: release.release_version, artifact_sha256: release.artifact_sha256,
          adapter_version: host.adapter_version, adapter_disposition: disposition, adoption_state: state, reason,
          receipt_payload: { release_id: release.release_id, release_channel: release.release_channel, reconciliation_trigger: body.trigger_kind ?? "manual_or_scheduled" },
          observed_at: new Date().toISOString()
        });
        if (insertError) {
          if (insertError.code === "23505") { alreadyRecorded++; outcomes.push({ event_id: release.event_id, host_id: host.host_id, state: "UNCHANGED_AFTER_RACE" }); continue; }
          return reply({ error: "reconcile_receipt_insert_failed", detail: insertError.message }, 500);
        }
        created++; if (state === "HELD") held++;
        outcomes.push({ event_id: release.event_id, host_id: host.host_id, state });
      }
    }
    return reply({ accepted: true, releases_seen: (releases ?? []).length, hosts_seen: (hosts ?? []).length, receipts_created: created, receipts_unchanged: alreadyRecorded, receipts_held: held, outcomes }, 200);
  }

  return reply({ error: "not_found" }, 404);
});
