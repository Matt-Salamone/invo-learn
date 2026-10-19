"""Agent-facing command line. The learner returns only a pasted report."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
import subprocess

from .contracts import Invalid
from .engine import Workspace, read_json
from .install import bootstrap, upgrade
from .updates import check_updates, study_update


def parser(workspace_default=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", type=Path, default=workspace_default or Path.cwd())
    p.add_argument("--today", default=dt.date.today().isoformat(), help="learner-local YYYY-MM-DD; defaults to system local date")
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("bootstrap", help="create an independent private workspace")
    b.add_argument("destination", type=Path)
    b.add_argument("--source", type=Path, default=Path(__file__).resolve().parent.parent)
    b.add_argument("--name", required=True)
    b.add_argument("--mailbox", type=Path)
    b.add_argument("--preferences", type=Path, help="optional JSON preferences")
    b.add_argument("--no-git", action="store_true")
    sub.add_parser("status", help="all tracks, gaps and due reviews")
    sub.add_parser("check-updates", help="read-only GitHub version check; never installs an update")
    su = sub.add_parser("study-update", help="automatically install a compatible trusted release unless opted out")
    su.add_argument("--track")
    bk = sub.add_parser("backup", help="agent: commit completed scoped files and push to a verified private remote")
    bk.add_argument("--paths", nargs="+", required=True)
    bk.add_argument("--message", required=True)
    bk.add_argument("--track")
    bc = sub.add_parser("configure-backup", help="bind an existing private GitHub remote to this workspace")
    bc.add_argument("--remote", default="origin")
    bc.add_argument("--repository", required=True, help="learner-owned OWNER/REPO, never the public harness")
    sub.add_parser("render", help="regenerate inspectable overview and coverage files")
    t = sub.add_parser("add-course", aliases=["add-track"], help="add a course or other learning track")
    t.add_argument("track_id")
    t.add_argument("--title", required=True)
    t.add_argument("--preferences", type=Path)
    pr = sub.add_parser("preferences")
    pr.add_argument("file", type=Path)
    pr.add_argument("--track")
    m = sub.add_parser("add-material")
    m.add_argument("track_id")
    m.add_argument("file", type=Path)
    m.add_argument("--role", choices=("primary", "supplemental"), default="primary")
    im = sub.add_parser("inspect-material", help="record successful direct reading with available tools")
    im.add_argument("track_id")
    im.add_argument("material_id")
    im.add_argument("--note", required=True)
    ap = sub.add_parser("approve-transform", help="record explicit learner consent BEFORE creating/running a local workflow")
    ap.add_argument("track_id")
    ap.add_argument("material_id")
    ap.add_argument("--workflow", required=True)
    ap.add_argument("--consent", required=True)
    de = sub.add_parser("add-derived")
    de.add_argument("track_id")
    de.add_argument("material_id")
    de.add_argument("file", type=Path)
    de.add_argument("--approval", required=True)
    de.add_argument("--note", required=True)
    mp = sub.add_parser("propose-map")
    mp.add_argument("track_id")
    mp.add_argument("file", type=Path)
    ma = sub.add_parser("accept-map")
    ma.add_argument("track_id")
    ma.add_argument("proposal_id")
    ma.add_argument("--approval", required=True)
    ov = sub.add_parser("override")
    ov.add_argument("track_id")
    ov.add_argument("objective_ids", nargs="+")
    ov.add_argument("--reason", required=True)
    le = sub.add_parser("prepare")
    le.add_argument("track_id")
    le.add_argument("file", type=Path)
    le.add_argument("--skip-update-check", action="store_true", help=argparse.SUPPRESS)
    rs = sub.add_parser("restage", help="recover staging of an already prepared handoff")
    rs.add_argument("lesson_id")
    ab = sub.add_parser("abandon")
    ab.add_argument("lesson_id")
    ab.add_argument("--reason", required=True)
    ing = sub.add_parser("ingest", help="agent saves exact paste to a private file, or passes it on stdin")
    ing.add_argument("file", nargs="?", type=Path)
    dis = sub.add_parser("dispute")
    dis.add_argument("report_id")
    dis.add_argument("--reason", required=True)
    policy = sub.add_parser("review-policy")
    policy.add_argument("intervals", type=int, nargs="+")
    up = sub.add_parser("upgrade", help="explicit upgrade from a trusted public checkout")
    up.add_argument("--source", type=Path, required=True)
    return p


def execute(args):
    cmd = args.command
    if cmd == "bootstrap":
        return bootstrap(args.source, args.destination, args.name, args.mailbox,
                         read_json(args.preferences) if args.preferences else None, not args.no_git)
    ws = Workspace(args.workspace)
    if cmd == "check-updates":
        return check_updates(read_json(ws.root / ".invo-learn/active.json")["version"])
    if cmd == "study-update":
        return study_update(ws, args.track)
    update_result = None
    if cmd == "prepare" and not args.skip_update_check:
        before = read_json(ws.root / ".invo-learn/active.json")["version"]
        update_result = study_update(ws, args.track_id)
        after = read_json(ws.root / ".invo-learn/active.json")["version"]
        if before != after:
            # Run the newly active code/templates, even if the old updater reported
            # a failure after activation. Never prepare using cached old modules.
            prepared = subprocess.run([sys.executable, str(ws.root / "learn.py"), "--today", args.today,
                                      "prepare", args.track_id, str(args.file.resolve()), "--skip-update-check"],
                                     capture_output=True, text=True)
            if prepared.returncode:
                raise Invalid(prepared.stderr.strip() or "Preparation failed after update; inspect active release")
            return json.loads(prepared.stdout) | {"update": update_result}
    if cmd == "status":
        return ws.status(args.today)
    with ws.locked():
        if cmd in ("backup", "configure-backup"):
            from .backup import backup, configure
            if cmd == "configure-backup":
                return configure(ws, args.remote, args.repository)
            return backup(ws, args.paths, args.message, args.track)
        if cmd == "render":
            ws.render()
            return {"status": "rendered"}
        if cmd in ("add-course", "add-track"):
            return ws.add_track(args.track_id, args.title, read_json(args.preferences) if args.preferences else None)
        if cmd == "preferences":
            return ws.set_preferences(args.track, read_json(args.file))
        if cmd == "add-material":
            return ws.add_material(args.track_id, args.file, args.role)
        if cmd == "inspect-material":
            return ws.inspect_material(args.track_id, args.material_id, args.note)
        if cmd == "approve-transform":
            return ws.approve_transformation(args.track_id, args.material_id, args.workflow, args.consent)
        if cmd == "add-derived":
            return ws.add_derived(args.track_id, args.material_id, args.file, args.approval, args.note)
        if cmd == "propose-map":
            return ws.propose_map(args.track_id, read_json(args.file))
        if cmd == "accept-map":
            return ws.accept_map(args.track_id, args.proposal_id, args.approval)
        if cmd == "override":
            return ws.override(args.track_id, args.objective_ids, args.reason)
        if cmd == "prepare":
            return ws.prepare(args.track_id, read_json(args.file), args.today) | {"update": update_result}
        if cmd == "restage":
            return ws.stage(args.lesson_id)
        if cmd == "abandon":
            return ws.abandon(args.lesson_id, args.reason)
        if cmd == "ingest":
            if args.file:
                with args.file.open(encoding="utf-8", newline="") as input_file:
                    raw = input_file.read()
            else:
                raw = sys.stdin.read()
            return ws.ingest(raw, args.today)
        if cmd == "dispute":
            return ws.dispute(args.report_id, args.reason)
        if cmd == "review-policy":
            return ws.set_policy(args.intervals)
        if cmd == "upgrade":
            return upgrade(ws, args.source)
    raise Invalid("unknown command")


def main(argv=None, workspace_default=None):
    args = parser(workspace_default).parse_args(argv)
    try:
        result = execute(args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (Invalid, ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        print(json.dumps({"error": str(exc), "command": args.command,
                          "recovery": "Raw ingest input is retained in inbox/reports. No learning evidence is added on validation failure." if args.command == "ingest" else "Resolve the error and retry; existing durable files are preserved."}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
