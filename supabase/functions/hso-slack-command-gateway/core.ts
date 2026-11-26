export type HsoCommandName =
  | "status"
  | "help"
  | "instruction"
  | "priority"
  | "pause"
  | "stop"
  | "freeze"
  | "resume"
  | "approve"
  | "reject"
  | "hold";

export interface ParsedHsoCommand {
  name: HsoCommandName;
  arguments: string;
}

const ALLOWED = new Set<HsoCommandName>([
  "status", "help", "instruction", "priority", "pause", "stop",
  "freeze", "resume", "approve", "reject", "hold",
]);

export function parseHsoCommand(input: string): ParsedHsoCommand | null {
  const normalized = input.trim();
  if (!normalized) return null;
  const firstSpace = normalized.search(/\s/);
  const rawName = firstSpace === -1 ? normalized : normalized.slice(0, firstSpace);
  const name = rawName.toLowerCase() as HsoCommandName;
  if (!ALLOWED.has(name)) return null;
  const args = firstSpace === -1 ? "" : normalized.slice(firstSpace).trim();
  if (!["status", "help"].includes(name) && !args) return null;
  return { name, arguments: args };
}

export function isFreshSlackTimestamp(
  timestamp: string,
  nowSeconds = Math.floor(Date.now() / 1000),
  toleranceSeconds = 300,
): boolean {
  if (!/^\d{10,}$/.test(timestamp)) return false;
  const value = Number(timestamp);
  return Number.isSafeInteger(value) && Math.abs(nowSeconds - value) <= toleranceSeconds;
}

export function constantTimeEqual(left: string, right: string): boolean {
  if (left.length !== right.length) return false;
  let difference = 0;
  for (let i = 0; i < left.length; i++) {
    difference |= left.charCodeAt(i) ^ right.charCodeAt(i);
  }
  return difference === 0;
}

export async function slackSignature(
  signingSecret: string,
  timestamp: string,
  rawBody: string,
): Promise<string> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(signingSecret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const digest = await crypto.subtle.sign(
    "HMAC",
    key,
    encoder.encode("v0:" + timestamp + ":" + rawBody),
  );
  const hex = [...new Uint8Array(digest)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
  return "v0=" + hex;
}

export function redactLikelySecrets(value: string): string {
  return value
    .replace(/\bBearer\s+[A-Za-z0-9._~+\/=-]{12,}/gi, "Bearer [REDACTED]")
    .replace(/\b(?:sk|rk|ghp|github_pat)_[A-Za-z0-9_-]{12,}\b/gi, "[REDACTED_TOKEN]")
    .replace(/\b([A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|API_KEY)[A-Z0-9_]*\s*[:=]\s*)\S+/gi, "$1[REDACTED]")
    .slice(0, 12000);
}
