"""Installed S1 verification of explicit, versioned reference-led assignment study."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from examples.worked_example import PUBLIC, item, map_spec, spec


class ReferenceJourneys(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-reference-")
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
        source.write_text("Build a solver for ax+b=c and check by substitution.", encoding="utf-8")
        self.material = self.cli("add-material", "math", source)
        mapping = map_spec(self.material["id"], [("solve", "Solve equations", "skill", "whole file", [])])
        proposal = self.cli("propose-map", "math", self.write(mapping))
        self.cli("accept-map", "math", proposal["proposal_id"], "--approval", "Synthetic approval")
        self.assignment_spec = {"title": "Equation solver", "requirements": ["Solve ax+b=c for nonzero a"],
                "deliverables": ["A solver with a substitution check"], "criteria": ["Return x=4 for 2x+3=11"],
                "material_ids": [self.material["id"]]}
        self.cli("add-assignment", "math", "solver", self.write(self.assignment_spec))
        self.artifact = self.base / "reference.py"
        self.artifact.write_text("def solve(a, b, c):\n    return (c - b) / a\n\nFULL_REFERENCE_ONLY = 'omit this unrelated section'\n", encoding="utf-8")

    def write(self, obj):
        path = self.base / ("input-" + str(len(list(self.base.glob("input-*")))) + ".json")
        path.write_text(json.dumps(obj), encoding="utf-8")
        return path

    def cli(self, *args, ok=True):
        out = subprocess.run([sys.executable, str(self.root / "learn.py"), "--today", "2026-10-29", *map(str, args)],
                             cwd=self.base, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0 if ok else 2, out.stdout + out.stderr)
        return json.loads(out.stdout if ok else out.stderr)

    def reference_spec(self, passed=True):
        check = subprocess.run([sys.executable, "-c", "import runpy; ns=runpy.run_path('reference.py'); x=ns['solve'](2,3,11); assert x==4 and 2*x+3==11; print('PASS: x=4; substitution 2*4+3=11')"],
                               cwd=self.base, capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)
        return {"provenance": "Planner-authored synthetic reference; executed the stated Python check locally",
                "artifacts": [{"id": "worked", "file": str(self.artifact), "description": "Synthetic solver source"}],
                "sections": [{"id": "solver", "artifact_id": "worked", "start_line": 1, "end_line": 2, "purpose": "Equality-preserving inverse operations"}],
                "checks": [{"requirements": self.assignment_spec["requirements"], "deliverables": self.assignment_spec["deliverables"],
                            "criteria": self.assignment_spec["criteria"], "method": "Run the synthetic Python solver and assert x=4 plus substitution",
                            "artifact_sha256": {"worked": hashlib.sha256(self.artifact.read_bytes()).hexdigest()},
                            "result": "passed" if passed else "not-run", "evidence": check.stdout if passed else "This verification has not been performed for this saved revision"}],
                "limitations": ["Only one representative nonzero-coefficient equation was executed; not an exhaustive numeric proof"]}

    def choice(self, answer="yes"):
        return self.cli("assignment-choice", "math", "solver", "--solution", answer, "--reason", "Explicit learner answer")

    def assignment(self):
        return self.cli("status")["tracks"]["math"]["assignments"]["solver"]

    def plan_spec(self):
        return {"rationale": "Teach inverse operations from verified selected reference context", "lessons": [
            {"id": "inverse", "title": "Inverse operations", "objective_ids": ["solve"], "material_ids": [self.material["id"]],
             "reference_sections": ["solver"]}]}

    def test_reference_requires_yes_and_actual_passed_checks_before_planning(self):
        error = self.cli("record-reference", "math", "solver", self.write(self.reference_spec()), ok=False)
        self.assertIn("explicit yes", error["error"])
        self.assertFalse((self.root / "tracks/math/assignments/solver/references").exists())
        self.choice()
        unchecked = self.cli("record-reference", "math", "solver", self.write(self.reference_spec(False)))
        self.assertFalse(unchecked["verified"])
        self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()), ok=False)
        verified = self.cli("record-reference", "math", "solver", self.write(self.reference_spec()))
        self.assertTrue(verified["verified"])
        self.assertEqual(verified["revision"], 2)
        self.assertEqual(len(self.assignment()["references"]), 2)

    def test_reference_led_plan_selects_excerpts_and_keeps_exact_report_lineage(self):
        self.choice()
        saved = self.cli("record-reference", "math", "solver", self.write(self.reference_spec()))
        plan = self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()))
        self.assertEqual(plan["basis"], "reference")
        self.cli("accept-assignment-plan", "math", "solver", plan["plan_id"], "--approval", "Explicit reference-led plan approval")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "solver", "plan_id": plan["plan_id"], "lesson_id": "inverse"}
        preflight = self.cli("preflight", "math", self.write(lesson))
        prepared = self.cli("prepare", "math", self.write(lesson))
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        text = (packet / "START-HERE.md").read_text()
        self.assertIn("return (c - b) / a", text)
        selected_bytes = b"".join(self.artifact.read_bytes().splitlines(keepends=True)[:2])
        self.assertIn(selected_bytes, (packet / "START-HERE.md").read_bytes())
        self.assertNotIn("FULL_REFERENCE_ONLY", text)
        self.assertFalse(any(p.name == "reference.py" for p in packet.iterdir()))
        self.assertEqual(prepared["preflight"], preflight)
        self.assertGreater(preflight["context_bytes"], len(lesson["context"].encode("utf-8")))
        report = json.loads((packet / "report-template.json").read_text())
        ref = report["assignment_context"]["reference"]
        self.assertEqual(ref["id"], saved["reference_id"])
        self.assertEqual(ref["revision"], 1)
        self.assertEqual([section["id"] for section in ref["sections"]], ["solver"])
        report.update(completed_on="2026-10-29", session_status="completed", objectives=[item("solve")])
        self.assertEqual(self.cli("ingest", self.write(report))["status"], "imported")
        self.assertEqual(self.assignment()["completion"], "not-started")
        self.assertEqual(self.cli("status")["tracks"]["math"]["objectives"]["solve"]["understanding"], "demonstrated")

    def test_corrected_reference_creates_new_plan_and_preserves_old_packet_and_return(self):
        self.choice()
        saved = self.cli("record-reference", "math", "solver", self.write(self.reference_spec()))
        first_reference = self.assignment()["references"][saved["reference_id"]]
        artifact = self.root / first_reference["artifacts"][0]["path"]
        original_reference = artifact.read_bytes()
        plan = self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()))
        self.cli("accept-assignment-plan", "math", "solver", plan["plan_id"], "--approval", "Explicit plan approval")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "solver", "plan_id": plan["plan_id"], "lesson_id": "inverse"}
        prepared = self.cli("prepare", "math", self.write(lesson))
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        issued = {p.name: p.read_bytes() for p in packet.iterdir()}
        report = json.loads((packet / "report-template.json").read_text())
        report.update(completed_on="2026-10-29", session_status="completed", objectives=[item("solve")])
        self.artifact.write_text("def solve(a, b, c):\n    return float(c - b) / a\n\nFULL_REFERENCE_ONLY = 'revision two'\n", encoding="utf-8")
        revised = self.reference_spec()
        revised.update(correction_of=saved["reference_id"], correction_reason="Normalize result type to float; re-ran the equation and substitution check")
        new_reference = self.cli("record-reference", "math", "solver", self.write(revised))
        self.assertEqual(new_reference["revision"], 2)
        self.assertEqual(artifact.read_bytes(), original_reference)
        correction = self.assignment()["references"][new_reference["reference_id"]]["correction"]
        self.assertEqual(correction["id"], saved["reference_id"])
        new_plan = self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()))
        self.assertNotEqual(plan["plan_id"], new_plan["plan_id"])
        self.cli("accept-assignment-plan", "math", "solver", new_plan["plan_id"], "--approval", "Approve plan for revised reference")
        returned = self.cli("ingest", self.write(report))
        self.assertEqual(returned["status"], "needs-review")
        self.assertEqual(self.cli("status")["tracks"]["math"]["objectives"]["solve"]["understanding"], "unassessed")
        self.cli("review-import", returned["import_id"], self.write({"solve": {"status": "retained", "reason": "Fresh equation answer is unaffected by result-type normalization"}}))
        self.assertEqual(issued, {p.name: p.read_bytes() for p in packet.iterdir()})
        self.assertEqual(json.loads((self.root / "reports" / (report["report_id"] + ".json")).read_text())["assignment_context"]["reference"]["id"], saved["reference_id"])
        lesson["assignment"]["plan_id"] = new_plan["plan_id"]
        next_packet = self.cli("prepare", "math", self.write(lesson))
        next_template = json.loads((self.root / "lessons" / next_packet["lesson_id"] / "packet/report-template.json").read_text())
        self.assertEqual(next_template["assignment_context"]["reference"]["id"], new_reference["reference_id"])

    def test_stale_check_hashes_cannot_verify_modified_reference_bytes(self):
        self.choice()
        checked = self.reference_spec()
        self.artifact.write_text("def solve(a, b, c):\n    return 999\n", encoding="utf-8")
        error = self.cli("record-reference", "math", "solver", self.write(checked), ok=False)
        self.assertIn("checked artifact", error["error"])
        self.assertFalse(self.assignment().get("references"))

    def test_damaged_reference_is_diagnosed_and_cannot_prepare_a_packet(self):
        self.choice()
        saved = self.cli("record-reference", "math", "solver", self.write(self.reference_spec()))
        plan = self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()))
        self.cli("accept-assignment-plan", "math", "solver", plan["plan_id"], "--approval", "Explicit plan approval")
        reference = self.assignment()["references"][saved["reference_id"]]
        (self.root / reference["artifacts"][0]["path"]).write_bytes(b"damaged")
        self.assertEqual(self.cli("doctor")["status"], "needs-attention")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "solver", "plan_id": plan["plan_id"], "lesson_id": "inverse"}
        error = self.cli("prepare", "math", self.write(lesson), ok=False)
        self.assertIn("checksum", error["error"])
        self.assertFalse((self.root / "lessons").exists())

    def test_explicit_new_solution_decision_preserves_prior_choices_and_references(self):
        original_choice = self.choice()["choice"]
        reference = self.cli("record-reference", "math", "solver", self.write(self.reference_spec()))
        plan = self.cli("propose-assignment-plan", "math", "solver", self.write(self.plan_spec()))
        self.cli("accept-assignment-plan", "math", "solver", plan["plan_id"], "--approval", "Explicit initial plan")
        self.cli("assignment-choice", "math", "solver", "--solution", "no", "--reason", "Changed preference without a new decision", ok=False)
        changed = self.cli("assignment-choice", "math", "solver", "--solution", "no", "--reason", "Learner explicitly requests a new no-reference planning decision", "--new-decision")
        self.assertFalse(changed["choice"]["generate"])
        assignment = self.assignment()
        self.assertEqual(assignment["solution_choice_history"], [original_choice])
        self.assertIn(reference["reference_id"], assignment["references"])
        self.assertEqual(assignment["plans"][plan["plan_id"]]["reference"]["id"], reference["reference_id"])
        no_reference = self.plan_spec()
        no_reference["lessons"][0].pop("reference_sections")
        fresh = self.cli("propose-assignment-plan", "math", "solver", self.write(no_reference))
        self.cli("accept-assignment-plan", "math", "solver", fresh["plan_id"], "--approval", "Approve explicit no-reference plan")
        lesson = spec(["solve"])
        lesson["assignment"] = {"assignment_id": "solver", "plan_id": fresh["plan_id"], "lesson_id": "inverse"}
        prepared = self.cli("prepare", "math", self.write(lesson))
        template = json.loads((self.root / "lessons" / prepared["lesson_id"] / "packet/report-template.json").read_text())
        self.assertNotIn("reference", template["assignment_context"])
        self.assertIn(reference["reference_id"], self.assignment()["references"])

    def test_verified_reference_supports_guided_and_independent_implementation(self):
        for guided, aid in ((True, "solver"), (False, "independent")):
            with self.subTest(guided=guided):
                if aid != "solver":
                    self.cli("add-assignment", "math", aid, self.write(self.assignment_spec))
                self.cli("assignment-choice", "math", aid, "--solution", "yes", "--reason", "Actual explicit reference choice")
                self.cli("record-reference", "math", aid, self.write(self.reference_spec()))
                plan = self.cli("propose-assignment-plan", "math", aid, self.write(self.plan_spec()))
                self.cli("accept-assignment-plan", "math", aid, plan["plan_id"], "--approval", "Explicit accepted reference-led plan")
                self.cli("begin-implementation", "math", aid, "--reason", "Learner reaches final implementation")
                self.cli("implementation-choice", "math", aid, "--guidance", "yes" if guided else "no", "--reason", "Actual independent guidance answer")
                progress = {"deliverables": [{"deliverable": self.assignment_spec["deliverables"][0], "status": "completed",
                                "evidence": "Synthetic learner-owned solver submitted with substitution check"}],
                            "checks": [{"criterion": self.assignment_spec["criteria"][0], "result": "passed", "method": "Synthetic actual-work check",
                                "evidence": "Synthetic return records x=4 and substitution result 11"}],
                            "assistance": [], "limitations": ["Synthetic contract fixture, not live learner verification"]}
                if guided:
                    lesson = spec(["solve"])
                    lesson["assignment"] = {"assignment_id": aid, "plan_id": plan["plan_id"], "lesson_id": "inverse", "phase": "implementation"}
                    prepared = self.cli("prepare", "math", self.write(lesson))
                    packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
                    report = json.loads((packet / "report-template.json").read_text())
                    self.assertIn("reference", report["assignment_context"])
                    self.assertTrue(report["assignment_context"]["implementation"]["guided"])
                    report.update(completed_on="2026-10-29", session_status="completed", implementation_progress=progress)
                    self.cli("ingest", self.write(report))
                else:
                    self.cli("record-implementation", "math", aid, self.write(progress))
                status = self.cli("status")
                self.assertEqual(status["tracks"]["math"]["assignments"][aid]["completion"], "completed")
                self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["understanding"], "unassessed")
                self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["retention"], "unassessed")
