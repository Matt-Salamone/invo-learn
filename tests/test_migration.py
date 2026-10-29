"""Lossless explicit rehearsal at installed command seam S1; synthetic records only."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from examples.worked_example import PUBLIC, item, make_report, map_spec, spec
from test_legacy import hashes, write_json


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


class MigrationRehearsalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-migration-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "course"
        self.stage = self.base / "rehearsal"
        prefs = self.write({"auto_update": False, "auto_backup": False,
                            "teaching_style": "Detailed worked examples; label source pages"})
        installed = subprocess.run([sys.executable, "-B", "-m", "invo_learn", "bootstrap", str(self.root),
                                   "--name", "Synthetic", "--preferences", str(prefs)], cwd=PUBLIC,
                                  capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.cli("add-course", "math", "--title", "Synthetic math")
        material_file = self.base / "notes.txt"
        material_file.write_text("Explain equality and solve equations.", encoding="utf-8")
        material = self.cli("add-material", "math", material_file)
        self.material = material
        proposed = self.cli("propose-map", "math", self.write(map_spec(material["id"], [
            ("solve", "Solve equations", "skill", "whole file", [])])))
        self.cli("accept-map", "math", proposed["proposal_id"], "--approval", "Synthetic approval")
        prepared = self.cli("prepare", "math", self.write(spec(["solve"])))
        self.packet = self.root / "lessons" / prepared["lesson_id"] / "packet"
        lesson = json.loads((self.packet / "lesson.json").read_text())
        report = make_report(lesson, "2026-10-29", [item("solve")])
        self.cli("ingest", self.write(report))
        git(self.root, "add", "--", "state.json", "tracks", "lessons", "reports", ".gitignore")
        git(self.root, "-c", "user.name=Synthetic", "-c", "user.email=synthetic@localhost",
            "commit", "-m", "Synthetic course history")
        (self.root / "untracked-course.txt").write_text("Keep course work", encoding="utf-8")
        self.assignment = self.base / "assignment"
        self.make_assignment(self.assignment, "00000000-0000-0000-0000-000000000001")

    def write(self, value):
        path = self.base / ("input-" + str(len(list(self.base.glob("input-*")))) + ".json")
        write_json(path, value)
        return path

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, "-B", str(self.root / "learn.py"),
                                 "--today", "2026-10-29", *map(str, args)],
                                cwd=self.base, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stdout + result.stderr)
        return json.loads(result.stdout if ok else result.stderr)

    def make_assignment(self, root, assignment_id):
        root.mkdir()
        git(root, "init")
        source = root / "materials/originals/note.unknown"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"Explain equality and solve equations.")
        solution = root / "solution/solver.py"
        solution.parent.mkdir()
        solution.write_bytes(b"# Synthetic reference solution\n")
        write_json(root / "solution/verification.json", {"checks": [], "limitations": []})
        git(root, "add", "--", "solution", "materials")
        git(root, "-c", "user.name=Synthetic", "-c", "user.email=synthetic@localhost",
            "commit", "-m", "Synthetic reference revision")
        revision = git(root, "rev-parse", "HEAD")
        packet = {"assignment_id": assignment_id, "lesson_id": "reasoning", "packet_id": "packet-original",
                  "contract_version": 1, "solution_revision": revision, "path": "packets/original",
                  "status": "outstanding", "included": []}
        folder = root / "packets/original"
        write_json(folder / "manifest.json", packet)
        write_json(folder / "report-template.json", packet)
        write_json(folder / "report-contract.json", {"version": 1})
        (folder / "tutor.md").write_text("Preserve original source commentary instructions", encoding="utf-8")
        state = {"state_version": 1, "assignment_id": assignment_id, "name": "Synthetic solver",
                 "status": "teaching", "next_action": "return-lesson-report", "skill_version": "0.4.0",
                 "intake": {"deliverables": ["A solver"], "constraints": ["Preserve equality"],
                    "grading_criteria": ["Correct reasoning"], "uncertainties": [], "assumptions": [],
                    "sources": [{"id": "note_original", "kind": "course", "status": "usable",
                        "reference": "Synthetic notes", "original": "materials/originals/note.unknown",
                        "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]},
                 "solution": {"revision": revision, "artifacts": ["solution/solver.py"], "checks": [], "limitations": []},
                 "packets": {packet["packet_id"]: packet}, "active_packet": packet["packet_id"],
                 "evidence": []}
        write_json(root / ".invo/state.json", state)
        (root / ".gitignore").write_text("ignored/\n", encoding="utf-8")
        git(root, "add", "--", ".invo", "packets", ".gitignore")
        git(root, "-c", "user.name=Synthetic", "-c", "user.email=synthetic@localhost",
            "commit", "-m", "Synthetic packet history")
        (root / "untracked.ipynb").write_bytes(b"{\"cells\": []}\r\n")
        (root / "ignored").mkdir()
        (root / "ignored/draft.txt").write_bytes(b"Keep ignored learner work\r\n")

    def plan(self):
        return {"destination": str(self.root), "assignments": [{"source": str(self.assignment), "track_id": "math"}],
                "stage": str(self.stage)}

    def test_rehearsal_preserves_complete_sources_and_course_learning_without_activation(self):
        course_before, assignment_before = hashes(self.root), hashes(self.assignment)
        original_state = json.loads((self.root / "state.json").read_text())
        result = self.cli("migration-rehearse", self.write(self.plan()))
        self.assertEqual(result["status"], "rehearsed")
        self.assertFalse(result["activated"])
        manifest = json.loads((self.stage / "migration-manifest.json").read_text())
        self.assertEqual(len(manifest["sources"]), 2)
        for key, source in manifest["sources"].items():
            copied = self.stage / source["snapshot"]
            self.assertEqual(hashes(copied), course_before if source["kind"] == "course" else assignment_before)
            self.assertEqual(git(copied, "rev-parse", "HEAD"), source["origin"]["commit"])
        combined = self.stage / manifest["workspace"]
        state = json.loads((combined / "state.json").read_text())
        self.assertEqual(state["tracks"]["math"]["objectives"], original_state["tracks"]["math"]["objectives"])
        self.assertEqual(state["reports"], original_state["reports"])
        self.assertEqual(state["review_policy"], original_state["review_policy"])
        self.assertIn("Detailed worked examples", state["profile"]["preferences"]["teaching_style"])
        self.assertIn("no source commentary", state["profile"]["preferences"]["teaching_style"])
        self.assertEqual(hashes(combined / self.packet.relative_to(self.root)), hashes(self.packet))
        assignments = state["tracks"]["math"]["assignments"]
        self.assertEqual(len(assignments), 1)
        record = next(iter(assignments.values()))
        self.assertEqual(record["legacy_context"]["assignment_id"], "00000000-0000-0000-0000-000000000001")
        self.assertIsNone(record["solution_choice"])
        self.assertEqual(record["completion"], "not-started")
        self.assertEqual(hashes(self.root), course_before)
        self.assertEqual(hashes(self.assignment), assignment_before)

    def test_rehearsal_retry_is_idempotent_and_distinct_origins_do_not_collapse(self):
        other = self.base / "other-assignment"
        self.make_assignment(other, "00000000-0000-0000-0000-000000000002")
        plan = self.plan()
        plan["assignments"].append({"source": str(other), "track_id": "math"})
        result = self.cli("migration-rehearse", self.write(plan))
        before = hashes(self.stage)
        repeated = self.cli("migration-rehearse", self.write(plan))
        self.assertEqual(repeated["status"], "already-rehearsed")
        self.assertEqual(repeated["migration_id"], result["migration_id"])
        self.assertEqual(hashes(self.stage), before)
        state = json.loads((self.stage / "workspace/state.json").read_text())
        assignments = state["tracks"]["math"]["assignments"]
        self.assertEqual(len(assignments), 2)
        materials = [record["spec"]["material_ids"][0] for record in assignments.values()]
        self.assertEqual(len(set(materials)), 2)
        self.assertEqual(len({state["tracks"]["math"]["materials"][mid]["sha256"] for mid in materials}), 1)
        self.assertEqual(len(self.cli("migration-status", self.stage)["manifest"]["sources"]), 3)

    def test_missing_or_damaged_recorded_original_refuses_before_creating_stage(self):
        source = self.assignment / "materials/originals/note.unknown"
        original = source.read_bytes()
        source.write_bytes(b"changed")
        before = hashes(self.assignment)
        failure = self.cli("migration-rehearse", self.write(self.plan()), ok=False)
        self.assertIn("integrity", failure["error"])
        self.assertFalse(self.stage.exists())
        self.assertEqual(hashes(self.assignment), before)
        source.unlink()
        missing = self.cli("migration-rehearse", self.write(self.plan()), ok=False)
        self.assertIn("integrity", missing["error"])
        self.assertFalse(self.stage.exists())
        source.write_bytes(original)

    def test_changed_preserved_snapshot_cannot_pass_verification(self):
        self.cli("migration-rehearse", self.write(self.plan()))
        manifest = json.loads((self.stage / "migration-manifest.json").read_text())
        assignment = next(record for record in manifest["sources"].values() if record["kind"] == "assignment")
        (self.stage / assignment["snapshot"] / "ignored/draft.txt").write_bytes(b"damaged")
        failure = self.cli("migration-status", self.stage, ok=False)
        self.assertIn("inventory/hash", failure["error"])
        self.assertEqual((self.assignment / "ignored/draft.txt").read_bytes(), b"Keep ignored learner work\r\n")

    def test_external_mailbox_is_preserved_and_stage_is_inactive_but_inspectable(self):
        external = self.base / "external-mailbox"
        shutil.copytree(self.root / "mailbox", external)
        (external / "new-upload.unknown").write_bytes(b"Preserve external incoming material\r\n")
        state = json.loads((self.root / "state.json").read_text())
        state["mailbox"] = str(external)
        write_json(self.root / "state.json", state)
        write_json(external / ".invo-mailbox.json", {"workspace_id": state["workspace_id"], "path": str(external)})
        external_before = hashes(external)
        result = self.cli("migration-rehearse", self.write(self.plan()))
        manifest = self.cli("migration-status", self.stage)["manifest"]
        source = next(record for record in manifest["sources"].values() if record["kind"] == "course")
        self.assertEqual(hashes(self.stage / source["external_mailbox"]["snapshot"]), external_before)
        state = json.loads((Path(result["workspace"]) / "state.json").read_text())
        self.assertTrue(Path(state["mailbox"]).is_relative_to(Path(result["workspace"])))
        self.assertEqual((Path(state["mailbox"]) / "new-upload.unknown").read_bytes(), b"Preserve external incoming material\r\n")
        self.assertEqual(hashes(external), external_before)
        status = self.cli("--workspace", result["workspace"], "status")
        self.assertEqual(len(status["tracks"]["math"]["assignments"]), 1)
        blocked = self.cli("--workspace", result["workspace"], "add-course", "extra", "--title", "Blocked", ok=False)
        self.assertIn("inactive", blocked["error"])

    def test_linked_git_history_refuses_before_copying_incomplete_git_pointer(self):
        linked = self.base / "linked-assignment"
        git(self.assignment, "worktree", "add", "--detach", str(linked), "HEAD")
        plan = self.plan()
        plan["assignments"][0]["source"] = str(linked)
        result = self.cli("migration-rehearse", self.write(plan), ok=False)
        self.assertIn("linked-worktree", result["error"])
        self.assertFalse(self.stage.exists())

    def test_changed_archived_course_report_cannot_be_preserved_as_valid_original(self):
        state = json.loads((self.root / "state.json").read_text())
        report = next(iter(state["reports"].values()))
        archived = self.root / report["path"]
        changed = json.loads(archived.read_text())
        changed["objectives"][0]["assessments"][0]["learner_answer"] = "A different answer"
        write_json(archived, changed)
        result = self.cli("migration-rehearse", self.write(self.plan()), ok=False)
        self.assertIn("integrity", result["error"])
        self.assertFalse(self.stage.exists())

    def test_manifest_workspace_path_cannot_escape_the_staged_directory(self):
        self.cli("migration-rehearse", self.write(self.plan()))
        path = self.stage / "migration-manifest.json"
        manifest = json.loads(path.read_text())
        manifest["workspace"] = str(self.root)
        write_json(path, manifest)
        result = self.cli("migration-status", self.stage, ok=False)
        self.assertIn("path", result["error"])
        self.assertIn("rehearsal", result["error"])
