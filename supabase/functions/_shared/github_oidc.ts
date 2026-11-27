const GITHUB_JWKS_URL = "https://token.actions.githubusercontent.com/.well-known/jwks";
const JWKS_CACHE_TTL_MS = 5 * 60 * 1000;
let cachedJwks: { keys: JsonWebKey[]; expiresAt: number } | null = null;

export interface GitHubOidcPolicy {
  audience: string;
  repository: string;
  repositoryId?: string;
  workflowRef: string;
  allowedEvents: string[];
  branchRef?: string;
}

function decodeBase64Url(value: string): Uint8Array {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "=".repeat((4 - normalized.length % 4) % 4);
  const binary = atob(padded);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

function toArrayBuffer(bytes: Uint8Array): ArrayBuffer {
  const copy = new ArrayBuffer(bytes.byteLength);
  new Uint8Array(copy).set(bytes);
  return copy;
}

function constantTimeEqual(left: string, right: string): boolean {
  if (left.length !== right.length) return false;
  let mismatch = 0;
  for (let index = 0; index < left.length; index++) {
    mismatch |= left.charCodeAt(index) ^ right.charCodeAt(index);
  }
  return mismatch === 0;
}

async function getJwks(): Promise<JsonWebKey[]> {
  if (cachedJwks && cachedJwks.expiresAt > Date.now()) return cachedJwks.keys;
  const response = await fetch(GITHUB_JWKS_URL, {
    headers: { "accept": "application/json" },
    signal: AbortSignal.timeout(10000),
  });
  if (!response.ok) throw new Error("github_oidc_jwks_unavailable");
  const payload = await response.json();
  if (!Array.isArray(payload?.keys)) throw new Error("github_oidc_jwks_invalid");
  cachedJwks = { keys: payload.keys, expiresAt: Date.now() + JWKS_CACHE_TTL_MS };
  return cachedJwks.keys;
}

/**
 * Verify a short-lived GitHub Actions OIDC JWT for one exact repository,
 * branch, workflow file, event set and endpoint audience.
 *
 * The Supabase platform JWT gate remains disabled for this endpoint because
 * GitHub OIDC is not a Supabase Auth JWT. This function is the application
 * authentication boundary and fails closed on every mismatch.
 */
export async function verifyGitHubActionsOidc(
  request: Request,
  policy: GitHubOidcPolicy,
): Promise<Record<string, unknown> | null> {
  try {
    const authorization = request.headers.get("authorization") ?? "";
    const bearer = authorization.replace(/^Bearer\s+/i, "").trim();
    if (!bearer) return null;

    const parts = bearer.split(".");
    if (parts.length !== 3) return null;

    const header = JSON.parse(new TextDecoder().decode(decodeBase64Url(parts[0])));
    const claims = JSON.parse(new TextDecoder().decode(decodeBase64Url(parts[1])));
    if (header?.alg !== "RS256" || typeof header?.kid !== "string") return null;

    const now = Math.floor(Date.now() / 1000);
    const audience = Array.isArray(claims?.aud) ? claims.aud : [claims?.aud];
    const branchRef = policy.branchRef ?? "refs/heads/main";
    if (
      claims?.iss !== "https://token.actions.githubusercontent.com" ||
      !audience.includes(policy.audience) ||
      typeof claims?.exp !== "number" || claims.exp <= now ||
      (typeof claims?.nbf === "number" && claims.nbf > now + 60) ||
      (typeof claims?.iat === "number" && claims.iat > now + 60) ||
      claims?.repository !== policy.repository ||
      (policy.repositoryId && String(claims?.repository_id ?? "") !== policy.repositoryId) ||
      claims?.ref !== branchRef ||
      claims?.workflow_ref !== policy.workflowRef ||
      !policy.allowedEvents.includes(String(claims?.event_name ?? ""))
    ) return null;

    const jwks = await getJwks();
    const jwk = jwks.find((candidate: any) => candidate?.kid === header.kid && candidate?.kty === "RSA");
    if (!jwk) return null;

    const verificationKey = await crypto.subtle.importKey(
      "jwk",
      jwk,
      { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
      false,
      ["verify"],
    );
    const signingInput = new TextEncoder().encode(parts[0] + "." + parts[1]);
    const signatureValid = await crypto.subtle.verify(
      { name: "RSASSA-PKCS1-v1_5" },
      verificationKey,
      toArrayBuffer(decodeBase64Url(parts[2])),
      toArrayBuffer(signingInput),
    );
    return signatureValid ? claims as Record<string, unknown> : null;
  } catch (error) {
    console.error("github_oidc_verification_failed", {
      reason: error instanceof Error ? error.message : "unknown_error",
    });
    return null;
  }
}

/** Reset only for deterministic tests; never exposed by an Edge Function route. */
export function clearGitHubOidcJwksCacheForTests(): void {
  cachedJwks = null;
}
