"""Installed reconciliation journeys with actual-shaped synthetic returns and waivers."""
import hashlib
import json
from pathlib import Path
import unittest

from examples.worked_example import item, make_report, spec
from test_legacy import hashes
import test_migration as fixtures


class ReconciliationJourneys(unittest.TestCase):
    setUp_base = fixtures.MigrationRehearsalTests.setUp
    write = fixtures.MigrationRehearsalTests.write
    cli = fixtures.MigrationRehearsalTests.cli
    make_assignment = fixtures.MigrationRehearsalTests.make_assignment
    plan = fixtures.MigrationRehearsalTests.plan

    def setUp(self):
        self.setUp_base()
        prepared = self.cli("prepare", "math", self.write(spec(["solve"])))
        self.course_lesson = json.loads((self.root / "lessons" / prepared["lesson_id"] / "packet/lesson.json").read_text())
        self.cli("migration-rehearse", self.write(self.plan()))
        self.manifest = json.loads((self.stage / "migration-manifest.json").read_text())
        self.course_key = next(key for key, source in self.manifest["sources"].items() if source["kind"] == "course")
        self.assignment_key = next(key for key, source in self.manifest["sources"].items() if source["kind"] == "assignment")
        self.workspace = self.stage / "workspace"

    def reconcile(self, reports=(), waivers=()):
        return self.cli("migration-reconcile", self.stage,
                        self.write({"reports": list(reports), "waivers": list(waivers)}))

    def test_missing_returns_inventory_every_checkout_without_changing_source_or_stage(self):
        before = hashes(self.stage)
        result = self.cli("migration-checkouts", self.stage)
        self.assertFalse(result["eligible"])
        self.assertEqual({row["packet_id"] for row in result["sessions"].values()},
                         {self.course_lesson["id"], "packet-original"})
        self.assertTrue(result["reminder"])
        self.assertEqual(hashes(self.stage), before)
        blocked = self.reconcile()
        self.assertEqual(blocked["status"], "blocked")
        self.assertFalse(blocked["eligible"])
        self.assertEqual(len(blocked["missing"]), 2)

    def actual_reports(self):
        course = make_report(self.course_lesson, "2026-10-29", [item("solve")], "report-cutover-course")
        course["session_status"] = "in-progress"
        source_state = json.loads((self.assignment / ".invo/state.json").read_text())
        packet = source_state["packets"]["packet-original"]
        assignment = {key: packet[key] for key in ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")}
        assignment.update(observations=[{"criterion": "Correct reasoning", "question": "Why subtract both sides?",
            "learner_response": "To preserve equality", "assistance": "Tutor supplied the balance analogy before the answer",
            "evidence_level": "assisted"}], remaining_gaps=["Try a fresh independent check"], suspected_errors=[])
        result = []
        for origin, report in ((self.course_key, course), (self.assignment_key, assignment)):
            path = self.write(report)
            path.write_bytes((json.dumps(report, indent=2) + "\r\n").encode())
            result.append({"origin_key": origin, "file": str(path)})
        return result

    def test_actual_partial_returns_are_preserved_and_reconciled_without_fake_completion(self):
        sources_before = hashes(self.root), hashes(self.assignment)
        reports = self.actual_reports()
        result = self.reconcile(reports)
        self.assertTrue(result["eligible"])
        self.assertEqual(result["status"], "reconciled")
        self.assertEqual(len(result["returns"]), 2)
        for record in result["returns"].values():
            supplied = next(selection for selection in reports if selection["origin_key"] == record["origin_key"])
            self.assertEqual((self.workspace / record["path"]).read_bytes(), Path(supplied["file"]).read_bytes())
        state = json.loads((self.workspace / "state.json").read_text())
        lesson = state["lessons"][self.course_lesson["id"]]
        self.assertEqual(lesson["status"], "paused")
        self.assertEqual(lesson["session_status"], "in-progress")
        self.assertEqual(len(state["reports"]), 2)
        self.assertFalse(any(lesson["status"] == "prepared" for lesson in state["lessons"].values()))
        self.assertTrue(all(row["session_status"] == "in-progress" for row in result["sessions"].values()))
        before = hashes(self.stage)
        repeated = self.reconcile(reports)
        self.assertTrue(repeated["eligible"])
        self.assertEqual(hashes(self.stage), before)
        self.assertEqual((hashes(self.root), hashes(self.assignment)), sources_before)

    def waive_all(self):
        inventory = self.cli("migration-checkouts", self.stage)
        return [{"origin_key": row["origin_key"], "packet_id": row["packet_id"],
                 "accept_lost_progress": True,
                 "reason": "Synthetic learner explicitly accepts lost unreported progress for this checkout"}
                for row in inventory["sessions"].values()]

    def test_explicit_waiver_retires_incomplete_without_reports_or_mastery_and_plans_fresh_study(self):
        original = json.loads((self.workspace / "state.json").read_text())
        sources_before = hashes(self.root), hashes(self.assignment)
        waivers = self.waive_all()
        result = self.reconcile(waivers=waivers)
        self.assertTrue(result["eligible"])
        self.assertFalse(result["returns"])
        self.assertTrue(all(row["resolution"] == "waiver" and row["session_status"] == "in-progress"
                            for row in result["sessions"].values()))
        state = json.loads((self.workspace / "state.json").read_text())
        self.assertEqual(state["reports"], original["reports"])
        self.assertEqual(state["tracks"]["math"]["objectives"], original["tracks"]["math"]["objectives"])
        self.assertFalse(any(lesson["status"] == "prepared" for lesson in state["lessons"].values()))
        status = self.cli("--workspace", self.workspace, "status")
        self.assertEqual(len([need for need in status["work_queue"] if need["action"] == "fresh-assessment-or-relearning"]), 2)
        before = hashes(self.stage)
        self.reconcile(waivers=waivers)
        self.assertEqual(hashes(self.stage), before)
        self.assertEqual((hashes(self.root), hashes(self.assignment)), sources_before)

    def test_valid_late_returns_after_waiver_remain_historical_without_reopening_checkouts(self):
        self.reconcile(waivers=self.waive_all())
        before = json.loads((self.workspace / "state.json").read_text())
        reports = self.actual_reports()
        result = self.reconcile(reports)
        self.assertTrue(result["eligible"])
        self.assertTrue(all(row["resolution"] == "waiver" for row in result["sessions"].values()))
        self.assertTrue(all(record["outcome"] == "historical" for record in result["returns"].values()))
        after = json.loads((self.workspace / "state.json").read_text())
        self.assertEqual(after["reports"], before["reports"])
        self.assertFalse(any(lesson["status"] == "prepared" for lesson in after["lessons"].values()))

    def test_wrong_association_is_saved_and_blocks_waiver_until_actual_repair(self):
        reports = self.actual_reports()
        selection = reports[0]
        path = Path(selection["file"])
        valid = path.read_bytes()
        broken = json.loads(valid)
        broken["track_id"] = "wrong-course"
        path.write_text(json.dumps(broken), encoding="utf-8")
        rejected_raw = path.read_bytes()
        result = self.reconcile([selection], self.waive_all())
        self.assertFalse(result["eligible"])
        self.assertTrue(result["integrity_problems"])
        self.assertTrue(all(row["resolution"] is None for row in result["sessions"].values()))
        record = next(iter(result["returns"].values()))
        self.assertEqual((self.workspace / record["path"]).read_bytes(), rejected_raw)
        fixed = self.write(json.loads(valid))
        repaired = self.reconcile([{"origin_key": self.course_key, "file": str(fixed),
                                   "repair_of": hashlib.sha256(rejected_raw).hexdigest(),
                                   "repair_note": "Corrected the copied track identifier from the exact issued packet; observations unchanged"}])
        self.assertTrue(repaired["eligible"])
        self.assertFalse(repaired["integrity_problems"])
        self.assertEqual((self.workspace / record["path"]).read_bytes(), rejected_raw)

    def test_explicit_empty_partial_return_is_not_fabricated_assessment(self):
        reports = self.actual_reports()
        assignment = json.loads(Path(reports[1]["file"]).read_text())
        assignment.update(session_status="in-progress", observations=[], remaining_gaps=[])
        Path(reports[1]["file"]).write_text(json.dumps(assignment), encoding="utf-8")
        result = self.reconcile(reports)
        self.assertTrue(result["eligible"])
        saved = next(record for record in result["returns"].values() if record["kind"] == "assignment")
        self.assertEqual(saved["report"]["observations"], [])
        self.assertEqual(saved["session_status"], "in-progress")

    def test_supplement_never_reconciles_a_main_checkout_and_malformed_input_stays_exact(self):
        selection = self.actual_reports()[1]
        source = json.loads(Path(selection["file"]).read_text())
        side = {key: source[key] for key in ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")}
        side.update(report_type="side-chat", report_id="side-cutover", discussions=[{
            "question": "Why balance?", "explanation": "Maintain equality", "source_reference": "Synthetic source"}],
            remaining_questions=[], assessment_help=[])
        Path(selection["file"]).write_text(json.dumps(side), encoding="utf-8")
        result = self.reconcile([selection])
        self.assertFalse(result["eligible"])
        self.assertEqual(len(result["missing"]), 2)
        self.assertTrue(all(row["resolution"] is None for row in result["sessions"].values()))
        malformed = self.base / "actual-malformed.txt"
        malformed.write_bytes(b"{not json\r\n")
        blocked = self.reconcile([{"origin_key": self.course_key, "file": str(malformed)}])
        record = next(record for record in blocked["returns"].values() if record["status"] == "malformed")
        self.assertEqual((self.workspace / record["path"]).read_bytes(), b"{not json\r\n")
        self.assertTrue(blocked["integrity_problems"])

    def test_busy_stage_refuses_a_competing_reconciliation_without_changes(self):
        lock = self.stage / "migration.lock"
        lock.write_text("synthetic competing writer", encoding="utf-8")
        before = hashes(self.stage)
        failed = self.cli("migration-reconcile", self.stage, self.write({"reports": []}), ok=False)
        self.assertIn("busy", failed["error"])
        self.assertEqual(hashes(self.stage), before)
        lock.unlink()

    def test_canonical_validation_failure_keeps_a_verified_stage_and_saved_diagnostic(self):
        selection = self.actual_reports()[0]
        path = Path(selection["file"])
        returned = json.loads(path.read_text())
        returned["report_id"] = "report-synthetic-1"  # Already belongs to an older source lesson.
        path.write_text(json.dumps(returned), encoding="utf-8")
        result = self.reconcile([selection])
        self.assertFalse(result["eligible"])
        self.assertTrue(result["integrity_problems"])
        self.assertEqual(self.cli("migration-status", self.stage)["status"], "verified")
        self.assertEqual(len(json.loads((self.workspace / "state.json").read_text())["reports"]), 1)


if __name__ == "__main__":
    unittest.main()
