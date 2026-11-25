"""Static acceptance checks for the HSO Octa-Prompt master instruction."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "prompts" / "HSO-SUPER-ORCHESTRATOR-MASTER-PROMPT.md"

EXPECTED_HEADINGS = [
    "ROLE & PERSONA ARCHETYPE",
    "CORE OBJECTIVE & TASK MATRIX",
    "CONTEXT & VARIABLE ANCHORS",
    "COGNITIVE REASONING & WORKFLOW",
    "CONSTRAINTS & NEGATIVE GUARDRAILS",
    "EDGE CASES & ERROR HANDLING",
    "STOP & COMPLETION CRITERIA",
    "OUTPUT SCHEMA & FORMATTING SPEC",
]


class HsoMasterPromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = PROMPT.read_text(encoding="utf-8")

    def test_master_prompt_file_exists_and_has_metadata(self):
        self.assertTrue(PROMPT.is_file())
        self.assertIn("Prompt ID:** HSO-MASTER-001", self.content)
        self.assertIn("NOT_TARGET_TESTED", self.content)
        self.assertIn("NOT_RELEASED", self.content)

    def test_eight_octa_headings_exist_in_canonical_order(self):
        headings = re.findall(r"(?m)^## ([1-8])\. (.+)$", self.content)
        self.assertEqual([number for number, _ in headings], list("12345678"))
        self.assertEqual([heading for _, heading in headings], EXPECTED_HEADINGS)

    def test_prompt_preserves_hso_control_plane_and_not_a_plugin_boundary(self):
        self.assertIn("bukan plugin ke-23", self.content)
        self.assertIn("HSMART", self.content)
        self.assertIn("A.S.F.R.E.E", self.content)
        self.assertIn("PRE", self.content)

    def test_prompt_separates_authority_capability_and_runtime_evidence(self):
        for token in ("S0 OBSERVE", "S5 PRODUCTION_RELEASE", "ACCESS_DENIED", "NOT_CHECKED",
                      "C4", "C5", "human", "explicit approval"):
            self.assertIn(token, self.content)

    def test_prompt_contains_recovery_and_completion_gates(self):
        for token in ("PARTIAL", "BLOCKED", "UNVERIFIABLE", "Definition of Done",
                      "residual risks", "NOT_RUN"):
            self.assertIn(token, self.content)


if __name__ == "__main__":
    unittest.main()
