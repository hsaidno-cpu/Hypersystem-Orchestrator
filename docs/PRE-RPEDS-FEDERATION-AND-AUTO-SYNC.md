# PRE–RPEDS Shared DNA and Automatic Release Synchronization

## Identity and merger

PRE Standalone and RPEDS are two first-class manifestations of one jointly evolved roadmap competency. PRE remains independently usable. RPEDS remains the native A.S.F.R.E.E roadmap workstream with its identity, four original modules, host procedures and M00/O01–O12 integration. The merger is at the shared DNA kernel, not an alias or replacement.

The shared kernel owns R0–R9 lifecycle semantics, roadmap object model, dependency, evidence, progress, gate and adaptation contracts, process audit, assurance/closure, capability learning, next-action/prompt contracts and release lineage. Host-specific extensions remain separate. Two-way contributions become shared DNA only after sanitization, provenance, validation and approval.

## Automatic release flow

PRE release published → authenticated event → provenance and digest verification → contract/SemVer compatibility → host AFSA policy decision → host regression → gated or eligible auto-adoption → target read-back → per-host adoption receipt.

The HSO Supabase registry contains pre_kernel_releases, pre_host_subscriptions, pre_host_adoption_receipts and pre_capability_contributions. RLS is enabled, anon/authenticated access is revoked and service_role has explicit policies.

## Edge Function

Supabase Edge Function pre-core-federation is deployed at version 5 in project ehgmtkkppmceaffhwcpc. Deployment read-back SHA-256: `195b8ff3cc611a3caea38c786146012ddd3212760b7849e52225a812a102079a`.

- GET /health reports service availability/configuration only.
- POST /release accepts a release envelope after HMAC verification using HSO_SYNC_TOKEN; event and idempotency keys are unique. Per-host receipts are created. Unverified host profiles are held.
- GET /latest?host_id=... requires the host-specific token named by host_auth_secret_ref.
- POST /adoption requires a host-specific HMAC signature. VERIFIED is rejected unless all tests are PASS and read-back version/digest match the release event.

Host auth references store environment variable names, not credential values. The values must be provisioned for each host. Missing host credentials fail closed with host_auth_not_configured.

## Deployed versus not yet live

Deployed: four registry tables, RLS/service-role permissions, explicit service-role policies, four initial host records, host auth references and Edge Function v5.

Not yet accepted end-to-end: Plugin Creator release publisher, signed event delivery, per-host secret provisioning, A.S.F.R.E.E Plugin Creator update/read-back, HSAR adapter/policy profile, host regression receipts and rollback drill.

Plugin Creator package updates do not automatically update other Plugin Creator packages. An authenticated publisher or scheduled exact-ID polling bridge must issue release events. Do not mark a host adopted on event acceptance alone.

## AFSA host adaptation policy

AFSA maps shared capabilities to host SOP, authority, security, privacy, data boundaries, runtime capability and audit sinks. It must not mutate canonical shared semantics or silently rewrite host SOP. Dispositions: DIRECT_COMPATIBLE, ADAPTED_COMPATIBLE, HELD_FOR_AUTHORITY, QUARANTINED_OR_REJECTED.

Automatic adoption is disabled by default. It may be enabled for additive, non-breaking shared DNA only after host policy profile, scoped auth, compatibility, tests, rollback and read-back are verified. Authority/security/privacy/licensing/permission/data-flow/SOP/breaking changes require host review or hold.

## Host snapshot — 2026-11-27

| Host | State | Auto-adopt |
|---|---|---:|
| PRE Standalone | 0.1.6 current; host policy profile pending | No |
| A.S.F.R.E.E / RPEDS | Source merged at `de6b0ce`; Plugin Creator 0.3.2 remains behind source 0.5.0-rc.1; host read-back pending | No |
| HSAR | Plugin Creator adapter package 0.3.1 updated; HSO policy profile and host authentication pending | No |
| HSO | Registry and Edge Function v5 deployed; publisher and host credentials pending | No |

Machine-readable status: catalog/pre-rpeds-federation.json.


## Reconciliation update — 27 November 2026

### Current package and source observations

- PRE Standalone current Plugin Creator package: **0.1.6**, release `pluginrel_6b0961f9dca08191a8af34dbb2e02881`, USER/PRIVATE; 14 skill definitions (one master + 13 subskills).
- HSAR host adapter package: **0.3.1**, release `pluginrel_6b09690c83488191bd950eb9df69d90a`, USER/PRIVATE; includes `hsar-pre-rpeds-federation` and `references/pre-rpeds-hsar-host-profile.md`.
- A.S.F.R.E.E/RPEDS source remains merged at `de6b0cecea5ce9c3aaf05bc57320b8f0dd2d9b3b`, source `0.5.0-rc.1`; its Plugin Creator package is still `0.3.2` and therefore behind source.
- HSO federation Edge Function `pre-core-federation` is deployed and reported ACTIVE at version **4**. Database schema, RLS and service-role policies are deployed.
- The PRE package has no registered canonical Git source repository. The public HSO instruction bundle remains a historical nine-skill v0.1.1 snapshot and is explicitly stale; it is not a complete or redistributable copy of the current private package.

### Supabase registry read-back

The four host records were reconciled. PRE Standalone now records kernel v0.1.6 and the new Plugin Creator release ID. HSAR records adapter v0.3.1, but policy profile remains `PENDING_PROFILE`, host auth remains `NOT_CONFIGURED`, and auto-adoption remains false. A.S.F.R.E.E/RPEDS is still `SOURCE_MERGED_PLATFORM_BEHIND`. HSO is `PUBLISHER_AND_HOST_AUTH_PENDING`.

A direct database read-back found zero rows in `pre_kernel_releases`, `pre_host_adoption_receipts` and `pre_capability_contributions`. Therefore no signed release event, verified release attestation, host adoption receipt or shared capability contribution has yet been processed. The deployed service is real; cross-host automatic adoption is not yet accepted.

### Remaining automation blockers

1. Configure the canonical PRE release publisher or authenticated polling bridge. Plugin Creator package updates do not natively trigger HSO release events.
2. Provision separate least-privilege publisher, verifier and per-host credentials in the secret store. No secret values belong in GitHub, Notion or package content.
3. Verify host-specific AFSA policy profiles for PRE Standalone, A.S.F.R.E.E/RPEDS, HSAR and HSO. Keep `auto_adopt_nonbreaking=false` until each named-host policy and test gate passes.
4. Run release-event, idempotency/replay, digest/signature/contract-attestation, host regression, exact read-back and rollback acceptance.
5. Record each result in a durable per-host adoption receipt. A release being `RELEASED` does not imply any host is `ADOPTED` or `VERIFIED`.

**Readiness remains `PARTIALLY_DEPLOYED`; runtime verification of end-to-end release propagation remains false.**


## Source candidate follow-up — HSO PR #50

The open source candidate adds an idempotent `POST /reconcile` recovery route and a 15-minute scheduled GitHub Actions workflow. The reconciliation logic does not overwrite existing receipts and queues a host for testing only when every capability class in the event is `SHARED_DNA`, the event is explicitly non-breaking, the host policy profile is `VERIFIED`, and host auto-adoption is explicitly enabled. Mixed `SHARED_DNA` + `HOST_ADAPTATION` events remain held. `VERIFIED` adoption also requires policy refs, adapter version, rollback ref, exact read-back and all-PASS tests.

The source PR and CI do not provision GitHub/Supabase secrets, create a Plugin Creator release event feed, or deploy the new reconciliation route. Those remain distinct activation steps. The migration file is a source mirror of already-applied live migration `20261127105413`; it must not be replayed against the production database.


## HSO PR #50 merged and Edge Function v5 deployment read-back — 27 November 2026

- HSO PR #50 is merged at `a13c710d8e40e2b66cc036fe535a317d53abba7c`.
- Supabase `pre-core-federation` is ACTIVE v5. Read-back reports the deployed source hash `195b8ff3cc611a3caea38c786146012ddd3212760b7849e52225a812a102079a`.
- The new `POST /reconcile` endpoint repairs missing per-host receipts idempotently. It never overwrites existing receipts or marks a host ADOPTED/VERIFIED by itself.
- Auto-queue eligibility now requires every event capability class to be `SHARED_DNA`, `is_breaking=false`, a `VERIFIED` host policy profile and explicit host opt-in. Mixed `HOST_ADAPTATION` events remain held.
- A host can be `VERIFIED` only with a verified host policy profile, compatible AFSA disposition, policy references, adapter version, rollback reference, matching release/read-back version and digest, and all-PASS test results.
- The GitHub Actions workflow schedules reconciliation every 15 minutes and accepts a signed publisher dispatch. The workflow and code are merged, but credentials and the Plugin Creator release relay remain unconfigured/not verified.
- Live database read-back still shows zero release events and zero adoption receipts. No host is upgraded by this merge or deployment alone.

**Runtime status:** Edge Function deployed and source read-back verified; event delivery and host adoption remain NOT CONFIGURED / NOT RUN. A direct HTTP health request could not be completed from the current inspection environment, so HTTP endpoint health is not claimed.


## A.S.F.R.E.E/RPEDS source amendment — 27 November 2026

- A.S.F.R.E.E PR #13 merged shared PRE–RPEDS identity and routing at commit `de6b0cecea5ce9c3aaf05bc57320b8f0dd2d9b3b`.
- A.S.F.R.E.E PR #14 merged `rpeds-adaptive-functional-situational-adapter`, eight AFSA acceptance specifications and package-validator registration. Source candidate is now **0.5.0-rc.2**, main commit `f814cff8e800136a6e3a1f664b41085076f19ac8`.
- RPEDS remains a first-class native A.S.F.R.E.E workstream with four modules; it is not deleted or replaced by PRE. PRE Standalone and RPEDS share roadmap DNA and release lineage.
- Parent HSO submodule pin and source registries are being advanced to this commit. Plugin Creator package remains **0.3.2**, release `pluginrel_6b00fc6b23bc8191a5930132969e52c2`; deployment read-back and source/platform parity are still pending.
- PolyForm Noncommercial 1.0.0 terms remain in force. No broader redistribution is implied by the public parent repository.


## Canonical PRE source snapshot registered — 27 November 2026

- Created private source repository: https://github.com/hsaidno-cpu/pre-rpeds-shared-roadmap-dna (main branch).
- Imported PRE Plugin Creator release 0.1.6 (pluginrel_6b0961f9dca08191a8af34dbb2e02881) at commit 98008cdf3e082fd4cc8de03e51b2863fbae8cf11.
- The import contains 37 text files, including the master skill, 13 specialist skill definitions, references, schemas and tests. The Python bytecode cache was excluded. Package artifact SHA-256 and independent signed attestation have not yet been computed.
- Exact Plugin Creator metadata read-back now identifies A.S.F.R.E.E package 0.5.0-rc.2, release pluginrel_6b097130b520819197895298a0a0f73c. Source and package versions match; byte-level package parity and runtime adoption remain unverified.
- The HSO federation workflow is being hardened to fail closed when publisher URL/token are missing. Live pre-core-federation/health returned HTTP 200 with application body federation_not_configured and missing HSO_SYNC_TOKEN.
- PRE registry still has no release event, adoption receipt or capability contribution. Host policy profiles remain pending and automatic adoption remains disabled.

**Status remains PARTIALLY_DEPLOYED.** Repository registration and source snapshot import do not constitute a signed release, host adoption or runtime verification.


## Federation target isolation, runtime acceptance and OIDC scheduler — 28 November 2026

- Every release must carry a non-empty, unique `target_host_ids` array. The initial release receipt creation, independent attestation, adoption update and reconciliation paths all fail closed when this target set is absent or invalid.
- Reconciliation may create or update a receipt only for a host explicitly listed in that release's `target_host_ids`. A host subscription or matching release channel is not sufficient authorization to receive a release.
- A host can submit an adoption receipt only for an event that names that host in its target set.
- `VERIFIED` is reserved for live host runtime acceptance. In addition to release attestation, policy, adapter, rollback and successful test requirements, the envelope must include HTTPS `deployment_ref`, HTTPS `runtime_invocation_ref`, and at least one passing `LIVE_HOST_RUNTIME` test with an HTTPS evidence reference. CI-only test receipts cannot satisfy this gate.
- The scheduled HSO reconciliation job requests a short-lived GitHub Actions OIDC JWT for the exact Supabase Edge Function audience. The job is constrained to the canonical repository ID, main ref, exact workflow_ref, and schedule/workflow_dispatch events. It does not require or expose `HSO_SYNC_TOKEN`.
- The existing HMAC publisher relay remains separate and requires its existing secret. OIDC reconciliation is not permission to publish releases or impersonate host identities.
- `HSO_SYNC_TOKEN` remains resolved server-side for the compatibility publisher path, but its absence no longer blocks OIDC-only routes such as scheduled reconciliation.
- These changes are source/PR changes only. They do not deploy Edge Functions, run a production reconciliation, provision host credentials, or promote any host state.
