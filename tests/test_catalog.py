"""Unit tests for central catalog invariants."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CatalogValidationTests(unittest.TestCase):
    def test_catalog_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate_catalog.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("PASS: 20 unique plugin identities", result.stdout)
        self.assertIn("PASS: 3 declared and pinned source submodules", result.stdout)

    def test_private_submodule_is_declared(self):
        gitmodules = (ROOT / ".gitmodules").read_text(encoding="utf-8")
        self.assertIn("anatomi-prompt-strategis", gitmodules)
        self.assertIn("https://github.com/hsaidno-cpu/anatomi-prompt-strategis.git", gitmodules)

    def test_legacy_plugin_is_redirect_only(self):
        import json
        catalog = json.loads((ROOT / "catalog" / "plugins.json").read_text(encoding="utf-8"))
        legacy = next(p for p in catalog["plugins"] if p["plugin_key"] == "asfree-legacy")
        self.assertEqual(legacy["source_state"], "canonical_redirect")
        self.assertEqual(legacy["alias_of"], "asfree-canonical")


if __name__ == "__main__":
    unittest.main()
