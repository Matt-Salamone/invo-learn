"""Guided and independent work through the agreed installed command seam S1."""
import json

import test_assignments
from examples.worked_example import item, spec


class ImplementationJourneys(test_assignments.AssignmentJourneys):
    # Reuse only installed-workspace setup/helpers, not the base test cases.
    test_solution_choice_is_explicit_and_kept_when_resuming = None
    test_requirements_led_plan_packet_and_report_have_no_solution_dependency = None
    test_standalone_assignment_uses_same_course_and_coding_packet_workflow = None
    test_yes_choice_requires_verified_reference_and_damaged_material_stops_packets = None

    def ready(self):
        self.add_assignment()
        self.cli("assignment-choice", "math", "solver", "--solution", "no", "--reason", "Actual synthetic no")
        plan = self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()))
        self.cli("accept-assignment-plan", "math", "solver", plan["plan_id"], "--approval", "Actual synthetic plan approval")
        return plan["plan_id"]

    def progress(self, complete=True):
        return {"deliverables": [{"deliverable": "A solver with a substitution check",
                    "status": "completed" if complete else "in-progress",
                    "evidence": "Learner ran the solver and substitution check" if complete else "Learner wrote the inverse operation step"}],
                "checks": [{"criterion": "Correctly solve a fresh equation", "result": "passed" if complete else "limited",
                            "method": "Run learner work on a fresh input", "evidence": "Actual synthetic run checked the result"}],
                "assistance": [], "limitations": []}

    def test_independent_implementation_requires_fresh_choice_and_adds_no_handoff_or_mastery(self):
        self.ready()
        self.assertNotIn("implementation", self.assignment())
        self.cli("implementation-choice", "math", "solver", "--guidance", "no", "--reason", "Too early", ok=False)
        reached = self.cli("begin-implementation", "math", "solver", "--reason", "Learner reaches final implementation")
        self.assertIn("guidance", reached["question"])
        self.assertIsNone(self.assignment()["implementation"]["decision"])
        self.assertEqual(self.cli("status")["next_action"]["action"], "ask-implementation-guidance")
        self.cli("record-implementation", "math", "solver", self.write(self.progress()), ok=False)
        chosen = self.cli("implementation-choice", "math", "solver", "--guidance", "no", "--reason", "Learner explicitly chooses independent work")
        repeated = self.cli("implementation-choice", "math", "solver", "--guidance", "no", "--reason", "Resume same answer")
        self.assertEqual(repeated["status"], "already-recorded")
        self.assertEqual(repeated["decision"], chosen["decision"])
        self.cli("record-implementation", "math", "solver", self.write(self.progress()))
        assignment = self.assignment()
        self.assertEqual(assignment["completion"], "completed")
        self.assertEqual(len(assignment["implementation"]["progress"]), 1)
        status = self.cli("status")
        self.assertEqual(status["pending_lessons"]["math"], [])
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["understanding"], "unassessed")
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["retention"], "unassessed")
        self.assertFalse((self.root / "lessons").exists())

    def test_guided_partial_then_completed_work_uses_one_slot_and_keeps_help(self):
        plan = self.ready()
        self.cli("begin-implementation", "math", "solver", "--reason", "Learner reaches implementation")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "solver", "plan_id": plan, "lesson_id": "inverse", "phase": "implementation"}
        self.cli("prepare", "math", self.write(lesson), ok=False)
        self.cli("implementation-choice", "math", "solver", "--guidance", "yes", "--reason", "Learner requests guidance")
        preflight = self.cli("preflight", "math", self.write(lesson))
        prepared = self.cli("prepare", "math", self.write(lesson))
        self.assertEqual(preflight, prepared["preflight"])
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        archived = (packet / "START-HERE.md").read_bytes()
        self.assertIn(b"learner edits and runs", archived.lower())
        self.assertIn(b"direct code", archived.lower())
        self.cli("prepare", "math", self.write(spec(["solve"])), ok=False)
        self.assertEqual((self.root / "mailbox/START-HERE.md").read_bytes(), archived)
        report = json.loads((packet / "report-template.json").read_text())
        self.assertIn("implementation_progress", report)
        self.assertEqual(report["assignment_context"]["implementation"]["guided"], True)
        progress = self.progress(complete=False)
        progress["assistance"] = [{"question": "How do I undo the addition?", "help": "Tutor gave a requested worked step",
                                   "timing": "before-answer", "objective_ids": ["solve"]}]
        assessed = item("solve")
        assessed["assessments"][0].update(assistance="heavy", assistance_details="Requested worked step before answering", independent=False)
        report.update(completed_on="2026-10-29", implementation_progress=progress, objectives=[assessed])
        self.cli("ingest", self.write(report))
        self.assertEqual(self.assignment()["completion"], "in-progress")
        self.assertEqual(self.cli("status")["lesson_history"][prepared["lesson_id"]]["status"], "paused")
        self.assertEqual(self.cli("status")["tracks"]["math"]["objectives"]["solve"]["understanding"], "needs-practice")
        second = self.cli("prepare", "math", self.write(lesson))
        packet2 = self.root / "lessons" / second["lesson_id"] / "packet"
        completed = json.loads((packet2 / "report-template.json").read_text())
        completed.update(completed_on="2026-10-29", session_status="completed", implementation_progress=self.progress())
        self.cli("ingest", self.write(completed))
        self.assertEqual(self.assignment()["completion"], "completed")
        self.assertEqual(len(self.assignment()["implementation"]["progress"]), 2)
        self.assertEqual(self.cli("ingest", self.write(completed))["status"], "duplicate")
        self.assertEqual(len(self.assignment()["implementation"]["progress"]), 2)
        self.assertEqual((packet / "START-HERE.md").read_bytes(), archived)
        self.assertEqual(self.assignment()["implementation"]["progress"][0]["progress"]["assistance"], progress["assistance"])

    def test_new_guidance_decision_retains_issued_context_and_actual_help_history(self):
        plan = self.ready()
        self.cli("begin-implementation", "math", "solver", "--reason", "Learner transitions to implementation")
        self.cli("implementation-choice", "math", "solver", "--guidance", "yes", "--reason", "Actual yes")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "solver", "plan_id": plan, "lesson_id": "inverse", "phase": "implementation"}
        prepared = self.cli("prepare", "math", self.write(lesson))
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        report = json.loads((packet / "report-template.json").read_text())
        original_context = report["assignment_context"]
        self.cli("implementation-choice", "math", "solver", "--guidance", "no", "--reason", "Contradictory resume", ok=False)
        changed = self.cli("implementation-choice", "math", "solver", "--guidance", "no", "--new-decision", "--reason", "Learner explicitly changes to independent work")
        self.assertNotEqual(changed["decision"]["id"], original_context["implementation"]["decision_id"])
        self.assertTrue(self.assignment()["implementation"]["decision_history"][0]["guided"])
        self.cli("prepare", "math", self.write(lesson), ok=False)
        progress = self.progress(False)
        progress["assistance"] = [{"question": "How should I start?", "help": "Learner requested and received direct code",
                                   "timing": "before-answer", "objective_ids": ["solve"]}]
        report.update(completed_on="2026-10-29", implementation_progress=progress)
        self.cli("ingest", self.write(report))
        self.assertEqual(json.loads((packet / "report-template.json").read_text())["assignment_context"], original_context)
        self.assertEqual(self.assignment()["implementation"]["progress"][0]["decision_id"], original_context["implementation"]["decision_id"])
        recorded = self.cli("record-implementation", "math", "solver", self.write(self.progress()))
        duplicate = self.cli("record-implementation", "math", "solver", self.write(self.progress()))
        self.assertEqual(recorded["progress_id"], duplicate["progress_id"])
        self.assertEqual(duplicate["status"], "already-recorded")
        self.assertEqual(len(self.assignment()["implementation"]["progress"]), 2)
        self.assertEqual(self.assignment()["completion"], "completed")
        self.assertEqual(self.cli("status")["tracks"]["math"]["objectives"]["solve"]["understanding"], "unassessed")

    def test_invalid_progress_preserves_pending_packet_and_completion_needs_actual_checks(self):
        plan = self.ready()
        self.cli("begin-implementation", "math", "solver", "--reason", "Learner reaches implementation")
        self.cli("implementation-choice", "math", "solver", "--guidance", "yes", "--reason", "Explicit guidance")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "solver", "plan_id": plan, "lesson_id": "inverse", "phase": "implementation"}
        prepared = self.cli("prepare", "math", self.write(lesson))
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        report = json.loads((packet / "report-template.json").read_text())
        progress = self.progress()
        progress["deliverables"][0]["deliverable"] = "Unknown deliverable"
        report.update(completed_on="2026-10-29", session_status="completed", implementation_progress=progress)
        raw = self.write(report)
        self.cli("ingest", raw, ok=False)
        self.assertEqual(self.assignment()["completion"], "not-started")
        self.assertEqual(self.cli("status")["pending_lessons"]["math"], [prepared["lesson_id"]])
        self.assertIn(raw.read_bytes(), [path.read_bytes() for path in (self.root / "inbox/reports").glob("*.txt")])
        report["implementation_progress"] = self.progress()
        report["implementation_progress"]["checks"] = []
        self.cli("ingest", self.write(report))
        self.assertEqual(self.assignment()["completion"], "in-progress")
        self.assertEqual(self.cli("status")["lesson_history"][prepared["lesson_id"]]["status"], "reported")

    def test_withdrawn_completion_is_not_restored_by_later_partial_independent_work(self):
        plan = self.ready()
        self.cli("begin-implementation", "math", "solver", "--reason", "Learner starts implementation")
        self.cli("implementation-choice", "math", "solver", "--guidance", "yes", "--reason", "Actual yes")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "solver", "plan_id": plan, "lesson_id": "inverse", "phase": "implementation"}
        prepared = self.cli("prepare", "math", self.write(lesson))
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        report = json.loads((packet / "report-template.json").read_text())
        report.update(completed_on="2026-10-29", session_status="completed", implementation_progress=self.progress())
        self.cli("ingest", self.write(report))
        self.assertEqual(self.assignment()["completion"], "completed")
        self.cli("dispute", report["report_id"], "--reason", "The supposed run was not performed")
        self.assertEqual(self.assignment()["completion"], "not-started")
        self.cli("implementation-choice", "math", "solver", "--guidance", "no", "--new-decision", "--reason", "Actual later independent choice")
        self.cli("record-implementation", "math", "solver", self.write({"deliverables": [], "checks": [], "assistance": [], "limitations": ["No evaluated work yet"]}))
        self.assertEqual(self.assignment()["completion"], "not-started")
        self.assertEqual(len(self.assignment()["implementation"]["progress"]), 2)

