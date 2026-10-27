"""Synthetic packet preservation and reference-boundary regression checks."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from invo_learn import quality, syntax_reference
from invo_learn.engine import Workspace
from invo_learn.install import bootstrap
from examples.worked_example import PUBLIC, call, map_spec, spec


SHEET = "# Syntax reference\n\n`len(value)` returns the number of items.\n"


class SyntaxReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invo-reference-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "learner"
        bootstrap(PUBLIC, self.root, "Synthetic learner", git=False)
        self.ws = Workspace(self.root)
        call(self.ws, "add_track", "coding", "Synthetic coding")
        source = self.base / "source.txt"
        source.write_text("Implement a fresh function over an input sequence.", encoding="utf-8")
        material = call(self.ws, "add_material", "coding", source)
        mapping = map_spec(material["id"], [("implement", "Implement a function", "skill", "whole source", [])])
        proposal = call(self.ws, "propose_map", "coding", mapping)
        call(self.ws, "accept_map", "coding", proposal["proposal_id"], "Synthetic approval")

    def lesson_spec(self, mode="lesson"):
        value = spec(["implement"], mode)
        value.update(context="Teach Python sequence operations and assess a fresh function.",
                     coding=True, syntax_cheatsheet=SHEET)
        return value

    def test_coding_sheet_is_counted_preserved_and_restaged(self):
        for mode in ("lesson", "review"):
            with self.subTest(mode=mode):
                value = self.lesson_spec(mode)
                measured = quality.preflight(self.ws, "coding", value)
                plain = copy.deepcopy(value)
                plain.pop("syntax_cheatsheet")
                plain["coding"] = False
                baseline = quality.preflight(self.ws, "coding", plain)
                self.assertEqual(measured["attachment_count"], baseline["attachment_count"] + 1)
                self.assertEqual(measured["selected_bytes"] - baseline["selected_bytes"], len(SHEET.encode()))
                prepared = call(self.ws, "prepare", "coding", value, "2026-10-27")
                lid = prepared["lesson_id"]
                packet = self.root / "lessons" / lid / "packet"
                expected = {p.name: p.read_bytes() for p in packet.iterdir()}
                self.assertEqual(expected["syntax-cheatsheet.md"], SHEET.encode())
                manifest = json.loads(expected["packet-manifest.json"])
                entry = next(f for f in manifest["files"] if f["name"] == "syntax-cheatsheet.md")
                self.assertEqual(entry["sha256"], hashlib.sha256(SHEET.encode()).hexdigest())
                instructions = expected["START-HERE.md"].decode()
                self.assertLess(instructions.index("Permitted syntax reference"), instructions.index("Select a chat role"))
                self.assertIn("Neutral lookup does not count as assistance", instructions)
                box = self.ws.mailbox()
                (box / "syntax-cheatsheet.md").write_text("Accidental mailbox edit", encoding="utf-8")
                call(self.ws, "stage", lid)
                self.assertEqual((box / "syntax-cheatsheet.md").read_bytes(), SHEET.encode())
                self.assertEqual(expected, {p.name: p.read_bytes() for p in packet.iterdir()})
                call(self.ws, "abandon", lid, "Synthetic test completed")

    def test_invalid_coding_spec_leaves_pending_packet_and_mailbox_intact(self):
        prepared = call(self.ws, "prepare", "coding", self.lesson_spec(), "2026-10-27")
        box = self.ws.mailbox()
        before = {p.name: p.read_bytes() for p in box.iterdir()}
        value = self.lesson_spec()
        value.pop("syntax_cheatsheet")
        with self.assertRaisesRegex(ValueError, "require nonempty"):
            call(self.ws, "prepare", "coding", value, "2026-10-27",
                 replace_lesson=prepared["lesson_id"], decision="Synthetic replacement")
        self.assertEqual(before, {p.name: p.read_bytes() for p in box.iterdir()})
        self.assertEqual(self.ws.state["lessons"][prepared["lesson_id"]]["status"], "prepared")

    def test_noncoding_and_legacy_packets_omit_reference(self):
        for coding in (None, False):
            value = self.lesson_spec()
            value.pop("syntax_cheatsheet")
            if coding is None:
                value.pop("coding")
            else:
                value["coding"] = coding
            result = call(self.ws, "prepare", "coding", value, "2026-10-27")
            self.assertFalse((self.ws.mailbox() / "syntax-cheatsheet.md").exists())
            call(self.ws, "abandon", result["lesson_id"], "Synthetic test completed")

    def test_reference_requires_explicit_boolean_and_coding_scope(self):
        for value in ({"coding": "yes"}, {"coding": True},
                      {"coding": True, "syntax_cheatsheet": "  "},
                      {"coding": False, "syntax_cheatsheet": SHEET}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                syntax_reference.prepare(value)
