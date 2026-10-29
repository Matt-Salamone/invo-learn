"""Read original-format returns after cutover without reopening retired checkouts."""
import copy
import json

from .contracts import require
from .engine import atomic, digest, read_json
from .legacy import read_snapshot


def verify_originals(ws, origin=None):
    migration = ws.state.get("migration", {})
    if not migration.get("late_origins"):
        return
    saved = migration.get("source_receipt", {})
    require(saved.get("path") and saved.get("sha256"), "activation lacks a verified original archive receipt")
    path = ws.path(saved["path"])
    require(digest(path.read_bytes()) == saved["sha256"], "original archive receipt checksum changed")
    receipt = read_json(path)
    for key, source in receipt["origins"].items():
        if origin is not None and origin != key:
            continue
        archive = ws.path(source["archive"])
        original_state = archive / ".invo/state.json"
        expected = source["files"].get(".invo/state.json")
        require(expected is not None and digest(original_state.read_bytes()) == expected["sha256"], "original archive state checksum changed")
        snapshot = read_snapshot(archive)
        # Check all registered context, instructions and returns, rather than
        # repeatedly hashing unrelated archived dependency/working directories.
        for reference in snapshot.artifact_references():
            relative = reference["path"]
            expected = source["files"].get(relative)
            require(expected is not None and digest(snapshot.path(relative).read_bytes()) == expected["sha256"],
                    "original archive artifact checksum changed: " + relative)


def ingest(ws, obj, raw_path, today):
    migration = ws.state.get("migration", {})
    if migration.get("status") != "active":
        return None
    origin, retired = None, None
    origins = migration.get("late_origins", {})
    for key, source in origins.items():
        if source["kind"] == "assignment" and obj.get("assignment_id") == source["origin"]["id"]:
            origin = key
            break
    if origin is None:
        for session in migration.get("reconciliation", {}).get("sessions", {}).values():
            if session["kind"] == "course" and session["packet_id"] == obj.get("lesson_id"):
                origin, retired = session["origin_key"], session
                break
    if origin is None:
        return None
    verify_originals(ws, origin)
    source = origins[origin]
    if retired is not None:
        require(retired["resolution"] in ("report", "waiver"), "late return has no reconciled original checkout")
    snapshot = read_snapshot(ws.path(source["archive"])) if source["kind"] == "assignment" else read_snapshot(ws.root)
    inspected = snapshot.inspect_report(raw_path, today)
    require(inspected["status"] == "associated", "late original return is not associated: " + inspected.get("reason", "invalid original context"))
    require(inspected["report"] == obj, "late raw return differs from parsed original")
    canonical = digest(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode())
    hid = "historical-" + digest((origin + ":" + canonical).encode())[:20]
    existing = ws.state.get("historical_reports", {}).get(hid)
    if existing:
        require(existing["sha256"] == canonical, "historical return identity conflict")
        return {"status": "duplicate", "report_id": hid, "historical": True, "credit_applied": False}
    relative = "reports/historical/" + hid + ".json"
    require(not ws.path(relative).exists(), "unregistered historical archive must be reviewed before reuse")
    atomic(ws.path(relative), obj)
    association = migration["associations"][origin]
    tid = retired["track_id"] if retired else association["track_id"]
    ws.state.setdefault("historical_reports", {})[hid] = {
        "sha256": canonical, "raw_sha256": digest(raw_path.read_bytes()),
        "raw_path": raw_path.relative_to(ws.root).as_posix(), "path": relative,
        "origin_key": origin, "context": inspected["context"], "track_id": tid,
        "original_report_id": obj.get("report_id"), "report": copy.deepcopy(obj),
        "credit_applied": False, "qualification": "Historical original return; no pending session reopened or learning credit applied"}
    ws.save("historical-return-preserved", {"report_id": hid, "origin_key": origin})
    return {"status": "historical", "report_id": hid, "track_id": tid, "path": relative,
            "raw_path": raw_path.relative_to(ws.root).as_posix(), "credit_applied": False}


def verify(ws):
    verify_originals(ws)
    for saved in ws.state.get("historical_reports", {}).values():
        raw = ws.path(saved["raw_path"]).read_bytes()
        archived = read_json(ws.path(saved["path"]))
        require(digest(raw) == saved["raw_sha256"] and archived == saved["report"], "historical original return bytes changed")
        require(digest(json.dumps(archived, sort_keys=True, ensure_ascii=False).encode()) == saved["sha256"],
                "historical return canonical checksum changed")
