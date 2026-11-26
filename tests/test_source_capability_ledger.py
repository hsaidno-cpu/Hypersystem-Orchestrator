"""Integrity and claim-boundary tests for the source/capability ledger."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.validate_source_capability_ledger import LedgerValidationError, validate_ledgers

ROOT = Path(__file__).resolve().parents[1]


class SourceCapabilityLedgerTests(unittest.TestCase):
    def test_all_source_parts_and_skill_rows_reconcile(self):
        report = validate_ledgers(ROOT)
        self.assertEqual(report["source_boundaries"], 10)
        self.assertEqual(report["source_file_paths"], 869)
        self.assertEqual(report["previous_expected_paths"], 864)
        self.assertEqual(report["hso_count_delta"], 5)
        self.assertEqual(report["unique_git_blob_sha1_groups"], 859)
        self.assertEqual(report["duplicate_blob_groups"], 5)
        self.assertEqual(report["duplicate_path_records"], 15)
        self.assertEqual(report["skill_metadata_rows"], 289)
        self.assertEqual(report["source_uri_declared"] + report["source_uri_not_declared"], 289)

    def test_capability_readiness_is_not_promoted_by_path_match(self):
        report = validate_ledgers(ROOT)
        self.assertEqual(report["content_sha256"], "NOT_COMPUTED")
        self.assertEqual(report["semantic_parity"], "NOT_COMPARED")
        self.assertEqual(report["behavior_tests"], "NOT_RUN")
        self.assertEqual(report["host_runtime"], "NOT_RUN")

    def test_hso_five_path_discrepancy_is_not_hidden(self):
        report = validate_ledgers(ROOT)
        self.assertEqual(report["hso_count_delta"], 5)

    def test_mutated_part_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in [
                "catalog/source-file-ledger-2026-11-26-part-01.json",
                "catalog/source-file-ledger-2026-11-26-part-02.json",
                "catalog/source-file-ledger-2026-11-26-part-03.json",
                "catalog/source-file-ledger-2026-11-26-index.json",
                "catalog/skill-source-crosswalk-2026-11-26.json",
            ]:
                dest = root / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, dest)
            part = root / "catalog/source-file-ledger-2026-11-26-part-03.json"
            data = json.loads(part.read_text(encoding="utf-8"))
            data["boundaries"][0]["entries"].pop()
            part.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(LedgerValidationError):
                validate_ledgers(root)


if __name__ == "__main__":
    unittest.main()
