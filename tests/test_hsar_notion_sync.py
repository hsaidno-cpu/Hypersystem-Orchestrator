import unittest
from unittest.mock import patch
import urllib.error

from scripts.hsar_notion_sync import (
    JsonHttpClient, HsarSyncService, SyncError, redact,
    read_rich_text, read_select, stable_json_hash, event_pr_numbers,
    is_same_repository_pull_request, assert_write_enabled,
)


class FakeGitHub:
    def list_pr_files(self, repo, number):
        return ([{"filename": "docs/hsar/example.md", "sha": "b" * 40, "status": "modified", "changes": 4}], False)

    def list_pulls_for_commit(self, repo, commit_sha):
        return {"a" * 40: [4], "b" * 40: [7, 4]}.get(commit_sha, [])

    def list_workflow_runs(self, repo, head_sha):
        return [{"name": "Docs validation", "run_number": 12, "status": "completed", "conclusion": "success", "url": "https://github.com/example/run/12", "head_sha": head_sha, "created_at": "2026-11-26T00:00:00Z", "updated_at": "2026-11-26T00:10:00Z"}]


class FakeNotion:
    def __init__(self, duplicates=0):
        self.pages = {}
        self.writes = 0
        self.duplicates = duplicates

    def query_pr_url(self, pr_url):
        matches = [p for p in self.pages.values() if p["properties"].get("PR URL", {}).get("url") == pr_url]
        return matches + ([{"id": "duplicate"}] * self.duplicates)

    def create_page(self, properties):
        self.writes += 1
        page_id = f"page-{len(self.pages)+1}"
        self.pages[page_id] = {"id": page_id, "properties": properties.copy()}
        return {"id": page_id}

    def get_page(self, page_id):
        if page_id not in self.pages:
            raise SyncError("missing fake page")
        return self.pages[page_id]

    def update_page(self, page_id, properties):
        self.writes += 1
        self.pages[page_id]["properties"].update(properties)
        return self.pages[page_id]


def make_pr(title="Doc contract"):
    return {
        "number": 9,
        "html_url": "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/9",
        "title": title, "state": "open", "merged": False, "merged_at": None,
        "updated_at": "2026-11-26T00:00:00Z", "changed_files": 1,
        "base": {"ref": "main", "sha": "a" * 40, "repo": {"full_name": "hsaidno-cpu/Hypersystem-Orchestrator"}},
        "head": {"ref": "hsar/test", "sha": "c" * 40, "repo": {"full_name": "hsaidno-cpu/Hypersystem-Orchestrator"}},
    }


class SyncContractTests(unittest.TestCase):
    def setUp(self):
        self.github = FakeGitHub()
        self.notion = FakeNotion()
        self.service = HsarSyncService(self.github, self.notion, "hsaidno-cpu/Hypersystem-Orchestrator")

    def test_github_commit_to_pr_endpoint_is_scoped_to_one_exact_sha(self):
        client = GitHubClient("test-token")
        with patch.object(client, "request", return_value=[{"number": 31}, {"number": 31}]) as mocked:
            self.assertEqual(client.list_pulls_for_commit("hsaidno-cpu/Hypersystem-Orchestrator", "a" * 40), [31])
        mocked.assert_called_once_with("GET", f"/repos/hsaidno-cpu/Hypersystem-Orchestrator/commits/{'a' * 40}/pulls?per_page=100")

    def test_push_event_commit_shas_are_validated_and_deduplicated(self):
        event = {
            "after": "b" * 40,
            "head_commit": {"id": "b" * 40},
            "commits": [{"id": "a" * 40}, {"id": "b" * 40}, {"id": "invalid"}],
        }
        self.assertEqual(event_commit_shas(event), ["b" * 40, "a" * 40])

    def test_push_processes_only_prs_linked_to_pushed_commits(self):
        event = {"after": "a" * 40, "commits": [{"id": "b" * 40}]}
        self.assertEqual(push_pr_numbers(self.github, "hsaidno-cpu/Hypersystem-Orchestrator", event), [4, 7])

    def test_write_gate_defaults_closed(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SyncError):
                assert_write_enabled(False)
            assert_write_enabled(True)
        with patch.dict("os.environ", {"HSAR_NOTION_SYNC_ENABLED": "true"}):
            assert_write_enabled(False)

    def test_hash_is_order_independent(self):
        self.assertEqual(stable_json_hash({"a": 1, "b": 2}), stable_json_hash({"b": 2, "a": 1}))

    def test_redacts_common_secret_shapes(self):
        value = "token=ghp_" + "x" * 30 + " Authorization: Bearer abcdefghijklmnop"
        cleaned = redact(value)
        self.assertNotIn("ghp_", cleaned)
        self.assertNotIn("Bearer abcdefghijklmnop", cleaned)

    def test_create_verifies_and_marks_synced(self):
        result = self.service.upsert_pr(make_pr())
        self.assertEqual(result.status, "CREATED")
        props = self.notion.get_page(result.page_id)["properties"]
        self.assertEqual(read_rich_text(props, "Content Hash"), result.content_hash)
        self.assertEqual(read_select(props, "GitHub Sync Status"), "Synced")
        self.assertEqual(read_select(props, "Notion Sync Status"), "Synced")
        self.assertNotIn("Decision State", props)

    def test_duplicate_delivery_is_noop(self):
        first = self.service.upsert_pr(make_pr())
        writes_after_first = self.notion.writes
        second = self.service.upsert_pr(make_pr())
        self.assertEqual(first.content_hash, second.content_hash)
        self.assertEqual(second.status, "NOOP")
        self.assertEqual(self.notion.writes, writes_after_first)

    def test_changed_source_updates_existing_page(self):
        first = self.service.upsert_pr(make_pr())
        second = self.service.upsert_pr(make_pr("Changed title"))
        self.assertEqual(second.status, "UPDATED")
        self.assertEqual(first.page_id, second.page_id)
        props = self.notion.get_page(second.page_id)["properties"]
        self.assertIn("PR #9", read_rich_text(props, "Automation Sync Receipt"))
        self.assertNotIn("Change Summary", props)

    def test_non_idempotent_create_transport_error_is_not_retried(self):
        client = JsonHttpClient("test-token", "https://example.invalid")
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("network timeout")) as mocked:
            with self.assertRaises(SyncError):
                client.request("POST", "/pages", {"title": "one"}, retry_safe=False)
        self.assertEqual(mocked.call_count, 1)

    def test_fork_originated_pr_is_outside_pilot_scope(self):
        pr = make_pr()
        self.assertTrue(is_same_repository_pull_request(pr, "hsaidno-cpu/Hypersystem-Orchestrator"))
        pr["head"]["repo"]["full_name"] = "contributor/fork"
        self.assertFalse(is_same_repository_pull_request(pr, "hsaidno-cpu/Hypersystem-Orchestrator"))

    def test_workflow_event_pr_numbers_are_deduplicated(self):
        event = {"workflow_run": {"pull_requests": [{"number": 4}, {"number": 4}, {"number": 7}]}}
        self.assertEqual(event_pr_numbers("workflow_run", event), [4, 7])

    def test_duplicate_stable_key_fails_closed(self):
        self.notion.duplicates = 2
        with self.assertRaises(SyncError):
            self.service.upsert_pr(make_pr())
        self.assertEqual(self.notion.writes, 0)

    def test_human_managed_fields_are_never_overwritten(self):
        result = self.service.upsert_pr(make_pr())
        page = self.notion.get_page(result.page_id)
        page["properties"]["Decision State"] = {"select": {"name": "Approved"}}
        page["properties"]["Acceptance Evidence"] = {"rich_text": [{"plain_text": "GOV-01 accepted"}]}
        page["properties"]["Change"] = {"title": [{"plain_text": "Human curated title"}]}
        self.service.upsert_pr(make_pr("A newer title"))
        props = page["properties"]
        self.assertEqual(read_select(props, "Decision State"), "Approved")
        self.assertEqual(read_rich_text(props, "Acceptance Evidence"), "GOV-01 accepted")
        self.assertEqual(read_rich_text(props, "Change"), "Human curated title")


if __name__ == "__main__":
    unittest.main()
