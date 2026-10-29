"""Agent-facing command line. The learner returns only a pasted report."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
import subprocess

from .contracts import Invalid
from .engine import Workspace, atomic, read_json
from .install import bootstrap, upgrade
from .updates import check_updates, study_update
from . import quality, revisions, workflow


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
    legacy = sub.add_parser("legacy-status", help="read an older course or assignment snapshot without converting it")
    legacy.add_argument("source", type=Path)
    legacy_report = sub.add_parser("legacy-report", help="inspect an older returned report against its exact issued packet")
    legacy_report.add_argument("source", type=Path)
    legacy_report.add_argument("file", type=Path)
    migration = sub.add_parser("migration-rehearse", help="explicitly preserve and stage a combined private workspace; never activate")
    migration.add_argument("file", type=Path)
    migration_status = sub.add_parser("migration-status", help="verify a preserved rehearsal without activating it")
    migration_status.add_argument("stage", type=Path)
    projection = sub.add_parser("migration-project", help="conservatively project preserved observations and plan fresh study")
    projection.add_argument("stage", type=Path)
    projection.add_argument("--links", type=Path, help="optional planner-justified objective associations")
    sub.add_parser("doctor", help="offline integrity, recovery queue and last operation outcomes")
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
    t = sub.add_parser("add-course", help="add a course or other learning track")
    t.add_argument("track_id")
    t.add_argument("--title", required=True)
    t.add_argument("--preferences", type=Path)
    for command in ("add-assignment", "propose-assignment-plan"):
        operation = sub.add_parser(command)
        operation.add_argument("track_id")
        operation.add_argument("assignment_id")
        operation.add_argument("file", type=Path)
    reference = sub.add_parser("record-reference", help="preserve an explicitly requested reference and actual requirement checks")
    reference.add_argument("track_id")
    reference.add_argument("assignment_id")
    reference.add_argument("file", type=Path)
    choice = sub.add_parser("assignment-choice", help="record this assignment's explicit upfront-solution answer")
    choice.add_argument("track_id")
    choice.add_argument("assignment_id")
    choice.add_argument("--solution", choices=("yes", "no"), required=True)
    choice.add_argument("--reason", required=True)
    choice.add_argument("--new-decision", action="store_true", help="record an explicit later solution choice while preserving earlier answers and references")
    begin = sub.add_parser("begin-implementation", help="record the actual transition to assignment implementation")
    begin.add_argument("track_id")
    begin.add_argument("assignment_id")
    begin.add_argument("--reason", required=True)
    guidance = sub.add_parser("implementation-choice", help="record the guidance answer at implementation")
    guidance.add_argument("track_id")
    guidance.add_argument("assignment_id")
    guidance.add_argument("--guidance", choices=("yes", "no"), required=True)
    guidance.add_argument("--reason", required=True)
    guidance.add_argument("--new-decision", action="store_true", help="explicitly change the answer while retaining earlier choices")
    progress = sub.add_parser("record-implementation", help="record actual independent deliverable checks without a chatbot checkout")
    progress.add_argument("track_id")
    progress.add_argument("assignment_id")
    progress.add_argument("file", type=Path)
    accept_assignment = sub.add_parser("accept-assignment-plan")
    accept_assignment.add_argument("track_id")
    accept_assignment.add_argument("assignment_id")
    accept_assignment.add_argument("plan_id")
    accept_assignment.add_argument("--approval", required=True)
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
    replace = sub.add_parser("replace", help="explicitly replace a pending lesson without changing its archive")
    replace.add_argument("lesson_id")
    replace.add_argument("file", type=Path)
    replace.add_argument("--reason", required=True)
    for command, help_text in (("preflight", "measure selected context and inspect recorded quality checks"),
                               ("reduce-context", "save a verified reduction of usable material"),
                               ("record-concern", "record a suspected content error"),
                               ("plan-decision", "record routine adaptations or substantial plan proposals")):
        operation = sub.add_parser(command, help=help_text)
        operation.add_argument("track_id")
        operation.add_argument("file", type=Path)
    for command, target in (("investigate", "concern_id"), ("correct", "concern_id"),
                            ("review-context", "lesson_id"), ("review-import", "import_id")):
        operation = sub.add_parser(command)
        operation.add_argument(target)
        operation.add_argument("file", type=Path)
    operation = sub.add_parser("review-evidence", help="append a scoped assessment/objective disposition")
    operation.add_argument("file", type=Path)
    rs = sub.add_parser("restage", help="recover staging of an already prepared handoff")
    rs.add_argument("lesson_id")
    ab = sub.add_parser("abandon")
    ab.add_argument("lesson_id")
    ab.add_argument("--reason", required=True)
    ing = sub.add_parser("ingest", help="agent saves exact paste to a private file, or passes it on stdin")
    ing.add_argument("file", nargs="?", type=Path)
    ing.add_argument("--repair-of")
    ing.add_argument("--repair-note")
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
    if cmd == "migration-project":
        from .migration_projection import project
        return project(args.stage, read_json(args.links) if args.links else None, args.today)
    if cmd == "migration-rehearse":
        from .migration import rehearse
        return rehearse(read_json(args.file))
    if cmd == "migration-status":
        from .migration import verify_rehearsal
        return verify_rehearsal(args.stage)
    if cmd == "legacy-status":
        from .legacy import read_snapshot
        return read_snapshot(args.source).status()
    if cmd == "legacy-report":
        from .legacy import read_snapshot
        return read_snapshot(args.source).inspect_report(args.file, args.today)
    if cmd == "bootstrap":
        return bootstrap(args.source, args.destination, args.name, args.mailbox,
                         read_json(args.preferences) if args.preferences else None, not args.no_git)
    ws = Workspace(args.workspace)
    if ws.state.get("migration", {}).get("status") == "rehearsed" and cmd not in ("status", "doctor"):
        raise Invalid("staged migration is inactive; complete explicit checks and activation before study changes")
    if cmd == "check-updates":
        return check_updates(read_json(ws.root / ".invo-learn/active.json")["version"])
    if cmd == "study-update":
        result = study_update(ws, args.track)
        atomic(ws.path(".invo-learn/last-update.json"), result)
        return result
    update_result = None
    if cmd == "prepare" and not args.skip_update_check:
        before = read_json(ws.root / ".invo-learn/active.json")["version"]
        update_result = study_update(ws, args.track_id)
        atomic(ws.path(".invo-learn/last-update.json"), update_result)
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
    if cmd == "doctor":
        return workflow.doctor(ws, args.today)
    if cmd == "preflight":
        from .assignments import prepare_context
        enriched, _ = prepare_context(ws, args.track_id, read_json(args.file))
        return quality.preflight(ws, args.track_id, enriched)
    with ws.locked():
        if cmd in ("backup", "configure-backup"):
            from .backup import backup, configure
            if cmd == "configure-backup":
                return configure(ws, args.remote, args.repository)
            result = backup(ws, args.paths, args.message, args.track)
            atomic(ws.path(".invo-learn/last-backup.json"), result)
            return result
        if cmd == "reduce-context":
            return quality.reduce_context(ws, args.track_id, read_json(args.file))
        if cmd == "record-concern":
            return revisions.record_concern(ws, args.track_id, read_json(args.file))
        if cmd == "investigate":
            return revisions.investigate(ws, args.concern_id, read_json(args.file))
        if cmd == "correct":
            return revisions.correct(ws, args.concern_id, read_json(args.file))
        if cmd == "review-context":
            return revisions.review_context(ws, args.lesson_id, read_json(args.file))
        if cmd == "review-evidence":
            return revisions.review_evidence(ws, read_json(args.file))
        if cmd == "review-import":
            return workflow.review_import(ws, args.import_id, read_json(args.file), args.today)
        if cmd == "plan-decision":
            return workflow.plan_decision(ws, args.track_id, read_json(args.file))
        if cmd == "render":
            ws.render()
            return {"status": "rendered"}
        if cmd == "add-course":
            return ws.add_track(args.track_id, args.title, read_json(args.preferences) if args.preferences else None)
        if cmd == "record-reference":
            from .reference_solution import save
            return save(ws, args.track_id, args.assignment_id, read_json(args.file))
        if cmd in ("begin-implementation", "implementation-choice", "record-implementation"):
            from . import implementation
            if cmd == "begin-implementation":
                return implementation.begin(ws, args.track_id, args.assignment_id, args.reason)
            if cmd == "implementation-choice":
                return implementation.choose(ws, args.track_id, args.assignment_id, args.guidance == "yes", args.reason, args.new_decision)
            return implementation.record_independent(ws, args.track_id, args.assignment_id, read_json(args.file))
        if cmd in ("add-assignment", "assignment-choice", "propose-assignment-plan", "accept-assignment-plan"):
            from . import assignments
            if cmd == "accept-assignment-plan":
                return assignments.accept_plan(ws, args.track_id, args.assignment_id, args.plan_id, args.approval)
            if cmd == "add-assignment":
                return assignments.add(ws, args.track_id, args.assignment_id, read_json(args.file))
            if cmd == "assignment-choice":
                return assignments.choose_solution(ws, args.track_id, args.assignment_id, args.solution == "yes", args.reason, args.new_decision)
            return assignments.propose_plan(ws, args.track_id, args.assignment_id, read_json(args.file))
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
        if cmd == "replace":
            if args.lesson_id not in ws.state["lessons"]:
                raise Invalid("unknown lesson")
            tid = ws.state["lessons"][args.lesson_id]["track_id"]
            return ws.prepare(tid, read_json(args.file), args.today, args.lesson_id, args.reason)
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
            return ws.ingest(raw, args.today, args.repair_of, args.repair_note)
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
