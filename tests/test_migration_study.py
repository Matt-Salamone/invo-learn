"""Fresh study after activation through the installed S1 boundary."""
import json
import unittest

import test_migration_activation
import test_migration_projection
from examples.worked_example import assessment, item, make_report, map_spec, spec


class MigrationStudyJourneys(unittest.TestCase):
    setUp = test_migration_activation.ActivationJourneys.setUp
    setUp_base = test_migration_activation.ActivationJourneys.setUp_base
    write = test_migration_activation.ActivationJourneys.write
    cli = test_migration_activation.ActivationJourneys.cli
    make_assignment = test_migration_activation.ActivationJourneys.make_assignment
    plan = test_migration_activation.ActivationJourneys.plan
    future = test_migration_activation.ActivationJourneys.future
    evidence = test_migration_projection.MigrationProjectionTests.evidence

    def needs(self):
        migration = json.loads((self.root / "state.json").read_text())["migration"]
        return {**migration["legacy_study_actions"], **migration["reconciliation"]["fresh_study"]}

    def test_activated_needs_close_only_from_linked_fresh_evidence_and_reopen_on_withdrawal(self):
        self.evidence()
        proposal = self.cli("propose-map", "math", self.write(map_spec(self.material["id"], [
            ("solve", "Solve equations", "skill", "whole file", []),
            ("explain", "Explain equality", "concept", "whole file", [])])))
        self.cli("accept-map", "math", proposal["proposal_id"], "--approval", "Synthetic approval")
        self.cli("prepare", "math", self.write(spec(["solve"])))
        self.cli("migration-rehearse", self.write(self.plan()))
        checkout = self.cli("migration-checkouts", self.stage)
        waivers = [{"origin_key": s["origin_key"], "packet_id": s["packet_id"], "accept_lost_progress": True,
                    "reason": "Synthetic learner accepts unreported progress loss"} for s in checkout["sessions"].values()]
        reconciled = self.cli("migration-reconcile", self.stage, self.write({"reports": [], "waivers": waivers}))
        self.assertTrue(reconciled["eligible"])
        self.assertNotIn("Collect", reconciled["reminder"])
        self.cli("migration-project", self.stage)
        self.cli("migration-activate", self.stage, "--source", self.future())
        needs = self.needs()
        self.assertEqual(len(needs), 4)
        # Prior course mastery and imported independent labels cannot retire needs.
        self.assertTrue(all(n["status"] == "pending" for n in needs.values()))
        lesson_spec = spec(["solve", "explain"])
        lesson_spec["legacy_study_links"] = [{"study_need_id": key, "objective_ids": ["solve", "explain"],
            "reason": "Planner compared the preserved requirement with equality explanation and fresh equation application"}
            for key in needs]
        prepared = self.cli("prepare", "math", self.write(lesson_spec))
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        frozen = {p.name: p.read_bytes() for p in packet.iterdir()}
        report = make_report({"id": prepared["lesson_id"], "track_id": "math"}, "2026-10-29", [
            item("solve"), item("explain", assessment("explain-a", "explain-back", "light"), "needs-practice")], "partial-fresh")
        self.cli("ingest", self.write(report))
        self.assertTrue(all(n["status"] == "pending" and n["study_progress"]["demonstrated_objective_ids"] == ["solve"] for n in self.needs().values()))
        # A later packet freezes the same justified target scope; both fresh targets count.
        prepared2 = self.cli("prepare", "math", self.write(lesson_spec))
        report2 = make_report({"id": prepared2["lesson_id"], "track_id": "math"}, "2026-10-29", [
            item("solve"), item("explain", assessment("explain-b", "explain-back"))], "completed-fresh")
        self.cli("ingest", self.write(report2))
        self.assertTrue(all(n["status"] == "completed" for n in self.needs().values()))
        queue = self.cli("status")["work_queue"]
        self.assertFalse(any(n.get("study_need_id") in needs for n in queue))
        side = {"schema_version": 1, "report_type": "side-chat", "report_id": "late-prior-help",
                "lesson_id": prepared2["lesson_id"], "track_id": "math", "map_revision": 2, "content_revision": 0,
                "remaining_questions": [], "discussions": [{"question": "Explain equality", "explanation": "Both sides receive the same operation", "source_reference": "Synthetic governing notes", "objective_ids": ["explain"]}], "assessment_help": [{"objective_id": "explain",
                    "question": report2["objectives"][1]["assessments"][0]["question"],
                    "help": "Actual requested equality explanation before this answer", "timing": "before-answer"}]}
        self.cli("ingest", self.write(side))
        self.assertTrue(all(n["status"] == "pending" for n in self.needs().values()))
        self.cli("dispute", report2["report_id"], "--reason", "Actual assessment invalidated")
        self.assertTrue(all(n["status"] == "pending" and len(n["study_history"]) >= 3 for n in self.needs().values()))
        self.assertEqual(frozen, {p.name: p.read_bytes() for p in packet.iterdir()})

    def test_fresh_need_links_are_planner_owned_and_global_handoffs_stay_sequential(self):
        self.evidence()
        self.cli("migration-rehearse", self.write(self.plan()))
        self.cli("migration-reconcile", self.stage, self.write({"reports": [], "waivers": []}))
        self.cli("migration-project", self.stage)
        self.cli("migration-activate", self.stage, "--source", self.future())
        need = next(iter(self.needs()))
        self.cli("add-course", "other", "--title", "Synthetic second course")
        material = self.cli("add-material", "other", self.base / "notes.txt")
        proposed = self.cli("propose-map", "other", self.write(map_spec(material["id"], [
            ("solve", "Second course equation", "skill", "whole file", [])])))
        self.cli("accept-map", "other", proposed["proposal_id"], "--approval", "Synthetic approval")
        other = spec(["solve"])
        other["legacy_study_links"] = [{"study_need_id": need, "objective_ids": ["solve"], "reason": "Unjustified cross-course identity"}]
        self.assertIn("assigned course", self.cli("prepare", "other", self.write(other), ok=False)["error"])
        prepared = self.cli("prepare", "math", self.write(spec(["solve"])))
        self.assertIn("awaits report", self.cli("prepare", "other", self.write(spec(["solve"])), ok=False)["error"])
        self.cli("ingest", self.write(make_report({"id": prepared["lesson_id"], "track_id": "math"}, "2026-10-29", [item("solve")], "unlinked-math")))
        self.assertTrue(all(n["status"] == "pending" for n in self.needs().values()))
        second = self.cli("prepare", "other", self.write(spec(["solve"])))
        self.cli("ingest", self.write(make_report({"id": second["lesson_id"], "track_id": "other"}, "2026-10-29", [item("solve")], "second-course")))
        status = self.cli("status")
        self.assertEqual(status["tracks"]["other"]["objectives"]["solve"]["understanding"], "demonstrated")
        self.assertTrue(all(n["status"] == "pending" for n in self.needs().values()))
