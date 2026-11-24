# HSO GitHub-to-Notion Evidence Synchronization

**Status:** IMPLEMENTED_IN_BRANCH / NOT_LIVE / CREDENTIALS_NOT_CONFIGURED  
**Scope:** GitHub pull requests, commits pushed to \`main\`, completed Catalog and distribution validation runs, and a weekly stale-evidence sweep.  
**Write boundary:** HSO Evidence Registry only. No roadmap status, gate, progress, decision, approval, or record deletion is performed.

## Architecture and idempotency

GitHub event -> normalize -> exact \`Source Locator\` query -> create/update/no-op -> Notion Evidence Registry.

Stable upsert keys:
- PR: canonical PR URL (one current evidence record per PR).
- CI: canonical workflow-run URL (one record per run).
- Main commit: canonical commit URL (one record per commit).

A SHA-256 digest detects unchanged events. More than one matching source locator fails closed. Notion 429/5xx and transport errors receive bounded retries; permission and schema errors do not. Pagination is followed. A weekly sweep only changes old \`FRESH\` records to \`STALE\`; it never deletes records or alters evidence outcome.

## Enablement prerequisites

1. Create a Notion internal integration.
2. Share the HSO Evidence Registry data source with that integration.
3. Add GitHub Actions secret \`HSO_NOTION_API_KEY\`; never put the token in code, workflow inputs, issues, or Notion content.
4. Add Actions variable \`HSO_NOTION_SYNC_ENABLED=true\`. Without this variable the sync job is skipped.
5. Ensure this workflow exists on the default branch before expecting event-driven runs.
6. Run a controlled test event and read back the resulting Notion page before enabling the workflow variable for normal operations.

## Acceptance tests

- Create event creates one evidence record.
- Replayed event is a no-op.
- Changed source event updates the same page.
- Duplicate source locators stop with an explicit error.
- Unsupported/fork events are ignored.
- Notion API transient failures retry within a bounded limit.
- Old evidence becomes STALE without deletion.
- Evidence writes never set roadmap progress, acceptance, PRE gate, or approval.

## Known limitations

- Live sync is not active until the Notion integration has been shared and the GitHub secret/variable are set.
- This first vertical slice updates only the Evidence Registry. It does not upsert Work Item properties or decision records.
- Human review, environment approval, merge authority, and live Remote MCP acceptance remain independent controls.
- Notion stores the latest normalized evidence per stable locator; this is not a full immutable event ledger.
