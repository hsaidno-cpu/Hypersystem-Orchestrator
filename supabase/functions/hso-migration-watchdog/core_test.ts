import {
  SOURCE_BOUNDARIES,
  PRIOR_HSAR_PATH_COUNT,
  DIRECT_GITHUB_PATH_COUNT,
  DIRECT_GITHUB_UNIQUE_BLOB_COUNT,
  HSO_OMITTED_ADDED_PATHS,
  boundedBatchSize,
  constantTimeEqual,
  countUniqueBlobShas,
  gitBlobSha,
  migrationAcceptanceState,
} from "./core.ts";

Deno.test("source manifest retains ten pinned boundaries and the direct tree baseline", () => {
  if (SOURCE_BOUNDARIES.length !== 10) throw new Error("expected ten source boundaries");
  const total = SOURCE_BOUNDARIES.reduce((sum, source) => sum + source.expected_blob_paths, 0);
  if (total !== DIRECT_GITHUB_PATH_COUNT || total !== 869) throw new Error("source count mismatch");
  if (PRIOR_HSAR_PATH_COUNT !== 864 || DIRECT_GITHUB_UNIQUE_BLOB_COUNT !== 859) throw new Error("historical baseline lost");
  if (HSO_OMITTED_ADDED_PATHS.length !== 7) throw new Error("HSO delta paths incomplete");
});

Deno.test("Git object hashing matches the canonical empty blob SHA", async () => {
  const digest = await gitBlobSha(new Uint8Array());
  if (digest !== "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391") throw new Error("empty Git blob SHA mismatch");
});

Deno.test("content deduplication counts unique Git objects while preserving path count", () => {
  const result = countUniqueBlobShas([
    { sha: "a" }, { sha: "b" }, { sha: "a" }, { sha: "c" }, { sha: "b" },
  ]);
  if (result.pathCount !== 5 || result.uniqueBlobCount !== 3 || result.duplicatePathRows !== 2) {
    throw new Error("deduplication metrics incorrect");
  }
});

Deno.test("batch size is bounded and cannot be expanded by untrusted request payloads", () => {
  if (boundedBatchSize(999, 16, 32) !== 32) throw new Error("upper bound not enforced");
  if (boundedBatchSize(-4, 16, 32) !== 1) throw new Error("lower bound not enforced");
  if (boundedBatchSize("not-a-number", 16, 32) !== 16) throw new Error("fallback not applied");
});

Deno.test("secret comparison rejects empty and mismatched values", () => {
  if (!constantTimeEqual("secret-value", "secret-value")) throw new Error("valid value rejected");
  if (constantTimeEqual("secret-value", "secret-valuf")) throw new Error("mismatch accepted");
  if (constantTimeEqual("", "")) throw new Error("empty token accepted");
});

Deno.test("acceptance never marks migration complete with missing test/runtime receipts", () => {
  const state = migrationAcceptanceState({
    sourceTreesComplete: true,
    allUniqueBlobsVerified: true,
    allCapabilitiesParityAccepted: true,
    allRequiredTestsPassed: false,
    allRuntimeReceiptsPresent: false,
    securityAcceptancePassed: false,
  });
  if (state !== "SOURCE_VERIFIED") throw new Error("acceptance gate bypassed");
});

Deno.test("partial source trees keep the migration acceptance open", () => {
  const state = migrationAcceptanceState({
    sourceTreesComplete: false,
    allUniqueBlobsVerified: false,
    allCapabilitiesParityAccepted: false,
    allRequiredTestsPassed: false,
    allRuntimeReceiptsPresent: false,
    securityAcceptancePassed: false,
  });
  if (state !== "OPEN") throw new Error("incomplete source marked as accepted");
});
