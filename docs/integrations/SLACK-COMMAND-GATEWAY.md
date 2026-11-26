# HSO Slack Command Gateway

**Status:** IMPLEMENTED_IN_BRANCH / NOT_DEPLOYED / NOT_LIVE / DISPATCH_DISABLED  
**Scope:** Slash-command ingress, GOV-01 identity allowlist, idempotent command intake, durable outbox and append-only ingress audit.  
**Non-goal:** This component is not an autonomous executor, approval issuer, GitHub writer, Notion synchronizer or always-on worker.

## Architecture

Slack /hso -> hso-slack-command-gateway -> HMAC/timestamp validation -> team/channel/user allowlist -> hso_slack_commands -> hso_command_outbox -> future governed worker -> evidence/receipt.

The request handler acknowledges Slack quickly and records an intent. It does not treat receipt as execution. The worker must independently revalidate permissions, policy version, target scope, dependency state, source freshness and approval requirements before taking action.

## Slack workspace channels provisioned

| Channel | Channel ID | Purpose |
|---|---|---|
| #hso-control-room | C0CM4C3BBGR | GOV-01 instructions and operational control requests |
| #hso-approvals | C0CMWSBAN8G | Private approval workflow; no approval buttons are active yet |
| #hso-operations | C0CM0GCQT7Y | Run and synchronization reports |
| #hso-security-incidents | C0CLM4823D5 | Private security and integration failures |

The connector can post/read messages and create channels, but it does not configure the Slack App, slash-command Request URL, Events API or Interactivity Request URL.

## Endpoint

After the Edge Function is deployed:

https://ehgmtkkppmceaffhwcpc.supabase.co/functions/v1/hso-slack-command-gateway

Create a Slack App with one slash command:
- Command: /hso
- Request URL: the endpoint above
- Method: POST
- Request signing: Slack's standard v0 signature
- Do not expose the signing secret in Slack messages, GitHub, source code or client-side settings.

The endpoint verifies X-Slack-Request-Timestamp within a five-minute window and the HMAC-SHA256 signature over v0:{timestamp}:{raw_body}. It checks the exact Slack team, control channel and GOV-01 user ID. It rejects missing configuration and does not use a legacy unsigned fallback.

## Required Supabase Edge Function secrets/configuration

Configure these through Supabase's secret manager/dashboard only. Never paste them into Slack or a repository.

- SLACK_SIGNING_SECRET: Slack App Signing Secret.
- HSO_SLACK_TEAM_ID: exact Slack workspace/team ID.
- HSO_SLACK_CONTROL_CHANNEL_ID: C0CM4C3BBGR.
- HSO_GOV01_SLACK_USER_ID: the verified GOV-01 Slack user ID, currently observed as U0CL2EC0CEB.
- HSO_COMMAND_RECEIVE_ENABLED: set to true only after the above identity and signature settings are read back and verified.
- HSO_COMMAND_DISPATCH_ENABLED: remain false until a separate governed worker, queue claim protocol, cancellation semantics and end-to-end tests are accepted.

Supabase-provided SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are used server-side only. The service-role key must never be exposed to Slack, a browser or a GitHub artifact.

## Command contract

- /hso status: read-only snapshot of source status and the latest recorded sync run.
- /hso help: display command contract.
- /hso instruction <brief>: record an instruction request for HSO planning.
- /hso priority <item> <priority>: record a priority-change request for dependency-aware evaluation.
- /hso pause <scope>, /hso stop <run-id>, /hso freeze <reason>, /hso resume <scope>: record control requests. They do not claim to pause or cancel a worker until a worker receipt confirms it.
- approve, reject and hold are deliberately blocked in v1. Approval requires a HAP-01 receipt bound to Action ID, operation, scope, repository, base/head SHA, evidence digest, expiry and one-time nonce.

Commands are accepted only from the configured GOV-01 identity in the designated control room. A non-GOV-01 user receives an access-denied response.

## Persistence and delivery semantics

- Slack trigger_id plus team ID is the idempotency key.
- Command arguments are redacted for common token/secret patterns and size-limited.
- Command intake and outbox writes are separate durable records.
- If only one of command/outbox/audit writes succeeds, the command is marked blocked_incomplete_persistence and not dispatched; reconciliation is required.
- hso_slack_command_audit has an append-only trigger and grants that exclude update/delete.
- No approval receipt, GitHub mutation, Notion mutation, roadmap update or worker dispatch is performed by this ingress.

## Activation sequence

1. Review and merge this PR only after exact-head CI and technical/security review pass.
2. Apply the additive database migration and verify RLS/grants plus table read-back.
3. Deploy the Edge Function and verify deployed source digest/version.
4. Configure the Slack App slash command Request URL and install/reinstall the app.
5. Provision secrets/configuration through Supabase secret management and verify presence without reading secret values.
6. Test valid signature, invalid signature, stale timestamp, wrong workspace, wrong channel, non-GOV-01 identity, duplicate trigger, partial persistence and oversized body.
7. Verify the database rows and Slack ephemeral replies.
8. Keep dispatch disabled until a separately reviewed worker implements row leasing, bounded retries, dead-letter handling, pause/stop/freeze cancellation, idempotent side effects and invocation receipts.
9. Enable dispatch only after HAP-01 approval and exact-scope runtime acceptance.

## Current external blockers

- The Slack connector cannot configure a Slack App or its callback URL.
- The authenticated Slack workspace list did not return a team ID; obtain the exact ID from Slack App configuration.
- The deployed Supabase project currently has no Vault secrets, no pg_cron schema/job and no successful sync-run or integration-event records.
- All five HSO source rows were read as not_configured.
- Existing Edge Functions are ACTIVE, but this is not proof of successful sync.
- Current deployed hso-github-webhook v4 still contains a legacy raw GitHub signature fallback. Draft PR #29 removes that fallback and adds replay protection, but its branch is not the deployed function.

## Acceptance receipt requirements

The integration is not LIVE until all of the following exist:
- GitHub merge SHA and exact-head CI result.
- Applied migration version and RLS/grant read-back.
- Active Edge Function version and source digest.
- Slack App installation plus exact signing validation tests.
- GOV-01 user/team/channel allowlist read-back.
- Successful command insert + outbox + append-only audit + duplicate suppression.
- A scheduled reconciliation run with source completeness and a source snapshot.
- Live Notion/GitHub read-back with source timestamps and content digest.
- Worker dispatch and pause/stop/recovery receipts.
