export function parseTargetHostIds(value: unknown): string[] | null {
  if (!Array.isArray(value) || value.length === 0) return null;
  const ids: string[] = [];
  const seen = new Set<string>();
  for (const candidate of value) {
    if (typeof candidate !== "string") return null;
    const id = candidate.trim();
    if (!id || seen.has(id)) return null;
    seen.add(id);
    ids.push(id);
  }
  return ids;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}

function isHttpsEvidenceRef(value: unknown): value is string {
  if (typeof value !== "string" || !value.trim()) return false;
  try {
    const url = new URL(value);
    return url.protocol === "https:" && Boolean(url.hostname) && !url.username && !url.password;
  } catch {
    return false;
  }
}

export function hasLiveRuntimeEvidence(value: unknown): boolean {
  if (!isRecord(value)) return false;
  if (!isHttpsEvidenceRef(value.deployment_ref) || !isHttpsEvidenceRef(value.runtime_invocation_ref)) return false;
  if (!Array.isArray(value.test_results) || value.test_results.length === 0) return false;
  if (value.test_results.some((test) => !isRecord(test) || test.status !== "PASS")) return false;
  return value.test_results.some((test) =>
    isRecord(test) &&
    test.scope === "LIVE_HOST_RUNTIME" &&
    test.status === "PASS" &&
    isHttpsEvidenceRef(test.evidence_ref)
  );
}
