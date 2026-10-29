"""Installed S1 maintenance, updates and byte-preserving Git journeys."""
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from examples.worked_example import PUBLIC, item, make_report, map_spec, spec


class MaintenanceJourneys(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-maintenance-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "private"
        preferences = self.write({"auto_update": False, "auto_backup": False, "teaching_style": "Synthetic concise teaching"})
        result = subprocess.run([sys.executable, "-m", "invo_learn", "bootstrap", str(self.root),
                                 "--name", "Synthetic", "--preferences", str(preferences)],
                                cwd=PUBLIC, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.cli("add-course", "math", "--title", "Synthetic math")
        source = self.base / "original.txt"
        source.write_bytes(b"Preserve LF.\nPreserve CRLF.\r\nInverse operations preserve equality.\n")
        material = self.cli("add-material", "math", source)
        proposal = self.cli("propose-map", "math", self.write(map_spec(material["id"], [("solve", "Solve equations", "skill", "whole file", [])])))
        self.cli("accept-map", "math", proposal["proposal_id"], "--approval", "Synthetic approval")
        prepared = self.cli("prepare", "math", self.write(spec(["solve"])))
        report = make_report({"id": prepared["lesson_id"], "track_id": "math"}, "2026-10-29", [item("solve")])
        self.cli("ingest", self.write(report))
        for directory in ("legacy/synthetic-origin", "migration-records/synthetic-migration/returns"):
            archive = self.root / directory / "original-return.txt"
            archive.parent.mkdir(parents=True, exist_ok=True)
            archive.write_bytes(b"Synthetic preserved legacy or migration return.\n")
        self.version = json.loads((self.root / ".invo-learn/active.json").read_text())["version"]
        major, minor, patch = map(int, self.version.split("."))
        self.next_version = f"{major}.{minor}.{patch + 1}"

    def write(self, obj):
        path = self.base / ("input-" + str(len(list(self.base.glob("input-*")))) + ".json")
        path.write_text(json.dumps(obj), encoding="utf-8", newline="")
        return path

    def cli(self, *args, ok=True, env=None, root=None):
        result = subprocess.run([sys.executable, str((root or self.root) / "learn.py"), "--today", "2026-10-29", *map(str, args)],
                                cwd=self.base, capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0 if ok else 2, result.stdout + result.stderr)
        return json.loads(result.stdout if ok else result.stderr)

    def git(self, *args, root=None):
        result = subprocess.run(["git", "-C", str(root or self.root), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def immutable(self, root=None):
        root = root or self.root
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for directory in ("tracks", "lessons", "reports", "inbox", "legacy", "migration-records", ".invo-learn/releases")
                for p in (root / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts}

    def test_equivalent_public_lf_and_crlf_sources_have_identical_installed_payload(self):
        from invo_learn.install import package
        _, _, files, _ = package(PUBLIC)
        sources = []
        for label, newline in (("lf", b"\n"), ("crlf", b"\r\n")):
            source = self.base / label
            for name, data in files.items():
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data.replace(b"\r\n", b"\n").replace(b"\n", newline))
            sources.append(source)
        original = self.immutable()
        first = self.cli("upgrade", "--source", sources[0])
        second = self.cli("upgrade", "--source", sources[1])
        self.assertEqual(first["status"], "already-current")
        self.assertEqual(second["status"], "already-current")
        self.assertEqual(package(sources[0])[2:], package(sources[1])[2:])
        self.assertEqual(self.immutable(), original)

    def test_missing_runtime_module_refuses_install_before_creating_workspace(self):
        from invo_learn.install import package
        _, _, files, _ = package(PUBLIC)
        source = self.base / "incomplete-public"
        for name, content in files.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        required = [name for name in files if name.startswith("invo_learn/") and name.endswith(".py")]
        for name in required + ["LICENSE"]:
            path = source / name
            raw = path.read_bytes()
            path.unlink()
            target = self.base / "must-not-create"
            result = self.cli("bootstrap", target, "--source", source, "--name", "Synthetic", "--no-git", ok=False)
            self.assertIn("incomplete harness package", result["error"])
            self.assertFalse(target.exists())
            path.write_bytes(raw)

    def future(self, layout=1):
        from invo_learn.install import package
        source = self.base / "future"
        _, _, files, _ = package(PUBLIC)
        for name, data in files.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (source / "VERSION").write_bytes((self.next_version + "\n").encode())
        metadata = json.loads((source / "harness.json").read_text())
        metadata["workspace_layout"] = layout
        (source / "harness.json").write_text(json.dumps(metadata), encoding="utf-8", newline="")
        with (source / "invo_learn/templates/chatbot.md").open("ab") as out:
            out.write(b"\nSYNTHETIC FUTURE ACTIVE TEMPLATE\n")
        return source

    def transport(self, source, mode="available"):
        fixtures = self.base / "transport"
        fixtures.mkdir(exist_ok=True)
        (fixtures / "sitecustomize.py").write_text(r'''import io, os, shutil, subprocess, urllib.request
from urllib.error import URLError
from pathlib import Path
_original_run = subprocess.run
_original_replace = os.replace
_failure = os.environ.get("INVO_TEST_MODE") == "activation-failed"
def _log(value):
    with open(os.environ["INVO_TEST_LOG"], "a", encoding="utf-8") as out:
        out.write(value + "\n")
def _urlopen(url, *args, **kwargs):
    _log("version-request")
    if os.environ.get("INVO_TEST_MODE") == "offline":
        raise URLError("synthetic offline")
    if url.startswith("https://codeload.github.com/") and os.environ.get("INVO_TEST_ARCHIVE"):
        return io.BytesIO(Path(os.environ["INVO_TEST_ARCHIVE"]).read_bytes())
    return io.BytesIO(os.environ["INVO_TEST_LATEST"].encode())
def _run(command, **kwargs):
    if os.environ.get("INVO_TEST_UNSAFE_INDEX") and command[0] == "git" and command[-2:] == ["ls-files", "-z"]:
        return subprocess.CompletedProcess(command, 0, b"../escaped/.gitattributes\x00", b"")
    if os.environ.get("INVO_TEST_BARE") and command[:2] == ["gh", "api"]:
        return subprocess.CompletedProcess(command, 0, '{"private":true,"full_name":"synthetic/private","permissions":{"push":true},"fork":false}', "")
    if os.environ.get("INVO_TEST_BARE") and command[0] == "git" and any(value in command for value in ("push", "ls-remote")):
        command = [os.environ["INVO_TEST_BARE"] if value == "https://github.com/synthetic/private.git" else value for value in command]
    if command[:2] == ["git", "clone"]:
        _log("trusted-clone")
        if os.environ.get("INVO_TEST_MODE") == "download-failed":
            return subprocess.CompletedProcess(command, 1, "", "synthetic transport failure")
        shutil.copytree(os.environ["INVO_TEST_SOURCE"], command[-1])
        return subprocess.CompletedProcess(command, 0, "", "")
    return _original_run(command, **kwargs)
def _replace(source, target):
    global _failure
    if _failure and str(target).replace("\\", "/").endswith("/.invo-learn/active.json"):
        _failure = False
        raise OSError("synthetic activation rename failure")
    return _original_replace(source, target)
urllib.request.urlopen = _urlopen
subprocess.run = _run
os.replace = _replace
''', encoding="utf-8", newline="")
        env = os.environ.copy()
        env.update(PYTHONPATH=str(fixtures), INVO_TEST_SOURCE=str(source), INVO_TEST_MODE=mode,
                   INVO_TEST_LATEST=self.next_version, INVO_TEST_LOG=str(self.base / "transport.log"))
        return env

    def test_layout_change_requires_explicit_migration_without_reorganizing_data(self):
        source = self.future(layout=2)
        before = self.immutable()
        state = (self.root / "state.json").read_bytes()
        self.cli("preferences", self.write({"auto_update": True}))
        state = (self.root / "state.json").read_bytes()
        result = self.cli("study-update", "--track", "math", env=self.transport(source))
        self.assertEqual(result["status"], "migration-required")
        self.assertEqual(result["required_layout"], 2)
        self.assertEqual(before, self.immutable())
        self.assertEqual(state, (self.root / "state.json").read_bytes())
        self.assertEqual(json.loads((self.root / ".invo-learn/active.json").read_text())["version"], self.version)
        self.assertFalse((self.root / ".invo-learn/releases" / self.next_version).exists())
        metadata = json.loads((source / "harness.json").read_text())
        metadata.update(workspace_layout=1, state_schema=2)
        (source / "harness.json").write_text(json.dumps(metadata), encoding="utf-8", newline="")
        schema_change = self.cli("study-update", "--track", "math", env=self.transport(source))
        self.assertEqual(schema_change["status"], "migration-required")
        self.assertEqual(schema_change["required_state_schema"], 2)
        self.assertEqual(before, self.immutable())
        self.assertEqual(state, (self.root / "state.json").read_bytes())


    def test_fresh_workspace_records_survive_autocrlf_clone_byte_for_byte(self):
        expected = self.immutable()
        for key, value in (("user.name", "Synthetic"), ("user.email", "synthetic@example.invalid"), ("core.autocrlf", "true")):
            self.git("config", key, value)
        files = self.git("ls-files", "--others", "--exclude-standard", "-z").split("\x00")
        paths = self.base / "commit-scope.txt"
        paths.write_bytes(b"\x00".join(name.encode("utf-8") for name in files if name) + b"\x00")
        self.git("add", "--pathspec-from-file", paths, "--pathspec-file-nul")
        self.git("commit", "-m", "Synthetic byte-preservation roundtrip")
        clone = self.base / "clone"
        self.git("-c", "core.autocrlf=true", "clone", "--local", self.root, clone, root=self.base)
        self.assertEqual(expected, self.immutable(clone))
        self.assertEqual(self.cli("status", root=clone)["learner"]["preferences"]["teaching_style"], "Synthetic concise teaching")

    def test_compatible_update_uses_new_active_code_and_preserves_learning_and_opt_outs(self):
        source = self.future()
        before = self.immutable()
        profile = self.cli("status")["learner"]
        self.cli("preferences", self.write({"auto_update": True}))
        result = self.cli("prepare", "math", self.write(spec(["solve"])), env=self.transport(source))
        self.assertEqual(result["update"]["status"], "upgraded")
        self.assertIn("SYNTHETIC FUTURE ACTIVE TEMPLATE", (self.root / "mailbox/START-HERE.md").read_text())
        self.assertTrue(all(self.immutable()[name] == checksum for name, checksum in before.items()))
        learner = self.cli("status")["learner"]
        self.assertEqual(learner["preferences"]["teaching_style"], profile["preferences"]["teaching_style"])
        self.assertFalse(learner["preferences"]["auto_backup"])

    def test_opt_out_and_offline_results_remain_truthful_and_study_available(self):
        source = self.future()
        env = self.transport(source)
        self.assertEqual(self.cli("study-update", "--track", "math", env=env)["status"], "disabled")
        self.assertFalse((self.base / "transport.log").exists())
        self.cli("preferences", self.write({"auto_update": True}))
        prepared = self.cli("prepare", "math", self.write(spec(["solve"])), env=self.transport(source, "offline"))
        self.assertEqual(prepared["update"]["status"], "unavailable")
        self.assertNotIn("latest_version", prepared["update"])
        self.assertNotIn("SYNTHETIC FUTURE ACTIVE TEMPLATE", (self.root / "mailbox/START-HERE.md").read_text())

    def test_activation_failure_rolls_back_exports_and_download_failure_keeps_work(self):
        source = self.future()
        self.cli("preferences", self.write({"auto_update": True}))
        active = (self.root / ".invo-learn/active.json").read_bytes()
        before = self.immutable()
        exports = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in (self.root / ".agents/skills").rglob("*") if p.is_file()}
        for mode in ("activation-failed", "download-failed"):
            with self.subTest(mode=mode):
                result = self.cli("study-update", "--track", "math", env=self.transport(source, mode))
                self.assertEqual(result["status"], "failed")
                self.assertEqual(active, (self.root / ".invo-learn/active.json").read_bytes())
                self.assertTrue(all(self.immutable()[name] == checksum for name, checksum in before.items()))
                self.assertEqual(exports, {p.relative_to(self.root).as_posix(): p.read_bytes() for p in (self.root / ".agents/skills").rglob("*") if p.is_file()})

    def test_customized_export_blocks_update_without_overwriting_it(self):
        source = self.future()
        custom = self.root / ".agents/skills/invo-learn/SKILL.md"
        custom.write_bytes(b"Synthetic user customization.\n")
        self.cli("preferences", self.write({"auto_update": True}))
        result = self.cli("study-update", "--track", "math", env=self.transport(source))
        self.assertEqual(result["status"], "failed")
        self.assertIn("modified", result["reason"])
        self.assertEqual(custom.read_bytes(), b"Synthetic user customization.\n")
        self.assertEqual(json.loads((self.root / ".invo-learn/active.json").read_text())["version"], self.version)

    def test_explicit_byte_maintenance_preserves_custom_rules_and_refuses_conflicts(self):
        attributes = self.root / ".gitattributes"
        custom = b"user-notes/** text eol=lf\r\n*.custom linguist-generated\r\n"
        attributes.write_bytes(custom)
        before = self.immutable()
        result = self.cli("protect-record-bytes")
        self.assertEqual(result["status"], "protected")
        self.assertTrue(attributes.read_bytes().startswith(custom))
        self.assertEqual(before, self.immutable())
        self.assertEqual(self.cli("protect-record-bytes")["status"], "already-protected")
        nested = self.root / "tracks/math/.gitattributes"
        nested.write_bytes(b"*.txt text\n")
        original = attributes.read_bytes()
        error = self.cli("protect-record-bytes", ok=False)
        self.assertIn("custom Git attributes", error["error"])
        self.assertEqual(original, attributes.read_bytes())
        self.assertEqual(nested.read_bytes(), b"*.txt text\n")

    def test_byte_maintenance_never_rehashes_corrupted_originals(self):
        material = next(iter(self.cli("status")["tracks"]["math"]["materials"].values()))
        (self.root / material["original"]).write_bytes(b"altered original\n")
        attributes = self.root / ".gitattributes"
        attributes.unlink()
        error = self.cli("protect-record-bytes", ok=False)
        self.assertIn("never rehash", error["error"])
        self.assertFalse(attributes.exists())
        actual = next(iter(self.cli("status")["tracks"]["math"]["materials"].values()))
        self.assertEqual(material["sha256"], actual["sha256"])

    def test_temporary_maintenance_upgrades_actual_older_bundle_without_rewriting_it(self):
        source = self.future()
        older = self.base / "older-source"
        with zipfile.ZipFile(PUBLIC / "tests/fixtures/invo-learn-0.7.0.zip") as bundle:
            bundle.extractall(older)
        older = older / "invo-learn-0.7.0"
        legacy = self.base / "legacy-private"
        preferences = self.write({"auto_update": False, "auto_backup": False, "teaching_style": "Actual old custom preference"})
        initial = subprocess.run([sys.executable, "-m", "invo_learn", "bootstrap", str(legacy),
                                  "--name", "Synthetic old learner", "--preferences", str(preferences)],
                                 cwd=older, capture_output=True, text=True)
        self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)
        original = {p.relative_to(legacy).as_posix(): p.read_bytes() for p in (legacy / ".invo-learn/releases/0.7.0").rglob("*") if p.is_file()}
        archive = self.base / "candidate.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            for path in source.rglob("*"):
                if path.is_file():
                    bundle.write(path, "candidate/" + path.relative_to(source).as_posix())
        env = self.transport(source)
        env["INVO_TEST_ARCHIVE"] = str(archive)
        result = subprocess.run([sys.executable, str(PUBLIC / "setup_workspace.py"), str(legacy), "--upgrade"],
                                cwd=self.base, capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "upgraded")
        self.assertTrue(all((legacy / name).read_bytes() == data for name, data in original.items()))
        self.assertEqual([p.parent.name for p in (legacy / ".agents/skills").glob("*/SKILL.md")], ["invo-learn"])
        learner = self.cli("status", root=legacy)["learner"]
        self.assertEqual(learner["preferences"]["teaching_style"], "Actual old custom preference")
        self.assertFalse(learner["preferences"]["auto_update"])
        self.assertFalse(learner["preferences"]["auto_backup"])
        self.assertIn("single", (legacy / ".agents/skills/invo-learn/SKILL.md").read_text().lower())
        self.assertNotIn("invo-learn-add-course/SKILL.md", (legacy / "AGENTS.md").read_text())

    def test_scoped_private_backup_requires_portable_attributes_in_the_commit(self):
        bare = self.base / "private-backup.git"
        self.git("init", "--bare", bare, root=self.base)
        for key, value in (("user.name", "Synthetic"), ("user.email", "synthetic@example.invalid")):
            self.git("config", key, value)
        self.git("remote", "add", "origin", "https://github.com/synthetic/private.git")
        env = self.transport(self.base / "unused-source")
        env["INVO_TEST_BARE"] = str(bare)
        (self.root / ".git/info/attributes").write_bytes(b"user-notes/** text eol=lf\n")
        self.cli("configure-backup", "--repository", "synthetic/private", env=env)
        self.cli("preferences", self.write({"auto_backup": True}))
        rejected = self.cli("backup", "--paths", "state.json", "--message", "Synthetic incomplete scope", env=env)
        self.assertEqual(rejected["status"], "backup-failed")
        self.assertIn(".gitattributes", rejected["reason"])
        self.git("rm", "--cached", "--", "state.json")
        files = [name for name in self.git("ls-files", "--others", "--exclude-standard", "-z").split("\x00") if name]
        before = self.immutable()
        result = self.cli("backup", "--paths", *files, "--message", "Synthetic reviewed private workspace", env=env)
        self.assertEqual(result["status"], "pushed", result)
        self.assertEqual(result["commit"], self.git("rev-parse", "refs/heads/main", root=bare).strip())
        clone = self.base / "private-backup-clone"
        self.git("-c", "core.autocrlf=true", "clone", "--branch", "main", "--local", bare, clone, root=self.base)
        self.assertEqual(before, self.immutable(clone))

    def test_compatible_update_preserves_custom_workspace_guidance(self):
        source = self.future()
        guidance = self.root / "AGENTS.md"
        custom = guidance.read_bytes() + b"\nSynthetic user guidance: retain this instruction.\n"
        guidance.write_bytes(custom)
        self.cli("preferences", self.write({"auto_update": True}))
        result = self.cli("study-update", "--track", "math", env=self.transport(source))
        self.assertEqual(result["status"], "upgraded")
        self.assertEqual(result["guidance"], "customized-preserved")
        self.assertEqual(guidance.read_bytes(), custom)

    def test_unrelated_local_attribute_rules_are_preserved_without_blocking_maintenance(self):
        local = self.root / ".git/info/attributes"
        custom = b"user-notes/** text eol=lf\n"
        local.write_bytes(custom)
        self.assertEqual(self.cli("protect-record-bytes")["status"], "already-protected")
        self.assertEqual(local.read_bytes(), custom)

    @unittest.skipUnless(os.name == "nt", "Windows temporary-path alias regression")
    def test_scoped_private_backup_accepts_windows_temp_path_alias(self):
        import ctypes
        from ctypes import wintypes
        target = self.base / "Long temporary directory alias target"
        target.mkdir()
        short_path = ctypes.WinDLL("kernel32", use_last_error=True).GetShortPathNameW
        short_path.argtypes = (wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD)
        short_path.restype = wintypes.DWORD
        size = short_path(str(target), None, 0)
        alias = target
        if size:
            buffer = ctypes.create_unicode_buffer(size)
            if short_path(str(target), buffer, size):
                alias = Path(buffer.value)
        if alias == alias.resolve():
            alias = self.base / "temporary-junction-alias"
            linked = subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(target)], capture_output=True, text=True)
            if linked.returncode:
                self.skipTest("A Windows short-name or junction alias is unavailable: " + linked.stderr.strip())
            self.addCleanup(alias.rmdir)
        self.assertNotEqual(alias, alias.resolve())
        self.assertTrue(alias.samefile(target))
        bare = self.base / "alias-backup.git"
        self.git("init", "--bare", bare, root=self.base)
        for key, value in (("user.name", "Synthetic"), ("user.email", "synthetic@example.invalid")):
            self.git("config", key, value)
        self.git("remote", "add", "origin", "https://github.com/synthetic/private.git")
        env = self.transport(self.base / "unused-source")
        env.update(INVO_TEST_BARE=str(bare), TMPDIR=str(alias), TEMP=str(alias), TMP=str(alias))
        (self.root / ".git/info/attributes").write_bytes(b"user-notes/** text eol=lf\n")
        self.cli("configure-backup", "--repository", "synthetic/private", env=env)
        self.cli("preferences", self.write({"auto_backup": True}))
        files = [name for name in self.git("ls-files", "--others", "--exclude-standard", "-z").split("\x00") if name]
        before = self.immutable()
        result = self.cli("backup", "--paths", *files, "--message", "Synthetic aliased temporary directory", env=env)
        self.assertEqual(result["status"], "pushed", result)
        self.assertEqual(result["commit"], self.git("rev-parse", "refs/heads/main", root=bare).strip())
        self.assertEqual(before, self.immutable())

    def test_scoped_private_backup_rejects_escaping_staged_attribute_path(self):
        bare = self.base / "guard-backup.git"
        self.git("init", "--bare", bare, root=self.base)
        for key, value in (("user.name", "Synthetic"), ("user.email", "synthetic@example.invalid")):
            self.git("config", key, value)
        self.git("remote", "add", "origin", "https://github.com/synthetic/private.git")
        env = self.transport(self.base / "unused-source")
        env.update(INVO_TEST_BARE=str(bare), INVO_TEST_UNSAFE_INDEX="1")
        (self.root / ".git/info/attributes").write_bytes(b"user-notes/** text eol=lf\n")
        self.cli("configure-backup", "--repository", "synthetic/private", env=env)
        self.cli("preferences", self.write({"auto_backup": True}))
        files = [name for name in self.git("ls-files", "--others", "--exclude-standard", "-z").split("\x00") if name]
        before = self.immutable()
        result = self.cli("backup", "--paths", *files, "--message", "Synthetic corrupt external index listing", env=env)
        self.assertEqual(result["status"], "backup-failed")
        self.assertEqual(result["reason"], "unsafe staged attribute path")
        self.assertEqual(self.git("ls-remote", bare, "refs/heads/main", root=self.base), "")
        self.assertEqual(before, self.immutable())
