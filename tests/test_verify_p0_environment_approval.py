"""Tests for identity-bound GitHub Actions Environment approval extraction."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import verify_p0_environment_approval as verifier


ACTOR = "hsaidno-cpu"
REVIEWER = "independent-security-reviewer"
RUN_ID = "123456789"
REVIEWER_ID = 424242


class VerifyEnvironmentApprovalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.output = Path(self.tmp.name) / "approval.json"
        self.environment = {
            "protection_rules": [{
                "type": "required_reviewers",
                "prevent_self_review": True,
                "reviewers": [{
                    "type": "User",
                    "reviewer": {"login": REVIEWER, "id": REVIEWER_ID},
                }],
            }],
        }
        self.history = [{
            "state": "approved",
            "user": {"login": REVIEWER, "id": REVIEWER_ID},
            "environments": [{"name": verifier.ENVIRONMENT}],
        }]

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *, environment=None, history=None, actor=ACTOR, run_id=RUN_ID,
                 attempt="1", allowlist=REVIEWER):
        values = {
            "GH_TOKEN": "test-token",
            "GITHUB_REPOSITORY": "hsaidno-cpu/Hypersystem-Orchestrator",
            "GITHUB_RUN_ID": run_id,
            "GITHUB_RUN_ATTEMPT": attempt,
            "GITHUB_ACTOR": actor,
            "GITHUB_ACTOR_ID": "100",
            "HSO_P0_ALLOWED_REVIEWER_LOGINS": allowlist,
        }
        with patch.dict(os.environ, values, clear=True), \
             patch.object(verifier, "api_get", side_effect=[
                 environment if environment is not None else self.environment,
                 history if history is not None else self.history,
             ]), \
             patch.object(sys, "argv", ["verify", "--output", str(self.output)]):
            return verifier.main()

    def test_records_authenticated_independent_reviewer_and_exact_run(self):
        self.assertEqual(self.run_main(), 0)
        record = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(record["workflow_run_id"], RUN_ID)
        self.assertEqual(record["workflow_actor"], ACTOR)
        self.assertEqual(record["workflow_actor_id"], 100)
        self.assertEqual(record["reviewer_login"], REVIEWER)
        self.assertEqual(record["reviewer_id"], REVIEWER_ID)
        self.assertEqual(record["approval_source"], "github_actions_workflow_run_approvals_api")
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o600)

    def test_rejects_requester_self_approval(self):
        history = [{
            "state": "approved",
            "user": {"login": ACTOR, "id": 100},
            "environments": [{"name": verifier.ENVIRONMENT}],
        }]
        with self.assertRaisesRegex(SystemExit, "cannot approve their own"):
            self.run_main(history=history)

    def test_rejects_unconfigured_or_unallowlisted_reviewer(self):
        with self.assertRaisesRegex(SystemExit, "must all be in"):
            self.run_main(allowlist="different-reviewer")
        with self.assertRaisesRegex(SystemExit, "missing required configuration"):
            self.run_main(allowlist="")

    def test_rejects_missing_approval_history(self):
        with self.assertRaisesRegex(SystemExit, "no authenticated approval record"):
            self.run_main(history=[])

    def test_rejects_wrong_environment_or_unapproved_state(self):
        history = [{
            "state": "rejected",
            "user": {"login": REVIEWER, "id": REVIEWER_ID},
            "environments": [{"name": verifier.ENVIRONMENT}],
        }]
        with self.assertRaisesRegex(SystemExit, "not approved"):
            self.run_main(history=history)

    def test_rejects_group_only_environment_reviewer(self):
        environment = {
            "protection_rules": [{
                "type": "required_reviewers",
                "prevent_self_review": True,
                "reviewers": [{"type": "Team", "reviewer": {"slug": "security"}}],
            }],
        }
        with self.assertRaisesRegex(SystemExit, "individually identifiable"):
            self.run_main(environment=environment)

    def test_rejects_retries_and_existing_output(self):
        with self.assertRaisesRegex(SystemExit, "first-attempt"):
            self.run_main(attempt="2")
        self.assertEqual(self.run_main(), 0)
        with self.assertRaisesRegex(SystemExit, "refusing overwrite"):
            self.run_main()


if __name__ == "__main__":
    unittest.main()
