# Contributing to Hypersystem Orchestrator

## Scope

Contribute ecosystem-level metadata, architecture, contracts, governance, documentation, tests and verified source references here. Change plugin-specific logic in the plugin's own repository.

## Before opening a pull request

1. Identify the affected plugin keys and repository IDs.
2. Confirm the owning source repository and its current main commit.
3. Check whether the change affects downstream consumers, contracts, versions, permissions or license boundaries.
4. Update the catalog and evidence references together.
5. Run the local validation commands in README.md.
6. Include risks, assumptions, limitations, rollback and acceptance criteria.

## Submodule updates

A submodule pointer update is a source dependency change. In the PR, show:
- previous and new source commit;
- child repository changelog or relevant diff;
- reason for the update;
- compatibility/test evidence;
- visibility/access impact, especially for private repositories.

Do not update a submodule simply to follow the newest branch tip. Pin the source commit that was actually reviewed.

## Pull request checklist

- [ ] Scope is limited to the parent ecosystem repository.
- [ ] Plugin identities and Creator IDs remain stable.
- [ ] No plugin source has been copied without license/provenance review.
- [ ] Catalog and repository references are accurate.
- [ ] Dependencies and responsibility owners are not duplicated.
- [ ] Static validator and unit tests pass.
- [ ] Runtime/host claims are backed by actual evidence or labeled NOT_RUN.
- [ ] Documentation and roadmap reflect the real change.
- [ ] Private repository and secret boundaries are preserved.
