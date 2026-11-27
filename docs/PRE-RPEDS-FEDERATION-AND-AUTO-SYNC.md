# PRE–RPEDS Shared DNA and Automatic Release Synchronization

## Identity and merger

PRE Standalone and RPEDS are two first-class manifestations of one jointly evolved roadmap competency. PRE remains independently usable. RPEDS remains the native A.S.F.R.E.E roadmap workstream with its identity, four original modules, host procedures and M00/O01–O12 integration. The merger is at the shared DNA kernel, not an alias or replacement.

The shared kernel owns R0–R9 lifecycle semantics, roadmap object model, dependency, evidence, progress, gate and adaptation contracts, process audit, assurance/closure, capability learning, next-action/prompt contracts and release lineage. Host-specific extensions remain separate. Two-way contributions become shared DNA only after sanitization, provenance, validation and approval.

## Automatic release flow

PRE release published → authenticated event → provenance and digest verification → contract/SemVer compatibility → host AFSA policy decision → host regression → gated or eligible auto-adoption → target read-back → per-host adoption receipt.

The HSO Supabase registry contains pre_kernel_releases, pre_host_subscriptions, pre_host_adoption_receipts and pre_capability_contributions. RLS is enabled, anon/authenticated access is revoked and service_role has explicit policies.

## Edge Function

Supabase Edge Function pre-core-federation is deployed at version 4 in project ehgmtkkppmceaffhwcpc.

- GET /health reports service availability/configuration only.
- POST /release accepts a release envelope after HMAC verification using HSO_SYNC_TOKEN; event and idempotency keys are unique. Per-host receipts are created. Unverified host profiles are held.
- GET /latest?host_id=... requires the host-specific token named by host_auth_secret_ref.
- POST /adoption requires a host-specific HMAC signature. VERIFIED is rejected unless all tests are PASS and read-back version/digest match the release event.

Host auth references store environment variable names, not credential values. The values must be provisioned for each host. Missing host credentials fail closed with host_auth_not_configured.

## Deployed versus not yet live

Deployed: four registry tables, RLS/service-role permissions, explicit service-role policies, four initial host records, host auth references and Edge Function v4.

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
| HSO | Registry and Edge Function v2 deployed; event publisher and credentials pending | No |

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
