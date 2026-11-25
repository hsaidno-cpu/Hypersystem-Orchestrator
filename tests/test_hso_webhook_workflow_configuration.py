from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "hso-mission-control-sync.yml"


class HsoWebhookWorkflowConfigurationTests(unittest.TestCase):
    def test_event_delivery_requires_all_three_configuration_values(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        event_job = workflow.split("  scheduled-reconciliation:", 1)[0]

        for value in (
            "HSO_GITHUB_WEBHOOK_URL",
            "HSO_SYNC_TOKEN",
            "HSO_WEBHOOK_SIGNING_SECRET",
        ):
            self.assertIn(value, event_job)

        guard = re.search(r"if \[(.*?)\]; then", event_job, re.DOTALL)
        self.assertIsNotNone(guard, "event job must have an explicit fail-closed shell guard")
        expression = guard.group(1)
        for value in (
            "$HSO_GITHUB_WEBHOOK_URL",
            "$HSO_SYNC_TOKEN",
            "$HSO_WEBHOOK_SIGNING_SECRET",
        ):
            self.assertIn(value, expression)

        self.assertIn("exit 0", event_job, "incomplete event configuration must be safe-skipped")

    def test_scheduled_reconciliation_requires_its_dedicated_sync_token(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        scheduled = workflow.split("  scheduled-reconciliation:", 1)[1]
        self.assertIn("HSO_GITHUB_WEBHOOK_URL", scheduled)
        self.assertIn("HSO_SYNC_TOKEN", scheduled)
        self.assertIn('python tools/emit_hso_sync_event.py --mode reconcile', scheduled)
        self.assertNotIn("HSO_WEBHOOK_SIGNING_SECRET", scheduled)

    def test_legacy_native_github_secret_is_not_wired_into_actions(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("GITHUB_WEBHOOK_SECRET", workflow)
        self.assertNotIn("x-hub-signature-256", workflow)


if __name__ == "__main__":
    unittest.main()
