# HSAR Comparative Analysis Output Contract — 4+2

**Version:** 0.3.0  
**Status:** Proposed in PR; not merged

## 1. Activation

Activate when the user explicitly requests comparison, benchmarking, ranking, alternatives assessment, feature comparison or comparative evaluation.

All four core analysis tables remain mandatory:
1. Cross-method analysis.
2. Positive analysis.
3. Negative/root-cause analysis.
4. Negative-to-positive conversion.

Append two comparison tables:
5. Comparative scorecard comparing the four analytical dimensions across all target objects.
6. Feature-gap and evaluative recommendation table.

The fifth table synthesizes the first four; it does not replace them. The sixth converts evidenced differences into testable target-state recommendations.

## 2. Anchored qualitative/quantitative rubric

Use a 0–5 scale only when the criterion has a defined operational meaning and enough comparable evidence:

| Score | Anchor | Classification |
|---:|---|---|
| 0 | Verified absent or demonstrably fails in declared scope | VERIFIED_ABSENT |
| 1 | Very weak; materially fails criterion | CRITICAL_GAP |
| 2 | Weak; below baseline | WEAK |
| 3 | Adequate; meets declared baseline | ADEQUATE |
| 4 | Strong; materially exceeds baseline | STRONG |
| 5 | Exceptional relative to a declared comparator | LEADING |

Use N/A for unknown, inaccessible, untested or non-comparable evidence. Unknown is N/A, not zero. Keep evidence coverage and confidence separate from the score. DOCUMENTED_ONLY is not runtime-proven. Score absence only when the declared scope was adequately examined and absence was verified.

## 3. Table 5 — Comparative scorecard

| Comparison ID | Dimension/criterion | Object | Value and rationale | Score (0–5/N/A) | Classification | Evidence coverage | Confidence | Positive evidence | Negative evidence | Conversion progress | Comparative delta | Caveat |
|---|---|---|---|---:|---|---|---|---|---|---|---|---|

Score every object using the same operational definition, source/version window, scan depth and relevant test baseline. If evidence is mismatched, report non-comparability instead of manufacturing a rank.

Value describes an evidence-backed value mechanism, not an invented monetary valuation. Currency/ROI requires source data and disclosed assumptions.

## 4. Table 6 — Feature-gap and evaluative recommendations

| Gap ID | Object | Feature/capability | Current state/evidence | Target/benchmark | Gap description | Current score | Target score | Gap score | Value/opportunity | Evaluative suggestion | Priority/classification | Effort/cost basis | Acceptance test/indicator | Confidence/residual risk |
|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|

Gap score = target score - current score only when both values use the same anchored rubric. Preserve N/A when evidence is insufficient.

Every evaluative suggestion must identify the action, benefit mechanism, trade-off, dependency, owner role, reversibility, acceptance test and residual risk.

## 5. Fairness and aggregation

- Freeze object identity, version, commit, scope, time window and scan depth.
- Use matched data/samples and common tests where possible.
- Record missing, denied, skipped and excluded evidence per object.
- Distinguish PRESENT_VERIFIED, PRESENT_UNVERIFIED, ABSENT_VERIFIED, PARTIAL, UNKNOWN and NOT_APPLICABLE.
- Preserve tie, dissent and inconclusive outcomes.
- Do not rank an object higher merely because it documents more features or runs more tests.
- Do not aggregate scores by default. If aggregation is justified, disclose weights, formula, denominator, N/A treatment and sensitivity analysis.
- A hard P0/P1 security, integrity, privacy or authority gate cannot be offset by a high average.

## 6. Report close

After six tables, include critical notes, trade-offs, score interpretation, recommendation and disposition, prioritized roadmap, acceptance criteria, residual risks and human decision gates. Conclude whether evidence supports a rank, conditional preference, tie or no reliable conclusion.
