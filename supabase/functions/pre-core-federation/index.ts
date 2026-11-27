import { createClient } from "npm:@supabase/supabase-js@2.57.0";

const corsHeaders = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type, authorization, x-hso-signature, x-hso-delivery, x-host-id, x-host-token, x-pre-artifact-sha256",
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


async function resolveSecret(supabase: any, name: string): Promise<string | null> {
  const envValue = Deno.env.get(name);
  if (envValue) return envValue;
  const { data, error } = await supabase.rpc("pre_federation_get_secret", { secret_name: name });
  if (error) {
    console.error("vault_secret_lookup_failed", { name, message: error.message });
    return null;
  }
  return typeof data === "string" && data.length > 0 ? data : null;
}

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function base64Bytes(value: string): Uint8Array {
  const binary = atob(value);
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

function decodeBase64Url(value: string): Uint8Array {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "=".repeat((4 - normalized.length % 4) % 4);
  return base64Bytes(padded);
}

async function verifyGitHubOidc(req: Request, role: "publisher" | "verifier" | "reconciler" | "asfree-rpeds"): Promise<Record<string, any> | null> {
  try {
    const bearer = (req.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "");
    if (!bearer) return null;
    const parts = bearer.split(".");
    if (parts.length !== 3) return null;
    const header = JSON.parse(new TextDecoder().decode(decodeBase64Url(parts[0])));
    const claims = JSON.parse(new TextDecoder().decode(decodeBase64Url(parts[1])));
    if (header.alg !== "RS256" || typeof header.kid !== "string") return null;

    const expectedAudience = `${Deno.env.get("SUPABASE_URL")}/functions/v1/pre-core-federation`;
    const audience = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
    const now = Math.floor(Date.now() / 1000);
    if (claims.iss !== "https://token.actions.githubusercontent.com" ||
        !audience.includes(expectedAudience) ||
        typeof claims.exp !== "number" || claims.exp <= now ||
        (typeof claims.nbf === "number" && claims.nbf > now + 60)) return null;

    const jwksResponse = await fetch("https://token.actions.githubusercontent.com/.well-known/jwks");
    if (!jwksResponse.ok) return null;
    const jwks = await jwksResponse.json();
    const jwk = Array.isArray(jwks.keys) ? jwks.keys.find((key: any) => key.kid === header.kid) : null;
    if (!jwk) return null;
    const verificationKey = await crypto.subtle.importKey(
      "jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"],
    );
    const signingInput = new TextEncoder().encode(`${parts[0]}.${parts[1]}`);
    const signatureValid = await crypto.subtle.verify(
      { name: "RSASSA-PKCS1-v1_5" }, verificationKey, decodeBase64Url(parts[2]), signingInput,
    );
    if (!signatureValid) return null;

    const repo = String(claims.repository ?? "");
    const ref = String(claims.ref ?? "");
    const workflowRef = String(claims.workflow_ref ?? "");
    const allowed = {
      publisher: repo === "hsaidno-cpu/pre-rpeds-shared-roadmap-dna" &&
        ref === "refs/heads/main" &&
        workflowRef === "hsaidno-cpu/pre-rpeds-shared-roadmap-dna/.github/workflows/pre-release-publish.yml@refs/heads/main",
      verifier: repo === "hsaidno-cpu/pre-rpeds-shared-roadmap-dna" &&
        ref === "refs/heads/main" &&
        workflowRef === "hsaidno-cpu/pre-rpeds-shared-roadmap-dna/.github/workflows/pre-release-verify.yml@refs/heads/main",
      reconciler: repo === "hsaidno-cpu/Hypersystem-Orchestrator" &&
        ref === "refs/heads/main" &&
        workflowRef === "hsaidno-cpu/Hypersystem-Orchestrator/.github/workflows/pre-rpeds-federation.yml@refs/heads/main",
      "asfree-rpeds": repo === "hsaidno-cpu/A.S.F.R.E.E" &&
        ref === "refs/heads/main" &&
        workflowRef === "hsaidno-cpu/A.S.F.R.E.E/.github/workflows/pre-rpeds-host-adopt.yml@refs/heads/main",
    }[role];
    return allowed ? claims : null;
  } catch (error) {
    console.error("github_oidc_verification_error", String(error));
    return null;
  }
}

async function authorizedHost(supabase: any, req: Request, hostId: string): Promise<boolean> {
  const { data: host } = await supabase.from("pre_host_subscriptions")
    .select("host_auth_secret_ref,host_auth_status").eq("host_id", hostId).maybeSingle();
  if (!host || host.host_auth_status !== "CONFIGURED") return false;
  const hostToken = req.headers.get("x-host-token") ??
    (req.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "");
  const hostSecret = host.host_auth_secret_ref ? await resolveSecret(supabase, host.host_auth_secret_ref) : null;
  if (hostSecret && safeEqual(hostToken, hostSecret)) return true;
  return hostId === "asfree-rpeds" && Boolean(await verifyGitHubOidc(req, "asfree-rpeds"));
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
  if (!isObject(value.issuer) || typeof value.issuer.identity !== "string" || typeof value.issuer.key_id !== "string" || typeof value.issuer.identity_ref !== "string" || value.issuer.identity_ref.length < 16) return "invalid_issuer";
  if (!validIsoDate(value.issued_at)) return "invalid_issued_at";
  if (!Array.isArray(value.capability_classes) || value.capability_classes.length === 0 || value.capability_classes.some((x) => !["SHARED_DNA", "HOST_ADAPTATION"].includes(String(x)))) return "invalid_capability_class";
  if (!Array.isArray(value.target_host_ids) || value.target_host_ids.length === 0 || value.target_host_ids.some((x) => typeof x !== "string" || !x)) return "invalid_target_host_ids";
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
  if (!url || !serviceKey) {
    return reply({ error: "federation_not_configured", missing: [
      ...(!url ? ["SUPABASE_URL"] : []),
      ...(!serviceKey ? ["SUPABASE_SERVICE_ROLE_KEY"] : []),
    ] }, 503);
  }

  const supabase = createClient(url, serviceKey, { auth: { persistSession: false } });
  const syncToken = await resolveSecret(supabase, "HSO_SYNC_TOKEN");
  if (!syncToken) return reply({ error: "federation_not_configured", missing: ["HSO_SYNC_TOKEN"] }, 503);
  const path = new URL(req.url).pathname.replace(/\/+$/, "").split("/").pop() ?? "";

  if (req.method === "GET" && path === "health") {
    const verifierSecret = await resolveSecret(supabase, "PRE_RELEASE_VERIFIER_TOKEN");
    return reply({
      service: "pre-core-federation", status: "ACTIVE", signed_transport: true,
      publisher_vault_configured: Boolean(syncToken),
      independent_verifier_configured: Boolean(verifierSecret),
      artifact_storage: "pre-release-artifacts",
      reconciliation_endpoint: "POST /reconcile",
      persistence: "SUPABASE_POSTGRES",
    });
  }

  if (req.method === "POST" && path === "artifact") {
    const expectedDigest = (req.headers.get("x-pre-artifact-sha256") ?? "").trim().toLowerCase();
    if (!validSha256(expectedDigest)) return reply({ error: "artifact_sha256_header_required" }, 400);
    const bytes = new Uint8Array(await req.arrayBuffer());
    const actualDigest = await sha256Hex(bytes);
    if (actualDigest !== expectedDigest) return reply({ error: "artifact_digest_mismatch" }, 409);

    const supplied = (req.headers.get("x-hso-signature") ?? "").replace(/^sha256=/i, "").trim().toLowerCase();
    const expected = await hmacHex(syncToken, `${actualDigest}\\n${bytes.length}`);
    const hmacAuthenticated = Boolean(supplied && safeEqual(supplied, expected));
    const oidcAuthenticated = Boolean(await verifyGitHubOidc(req, "publisher"));
    if (!hmacAuthenticated && !oidcAuthenticated) return reply({ error: "publisher_authentication_required" }, 401);

    const storagePath = `${actualDigest}.tar.gz`;
    const { error } = await supabase.storage.from("pre-release-artifacts").upload(storagePath, bytes, {
      contentType: "application/gzip", cacheControl: "0", upsert: false,
    });
    if (error && !String(error.message ?? "").toLowerCase().includes("already exists")) {
      return reply({ error: "artifact_storage_failed", detail: error.message }, 500);
    }
    const sourceLocator = `${url}/functions/v1/pre-core-federation/artifact?sha256=${actualDigest}`;
    return reply({ accepted: true, artifact_sha256: actualDigest, bytes: bytes.length, source_locator: sourceLocator }, 201);
  }

  if (req.method === "GET" && path === "artifact") {
    const digest = new URL(req.url).searchParams.get("sha256") ?? "";
    if (!validSha256(digest)) return reply({ error: "valid_sha256_required" }, 400);
    const bearer = (req.headers.get("authorization") ?? "").replace(/^Bearer\s+/i, "");
    const verifierToken = await resolveSecret(supabase, "PRE_RELEASE_VERIFIER_TOKEN");
    const verifierAuthenticated = Boolean(
      (verifierToken && safeEqual(bearer, verifierToken)) ||
      (await verifyGitHubOidc(req, "verifier"))
    );
    const hostId = new URL(req.url).searchParams.get("host_id");
    if (!verifierAuthenticated) {
      if (!hostId || !(await authorizedHost(supabase, req, hostId))) return reply({ error: "artifact_access_denied" }, 401);
      const { data: released } = await supabase.from("pre_kernel_releases")
        .select("event_id").eq("artifact_sha256", digest).eq("processing_state", "RELEASED")
        .eq("artifact_digest_verified", true).eq("issuer_signature_verified", true)
        .eq("contract_validated", true).limit(1).maybeSingle();
      if (!released) return reply({ error: "artifact_not_released" }, 404);
    }
    const { data: file, error } = await supabase.storage.from("pre-release-artifacts").download(`${digest}.tar.gz`);
    if (error || !file) return reply({ error: "artifact_not_found" }, 404);
    const bytes = new Uint8Array(await file.arrayBuffer());
    if (await sha256Hex(bytes) !== digest) return reply({ error: "stored_artifact_integrity_failure" }, 409);
    return new Response(bytes, { status: 200, headers: {
      ...corsHeaders, "content-type": "application/gzip", "content-length": String(bytes.length),
      "content-disposition": `attachment; filename="pre-rpeds-${digest}.tar.gz"`,
    }});
  }

  if (req.method === "POST" && path === "release") {
    const raw = await req.text();
    const oidcPublisher = await verifyGitHubOidc(req, "publisher");
    if (!oidcPublisher && !(await verifyHsoSignature(req, raw, syncToken))) return reply({ error: "invalid_signature" }, 401);
    let event: unknown;
    try { event = JSON.parse(raw); } catch { return reply({ error: "invalid_json" }, 400); }
    const invalid = validateReleaseEvent(event);
    if (invalid) return reply({ error: invalid }, 422);

    const e = event as Record<string, any>;
    const expectedLocator = `${url}/functions/v1/pre-core-federation/artifact?sha256=${e.artifact_sha256}`;
    if (e.source_locator !== expectedLocator) return reply({ error: "source_locator_must_reference_registered_private_artifact" }, 422);
    const { data: storedArtifact, error: artifactReadError } = await supabase.storage
      .from("pre-release-artifacts").download(`${e.artifact_sha256}.tar.gz`);
    if (artifactReadError || !storedArtifact) return reply({ error: "artifact_not_uploaded" }, 409);
    const storedBytes = new Uint8Array(await storedArtifact.arrayBuffer());
    if (await sha256Hex(storedBytes) !== e.artifact_sha256) return reply({ error: "stored_artifact_digest_mismatch" }, 409);
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
      publisher_hmac_verified: !oidcPublisher,
      artifact_digest_verified: false,
      issuer_signature_verified: false,
      contract_validated: false,
      source_commit: typeof e.source_commit === "string" ? e.source_commit : null,
      publisher_run_ref: typeof e.publisher_run_ref === "string" ? e.publisher_run_ref : null,
      origin_lineage: Array.isArray(e.origin_lineage) ? e.origin_lineage : [],
      capability_classes: Array.isArray(e.capability_classes) ? e.capability_classes : [],
      payload: { ...e, _publisher_oidc: oidcPublisher ? {
        repository: oidcPublisher.repository,
        workflow_ref: oidcPublisher.workflow_ref,
        ref: oidcPublisher.ref,
        sha: oidcPublisher.sha,
        run_id: oidcPublisher.run_id,
      } : null },
      processing_state: "PUBLISHER_AUTHENTICATED",
      issued_at: e.issued_at,
      processed_at: new Date().toISOString(),
      verification_evidence: {
        transport_auth: oidcPublisher ? "GITHUB_OIDC_SIGNATURE_VERIFIED" : "HMAC_SHA256",
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
    const enabledHostIds = new Set((hosts ?? []).map((host: any) => host.host_id));
    const targetHostIds = new Set(e.target_host_ids as string[]);
    if ([...targetHostIds].some((hostId) => !enabledHostIds.has(hostId))) {
      return reply({ error: "release_target_host_not_registered_or_disabled" }, 422);
    }

    const receipts = [];
    for (const host of hosts ?? []) {
      if (!targetHostIds.has(host.host_id)) continue;
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
    const verifierToken = await resolveSecret(supabase, "PRE_RELEASE_VERIFIER_TOKEN");
    if (!verifierToken) return reply({ error: "release_verifier_not_configured" }, 503);
    const oidcVerifier = await verifyGitHubOidc(req, "verifier");
    if (!oidcVerifier && !(await verifyHsoSignature(req, raw, verifierToken))) {
      return reply({ error: "invalid_verifier_signature" }, 401);
    }

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
    const { data: packageBlob, error: packageError } = await supabase.storage
      .from("pre-release-artifacts").download(`${release.artifact_sha256}.tar.gz`);
    if (packageError || !packageBlob) return reply({ error: "independent_verifier_artifact_unavailable" }, 409);
    const packageBytes = new Uint8Array(await packageBlob.arrayBuffer());
    const computedDigest = await sha256Hex(packageBytes);
    if (computedDigest !== release.artifact_sha256 || body.verified_artifact_sha256 !== computedDigest) {
      await supabase.from("pre_kernel_releases").update({
        processing_state: "QUARANTINED",
        last_error: "Independent artifact digest does not match the immutable publisher envelope.",
        verification_evidence: { verifier_report: body, computed_digest: computedDigest, digest_match: false }
      }).eq("event_id", eventId);
      return reply({ error: "artifact_digest_mismatch_quarantined" }, 409);
    }

    const releaseEvent = release.payload as Record<string, any>;
    if (validateReleaseEvent(releaseEvent) !== null || body.is_breaking !== releaseEvent.is_breaking ||
        body.compatibility_verified !== true) {
      await supabase.from("pre_kernel_releases").update({
        processing_state: "QUARANTINED",
        last_error: "Independent contract and compatibility validation failed.",
        verification_evidence: { verifier_report: body, contract_validated: false }
      }).eq("event_id", eventId);
      return reply({ error: "contract_or_compatibility_validation_failed_quarantined" }, 409);
    }
    const publisherProof = releaseEvent._publisher_oidc;
    const publisherIdentityValid = isObject(publisherProof) &&
      publisherProof.repository === "hsaidno-cpu/pre-rpeds-shared-roadmap-dna" &&
      publisherProof.ref === "refs/heads/main" &&
      publisherProof.workflow_ref === "hsaidno-cpu/pre-rpeds-shared-roadmap-dna/.github/workflows/pre-release-publish.yml@refs/heads/main" &&
      typeof publisherProof.sha === "string" && /^[a-f0-9]{40}$/.test(publisherProof.sha);
    const issuerEnvelopeValid =
      releaseEvent.issuer?.identity === "https://token.actions.githubusercontent.com/hsaidno-cpu/pre-rpeds-shared-roadmap-dna" &&
      releaseEvent.issuer?.key_id === publisherProof?.sha &&
      releaseEvent.issuer?.identity_ref === releaseEvent.publisher_run_ref &&
      releaseEvent.source_commit === publisherProof?.sha;
    const independentRebuildVerified = body.independent_rebuild_verified === true &&
      body.independent_rebuild_commit === publisherProof?.sha &&
      body.independent_rebuild_sha256 === computedDigest &&
      typeof body.independent_rebuild_ref === "string" && body.independent_rebuild_ref.length > 0;
    if (!publisherIdentityValid || !issuerEnvelopeValid || !independentRebuildVerified) {
      await supabase.from("pre_kernel_releases").update({
        processing_state: "QUARANTINED",
        last_error: "Publisher OIDC identity or independent deterministic source rebuild verification is missing.",
        verification_evidence: {
          verifier_report: body,
          publisher_identity_valid: Boolean(publisherIdentityValid),
          issuer_envelope_valid: Boolean(issuerEnvelopeValid),
          independent_rebuild_verified: Boolean(independentRebuildVerified)
        }
      }).eq("event_id", eventId);
      return reply({ error: "publisher_identity_or_independent_rebuild_invalid_quarantined" }, 409);
    }
    if (!Array.isArray(body.evidence_refs) || body.evidence_refs.length === 0) {
      return reply({ error: "verifier_evidence_refs_required" }, 422);
    }

    const evidence = {
      artifact_digest: "PASS",
      issuer_signature: "PASS_GITHUB_OIDC_TOKEN_SIGNATURE_AND_WORKFLOW_IDENTITY",
      compatibility_contract: "PASS",
      compatibility_verified: true,
      evidence_refs: body.evidence_refs,
      verifier_identity: body.verifier_identity ?? "GITHUB_ACTIONS_INDEPENDENT_VERIFIER",
      computed_artifact_sha256: computedDigest,
      publisher_identity: publisherProof,
      independent_rebuild: "PASS",
      independent_rebuild_ref: body.independent_rebuild_ref,
      independent_rebuild_commit: body.independent_rebuild_commit,
      independent_rebuild_sha256: body.independent_rebuild_sha256,
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
    const releaseTargets = Array.isArray(release.payload?.target_host_ids) ? new Set(release.payload.target_host_ids) : null;
    for (const host of hosts ?? []) {
      if (releaseTargets && !releaseTargets.has(host.host_id)) continue;
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
    if (!(await authorizedHost(supabase, req, hostId))) return reply({ error: "host_unauthorized" }, 401);
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
    const hostSecret = await resolveSecret(supabase, hostAuth.host_auth_secret_ref);
    const oidcHost = hostId === "asfree-rpeds" ? await verifyGitHubOidc(req, "asfree-rpeds") : null;
    if (!oidcHost && (!hostSecret || !(await verifyHsoSignature(req, raw, hostSecret)))) {
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
    const oidcReconciler = await verifyGitHubOidc(req, "reconciler");
    if (!oidcReconciler && !(await verifyHsoSignature(req, raw, syncToken))) return reply({ error: "invalid_signature" }, 401);
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
