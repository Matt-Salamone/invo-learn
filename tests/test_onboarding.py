import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from invo_learn.contracts import Invalid
from invo_learn.engine import Workspace, digest, read_json
from invo_learn.install import bootstrap, package
from examples.worked_example import PUBLIC, call, item, make_report, map_spec, spec
from setup_workspace import install, unpack


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-learn-onboarding-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "learning"

    def archive(self):
        _, _, files, _ = package(PUBLIC)
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as bundle:
            for name, content in files.items():
                bundle.writestr("invo-learn-main/" + name, content)
        return data.getvalue()

    def test_standalone_install_leaves_one_usable_workspace_and_no_source_clone(self):
        prefs = self.base / "preferences.json"
        prefs.write_text(json.dumps({"teaching_style": "examples then practice", "supplemental_research": True,
                                     "auto_update": False, "auto_backup": False}))
        mailbox = self.base / "Desktop/learning-mailbox"
        with patch("setup_workspace.urlopen", return_value=io.BytesIO(self.archive())):
            result = install(self.root, "Synthetic learner", mailbox, prefs)
        self.assertEqual(result["workspace"], str(self.root))
        ws = Workspace(self.root)
        self.assertEqual(ws.mailbox(), mailbox)
        self.assertEqual(ws.state["profile"]["preferences"]["teaching_style"], "examples then practice")
        self.assertTrue(ws.state["profile"]["preferences"]["supplemental_research"])
        self.assertIsNone(ws.state["profile"]["preferences"]["schedule"])
        self.assertFalse((self.root / "invo_learn").exists())
        self.assertFalse((self.root / "incoming").exists())
        self.assertEqual(subprocess.run(["git", "-C", str(self.root), "remote"],
                                       capture_output=True, text=True, check=True).stdout, "")
        active = read_json(self.root / ".invo-learn/active.json")
        self.assertTrue(active["source"].startswith("https://codeload.github.com/"))
        self.assertEqual(sorted(p.name for p in self.base.iterdir()),
                         ["Desktop", "learning", "preferences.json"])
        skill_file = self.root / ".agents/skills/invo-learn/SKILL.md"
        self.assertEqual(skill_file.read_bytes(), (PUBLIC / "skills/invo-learn/SKILL.md").read_bytes().replace(b"\r\n", b"\n"))
        self.assertEqual(sorted(p.name for p in (self.root / ".agents/skills").iterdir()), ["invo-learn"])
        self.assertEqual(sorted(p.name for p in (self.root / ".invo-learn/releases" / active["version"] / "skills").iterdir()), ["invo-learn"])
        self.assertIn(str(mailbox), (self.root / "START-HERE.md").read_text())
        out = subprocess.run([sys.executable, str(self.root / "learn.py"), "status"],
                             capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(out.stdout)["mailbox"], str(mailbox))

        # The downloaded public source is gone: every subsequent operation uses
        # the installed command from an unrelated working directory (seam S1).
        def installed(*args):
            result = subprocess.run([sys.executable, str(self.root / "learn.py"),
                                     "--today", "2026-10-14", *map(str, args)],
                                    cwd=self.base, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)

        def private_json(name, data):
            path = self.base / name
            path.write_text(json.dumps(data), encoding="utf-8")
            return path

        installed("add-course", "math", "--title", "Synthetic math")
        source = mailbox / "lecture.any-extension"
        source.write_text("Solve equations using inverse operations on both sides.", encoding="utf-8")
        original = source.read_bytes()
        material = installed("add-material", "math", source)
        mapping = map_spec(material["id"], [("solve", "Solve a linear equation", "skill", "whole file", [])])
        proposal = installed("propose-map", "math", private_json("map.json", mapping))
        installed("accept-map", "math", proposal["proposal_id"], "--approval", "Synthetic approval")
        prepared = installed("prepare", "math", private_json("lesson.json", spec(["solve"])))
        packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        packet_before = {p.name: p.read_bytes() for p in packet.iterdir() if p.is_file()}
        report = make_report({"id": prepared["lesson_id"], "track_id": "math"},
                             "2026-10-14", [item("solve")])
        raw = json.dumps(report)
        report_file = self.base / "returned-report.json"
        report_file.write_text(raw, encoding="utf-8")
        installed("ingest", report_file)
        status = installed("status")
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"]["understanding"], "demonstrated")
        self.assertTrue(status["tracks"]["math"]["objectives"]["solve"]["review"])
        self.assertTrue(any(p.read_bytes() == original for p in self.root.rglob("lecture.any-extension")))
        self.assertTrue(any(p.read_text(encoding="utf-8") == raw for p in (self.root / "inbox").rglob("*.txt")))
        self.assertEqual(packet_before, {p.name: p.read_bytes() for p in packet.iterdir() if p.is_file()})

    def test_obsolete_course_alias_is_not_delivered(self):
        bootstrap(PUBLIC, self.root, "Synthetic", git=False)
        out = subprocess.run([sys.executable, str(self.root / "learn.py"), "add-track",
                              "math", "--title", "Math"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 2)
        status = subprocess.run([sys.executable, str(self.root / "learn.py"), "status"],
                                capture_output=True, text=True, check=True)
        self.assertNotIn("math", json.loads(status.stdout)["tracks"])

    def test_install_refuses_nonempty_destination_without_touching_files(self):
        self.root.mkdir()
        valuable = self.root / "notes.txt"
        valuable.write_text("keep")
        with patch("setup_workspace.urlopen", return_value=io.BytesIO(self.archive())):
            with self.assertRaisesRegex(RuntimeError, "new or empty"):
                install(self.root, "Synthetic")
        self.assertEqual(valuable.read_text(), "keep")
        self.assertEqual([p.name for p in self.root.iterdir()], ["notes.txt"])

    def test_archive_traversal_is_rejected_before_any_extraction(self):
        for path in ("package/../../escape.txt", "/absolute.txt", "package/C:/escape", "package\\..\\escape"):
            data = io.BytesIO()
            with zipfile.ZipFile(data, "w") as bundle:
                bundle.writestr("package/normal.txt", "normal")
                bundle.writestr(path, "escape")
            data.seek(0)
            destination = self.base / "extracted"
            with self.subTest(path=path), self.assertRaises(ValueError):
                unpack(data, destination)
            self.assertFalse(destination.exists())

    def course(self):
        bootstrap(PUBLIC, self.root, "Synthetic", git=False)
        result = subprocess.run([sys.executable, str(self.root / "learn.py"), "add-course",
                                 "math", "--title", "Math"], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["track_id"], "math")
        return Workspace(self.root)

    def test_mailbox_upload_is_durable_and_repeat_intake_is_idempotent(self):
        ws = self.course()
        source = ws.mailbox() / "lecture.arbitrary"
        source.write_bytes(b"Solve linear equations.\n")
        material = call(ws, "add_material", "math", source)
        before = copy.deepcopy(ws.state)
        duplicate = call(ws, "add_material", "math", source)
        self.assertEqual(duplicate["id"], material["id"])
        self.assertEqual(ws.state, before)
        original = ws.path(material["original"])
        self.assertEqual(original.read_bytes(), source.read_bytes())
        self.assertTrue(source.exists())
        source.write_text("Updated lecture")
        updated = call(ws, "add_material", "math", source)
        self.assertNotEqual(updated["id"], material["id"])
        self.assertEqual(original.read_bytes(), b"Solve linear equations.\n")
        original.write_bytes(b"damaged")
        source.write_bytes(b"Solve linear equations.\n")
        with self.assertRaisesRegex(Invalid, "checksum"):
            call(ws, "add_material", "math", source)

    def test_additional_mailbox_upload_keeps_pending_lesson_and_approved_map(self):
        ws = self.course()
        source = ws.mailbox() / "lecture.md"
        source.write_text("Solve linear equations.")
        material = call(ws, "add_material", "math", source)
        mapping = map_spec(material["id"], [("solve", "Solve linear equations", "skill", "whole file", [])])
        proposal = call(ws, "propose_map", "math", mapping)
        call(ws, "accept_map", "math", proposal["proposal_id"], "Synthetic approval")
        prepared = call(ws, "prepare", "math", spec(["solve"]), "2026-10-14")
        lesson = ws.state["lessons"][prepared["lesson_id"]]
        start = (ws.mailbox() / "START-HERE.md").read_bytes()
        original_map = copy.deepcopy(ws.track("math")["objectives"])
        extra = ws.mailbox() / "lecture-2.md"
        extra.write_text("Explain inverse operations.")
        added = call(ws, "add_material", "math", extra)
        self.assertEqual(ws.state["active_lesson"], lesson["id"])
        self.assertEqual((ws.mailbox() / "START-HERE.md").read_bytes(), start)
        self.assertEqual(ws.track("math")["objectives"], original_map)
        expanded = copy.deepcopy(mapping)
        expanded["objectives"] += map_spec(added["id"], [
            ("inverse", "Explain inverse operations", "concept", "whole file", [])])["objectives"]
        proposal = call(ws, "propose_map", "math", expanded)
        self.assertEqual(ws.track("math")["map_revision"], 1)
        with self.assertRaisesRegex(Invalid, "awaits report"):
            call(ws, "prepare", "math", spec(["solve"]), "2026-10-14")
        report = make_report(lesson, "2026-10-14", [item("solve")])
        call(ws, "ingest", json.dumps(report), "2026-10-14")
        evidence = copy.deepcopy(ws.track("math")["objectives"]["solve"])
        call(ws, "accept_map", "math", proposal["proposal_id"], "Synthetic expanded-map approval")
        self.assertEqual(ws.track("math")["objectives"]["solve"], evidence)
        self.assertEqual(len(ws.state["tracks"]), 1)
        call(ws, "prepare", "math", spec(["inverse"]), "2026-10-14")
        snapshot = list((self.root / "inbox/mailbox-snapshots").rglob("lecture-2.md"))
        self.assertEqual(len(snapshot), 1)
        self.assertEqual(digest(snapshot[0].read_bytes()), added["sha256"])
        self.assertEqual(digest(ws.path(added["original"]).read_bytes()), added["sha256"])

    def test_mailbox_marker_is_not_registered_as_a_resource(self):
        ws = self.course()
        with self.assertRaisesRegex(Invalid, "ownership marker"):
            call(ws, "add_material", "math", ws.mailbox() / ".invo-mailbox.json")
        self.assertFalse(ws.track("math")["materials"])


if __name__ == "__main__":
    unittest.main()
