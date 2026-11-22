# Source Repository Onboarding

## Purpose

Register each plugin's true canonical source repository without copying, silently moving or relabeling code. Use a submodule only after repository identity and content are verified.

## Required intake

For each proposed source:
- plugin key and Plugin Creator identity;
- full GitHub repository URL and owner;
- public/private visibility and access status;
- default branch and current head SHA;
- README, manifest, source tree, tests, references and license;
- package version and release evidence;
- relationship to existing repositories (canonical, mirror, monorepo package, prototype, redirect or unrelated);
- permission to add the repository as a submodule;
- any sensitive content or assets that must not be exposed.

## Verification states

- DISCOVERED: a URL/name has been found.
- IDENTIFIED: repository ownership and identity are confirmed.
- SOURCE_VERIFIED: relevant source artifacts and license inspected.
- SUBMODULE_READY: repository can be pinned and its visibility consequences are known.
- SUBMODULE_PINNED: parent commit includes a gitlink to a recorded source SHA.
- HOST_TESTED: actual target-host activation or routing was tested.
- RUNTIME_VERIFIED: actual runtime execution was observed and evidenced.

Do not skip states. Candidate and pending are not source-verified.

## Add a verified public or private source

1. Read repository metadata and confirm write/read permission.
2. Inspect root guidance, README, manifest, license, relevant source files, tests and changelog.
3. Verify package identity against the plugin registry entry.
4. Confirm whether the repository is public or private and note public-clone implications.
5. Fetch the exact branch-head commit SHA.
6. Add a catalog repository record and set the plugin source_repository_id.
7. Add the submodule using the canonical URL and pin the inspected commit.
8. Validate the central catalog and review the complete diff.
9. Open a parent-repository pull request and verify it after creation.
10. Update Notion with the actual source, commit, status and limitations.

Typical local command sequence:

~~~bash
git submodule add https://github.com/OWNER/REPOSITORY.git plugins/PLUGIN_KEY
git -C plugins/PLUGIN_KEY checkout IMMUTABLE_COMMIT_SHA
git add .gitmodules plugins/PLUGIN_KEY catalog
git commit -m "chore(ecosystem): register PLUGIN_KEY source"
~~~

For a private submodule, every collaborator who initializes it must have read access to the private repository. Never expose the source by changing its visibility without explicit approval.

## When not to add a submodule

- repository identity is uncertain;
- repository is only a placeholder or has no source artifacts;
- it is a legacy redirect, not a canonical implementation;
- license/provenance is unknown;
- source includes secrets or sensitive information;
- source is an unrelated product despite a similar name.

In those cases, retain a candidate/pending registry record and document the missing evidence.
