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

## Activation gates
Deploy the Edge Function; apply its schema/RPC/Vault/cron migration; verify scheduled request and run receipt; then mark the watchdog worker ACTIVE. Code on a Git branch or a cron row alone is not runtime acceptance.
- The worker is not the generic skill invocation gateway.
- It does not write or distribute package content.
- It never marks semantic parity, runtime, or security acceptance on its own.
