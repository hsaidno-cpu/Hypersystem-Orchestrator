from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE_TEST = ROOT / "tests" / "hso_webhook_handler_node_test.mjs"


class HsoWebhookHandlerRuntimeTests(unittest.TestCase):
    def test_shared_handler_cases_run_under_node_web_runtime(self) -> None:
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node.js is required to execute the shared handler test cases")
        result = subprocess.run(
            [str(node), "--experimental-strip-types", "--test", str(NODE_TEST)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg="Handler runtime tests failed.\nSTDOUT:\n" + result.stdout + "\nSTDERR:\n" + result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
