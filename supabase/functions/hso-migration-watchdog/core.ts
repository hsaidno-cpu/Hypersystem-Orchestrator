export interface SourceBoundary {
  boundary_key: string;
  repository_full_name: string;
  commit_sha: string;
  visibility: "public" | "private";
  expected_blob_paths: number;
}

export const SOURCE_BOUNDARIES: SourceBoundary[] = [
  { boundary_key: "HSO", repository_full_name: "hsaidno-cpu/Hypersystem-Orchestrator", commit_sha: "69479c9fc898d12d6780964fb431fb9a89b1c675", visibility: "public", expected_blob_paths: 166 },
  { boundary_key: "HSMART", repository_full_name: "hsaidno-cpu/HSMART", commit_sha: "26bf979401499b503fc33f1dbe3247f495ad5659", visibility: "public", expected_blob_paths: 131 },
  { boundary_key: "SKILL_ANALYZER", repository_full_name: "hsaidno-cpu/skill-analyzer", commit_sha: "c469af7977c9bf6dcb3f5ab7b085a6de20d87004", visibility: "public", expected_blob_paths: 107 },
  { boundary_key: "ASFREE", repository_full_name: "hsaidno-cpu/A.S.F.R.E.E", commit_sha: "a5eb55db0f6c2c6126a7fbcba645caf44c660c93", visibility: "public", expected_blob_paths: 151 },
  { boundary_key: "ANATOMI_PROMPT", repository_full_name: "hsaidno-cpu/anatomi-prompt-strategis", commit_sha: "06b46b88ed7eddc437792fae715f255cbe4eb13d", visibility: "private", expected_blob_paths: 100 },
  { boundary_key: "VIDEO_EXPLAINER", repository_full_name: "promkespkmbinuang-coder/VIDEO-ANIMATION-EXPLAINER-PROMKES-PROMPT-CREATOR", commit_sha: "f8f8c0f29ff9d851fa75eba764978c24bdd79416", visibility: "public", expected_blob_paths: 177 },
  { boundary_key: "SDO", repository_full_name: "promkespkmbinuang-coder/SPDO", commit_sha: "9d3c4bc09179ff857df4f3819be83e1847571add", visibility: "public", expected_blob_paths: 8 },
  { boundary_key: "PHOTO_FIXER_CANDIDATE", repository_full_name: "hsaidno-cpu/Photo-Fixer", commit_sha: "95339901f84cdae861efcebd9820cb2e1efdc27d", visibility: "public", expected_blob_paths: 2 },
  { boundary_key: "PVEE_CANDIDATE", repository_full_name: "promkespkmbinuang-coder/CL-VAEPPC", commit_sha: "1ab0c41081ccdbb91cc9dec0a2864acd0de00d54", visibility: "public", expected_blob_paths: 3 },
  { boundary_key: "VCM_PRIVATE", repository_full_name: "hsaidno-cpu/vibe-coding-mentor", commit_sha: "84214752bb298002b96f9ff1c60e16b7a09e99d7", visibility: "private", expected_blob_paths: 24 },
];

export const PRIOR_HSAR_PATH_COUNT = 864;
export const DIRECT_GITHUB_PATH_COUNT = 869;
export const DIRECT_GITHUB_UNIQUE_BLOB_COUNT = 859;
export const HSO_PRIOR_REPORTED_BLOB_COUNT = 161;
export const HSO_DIRECT_BLOB_COUNT = 166;
export const HSO_OMITTED_ADDED_PATHS = [
  "contracts/ewo-routing-contracts.json",
  "docs/EWO-P0-TEST-PLAN.md",
  "docs/EXECUTIVE-WORKDAY-ORCHESTRATOR-INTEGRATION.md",
  "docs/VIBE-CODING-MENTOR-INTEGRATION.md",
  "plugin-instructions/executive-workday-orchestrator/SOURCE-POINTER.md",
  "plugin-instructions/vibe-coding-mentor/SOURCE-POINTER.md",
  "tests/test_ewo_routing_contracts.py",
];

export function constantTimeEqual(left: string, right: string): boolean {
  if (!left || left.length !== right.length) return false;
  let diff = 0;
  for (let i = 0; i < left.length; i++) diff |= left.charCodeAt(i) ^ right.charCodeAt(i);
  return diff === 0;
}

export function hex(bytes: Uint8Array): string {
  return Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("");
}

export async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const owned = new Uint8Array(new ArrayBuffer(bytes.byteLength));
  owned.set(bytes);
  return hex(new Uint8Array(await crypto.subtle.digest("SHA-256", owned.buffer)));
}

export async function gitBlobSha(bytes: Uint8Array): Promise<string> {
  const header = new TextEncoder().encode("blob " + bytes.length + "\0");
  const framed = new Uint8Array(new ArrayBuffer(header.length + bytes.length));
  framed.set(header, 0);
  framed.set(bytes, header.length);
  return hex(new Uint8Array(await crypto.subtle.digest("SHA-1", framed.buffer)));
}

export function boundedBatchSize(value: unknown, fallback = 16, max = 32): number {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.max(1, Math.min(max, Math.floor(n)));
}

export function countUniqueBlobShas(paths: Array<{ sha: string }>): {
  pathCount: number;
  uniqueBlobCount: number;
  duplicatePathRows: number;
} {
  const unique = new Set(paths.map((item) => item.sha));
  return {
    pathCount: paths.length,
    uniqueBlobCount: unique.size,
    duplicatePathRows: paths.length - unique.size,
  };
}

export function migrationAcceptanceState(input: {
  sourceTreesComplete: boolean;
  allUniqueBlobsVerified: boolean;
  allCapabilitiesParityAccepted: boolean;
  allRequiredTestsPassed: boolean;
  allRuntimeReceiptsPresent: boolean;
  securityAcceptancePassed: boolean;
}): "OPEN" | "SOURCE_VERIFIED" | "CAPABILITY_VERIFIED" | "RUNTIME_VERIFIED" | "COMPLETE" {
  if (!input.sourceTreesComplete) return "OPEN";
  if (!input.allUniqueBlobsVerified) return "OPEN";
  if (!input.allCapabilitiesParityAccepted || !input.allRequiredTestsPassed) return "SOURCE_VERIFIED";
  if (!input.allRuntimeReceiptsPresent || !input.securityAcceptancePassed) return "CAPABILITY_VERIFIED";
  return "COMPLETE";
}
