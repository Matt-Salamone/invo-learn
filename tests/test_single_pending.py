"""Installed S1 journeys for one workspace-wide handoff and partial returns."""
import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from examples.worked_example import PUBLIC, item, make_report, map_spec, spec


class SinglePendingJourneys(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-single-pending-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "private"
        prefs = self.write({"auto_update": False, "auto_backup": False})
        out = subprocess.run([sys.executable, "-m", "invo_learn", "bootstrap", str(self.root),
                              "--name", "Synthetic", "--no-git", "--preferences", str(prefs)],
                             cwd=PUBLIC, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        source = self.base / "notes.txt"
        source.write_text("Inverse operations preserve equality. Solve linear equations.", encoding="utf-8")
        for tid in ("math", "science"):
            self.cli("add-course", tid, "--title", tid)
            m = self.cli("add-material", tid, source)
            mapping = map_spec(m["id"], [("solve", "Solve a linear equation", "skill", "whole file", [])])
            p = self.cli("propose-map", tid, self.write(mapping))
            self.cli("accept-map", tid, p["proposal_id"], "--approval", "Synthetic approval")

    def write(self, obj):
        path = self.base / ("input-" + str(len(list(self.base.glob("input-*")))) + ".json")
        path.write_text(json.dumps(obj), encoding="utf-8")
        return path

    def command(self, *args):
        return [sys.executable, str(self.root / "learn.py"), "--today", "2026-10-29", *map(str, args)]

    def cli(self, *args, ok=True):
        out = subprocess.run(self.command(*args), cwd=self.base, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0 if ok else 2, out.stdout + out.stderr)
        return json.loads(out.stdout if ok else out.stderr)

    def prepare(self, tid="math"):
        return self.cli("prepare", tid, self.write(spec(["solve"])))

    def report(self, prepared, session_status="in-progress", rid="partial-report"):
        report = make_report({"id": prepared["lesson_id"], "track_id": "math"}, "2026-10-29", [item("solve")], rid)
        report["session_status"] = session_status
        return report

    def snapshot(self, folder):
        return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*") if p.is_file()}

    def test_second_course_cannot_mutate_pending_packet_or_mailbox(self):
        first = self.prepare()
        box = self.snapshot(self.root / "mailbox")
        packets = self.snapshot(self.root / "lessons")
        error = self.cli("prepare", "science", self.write(spec(["solve"])), ok=False)
        self.assertIn("awaits report", error["error"])
        self.assertEqual(box, self.snapshot(self.root / "mailbox"))
        self.assertEqual(packets, self.snapshot(self.root / "lessons"))
        self.assertEqual(self.cli("status")["pending_lessons"], {"math": [first["lesson_id"]], "science": []})

    def test_partial_return_releases_slot_and_preserves_evaluated_progress(self):
        first = self.prepare()
        before = self.snapshot(self.root / "lessons" / first["lesson_id"] / "packet")
        report = self.report(first)
        raw = json.dumps(report)
        returned = self.write(report)
        result = self.cli("ingest", returned)
        self.assertEqual(result["status"], "imported")
        status = self.cli("status")
        self.assertEqual(status["lesson_history"][first["lesson_id"]]["status"], "paused")
        self.assertEqual(status["lesson_history"][first["lesson_id"]]["session_status"], "in-progress")
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["understanding"], "demonstrated")
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["retention"], "unassessed")
        self.assertEqual(self.cli("ingest", returned)["status"], "duplicate")
        self.prepare("science")
        self.assertEqual(before, self.snapshot(self.root / "lessons" / first["lesson_id"] / "packet"))
        self.assertTrue(any(p.read_text(encoding="utf-8") == raw for p in (self.root / "inbox/reports").glob("*.txt")))

    def test_retired_packet_late_return_is_reviewed_without_reopening_checkout(self):
        first = self.prepare()
        self.cli("abandon", first["lesson_id"], "--reason", "Synthetic explicit retirement")
        second = self.prepare("science")
        report = self.write(self.report(first))
        outcome = self.cli("ingest", report)
        self.assertEqual(outcome["status"], "needs-review")
        status = self.cli("status")
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["understanding"], "unassessed")
        self.assertEqual(status["lesson_history"][first["lesson_id"]]["status"], "abandoned")
        decisions = self.write({"solve": {"status": "retained", "reason": "Exact original task is unchanged and relevant"}})
        self.assertEqual(self.cli("review-import", outcome["import_id"], decisions)["status"], "imported")
        self.assertEqual(self.cli("ingest", report)["status"], "duplicate")
        status = self.cli("status")
        self.assertEqual(status["pending_lessons"], {"math": [], "science": [second["lesson_id"]]})
        self.assertEqual(status["lesson_history"][first["lesson_id"]]["status"], "abandoned")
        self.assertEqual(status["lesson_history"][first["lesson_id"]]["session_status"], "in-progress")

    def test_competing_writers_cannot_issue_two_packets(self):
        lesson = self.write(spec(["solve"]))
        processes = [subprocess.Popen(self.command("prepare", tid, lesson), cwd=self.base,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for tid in ("math", "science")]
        outputs = [process.communicate(timeout=30) for process in processes]
        self.assertEqual(sorted(process.returncode for process in processes), [0, 2], outputs)
        self.assertEqual(sum(len(ids) for ids in self.cli("status")["pending_lessons"].values()), 1)
        self.assertEqual(len(list((self.root / "lessons").iterdir())), 1)
        packet = json.loads((self.root / "mailbox/lesson.json").read_text())
        self.assertIn(packet["id"], sum(self.cli("status")["pending_lessons"].values(), []))

    def test_malformed_partial_return_can_be_repaired_without_inventing_progress(self):
        first = self.prepare()
        report = self.report(first)
        report["objectives"][0].update(coverage="unassessed", judgment="uncertain", assessments=[])
        malformed = dict(report, session_status="paused")
        error = self.cli("ingest", self.write(malformed), ok=False)
        self.assertIn("session_status", error["error"])
        status = self.cli("status")
        self.assertEqual(status["pending_lessons"]["math"], [first["lesson_id"]])
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["understanding"], "unassessed")
        import_id = hashlib.sha256(json.dumps(malformed).encode("utf-8")).hexdigest()
        self.cli("ingest", self.write(report), "--repair-of", import_id,
                 "--repair-note", "Corrected invalid status spelling; no learner evidence changed")
        status = self.cli("status")
        self.assertEqual(status["lesson_history"][first["lesson_id"]]["status"], "paused")
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["understanding"], "unassessed")
        self.assertIsNone(status["tracks"]["math"]["objectives"]["solve"]["review"])
        resumed = self.prepare()
        self.assertNotEqual(resumed["lesson_id"], first["lesson_id"])

    def test_side_return_does_not_release_the_main_pending_slot(self):
        first = self.prepare()
        lesson = json.loads((self.root / "mailbox/lesson.json").read_text())
        side = {"schema_version": 1, "report_type": "side-chat", "report_id": "side-one",
                "lesson_id": first["lesson_id"], "track_id": "math", "map_revision": lesson["map_revision"],
                "content_revision": lesson["content_revision"], "remaining_questions": [], "assessment_help": [],
                "discussions": [{"question": "What does equality mean?", "explanation": "Both expressions have the same value.",
                                 "source_reference": "Synthetic teaching context", "objective_ids": ["solve"]}]}
        self.assertEqual(self.cli("ingest", self.write(side))["status"], "supplemental-recorded")
        self.cli("prepare", "science", self.write(spec(["solve"])), ok=False)
        self.assertEqual(self.cli("status")["pending_lessons"]["math"], [first["lesson_id"]])
