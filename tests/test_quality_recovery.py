"""Black-box journeys through a separately installed, offline harness."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PUBLIC = Path(__file__).resolve().parents[1]
DAY = "2026-10-14"


class QualityRecoveryJourneys(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-quality-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "private"
        preferences = self.write({"auto_update": False, "auto_backup": False})
        result = subprocess.run([sys.executable, "-m", "invo_learn", "bootstrap", str(self.root),
                                 "--name", "Synthetic learner", "--no-git", "--preferences", str(preferences)],
                                cwd=PUBLIC, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.run_cli("add-course", "math", "--title", "Synthetic algebra")
        self.source = self.base / "lecture.txt"
        self.source.write_text("Equality is preserved by the same operation on both sides.\n"
                               "Solve 2x+3=11: subtract 3 on both sides, then divide by 2.\n"
                               + "Unrelated source discussion.\n" * 50, encoding="utf-8")
        self.material = self.run_cli("add-material", "math", self.source)
        self.mapping = self.map_spec()
        self.accept(self.mapping)

    def write(self, obj):
        path = self.base / ("input-" + str(len(list(self.base.glob("input-*")))) + ".json")
        path.write_text(json.dumps(obj), encoding="utf-8")
        return path

    def run_cli(self, *args, ok=True, day=DAY):
        result = subprocess.run([sys.executable, str(self.root / "learn.py"), "--today", day, *map(str, args)],
                                cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stdout + result.stderr)
        return json.loads(result.stdout if ok else result.stderr)

    def map_spec(self):
        mid = self.material["id"]
        return {"rationale": "Cover both synthetic sections", "source_gaps": [], "objectives": [
            {"id": "balance", "title": "Explain equality", "kind": "concept", "sources": [{"material_id": mid, "locator": "line 1"}],
             "prerequisites": [], "scope": "included", "reason": "", "success_criteria": ["Justify applying the same operation to both sides"]},
            {"id": "solve", "title": "Solve a linear equation", "kind": "skill", "sources": [{"material_id": mid, "locator": "line 2"}],
             "prerequisites": ["balance"], "scope": "included", "reason": "", "success_criteria": ["Solve a fresh equation and check by substitution"]}],
            "source_sections": [
                {"id": "equality", "material_id": mid, "locator": "line 1", "objective_ids": ["balance"], "reason": ""},
                {"id": "equations", "material_id": mid, "locator": "line 2", "objective_ids": ["solve"], "reason": ""},
                {"id": "discussion", "material_id": mid, "locator": "lines 3-52", "objective_ids": [], "reason": "Learner defers the unrelated discussion"}],
            "section_inventory": [{"material_id": mid, "complete": True, "inspection_note": "Inspected the entire synthetic text; all sections listed"}]}

    def accept(self, spec):
        proposal = self.run_cli("propose-map", "math", self.write(spec))
        return self.run_cli("accept-map", "math", proposal["proposal_id"], "--approval", "Synthetic learner approved these sections")

    def lesson_spec(self, oids=None):
        return {"objective_ids": oids or ["balance", "solve"], "mode": "lesson", "attachments": [], "supplemental_context": "",
                "context": "Equality means the same value. Applying the same inverse operation to both sides preserves it. "
                           "For 2x+3=11 subtract 3 on both sides, then divide by 2: x=4. Check 2(4)+3=11. "
                           "Use a labeled balance diagram and then a fresh equation without hints."}

    def prepare(self, spec=None, day=DAY):
        return self.run_cli("prepare", "math", self.write(spec or self.lesson_spec()), day=day)

    def report(self, prepared, rid="report-one", day=DAY):
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        result = json.loads((packet / "report-template.json").read_text())
        result.update(report_id=rid, completed_on=day)
        for item in result["objectives"]:
            oid = item["objective_id"]
            item.update(coverage="covered", judgment="demonstrated", assessments=[self.attempt(oid)])
        return result

    def attempt(self, oid, aid=None):
        return {"assessment_id": aid or "q-" + oid, "question": "Explain the equality principle" if oid == "balance" else "Solve 3x+2=14 and justify the steps",
                "learner_answer": "The same operation on both sides preserves equality" if oid == "balance" else "Subtract 2 on both sides; divide by 3. x=4; 3(4)+2=14",
                "rubric": "Preselected: correct result and justified operations", "rationale": "The actual answer meets both criteria",
                "result": "pass", "assistance": "none", "assistance_details": "", "kind": "explain-back" if oid == "balance" else "application",
                "fresh": True, "independent": True, "valid": True, "phase": "assessment", "before_teaching": False, "resolves": []}

    def status(self):
        return self.run_cli("status")

    def objectives(self):
        return self.status()["tracks"]["math"]["objectives"]

    def correction(self, oid="solve", base_revision=0):
        concern = self.run_cli("record-concern", "math", self.write({"objective_ids": [oid], "claim": "Example needs a substitution check",
            "reasoning": "Checking the result catches arithmetic mistakes", "source_reference": "Synthetic equation example"}))
        self.run_cli("investigate", concern["id"], self.write({"sources_examined": ["Original line 2", "Substitution into the equation"],
            "reasoning": "The verification step is missing from the teaching context", "conclusion": "confirmed"}))
        correction = self.run_cli("correct", concern["id"], self.write({"base_revision": base_revision,
            "context": "After solving, substitute the result into the original equation and compare both sides.",
            "checks": [{"check": "Substitute x=4 into 2x+3=11", "result": "passed", "evidence": "2(4)+3=11"}],
            "limitations": [], "announcement": "Added the missing result-verification step."}))
        return correction

    def test_verified_reduction_preflight_and_fresh_chat_packet(self):
        original = self.source.read_bytes()
        reduction_spec = {"material_id": self.material["id"], "mode": "summary", "source_locator": "lines 1-2",
            "content": "Apply the same operation to both sides. Solve 2x+3=11: x=4; check by substitution.",
            "method": "Summarized inspected usable text without the unrelated discussion",
            "assessment": {"basis": "Inspected source and byte sizes", "relevance": "Selected both lesson concepts", "uncertainty": "Chatbot token limit unknown"},
            "critical_details": [{"detail": "Equality preservation", "evidence": "same operation to both sides"}],
            "omissions": ["Unrelated discussion deferred in accepted map"], "limitations": []}
        invalid = copy.deepcopy(reduction_spec)
        invalid["critical_details"][0]["evidence"] = "absent detail"
        self.run_cli("reduce-context", "math", self.write(invalid), ok=False)
        reduced = self.run_cli("reduce-context", "math", self.write(reduction_spec))
        self.assertEqual(self.source.read_bytes(), original)
        spec = self.lesson_spec()
        spec["attachments"] = [{"material_id": self.material["id"], "derived_id": reduced["id"]}]
        spec["quality_review"] = {"assessment": reduction_spec["assessment"], "critical_details": ["equality", "worked equation"],
            "omissions": [], "limitations": [], "budget_bytes": 4096,
            "checks": {"self_contained": True, "critical_details_verified": True, "assessment_safe": True, "references_verified": True}}
        preflight = self.run_cli("preflight", "math", self.write(spec))
        self.assertTrue(preflight["content_checked"])
        self.assertLess(preflight["included"][0]["bytes"], len(original))
        broken = copy.deepcopy(spec)
        broken["quality_review"]["checks"]["self_contained"] = False
        self.run_cli("prepare", "math", self.write(broken), ok=False)
        self.assertIsNone(self.status()["active_lesson"])
        prepared = self.prepare(spec)
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        manifest = json.loads((packet / "packet-manifest.json").read_text())
        self.assertEqual(manifest["payload_bytes"], sum((packet / f["name"]).stat().st_size for f in manifest["files"]))
        for entry in manifest["files"]:
            self.assertEqual(hashlib.sha256((packet / entry["name"]).read_bytes()).hexdigest(), entry["sha256"])
        template = json.loads((packet / "report-template.json").read_text())
        self.assertIsNone(template["completed_on"])
        self.run_cli("ingest", self.write(template), ok=False)
        text = (packet / "START-HERE.md").read_text()
        for term in ("2x+3=11", "success_criteria", "report-template.json", "fresh", "critical_details"):
            self.assertIn(term.lower(), text.lower())
        report = self.report(prepared)
        self.run_cli("ingest", self.write(report))
        self.assertEqual(self.objectives()["solve"]["understanding"], "demonstrated")
        self.assertEqual(self.run_cli("doctor")["status"], "healthy")

    def test_reduction_cannot_bypass_conversion_permission_or_integrity(self):
        opaque = self.base / "opaque.bin"
        opaque.write_bytes(b"\x00\xff")
        material = self.run_cli("add-material", "math", opaque)
        reduction = {"material_id": material["id"], "mode": "summary", "source_locator": "unknown",
            "content": "Made-up content", "method": "unsupported", "assessment": {"basis": "x", "relevance": "x", "uncertainty": "x"},
            "critical_details": [{"detail": "x", "evidence": "content"}], "omissions": [], "limitations": []}
        self.assertIn("inspection", self.run_cli("reduce-context", "math", self.write(reduction), ok=False)["error"])
        durable = self.root / self.material["original"]
        durable.write_text("tampered")
        self.assertEqual(self.run_cli("doctor")["status"], "needs-attention")
        spec = self.lesson_spec()
        spec["attachments"] = [{"material_id": self.material["id"]}]
        self.assertIn("checksum", self.run_cli("preflight", "math", self.write(spec), ok=False)["error"])

    def test_content_correction_and_stale_report_preserve_unaffected_evidence(self):
        first = self.prepare()
        original_report = self.report(first)
        self.run_cli("ingest", self.write(original_report))
        pending = self.prepare()
        packet = self.root / "lessons" / pending["lesson_id"] / "packet"
        before = {p.name: p.read_bytes() for p in packet.iterdir()}
        correction = self.correction()
        self.assertEqual(self.objectives()["balance"]["understanding"], "demonstrated")
        self.assertEqual(self.objectives()["solve"]["understanding"], "unassessed")
        self.run_cli("restage", pending["lesson_id"], ok=False)
        self.run_cli("review-evidence", self.write({"report_id": "report-one", "objective_id": "solve", "assessment_ids": [],
            "status": "retained", "reason": "The answer independently includes substitution", "correction_id": correction["id"]}))
        self.assertEqual(self.objectives()["solve"]["understanding"], "demonstrated")
        stale = self.report(pending, "report-stale")
        imported = self.run_cli("ingest", self.write(stale))
        self.assertEqual(imported["status"], "needs-review")
        self.assertEqual(len(self.objectives()["balance"]["evidence"]), 1)
        choices = {"balance": {"status": "retained", "reason": "Equality principle unchanged"},
                   "solve": {"status": "withdrawn", "reason": "Old teaching omitted verification"}}
        self.run_cli("review-import", imported["import_id"], self.write({"balance": choices["balance"]}), ok=False)
        # A failed relevance decision remains reviewable, not a rejected raw report.
        self.run_cli("review-import", imported["import_id"], self.write(choices))
        self.assertEqual(len(self.objectives()["balance"]["evidence"]), 2)
        self.assertEqual(self.run_cli("ingest", self.write(stale))["status"], "duplicate")
        self.assertEqual({p.name: p.read_bytes() for p in packet.iterdir()}, before)
        next_packet = self.prepare()
        self.assertIn("substitute the result", (self.root / "lessons" / next_packet["lesson_id"] / "packet/START-HERE.md").read_text())
        self.assertEqual(json.loads((self.root / "reports/report-one.json").read_text()), original_report)

    def test_correction_includes_prerequisite_dependents_and_requires_investigation(self):
        self.prepare()
        correction = self.correction("balance")
        self.assertEqual(set(correction["objective_ids"]), {"balance", "solve"})
        self.assertTrue(any(q["action"] == "review-packet-context" for q in self.status()["work_queue"]))
        self.run_cli("correct", correction["concern_id"], self.write({"base_revision": 0, "context": "change",
            "checks": [], "limitations": [], "announcement": "invalid"}), ok=False)

    def test_multiple_correction_reviews_do_not_clear_each_other(self):
        self.run_cli("ingest", self.write(self.report(self.prepare())))
        pending = self.prepare()
        first = self.correction()
        second = self.correction(base_revision=1)
        for correction in (first, second):
            self.run_cli("review-evidence", self.write({"report_id": "report-one", "objective_id": "solve", "assessment_ids": [],
                "status": "retained", "reason": "Verified the actual independent work remains valid", "correction_id": correction["id"]}))
            self.run_cli("review-context", pending["lesson_id"], self.write({"correction_id": correction["id"],
                "status": "safe-to-resume", "reason": "The packet already contains the required substitution check"}))
            if correction is first:
                self.assertEqual(self.objectives()["solve"]["understanding"], "unassessed")
                self.run_cli("restage", pending["lesson_id"], ok=False)
        self.assertEqual(self.objectives()["solve"]["understanding"], "demonstrated")
        self.run_cli("restage", pending["lesson_id"])
        self.assertEqual(self.status()["tracks"]["math"]["content_revision"], 2)

    def test_selective_assessment_dispositions_preserve_originals_and_cold_rules(self):
        prepared = self.prepare()
        report = self.report(prepared)
        failed = self.attempt("solve", "bad-question")
        failed.update(result="fail", learner_answer="Question was ambiguous")
        report["objectives"][1]["assessments"].append(failed)
        self.run_cli("ingest", self.write(report))
        self.assertEqual(self.objectives()["solve"]["understanding"], "uncertain")
        decision = {"report_id": "report-one", "objective_id": "solve", "assessment_ids": ["bad-question"],
                    "status": "withdrawn", "reason": "Confirmed ambiguous item; retain the other independent answer"}
        self.run_cli("review-evidence", self.write(decision))
        self.assertEqual(self.objectives()["solve"]["understanding"], "demonstrated")
        self.assertEqual(self.objectives()["balance"]["understanding"], "demonstrated")
        self.assertEqual(json.loads((self.root / "reports/report-one.json").read_text()), report)
        decision["status"] = "pending"
        self.run_cli("review-evidence", self.write(decision))
        self.assertEqual(self.objectives()["solve"]["understanding"], "unassessed")
        decision["status"] = "retained"
        self.run_cli("review-evidence", self.write(decision))
        self.assertEqual(self.objectives()["solve"]["understanding"], "uncertain")

    def test_import_repair_ledger_and_exact_duplicate_are_idempotent(self):
        prepared = self.prepare()
        valid = json.dumps(self.report(prepared))
        raw = valid + ","
        path = self.base / "pasted.txt"
        path.write_bytes(raw.encode())
        self.run_cli("ingest", path, ok=False)
        iid = hashlib.sha256(raw.encode()).hexdigest()
        self.assertEqual(self.status()["next_action"]["action"], "repair-report")
        path.write_bytes(valid.encode())
        result = self.run_cli("ingest", path, "--repair-of", iid, "--repair-note", "Removed one trailing comma; all evidence unchanged")
        self.assertEqual(result["status"], "imported")
        self.assertEqual((self.root / "inbox/reports" / (iid + ".txt")).read_bytes(), raw.encode())
        self.assertFalse(any(q["action"] == "repair-report" for q in self.status()["work_queue"]))
        ledger = self.root / "inbox/imports" / (result["import_id"] + ".json")
        before = ledger.read_bytes()
        self.assertEqual(self.run_cli("ingest", path)["status"], "duplicate")
        self.assertEqual(ledger.read_bytes(), before)
        self.assertEqual(len(self.objectives()["solve"]["evidence"]), 1)

    def test_dispositions_cannot_turn_taught_review_into_cold_retention(self):
        self.run_cli("ingest", self.write(self.report(self.prepare())))
        spec = self.lesson_spec(["solve"])
        spec["mode"] = "review"
        prepared = self.prepare(spec, day="2026-10-15")
        report = self.report(prepared, "review-taught", day="2026-10-15")
        practice = self.attempt("solve", "guided")
        practice.update(phase="practice", assistance="heavy", assistance_details="Tutor re-explained the method", independent=False)
        report["objectives"][0]["assessments"].insert(0, practice)
        self.run_cli("ingest", self.write(report), day="2026-10-15")
        self.run_cli("review-evidence", self.write({"report_id": "review-taught", "objective_id": "solve", "assessment_ids": ["guided"],
            "status": "withdrawn", "reason": "Practice item not a valid assessment"}), day="2026-10-15")
        objective = self.objectives()["solve"]
        self.assertEqual(objective["understanding"], "demonstrated")
        self.assertEqual(objective["retention"], "needs-review")
        self.assertEqual(objective["review"]["step"], 0)

    def test_doctor_surfaces_corrupt_audit_and_recorded_failures_without_network(self):
        imported = self.run_cli("ingest", self.write(self.report(self.prepare())))
        ledger = self.root / "inbox/imports" / (imported["import_id"] + ".json")
        ledger.write_text("not json")
        (self.root / ".invo-learn/last-backup.json").write_text(json.dumps({"status": "backup-failed", "reason": "Synthetic disconnected remote"}))
        doctor = self.run_cli("doctor")
        self.assertEqual(doctor["status"], "needs-attention")
        self.assertTrue(any(q["action"] == "inspect-import-audit" for q in doctor["work_queue"]))
        self.assertTrue(any(q["action"] == "retry-backup" for q in self.status()["work_queue"]))
        (self.root / ".invo-learn/last-update.json").write_text("broken update outcome")
        self.assertTrue(self.run_cli("doctor")["last_operations"]["update"]["record_error"])

    def test_raw_report_integrity_is_checked_on_replay_and_diagnosis(self):
        report = self.report(self.prepare())
        imported = self.run_cli("ingest", self.write(report))
        raw = self.root / "inbox/reports" / (imported["import_id"] + ".txt")
        raw.write_text("damaged archived paste")
        self.assertIn("checksum", self.run_cli("ingest", self.write(report), ok=False)["error"])
        self.assertEqual(self.run_cli("doctor")["status"], "needs-attention")
        self.assertEqual(len(self.objectives()["solve"]["evidence"]), 1)

    def test_objective_gaps_resolve_only_with_relevant_independent_evidence(self):
        prepared = self.prepare()
        report = self.report(prepared)
        report["misconceptions"] = ["Legacy report-wide note with unknown objective association"]
        item = report["objectives"][0]
        item["assessments"][0].update(result="fail", learner_answer="Only change the left side")
        item["judgment"] = "needs-practice"
        item["gaps"] = [{"id": "gap-equality", "kind": "misconception", "description": "Changes one side only", "assessment_ids": ["q-balance"]}]
        self.run_cli("ingest", self.write(report))
        objectives = self.objectives()
        self.assertEqual(objectives["balance"]["gaps"]["gap-equality"]["status"], "open")
        self.assertFalse(objectives["solve"]["gaps"])
        self.assertFalse(any("Legacy report-wide" in x for x in objectives["solve"]["uncertainties"]))
        self.assertTrue(self.status()["tracks"]["math"]["unscoped_notes"])
        repair_packet = self.prepare()
        repair = self.report(repair_packet, "report-repair")
        repair["objectives"][0]["resolved_gaps"] = [{"gap_id": "gap-equality", "assessment_id": "q-balance", "rationale": "New explanation correctly justifies both sides"}]
        hinted = copy.deepcopy(repair)
        hinted["objectives"][0]["assessments"][0].update(assistance="light", assistance_details="Tutor named the rule", independent=False)
        self.run_cli("ingest", self.write(hinted), ok=False)
        self.run_cli("ingest", self.write(repair))
        self.assertEqual(self.objectives()["balance"]["gaps"]["gap-equality"]["status"], "resolved")
        self.run_cli("review-evidence", self.write({"report_id": "report-repair", "objective_id": "balance", "assessment_ids": ["q-balance"],
            "status": "withdrawn", "reason": "Later investigation finds the assessment invalid"}))
        self.assertEqual(self.objectives()["balance"]["gaps"]["gap-equality"]["status"], "open")

    def test_section_accounting_and_evidenced_criteria_cannot_silently_change(self):
        invalid = copy.deepcopy(self.mapping)
        invalid["source_sections"][2]["reason"] = ""
        self.run_cli("propose-map", "math", self.write(invalid), ok=False)
        invalid = copy.deepcopy(self.mapping)
        invalid["section_inventory"] = []
        self.run_cli("propose-map", "math", self.write(invalid), ok=False)
        self.run_cli("ingest", self.write(self.report(self.prepare())))
        invalid = copy.deepcopy(self.mapping)
        invalid["objectives"][0]["success_criteria"] = ["Different criterion"]
        self.run_cli("propose-map", "math", self.write(invalid), ok=False)
        self.accept(self.mapping)
        self.assertEqual(self.objectives()["solve"]["understanding"], "demonstrated")
        coverage = (self.root / "tracks/math/coverage.md").read_text()
        self.assertIn("unmapped: Learner defers", coverage)

    def test_plan_changes_and_optional_pacing_survive_new_processes(self):
        routine = {"kind": "routine", "reason": "Learner needs another representation", "objective_ids": ["balance"], "changes": "Add one balance-diagram exercise"}
        self.assertEqual(self.run_cli("plan-decision", "math", self.write(routine))["status"], "applied")
        substantial = {**routine, "kind": "substantial", "changes": "Expand practice into four sessions", "minutes": 60, "available_minutes": 30,
                       "preferred_lesson_minutes": 15, "deadline": "2026-10-20"}
        proposal = self.run_cli("plan-decision", "math", self.write(substantial))
        self.assertEqual(proposal["status"], "pending")
        self.assertTrue(proposal["pacing_warning"])
        changed = {**substantial, "proposal_id": proposal["id"], "approval": "Learner approved", "minutes": 120}
        self.run_cli("plan-decision", "math", self.write(changed), ok=False)
        approved = {**substantial, "proposal_id": proposal["id"], "approval": "Learner chose to extend available study time"}
        self.assertEqual(self.run_cli("plan-decision", "math", self.write(approved))["status"], "applied")
        self.assertFalse(any(q["action"] == "review-plan" for q in self.status()["work_queue"]))
        self.assertTrue((self.root / "tracks/math/plan-decisions.json").exists())

    def test_replacement_preserves_old_packet_and_late_report_needs_review(self):
        old = self.prepare()
        path = self.root / "lessons" / old["lesson_id"] / "packet/START-HERE.md"
        original = path.read_bytes()
        self.run_cli("add-course", "other", "--title", "Other synthetic course")
        material = self.run_cli("add-material", "other", self.source)
        mapping = {"rationale": "Independent course", "source_gaps": [], "objectives": [{"id": "other-objective", "title": "Other objective", "kind": "concept",
            "sources": [{"material_id": material["id"], "locator": "line 1"}], "prerequisites": [], "scope": "included", "reason": ""}]}
        proposed = self.run_cli("propose-map", "other", self.write(mapping))
        self.run_cli("accept-map", "other", proposed["proposal_id"], "--approval", "Synthetic other-course approval")
        other = self.run_cli("prepare", "other", self.write(self.lesson_spec(["other-objective"])))
        other_packet = self.root / "lessons" / other["lesson_id"] / "packet/START-HERE.md"
        other_original = other_packet.read_bytes()
        queued = {q["lesson_id"] for q in self.status()["work_queue"] if q["action"] == "return-report"}
        self.assertEqual(queued, {old["lesson_id"], other["lesson_id"]})
        bad = self.lesson_spec()
        bad["objective_ids"] = ["missing"]
        self.run_cli("replace", old["lesson_id"], self.write(bad), "--reason", "Learner requests replacement", ok=False)
        self.assertEqual(self.status()["active_lesson"], other["lesson_id"])
        replacement = self.run_cli("replace", old["lesson_id"], self.write(self.lesson_spec()), "--reason", "Learner explicitly requests a shorter packet")
        self.assertEqual(path.read_bytes(), original)
        late = self.run_cli("ingest", self.write(self.report(old)))
        self.assertEqual(late["status"], "needs-review")
        choices = {oid: {"status": "retained", "reason": "Question and objective still applicable"} for oid in ("balance", "solve")}
        self.run_cli("review-import", late["import_id"], self.write(choices))
        self.assertEqual(self.status()["active_lesson"], replacement["lesson_id"])
        self.assertEqual(self.status()["next_action"]["action"], "return-report")
        self.assertEqual(self.status()["pending_lessons"]["other"], [other["lesson_id"]])
        self.assertEqual(other_packet.read_bytes(), other_original)

    def test_suspected_report_errors_do_not_become_unverified_corrections(self):
        report = self.report(self.prepare())
        report["suspected_errors"] = [{"objective_ids": ["solve"], "claim": "Possible sign issue", "reasoning": "Tutor suspects a missing minus sign", "source_reference": "Worked example"}]
        self.run_cli("ingest", self.write(report))
        status = self.status()
        self.assertEqual(len(status["concerns"]), 1)
        self.assertFalse(status["corrections"])
        self.run_cli("ingest", self.write(report))
        self.assertEqual(len(self.status()["concerns"]), 1)

    def test_legacy_v1_maps_and_reports_remain_usable(self):
        # A new track uses exactly the old v1 shapes, with no new optional fields.
        self.run_cli("add-course", "legacy", "--title", "Legacy synthetic course")
        material = self.run_cli("add-material", "legacy", self.source)
        mapping = {"rationale": "Legacy map", "source_gaps": [], "objectives": [{"id": "old", "title": "Old objective", "kind": "skill",
            "sources": [{"material_id": material["id"], "locator": "whole source"}], "prerequisites": [], "scope": "included", "reason": ""}]}
        proposal = self.run_cli("propose-map", "legacy", self.write(mapping))
        self.run_cli("accept-map", "legacy", proposal["proposal_id"], "--approval", "Legacy approval")
        spec = self.lesson_spec(["old"])
        prepared = self.run_cli("prepare", "legacy", self.write(spec))
        attempt = self.attempt("solve")
        for key in ("phase", "before_teaching", "resolves"):
            attempt.pop(key)
        report = {"schema_version": 1, "report_id": "old-report", "lesson_id": prepared["lesson_id"], "track_id": "legacy", "completed_on": DAY,
                  "objectives": [{"objective_id": "old", "coverage": "covered", "judgment": "demonstrated", "assessments": [attempt]}],
                  "misconceptions": [], "prerequisite_gaps": [], "recommended_next_steps": []}
        self.run_cli("ingest", self.write(report))
        self.assertEqual(self.status()["tracks"]["legacy"]["objectives"]["old"]["understanding"], "demonstrated")

    def test_setup_rejects_enclosing_git_directories_and_worktree_markers(self):
        for marker_type in ("directory", "worktree-file", "learner-state"):
            parent = self.base / marker_type
            parent.mkdir()
            marker = parent / ("state.json" if marker_type == "learner-state" else ".git")
            if marker_type == "directory":
                marker.mkdir()
            else:
                marker.write_text("{}" if marker_type == "learner-state" else "gitdir: elsewhere")
            target = parent / "empty-child"
            result = subprocess.run([sys.executable, "-m", "invo_learn", "bootstrap", str(target), "--name", "Synthetic", "--no-git"],
                                    cwd=PUBLIC, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertFalse(target.exists())
        target = self.base / "git-environment-override"
        result = subprocess.run([sys.executable, "-m", "invo_learn", "bootstrap", str(target), "--name", "Synthetic", "--no-git"],
                                cwd=PUBLIC, capture_output=True, text=True, env={**os.environ, "GIT_WORK_TREE": str(PUBLIC)})
        self.assertEqual(result.returncode, 2)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
