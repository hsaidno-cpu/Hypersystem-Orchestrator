# Versioning and Release Governance

## 1. Independent version planes

Keep these version identifiers distinct:

- Parent ecosystem release: version of catalog, shared architecture, contracts and governance in this repository.
- Plugin package version: version declared by the owning plugin's canonical manifest/release.
- Plugin Creator release identifier: deployment record in the platform; not the source version.
- Runtime/adapter version: version of the implementation or hosted service, where one exists.
- Submodule pin: exact commit SHA selected by the parent; not a release version.

Do not infer a child plugin version from its display name, Plugin Creator ID, legacy alias or parent tag.

## 2. Semantic versioning policy

Use SemVer for parent releases once the first formal release is tagged:

- MAJOR: incompatible catalog schema, integration contract or governance behavior.
- MINOR: backward-compatible plugin registrations, optional fields, new contracts or compatible capabilities.
- PATCH: documentation, validation or backward-compatible metadata corrections.

Plugin repositories retain their own version authority and release cadence. The parent does not force every plugin to share one version.

## 3. Version evidence

For every plugin version in the catalog, record:
- exact source path (manifest, package file or release page);
- source repository and immutable commit;
- observed version string;
- evidence date;
- candidate/stable/deprecated state;
- any conflict between plugin label, skill header and source manifest.

If no authoritative evidence is available, use null and state UNKNOWN or NOT_VERIFIED. User-supplied names can be retained as labels but must not be presented as independently verified source versions.

## 4. Compatibility matrix

Compatibility is declared between a producer and consumer contract, not inferred from similar names.

Each future compatibility record should include:
- producer plugin key and version;
- consumer plugin key and version;
- contract/schema version;
- supported input/output format;
- required capabilities and permission scopes;
- test suite and exact tested commits;
- status: PROPOSED, DECLARED, STATIC_VALIDATED, CONTRACT_TESTED, HOST_TESTED, RUNTIME_VERIFIED, BLOCKED or DEPRECATED;
- evidence locator and known limitations.

## 5. Release gates

A parent release candidate should pass:
1. catalog and schema validation;
2. source URL and submodule commit verification;
3. documentation and changelog review;
4. dependency and compatibility review;
5. security, license and private-source exposure review;
6. applicable contract tests;
7. human review and explicit release authorization.

A plugin source release must separately pass its own repository release gates. A parent tag does not publish child plugins.

## 6. Deprecation and migration

- Assign a canonical target and sunset policy to every redirect/legacy record.
- Never create a second active orchestrator for a deprecated plugin.
- Keep migration instructions explicit about data, case history, source files, schema and version changes.
- Do not silently migrate secrets, private context or user records.
- Retain enough historical evidence to trace the old plugin identity to its canonical replacement.
