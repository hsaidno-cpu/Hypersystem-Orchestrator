export const PRIORITY_WEIGHTS = Object.freeze({
  dependency_unlock_value: 0.25,
  risk_reduction: 0.25,
  critical_path_impact: 0.20,
  urgency: 0.15,
  effort_efficiency: 0.10,
  evidence_confidence: 0.05,
});

/**
 * Normalizes numeric IDs such as 10, 010 and HSO-010 to the same key.
 * Non-numeric stable IDs retain their uppercase identifier.
 * @param {unknown} value
 * @returns {string}
 */
export function normalizeWorkKey(value) {
  const raw = String(value ?? "").trim().toUpperCase().replace(/^HSO[-_]?/, "");
  if (!raw) return "";
  if (/^[0-9]+$/.test(raw)) return String(Number(raw));
  return raw;
}

/**
 * @param {{item_key?: unknown, external_id?: string}} item
 * @returns {string}
 */
export function taskId(item) {
  const raw = normalizeWorkKey(item.item_key);
  if (!raw) return String(item.external_id ?? "UNIDENTIFIED_TASK");
  return "HSO-" + (/^[0-9]+$/.test(raw) ? raw.padStart(3, "0") : raw);
}

/**
 * Priority is deterministic and is only applied after hard eligibility passes.
 * @param {Record<string, any>} item
 * @returns {number|null}
 */
export function calculatePriorityScore(item) {
  const keys = Object.keys(PRIORITY_WEIGHTS);
  for (const key of keys) {
    const value = item[key];
    if (value === null || value === undefined || !Number.isFinite(Number(value)) ||
        Number(value) < 0 || Number(value) > 100) return null;
  }
  return keys.reduce((sum, key) =>
    sum + Number(item[key]) * PRIORITY_WEIGHTS[key], 0);
}

/**
 * Calculates progress only from explicit positive scope weights.
 * A caller must supply the set of independently verified work-item IDs.
 * @param {Array<Record<string, any>>} items
 * @param {Set<string>} verifiedIds
 */
export function calculateWeightedProgress(items, verifiedIds) {
  const weighted = items.filter((item) =>
    Number.isFinite(Number(item.scope_weight)) && Number(item.scope_weight) > 0
  );
  const totalWeight = weighted.reduce((sum, item) => sum + Number(item.scope_weight), 0);
  const verifiedWeight = weighted
    .filter((item) => verifiedIds.has(String(item.id)))
    .reduce((sum, item) => sum + Number(item.scope_weight), 0);
  const pct = totalWeight > 0
    ? Math.round((verifiedWeight / totalWeight) * 10000) / 100
    : null;
  const coverage = items.length > 0
    ? Math.round((weighted.length / items.length) * 10000) / 100
    : null;
  return {
    total_work_items: items.length,
    weighted_work_items: weighted.length,
    unweighted_work_items: items.length - weighted.length,
    scope_weight_total: totalWeight,
    verified_weight: verifiedWeight,
    weighted_progress_pct: pct,
    weight_coverage_pct: coverage,
    verified_count: items.filter((item) => verifiedIds.has(String(item.id))).length,
    active_count: items.filter((item) => item.execution_state === "In progress").length,
    blocked_count: items.filter((item) =>
      item.execution_state === "Blocked" ||
      ["BLOCKED", "HOLD", "FAIL"].includes(String(item.gate_state))
    ).length,
    failed_count: items.filter((item) => item.gate_state === "FAIL").length,
    pending_approval_count: items.filter((item) => item.approval_state === "PENDING").length,
    measurement_state: weighted.length === 0
      ? "UNMEASURED"
      : weighted.length === items.length
        ? "MEASURED"
        : "PARTIAL_COVERAGE",
  };
}
