import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from invo_learn.contracts import Invalid
from invo_learn.engine import Workspace, atomic, digest, read_json, safe_mailbox
from invo_learn.install import bootstrap, package, upgrade
from examples.worked_example import PUBLIC, assessment, call, item, make_report, map_spec, run_example, spec


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-learn-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "private"
        bootstrap(PUBLIC, self.root, "Synthetic test", git=False)
        self.ws = Workspace(self.root)
        call(self.ws, "add_track", "math", "Math")
        self.source = self.base / "upload.unknown-extension"
        self.source.write_text("Inverse operations preserve equality. Solve linear equations.\n", encoding="utf-8")
        self.material = call(self.ws, "add_material", "math", self.source)
        self.mapping = map_spec(self.material["id"], [("solve", "Solve a linear equation", "skill", "whole text", [])])
        proposal = call(self.ws, "propose_map", "math", self.mapping)
        call(self.ws, "accept_map", "math", proposal["proposal_id"], "Synthetic map approval")

    def prepare(self, mode="lesson", day="2026-10-14"):
        result = call(self.ws, "prepare", "math", spec(["solve"], mode, [{"material_id": self.material["id"]}]), day)
        return self.ws.state["lessons"][result["lesson_id"]]

    def report(self, lesson, a=None, day="2026-10-14", rid="report-test"):
        return make_report(lesson, day, [item("solve", a)], rid)

    def ingest(self, r, day="2026-10-14"):
        return call(self.ws, "ingest", json.dumps(r), day)

    def objective(self):
        return self.ws.track("math")["objectives"]["solve"]

    def future(self, version="0.2.2"):
        _, _, files, _ = package(PUBLIC)
        future = self.base / ("package-" + version)
        for name, data in files.items():
            p = future / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        (future / "VERSION").write_text(version + "\n", encoding="utf-8")
        return future

    def test_unknown_extensions_and_original_bytes_preserved(self):
        self.assertEqual(self.material["status"], "usable")
        self.source.write_text("changed external upload")
        self.assertNotEqual(self.ws.path(self.material["original"]).read_bytes(), self.source.read_bytes())
        self.assertEqual(digest(self.ws.path(self.material["original"]).read_bytes()), self.material["sha256"])

    def test_pending_handoff_cannot_be_overwritten(self):
        self.prepare()
        before = (self.ws.mailbox() / "START-HERE.md").read_bytes()
        with self.assertRaisesRegex(Invalid, "awaits report"):
            self.prepare()
        self.assertEqual((self.ws.mailbox() / "START-HERE.md").read_bytes(), before)

    def test_mailbox_reuse_preserves_unexpected_report_and_durable_packet(self):
        first = self.prepare()
        r = self.report(first)
        self.ingest(r)
        (self.ws.mailbox() / "returned-report.txt").write_text(json.dumps(r), encoding="utf-8")
        (self.ws.mailbox() / "snapshot.json").write_text("preserve this collision too")
        extra = self.ws.mailbox() / "nested"
        extra.mkdir()
        (extra / "note.txt").write_text("preserve me")
        self.prepare("review", "2026-10-15")
        self.assertTrue(list((self.root / "inbox/mailbox-snapshots").rglob("returned-report.txt")))
        self.assertEqual(list((self.root / "inbox/mailbox-snapshots").rglob("note.txt"))[0].read_text(), "preserve me")
        self.assertEqual(list((self.root / "inbox/mailbox-snapshots").glob("*/contents/snapshot.json"))[0].read_text(), "preserve this collision too")
        self.assertTrue(self.ws.path(f"lessons/{first['id']}/packet/START-HERE.md").exists())
        self.assertEqual(digest(self.ws.path(self.material["original"]).read_bytes()), self.material["sha256"])

    def test_external_mailbox_and_independent_git_repository(self):
        ext = self.base / "desktop/mailbox"
        private = self.base / "other-private"
        result = bootstrap(PUBLIC, private, "Synthetic external", ext)
        self.assertEqual(result["mailbox"], str(ext))
        self.assertEqual(Workspace(private).mailbox(), ext)
        remote = subprocess.run(["git", "-C", str(private), "remote", "-v"], capture_output=True, text=True, check=True)
        self.assertEqual(remote.stdout, "")

    def test_unsafe_mailbox_roots_and_protected_folders_rejected(self):
        for candidate in (self.root, self.root.parent, Path(self.root.anchor), self.root / "tracks", self.root / "reports", self.root / "tracks/math/materials"):
            with self.subTest(path=candidate), self.assertRaises(Invalid):
                safe_mailbox(self.root, candidate)

    def test_nonempty_external_folder_not_adopted(self):
        box = self.base / "unrelated"
        box.mkdir()
        (box / "valuable.txt").write_text("valuable")
        with self.assertRaisesRegex(Invalid, "new or empty"):
            bootstrap(PUBLIC, self.base / "second-private", "Synthetic", box, git=False)
        self.assertEqual((box / "valuable.txt").read_text(), "valuable")

    def test_mailbox_marker_tamper_rejected_without_clearing(self):
        self.prepare()
        box = self.ws.mailbox()
        atomic(box / ".invo-mailbox.json", {"workspace_id": "wrong", "path": str(box)})
        with self.assertRaisesRegex(Invalid, "ownership"):
            call(self.ws, "stage", self.ws.state["active_lesson"])
        self.assertTrue((box / "START-HERE.md").exists())

    def test_symlink_preflight_preserves_target(self):
        lesson = self.prepare()
        valuable = self.base / "valuable.txt"
        valuable.write_text("valuable")
        link = self.root / "mailbox/link.txt"
        try:
            link.symlink_to(valuable)
        except OSError:
            self.skipTest("Windows symlink creation requires developer mode or privilege")
        with self.assertRaisesRegex(Invalid, "symlink"):
            call(self.ws, "stage", lesson["id"])
        link.unlink()
        self.assertEqual(valuable.read_text(), "valuable")

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_windows_junction_preflight_preserves_target_directory(self):
        lesson = self.prepare()
        valuable = self.base / "valuable-directory"
        valuable.mkdir()
        (valuable / "note.txt").write_text("valuable")
        junction = self.root / "mailbox/junction"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(valuable)], capture_output=True, text=True)
        if result.returncode:
            self.skipTest("junction creation unavailable on this filesystem")
        try:
            with self.assertRaisesRegex(Invalid, "symlink/junction"):
                call(self.ws, "stage", lesson["id"])
            self.assertEqual((valuable / "note.txt").read_text(), "valuable")
        finally:
            # Removing the junction itself is nonrecursive and leaves its target intact.
            os.rmdir(junction)

    def test_durable_packet_and_source_tamper_rejected(self):
        self.ws.path(self.material["original"]).write_text("tampered")
        with self.assertRaisesRegex(Invalid, "checksum"):
            self.prepare()
        self.assertIsNone(self.ws.state["active_lesson"])

    def test_malformed_reports_preserved_without_state_mutation(self):
        lesson = self.prepare()
        before = copy.deepcopy(self.ws.state)
        good = self.report(lesson)
        missing = copy.deepcopy(good)
        del missing["objectives"][0]["assessments"][0]["learner_answer"]
        unknown = copy.deepcopy(good)
        unknown["objectives"][0]["objective_id"] = "unknown"
        wrong_type = copy.deepcopy(good)
        wrong_type["objectives"][0]["assessments"][0]["independent"] = "true"
        for raw in ("not json", json.dumps(missing), json.dumps(unknown), json.dumps(wrong_type)):
            with self.subTest(raw=raw), self.assertRaises((Invalid, ValueError)):
                call(self.ws, "ingest", raw, "2026-10-14")
            self.assertEqual(read_json(self.root / "state.json"), before)
            self.assertTrue((self.root / "inbox/reports" / (digest(raw.encode()) + ".txt")).exists())

    def test_duplicate_json_keys_and_nonfinite_numbers_rejected(self):
        self.prepare()
        for raw in ('{"lesson_id":"a","lesson_id":"b"}', '{"grade":NaN}'):
            with self.assertRaises(Invalid):
                call(self.ws, "ingest", raw, "2026-10-14")
        self.assertFalse(self.ws.state["reports"])

    def test_fenced_duplicate_import_is_idempotent(self):
        r = self.report(self.prepare())
        self.ingest(r)
        before = copy.deepcopy(self.ws.state)
        result = call(self.ws, "ingest", "```json\n" + json.dumps(r, indent=4) + "\n```", "2026-10-14")
        self.assertEqual(result["status"], "duplicate")
        self.assertEqual(self.ws.state, before)
        self.assertEqual(len(self.objective()["evidence"]), 1)

    def test_windows_fenced_report_preserves_raw_line_endings(self):
        r = self.report(self.prepare())
        raw = "```json\r\n" + json.dumps(r, indent=2).replace("\n", "\r\n") + "\r\n```"
        self.assertEqual(call(self.ws, "ingest", raw, "2026-10-14")["status"], "imported")
        stored = self.root / "inbox/reports" / (digest(raw.encode()) + ".txt")
        self.assertEqual(stored.read_bytes().decode("utf-8"), raw)

    def test_same_id_conflict_and_second_report_for_lesson_rejected(self):
        r = self.report(self.prepare())
        self.ingest(r)
        changed = copy.deepcopy(r)
        changed["recommended_next_steps"] = ["different"]
        with self.assertRaisesRegex(Invalid, "conflict"):
            self.ingest(changed)
        changed["report_id"] = "another-report"
        with self.assertRaisesRegex(Invalid, "already has a report"):
            self.ingest(changed)
        self.assertEqual(len(Workspace(self.root).state["reports"]), 1)

    def test_hinted_work_does_not_demonstrate_independence(self):
        r = self.report(self.prepare(), assessment(assistance="heavy"))
        self.ingest(r)
        o = self.objective()
        self.assertEqual(o["coverage"], "covered")
        self.assertEqual(o["understanding"], "needs-practice")
        self.assertEqual(o["retention"], "unassessed")
        self.assertTrue(o["uncertainties"])
        self.assertEqual(o["review"]["due_on"], "2026-10-15")

    def test_light_hints_repeated_wrong_kind_invalid_empty_and_conflicting_evidence(self):
        variants = []
        for changes in ({"assistance": "light"}, {"fresh": False}, {"kind": "recall"},
                        {"valid": False}, {"learner_answer": ""}, {"independent": False},
                        {"assistance_details": "Hint supplied, despite none label"}):
            a = assessment()
            a.update(changes)
            variants.append(a)
        for index, a in enumerate(variants):
            lesson = self.prepare()
            self.ingest(self.report(lesson, a, rid=f"report-{index}"))
            self.assertNotEqual(self.objective()["understanding"], "demonstrated")
        r = self.report(self.prepare(), rid="contradictory")
        r["objectives"][0]["assessments"].append(assessment("q-fail", result="fail"))
        self.ingest(r)
        self.assertEqual(self.objective()["understanding"], "uncertain")

    def test_delayed_reviews_expand_and_hinted_review_resets(self):
        self.ingest(self.report(self.prepare()))
        self.assertEqual(self.objective()["retention"], "unassessed")
        review = self.prepare("review", "2026-10-15")
        self.ingest(self.report(review, day="2026-10-15", rid="review-1"), "2026-10-15")
        self.assertEqual(self.objective()["retention"], "demonstrated")
        self.assertEqual(self.objective()["review"]["due_on"], "2026-10-18")
        review = self.prepare("review", "2026-10-18")
        self.ingest(self.report(review, assessment(assistance="heavy"), "2026-10-18", "review-hinted"), "2026-10-18")
        self.assertEqual(self.objective()["retention"], "needs-review")
        self.assertEqual(self.objective()["review"]["due_on"], "2026-10-19")
        self.assertEqual(self.objective()["review"]["lapses"], 1)

    def test_early_review_does_not_establish_retention_or_postpone_due(self):
        self.ingest(self.report(self.prepare()))
        old = copy.deepcopy(self.objective()["review"])
        early = self.prepare("review")
        self.ingest(self.report(early, rid="review-early"))
        self.assertEqual(self.objective()["review"], old)
        self.assertEqual(self.objective()["retention"], "unassessed")

    def test_review_intervals_repeat_at_cap_and_are_adjustable(self):
        call(self.ws, "set_policy", [1, 2])
        self.ingest(self.report(self.prepare()))
        for n, day in enumerate(("2026-10-15", "2026-10-17", "2026-10-19")):
            review = self.prepare("review", day)
            self.ingest(self.report(review, day=day, rid=f"review-{n}"), day)
        self.assertEqual(self.objective()["review"]["step"], 1)
        self.assertEqual(self.objective()["review"]["due_on"], "2026-10-21")
        for invalid in ([], [0, 3], [3, 1], [1, 1], [True, 3]):
            with self.assertRaises(Invalid):
                call(self.ws, "set_policy", invalid)

    def test_dispute_withdraws_progress_and_preserves_report(self):
        r = self.report(self.prepare())
        self.ingest(r)
        call(self.ws, "dispute", r["report_id"], "Invalid question; rubric failed to capture objective")
        self.assertEqual(self.objective()["understanding"], "unassessed")
        self.assertIsNone(self.objective()["review"])
        self.assertTrue(self.objective()["evidence"][0]["invalidated"])
        self.assertTrue((self.root / "reports/report-test.json").exists())

    def test_skipped_objective_and_future_report_dates(self):
        lesson = self.prepare()
        r = self.report(lesson, day="2026-10-15")
        with self.assertRaisesRegex(Invalid, "future"):
            self.ingest(r)
        r["completed_on"] = "2026-10-14"
        r["objectives"][0].update(coverage="unassessed", judgment="uncertain", assessments=[])
        self.ingest(r)
        self.assertIsNone(self.objective()["review"])
        self.assertEqual(self.objective()["coverage"], "unassessed")

    def test_new_material_requires_map_proposal_and_stale_proposals_rejected(self):
        old_revision = self.ws.track("math")["map_revision"]
        pending = call(self.ws, "propose_map", "math", self.mapping)
        extra = self.base / "extra"
        extra.write_text("Quadratic equations")
        call(self.ws, "add_material", "math", extra)
        self.assertEqual(self.ws.track("math")["map_revision"], old_revision)
        with self.assertRaisesRegex(Invalid, "stale"):
            call(self.ws, "accept_map", "math", pending["proposal_id"], "approved")
        with self.assertRaisesRegex(Invalid, "every primary"):
            call(self.ws, "propose_map", "math", self.mapping)
        self.assertTrue(self.ws.status("2026-10-14")["tracks"]["math"]["unmapped_primary_materials"])

    def test_map_cycles_deferral_and_meaning_preservation(self):
        mapping = copy.deepcopy(self.mapping)
        mapping["objectives"][0]["prerequisites"] = ["solve"]
        with self.assertRaises(Invalid):
            call(self.ws, "propose_map", "math", mapping)
        self.ingest(self.report(self.prepare()))
        mapping = copy.deepcopy(self.mapping)
        mapping["objectives"][0]["title"] = "Different objective"
        with self.assertRaisesRegex(Invalid, "immutable"):
            call(self.ws, "propose_map", "math", mapping)
        mapping = copy.deepcopy(self.mapping)
        mapping["objectives"][0].update(scope="deferred", reason="Learner postponed this objective")
        proposed = call(self.ws, "propose_map", "math", mapping)
        call(self.ws, "accept_map", "math", proposed["proposal_id"], "Learner approved postponement")
        self.assertEqual(self.objective()["understanding"], "demonstrated")
        self.assertEqual(self.ws.status("2026-10-15")["due_reviews"], [])

    def test_preferences_inherit_live_and_track_overrides_survive(self):
        call(self.ws, "add_track", "bread", "Bread", {"teaching_style": "practice first"})
        call(self.ws, "set_preferences", None, {"teaching_style": "short explanations", "supplemental_research": True})
        self.assertEqual(self.ws.effective_preferences("math")["teaching_style"], "short explanations")
        self.assertEqual(self.ws.effective_preferences("bread")["teaching_style"], "practice first")
        self.assertTrue(self.ws.effective_preferences("bread")["supplemental_research"])
        self.assertIsNone(self.ws.effective_preferences("bread")["schedule"])

    def test_transformation_requires_scoped_single_use_permission(self):
        binary = self.base / "opaque.custom"
        binary.write_bytes(b"\x00\xff\x00\xfe")
        m = call(self.ws, "add_material", "math", binary)
        self.assertEqual(m["status"], "needs-transformation")
        converted = self.base / "conversion.txt"
        converted.write_text("A inspected local conversion output")
        with self.assertRaisesRegex(Invalid, "approval"):
            call(self.ws, "add_derived", "math", m["id"], converted, "missing", "synthetic conversion")
        approval = call(self.ws, "approve_transformation", "math", m["id"], "Local converter -> text; may lose layout", "Learner authorized local conversion")
        result = call(self.ws, "add_derived", "math", m["id"], converted, approval["id"], "Inspected output, layout omitted")
        self.assertEqual(result["status"], "usable")
        self.assertEqual(self.ws.path(m["original"]).read_bytes(), b"\x00\xff\x00\xfe")
        with self.assertRaisesRegex(Invalid, "approval"):
            call(self.ws, "add_derived", "math", m["id"], converted, approval["id"], "reuse")
        with self.assertRaisesRegex(Invalid, "approval"):
            call(self.ws, "add_derived", "math", self.material["id"], converted, approval["id"], "cross material")

    def test_supplemental_intake_is_opt_in_and_cannot_define_primary_scope(self):
        with self.assertRaisesRegex(Invalid, "disabled"):
            call(self.ws, "add_material", "math", self.source, "supplemental")
        call(self.ws, "set_preferences", "math", {"supplemental_research": True})
        extra = call(self.ws, "add_material", "math", self.source, "supplemental")
        mapping = copy.deepcopy(self.mapping)
        mapping["objectives"][0]["sources"][0]["material_id"] = extra["id"]
        with self.assertRaisesRegex(Invalid, "primary"):
            call(self.ws, "propose_map", "math", mapping)

    def test_upgrade_preserves_learning_files_preferences_and_review_state(self):
        self.ingest(self.report(self.prepare()))
        plan = self.root / "tracks/math/plan.md"
        plan.write_text("Private evolving plan")
        before = copy.deepcopy(self.ws.state)
        with self.ws.locked():
            result = upgrade(self.ws, self.future())
        self.assertEqual(result["status"], "upgraded")
        for key in ("profile", "tracks", "reports", "lessons", "review_policy", "mailbox", "active_lesson"):
            self.assertEqual(self.ws.state[key], before[key])
        self.assertEqual(plan.read_text(), "Private evolving plan")
        self.assertEqual(read_json(self.root / ".invo-learn/active.json")["version"], "0.2.2")
        self.assertTrue((Path(result["backup"]) / "state.json").exists())
        out = subprocess.run([sys.executable, str(self.root / "learn.py"), "--today", "2026-10-15", "status"], capture_output=True, text=True, check=True)
        self.assertEqual(len(json.loads(out.stdout)["due_reviews"]), 1)

    def test_upgrade_refuses_custom_skills_and_same_version_changes(self):
        future = self.future("0.2.1")
        (future / "invo_learn/__init__.py").write_text("# modified same release")
        with self.ws.locked(), self.assertRaisesRegex(Invalid, "same-version"):
            upgrade(self.ws, future)
        future = self.future()
        skill = self.root / ".agents/skills/invo-learn/SKILL.md"
        skill.write_text("private customized skill")
        with self.ws.locked(), self.assertRaisesRegex(Invalid, "skill modified"):
            upgrade(self.ws, future)
        self.assertEqual(skill.read_text(), "private customized skill")
        self.assertEqual(read_json(self.root / ".invo-learn/active.json")["version"], "0.2.1")

    def test_upgrade_rejects_modified_runtime_downgrade_and_unmanaged_skill_collision(self):
        with self.ws.locked(), self.assertRaisesRegex(Invalid, "downgrades"):
            upgrade(self.ws, self.future("0.0.9"))
        future = self.future()
        custom = future / "skills/new-skill/SKILL.md"
        custom.parent.mkdir()
        custom.write_text("new distribution skill")
        private_skill = self.root / ".agents/skills/new-skill/SKILL.md"
        private_skill.parent.mkdir()
        private_skill.write_text("private user skill")
        with self.ws.locked(), self.assertRaisesRegex(Invalid, "unmanaged"):
            upgrade(self.ws, future)
        self.assertEqual(private_skill.read_text(), "private user skill")
        runtime = self.root / ".invo-learn/releases/0.2.1/invo_learn/engine.py"
        runtime.write_text("custom runtime")
        with self.ws.locked(), self.assertRaisesRegex(Invalid, "harness modified"):
            upgrade(self.ws, future)
        self.assertEqual(read_json(self.root / ".invo-learn/active.json")["version"], "0.2.1")

    def test_caught_upgrade_activation_failure_restores_exports_and_retries(self):
        future = self.future()
        skill = future / "skills/invo-learn/SKILL.md"
        skill.write_text(skill.read_text() + "\nSynthetic new guidance.\n")
        private_skill = self.root / ".agents/skills/invo-learn/SKILL.md"
        before = private_skill.read_bytes()
        original = os.replace
        def fail_activation(src, dst):
            if Path(dst) == self.root / ".invo-learn/active.json":
                raise OSError("simulated activation failure")
            return original(src, dst)
        with self.ws.locked(), patch("invo_learn.engine.os.replace", side_effect=fail_activation), self.assertRaises(OSError):
            upgrade(self.ws, future)
        self.assertEqual(private_skill.read_bytes(), before)
        self.assertEqual(read_json(self.root / ".invo-learn/active.json")["version"], "0.2.1")
        with self.ws.locked():
            self.assertEqual(upgrade(self.ws, future)["status"], "upgraded")

    def test_incompatible_update_metadata_preserves_activation_and_records(self):
        future = self.future()
        metadata = read_json(future / "harness.json")
        metadata["state_schema"] = 2
        atomic(future / "harness.json", metadata)
        before = copy.deepcopy(self.ws.state)
        with self.ws.locked(), self.assertRaisesRegex(Invalid, "incompatible"):
            upgrade(self.ws, future)
        self.assertEqual(self.ws.state, before)
        self.assertEqual(read_json(self.root / ".invo-learn/active.json")["version"], "0.2.1")

    def test_prerequisite_override_retains_gap_without_learning_lock(self):
        mapping = copy.deepcopy(self.mapping)
        prerequisite = copy.deepcopy(mapping["objectives"][0])
        prerequisite.update(id="inverse", title="Explain equality", kind="concept")
        mapping["objectives"][0]["prerequisites"] = ["inverse"]
        mapping["objectives"].append(prerequisite)
        p = call(self.ws, "propose_map", "math", mapping)
        call(self.ws, "accept_map", "math", p["proposal_id"], "Approved prereq")
        call(self.ws, "override", "math", ["solve"], "Learner wants to proceed despite inverse gap")
        result = call(self.ws, "prepare", "math", spec(["solve"]), "2026-10-14")
        self.assertTrue(result["warnings"])
        self.assertEqual(self.ws.track("math")["objectives"]["inverse"]["understanding"], "unassessed")
        self.assertTrue(self.ws.track("math")["overrides"])

    def test_unreadable_objective_cannot_create_teaching_handoff(self):
        binary = self.base / "unknown.bin"
        binary.write_bytes(b"\xff\x00")
        m = call(self.ws, "add_material", "math", binary)
        mapping = copy.deepcopy(self.mapping)
        mapping["objectives"].append({"id": "opaque", "title": "Unknown source placeholder", "kind": "concept",
            "sources": [{"material_id": m["id"], "locator": "pending inspection"}], "prerequisites": [], "scope": "included", "reason": ""})
        p = call(self.ws, "propose_map", "math", mapping)
        call(self.ws, "accept_map", "math", p["proposal_id"], "Synthetic placeholder approved")
        with self.assertRaisesRegex(Invalid, "unreadable"):
            call(self.ws, "prepare", "math", spec(["opaque"]), "2026-10-14")

    def test_abandon_requires_reason_and_adds_no_evidence(self):
        lesson = self.prepare()
        with self.assertRaises(Invalid):
            call(self.ws, "abandon", lesson["id"], "")
        call(self.ws, "abandon", lesson["id"], "Learner chose to skip this session")
        with self.assertRaisesRegex(Invalid, "abandoned"):
            self.ingest(self.report(lesson))
        self.assertFalse(Workspace(self.root).state["reports"])
        self.assertIsNone(self.objective()["review"])
        self.prepare()

    def test_lock_and_interrupted_packet_recovery(self):
        lesson = self.prepare()
        lock = self.root / ".invo-learn/operation.lock"
        with self.ws.locked():
            with self.assertRaisesRegex(Invalid, "busy"):
                with Workspace(self.root).locked():
                    pass
        self.assertFalse(lock.exists())
        (self.ws.mailbox() / "START-HERE.md").unlink()
        call(self.ws, "stage", lesson["id"])
        self.assertTrue((self.ws.mailbox() / "START-HERE.md").exists())

    def test_public_package_cannot_be_a_private_workspace(self):
        with self.assertRaisesRegex(Invalid, "independent"):
            bootstrap(PUBLIC, PUBLIC / "synthetic-private-forbidden", "Synthetic", git=False)

    def test_atomic_state_failure_does_not_add_progress_and_retry_succeeds(self):
        r = self.report(self.prepare())
        original = os.replace
        def fail_state(src, dst):
            if Path(dst) == self.root / "state.json":
                raise OSError("simulated disk error")
            return original(src, dst)
        with patch("invo_learn.engine.os.replace", side_effect=fail_state), self.assertRaises(OSError):
            self.ingest(r)
        self.assertFalse(Workspace(self.root).state["reports"])
        self.assertEqual(self.ingest(r)["status"], "imported")
        self.assertEqual(len(self.objective()["evidence"]), 1)


class EndToEndTests(unittest.TestCase):
    def test_two_track_synthetic_worked_example(self):
        with tempfile.TemporaryDirectory(prefix="invo-learn-e2e-") as base:
            result = run_example(base)
            self.assertEqual(result["delayed_retention"], "demonstrated")
            self.assertTrue(result["mailbox_originals_packets_and_return_preserved"])
            self.assertEqual(result["synthetic_upgrade"], "0.2.2")


if __name__ == "__main__":
    unittest.main()
