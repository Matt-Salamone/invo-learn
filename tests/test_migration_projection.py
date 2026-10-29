"""Conservative legacy projection through the installed command seam S1."""
import copy
import hashlib
import json
import unittest

import test_migration
from examples.worked_example import map_spec
from test_legacy import hashes, write_json


class MigrationProjectionTests(unittest.TestCase):
    setUp = test_migration.MigrationRehearsalTests.setUp
    write = test_migration.MigrationRehearsalTests.write
    cli = test_migration.MigrationRehearsalTests.cli
    make_assignment = test_migration.MigrationRehearsalTests.make_assignment
    plan = test_migration.MigrationRehearsalTests.plan

    def evidence(self):
        state_path = self.assignment / ".invo/state.json"
        state = json.loads(state_path.read_text())
        packet = next(iter(state["packets"].values()))
        observations = [
            {"criterion": "Solve equations", "question": "Solve 2x+3=11", "learner_response": "x=4",
             "assistance": "none", "evidence_level": "independent"},
            {"criterion": "Explain inverse operations", "question": "Why subtract on both sides?", "learner_response": "Preserves equality",
             "assistance": "Tutor supplied a requested worked step", "evidence_level": "assisted"},
            {"criterion": "Explain a substitution check", "question": "Why check the result?", "learner_response": "It checks the original equality",
             "assistance": "none", "evidence_level": "independent"}]
        report = {key: packet[key] for key in ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")}
        report.update(observations=observations, remaining_gaps=[], suspected_errors=[])
        raw = self.assignment / "reports/legacy-main.json"
        write_json(raw, report)
        state["imports"] = {"import-original": {"id": "import-original", "raw_path": "reports/legacy-main.json",
            "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "outcome": "applied", "packet_id": packet["packet_id"]}}
        state["evidence"] = [{"import_id": "import-original", "lesson_id": packet["lesson_id"],
            "solution_revision": packet["solution_revision"], "observations": copy.deepcopy(observations), "remaining_gaps": [], "qualification": {}}]
        packet["status"] = "completed"
        state["active_packet"] = None
        write_json(state_path, state)
        return observations

    def staged_status(self):
        return self.cli("--workspace", self.stage / "workspace", "status")

    def test_unmapped_originals_schedule_fresh_study_without_inventing_credit_or_manual_mapping_queue(self):
        observations = self.evidence()
        original_course = self.cli("status")["tracks"]["math"]["objectives"]["solve"]
        course_before, assignment_before = hashes(self.root), hashes(self.assignment)
        self.cli("migration-rehearse", self.write(self.plan()))
        result = self.cli("migration-project", self.stage)
        self.assertEqual(result["status"], "projected")
        status = self.staged_status()
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"], original_course)
        records = status["tracks"]["math"]["legacy_evidence"]
        self.assertEqual([record["observation"] for record in records], observations)
        self.assertTrue(all(record["objective_ids"] == [] and record["credit"] == "none" for record in records))
        actions = [entry for entry in status["work_queue"] if entry.get("study_need_id")]
        self.assertEqual(len(actions), 3)
        self.assertEqual({entry["action"] for entry in actions}, {"fresh-demonstration", "relearn-legacy-topic"})
        self.assertTrue(all("mapping" not in entry["action"] and entry["material_ids"] for entry in actions))
        self.assertTrue(all(entry["due_on"] == "2026-10-29" for entry in actions))
        self.assertEqual(hashes(self.root), course_before)
        self.assertEqual(hashes(self.assignment), assignment_before)
        before = hashes(self.stage)
        self.assertEqual(self.cli("migration-project", self.stage)["status"], "already-projected")
        self.assertEqual(hashes(self.stage), before)

    def test_actual_legacy_side_help_is_preserved_with_timing_and_not_upgraded(self):
        observations = self.evidence()
        state_path = self.assignment / ".invo/state.json"
        state = json.loads(state_path.read_text())
        main = json.loads((self.assignment / "reports/legacy-main.json").read_text())
        side = {key: main[key] for key in ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")}
        side.update(report_type="side-chat", report_id="side-original", discussions=[{
            "question": "Explain a check", "explanation": "Actual explanation", "source_reference": "Synthetic governing material"}],
            remaining_questions=[], assessment_help=[
                {"question": observations[0]["question"], "help": "Post-answer explanation", "timing": "after-answer"},
                {"question": observations[2]["question"], "help": "Requested worked solution before assessed response", "timing": "unknown"}])
        raw = self.assignment / "reports/legacy-side.json"
        write_json(raw, side)
        state["imports"]["import-side"] = {"id": "import-side", "raw_path": "reports/legacy-side.json", "packet_id": main["packet_id"],
            "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "outcome": "supplemental-recorded"}
        state["supplemental_reports"] = {"side-original": {"import_id": "import-side", "packet_id": main["packet_id"],
            "raw_path": "reports/legacy-side.json", "report": side, "evidence_level": "covered"}}
        write_json(state_path, state)
        before = hashes(self.assignment)
        self.cli("migration-rehearse", self.write(self.plan()))
        self.cli("migration-project", self.stage)
        records = self.staged_status()["tracks"]["math"]["legacy_evidence"]
        self.assertEqual([record["observation"] for record in records], observations)
        self.assertEqual([record["effective_level"] for record in records], ["independent", "assisted", "assisted"])
        self.assertEqual(records[0]["assistance"][0]["timing"], "after-answer")
        self.assertEqual(records[2]["assistance"][0]["help"], "Requested worked solution before assessed response")
        self.assertEqual(hashes(self.assignment), before)
        self.assertEqual(self.cli("migration-status", self.stage)["manifest"]["projection"]["status"], "projected")

    def test_justified_links_add_coverage_only_and_preserve_unaffected_course_reviews(self):
        mapping = map_spec(self.material["id"], [
            ("solve", "Solve equations", "skill", "whole file", []),
            ("explain", "Explain equality", "concept", "whole file", [])])
        proposed = self.cli("propose-map", "math", self.write(mapping))
        self.cli("accept-map", "math", proposed["proposal_id"], "--approval", "Actual synthetic scope approval")
        self.evidence()
        original = self.cli("status")["tracks"]["math"]["objectives"]["solve"]
        self.cli("migration-rehearse", self.write(self.plan()))
        self.cli("migration-project", self.stage)
        records = self.staged_status()["tracks"]["math"]["legacy_evidence"]
        links = {"links": [{"observation_id": record["observation_id"], "objective_id": "explain",
                            "reason": "Compared the actual explanation with the accepted equality objective and governing requirements"}
                           for record in records[1:]]}
        self.cli("migration-project", self.stage, "--links", self.write(links))
        status = self.staged_status()
        self.assertEqual(status["tracks"]["math"]["objectives"]["solve"], original)
        objective = status["tracks"]["math"]["objectives"]["explain"]
        self.assertEqual(objective["coverage"], "covered")
        self.assertEqual(objective["understanding"], "unassessed")
        self.assertEqual(objective["retention"], "unassessed")
        self.assertIsNone(objective["review"])
        records = status["tracks"]["math"]["legacy_evidence"]
        self.assertEqual([record["credit"] for record in records], ["none", "covered", "covered"])
        self.assertEqual(records[0]["objective_ids"], [])
        actions = [entry for entry in status["work_queue"] if entry.get("study_need_id")]
        self.assertEqual([action["objective_ids"] for action in actions], [[], ["explain"], ["explain"]])
        before = hashes(self.stage)
        self.assertEqual(self.cli("migration-project", self.stage)["status"], "already-projected")
        self.assertEqual(hashes(self.stage), before)
        bad = {"links": [{"observation_id": records[0]["observation_id"], "objective_id": "invented", "reason": "No accepted objective exists"}]}
        self.cli("migration-project", self.stage, "--links", self.write(bad), ok=False)
        self.assertEqual(hashes(self.stage), before)

    def test_reconciled_actual_returns_refresh_projection_and_metadata_retries_keep_one_observation(self):
        self.cli("migration-rehearse", self.write(self.plan()))
        self.cli("migration-project", self.stage)
        manifest = self.cli("migration-status", self.stage)["manifest"]
        key = next(key for key, source in manifest["sources"].items() if source["kind"] == "assignment")
        source = json.loads((self.assignment / ".invo/state.json").read_text())
        packet = source["packets"]["packet-original"]
        report = {key: packet[key] for key in ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")}
        observation = {"criterion": "Correct reasoning", "question": "Why subtract both sides?", "learner_response": "To preserve equality",
                       "assistance": "Actual requested worked example", "evidence_level": "assisted"}
        report.update(observations=[observation], remaining_gaps=[], suspected_errors=[])
        request = {"reports": [{"origin_key": key, "file": str(self.write(report))}], "waivers": []}
        self.cli("migration-reconcile", self.stage, self.write(request))
        self.assertFalse(self.cli("migration-status", self.stage)["projection_current"])
        result = self.cli("migration-project", self.stage)
        self.assertEqual(result["status"], "projected")
        self.assertTrue(self.cli("migration-status", self.stage)["projection_current"])
        records = self.staged_status()["tracks"]["math"]["legacy_evidence"]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["observation"], observation)
        self.assertEqual(records[0]["credit"], "none")
        report["session_status"] = "in-progress"
        request["reports"][0]["file"] = str(self.write(report))
        self.cli("migration-reconcile", self.stage, self.write(request))
        self.cli("migration-project", self.stage)
        records = self.staged_status()["tracks"]["math"]["legacy_evidence"]
        self.assertEqual(len(records), 1)
        self.assertEqual(len(records[0]["provenance"]), 2)
        self.assertEqual(records[0]["credit"], "none")

    def test_late_post_waiver_observation_stays_historical_even_with_a_justified_topic_link(self):
        self.cli("migration-rehearse", self.write(self.plan()))
        manifest = self.cli("migration-status", self.stage)["manifest"]
        key = next(key for key, source in manifest["sources"].items() if source["kind"] == "assignment")
        self.cli("migration-reconcile", self.stage, self.write({"reports": [], "waivers": [{
            "origin_key": key, "packet_id": "packet-original", "accept_lost_progress": True,
            "reason": "Actual synthetic learner accepts loss of this checkout's unreported progress"}]}))
        packet = json.loads((self.assignment / ".invo/state.json").read_text())["packets"]["packet-original"]
        report = {field: packet[field] for field in ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")}
        report.update(observations=[{"criterion": "Correct reasoning", "question": "Solve 2x+3=11", "learner_response": "x=4",
            "assistance": "none", "evidence_level": "independent"}], remaining_gaps=[], suspected_errors=[])
        self.cli("migration-reconcile", self.stage, self.write({"reports": [{"origin_key": key, "file": str(self.write(report))}], "waivers": []}))
        self.cli("migration-project", self.stage)
        record = self.staged_status()["tracks"]["math"]["legacy_evidence"][0]
        link = {"links": [{"observation_id": record["observation_id"], "objective_id": "solve", "reason": "Actual equation task concerns the accepted solve objective"}]}
        self.cli("migration-project", self.stage, "--links", self.write(link))
        record = self.staged_status()["tracks"]["math"]["legacy_evidence"][0]
        self.assertEqual(record["provenance"][0]["outcome"], "historical")
        self.assertEqual(record["credit"], "none")
        self.assertFalse(record["coverage_eligible"])
