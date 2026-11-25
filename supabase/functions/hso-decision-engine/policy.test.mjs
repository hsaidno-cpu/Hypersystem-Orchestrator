import test from "node:test";
import assert from "node:assert/strict";
import {
  PRIORITY_WEIGHTS, normalizeWorkKey, taskId, calculatePriorityScore,
  calculateWeightedProgress
} from "./policy.mjs";

const owner = "notion-user-1";
const approvedAt = "2026-11-25T08:00:00.000Z";
function scoped(id, itemKey, weight, extra = {}) {
  return {
    id, item_key: itemKey, execution_state: "Verified", gate_state: "PASS",
    scope_inclusion_state: "IN_SCOPE",
    scope_decision_by: owner, scope_decision_at: approvedAt,
    scope_decision_rationale: "Included in frozen project baseline.",
    scope_weight: weight, weight_rationale: "Relative delivery effort and impact.",
    scope_weight_approval: "APPROVED",
    scope_weight_approved_by: owner, scope_weight_approved_at: approvedAt,
    ...extra,
  };
}
const complete = { sourceComplete: true, scopeDrift: false };

test("normalizes numeric and prefixed task identifiers consistently", () => {
  assert.equal(normalizeWorkKey("10"), "10");
  assert.equal(normalizeWorkKey("010"), "10");
  assert.equal(normalizeWorkKey("HSO-010"), "10");
  assert.equal(normalizeWorkKey("hso_10"), "10");
  assert.equal(taskId({ item_key: "10" }), "HSO-010");
  assert.equal(taskId({ item_key: "HSO-010" }), "HSO-010");
});

test("priority weights total 100 and a complete candidate scores 100", () => {
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

test("fully decided scope and approved weights produce publishable weighted completion", () => {
  const items=[scoped("a","10",3),scoped("b","11",1,{execution_state:"Completed"}),scoped("c","12",2)];
  const out=calculateWeightedProgress(items,new Set(["a","c"]),complete);
  assert.equal(out.weighted_progress_pct,83.33);
  assert.equal(out.partial_weighted_progress_pct,null);
  assert.equal(out.weight_coverage_pct,100);
  assert.equal(out.scope_decision_coverage_pct,100);
  assert.equal(out.measurement_state,"MEASURED");
  assert.equal(out.is_publishable,true);
});

test("partial weight coverage never masquerades as project-wide percentage",()=>{
  const items=[
    scoped("a","10",3),
    scoped("b","11",null,{weight_rationale:null,scope_weight_approval:"PENDING",scope_weight_approved_by:null,scope_weight_approved_at:null}),
  ];
  const out=calculateWeightedProgress(items,new Set(["a"]),complete);
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.partial_weighted_progress_pct,100);
  assert.equal(out.weight_coverage_pct,50);
  assert.equal(out.measurement_state,"PARTIAL_COVERAGE");
  assert.equal(out.is_publishable,false);
});

test("scope decision missing suppresses all project percentage and weight coverage",()=>{
  const items=[scoped("a","10",3),{id:"b",item_key:"11",scope_inclusion_state:"PENDING"}];
  const out=calculateWeightedProgress(items,new Set(["a"]),complete);
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.partial_weighted_progress_pct,null);
  assert.equal(out.scope_decision_coverage_pct,50);
  assert.equal(out.measurement_state,"SCOPE_UNCONFIRMED");
});

test("owner-decided out-of-scope items are excluded from denominator",()=>{
  const outScope={
    id:"x",item_key:"99",scope_inclusion_state:"OUT_OF_SCOPE",
    scope_decision_by:owner,scope_decision_at:approvedAt,
    scope_decision_rationale:"Separate product roadmap, excluded by owner.",
    scope_weight:null,
  };
  const out=calculateWeightedProgress([scoped("a","10",5),outScope],new Set(["a"]),complete);
  assert.equal(out.weighted_progress_pct,100);
  assert.equal(out.in_scope_work_items,1);
  assert.equal(out.out_of_scope_work_items,1);
  assert.equal(out.is_publishable,true);
});

test("empty project is UNMEASURED rather than zero or 100 percent",()=>{
  const out=calculateWeightedProgress([],new Set(),complete);
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.measurement_state,"UNMEASURED");
  assert.equal(out.is_publishable,false);
});

test("no approved weights is UNMEASURED",()=>{
  const item=scoped("a","10",null,{weight_rationale:null,scope_weight_approval:"PENDING",scope_weight_approved_by:null,scope_weight_approved_at:null});
  const out=calculateWeightedProgress([item],new Set(),complete);
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.partial_weighted_progress_pct,null);
  assert.equal(out.weight_coverage_pct,0);
  assert.equal(out.measurement_state,"UNMEASURED");
});

test("source incompleteness suppresses numeric metrics",()=>{
  const out=calculateWeightedProgress([scoped("a","10",10)],new Set(["a"]),{sourceComplete:false});
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.weight_coverage_pct,null);
  assert.equal(out.total_work_items,null);
  assert.equal(out.measurement_state,"SOURCE_INCOMPLETE");
});

test("scope drift suppresses numeric metrics",()=>{
  const out=calculateWeightedProgress([scoped("a","10",10)],new Set(["a"]),{sourceComplete:true,scopeDrift:true});
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.measurement_state,"SCOPE_DRIFT");
});

test("duplicate normalized scope IDs prevent project-wide measurement",()=>{
  const out=calculateWeightedProgress([scoped("a","010",2),scoped("b","HSO-10",3)],new Set(["a"]),complete);
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.measurement_state,"SCOPE_CONFLICT");
  assert.deepEqual(out.conflicting_task_ids,["10"]);
});

test("missing stable scope ID prevents project-wide measurement",()=>{
  const out=calculateWeightedProgress([scoped("a","",2)],new Set(["a"]),complete);
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.measurement_state,"SCOPE_CONFLICT");
});

test("scope weights require rationale and explicit owner approval metadata",()=>{
  const item=scoped("a","10",10,{scope_weight_approval:"APPROVED",scope_weight_approved_by:null});
  const out=calculateWeightedProgress([item],new Set(["a"]),complete);
  assert.equal(out.weighted_progress_pct,null);
  assert.equal(out.weight_coverage_pct,0);
  assert.equal(out.measurement_state,"UNMEASURED");
});

test("Completed without independent verification is not counted as verified",()=>{
  const item=scoped("a","10",10,{execution_state:"Completed"});
  const out=calculateWeightedProgress([item],new Set(),complete);
  assert.equal(out.weighted_progress_pct,0);
  assert.equal(out.verified_count,0);
});
