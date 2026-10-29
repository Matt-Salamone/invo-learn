"""Shared assignment/course evidence at the approved installed command seam S1."""
import json
import subprocess
import sys
import unittest

import test_assignments
import test_implementation
from examples.worked_example import assessment, item, phased, spec


class SharedAssignmentEvidence(unittest.TestCase):
    setUp = test_assignments.AssignmentJourneys.setUp
    write = test_assignments.AssignmentJourneys.write
    assignment_spec = test_assignments.AssignmentJourneys.assignment_spec
    plan_spec = test_assignments.AssignmentJourneys.plan_spec
    add_assignment = test_assignments.AssignmentJourneys.add_assignment
    assignment = test_assignments.AssignmentJourneys.assignment
    ready = test_implementation.ImplementationJourneys.ready
    progress = test_implementation.ImplementationJourneys.progress

    def cli(self, *args, ok=True, day="2026-10-29"):
        result = subprocess.run([sys.executable, str(self.root / "learn.py"), "--today", day, *map(str, args)],
                                cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stdout + result.stderr)
        return json.loads(result.stdout if ok else result.stderr)

    def objective(self):
        return self.cli("status")["tracks"]["math"]["objectives"]["solve"]

    def guided(self, plan):
        self.cli("begin-implementation", "math", "solver", "--reason", "Actual transition")
        self.cli("implementation-choice", "math", "solver", "--guidance", "yes", "--reason", "Actual guidance choice")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "solver", "plan_id": plan, "lesson_id": "inverse", "phase": "implementation"}
        return self.cli("prepare", "math", self.write(lesson))

    def main(self, prepared, items, day="2026-10-29"):
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        report = json.loads((packet / "report-template.json").read_text())
        report.update(completed_on=day, session_status="completed", objectives=items)
        return report

    def test_actual_implementation_help_qualifies_assessment_but_fresh_check_and_delayed_review_can_demonstrate(self):
        plan = self.ready()
        guided = self.guided(plan)
        observed = assessment()
        report = self.main(guided, [item("solve", observed)])
        progress = self.progress()
        progress["assistance"] = [{"question": observed["question"], "help": "Learner requested code solving this exact task",
                                   "timing": "before-answer", "objective_ids": ["solve"]}]
        report["implementation_progress"] = progress
        self.cli("ingest", self.write(report))
        self.assertEqual(self.assignment()["completion"], "completed")
        self.assertEqual(self.objective()["understanding"], "needs-practice")
        self.assertEqual(self.objective()["review"]["last_result"], "not-demonstrated")
        self.assertEqual(self.objective()["evidence"][0]["assessments"][0], observed)
        fresh = self.cli("prepare", "math", self.write(spec(["solve"])))
        independent = assessment()
        independent.update(question="Solve 5x-7=18 and explain why each step preserves equality", learner_answer="x=5; add7 then divide5")
        fresh_report = self.main(fresh, [item("solve", independent)])
        self.cli("ingest", self.write(fresh_report))
        self.assertEqual(self.objective()["understanding"], "demonstrated")
        self.assertEqual(self.objective()["retention"], "unassessed")
        delayed_spec = spec(["solve"], mode="review")
        delayed = self.cli("prepare", "math", self.write(delayed_spec), day="2026-11-02")
        cold = phased(assessment(aid="cold-transfer"), before_teaching=True)
        cold.update(question="Solve 7x+4=46 using inverse operations", learner_answer="x=6")
        delayed_report = self.main(delayed, [item("solve", cold)], day="2026-11-02")
        self.cli("ingest", self.write(delayed_report), day="2026-11-02")
        self.assertEqual(self.objective()["retention"], "demonstrated")
        self.assertEqual(len(self.objective()["evidence"]), 3)
        self.assertEqual(self.assignment()["implementation"]["progress"][0]["progress"]["assistance"], progress["assistance"])
        late = self.side(report, "unknown", "late-original-help")
        self.cli("ingest", self.write(late), day="2026-11-02")
        self.assertEqual(self.objective()["retention"], "demonstrated")
        self.assertEqual(len(self.objective()["evidence"]), 3)

    def side(self, report, timing, suffix):
        return {"schema_version": 1, "report_type": "side-chat", "report_id": "side-" + suffix,
                "lesson_id": report["lesson_id"], "track_id": "math", "map_revision": 1, "content_revision": 0,
                "assignment_context": report["assignment_context"], "remaining_questions": [],
                "discussions": [{"question": "Explain the implementation task", "explanation": "Actual task-specific explanation",
                                 "source_reference": "Synthetic governing material", "objective_ids": ["solve"]}],
                "assessment_help": [{"objective_id": "solve", "question": report["objectives"][0]["assessments"][0]["question"],
                                     "help": "Actual requested explanation of this assessed task", "timing": timing}]}

    def test_side_help_in_either_report_order_qualifies_only_prior_or_unknown_help(self):
        plan = self.ready()
        for order in ("side-first", "main-first", "after-answer"):
            with self.subTest(order=order):
                prepared = self.guided(plan)
                report = self.main(prepared, [item("solve")])
                report["implementation_progress"] = self.progress()
                side = self.side(report, "after-answer" if order == "after-answer" else "unknown", order)
                if order == "side-first":
                    self.cli("ingest", self.write(side))
                    self.assertEqual(self.cli("status")["pending_lessons"]["math"], [prepared["lesson_id"]])
                self.cli("ingest", self.write(report))
                archive = self.root / "reports" / (report["report_id"] + ".json")
                original = archive.read_bytes()
                if order != "side-first":
                    self.cli("ingest", self.write(side))
                self.assertEqual(self.cli("ingest", self.write(side))["status"], "duplicate")
                self.assertEqual(archive.read_bytes(), original)
                self.assertEqual(self.assignment()["completion"], "completed")
                self.assertEqual(self.objective()["understanding"], "demonstrated" if order == "after-answer" else "needs-practice")
                latest = self.objective()["evidence"][-1]
                self.assertTrue(latest["assessments"][0]["independent"])
                if order != "after-answer":
                    self.assertEqual(latest["assistance_qualifications"][0]["source"], "side-chat")

    def test_review_repair_preserves_failures_and_fresh_success_is_relearning(self):
        plan = self.ready()
        first = self.guided(plan)
        report = self.main(first, [item("solve")])
        report["implementation_progress"] = self.progress()
        self.cli("ingest", self.write(report))
        review = spec(["solve"], mode="review")
        review["assignment"] = {"assignment_id": "solver", "plan_id": plan, "lesson_id": "inverse", "phase": "implementation"}
        prepared = self.cli("prepare", "math", self.write(review), day="2026-11-02")
        diagnostic = phased(assessment(aid="diagnostic-failure", result="fail"), phase="diagnostic", before_teaching=True)
        diagnostic.update(question="Solve 4x+1=17", learner_answer="x=3")
        practice = phased(assessment(aid="guided-practice"), phase="practice", before_teaching=False)
        practice.update(question="Use the supplied worked steps to solve 6x+2=20", learner_answer="x=3")
        fresh = phased(assessment(aid="fresh-repair"), resolves=["diagnostic-failure"])
        fresh.update(question="Solve 8x-3=37 and check by substitution", learner_answer="x=5; 8(5)-3=37")
        report = self.main(prepared, [item("solve", diagnostic)], day="2026-11-02")
        report["objectives"][0]["assessments"] = [diagnostic, practice, fresh]
        progress = self.progress()
        progress["assistance"] = [{"question": practice["question"], "help": "Requested worked steps supplied during repair",
                                   "timing": "before-answer", "objective_ids": ["solve"]}]
        report["implementation_progress"] = progress
        self.cli("ingest", self.write(report), day="2026-11-02")
        objective = self.objective()
        self.assertEqual(objective["understanding"], "demonstrated")
        self.assertEqual(objective["retention"], "needs-review")
        self.assertEqual(objective["review"]["step"], 0)
        self.assertEqual(objective["evidence"][-1]["assessments"], [diagnostic, practice, fresh])
        self.assertEqual(objective["evidence"][-1]["assistance_qualifications"][0]["assessment_id"], "guided-practice")

    def test_post_answer_help_and_content_review_preserve_original_assignment_records(self):
        plan = self.ready()
        prepared = self.guided(plan)
        observed = assessment()
        report = self.main(prepared, [item("solve", observed)])
        progress = self.progress()
        progress["assistance"] = [{"question": observed["question"], "help": "Explained a solution after the learner answered independently",
                                   "timing": "after-answer", "objective_ids": ["solve"]}]
        report["implementation_progress"] = progress
        self.cli("ingest", self.write(report))
        self.assertEqual(self.objective()["understanding"], "demonstrated")
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet/START-HERE.md"
        archive = self.root / "reports" / (report["report_id"] + ".json")
        packet_bytes, report_bytes = packet.read_bytes(), archive.read_bytes()
        concern = self.cli("record-concern", "math", self.write({"objective_ids": ["solve"], "claim": "Teaching omitted verification",
            "reasoning": "A substitution check should accompany the example", "source_reference": "Synthetic requirements"}))
        self.cli("investigate", concern["id"], self.write({"sources_examined": ["Original requirement and worked equation"],
            "reasoning": "Substitution verification should be explicit", "conclusion": "confirmed"}))
        correction = self.cli("correct", concern["id"], self.write({"base_revision": 0,
            "context": "Substitute the result into the original equation to verify both sides match.",
            "checks": [{"check": "Substitute x=4 into 4x+3=19", "result": "passed", "evidence": "4(4)+3=19"}],
            "limitations": [], "announcement": "Verification step added to teaching context"}))
        self.assertEqual(self.objective()["understanding"], "unassessed")
        self.assertEqual(self.cli("ingest", self.write(report))["status"], "duplicate")
        self.cli("review-evidence", self.write({"report_id": report["report_id"], "objective_id": "solve", "assessment_ids": [],
            "status": "retained", "correction_id": correction["id"], "reason": "Actual response already verifies equality by substitution"}))
        self.assertEqual(self.objective()["understanding"], "demonstrated")
        self.assertEqual(self.objective()["evidence"][0]["assessments"][0], observed)
        self.assertEqual(archive.read_bytes(), report_bytes)
        self.assertEqual(packet.read_bytes(), packet_bytes)
        self.cli("dispute", report["report_id"], "--reason", "Fresh evidence needed to revisit this judgment")
        self.assertEqual(self.objective()["understanding"], "unassessed")
        self.assertEqual(self.assignment()["completion"], "not-started")
        self.assertTrue(self.objective()["evidence"][0]["invalidated"])
        self.assertEqual(archive.read_bytes(), report_bytes)

    def test_unscoped_help_qualifies_only_an_exact_matching_task(self):
        plan = self.ready()
        for matched in (True, False):
            with self.subTest(exact_task_match=matched):
                prepared = self.guided(plan)
                observed = assessment()
                if not matched:
                    observed.update(question="Solve 9x+1=28 and check the result", learner_answer="x=3; 9(3)+1=28")
                report = self.main(prepared, [item("solve", observed)])
                progress = self.progress()
                progress["assistance"] = [{"question": observed["question"] if matched else "How should I name my output file?",
                    "help": "Actual requested task explanation", "timing": "unknown", "objective_ids": []}]
                report["implementation_progress"] = progress
                self.cli("ingest", self.write(report))
                self.assertEqual(self.objective()["understanding"], "needs-practice" if matched else "demonstrated")
                self.assertEqual(self.assignment()["implementation"]["progress"][-1]["progress"]["assistance"][0]["objective_ids"], [])
