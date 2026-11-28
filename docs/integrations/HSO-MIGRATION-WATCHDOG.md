# HSO Migration Watchdog — runtime contract

**Function:** hso-migration-watchdog  
**Mode:** read-only source inventory, bounded Git blob verification and 289-skill metadata inventory seed. It does not modify plugin source, publish releases, assign licences or invoke plugin runtimes.

## Runtime flow
1. Verify x-hso-migration-token using a restricted database RPC against a digest stored in Supabase Vault.
2. Claim a 15-minute database lease to prevent concurrent workers.
3. Enumerate ten pinned source trees.
4. Store every path, repo, commit, blob SHA and byte size.
5. Deduplicate by Git blob SHA while preserving all original path links.
6. Read at most 16 pending blob payloads per run (hard maximum 32); recompute Git's blob SHA-1 over `blob <length>\0<bytes>`; compute SHA-256; record verification state. Payload bytes are not persisted.
7. Seed 289 skill metadata records from the pinned HSO snapshot; parity/tests/runtime remain NOT_ASSESSED or NOT_RUN.
8. Persist a run receipt and counts. No plugin becomes VERIFIED.

## Current baseline
10 pinned source boundaries; 869 path records; 859 unique Git blob IDs. Historical HSAR denominator 864 remains unresolved against direct Git tree inventory (HSO 166 vs prior 161). The worker will report discrepancies rather than force the old count.

## Secrets and private sources
- Function token is generated and stored only in Supabase Vault as hso_migration_watchdog_token.
- Optional GitHub read-only token stored as hso_github_read_token.
- Private Anatomi and VCM source trees remain PRIVATE_ACCESS_PENDING until that token is supplied and permitted.
- Public GitHub recursive-tree read does not require a token, but API rate limits are recorded.

## Live activation and first receipt — 26 November 2026

The background migration worker is now **ACTIVE** in Supabase:
- Edge Function: `hso-migration-watchdog`, deployed version **4**, status ACTIVE. JWT verification is disabled only for this function because the handler authenticates a dedicated Vault-backed bearer token; Supabase gateway access also uses the publishable API key.
- Database migration applied: `20261126033330_hso_migration_watchdog_foundation_v1`.
- Cron job: `hso-migration-watchdog`, active schedule `17 */2 * * *` (every two hours at minute 17 UTC).
- An authenticated manual invocation returned HTTP **200** and created run receipt `8fd7091b-446f-438d-9a8b-36379013f052`.
- First corrected scan state: **PARTIAL**, not COMPLETE. It enumerated 8/10 boundaries, 745 path records and 735 unique Git blob IDs; 10 duplicate path rows; 32 blob payloads hash-verified over two manual batches; 703 remain pending; 0 read failures; all 289 capability metadata rows are seeded; 0 capabilities accepted.
- Anatomi Prompt private (100 blobs) and Vibe Coding Mentor private (24 blobs) remain PRIVATE_ACCESS_PENDING because no owner-authorized read-only GitHub token has been stored in Vault.
- The prior 864 count remains a historical denominator; direct tree baseline is 869/859. The live database contains only eight scanned public/candidate boundaries until the two private sources are authorized.

The function and cron are live, but the **full migration remains OPEN**. The first scan exposed and corrected an FK insert-order defect; subsequent exact-head CI passed. Do not infer completion from HTTP 200 or an active cron row.

- The worker is not the generic skill invocation gateway.
- It does not write or distribute package content.
- It does not semantically review content or run capability tests.
- It never marks parity, runtime, rights or security acceptance on its own.
- Slack `/hso` ingress in PR #43 is separate and remains NOT_DEPLOYED / DISPATCH_DISABLED until Slack App signing secret, team ID, GOV-01 identity, merge, deployment and acceptance tests are completed.


## GitHub rate-limit behavior

The worker now classifies authenticated/unauthenticated GitHub 403 responses with exhausted rate-limit headers as `rate_limited`. A prior completed tree/path inventory is preserved; a rate-limited blob fetch returns to `pending` and is retried on a later schedule. Do not count rate-limit deferral as content corruption. Store an owner-authorized least-privilege GitHub read-only token in Vault as `hso_github_read_token`; it should cover public repositories and the two private sources (Anatomi Prompt and Vibe Coding Mentor).