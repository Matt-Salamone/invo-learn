"""S1 installed legacy readers, using synthetic historical filesystem records."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PUBLIC = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class LegacyReadersTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-legacy-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.workspace = self.base / "installed"
        installed = subprocess.run([sys.executable, "-m", "invo_learn", "bootstrap",
                                   str(self.workspace), "--source", str(PUBLIC),
                                   "--name", "Synthetic", "--no-git"], cwd=PUBLIC,
                                  capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.source = self.base / "old-assignment"
        self.source.mkdir()
        self.packet = {"assignment_id": "08000000-0000-0000-0000-000000000001",
                       "lesson_id": "reasoning", "packet_id": "08000000-0000-0000-0000-000000000002",
                       "contract_version": 1, "solution_revision": "a" * 40,
                       "path": "packets/original", "status": "outstanding", "included": []}
        self.state = {"state_version": 1, "assignment_id": self.packet["assignment_id"],
                      "name": "Synthetic fractions", "skill_version": "0.4.0",
                      "status": "teaching", "next_action": "return-lesson-report",
                      "solution": {"revision": "b" * 40, "artifacts": []},
                      "packets": {self.packet["packet_id"]: self.packet},
                      "active_packet": self.packet["packet_id"], "evidence": []}
        write_json(self.source / ".invo/state.json", self.state)
        write_json(self.source / "packets/original/manifest.json", self.packet)
        for name in ("tutor.md", "report-template.json", "report-contract.json"):
            (self.source / "packets/original" / name).write_text("Synthetic preserved " + name, encoding="utf-8")
        (self.source / "untracked.txt").write_text("Original untracked learner work", encoding="utf-8")

    def run_command(self, *args):
        result = subprocess.run([sys.executable, "-B", str(self.workspace / "learn.py"), *map(str, args)],
                                capture_output=True, text=True, cwd=self.base)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def report(self):
        return {k: self.packet[k] for k in ("assignment_id", "lesson_id", "packet_id",
                                          "contract_version", "solution_revision")} | {
            "observations": [{"criterion": "Explain denominators", "question": "What does 4 mean in 3/4?",
                              "learner_response": "Four equal parts", "assistance": "none",
                              "evidence_level": "independent"}],
            "remaining_gaps": [], "suspected_errors": []}

    def test_installed_assignment_inspection_is_read_only_and_keeps_original_identity(self):
        before = hashes(self.source)
        destination_before = hashes(self.workspace)
        inspected = self.run_command("legacy-status", self.source)
        self.assertEqual(inspected["kind"], "assignment")
        self.assertEqual(inspected["origin"]["id"], self.state["assignment_id"])
        self.assertEqual(inspected["pending"], [self.packet["packet_id"]])
        self.assertEqual(inspected["packets"][self.packet["packet_id"]]["solution_revision"], "a" * 40)
        self.assertEqual(inspected["current_solution_revision"], "b" * 40)
        self.assertEqual(hashes(self.source), before)
        self.assertEqual(hashes(self.workspace), destination_before)

    def test_report_resolves_exact_issued_revision_even_after_solution_changes(self):
        returned = self.source / "reports/late.json"
        write_json(returned, self.report())
        before = hashes(self.source)
        inspected = self.run_command("legacy-report", self.source, returned)
        self.assertEqual(inspected["status"], "associated")
        self.assertEqual(inspected["context"]["solution_revision"], "a" * 40)
        self.assertTrue(inspected["historical_context"])
        self.assertEqual(inspected["report"]["observations"][0]["learner_response"], "Four equal parts")
        self.assertEqual(inspected["raw_sha256"], hashlib.sha256(returned.read_bytes()).hexdigest())
        self.assertEqual(hashes(self.source), before)

    def test_malformed_and_broken_associations_remain_readable_without_credit(self):
        returned = self.source / "reports/return.json"
        write_json(returned, self.report())
        for field, wrong in (("assignment_id", "other"), ("packet_id", "unknown"),
                             ("lesson_id", "other"), ("contract_version", True),
                             ("solution_revision", "b" * 40)):
            with self.subTest(field=field):
                value = self.report()
                value[field] = wrong
                write_json(returned, value)
                original = returned.read_bytes()
                result = self.run_command("legacy-report", self.source, returned)
                self.assertEqual(result["status"], "unresolved")
                self.assertFalse(result["credit_applied"])
                self.assertEqual(returned.read_bytes(), original)
        returned.write_bytes(b"{broken\r\n")
        result = self.run_command("legacy-report", self.source, returned)
        self.assertEqual(result["status"], "malformed")
        self.assertTrue(result["reason"])
        self.assertEqual(result["raw_bytes"], 9)
        self.assertEqual(returned.read_bytes(), b"{broken\r\n")

    def test_associated_packet_does_not_make_an_invalid_observation_valid(self):
        value = self.report()
        value["observations"][0]["learner_response"] = ""
        returned = self.source / "returned.json"
        write_json(returned, value)
        result = self.run_command("legacy-report", self.source, returned)
        self.assertEqual(result["status"], "invalid")
        self.assertFalse(result["credit_applied"])

    def test_damaged_original_packet_is_diagnostic_and_cannot_be_associated(self):
        payload = b"Original source passage\n"
        source = self.source / "packets/original/context/0-source.txt"
        source.parent.mkdir(parents=True)
        source.write_bytes(payload)
        self.packet["included"] = [{"source": "materials/originals/source.txt",
                                    "path": "context/0-source.txt", "reference": "Synthetic source",
                                    "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}]
        write_json(self.source / ".invo/state.json", self.state)
        write_json(self.source / "packets/original/manifest.json", self.packet)
        returned = self.source / "returned.json"
        write_json(returned, self.report())
        self.assertEqual(self.run_command("legacy-report", self.source, returned)["status"], "associated")
        source.write_bytes(b"damaged")
        before = hashes(self.source)
        status = self.run_command("legacy-status", self.source)
        self.assertTrue(status["integrity_problems"])
        result = self.run_command("legacy-report", self.source, returned)
        self.assertEqual(result["status"], "unresolved")
        self.assertIn("checksum", result["reason"])
        self.assertEqual(hashes(self.source), before)

    def test_course_main_and_side_returns_keep_exact_packet_revision_and_fenced_bytes(self):
        from examples.worked_example import item, make_report
        source = self.base / "old-course"
        lesson = {"id": "lesson-original", "track_id": "algebra", "status": "prepared",
                  "objective_ids": ["solve"], "prepared_on": "2026-10-14",
                  "map_revision": 1, "content_revision": 0, "staged_files": {}}
        write_json(source / "lessons/lesson-original/packet/lesson.json", lesson)
        state = {"schema_version": 1, "workspace_id": "synthetic-course",
                 "lessons": {lesson["id"]: lesson}, "tracks": {"algebra": {"map_revision": 2}}}
        write_json(source / "state.json", state)
        returned = source / "late.txt"
        original = ("```json\r\n" + json.dumps(make_report(lesson, "2026-10-14", [item("solve")]))
                    + "\r\n```\r\n").encode()
        returned.write_bytes(original)
        before = hashes(source)
        result = self.run_command("legacy-report", source, returned)
        self.assertEqual(result["status"], "associated")
        self.assertTrue(result["historical_context"])
        self.assertEqual(result["context"]["map_revision"], 1)
        self.assertEqual(hashes(source), before)
        side = {"schema_version": 1, "report_type": "side-chat", "report_id": "side-original",
                "lesson_id": lesson["id"], "track_id": "algebra", "map_revision": 1,
                "content_revision": 0, "discussions": [{"question": "Why equality?",
                "explanation": "Balance both sides", "source_reference": "Synthetic note"}],
                "remaining_questions": [], "assessment_help": []}
        write_json(returned, side)
        self.assertEqual(self.run_command("legacy-report", source, returned)["status"], "associated")
        side["map_revision"] = 2
        write_json(returned, side)
        self.assertEqual(self.run_command("legacy-report", source, returned)["status"], "unresolved")

    def test_legacy_assignment_side_report_is_separate_from_formal_evidence(self):
        side = {k: self.packet[k] for k in ("assignment_id", "lesson_id", "packet_id",
                                          "contract_version", "solution_revision")}
        side.update(report_type="side-chat", report_id="side-original",
                    discussions=[{"question": "How do parts relate?", "explanation": "Compare equal parts",
                                  "source_reference": "Synthetic source"}], remaining_questions=[],
                    assessment_help=[{"question": "What does 4 mean in 3/4?", "help": "Four equal parts",
                                      "timing": "before-answer"}])
        returned = self.source / "side.json"
        write_json(returned, side)
        before = hashes(self.source)
        result = self.run_command("legacy-report", self.source, returned)
        self.assertEqual(result["status"], "associated")
        self.assertEqual(result["report"]["assessment_help"][0]["timing"], "before-answer")
        self.assertFalse(result["credit_applied"])
        self.assertEqual(hashes(self.source), before)

    def test_missing_required_snapshot_file_refuses_report_association(self):
        (self.source / "packets/original/tutor.md").unlink()
        returned = self.source / "returned.json"
        write_json(returned, self.report())
        result = self.run_command("legacy-report", self.source, returned)
        self.assertEqual(result["status"], "unresolved")
        self.assertIn("tutor.md", result["reason"])


if __name__ == "__main__":
    unittest.main()
