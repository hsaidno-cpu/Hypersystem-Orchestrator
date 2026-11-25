import { test } from "node:test";

// The handler under test uses Fetch/Web Crypto APIs also provided by Node.
// This shim lets the same Deno.test cases execute in the repository's unittest CI.
globalThis.Deno = { test };
await import("../supabase/functions/hso-github-webhook/handler_test.ts");
