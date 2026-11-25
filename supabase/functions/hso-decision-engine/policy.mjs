export const PRIORITY_WEIGHTS = Object.freeze({
  dependency_unlock_value: 0.25,
  risk_reduction: 0.25,
  critical_path_impact: 0.20,
  urgency: 0.15,
  effort_efficiency: 0.10,
  evidence_confidence: 0.05,
});

/** Normalize stable IDs without conflating non-numeric identifiers. */
export function normalizeWorkKey(value) {
  const raw = String(value ?? "").trim().toUpperCase().replace(/^HSO[-_]?/, "");
  if (!raw) return "";
  if (/^[0-9]+$/.test(raw)) return String(Number(raw));
  return raw;
}

/** @param {{item_key?: unknown, external_id?: string}} item */
export function taskId(item) {
  const raw = normalizeWorkKey(item.item_key);
  if (!raw) return String(item.external_id ?? "UNIDENTIFIED_TASK");
  return "HSO-" + (/^[0-9]+$/.test(raw) ? raw.padStart(3, "0") : raw);
}

/** Ranking is deterministic and only runs after eligibility gates. */
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

function nonEmpty(value) {
  return typeof value === "string" && value.trim().length > 0;
}

export function hasScopeDecision(item) {
  return ["IN_SCOPE", "OUT_OF_SCOPE"].includes(item.scope_inclusion_state) &&
    nonEmpty(item.scope_decision_by) &&
    Boolean(item.scope_decision_at) &&
    nonEmpty(item.scope_decision_rationale);
}

export function hasApprovedWeight(item) {
  return Number.isFinite(Number(item.scope_weight)) &&
    Number(item.scope_weight) > 0 &&
    nonEmpty(item.weight_rationale) &&
    item.scope_weight_approval === "APPROVED" &&
    nonEmpty(item.scope_weight_approved_by) &&
    Boolean(item.scope_weight_approved_at);
}

/**
 * Publish a project-wide percentage only when the source snapshot is complete,
 * scope membership is decided for every item, in-scope IDs are unique and every
 * in-scope item has an owner-approved positive weight. Otherwise keep the
 * project-wide value null. A separately named partial ratio is diagnostic only.
 *
 * @param {Array<Record<string, any>>} items
 * @param {Set<string>} verifiedIds IDs independently verified by the caller.
 * @param {{sourceComplete?:boolean,scopeDrift?:boolean}} options
 */
export function calculateWeightedProgress(items, verifiedIds, options = {}) {
  const sourceComplete = options.sourceComplete === true;
  const scopeDrift = options.scopeDrift === true;
  const reasons = [];
  const observedCount = items.length;

  if (!sourceComplete) reasons.push("SOURCE_INCOMPLETE");
  if (scopeDrift) reasons.push("SCOPE_DRIFT");

  const hardIncomplete = !sourceComplete || scopeDrift;
  if (hardIncomplete) {
    return {
      data_complete: false,
      observed_work_item_count: observedCount,
      total_work_items: null,
      in_scope_work_items: null,
      out_of_scope_work_items: null,
      weighted_work_items: null,
      unweighted_work_items: null,
      scope_weight_total: null,
      verified_weight: null,
      weighted_progress_pct: null,
      partial_weighted_progress_pct: null,
      weight_coverage_pct: null,
      scope_decision_coverage_pct: null,
      weight_approval_coverage_pct: null,
      verified_count: null,
      active_count: null,
      blocked_count: null,
      failed_count: null,
      pending_approval_count: null,
      measurement_state: scopeDrift ? "SCOPE_DRIFT" : "SOURCE_INCOMPLETE",
      measurement_reasons: reasons,
      is_publishable: false,
    };
  }

  if (observedCount === 0) {
    return {
      data_complete: true,
      observed_work_item_count: 0,
      total_work_items: 0,
      in_scope_work_items: 0,
      out_of_scope_work_items: 0,
      weighted_work_items: 0,
      unweighted_work_items: 0,
      scope_weight_total: 0,
      verified_weight: 0,
      weighted_progress_pct: null,
      partial_weighted_progress_pct: null,
      weight_coverage_pct: null,
      scope_decision_coverage_pct: null,
      weight_approval_coverage_pct: null,
      verified_count: 0,
      active_count: 0,
      blocked_count: 0,
      failed_count: 0,
      pending_approval_count: 0,
      measurement_state: "UNMEASURED",
      measurement_reasons: ["NO_WORK_ITEMS"],
      is_publishable: false,
    };
  }

  const decided = items.filter(hasScopeDecision);
  const scopeDecisionCoverage = Math.round((decided.length / observedCount) * 10000) / 100;
  if (decided.length !== observedCount) reasons.push("SCOPE_DECISION_MISSING");

  // Do not infer the denominator while one or more scope decisions are missing.
  if (decided.length !== observedCount) {
    return {
      data_complete: true,
      observed_work_item_count: observedCount,
      total_work_items: observedCount,
      in_scope_work_items: null,
      out_of_scope_work_items: null,
      weighted_work_items: null,
      unweighted_work_items: null,
      scope_weight_total: null,
      verified_weight: null,
      weighted_progress_pct: null,
      partial_weighted_progress_pct: null,
      weight_coverage_pct: null,
      scope_decision_coverage_pct: scopeDecisionCoverage,
      weight_approval_coverage_pct: null,
      verified_count: null,
      active_count: null,
      blocked_count: null,
      failed_count: null,
      pending_approval_count: null,
      measurement_state: "SCOPE_UNCONFIRMED",
      measurement_reasons: reasons,
      is_publishable: false,
    };
  }

  const inScope = items.filter((item) => item.scope_inclusion_state === "IN_SCOPE");
  const outOfScope = items.filter((item) => item.scope_inclusion_state === "OUT_OF_SCOPE");
  if (inScope.length === 0) reasons.push("NO_IN_SCOPE_WORK_ITEMS");

  const keyCounts = new Map();
  const missingIds = [];
  for (const item of inScope) {
    const key = normalizeWorkKey(item.item_key);
    if (!key) missingIds.push(item.id);
    else keyCounts.set(key, (keyCounts.get(key) ?? 0) + 1);
  }
  const duplicateKeys = [...keyCounts.entries()].filter(([, count]) => count > 1).map(([key]) => key);
  if (missingIds.length) reasons.push("STABLE_TASK_ID_MISSING");
  if (duplicateKeys.length) reasons.push("DUPLICATE_SCOPE_TASK_ID");

  // Ambiguous scope identity makes the numerator and denominator untrustworthy.
  if (missingIds.length || duplicateKeys.length) {
    return {
      data_complete: true,
      observed_work_item_count: observedCount,
      total_work_items: observedCount,
      in_scope_work_items: inScope.length,
      out_of_scope_work_items: outOfScope.length,
      weighted_work_items: null,
      unweighted_work_items: null,
      scope_weight_total: null,
      verified_weight: null,
      weighted_progress_pct: null,
      partial_weighted_progress_pct: null,
      weight_coverage_pct: null,
      scope_decision_coverage_pct: 100,
      weight_approval_coverage_pct: null,
      verified_count: null,
      active_count: null,
      blocked_count: null,
      failed_count: null,
      pending_approval_count: null,
      measurement_state: "SCOPE_CONFLICT",
      measurement_reasons: reasons,
      conflicting_task_ids: duplicateKeys,
      missing_task_ids: missingIds,
      is_publishable: false,
    };
  }

  const approvedWeighted = inScope.filter(hasApprovedWeight);
  const approvedIds = new Set(approvedWeighted.map((item) => String(item.id)));
  const unweighted = inScope.length - approvedWeighted.length;
  const totalWeight = approvedWeighted.reduce((sum, item) => sum + Number(item.scope_weight), 0);
  const verifiedWeight = approvedWeighted
    .filter((item) => verifiedIds.has(String(item.id)))
    .reduce((sum, item) => sum + Number(item.scope_weight), 0);
  const partialPct = totalWeight > 0
    ? Math.round((verifiedWeight / totalWeight) * 10000) / 100
    : null;
  const coverage = inScope.length > 0
    ? Math.round((approvedWeighted.length / inScope.length) * 10000) / 100
    : null;
  const approvalCoverage = coverage;

  if (inScope.length === 0) {
    // Empty scope is not 100% complete. It is a missing/invalid baseline.
  } else if (unweighted > 0) {
    reasons.push("WEIGHT_APPROVAL_INCOMPLETE");
  }

  const publishable = inScope.length > 0 && unweighted === 0 && totalWeight > 0;
  return {
    data_complete: true,
    observed_work_item_count: observedCount,
    total_work_items: observedCount,
    in_scope_work_items: inScope.length,
    out_of_scope_work_items: outOfScope.length,
    weighted_work_items: approvedWeighted.length,
    unweighted_work_items: unweighted,
    scope_weight_total: totalWeight,
    verified_weight: verifiedWeight,
    weighted_progress_pct: publishable ? partialPct : null,
    partial_weighted_progress_pct: publishable ? null : partialPct,
    weight_coverage_pct: coverage,
    scope_decision_coverage_pct: scopeDecisionCoverage,
    weight_approval_coverage_pct: approvalCoverage,
    verified_count: inScope.filter((item) => verifiedIds.has(String(item.id))).length,
    active_count: inScope.filter((item) => item.execution_state === "In progress").length,
    blocked_count: inScope.filter((item) =>
      item.execution_state === "Blocked" ||
      ["BLOCKED", "HOLD", "FAIL"].includes(String(item.gate_state))
    ).length,
    failed_count: inScope.filter((item) => item.gate_state === "FAIL").length,
    pending_approval_count: inScope.filter((item) => item.approval_state === "PENDING").length,
    measurement_state: publishable
      ? "MEASURED"
      : inScope.length === 0
        ? "UNMEASURED"
        : approvedWeighted.length > 0
          ? "PARTIAL_COVERAGE"
          : "UNMEASURED",
    measurement_reasons: reasons.length ? reasons : (publishable ? [] : ["NO_APPROVED_WEIGHTS"]),
    is_publishable: publishable,
  };
}
