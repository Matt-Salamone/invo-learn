"""Assignment journeys at the accepted installed-command seam S1."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from examples.worked_example import PUBLIC, item, map_spec, spec


class AssignmentJourneys(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-assignments-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "private"
        prefs = self.write({"auto_update": False, "auto_backup": False})
        result = subprocess.run([sys.executable, "-m", "invo_learn", "bootstrap", str(self.root),
                                 "--name", "Synthetic", "--no-git", "--preferences", str(prefs)],
                                cwd=PUBLIC, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.cli("add-course", "math", "--title", "Synthetic math")
        source = self.base / "requirements.txt"
        source.write_text("Build an equation solver and explain inverse operations. Check by substitution.", encoding="utf-8")
        self.material = self.cli("add-material", "math", source)
        mapping = map_spec(self.material["id"], [("solve", "Solve equations", "skill", "whole file", [])])
        proposal = self.cli("propose-map", "math", self.write(mapping))
        self.cli("accept-map", "math", proposal["proposal_id"], "--approval", "Synthetic approval")

    def write(self, obj):
        path = self.base / ("input-" + str(len(list(self.base.glob("input-*")))) + ".json")
        path.write_text(json.dumps(obj), encoding="utf-8")
        return path

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(self.root / "learn.py"), "--today", "2026-10-29", *map(str, args)],
                                cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stdout + result.stderr)
        return json.loads(result.stdout if ok else result.stderr)

    def assignment_spec(self):
        return {"title": "Equation solver", "requirements": ["Use equality-preserving inverse operations"],
                "deliverables": ["A solver with a substitution check"], "criteria": ["Correctly solve a fresh equation"],
                "material_ids": [self.material["id"]]}

    def plan_spec(self):
        return {"rationale": "Teach from the assignment requirements without a completed solution", "lessons": [
            {"id": "inverse", "title": "Inverse operations", "objective_ids": ["solve"], "material_ids": [self.material["id"]]}]}

    def add_assignment(self, aid="solver"):
        return self.cli("add-assignment", "math", aid, self.write(self.assignment_spec()))

    def assignment(self, aid="solver"):
        return self.cli("status")["tracks"]["math"]["assignments"][aid]

    def test_solution_choice_is_explicit_and_kept_when_resuming(self):
        self.add_assignment()
        self.assertIsNone(self.assignment()["solution_choice"])
        self.assertEqual(self.cli("status")["next_action"]["action"], "ask-assignment-solution-choice")
        self.assertEqual(self.assignment()["completion"], "not-started")
        error = self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()), ok=False)
        self.assertIn("solution choice", error["error"])
        self.cli("assignment-choice", "math", "solver", "--solution", "no", "--reason", "Learner explicitly declines")
        self.assertFalse(self.assignment()["solution_choice"]["generate"])
        resumed = self.cli("assignment-choice", "math", "solver", "--solution", "no", "--reason", "Resuming the same answer")
        self.assertEqual(resumed["status"], "already-recorded")
        self.add_assignment("second")
        self.assertIsNone(self.assignment("second")["solution_choice"])
        self.assertFalse(self.assignment()["plans"])

    def test_requirements_led_plan_packet_and_report_have_no_solution_dependency(self):
        self.add_assignment()
        self.cli("assignment-choice", "math", "solver", "--solution", "no", "--reason", "Learner chooses learning first")
        plan = self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()))
        self.assertEqual(plan["basis"], "requirements")
        lesson_spec = spec(["solve"])
        lesson_spec["assignment"] = {"assignment_id": "solver", "plan_id": plan["plan_id"], "lesson_id": "inverse"}
        self.cli("prepare", "math", self.write(lesson_spec), ok=False)
        self.cli("accept-assignment-plan", "math", "solver", plan["plan_id"], "--approval", "Learner accepts requirements-led lessons")
        prepared = self.cli("prepare", "math", self.write(lesson_spec))
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        issued = json.loads((packet / "lesson.json").read_text())
        self.assertEqual(issued["spec"], lesson_spec)
        report = json.loads((packet / "report-template.json").read_text())
        context = report["assignment_context"]
        self.assertEqual(context["assignment_id"], "solver")
        self.assertEqual(context["plan_id"], plan["plan_id"])
        self.assertEqual(context["materials"], [{"material_id": self.material["id"], "sha256": self.material["sha256"]}])
        self.assertNotIn("solution", json.dumps(context))
        side = {"schema_version": 1, "report_type": "side-chat", "report_id": "side-assignment",
                "lesson_id": prepared["lesson_id"], "track_id": "math", "map_revision": 1, "content_revision": 0,
                "assignment_context": context, "remaining_questions": [], "assessment_help": [],
                "discussions": [{"question": "Why inverse operations?", "explanation": "They undo operations while preserving equality.",
                                 "source_reference": "Selected assignment requirements", "objective_ids": ["solve"]}]}
        self.assertEqual(self.cli("ingest", self.write(side))["status"], "supplemental-recorded")
        self.assertEqual(self.cli("status")["pending_lessons"]["math"], [prepared["lesson_id"]])
        self.assertEqual(self.cli("status")["tracks"]["math"]["objectives"]["solve"]["understanding"], "unassessed")

        teaching = (packet / "START-HERE.md").read_text()
        self.assertIn("A solver with a substitution check", teaching)
        self.assertIn("source", teaching.lower())
        self.assertIn("commentary", teaching.lower())
        report.update(completed_on="2026-10-29", session_status="completed", objectives=[item("solve")])
        forged = json.loads(json.dumps(report))
        forged["assignment_context"]["plan_id"] = "other-plan"
        self.cli("ingest", self.write(forged), ok=False)
        self.assertEqual(self.cli("status")["tracks"]["math"]["objectives"]["solve"]["understanding"], "unassessed")
        self.assertEqual(self.cli("ingest", self.write(report))["status"], "imported")
        assignment = self.assignment()
        self.assertEqual(assignment["completion"], "not-started")
        self.assertNotIn("reference_solution", assignment)
        self.assertNotIn("solution_revision", json.dumps(assignment))
        status = self.cli("status")
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["understanding"], "demonstrated")
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["retention"], "unassessed")

    def test_standalone_assignment_uses_same_course_and_coding_packet_workflow(self):
        self.cli("add-course", "standalone", "--title", "Standalone equation-solver project")
        source = self.base / "project.txt"
        source.write_text("Implement a solver and check its result by substitution.", encoding="utf-8")
        material = self.cli("add-material", "standalone", source)
        mapping = map_spec(material["id"], [("solve", "Solve equations", "skill", "whole file", [])])
        proposed = self.cli("propose-map", "standalone", self.write(mapping))
        self.cli("accept-map", "standalone", proposed["proposal_id"], "--approval", "Synthetic scope approval")
        assignment = self.assignment_spec()
        assignment["material_ids"] = [material["id"]]
        self.cli("add-assignment", "standalone", "project", self.write(assignment))
        self.cli("assignment-choice", "standalone", "project", "--solution", "no", "--reason", "Explicit no reference")
        plan_spec = self.plan_spec()
        plan_spec["lessons"][0]["material_ids"] = [material["id"]]
        plan = self.cli("propose-assignment-plan", "standalone", "project", self.write(plan_spec))
        self.cli("accept-assignment-plan", "standalone", "project", plan["plan_id"], "--approval", "Synthetic plan approval")
        lesson = spec(["solve"])
        lesson.update(coding=True, syntax_cheatsheet="# Python syntax\n\n`abs(value)` returns an absolute value.",
                      assignment={"assignment_id": "project", "plan_id": plan["plan_id"], "lesson_id": "inverse"})
        preflight = self.cli("preflight", "standalone", self.write(lesson))
        prepared = self.cli("prepare", "standalone", self.write(lesson))
        self.assertEqual(preflight, prepared["preflight"])
        self.assertTrue((self.root / "mailbox/syntax-cheatsheet.md").is_file())
        self.assertEqual(self.cli("status")["tracks"]["standalone"]["assignments"]["project"]["track_id"], "standalone")
        blocked = self.cli("prepare", "math", self.write(spec(["solve"])), ok=False)
        self.assertIn("awaits report", blocked["error"])
        archived = (self.root / "mailbox/START-HERE.md").read_bytes()
        self.cli("restage", prepared["lesson_id"])
        self.assertEqual(archived, (self.root / "mailbox/START-HERE.md").read_bytes())

    def test_yes_choice_requires_verified_reference_and_damaged_material_stops_packets(self):
        self.add_assignment()
        self.cli("assignment-choice", "math", "solver", "--solution", "yes", "--reason", "Learner requests reference first")
        error = self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()), ok=False)
        self.assertIn("verified", error["error"])
        self.assertFalse(self.assignment()["plans"])
        self.add_assignment("no-reference")
        self.cli("assignment-choice", "math", "no-reference", "--solution", "no", "--reason", "Explicit learning-first choice")
        plan = self.cli("propose-assignment-plan", "math", "no-reference", self.write(self.plan_spec()))
        self.cli("accept-assignment-plan", "math", "no-reference", plan["plan_id"], "--approval", "Synthetic approval")
        (self.root / self.material["original"]).write_bytes(b"damaged")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "no-reference", "plan_id": plan["plan_id"], "lesson_id": "inverse"}
        error = self.cli("prepare", "math", self.write(lesson), ok=False)
        self.assertIn("checksum", error["error"])
        self.assertFalse((self.root / "lessons").exists())
        self.assertEqual(list((self.root / "mailbox").iterdir()), [self.root / "mailbox/.invo-mailbox.json"])
