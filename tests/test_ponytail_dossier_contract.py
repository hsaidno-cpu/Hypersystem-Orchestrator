"""Schema and authority-boundary tests for the Ponytail Engineering Dossier."""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts" / "ponytail-engineering-dossier.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "ponytail-engineering-dossier.example.json"


class PonytailEngineeringDossierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def test_example_is_valid_against_dossier_schema(self):
        self.validator.validate(self.example)

    def test_ponytail_cannot_claim_source_write_ownership(self):
        payload = copy.deepcopy(self.example)
        payload["authority_boundary"]["source_write_owner"] = "ponytail-engineering-optimizer"
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_sdo_cannot_replace_evaluator_team_as_independent_judge(self):
        payload = copy.deepcopy(self.example)
        payload["authority_boundary"]["independent_evaluator"] = "skill-developer-orchestrator"
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)

    def test_unknown_runtime_dispatch_field_is_rejected(self):
        payload = copy.deepcopy(self.example)
        payload["runtime_dispatch"] = True
        with self.assertRaises(ValidationError):
            self.validator.validate(payload)


if __name__ == "__main__":
    unittest.main()
