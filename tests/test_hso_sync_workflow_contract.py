from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "hso-mission-control-sync.yml"


class HsoSyncWorkflowContractTests(unittest.TestCase):
    def test_event_ingestion_requires_all_three_separate_configuration_values(self) -> None:
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("HSO_GITHUB_WEBHOOK_URL: ${{ vars.HSO_GITHUB_WEBHOOK_URL }}", content)
        self.assertIn("HSO_SYNC_TOKEN: ${{ secrets.HSO_SYNC_TOKEN }}", content)
        self.assertIn("HSO_WEBHOOK_SIGNING_SECRET: ${{ secrets.HSO_WEBHOOK_SIGNING_SECRET }}", content)
        self.assertIn(
            'if [ -z "$HSO_GITHUB_WEBHOOK_URL" ] || [ -z "$HSO_SYNC_TOKEN" ] || [ -z "$HSO_WEBHOOK_SIGNING_SECRET" ]; then',
            content,
        )
        self.assertNotIn("HSO_SYNC_URL:", content)
        self.assertNotIn("GITHUB_WEBHOOK_SECRET", content)

    def test_scheduled_reconciliation_requires_endpoint_and_sync_token(self) -> None:
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('if [ -z "$HSO_GITHUB_WEBHOOK_URL" ] || [ -z "$HSO_SYNC_TOKEN" ]; then', content)
        self.assertIn("python tools/emit_hso_sync_event.py --mode reconcile", content)


if __name__ == "__main__":
    unittest.main()
