import test from "node:test";
import assert from "node:assert/strict";
import { PRIORITY_WEIGHTS, normalizeWorkKey, taskId, calculatePriorityScore, calculateWeightedProgress } from "./policy.mjs";

test("normalizes numeric and prefixed task identifiers consistently", () => {
  assert.equal(normalizeWorkKey("10"), "10");
  assert.equal(normalizeWorkKey("010"), "10");
  assert.equal(normalizeWorkKey("HSO-010"), "10");
  assert.equal(normalizeWorkKey("hso_10"), "10");
  assert.equal(taskId({ item_key: "10" }), "HSO-010");
  assert.equal(taskId({ item_key: "HSO-010" }), "HSO-010");
});
test("priority weights sum to one and a complete candidate scores 100", () => {
  assert.equal(Object.values(PRIORITY_WEIGHTS).reduce((a,b)=>a+b,0),1);
  const candidate=Object.fromEntries(Object.keys(PRIORITY_WEIGHTS).map(key=>[key,100]));
  assert.equal(calculatePriorityScore(candidate),100);
});
test("priority score refuses missing or out-of-range factors", () => {
  assert.equal(calculatePriorityScore({dependency_unlock_value:100}),null);
  const invalid=Object.fromEntries(Object.keys(PRIORITY_WEIGHTS).map(key=>[key,50]));
  invalid.urgency=101;
  assert.equal(calculatePriorityScore(invalid),null);
});
test("weighted completion excludes unweighted work and discloses coverage", () => {
  const items=[
    {id:"a",scope_weight:3,execution_state:"Verified",gate_state:"PASS"},
    {id:"b",scope_weight:1,execution_state:"Completed",gate_state:"PASS"},
    {id:"c",scope_weight:null,execution_state:"Verified",gate_state:"PASS"}
  ];
  const out=calculateWeightedProgress(items,new Set(["a","c"]));
  assert.equal(out.weighted_progress_pct,75);
  assert.equal(out.weight_coverage_pct,66.67);
  assert.equal(out.measurement_state,"PARTIAL_COVERAGE");
  assert.equal(out.verified_weight,3);
});
test("no scope weights is UNMEASURED, not a guessed completion percentage",()=>{
  const out=calculateWeightedProgress([{id:"a",scope_weight:null},{id:"b"}],new Set(["a","b"]));
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.weight_coverage_pct,0);
  assert.equal(out.measurement_state,"UNMEASURED");
});
test("Completed without independent verification is not counted as verified",()=>{
  const out=calculateWeightedProgress([{id:"a",scope_weight:10,execution_state:"Completed",gate_state:"PASS"}],new Set());
  assert.equal(out.weighted_progress_pct,0);
  assert.equal(out.verified_count,0);
});
