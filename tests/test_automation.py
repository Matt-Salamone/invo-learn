"""Synthetic workspaces only; no live network, credentials or learner data."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from examples.worked_example import PUBLIC, call, item, make_report, map_spec, spec
from invo_learn import backup as backups
from invo_learn.cli import execute, parser
from invo_learn.contracts import Invalid, preferences
from invo_learn.engine import DEFAULTS, Workspace, atomic, read_json
from invo_learn.install import bootstrap, package, upgrade
from invo_learn.updates import study_update


class AutomationTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory(prefix="invo-learn-automation-")
        self.addCleanup(scratch.cleanup)
        self.base = Path(scratch.name).resolve()
        self.root = self.base / "private"
        bootstrap(PUBLIC, self.root, "Synthetic", git=True)
        self.ws = Workspace(self.root)
        call(self.ws, "add_track", "math", "Synthetic math")
        source = self.base / "source.md"
        source.write_text("Inverse operations preserve equality.", encoding="utf-8")
        m = call(self.ws, "add_material", "math", source)
        p = call(self.ws, "propose_map", "math", map_spec(m["id"], [("solve", "Solve equations", "skill", "whole text", [])]))
        call(self.ws, "accept_map", "math", p["proposal_id"], "Synthetic approval")
        self.version = read_json(self.root / ".invo-learn/active.json")["version"]
        major, minor, patch_version = map(int, self.version.split("."))
        self.new_version = f"{major}.{minor}.{patch_version + 1}"

    def future(self):
        _, _, files, _ = package(PUBLIC)
        source = self.base / "future"
        for name, data in files.items():
            p = source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        (source / "VERSION").write_text(self.new_version, encoding="utf-8")
        with (source / "invo_learn/templates/chatbot.md").open("a", encoding="utf-8") as out:
            out.write("\nSYNTHETIC NEW ACTIVE TEMPLATE\n")
        return source

    def cli(self, *args):
        return execute(parser().parse_args(["--workspace", str(self.root), "--today", "2026-10-18", *args]))

    def test_missing_defaults_and_explicit_preferences_survive_upgrade(self):
        prefs = self.ws.state["profile"]["preferences"]
        prefs.pop("auto_update")
        prefs.pop("auto_backup")
        prefs["teaching_style"] = "brief explanation, attempt, feedback"
        atomic(self.ws.state_path, self.ws.state)
        before = copy.deepcopy(prefs)
        with self.ws.locked():
            upgrade(self.ws, self.future())
        self.assertEqual(self.ws.state["profile"]["preferences"], before)
        effective = self.ws.effective_preferences("math")
        self.assertTrue(effective["auto_update"])
        self.assertTrue(effective["auto_backup"])
        self.assertEqual(effective["teaching_style"], before["teaching_style"])
        call(self.ws, "set_preferences", None, {"auto_update": False, "auto_backup": False})
        self.assertFalse(self.ws.effective_preferences("math")["auto_update"])
        with patch("invo_learn.updates.check_updates") as check:
            self.assertEqual(study_update(self.ws, "math")["status"], "disabled")
        check.assert_not_called()
        self.assertEqual(backups.backup(self.ws, [], "ignored", "math")["status"], "disabled")
        call(self.ws, "set_preferences", "math", {"auto_update": True})
        self.assertTrue(self.ws.effective_preferences("math")["auto_update"])
        for key in ("auto_update", "auto_backup"):
            with self.assertRaises(Invalid):
                preferences({key: "false"})

    def test_new_default_packet_has_depth_and_keeps_adaptive_evidence_rules(self):
        self.assertIn("comprehensive", DEFAULTS["teaching_style"])
        lesson = call(self.ws, "prepare", "math", spec(["solve"]), "2026-10-18")
        text = (self.ws.mailbox() / "START-HERE.md").read_text(encoding="utf-8")
        for fragment in ("causal reasoning", "worked examples", "BEFORE practice", "one manageable question",
                         "fade support", "static", "fresh", "not time remaining or mastery"):
            self.assertIn(fragment, text)
        self.assertEqual(self.ws.state["lessons"][lesson["lesson_id"]]["preferences"]["teaching_style"], DEFAULTS["teaching_style"])

    def test_explicit_global_and_track_opt_outs_survive_upgrade(self):
        call(self.ws, "set_preferences", None, {"auto_update": False, "auto_backup": False, "teaching_style": "Concise"})
        call(self.ws, "set_preferences", "math", {"teaching_style": "Practice first", "auto_backup": False})
        before = copy.deepcopy(self.ws.state)
        with self.ws.locked():
            upgrade(self.ws, self.future())
        self.assertEqual(self.ws.state["profile"], before["profile"])
        self.assertEqual(self.ws.state["tracks"], before["tracks"])
        self.assertFalse(self.ws.effective_preferences("math")["auto_update"])
        self.assertFalse(self.ws.effective_preferences("math")["auto_backup"])
        self.assertEqual(self.ws.effective_preferences("math")["teaching_style"], "Practice first")

    def downloaded_update(self, future):
        original = subprocess.run
        def run(command, **kwargs):
            if command[:2] == ["git", "clone"]:
                self.assertEqual(command[-2], "https://github.com/Matt-Salamone/invo-learn.git")
                shutil.copytree(future, Path(command[-1]))
                return subprocess.CompletedProcess(command, 0, "", "")
            return original(command, **kwargs)
        return patch("invo_learn.updates.subprocess.run", side_effect=run)

    def test_prepare_activates_update_and_uses_new_interpreter_template(self):
        future = self.future()
        lesson_spec = self.base / "spec.json"
        atomic(lesson_spec, spec(["solve"]))
        with patch("invo_learn.updates.check_updates", return_value={"status": "available", "latest_version": self.new_version}), self.downloaded_update(future):
            result = self.cli("prepare", "math", str(lesson_spec))
        self.assertEqual(result["update"]["status"], "upgraded")
        self.assertEqual(read_json(self.root / ".invo-learn/active.json")["version"], self.new_version)
        self.assertIn("SYNTHETIC NEW ACTIVE TEMPLATE", (self.ws.mailbox() / "START-HERE.md").read_text(encoding="utf-8"))

    def test_migration_requirement_continues_without_false_current_or_lost_records(self):
        future = self.future()
        metadata = read_json(future / "harness.json")
        metadata["state_schema"] = 2
        atomic(future / "harness.json", metadata)
        before = self.ws.state_path.read_bytes()
        with patch("invo_learn.updates.check_updates", return_value={"status": "available", "latest_version": self.new_version}), self.downloaded_update(future):
            result = study_update(self.ws, "math")
        self.assertEqual(result["status"], "migration-required")
        self.assertEqual(self.ws.state_path.read_bytes(), before)
        self.assertEqual(read_json(self.root / ".invo-learn/active.json")["version"], self.version)
        lesson_spec = self.base / "spec.json"
        atomic(lesson_spec, spec(["solve"]))
        with patch("invo_learn.cli.study_update", return_value=result):
            prepared = self.cli("prepare", "math", str(lesson_spec))
        self.assertEqual(prepared["update"]["status"], "migration-required")
        self.assertTrue((self.root / "lessons" / prepared["lesson_id"] / "packet/START-HERE.md").exists())

    def test_customization_and_download_version_race_are_not_bypassed(self):
        future = self.future()
        skill = self.root / ".agents/skills/invo-learn/SKILL.md"
        skill.write_text("Synthetic customization", encoding="utf-8")
        for announced in (self.new_version, "99.0.0"):
            with self.subTest(announced=announced), patch("invo_learn.updates.check_updates", return_value={"status": "available", "latest_version": announced}), self.downloaded_update(future):
                self.assertEqual(study_update(self.ws, "math")["status"], "failed")
            self.assertEqual(skill.read_text(encoding="utf-8"), "Synthetic customization")
            self.assertEqual(read_json(self.root / ".invo-learn/active.json")["version"], self.version)

    def test_pending_report_defers_update_and_restage_keeps_old_packet(self):
        prepared = call(self.ws, "prepare", "math", spec(["solve"]), "2026-10-18")
        lid = prepared["lesson_id"]
        before = (self.ws.mailbox() / "START-HERE.md").read_bytes()
        with patch("invo_learn.updates.check_updates") as check:
            self.assertEqual(study_update(self.ws, "math")["status"], "deferred")
        check.assert_not_called()
        # Simulate interrupted mailbox copying. The durable archive is unchanged.
        (self.ws.mailbox() / "START-HERE.md").write_text("partial staging", encoding="utf-8")
        call(self.ws, "stage", lid)
        self.assertEqual((self.ws.mailbox() / "START-HERE.md").read_bytes(), before)
        raw = json.dumps(make_report(self.ws.state["lessons"][lid], "2026-10-18", [item("solve")]))
        call(self.ws, "ingest", raw, "2026-10-18")
        future = self.future()
        with patch("invo_learn.updates.check_updates", return_value={"status": "available", "latest_version": self.new_version}), self.downloaded_update(future):
            self.assertEqual(study_update(self.ws, "math")["status"], "upgraded")
        self.assertEqual((self.root / "lessons" / lid / "packet/START-HERE.md").read_bytes(), before)
        fresh_spec = self.base / "spec.json"
        atomic(fresh_spec, spec(["solve"], "review"))
        # The active runner must load the installed release, not this test's modules.
        prepared = subprocess.run([sys.executable, str(self.root / "learn.py"),
                                   "--today", "2026-10-18", "prepare", "math", str(fresh_spec), "--skip-update-check"],
                                  capture_output=True, text=True, check=True)
        self.assertNotEqual(json.loads(prepared.stdout)["lesson_id"], lid)
        self.assertIn("SYNTHETIC NEW ACTIVE TEMPLATE", (self.ws.mailbox() / "START-HERE.md").read_text(encoding="utf-8"))

    def test_pending_handoff_defers_other_course_update_and_preserves_archive(self):
        prepared = call(self.ws, "prepare", "math", spec(["solve"]), "2026-10-18")
        lid = prepared["lesson_id"]
        before_state = copy.deepcopy(self.ws.state)
        packet = self.root / "lessons" / lid / "packet"
        before_packet = {p.name: p.read_bytes() for p in packet.iterdir()}
        call(self.ws, "add_track", "science", "Science")
        with patch("invo_learn.updates.check_updates") as check:
            self.assertEqual(study_update(self.ws, "science")["status"], "deferred")
        check.assert_not_called()
        self.assertEqual(self.ws.state["lessons"][lid], before_state["lessons"][lid])
        self.assertEqual({p.name: p.read_bytes() for p in packet.iterdir()}, before_packet)
        # The old course still defers even when active_lesson points elsewhere.
        self.ws.state["active_lesson"] = None
        with patch("invo_learn.updates.check_updates") as check:
            self.assertEqual(study_update(self.ws, "math")["status"], "deferred")
            self.assertEqual(study_update(self.ws)["status"], "deferred")
        check.assert_not_called()

    def synthetic_remote(self):
        self.remote = self.base / "backup.git"
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        for key, value in (("user.name", "Synthetic"), ("user.email", "synthetic@example.invalid")):
            backups.git(self.ws, "config", key, value)
        self.url = "https://github.com/synthetic/learner.git"
        backups.git(self.ws, "remote", "add", "origin", self.url)
        original = backups.run
        def transport(ws, *args, **kwargs):
            if args[:2] == ("gh", "api"):
                return json.dumps({"private": True, "full_name": "synthetic/learner", "permissions": {"push": True}, "fork": False})
            # Map ONLY Git's network transport to a synthetic local bare repo.
            return original(ws, *(str(self.remote) if a == self.url and any(v in args for v in ("push", "ls-remote")) else a for a in args), **kwargs)
        patcher = patch("invo_learn.backup.run", side_effect=transport)
        patcher.start()
        self.addCleanup(patcher.stop)
        backups.configure(self.ws, "origin", "synthetic/learner")

    def files(self):
        return [p.relative_to(self.root).as_posix() for p in self.root.rglob("*")
                if p.is_file() and ".git" not in p.parts and "mailbox" not in p.parts]

    def test_scoped_commit_push_verification_and_no_empty_duplicate(self):
        self.synthetic_remote()
        before = self.ws.state_path.read_bytes()
        paths = self.files()
        unrelated = self.root / "unrelated.txt"
        unrelated.write_text("must remain untracked", encoding="utf-8")
        result = backups.backup(self.ws, paths, "Synthetic completed work", "math")
        self.assertEqual(result["status"], "pushed", result)
        self.assertEqual(self.ws.state_path.read_bytes(), before)
        self.assertNotIn("unrelated.txt", backups.git(self.ws, "ls-tree", "-r", "--name-only", "HEAD"))
        self.assertEqual(backups.backup(self.ws, paths, "No empty commit")["status"], "no-changes")
        self.assertEqual(backups.git(self.ws, "rev-list", "--count", "HEAD"), "1")

    def test_report_plan_backup_duplicate_and_push_retry_preserve_artifacts(self):
        self.synthetic_remote()
        lesson = call(self.ws, "prepare", "math", spec(["solve"]), "2026-10-18")
        raw = "```json\r\n" + json.dumps(make_report(self.ws.state["lessons"][lesson["lesson_id"]], "2026-10-18", [item("solve")])) + "\r\n```"
        call(self.ws, "ingest", raw, "2026-10-18")
        plan = self.root / "tracks/math/plan.md"
        plan.write_text("Synthetic next plan after report", encoding="utf-8")
        before = {p: (self.root / p).read_bytes() for p in self.files()}
        original = backups.git
        def failed_push(ws, *args, **kwargs):
            if args[0] == "push":
                raise Invalid("Synthetic push failure")
            return original(ws, *args, **kwargs)
        with patch("invo_learn.backup.git", side_effect=failed_push):
            failed = backups.backup(self.ws, self.files(), "Synthetic report and plan")
        self.assertEqual(failed["status"], "backup-failed")
        self.assertTrue(failed["local_work_preserved"])
        self.assertTrue(failed["commit"])
        for p, data in before.items():
            self.assertEqual((self.root / p).read_bytes(), data)
        self.assertEqual(backups.backup(self.ws, self.files(), "Retry backup")["status"], "pushed")
        self.assertEqual(call(self.ws, "ingest", raw, "2026-10-18")["status"], "duplicate")
        self.assertEqual(backups.backup(self.ws, self.files(), "Duplicate report")["status"], "no-changes")
        self.assertEqual(backups.git(self.ws, "rev-list", "--count", "HEAD"), "1")

    def test_absent_public_unverified_and_wrong_workspace_remotes_do_not_push(self):
        before = self.ws.state_path.read_bytes()
        result = backups.backup(self.ws, self.files(), "No remote")
        self.assertEqual(result["status"], "backup-failed")
        for url in ("https://github.com/Matt-Salamone/invo-learn.git", "git@github.com:Matt-Salamone/invo-learn.git"):
            with self.assertRaisesRegex(Invalid, "public harness"):
                backups.repository_url(url)
        self.synthetic_remote()
        with patch("invo_learn.backup.verify", side_effect=Invalid("private status unavailable")):
            self.assertEqual(backups.backup(self.ws, self.files(), "Unverified")["status"], "backup-failed")
        binding = read_json(self.root / ".invo-learn/backup-remote.json")
        binding["workspace_id"] = "different"
        atomic(self.root / ".invo-learn/backup-remote.json", binding)
        self.assertIn("different workspace", backups.backup(self.ws, self.files(), "Wrong workspace")["reason"])
        self.assertEqual(self.ws.state_path.read_bytes(), before)
        self.assertEqual(backups.git(self.ws, "diff", "--cached", "--name-only"), "")

    def test_staged_changes_and_unrelated_unpushed_history_are_refused(self):
        self.synthetic_remote()
        other = self.root / "other.txt"
        other.write_text("unrelated", encoding="utf-8")
        backups.git(self.ws, "add", "--", "other.txt")
        before = backups.git(self.ws, "diff", "--cached")
        result = backups.backup(self.ws, ["state.json"], "Should refuse")
        self.assertIn("staged", result["reason"])
        self.assertEqual(backups.git(self.ws, "diff", "--cached"), before)
        backups.git(self.ws, "commit", "-m", "Synthetic unrelated history")
        result = backups.backup(self.ws, ["state.json"], "Should refuse history")
        self.assertIn("Unpushed history", result["reason"])

    def test_visibility_identity_forks_and_multi_destination_remotes_are_refused(self):
        self.synthetic_remote()
        original = backups.run
        for response in ({"private": False}, {"private": True, "full_name": "wrong/repo", "permissions": {"push": True}},
                         {"private": True, "full_name": "synthetic/learner", "permissions": {"push": True}, "fork": True}):
            def api(ws, *args, **kwargs):
                if args[:2] == ("gh", "api"):
                    return json.dumps(response)
                return original(ws, *args, **kwargs)
            with self.subTest(response=response), patch("invo_learn.backup.run", side_effect=api):
                self.assertEqual(backups.backup(self.ws, self.files(), "Should refuse privacy")["status"], "backup-failed")
            self.assertEqual(backups.git(self.ws, "diff", "--cached", "--name-only"), "")
        backups.git(self.ws, "config", "--add", "remote.origin.pushurl", self.url)
        backups.git(self.ws, "config", "--add", "remote.origin.pushurl", "https://github.com/synthetic/other.git")
        self.assertIn("one identical", backups.backup(self.ws, self.files(), "No multi-push")["reason"])

    def test_commit_failure_and_unverified_push_preserve_successful_learning(self):
        self.synthetic_remote()
        before = self.ws.state_path.read_bytes()
        original = backups.git
        def fail_commit(ws, *args, **kwargs):
            if args[0] == "commit":
                raise Invalid("Synthetic identity failure")
            return original(ws, *args, **kwargs)
        with patch("invo_learn.backup.git", side_effect=fail_commit):
            failed = backups.backup(self.ws, self.files(), "Commit failure")
        self.assertEqual(failed["status"], "backup-failed")
        self.assertIsNone(failed["commit"])
        self.assertEqual(self.ws.state_path.read_bytes(), before)
        self.assertTrue(backups.git(self.ws, "diff", "--cached", "--name-only"))
        # Resolve the saved scoped index, then test a push acknowledgement without
        # a matching remote SHA. This must never be reported as pushed.
        backups.git(self.ws, "commit", "-m", "Synthetic completed work")
        def unverified(ws, *args, **kwargs):
            if args[0] == "ls-remote":
                return ""
            if args[0] == "push":
                return ""
            return original(ws, *args, **kwargs)
        with patch("invo_learn.backup.git", side_effect=unverified):
            failed = backups.backup(self.ws, self.files(), "Unverified push")
        self.assertEqual(failed["status"], "backup-failed")
        self.assertIn("verification failed", failed["reason"])
        self.assertTrue(failed["commit"])
        self.assertEqual(self.ws.state_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
