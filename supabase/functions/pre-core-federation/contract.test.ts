import { hasLiveRuntimeEvidence, parseTargetHostIds } from "./contract.ts";
Deno.test("target host list must be non-empty, string-only and unique", () => {
  if (parseTargetHostIds(["asfree-rpeds", "pre-standalone"])?.length !== 2) throw new Error("valid target host list rejected");
  for (const invalid of [null, [], [" "], ["hso", 4], ["hso", "hso"]]) {
    if (parseTargetHostIds(invalid) !== null) throw new Error("invalid target host list accepted");
  }
});
Deno.test("live runtime verification requires deployment and invocation evidence", () => {
  const envelope = {
    deployment_ref: "https://deploy.example.com/releases/abc",
    runtime_invocation_ref: "https://logs.example.com/invocations/123",
    test_results: [{ scope: "LIVE_HOST_RUNTIME", status: "PASS", evidence_ref: "https://logs.example.com/tests/runtime-123" }],
  };
  if (!hasLiveRuntimeEvidence(envelope)) throw new Error("complete runtime evidence rejected");
});
Deno.test("CI-only evidence cannot produce runtime VERIFIED", () => {
  const ciOnly = {
    deployment_ref: "https://deploy.example.com/releases/abc",
    runtime_invocation_ref: "https://logs.example.com/invocations/123",
    test_results: [{ scope: "CI", status: "PASS", evidence_ref: "https://ci.example.com/run/1" }],
  };
  if (hasLiveRuntimeEvidence(ciOnly)) throw new Error("CI-only evidence accepted");
});
Deno.test("missing deployment reference cannot produce runtime VERIFIED", () => {
  const invalid = {
    deployment_ref: null,
    runtime_invocation_ref: "https://logs.example.com/invocations/123",
    test_results: [{ scope: "LIVE_HOST_RUNTIME", status: "PASS", evidence_ref: "https://logs.example.com/tests/runtime-123" }],
  };
  if (hasLiveRuntimeEvidence(invalid)) throw new Error("missing deployment reference accepted");
});
