"""Actual-return reconciliation and explicit missing-progress waivers on private stages."""
import copy
import json
from pathlib import Path

from .contracts import fields, require, string
from .engine import Workspace, atomic, atomic_bytes, digest, no_links
from .legacy import ASSIGNMENT_CONTEXT, read_snapshot
from .migration import save_rehearsal, stage_locked, stage_path, verify_rehearsal


REMINDER = ("Collect an in-progress report from every checked-out main lesson chat. "
            "Missing returns require an explicit recorded acceptance of lost unreported progress; "
            "a waiver preserves existing work and never supplies missing answers.")


def _ledger(root, manifest):
    ledger = copy.deepcopy(manifest.get("reconciliation", {}))
    ledger.setdefault("sessions", {})
    ledger.setdefault("returns", {})
    ledger.setdefault("waivers", {})
    ledger.setdefault("fresh_study", {})
    ledger.setdefault("integrity_problems", [])
    for origin, source in manifest["sources"].items():
        snapshot = read_snapshot(stage_path(root, source["snapshot"]))
        require(not snapshot.integrity_problems(), "preserved original artifacts or associations are damaged")
        if snapshot.kind == "assignment" and snapshot.state.get("active_packet"):
            active = snapshot.state["active_packet"]
            require(active in snapshot.packets and snapshot.packets[active].get("status") == "outstanding",
                    "original assignment active packet association is broken")
        for key, packet in snapshot.packets.items():
            pending = "prepared" if snapshot.kind == "course" else "outstanding"
            if packet.get("status") != pending:
                continue
            sid = origin + ":" + key
            if snapshot.kind == "course":
                require(key == packet.get("id"), "original lesson identity is inconsistent")
                context = {"lesson_id": key, "track_id": packet["track_id"],
                           "map_revision": packet.get("map_revision")}
                tid = packet["track_id"]
            else:
                require(key == packet.get("packet_id"), "original packet identity is inconsistent")
                context = {field: packet[field] for field in ASSIGNMENT_CONTEXT}
                tid = source["track_id"]
            initial = {"origin_key": origin, "packet_id": key, "kind": snapshot.kind,
                       "context": context, "track_id": tid, "objective_ids": packet.get("objective_ids", []),
                       "status": "awaiting-return", "resolution": None, "session_status": "in-progress"}
            prior = ledger["sessions"].get(sid)
            require(prior is None or all(prior[field] == initial[field] for field in
                    ("origin_key", "packet_id", "kind", "context", "track_id", "objective_ids")),
                    "recorded checkout identity differs from immutable source")
            ledger["sessions"].setdefault(sid, initial)
    return ledger


def _summary(ledger):
    ledger["integrity_problems"] = [{"return_id": key, "reason": record["reason"]}
        for key, record in ledger["returns"].items()
        if record["status"] != "associated" and not record.get("repaired_by")]
    missing = [sid for sid, session in ledger["sessions"].items() if session["resolution"] is None]
    eligible = not missing and not ledger["integrity_problems"]
    reminder = (REMINDER if missing else "Resolve the recorded integrity problems before activation."
                if ledger["integrity_problems"] else "All inventoried checkouts are resolved. Continue with projection and activation; recorded waivers require fresh study.")
    ledger.update(status="reconciled" if eligible else "blocked", eligible=eligible, missing=missing, reminder=reminder)
    return ledger


def checkouts(stage):
    root = no_links(stage).resolve()
    require(not (root / "migration.lock").exists(), "migration stage busy; retry after its writer finishes")
    verified = verify_rehearsal(root)
    return _summary(_ledger(root, verified["manifest"]))


def _persist(root, manifest, ws, ledger):
    _summary(ledger)
    manifest["reconciliation"] = ledger
    ws.state["migration"]["reconciliation"] = copy.deepcopy(ledger)
    atomic(ws.state_path, ws.state)
    ws.render()
    save_rehearsal(root, manifest)
    return copy.deepcopy(ledger)


def _selection(selection, manifest):
    fields(selection, ("origin_key", "file"), ("repair_of", "repair_note"))
    require(selection["origin_key"] in manifest["sources"], "return selects an unknown source origin")
    string(selection["file"], "actual returned report path")
    if "repair_of" in selection:
        string(selection["repair_of"], "rejected raw return checksum")
        string(selection.get("repair_note"), "actual evidence-backed repair note")
    else:
        require("repair_note" not in selection, "repair note needs repair_of")


def _waiver(selection, ledger):
    fields(selection, ("origin_key", "packet_id", "accept_lost_progress", "reason"))
    string(selection["origin_key"], "waiver source origin")
    string(selection["packet_id"], "waiver checkout identity")
    require(selection["accept_lost_progress"] is True, "explicit acceptance of lost unreported progress is required")
    string(selection["reason"], "actual learner loss-acceptance record")
    require(selection["origin_key"] + ":" + selection["packet_id"] in ledger["sessions"],
            "waiver must identify an inventoried original checkout")


def _apply_waivers(manifest, ws, ledger):
    if _summary(ledger)["integrity_problems"]:
        return  # Loss acceptance cannot override a broken or malformed actual return.
    for wid, waiver in ledger["waivers"].items():
        sid = waiver["origin_key"] + ":" + waiver["packet_id"]
        session = ledger["sessions"][sid]
        if session["resolution"] is not None:
            continue
        session.update(status="retired-incomplete", resolution="waiver", waiver_id=wid,
                       session_status="in-progress", lost_unreported_progress=True)
        if session["kind"] == "course":
            lesson = ws.state["lessons"][session["packet_id"]]
            lesson.update(status="paused", session_status="in-progress",
                          migration_retirement={"waiver_id": wid, "reason": waiver["reason"]})
        else:
            association = manifest["associations"][session["origin_key"]]
            assignment = ws.state["tracks"][association["track_id"]]["assignments"][association["assignment_id"]]
            assignment["legacy_context"].setdefault("retired_checkouts", {})[session["packet_id"]] = copy.deepcopy(session)
        need = {"action": "fresh-assessment-or-relearning", "status": "pending",
                "origin_key": session["origin_key"], "packet_id": session["packet_id"],
                "track_id": session["track_id"], "objective_ids": session["objective_ids"],
                "reason": "Unreported progress was explicitly waived; establish current understanding with a fresh check or relearning"}
        association = manifest["associations"][session["origin_key"]]
        if "assignment_id" in association:
            need["assignment_id"] = association["assignment_id"]
        ledger["fresh_study"].setdefault(sid, need)


def _record_assignment_return(ws, manifest, origin, record):
    association = manifest["associations"][origin]
    assignment = ws.state["tracks"][association["track_id"]]["assignments"][association["assignment_id"]]
    section = "supplemental_returns" if record["report_type"] == "side-chat" else "reconciled_returns"
    assignment["legacy_context"].setdefault(section, {}).setdefault(record["canonical_sha256"], {
        "report": copy.deepcopy(record["report"]), "path": record["path"],
        "raw_sha256": record["raw_sha256"], "outcome": record["outcome"],
        "session_status": record.get("session_status", "in-progress")})


def _mark_repair(ledger, selection, record):
    if "repair_of" not in selection:
        return
    old = ledger["returns"][selection["origin_key"] + ":" + selection["repair_of"]]
    old.update(repaired_by=record["raw_sha256"], repair_note=selection["repair_note"])
    record.update(repair_of=selection["repair_of"], repair_note=selection["repair_note"])


def _course_ingest(ws, raw, today, record):
    before = copy.deepcopy(ws.state)
    try:
        return ws.ingest(raw.decode("utf-8-sig"), today)
    except (ValueError, TypeError, KeyError) as exc:
        # The ordinary ingester retains raw input and its rejected-import ledger.
        # Preserve prior changes from this reconciliation batch in memory too.
        ws.state = before
        record.update(status="invalid", outcome="rejected", reason=str(exc))
        return None


def _accept_return(root, manifest, ws, ledger, selection, raw, today):
    origin = selection["origin_key"]
    checksum = digest(raw)
    rid = origin + ":" + checksum
    if rid in ledger["returns"]:
        return  # An exact retry does not add events, observations or new history.
    relative = "migration-records/" + manifest["id"] + "/returns/" + checksum + ".txt"
    path = ws.path(relative)
    if not path.exists():
        atomic_bytes(path, raw)
    require(digest(path.read_bytes()) == checksum, "preserved return checksum mismatch")
    snapshot = read_snapshot(stage_path(root, manifest["sources"][origin]["snapshot"]))
    inspected = snapshot.inspect_report(path, today)
    record = {key: copy.deepcopy(value) for key, value in inspected.items()
              if key not in ("raw_path", "read_only", "credit_applied", "origin")}
    record.update(path=relative, origin_key=origin, raw_sha256=checksum, outcome="rejected")
    ledger["returns"][rid] = record
    if inspected["status"] != "associated":
        return
    report = inspected["report"]
    record["canonical_sha256"] = digest(json.dumps(report, sort_keys=True, ensure_ascii=False).encode())
    record["report_type"] = report.get("report_type", "lesson")
    packet_id = report["lesson_id" if snapshot.kind == "course" else "packet_id"]
    record["packet_id"] = packet_id
    sid = origin + ":" + packet_id
    session = ledger["sessions"].get(sid)
    prior = next((other for key, other in ledger["returns"].items() if key != rid
        and other.get("origin_key") == origin and other.get("canonical_sha256") == record["canonical_sha256"]
        and other["status"] == "associated"), None)
    if prior:
        record.update(outcome="duplicate", duplicate_of=prior["raw_sha256"])
        _mark_repair(ledger, selection, record)
        return
    partial = report.get("session_status", "in-progress")
    record["session_status"] = partial
    if record["report_type"] == "side-chat":
        record["outcome"] = "supplemental"
        if snapshot.kind == "course":
            if _course_ingest(ws, raw, today, record) is None:
                return
    elif session is None or session["resolution"] is not None:
        record["outcome"] = "historical"
    else:
        record["outcome"] = "preserved"
        if snapshot.kind == "course":
            result = _course_ingest(ws, raw, today, record)
            if result is None:
                return
            record["outcome"] = "applied" if result["status"] == "imported" else "historical"
            lesson = ws.state["lessons"][packet_id]
            lesson["status"] = "reported" if partial == "completed" and result["status"] == "imported" else "paused"
            lesson["session_status"] = partial if result["status"] == "imported" else "in-progress"
        session.update(status="reconciled-completed" if partial == "completed" else "retired-incomplete",
                       resolution="report", session_status=partial, report_sha256=record["canonical_sha256"],
                       return_id=rid, completion_inference="explicit" if "session_status" in report else "legacy completion unknown; kept incomplete")
    if snapshot.kind == "assignment":
        _record_assignment_return(ws, manifest, origin, record)
    _mark_repair(ledger, selection, record)


def reconcile(stage, payload, today):
    fields(payload, ("reports",), ("waivers",))
    require(isinstance(payload["reports"], list) and isinstance(payload.get("waivers", []), list),
            "reports and waivers must be lists")
    with stage_locked(stage) as root:
        verified = verify_rehearsal(root)
        manifest = verified["manifest"]
        ledger = _ledger(root, manifest)
        ws = Workspace(verified["workspace"])
        incoming = []
        for selection in payload["reports"]:
            _selection(selection, manifest)
            raw = no_links(Path(selection["file"])).read_bytes()
            if "repair_of" in selection:
                prior = ledger["returns"].get(selection["origin_key"] + ":" + selection["repair_of"])
                require(prior is not None and prior["status"] != "associated", "repair must link a preserved rejected actual return")
                require(not prior.get("repaired_by") or prior["repaired_by"] == digest(raw),
                        "rejected return already has a different preserved repair")
                require(selection["repair_of"] != digest(raw), "repair must preserve a different original representation")
            incoming.append((selection, raw))
        for waiver in payload.get("waivers", []):
            _waiver(waiver, ledger)
        for selection, raw in incoming:
            _accept_return(root, manifest, ws, ledger, selection, raw, today)
        for waiver in payload.get("waivers", []):
            wid = digest(json.dumps(waiver, sort_keys=True, ensure_ascii=False).encode())
            ledger["waivers"].setdefault(wid, copy.deepcopy(waiver))
        _apply_waivers(manifest, ws, ledger)
        return _persist(root, manifest, ws, ledger)
