import {
  constantTimeEqual,
  isFreshSlackTimestamp,
  parseHsoCommand,
  redactLikelySecrets,
  slackSignature,
} from "./core.ts";

Deno.test("accepts timestamps within the five-minute window", () => {
  if (!isFreshSlackTimestamp("1700000000", 1700000000)) throw new Error("current timestamp rejected");
  if (!isFreshSlackTimestamp("1699999700", 1700000000)) throw new Error("inclusive boundary rejected");
  if (isFreshSlackTimestamp("1699999699", 1700000000)) throw new Error("stale timestamp accepted");
});

Deno.test("rejects malformed timestamps", () => {
  for (const value of ["", "abc", "1.2", "-1000", "999999999999999999999"]) {
    if (isFreshSlackTimestamp(value, 1000)) throw new Error("accepted " + value);
  }
});

Deno.test("compares signatures without accepting mismatches", () => {
  if (!constantTimeEqual("v0=abc", "v0=abc")) throw new Error("equal values rejected");
  if (constantTimeEqual("v0=abc", "v0=abd")) throw new Error("mismatch accepted");
  if (constantTimeEqual("short", "longer")) throw new Error("different lengths accepted");
});

Deno.test("parses only supported commands and requires arguments for mutations", () => {
  const status = parseHsoCommand("status");
  if (status?.name !== "status") throw new Error("status parse failed");
  const instruction = parseHsoCommand("instruction Build the control gateway");
  if (instruction?.arguments !== "Build the control gateway") throw new Error("instruction parse failed");
  if (parseHsoCommand("priority")) throw new Error("priority without arguments accepted");
  if (parseHsoCommand("not-a-command")) throw new Error("unknown command accepted");
});

Deno.test("redacts common bearer, API-token and secret assignments", () => {
  const result = redactLikelySecrets(
    "Bearer abcdefghijklmnop sk_abcdefghijklmnop HSO_SYNC_TOKEN=supersecretvalue",
  );
  if (result.includes("abcdefghijklmnop") || result.includes("supersecretvalue")) {
    throw new Error("likely secret was not redacted");
  }
});

Deno.test("builds Slack v0 request signature over timestamp and raw body", async () => {
  const signature = await slackSignature("test-signing-secret", "1700000000", "token=abc&text=status");
  if (!/^v0=[0-9a-f]{64}$/.test(signature)) throw new Error("signature format incorrect");
  const differentBody = await slackSignature("test-signing-secret", "1700000000", "token=abc&text=stop");
  if (constantTimeEqual(signature, differentBody)) throw new Error("body is not bound to signature");
});
