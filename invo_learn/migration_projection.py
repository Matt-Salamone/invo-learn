"""Conservative, explicit projection of preserved historical assignment evidence."""
import copy
import json

from .contracts import date, fields, require, string
from .engine import Workspace, atomic, atomic_bytes, digest, read_json
from .legacy import read_snapshot
from .migration import save_rehearsal, stage_locked, stage_path, verify_rehearsal


REPORT_PATH = ".invo-learn/migration-projection.json"
NO_HELP = {"none", "no help", "no assistance", "unaided", "independent"}


def canonical(report):
    return digest(json.dumps(report, sort_keys=True, ensure_ascii=False).encode())


def supplemental_help(snapshot):
    result = []
    for sid, saved in snapshot.state.get("supplemental_reports", {}).items():
        imported = snapshot.state.get("imports", {}).get(saved.get("import_id"), {})
        path = saved.get("raw_path") or imported.get("raw_path")
        if path:
            inspected = snapshot.inspect_report(snapshot.path(path))
            if inspected.get("status") != "associated":
                continue
            report, context = inspected["report"], inspected["context"]
        else:
            report = saved.get("report", {})
            try:
                context, _, packet = snapshot.associate_report(report)
                snapshot.validate_report(report, packet, None)
            except (ValueError, TypeError, KeyError):
                continue
        for help_item in report.get("assessment_help", []):
            result.append({"source": "side-chat", "report_id": sid, "packet_context": context,
                           "raw_path": path, **copy.deepcopy(help_item)})
    return result


def collect(ws, manifest, stage):
    """Read actual preserved observations; never infer identity from their prose."""
    records = {}
    for key, source in manifest["sources"].items():
        if source["kind"] != "assignment":
            continue
        association = manifest["associations"][key]
        tid, aid = association["track_id"], association["assignment_id"]
        snapshot = read_snapshot(stage_path(stage, source["snapshot"]))
        imports = snapshot.state.get("imports", {})
        help_records = supplemental_help(snapshot)
        for event_index, event in enumerate(snapshot.state.get("evidence", [])):
            iid = event.get("import_id")
            imported = imports.get(iid, {})
            inspected = snapshot.inspect_report(snapshot.path(imported["raw_path"])) if imported.get("raw_path") else {}
            report = inspected.get("report", {})
            associated = inspected.get("status") == "associated"
            for index, observation in enumerate(event.get("observations", [])):
                raw_indices = [n for n, observed in enumerate(report.get("observations", [])) if observed == observation]
                exact = associated and len(raw_indices) == 1
                identity = (canonical(report) + ":" + str(raw_indices[0])) if exact else str(iid or event_index) + ":" + str(index)
                oid = "legacy-observation-" + digest((key + ":" + identity).encode())[:20]
                record = records.setdefault(oid, {"observation_id": oid, "origin_key": key,
                    "track_id": tid, "assignment_id": aid, "migration_id": manifest["id"],
                    "observation": copy.deepcopy(observation), "association_valid": exact, "provenance": [],
                    "assistance": [], "objective_ids": [], "credit": "none"})
                record["provenance"].append({"state_path": association["archive"] + "/.invo/state.json",
                    "event_index": event_index, "observation_index": index, "import_id": iid,
                    "raw_path": imported.get("raw_path"), "packet_context": inspected.get("context")})
                level = observation.get("evidence_level", "covered")
                if observation.get("assistance", "").strip().lower() not in NO_HELP:
                    level = "assisted"
                matches = [copy.deepcopy(help_item) for help_item in help_records
                           if help_item["packet_context"] == inspected.get("context")
                           and help_item["question"] == observation.get("question")]
                record["assistance"] = matches
                if any(help_item["timing"] != "after-answer" for help_item in matches):
                    level = "assisted"
                record["effective_level"] = level
    return list(records.values())


def input_sha256(ws, manifest, stage):
    return canonical(collect(ws, manifest, stage))


def projection_current(ws, manifest, stage):
    projection = manifest.get("projection", {})
    return (projection.get("status") == "projected"
            and projection.get("input_sha256") == input_sha256(ws, manifest, stage))


def next_actions(ws):
    return [copy.deepcopy(action) for action in ws.state.get("migration", {}).get("legacy_study_actions", {}).values()
            if action.get("status") == "pending"]


def justified_links(ws, records, prior, supplied):
    known = {record["observation_id"]: record for record in records}
    result = {(item["observation_id"], item["objective_id"]): copy.deepcopy(item) for item in prior}
    if supplied is None:
        return list(result.values())
    fields(supplied, ("links",))
    require(isinstance(supplied["links"], list), "projection links must be a list")
    for item in supplied["links"]:
        fields(item, ("observation_id", "objective_id", "reason"))
        require(item["observation_id"] in known, "projection link references unknown original observation")
        record = known[item["observation_id"]]
        require(item["objective_id"] in ws.track(record["track_id"])["objectives"], "projection link needs an accepted objective in the assignment's course")
        string(item["reason"], "actual justification for the objective association")
        key = item["observation_id"], item["objective_id"]
        require(key not in result or result[key] == item, "prior association justification differs; preserve this stage and rehearse a corrected mapping separately")
        result[key] = copy.deepcopy(item)
    return list(result.values())


def project_course_coverage(ws, tid):
    track = ws.track(tid)
    for record in track.get("legacy_evidence", []):
        if record["credit"] == "covered":
            for oid in record["objective_ids"]:
                track["objectives"][oid]["coverage"] = "covered"


def project(stage, links=None, today=None):
    date(today)
    with stage_locked(stage) as root:
        checked = verify_rehearsal(root)
        manifest = checked["manifest"]
        require(not manifest.get("activated"), "project the inactive rehearsal before activation")
        ws = Workspace(checked["workspace"])
        records = collect(ws, manifest, root)
        fingerprint = canonical(records)
        prior = manifest.get("projection", {})
        associations = justified_links(ws, records, prior.get("links", []), links)
        request_digest = canonical({"input": fingerprint, "links": associations})
        if prior.get("status") == "projected" and prior.get("request_sha256") == request_digest:
            return {"status": "already-projected", "migration_id": manifest["id"],
                    "observations": len(records), "study_needs": len(ws.state["migration"]["legacy_study_actions"])}
        actions = {}
        for record in records:
            matched = [item for item in associations if item["observation_id"] == record["observation_id"]]
            record["objective_ids"] = [item["objective_id"] for item in matched]
            record["association_reasons"] = [item["reason"] for item in matched]
            if matched and record["association_valid"]:
                record["credit"] = "covered"
            assignment = ws.track(record["track_id"])["assignments"][record["assignment_id"]]
            need = "study-" + record["observation_id"][len("legacy-observation-"):]
            due = ws.state["migration"].get("legacy_study_actions", {}).get(need, {}).get("due_on", today)
            actions[need] = {"study_need_id": need, "status": "pending", "due_on": due,
                "action": "fresh-demonstration" if record["effective_level"] == "independent" else "relearn-legacy-topic",
                "track_id": record["track_id"], "assignment_id": record["assignment_id"],
                "objective_ids": record["objective_ids"][:], "material_ids": assignment["spec"]["material_ids"],
                "observation_id": record["observation_id"], "criterion": record["observation"].get("criterion"),
                "reason": "Use governing requirements for a fresh check or relearning; historical labels do not prove fresh independent understanding or retention."}
        for tid, track in ws.state["tracks"].items():
            retained = [item for item in track.get("legacy_evidence", []) if item.get("migration_id") != manifest["id"]]
            track["legacy_evidence"] = retained + [copy.deepcopy(item) for item in records if item["track_id"] == tid]
            project_course_coverage(ws, tid)
        ws.state["migration"]["legacy_study_actions"] = actions
        summary = {"status": "projected", "input_sha256": fingerprint, "request_sha256": request_digest,
                   "links": associations, "observations": len(records), "study_needs": len(actions),
                   "path": REPORT_PATH, "projected_on": prior.get("projected_on", today)}
        ws.state["migration"]["projection"] = copy.deepcopy(summary)
        manifest["projection"] = copy.deepcopy(summary)
        report = {"migration_id": manifest["id"], "policy": "coverage requires justified links; legacy assignment observations never establish independent mastery or delayed retention",
                  "observations": records, "study_actions": actions}
        paths = (ws.state_path, ws.path(REPORT_PATH), root / "migration-manifest.json")
        require(not paths[1].exists() or prior.get("path") == REPORT_PATH, "projection artifact conflicts with unmanaged work")
        before = {path: path.read_bytes() if path.exists() else None for path in paths}
        try:
            atomic(paths[1], report)
            atomic(ws.state_path, ws.state)
            save_rehearsal(root, manifest)
        except BaseException:
            for path, data in before.items():
                if data is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_bytes(path, data)
            raise
        return {"status": "projected", "migration_id": manifest["id"], "observations": len(records),
                "study_needs": len(actions), "path": str(paths[1]), "activated": False}
