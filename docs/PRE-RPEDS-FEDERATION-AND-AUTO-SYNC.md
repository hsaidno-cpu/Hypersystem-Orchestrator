# PRE–RPEDS Shared DNA and Automatic Release Synchronization

## Identity and merger

PRE Standalone and RPEDS are two first-class manifestations of one jointly evolved roadmap competency. PRE remains independently usable. RPEDS remains the native A.S.F.R.E.E roadmap workstream with its identity, four original modules, host procedures and M00/O01–O12 integration. The merger is at the shared DNA kernel, not an alias or replacement.

The shared kernel owns R0–R9 lifecycle semantics, roadmap object model, dependency, evidence, progress, gate and adaptation contracts, process audit, assurance/closure, capability learning, next-action/prompt contracts and release lineage. Host-specific extensions remain separate. Two-way contributions become shared DNA only after sanitization, provenance, validation and approval.

## Automatic release flow

PRE release published → authenticated event → provenance and digest verification → contract/SemVer compatibility → host AFSA policy decision → host regression → gated or eligible auto-adoption → target read-back → per-host adoption receipt.

The HSO Supabase registry contains pre_kernel_releases, pre_host_subscriptions, pre_host_adoption_receipts and pre_capability_contributions. RLS is enabled, anon/authenticated access is revoked and service_role has explicit policies.

## Edge Function

Supabase Edge Function pre-core-federation is deployed at version 2 in project ehgmtkkppmceaffhwcpc.

- GET /health reports service availability/configuration only.
- POST /release accepts a release envelope after HMAC verification using HSO_SYNC_TOKEN; event and idempotency keys are unique. Per-host receipts are created. Unverified host profiles are held.
- GET /latest?host_id=... requires the host-specific token named by host_auth_secret_ref.
- POST /adoption requires a host-specific HMAC signature. VERIFIED is rejected unless all tests are PASS and read-back version/digest match the release event.

Host auth references store environment variable names, not credential values. The values must be provisioned for each host. Missing host credentials fail closed with host_auth_not_configured.

## Deployed versus not yet live

Deployed: four registry tables, RLS/service-role permissions, explicit service-role policies, four initial host records, host auth references and Edge Function v2.

Not yet accepted end-to-end: Plugin Creator release publisher, signed event delivery, per-host secret provisioning, A.S.F.R.E.E PR merge/install/read-back, HSAR adapter/policy profile, host regression receipts and rollback drill.

Plugin Creator package updates do not automatically update other Plugin Creator packages. An authenticated publisher or scheduled exact-ID polling bridge must issue release events. Do not mark a host adopted on event acceptance alone.

## AFSA host adaptation policy

AFSA maps shared capabilities to host SOP, authority, security, privacy, data boundaries, runtime capability and audit sinks. It must not mutate canonical shared semantics or silently rewrite host SOP. Dispositions: DIRECT_COMPATIBLE, ADAPTED_COMPATIBLE, HELD_FOR_AUTHORITY, QUARANTINED_OR_REJECTED.

Automatic adoption is disabled by default. It may be enabled for additive, non-breaking shared DNA only after host policy profile, scoped auth, compatibility, tests, rollback and read-back are verified. Authority/security/privacy/licensing/permission/data-flow/SOP/breaking changes require host review or hold.

## Host snapshot — 2026-11-27

| Host | State | Auto-adopt |
|---|---|---:|
| PRE Standalone | 0.1.5 current; host policy profile pending | No |
| A.S.F.R.E.E / RPEDS | PR #13 candidate; not yet merged | No |
| HSAR | Conditional routing only; no dedicated adapter/profile | No |
| HSO | Registry and Edge Function v2 deployed; event publisher and credentials pending | No |

Machine-readable status: catalog/pre-rpeds-federation.json.
