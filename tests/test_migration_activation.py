"""Installed S1 activation/recovery with real old code and synthetic learner records."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import zipfile

from examples.worked_example import PUBLIC, item, make_report, map_spec, spec
from test_legacy import hashes
import test_migration as fixtures


class ActivationJourneys(unittest.TestCase):
    setUp_base = fixtures.MigrationRehearsalTests.setUp
    write = fixtures.MigrationRehearsalTests.write
    cli = fixtures.MigrationRehearsalTests.cli
    make_assignment = fixtures.MigrationRehearsalTests.make_assignment
    plan = fixtures.MigrationRehearsalTests.plan

    def setUp(self):
        self.setUp_base()

    def ready(self):
        prepared = self.cli("prepare", "math", self.write(spec(["solve"])))
        self.original_packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        self.cli("migration-rehearse", self.write(self.plan()))
        inventory = self.cli("migration-checkouts", self.stage)
        waivers = [{"origin_key": row["origin_key"], "packet_id": row["packet_id"], "accept_lost_progress": True,
                    "reason": "Synthetic learner accepts losing this checkout's unreported progress"}
                   for row in inventory["sessions"].values()]
        self.cli("migration-reconcile", self.stage, self.write({"reports": [], "waivers": waivers}))
        self.cli("migration-project", self.stage)

    def future(self):
        from invo_learn.install import package
        source = self.base / "current-trusted-package"
        _, version, files, _ = package(PUBLIC)
        for name, content in files.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        major, minor, patch = map(int, version.split("."))
        self.new_version = f"{major}.{minor}.{patch + 1}"
        (source / "VERSION").write_text(self.new_version + "\n", encoding="utf-8")
        return source

    def old_workspace(self):
        extracted = self.base / "frozen-public"
        with zipfile.ZipFile(PUBLIC / "tests/fixtures/invo-learn-0.7.0.zip") as archive:
            archive.extractall(extracted)
        source = extracted / "invo-learn-0.7.0"
        root = self.base / "older-private"
        result = subprocess.run([sys.executable, "-B", "-m", "invo_learn", "bootstrap", str(root), "--name", "Synthetic old learner",
                                 "--preferences", str(self.write({"auto_update": False, "auto_backup": False}))],
                                cwd=source, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return root

    def test_actual_old_copied_runner_cannot_mutate_an_inactive_rehearsal(self):
        older = self.old_workspace()
        stage = self.base / "older-stage"
        original = hashes(older)
        self.cli("migration-rehearse", self.write({"destination": str(older), "assignments": [], "stage": str(stage)}))
        before = hashes(stage / "workspace")
        attempted = subprocess.run([sys.executable, "-B", str(stage / "workspace/learn.py"), "add-course", "forbidden", "--title", "Must stay inactive"],
                                   capture_output=True, text=True)
        self.assertNotEqual(attempted.returncode, 0)
        self.assertIn("inactive", attempted.stderr.lower())
        self.assertEqual(hashes(stage / "workspace"), before)
        self.assertEqual(hashes(older), original)

    def test_activate_keeps_history_and_untracked_work_and_uses_current_installed_code(self):
        self.ready()
        old_release = hashes(self.root / ".invo-learn/releases")
        history = hashes(self.root / ".git")
        packet = hashes(self.original_packet)
        future = self.future()
        result = self.cli("migration-activate", self.stage, "--source", future)
        self.assertEqual(result["status"], "activated")
        self.assertTrue(result["activated"])
        state = json.loads((self.root / "state.json").read_text())
        self.assertEqual(state["migration"]["status"], "active")
        self.assertEqual(json.loads((self.root / ".invo-learn/active.json").read_text())["version"], self.new_version)
        self.assertEqual(hashes(self.root / ".git"), history)
        self.assertEqual((self.root / "untracked-course.txt").read_text(), "Keep course work")
        self.assertEqual(hashes(self.original_packet), packet)
        for name, checksum in old_release.items():
            self.assertEqual(hashes(self.root / ".invo-learn/releases")[name], checksum)
        status = self.cli("status")
        self.assertEqual(len(status["tracks"]["math"]["assignments"]), 1)
        self.assertEqual(status["pending_lessons"]["math"], [])
        self.cli("add-course", "other", "--title", "Another synthetic course")
        material = self.cli("add-material", "other", self.base / "notes.txt")
        proposed = self.cli("propose-map", "other", self.write(map_spec(material["id"], [("solve", "Solve equations", "skill", "whole file", [])])))
        self.cli("accept-map", "other", proposed["proposal_id"], "--approval", "Synthetic approval")
        self.cli("prepare", "math", self.write(spec(["solve"])))
        blocked = self.cli("prepare", "other", self.write(spec(["solve"])), ok=False)
        self.assertIn("awaits report", blocked["error"])
        already = self.cli("migration-activate", self.stage, "--source", future)
        self.assertEqual(already["status"], "already-active")

    def test_interruption_resumes_without_duplicate_progress_or_overwriting_new_untracked_work(self):
        self.ready()
        future = self.future()
        original_state = (self.root / "state.json").read_bytes()
        interrupted = self.cli("migration-activate", self.stage, "--source", future, "--interrupt-after", "2")
        self.assertEqual(interrupted["status"], "interrupted")
        self.assertFalse(interrupted["activated"])
        self.assertEqual((self.root / "state.json").read_bytes(), original_state)
        (self.root / "work-after-interruption.txt").write_bytes(b"Preserve new unrelated learner work\r\n")
        resumed = self.cli("migration-recover", self.stage, "--action", "resume")
        self.assertEqual(resumed["status"], "activated")
        self.assertEqual((self.root / "work-after-interruption.txt").read_bytes(), b"Preserve new unrelated learner work\r\n")
        state = json.loads((self.root / "state.json").read_text())
        self.assertEqual(len(state["tracks"]["math"]["assignments"]), 1)
        self.assertEqual(len([event for event in state["events"] if event["action"] == "migration-activated"]), 1)
        self.assertEqual(self.cli("migration-recover", self.stage, "--action", "resume")["status"], "already-active")

    def test_changed_source_blocks_cutover_without_replacing_any_newer_work(self):
        self.ready()
        future = self.future()
        (self.root / "untracked-course.txt").write_bytes(b"Newer source work must survive")
        before = hashes(self.root)
        failed = self.cli("migration-activate", self.stage, "--source", future, ok=False)
        self.assertIn("source changed", failed["error"])
        self.assertEqual(hashes(self.root), before)

    def test_postactivation_late_course_and_assignment_returns_are_historical_and_leave_new_checkout_open(self):
        self.ready()
        original_lesson = json.loads((self.original_packet / "lesson.json").read_text())
        self.cli("migration-activate", self.stage, "--source", self.future())
        current = self.cli("prepare", "math", self.write(spec(["solve"])))
        before = json.loads((self.root / "state.json").read_text())
        packet = json.loads((self.assignment / ".invo/state.json").read_text())["packets"]["packet-original"]
        legacy = {key: packet[key] for key in ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")}
        legacy.update(observations=[{"criterion": "Correct reasoning", "question": "Why balance?", "learner_response": "Preserve equality",
                                     "assistance": "none", "evidence_level": "independent"}], remaining_gaps=[], suspected_errors=[])
        course = make_report(original_lesson, "2026-10-29", [item("solve")], "late-course-return")
        for report in (legacy, course):
            path = self.write(report)
            raw = path.read_bytes()
            result = self.cli("ingest", path)
            self.assertEqual(result["status"], "historical")
            self.assertFalse(result["credit_applied"])
            self.assertEqual((self.root / result["raw_path"]).read_bytes(), raw)
            self.assertEqual(self.cli("ingest", path)["status"], "duplicate")
        after = json.loads((self.root / "state.json").read_text())
        self.assertEqual(after["reports"], before["reports"])
        self.assertEqual(after["tracks"]["math"]["objectives"], before["tracks"]["math"]["objectives"])
        self.assertEqual(self.cli("status")["pending_lessons"]["math"], [current["lesson_id"]])
        self.assertEqual(len(after["historical_reports"]), 2)

    def test_late_association_refuses_altered_original_archive_bytes_after_activation(self):
        self.ready()
        self.cli("migration-activate", self.stage, "--source", self.future())
        state = json.loads((self.root / "state.json").read_text())
        origin = next(key for key, source in state["migration"]["late_origins"].items() if source["kind"] == "assignment")
        archive = self.root / state["migration"]["late_origins"][origin]["archive"]
        (archive / "packets/original/tutor.md").write_bytes(b"Changed original instructions")
        packet = json.loads((self.assignment / ".invo/state.json").read_text())["packets"]["packet-original"]
        report = {key: packet[key] for key in ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")}
        report.update(observations=[], session_status="in-progress", remaining_gaps=[], suspected_errors=[])
        failed = self.cli("ingest", self.write(report), ok=False)
        self.assertIn("archive", failed["error"])
        self.assertFalse(json.loads((self.root / "state.json").read_text()).get("historical_reports"))

    def test_actual_older_bundle_is_upgraded_without_replacing_its_frozen_release(self):
        older = self.old_workspace()
        original_release = hashes(older / ".invo-learn/releases/0.7.0")
        stage = self.base / "older-stage"
        self.cli("migration-rehearse", self.write({"destination": str(older), "assignments": [], "stage": str(stage)}))
        self.cli("migration-reconcile", stage, self.write({"reports": []}))
        self.cli("migration-project", stage)
        result = self.cli("migration-activate", stage, "--source", self.future())
        self.assertTrue(result["activated"])
        self.assertEqual(hashes(older / ".invo-learn/releases/0.7.0"), original_release)
        self.assertEqual(json.loads((older / ".invo-learn/active.json").read_text())["version"], self.new_version)
        self.assertEqual([path.parent.name for path in (older / ".agents/skills").glob("*/SKILL.md")], ["invo-learn"])
        usable = subprocess.run([sys.executable, "-B", str(older / "learn.py"), "status"], capture_output=True, text=True)
        self.assertEqual(usable.returncode, 0, usable.stderr)
        self.assertEqual(json.loads(usable.stdout)["tracks"], {})
        self.assertTrue(self.cli("migration-status", stage)["activated"])

    def test_external_mailbox_keeps_its_binding_bytes_and_unrelated_internal_mailbox_files(self):
        external = self.base / "external-mailbox"
        shutil.copytree(self.root / "mailbox", external)
        (external / "incoming.unknown").write_bytes(b"Keep external new material\r\n")
        state = json.loads((self.root / "state.json").read_text())
        state["mailbox"] = str(external)
        (self.root / "state.json").write_text(json.dumps(state), encoding="utf-8")
        (external / ".invo-mailbox.json").write_text(json.dumps({"workspace_id": state["workspace_id"], "path": str(external)}), encoding="utf-8")
        (self.root / "mailbox/unrelated.txt").write_bytes(b"Keep unrelated former mailbox contents")
        self.ready()
        before = hashes(external)
        self.cli("migration-activate", self.stage, "--source", self.future())
        self.assertEqual(self.cli("status")["mailbox"], str(external))
        self.assertEqual(hashes(external), before)
        self.assertEqual((self.root / "mailbox/unrelated.txt").read_bytes(), b"Keep unrelated former mailbox contents")
        self.assertFalse(any(self.root.glob("migration-mailbox-*")))

    def test_activation_requires_both_explicit_reconciliation_and_current_projection(self):
        self.cli("migration-rehearse", self.write(self.plan()))
        before = hashes(self.root)
        failed = self.cli("migration-activate", self.stage, "--source", self.future(), ok=False)
        self.assertIn("projection", failed["error"])
        self.assertEqual(hashes(self.root), before)

    def test_interrupted_owned_writes_can_be_rolled_back_and_retried(self):
        self.ready()
        future = self.future()
        original = hashes(self.root)
        self.cli("migration-activate", self.stage, "--source", future, "--interrupt-after", "2")
        rolled_back = self.cli("migration-recover", self.stage, "--action", "rollback")
        self.assertEqual(rolled_back["status"], "rolled-back")
        self.assertFalse(rolled_back["activated"])
        self.assertEqual(hashes(self.root), original)
        self.assertEqual(self.cli("migration-recover", self.stage, "--action", "resume")["status"], "activated")

    def test_new_staged_returns_cannot_be_dropped_by_a_previously_prepared_activation(self):
        self.ready()
        future = self.future()
        self.cli("migration-activate", self.stage, "--source", future, "--interrupt-after", "2")
        self.cli("migration-recover", self.stage, "--action", "rollback")
        manifest = json.loads((self.stage / "migration-manifest.json").read_text())
        origin = next(key for key, source in manifest["sources"].items() if source["kind"] == "assignment")
        packet = json.loads((self.assignment / ".invo/state.json").read_text())["packets"]["packet-original"]
        returned = {key: packet[key] for key in ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")}
        returned.update(observations=[], session_status="in-progress", remaining_gaps=[], suspected_errors=[])
        self.cli("migration-reconcile", self.stage, self.write({"reports": [{"origin_key": origin, "file": str(self.write(returned))}]}))
        self.cli("migration-project", self.stage)
        before = hashes(self.root)
        refused = self.cli("migration-activate", self.stage, "--source", future, ok=False)
        self.assertIn("staged", refused["error"])
        self.assertEqual(hashes(self.root), before)

    def test_resume_refuses_changed_or_missing_unchanged_originals_and_keeps_new_files(self):
        self.ready()
        source = self.future()
        original = self.root / "untracked-course.txt"
        raw = original.read_bytes()
        self.cli("migration-activate", self.stage, "--source", source, "--interrupt-after", "2")
        new_file = self.root / "new-unrelated-during-recovery.txt"
        new_file.write_bytes(b"Preserve unrelated new work")
        original.write_bytes(b"Concurrent change must not disappear")
        failed = self.cli("migration-recover", self.stage, "--action", "resume", ok=False)
        self.assertIn("original", failed["error"])
        self.assertEqual(original.read_bytes(), b"Concurrent change must not disappear")
        original.unlink()
        failed = self.cli("migration-recover", self.stage, "--action", "resume", ok=False)
        self.assertIn("original", failed["error"])
        self.assertFalse(original.exists())
        self.assertNotEqual(json.loads((self.root / "state.json").read_text()).get("migration", {}).get("status"), "active")
        original.write_bytes(raw)
        self.assertEqual(self.cli("migration-recover", self.stage, "--action", "resume")["status"], "activated")
        self.assertEqual(new_file.read_bytes(), b"Preserve unrelated new work")


    def test_finalization_refuses_original_changed_during_the_installed_command_check(self):
        self.ready()
        source = self.future()
        original = self.root / "untracked-course.txt"
        support = self.base / "concurrent-writer"
        support.mkdir()
        # Model an external writer at a deterministic process boundary: the real
        # installed status command returns, then the original changes before commit.
        startup = ("import atexit, sys\nfrom pathlib import Path\n"
                   + "if sys.argv[-1:] == ['status'] and Path(sys.argv[0]).resolve() == Path(" + repr(str(self.root / "learn.py")) + "):\n"
                   + "    atexit.register(lambda: Path(" + repr(str(original)) + ").write_bytes(b'Concurrent original edit'))\n")
        (support / "sitecustomize.py").write_text(startup, encoding="utf-8")
        attempted = subprocess.run([sys.executable, "-B", str(self.root / "learn.py"), "--today", "2026-10-29",
                                   "migration-activate", str(self.stage), "--source", str(source)],
                                  cwd=self.base, capture_output=True, text=True,
                                  env={**os.environ, "PYTHONPATH": str(support)})
        self.assertEqual(attempted.returncode, 2, attempted.stdout + attempted.stderr)
        self.assertIn("original", json.loads(attempted.stderr)["error"])
        self.assertEqual(original.read_bytes(), b"Concurrent original edit")
        self.assertNotEqual(json.loads((self.root / "state.json").read_text())["migration"]["status"], "active")


    def test_late_side_help_qualifies_actual_reconciled_course_evidence_without_reopening_checkout(self):
        prepared = self.cli("prepare", "math", self.write(spec(["solve"])))
        lesson = json.loads((self.root / "lessons" / prepared["lesson_id"] / "packet/lesson.json").read_text())
        main = make_report(lesson, "2026-10-29", [item("solve")], "actual-course-before-cutover")
        main_path = self.write(main)
        self.cli("migration-rehearse", self.write(self.plan()))
        checkout = self.cli("migration-checkouts", self.stage)
        course = next(row for row in checkout["sessions"].values() if row["kind"] == "course")
        assignment = next(row for row in checkout["sessions"].values() if row["kind"] == "assignment")
        self.cli("migration-reconcile", self.stage, self.write({
            "reports": [{"origin_key": course["origin_key"], "file": str(main_path)}],
            "waivers": [{"origin_key": assignment["origin_key"], "packet_id": assignment["packet_id"],
                         "accept_lost_progress": True, "reason": "Actual synthetic acceptance"}]}))
        self.cli("migration-project", self.stage)
        self.cli("migration-activate", self.stage, "--source", self.future())
        current = self.cli("prepare", "math", self.write(spec(["solve"])))
        state = json.loads((self.root / "state.json").read_text())
        saved = state["reports"][main["report_id"]]
        originals = {key: (self.root / saved[key]).read_bytes() for key in ("path", "raw_path")}
        self.assertEqual(self.cli("status")["tracks"]["math"]["objectives"]["solve"]["understanding"], "demonstrated")
        for timing in ("after-answer", "unknown", "before-answer"):
            side = {"schema_version": 1, "report_type": "side-chat", "report_id": "late-side-" + timing,
                "lesson_id": lesson["id"], "track_id": "math", "map_revision": lesson["map_revision"],
                "content_revision": lesson.get("content_revision", 0), "remaining_questions": [],
                "discussions": [{"question": "Explain the assessed equation", "explanation": "Actual requested equality explanation",
                                 "source_reference": "Synthetic source", "objective_ids": ["solve"]}],
                "assessment_help": [{"objective_id": "solve", "question": main["objectives"][0]["assessments"][0]["question"],
                                     "help": "Task-specific explanation", "timing": timing}]}
            returned = self.cli("ingest", self.write(side))
            self.assertEqual(returned["status"], "supplemental-recorded")
            status = self.cli("status")
            objective = status["tracks"]["math"]["objectives"]["solve"]
            self.assertEqual(objective["understanding"], "demonstrated" if timing == "after-answer" else "needs-practice")
            self.assertEqual(objective["review"]["last_result"], "independent-pass" if timing == "after-answer" else "not-demonstrated")
            self.assertEqual(status["pending_lessons"]["math"], [current["lesson_id"]])
            self.assertEqual({key: (self.root / saved[key]).read_bytes() for key in originals}, originals)
        self.assertEqual(self.cli("ingest", main_path)["status"], "duplicate")


if __name__ == "__main__":
    unittest.main()
