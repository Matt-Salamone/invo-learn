"""Exercise the portable synthetic evaluation generator without a teaching API."""
import json
from pathlib import Path
import subprocess
import sys
import unittest


class PacketEvaluationTests(unittest.TestCase):
    def test_synthetic_fresh_chat_cases_construct_and_refuse_missing_context(self):
        public = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(public / "examples/packet_evaluation.py")],
                                cwd=public, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["case_count"], 4)
        self.assertEqual(summary["prepared"], 3)
        self.assertEqual(summary["refused_as_expected"], 1)
        self.assertFalse(summary["teaching_evaluated"])
