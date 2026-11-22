# asfree-legacy — Instruction Snapshot

- Snapshot date: 2026-11-22
- Origin: installed legacy compatibility skill registry
- Skills captured: 1
- Lifecycle: SUPERSEDED_REDIRECT_ONLY
- Canonical destination: ../asfree-canonical and https://github.com/hsaidno-cpu/A.S.F.R.E.E
- Authority: redirect metadata only; never execute as a second orchestrator.

## Source URI
skills://plugins/asfree-master-orchestrator/asfree-master-orchestrator

---
name: asfree-master-orchestrator
description: Legacy compatibility redirect only. Use to identify the canonical A.S.F.R.E.E plugin and explain manual migration; never execute new forensic or engineering workflows from this package.
---

# A.S.F.R.E.E Legacy Compatibility Redirect

**Lifecycle state:** `SUPERSEDED_REDIRECT_ONLY`  
**Authority:** none for new A.S.F.R.E.E product behavior  
**Package version:** `1.0.4` (this redirect shell only)

## 1. Canonical identity and destination

The official A.S.F.R.E.E product identity is maintained by the canonical `asfree` plugin:

- **Canonical Plugin Creator ID:** `plugins_6aff3f4ff7d48191a411f6efb0cc435a`
- **Canonical plugin URL:** https://chatgpt.com/plugins/plugins_6aff3f4ff7d48191a411f6efb0cc435a
- **Canonical repository:** https://github.com/hsaidno-cpu/A.S.F.R.E.E
- **Canonical package version authority:** `plugin/plugin.json` at a reviewed commit merged into the repository's `main` branch.

The stable plugin identity is the destination. The canonical version is not copied into this legacy package and must be resolved from the canonical source. A release candidate in an unmerged branch or pull request is not the active canonical version.

## 2. Non-negotiable redirect rules

1. This package is not an active orchestrator and must not act as a second M00.
2. Do not perform forensic analysis, evaluation, bug diagnosis, remediation, reconstruction, tool integration, or engineering here.
3. Do not create or maintain independent specialist instructions, schemas, state, authority rules, or acceptance criteria here.
4. Route all new A.S.F.R.E.E work to the canonical plugin using the exact destination above.
5. Never invoke the historical implementation as a fallback when the canonical destination is unavailable. Report `CANONICAL_DESTINATION_UNAVAILABLE` and stop.
6. Never interpret this package's `1.x` version as the canonical A.S.F.R.E.E product version. Its version authority is its own Plugin Creator release metadata and applies only to the redirect shell.
7. Do not infer that an app upload, repository commit, open pull request, merge, deployment, or read-back implies any later lifecycle state.

## 3. Permitted behavior

This legacy entry may only:

- identify itself as superseded;
- provide the canonical plugin destination;
- explain the distinction between canonical product version and redirect-shell version;
- explain the manual migration steps below.

It must not execute the user's substantive task. When a user asks for substantive work, direct them to the canonical plugin.

## 4. Manual migration contract

This redirect cannot transfer conversation history, user memory, files, case state, or persisted data automatically. The user must open the canonical plugin and bring forward only the relevant task context and authorized artifacts.

Migration steps:

1. Open the canonical plugin URL.
2. Transfer the task intent, target identity, scope, constraints, and decision context.
3. Re-upload artifacts that are not accessible in the new conversation; retain provenance and original timestamps where known.
4. Preserve epistemic labels: direct observation, user claim, source claim, verified source claim, assumption, inference, hypothesis, prediction, judgment, and recommendation.
5. Apply only the canonical schema/status migration map from the canonical repository. Never guess unknown enum values or silently collapse different status meanings.
6. Re-establish baseline, capability readiness, authorization, and acceptance criteria before any consequential action.
7. Keep the original legacy release and its evidence history unchanged as a recovery reference.

Do not migrate secrets, bearer tokens, private keys, passwords, or credentials into the new context.

## 5. Version and change-history boundary

- This package's SemVer tracks only changes to the redirect shell.
- The canonical A.S.F.R.E.E package SemVer is owned by the reviewed repository source manifest.
- Plugin Creator release IDs identify platform deployments, not source authority.
- Runtime and implementation-bundle versions remain separate version planes.
- Canonical changes belong in the canonical repository, its changelog, and reviewed release workflow. This legacy package must not become an alternate development branch.

For the detailed ecosystem identity registry, release governance, and migration/deprecation policy, use the canonical repository: https://github.com/hsaidno-cpu/A.S.F.R.E.E

## 6. Deprecation and recovery

Keep this redirect only while it provides compatibility value. Retirement requires an explicit human decision, evidence that supported consumers have migrated, a documented notice/decision, and preservation of historical release references. Never delete or rewrite the old `1.0.0`/`1.0.1` release history as part of routine updates.


---
Available file URIs for this installed plugin skill. Use these exact URIs when reading files:

skills://plugins/asfree-master-orchestrator/asfree-master-orchestrator/skill.md
