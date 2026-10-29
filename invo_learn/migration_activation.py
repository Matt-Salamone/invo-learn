"""Journaled activation into the existing workspace without replacing its Git history."""
import copy
import datetime as dt
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

from .contracts import date, require
from .engine import Workspace, atomic, atomic_bytes, digest, no_links, read_json, within
from .git_bytes import attribute_conflicts, protect, protected_paths
from .install import package, upgrade
from .legacy import read_snapshot
from .migration import INACTIVE_RUNNER, inventory, stage_locked, stage_path, verify_rehearsal
from .migration_projection import projection_current
from .migration_reconciliation import _ledger, _summary


PLAN = "activation/plan.json"
PROGRESS = "activation-progress.json"


def _metadata(data):
    return {"sha256": digest(data), "bytes": len(data)}


def _file(root, relative):
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute(), "activation file path must be relative")
    path = (root / relative).resolve()
    require(within(path, root) and path != root, "activation file path escapes its workspace")
    return no_links(path)


def _ordinary(tree):
    return {"files": {name: value for name, value in tree["files"].items()
                      if ".git" not in Path(name).parts and name != ".invo-learn/operation.lock"},
            "directories": [name for name in tree["directories"] if ".git" not in Path(name).parts]}


def _current(path):
    require(not path.exists() or path.is_file(), "activation file conflicts with a directory: " + str(path))
    return _metadata(path.read_bytes()) if path.is_file() else None


def _validate_gate(root, manifest, ws, today):
    require(projection_current(ws, manifest, root), "evidence projection is missing or stale; project current actual returns before activation")
    require(manifest.get("reconciliation") == ws.state["migration"].get("reconciliation"),
            "reconciliation ledger differs from canonical staged records")
    ledger = _summary(_ledger(root, manifest))
    require(ledger["eligible"] and ledger["status"] == "reconciled", "actual reports or explicit lost-progress waivers are still required")
    for key, record in ledger["returns"].items():
        raw = ws.path(record["path"]).read_bytes()
        require(digest(raw) == record["raw_sha256"], "saved actual return checksum changed")
        source = manifest["sources"][record["origin_key"]]
        inspected = read_snapshot(stage_path(root, source["snapshot"])).inspect_report(ws.path(record["path"]), today)
        if record["status"] == "associated":
            require(inspected["status"] == "associated" and inspected["report"] == record["report"],
                    "saved actual report association changed")
        else:
            repaired = ledger["returns"].get(record["origin_key"] + ":" + record.get("repaired_by", ""))
            require(repaired is not None and repaired["status"] == "associated", "invalid actual return has no verified repair")
    for session in ledger["sessions"].values():
        if session["resolution"] == "waiver":
            waiver = ledger["waivers"].get(session.get("waiver_id"), {})
            require(waiver.get("accept_lost_progress") is True and bool(waiver.get("reason", "").strip())
                    and waiver.get("origin_key") == session["origin_key"] and waiver.get("packet_id") == session["packet_id"],
                    "checkout retirement lacks its explicit loss-acceptance record")
        else:
            returned = ledger["returns"].get(session.get("return_id"), {})
            require(session["resolution"] == "report" and returned.get("status") == "associated"
                    and returned.get("report_type") == "lesson" and returned.get("packet_id") == session["packet_id"],
                    "checkout retirement lacks its actual main return")
    require(not ws.pending_lessons(), "unreconciled canonical checkout remains; activation cannot create multiple pending sessions")


def _attributes(candidate, destination, target):
    if not (destination / ".git").exists():
        return
    names = [name for name in protected_paths(candidate) if name in target["files"]]
    checked = subprocess.run(["git", "--git-dir", str(destination / ".git"), "--work-tree", str(candidate),
                              "-c", "core.bare=false", "check-attr", "--stdin", "-z", "text", "filter", "working-tree-encoding", "ident"],
                             input=b"\x00".join(name.encode() for name in names) + b"\x00", capture_output=True)
    require(checked.returncode == 0 and not attribute_conflicts(checked.stdout),
            "destination Git attributes conflict with exact migrated bytes; preserve and review custom rules")


def _prepare(root, manifest, source, today):
    ws = Workspace(stage_path(root, manifest["workspace"]))
    _validate_gate(root, manifest, ws, today)
    source, version, files, hashes = package(source)
    require("invo_learn/migration_activation.py" in files, "activation requires the current combined trusted package")
    candidate_relative = "activation/candidate-" + uuid.uuid4().hex
    candidate = stage_path(root, candidate_relative)
    shutil.copytree(ws.root, candidate)
    candidate_ws = Workspace(candidate)
    box_relative = Path(ws.state["mailbox"]).relative_to(ws.root)
    candidate_box = candidate / box_relative
    candidate_ws.state["mailbox"] = str(candidate_box)
    atomic(candidate_box / ".invo-mailbox.json", {"workspace_id": ws.state["workspace_id"], "path": str(candidate_box)})
    atomic(candidate_ws.state_path, candidate_ws.state)
    runner = manifest.get("inactive_runner", {})
    require((candidate / "learn.py").read_bytes() == INACTIVE_RUNNER, "inactive rehearsal runner guard changed")
    original_runner = stage_path(root, runner["original_path"]).read_bytes()
    require(digest(original_runner) == runner["original_sha256"], "frozen original runner checksum changed")
    with candidate_ws.locked():
        atomic_bytes(candidate / "learn.py", original_runner)
        installed = upgrade(candidate_ws, source)
        require(installed["status"] in ("upgraded", "already-current"), "current installed code requires a separate compatible migration")
        protect(candidate_ws, today)
        active_runner = (candidate / "learn.py").read_bytes()
        atomic_bytes(candidate / "learn.py", INACTIVE_RUNNER)
    destination = no_links(manifest["destination"]).resolve()
    final_state = copy.deepcopy(candidate_ws.state)
    final_state["mailbox"] = final_state["migration"]["intended_mailbox"]
    receipt_path = "migration-records/" + manifest["id"] + "/original-archives.json"
    receipt = {"migration_id": manifest["id"], "origins": {
        key: {"archive": manifest["associations"][key]["archive"],
              "files": _ordinary(value["inventory"])["files"]}
        for key, value in manifest["sources"].items() if value["kind"] == "assignment"}}
    require(not (candidate / receipt_path).exists(), "original archive receipt conflicts with existing work")
    atomic(candidate / receipt_path, receipt)
    final_state["migration"]["source_receipt"] = {"path": receipt_path, "sha256": digest((candidate / receipt_path).read_bytes())}
    final_state["migration"].update(status="active", activated_on=today, preservation_root=str(root),
        late_origins={key: {"kind": value["kind"], "origin": value["origin"],
                           "archive": manifest["associations"][key].get("archive")}
                      for key, value in manifest["sources"].items()})
    final_state["events"].append({"action": "migration-activated", "details": {"migration_id": manifest["id"]},
                                   "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    payloads = "activation/payloads-" + uuid.uuid4().hex
    atomic(stage_path(root, payloads + "/state.active.json"), final_state)
    applying_state = copy.deepcopy(final_state)
    applying_state["migration"]["status"] = "activating"
    atomic(stage_path(root, payloads + "/state.applying.json"), applying_state)
    atomic_bytes(stage_path(root, payloads + "/learn.py"), active_runner)
    target = _ordinary(inventory(candidate))
    overrides = {"state.json": payloads + "/state.applying.json", "learn.py": payloads + "/learn.py"}
    original_box = Path(final_state["mailbox"]).resolve()
    if within(original_box, destination):
        marker = (original_box.relative_to(destination) / ".invo-mailbox.json").as_posix()
        atomic(stage_path(root, payloads + "/mailbox-marker.json"), {"workspace_id": final_state["workspace_id"], "path": str(original_box)})
        overrides[marker] = payloads + "/mailbox-marker.json"
    else:
        prefix = box_relative.as_posix()
        target["files"] = {name: meta for name, meta in target["files"].items() if not (name == prefix or name.startswith(prefix + "/"))}
        target["directories"] = [name for name in target["directories"] if not (name == prefix or name.startswith(prefix + "/"))]
    for name, relative in overrides.items():
        target["files"][name] = _metadata(stage_path(root, relative).read_bytes())
    _attributes(candidate, destination, target)
    original = next(value for value in manifest["sources"].values() if value["kind"] == "course")
    baseline = _ordinary(original["inventory"])
    changes = []
    for name in sorted(set(baseline["files"]) | set(target["files"])):
        before, after = baseline["files"].get(name), target["files"].get(name)
        if before != after:
            changes.append({"path": name, "before": before, "after": after,
                            "source": overrides.get(name, candidate_relative + "/" + name) if after else None})
    changes.sort(key=lambda row: (1000 if row["path"] == "state.json" else 900 if row["path"] == ".invo-learn/active.json"
                                 else 899 if row["path"] == "learn.py" else 0, row["path"]))
    plan = {"schema_version": 1, "migration_id": manifest["id"], "destination": str(destination), "candidate": candidate_relative,
            "staged_workspace_sha256": digest(json.dumps(manifest["workspace_inventory"], sort_keys=True, ensure_ascii=False).encode()),
            "candidate_inventory": inventory(candidate), "source_version": version, "package_sha256": digest(json.dumps(hashes, sort_keys=True).encode()),
            "baseline": original["inventory"], "original_snapshot": original["snapshot"], "target": target, "changes": changes,
            "active_state": payloads + "/state.active.json", "active_state_metadata": _metadata(stage_path(root, payloads + "/state.active.json").read_bytes()),
            "new_directories": [name for name in target["directories"] if name not in baseline["directories"]],
            "removed_directories": [name for name in baseline["directories"] if name not in target["directories"]]}
    atomic(stage_path(root, PLAN), plan)
    progress = {"migration_id": manifest["id"], "plan_sha256": digest(stage_path(root, PLAN).read_bytes()), "status": "prepared", "cursor": 0}
    atomic(root / PROGRESS, progress)
    return plan, progress


def _load_plan(root):
    plan = read_json(stage_path(root, PLAN))
    progress = read_json(root / PROGRESS)
    require(digest(stage_path(root, PLAN).read_bytes()) == progress["plan_sha256"], "immutable activation plan checksum changed")
    require(inventory(stage_path(root, plan["candidate"])) == plan["candidate_inventory"], "checked activation candidate changed")
    return plan, progress


def _installed(destination, version, today):
    active = read_json(destination / ".invo-learn/active.json")
    require(active["version"] == version, "destination did not activate the checked current harness")
    checked = subprocess.run([sys.executable, "-B", str(destination / "learn.py"), "--today", today, "status"],
                             capture_output=True, text=True)
    require(checked.returncode == 0, "activated installed command failed: " + checked.stderr.strip())
    json.loads(checked.stdout)
    protect(Workspace(destination), today)


def _unchanged_originals(destination, plan):
    """Check preserved baseline entries while allowing unrelated new learner work."""
    changed = {row["path"] for row in plan["changes"]}
    baseline = _ordinary(plan["baseline"])
    for name, metadata in baseline["files"].items():
        if name not in changed and "__pycache__" not in Path(name).parts:
            require(_current(_file(destination, name)) == metadata,
                    "unchanged original file is missing or altered during cutover: " + name)
    removed = set(plan.get("removed_directories", []))
    for name in baseline["directories"]:
        if name not in removed and "__pycache__" not in Path(name).parts:
            require(_file(destination, name).is_dir(), "unchanged original directory is missing during cutover: " + name)


def _apply(root, manifest, plan, progress, today, interrupt_after=None):
    destination = no_links(plan["destination"]).resolve()
    ws = Workspace(destination)
    with ws.locked():
        _unchanged_originals(destination, plan)
        for name in plan["new_directories"]:
            directory = _file(destination, name)
            require(not directory.exists() or directory.is_dir(), "new migrated directory conflicts with learner work")
            directory.mkdir(parents=True, exist_ok=True)
        for row in plan["changes"]:
            require(_current(_file(destination, row["path"])) in (row["before"], row["after"]),
                    "activation conflicts with newer work; preserve it before recovery: " + row["path"])
        written = 0
        for index, row in enumerate(plan["changes"]):
            path = _file(destination, row["path"])
            if _current(path) != row["after"]:
                if row["after"] is None:
                    path.unlink()
                else:
                    data = stage_path(root, row["source"]).read_bytes()
                    require(_metadata(data) == row["after"], "checked activation payload checksum changed")
                    atomic_bytes(path, data)
                written += 1
            if interrupt_after is not None and written >= interrupt_after:
                progress.update(status="interrupted", cursor=index + 1)
                atomic(root / PROGRESS, progress)
                return {"status": "interrupted", "activated": False, "migration_id": manifest["id"],
                        "recovery": "Resume this verified journal with migration-recover --action resume"}
            if (index + 1) % 32 == 0 or index + 1 == len(plan["changes"]):
                progress.update(status="applying", cursor=index + 1)
                atomic(root / PROGRESS, progress)
        for name in sorted(plan.get("removed_directories", []), key=lambda value: len(Path(value).parts), reverse=True):
            directory = _file(destination, name)
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
        _installed(destination, plan["source_version"], today)
        _independent_inputs(root, manifest)
        _unchanged_originals(destination, plan)
        for row in plan["changes"]:
            require(_current(_file(destination, row["path"])) == row["after"], "destination activation verification failed")
        data = stage_path(root, plan["active_state"]).read_bytes()
        require(_metadata(data) == plan["active_state_metadata"], "active state payload checksum changed")
        atomic_bytes(destination / "state.json", data)
        progress.update(status="committed", cursor=len(plan["changes"]))
        atomic(root / PROGRESS, progress)
        manifest.update(activated=True, activation={"status": "active", "version": plan["source_version"], "plan": PLAN})
        atomic(root / "migration-manifest.json", manifest)
    return {"status": "activated", "activated": True, "migration_id": manifest["id"], "destination": str(destination), "version": plan["source_version"]}


def _mark_active(root, manifest, plan, progress):
    progress.update(status="committed", cursor=len(plan["changes"]))
    atomic(root / PROGRESS, progress)
    manifest.update(activated=True, activation={"status": "active", "version": plan["source_version"], "plan": PLAN})
    atomic(root / "migration-manifest.json", manifest)


def _independent_inputs(root, manifest):
    for original in manifest["sources"].values():
        if original["kind"] != "course":
            require(inventory(Path(original["source"])) == original["inventory"], "assignment source changed during cutover")
        if original.get("external_mailbox"):
            mailbox = original["external_mailbox"]
            require(inventory(Path(mailbox["source"])) == mailbox["inventory"], "external mailbox changed during cutover")


def _existing(root, manifest, current, today):
    require(current.state.get("migration", {}).get("id") == manifest["id"] and current.state["migration"]["status"] == "active",
            "activation receipt differs from active destination")
    verify_rehearsal(root, verify_sources=False)
    protect(current, today)
    return {"status": "already-active", "activated": True, "migration_id": manifest["id"], "destination": str(current.root)}


def activate(stage, source=None, today=None, interrupt_after=None):
    date(today)
    require(interrupt_after is None or type(interrupt_after) is int and interrupt_after > 0, "interruption checkpoint must be a positive integer")
    source = source or Path(__file__).resolve().parent.parent
    with stage_locked(stage) as root:
        from .migration import load_rehearsal
        _, manifest = load_rehearsal(root)
        destination = no_links(manifest["destination"]).resolve()
        current = Workspace(destination)
        if manifest.get("activated"):
            return _existing(root, manifest, current, today)
        if stage_path(root, PLAN).exists():
            verify_rehearsal(root, verify_sources=False)
            plan, progress = _load_plan(root)
            require(plan["migration_id"] == manifest["id"] and Path(plan["destination"]) == destination,
                    "activation plan does not identify this destination")
            if current.state.get("migration", {}).get("id") == manifest["id"] and current.state["migration"]["status"] == "active":
                _installed(destination, plan["source_version"], today)
                _unchanged_originals(destination, plan)
                _mark_active(root, manifest, plan, progress)
                return _existing(root, manifest, current, today)
            _validate_gate(root, manifest, Workspace(stage_path(root, manifest["workspace"])), today)
            require(plan["staged_workspace_sha256"] == digest(json.dumps(manifest["workspace_inventory"], sort_keys=True, ensure_ascii=False).encode()),
                    "staged records changed after activation preparation; preserve this journal and rehearse a fresh stage with the newer returns")
            _independent_inputs(root, manifest)
        else:
            checked = verify_rehearsal(root)
            plan, progress = _prepare(root, checked["manifest"], source, today)
        return _apply(root, manifest, plan, progress, today, interrupt_after)


def recover(stage, action, today):
    if action == "resume":
        return activate(stage, today=today)
    require(action == "rollback", "recovery action must be resume or rollback")
    date(today)
    with stage_locked(stage) as root:
        checked = verify_rehearsal(root, verify_sources=False)
        manifest = checked["manifest"]
        plan, progress = _load_plan(root)
        require(not manifest.get("activated"), "completed activation cannot be erased by interruption recovery")
        ws = Workspace(plan["destination"])
        require(not (ws.state.get("migration", {}).get("id") == manifest["id"] and ws.state["migration"].get("status") == "active"),
                "active learner records require finalizing the activation receipt, not rolling back newer work")
        if progress["status"] == "rolled-back":
            return {"status": "already-rolled-back", "activated": False, "migration_id": manifest["id"]}
        with ws.locked():
            for row in plan["changes"]:
                require(_current(_file(ws.root, row["path"])) in (row["before"], row["after"]),
                        "rollback conflicts with newer work; preserve it before recovery: " + row["path"])
            for index, row in enumerate(reversed(plan["changes"])):
                path = _file(ws.root, row["path"])
                if _current(path) != row["before"]:
                    if row["before"] is None:
                        path.unlink()
                    else:
                        data = stage_path(root, plan["original_snapshot"] + "/" + row["path"]).read_bytes()
                        require(_metadata(data) == row["before"], "preserved rollback original checksum changed")
                        atomic_bytes(path, data)
                if (index + 1) % 32 == 0 or index + 1 == len(plan["changes"]):
                    progress.update(status="rolling-back", cursor=index + 1)
                    atomic(root / PROGRESS, progress)
            for name in sorted(plan["new_directories"], key=lambda value: len(Path(value).parts), reverse=True):
                directory = _file(ws.root, name)
                if directory.is_dir() and not any(directory.iterdir()):
                    directory.rmdir()
            checked_command = subprocess.run([sys.executable, "-B", str(ws.root / "learn.py"), "--today", today, "doctor"],
                                             capture_output=True, text=True)
            require(checked_command.returncode == 0, "restored installed runtime needs attention: " + checked_command.stderr.strip())
            health = json.loads(checked_command.stdout)
            require(all(check["status"] == "ok" for check in health["checks"] if check["check"] in ("durable-artifacts", "active-release")),
                    "restored original archives need attention; originals remain preserved")
            progress.update(status="rolled-back", cursor=0)
            atomic(root / PROGRESS, progress)
        return {"status": "rolled-back", "activated": False, "migration_id": manifest["id"], "destination": str(ws.root)}
