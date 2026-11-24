import unittest
from datetime import date
import json
import urllib.error
from tools.github_notion_sync import SyncError, build_event_record, digest_record, upsert_record, stale_sweep

CONFIG = {
    "repository": "hsaidno-cpu/Hypersystem-Orchestrator",
    "main_branch": "main",
    "pull_request_relation_map": {"15": "42299868-397f-81fe-8349-c8e97800573a"},
    "branch_relation_map": {"main": "42299868-397f-81fe-8349-c8e97800573a"},
    "default_relation_ids": [],
    "workflow_names": ["Catalog and distribution validation"],
}


class FakeNotion:
    def __init__(self):
        self.rows, self.created, self.updated = [], 0, 0

    def query_by_locator(self, locator):
        return [row for row in self.rows if row["properties"]["Source Locator"]["url"] == locator]

    def create_page(self, properties, source_locator):
        self.created += 1
        row = {"id": f"page-{self.created}", "properties": properties}
        self.rows.append(row)
        return {"id": row["id"]}

    def update_page(self, page_id, properties):
        self.updated += 1
        row = next(row for row in self.rows if row["id"] == page_id)
        row["properties"].update(properties)
        return {"id": page_id}

    def query_all(self):
        return self.rows


def sample_pr():
    return {
        "action": "synchronize",
        "number": 15,
        "pull_request": {
            "number": 15, "title": "Correct test state",
            "html_url": "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/15",
            "state": "open", "merged": False,
            "head": {
                "ref": "fix/ponytail-c2-c3-test-contract-20261124",
                "sha": "7d07d5efbfefd85865ce7d03ec8529582fea9cfc",
                "repo": {"full_name": "hsaidno-cpu/Hypersystem-Orchestrator"},
            },
        },
    }


class GitHubNotionSyncTests(unittest.TestCase):
    def test_pr_event_is_metadata_only(self):
        record = build_event_record("pull_request", sample_pr(), CONFIG, today=date(2026, 11, 24))
        self.assertEqual(record["evidence_type"], "Pull Request")
        self.assertEqual(record["evidence_state"], "UNKNOWN")
        self.assertEqual(record["related_work_item_ids"], ["42299868-397f-81fe-8349-c8e97800573a"])
        self.assertIn("source metadata only", record["claim"])
        self.assertIn("does not prove CI success", record["limitation"])

    def test_fork_pr_is_ignored(self):
        event = sample_pr()
        event["pull_request"]["head"]["repo"]["full_name"] = "external/fork"
        self.assertIsNone(build_event_record("pull_request", event, CONFIG))
        self.assertIsNone(build_event_record("pull_request_target", event, CONFIG))

    def test_pull_request_target_event_is_normalized(self):
        record = build_event_record("pull_request_target", sample_pr(), CONFIG)
        self.assertEqual(record["evidence_type"], "Pull Request")
        self.assertEqual(record["evidence_state"], "UNKNOWN")

    def test_p1_sync_pr_maps_to_its_own_work_item(self):
        event = sample_pr()
        event["number"] = 16
        event["pull_request"]["number"] = 16
        event["pull_request"]["head"]["ref"] = "feat/github-notion-evidence-sync-20261124"
        event["pull_request"]["html_url"] = "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/16"
        config = dict(CONFIG)
        config["pull_request_relation_map"] = dict(CONFIG["pull_request_relation_map"])
        config["pull_request_relation_map"]["16"] = "42299868-397f-8167-afb4-c4fbb98b6e06"
        record = build_event_record("pull_request_target", event, config)
        self.assertEqual(record["related_work_item_ids"], ["42299868-397f-8167-afb4-c4fbb98b6e06"])


    def test_workflow_failure_maps_to_fail_without_gate_claim(self):
        event = {"workflow_run": {
            "id": 987, "run_number": 74, "name": "Catalog and distribution validation",
            "conclusion": "failure",
            "head_repository": {"full_name": CONFIG["repository"]},
            "head_branch": "fix/ponytail-c2-c3-test-contract-20261124",
            "head_sha": "7d07d5efbfefd85865ce7d03ec8529582fea9cfc",
            "html_url": "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/actions/runs/987",
            "pull_requests": [{"number": 15}],
        }}
        record = build_event_record("workflow_run", event, CONFIG)
        self.assertEqual(record["evidence_state"], "FAIL")
        self.assertEqual(record["evidence_type"], "CI Run")
        self.assertIn("not human approval", record["limitation"])

    def test_unapproved_workflow_name_is_ignored(self):
        event = {"workflow_run": {
            "name": "Untrusted workflow",
            "head_repository": {"full_name": CONFIG["repository"]},
        }}
        self.assertIsNone(build_event_record("workflow_run", event, CONFIG))

    def test_main_push_is_commit_evidence_only(self):
        event = {"ref": "refs/heads/main", "head_commit": {"id": "a" * 40, "message": "merge"}}
        record = build_event_record("push", event, CONFIG)
        self.assertEqual(record["evidence_type"], "Commit")
        self.assertEqual(record["evidence_state"], "UNKNOWN")
        self.assertIn("not a successful test", record["limitation"])

    def test_source_digest_ignores_observation_timestamps_on_replay(self):
        first = build_event_record("pull_request", sample_pr(), CONFIG, today=date(2026, 11, 24))
        replay = build_event_record("pull_request", sample_pr(), CONFIG, today=date(2026, 11, 25))
        self.assertNotEqual(first["observed_at"], replay["observed_at"])
        self.assertNotEqual(first["verified_at"], replay["verified_at"])
        self.assertEqual(digest_record(first), digest_record(replay))

    def test_upsert_create_then_noop(self):
        client = FakeNotion()
        record = build_event_record("pull_request", sample_pr(), CONFIG, today=date(2026, 11, 24))
        first = upsert_record(client, record, apply=True)
        second = upsert_record(client, record, apply=True)
        self.assertEqual(first["operation"], "CREATED")
        self.assertEqual(second["operation"], "NO_OP")
        self.assertEqual(client.created, 1)
        self.assertEqual(client.updated, 0)

    def test_changed_event_updates_same_page(self):
        client = FakeNotion()
        record = build_event_record("pull_request", sample_pr(), CONFIG)
        upsert_record(client, record, apply=True)
        changed = dict(record)
        changed["claim"] = changed["claim"] + " changed"
        result = upsert_record(client, changed, apply=True)
        self.assertEqual(result["operation"], "UPDATED")
        self.assertEqual(client.created, 1)
        self.assertEqual(client.updated, 1)

    def test_page_create_does_not_blindly_retry_ambiguous_post(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({"results": [], "has_more": False}).encode("utf-8")

        class FailingCreateOpener:
            def __init__(self):
                self.calls = []
            def __call__(self, request, timeout=20):
                self.calls.append(request.full_url)
                if request.full_url.endswith("/pages"):
                    raise urllib.error.URLError("connection reset after request")
                return FakeResponse()

        opener = FailingCreateOpener()
        from tools.github_notion_sync import NotionClient
        client = NotionClient("not-a-real-token", "42299868-397f-817c-bb25-000b49b243fa",
                              opener=opener, sleeper=lambda delay: None)
        locator = "https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/pull/15"
        with self.assertRaisesRegex(SyncError, "outcome is ambiguous"):
            client.create_page({"Source Locator": {"url": locator}}, locator)
        self.assertEqual(sum(url.endswith("/pages") for url in opener.calls), 1)
        self.assertEqual(sum("/data_sources/" in url for url in opener.calls), 1)

    def test_duplicate_locator_fails_closed(self):
        client = FakeNotion()
        record = build_event_record("pull_request", sample_pr(), CONFIG)
        locator = record["source_locator"]
        client.rows = [
            {"id": "one", "properties": {"Source Locator": {"url": locator}}},
            {"id": "two", "properties": {"Source Locator": {"url": locator}}},
        ]
        with self.assertRaisesRegex(SyncError, "Duplicate Source Locator"):
            upsert_record(client, record, apply=True)
        self.assertEqual(client.updated, 0)

    def test_stale_sweep_marks_old_fresh_only_and_never_deletes(self):
        client = FakeNotion()
        client.rows = [
            {"id": "old", "properties": {
                "Evidence Freshness": {"select": {"name": "FRESH"}},
                "Verified At": {"date": {"start": "2026-10-01"}},
            }},
            {"id": "recent", "properties": {
                "Evidence Freshness": {"select": {"name": "FRESH"}},
                "Verified At": {"date": {"start": "2026-11-20"}},
            }},
            {"id": "already-stale", "properties": {
                "Evidence Freshness": {"select": {"name": "STALE"}},
                "Verified At": {"date": {"start": "2026-10-01"}},
            }},
        ]
        result = stale_sweep(client, today=date(2026, 11, 24), stale_after_days=14, apply=True)
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["updated_count"], 1)
        self.assertEqual(client.updated, 1)
        self.assertEqual(len(client.rows), 3)


if __name__ == "__main__":
    unittest.main()
