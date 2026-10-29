"""Import audit, plan decisions, and offline recovery diagnostics."""
import copy
import datetime as dt
import json
import subprocess
import uuid

from .contracts import Invalid, date, fields, identifier, require, string, strings


def ingest(ws, raw, today, repair_of=None, repair_note=None, relevance=None):
    from .engine import atomic, atomic_bytes, digest, read_json
    date(today)
    rid = digest(raw.encode("utf-8"))
    raw_relative = f"inbox/reports/{rid}.txt"
    path = ws.path(raw_relative)
    if not path.exists():
        atomic_bytes(path, raw.encode("utf-8"))
    require(digest(path.read_bytes()) == rid, "raw report archive checksum changed; preserve the paste and restore its archive")
    ledger_path = ws.path(f"inbox/imports/{rid}.json")
    ledger = read_json(ledger_path) if ledger_path.exists() else {"import_id": rid, "raw_path": raw_relative, "attempts": []}
    attempt = {"recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(), "repair_of": repair_of, "repair_note": repair_note}
    try:
        if repair_of is not None:
            identifier(repair_of)
            string(repair_note, "repair note")
            require(repair_of != rid, "repair must preserve a different original representation")
            parent = read_json(ws.path(f"inbox/imports/{repair_of}.json"))
            require(parent["outcome"] == "rejected", "repair must link a rejected import")
        else:
            require(repair_note is None, "repair note requires repair_of")
        result = ws._ingest(raw, today, relevance)
        if (result["status"] == "duplicate" and ledger.get("outcome") in ("imported", "supplemental-recorded", "duplicate")
                and repair_of is None and relevance is None):
            return result | {"import_id": rid}
        attempt.update(outcome=result["status"], result=result)
        ledger.update(outcome=result["status"], report_id=result.get("report_id"))
    except (Invalid, ValueError, TypeError, KeyError, OSError) as exc:
        attempt.update(outcome="rejected", reason=str(exc))
        # An invalid review decision does not turn a valid quarantined report
        # into a formatting rejection; it remains available for another review.
        ledger["outcome"] = "needs-review" if relevance is not None and ledger.get("outcome") == "needs-review" else "rejected"
        # A failed validation/state write never leaves speculative evidence in memory.
        ws.state = read_json(ws.state_path)
        ledger["attempts"].append(attempt)
        atomic(ledger_path, ledger)
        raise
    ledger["attempts"].append(attempt)
    atomic(ledger_path, ledger)
    return result | {"import_id": rid}


def imports(ws):
    from .engine import read_json
    folder = ws.path("inbox/imports")
    result = []
    if folder.exists():
        for path in sorted(folder.glob("*.json")):
            try:
                entry = read_json(path)
                fields(entry, ("import_id", "raw_path", "attempts", "outcome"), ("report_id",))
                require(entry["import_id"] == path.stem and isinstance(entry["attempts"], list) and entry["attempts"], "invalid import audit")
                require(all(isinstance(a, dict) and "outcome" in a for a in entry["attempts"]), "invalid import attempts")
                result.append(entry)
            except (Invalid, ValueError, TypeError, KeyError, OSError) as exc:
                result.append({"import_id": path.stem, "raw_path": None, "outcome": "audit-unreadable",
                               "attempts": [{"outcome": "audit-unreadable", "reason": str(exc)}]})
    # Successful linked repairs settle the original rejected input without editing it.
    repaired = {a["repair_of"] for entry in result for a in entry["attempts"]
                if a.get("repair_of") and a["outcome"] in ("imported", "supplemental-recorded", "duplicate")}
    return [dict(entry, settled_by_repair=entry["import_id"] in repaired) for entry in result]


def review_import(ws, iid, decisions, today):
    from .engine import read_json
    identifier(iid)
    ledger = read_json(ws.path(f"inbox/imports/{iid}.json"))
    require(ledger["outcome"] == "needs-review", "import is not awaiting relevance review")
    with ws.path(ledger["raw_path"]).open(encoding="utf-8", newline="") as stream:
        return ingest(ws, stream.read(), today, relevance=decisions)


def plan_decision(ws, tid, spec):
    fields(spec, ("kind", "reason", "objective_ids", "changes"),
           ("approval", "minutes", "available_minutes", "preferred_lesson_minutes", "deadline", "proposal_id"))
    track = ws.track(tid)
    require(spec["kind"] in ("routine", "substantial"), "plan kind must be routine or substantial")
    for key in ("reason", "changes"):
        string(spec[key], key)
    strings(spec["objective_ids"], "plan objectives")
    require(spec["objective_ids"] and set(spec["objective_ids"]) <= track["objectives"].keys(), "plan uses unknown objectives")
    require(all(track["objectives"][oid]["scope"] == "included" for oid in spec["objective_ids"]),
            "accept a coverage-map change before planning deferred objectives")
    for key in ("minutes", "available_minutes", "preferred_lesson_minutes"):
        if key in spec:
            require(type(spec[key]) is int and spec[key] > 0, f"{key} must be positive minutes")
    if "deadline" in spec:
        date(spec["deadline"])
    if "approval" in spec:
        string(spec["approval"], "learner approval")
    previous = next((d for d in track.get("plan_decisions", []) if d["id"] == spec.get("proposal_id")), None)
    if "proposal_id" in spec:
        require(previous and previous["status"] == "pending", "unknown/finalized plan proposal")
        # Approval must concern the exact proposal, not silently edited scope or pacing.
        original = {k: v for k, v in previous.items() if k not in ("id", "status", "pacing_warning")}
        proposed = {k: v for k, v in spec.items() if k not in ("approval", "proposal_id")}
        require(proposed == original, "plan changed; propose and review the new plan")
    mismatch = ("minutes" in spec and "available_minutes" in spec and spec["minutes"] > spec["available_minutes"])
    status = "applied" if (spec["kind"] == "routine" and not mismatch) or spec.get("approval") else "pending"
    decision = {"id": "plan-" + uuid.uuid4().hex[:12], **copy.deepcopy(spec), "status": status,
                "pacing_warning": "Estimated work exceeds supplied available time; learner decision needed" if mismatch else None}
    track.setdefault("plan_decisions", []).append(decision)
    if previous and status == "applied":
        previous["status"] = "superseded"
    ws.save("plan-decision", {"track_id": tid, "decision_id": decision["id"], "status": status})
    return decision


def work_queue(ws, today):
    from .revisions import context_ready
    queue = []
    for item in imports(ws):
        if item["outcome"] == "audit-unreadable":
            queue.append({"action": "inspect-import-audit", "import_id": item["import_id"], "reason": item["attempts"][-1]["reason"]})
        if item["outcome"] in ("rejected", "needs-review") and not item["settled_by_repair"]:
            queue.append({"action": "review-import" if item["outcome"] == "needs-review" else "repair-report",
                          "import_id": item["import_id"], "reason": item["attempts"][-1].get("reason", item["outcome"])})
    for concern in ws.state.get("concerns", {}).values():
        if concern["status"] in ("suspected", "confirmed"):
            queue.append({"action": "investigate-content" if concern["status"] == "suspected" else "correct-content",
                          "concern_id": concern["id"], "track_id": concern["track_id"]})
    for rid, record in ws.state["reports"].items():
        for item in record["report"]["objectives"]:
            from .revisions import effective_item, latest_dispositions
            _, reviews = effective_item(ws, record, item)
            for (basis, aid), review in latest_dispositions(reviews).items():
                if review["status"] == "pending":
                    queue.append({"action": "review-evidence", "report_id": rid, "objective_id": item["objective_id"],
                                  "assessment_id": aid, "basis": basis, "reason": review["reason"]})
    active = ws.state.get("active_lesson")
    for lesson in sorted(ws.pending_lessons(), key=lambda l: (l["id"] != active, l["sequence"])):
        queue.append({"action": "return-report" if context_ready(lesson) else "review-packet-context",
                      "lesson_id": lesson["id"], "track_id": lesson["track_id"], "staged": lesson["id"] == active})
    for tid, track in ws.state["tracks"].items():
        for decision in track.get("plan_decisions", []):
            if decision["status"] == "pending":
                queue.append({"action": "review-plan", "track_id": tid, "proposal_id": decision["id"]})
        for pid, proposal in track["proposals"].items():
            if proposal["status"] == "pending":
                fresh = proposal["base_revision"] == track["map_revision"] and proposal["material_ids"] == sorted(track["materials"])
                queue.append({"action": "review-map" if fresh else "revise-stale-map", "track_id": tid, "proposal_id": pid})
        gaps = track.get("source_gaps", [])
        if gaps:
            queue.append({"action": "inspect-source-gaps", "track_id": tid, "count": len(gaps)})
        mapped = {r["material_id"] for objective in track["objectives"].values() for r in objective["sources"]}
        unaccounted = {mid for mid, material in track["materials"].items() if material["role"] == "primary"} - mapped - {g["material_id"] for g in gaps}
        if unaccounted and not any(p["status"] == "pending" for p in track["proposals"].values()):
            queue.append({"action": "propose-map", "track_id": tid, "material_ids": sorted(unaccounted)})
    from .assignments import next_actions
    queue.extend(next_actions(ws))
    for name, outcome in last_outcomes(ws).items():
        if outcome.get("status") in ("backup-failed", "failed", "unavailable"):
            queue.append({"action": "retry-" + name, "reason": outcome.get("reason", "previous operation unsuccessful")})
    return queue


def last_outcomes(ws):
    from .engine import read_json
    result = {}
    for name in ("backup", "update"):
        path = ws.path(f".invo-learn/last-{name}.json")
        if path.exists():
            try:
                outcome = read_json(path)
                require(isinstance(outcome, dict) and isinstance(outcome.get("status"), str), "invalid operation outcome")
                result[name] = outcome
            except (Invalid, ValueError, TypeError, OSError) as exc:
                result[name] = {"status": "unavailable", "record_error": True, "reason": "Cannot read saved outcome: " + str(exc)}
    return result


def doctor(ws, today):
    from .engine import digest, read_json
    checks = []
    def check(name, operation):
        try:
            details = operation()
            checks.append({"check": name, "status": "ok", "details": details})
        except (Invalid, ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
            checks.append({"check": name, "status": "needs-attention", "reason": str(exc)})
    check("mailbox-ownership", lambda: str(ws.mailbox()))
    def verify_artifacts():
        count = 0
        def verify(relative, checksum):
            nonlocal count
            require(digest(ws.path(relative).read_bytes()) == checksum, "checksum mismatch: " + relative)
            count += 1
        for track in ws.state["tracks"].values():
            for material in track["materials"].values():
                verify(material["original"], material["sha256"])
                for derived in material["derived"]:
                    verify(derived["path"], derived["sha256"])
        for lesson in ws.state["lessons"].values():
            for name, checksum in lesson["staged_files"].items():
                verify(f"lessons/{lesson['id']}/packet/{name}", checksum)
        from .assignments import checked_assignment, checked_plan
        from .reference_solution import checked as checked_reference
        for tid, track in ws.state["tracks"].items():
            for aid, assignment in track.get("assignments", {}).items():
                checked_assignment(ws, tid, aid)
                count += 1
                for pid in assignment["plans"]:
                    checked_plan(ws, assignment, pid)
                    count += 1
                for reference_id in assignment.get("references", {}):
                    reference = checked_reference(ws, assignment, reference_id, verified=False)
                    count += 1 + len(reference["artifacts"])
        for correction in ws.state.get("corrections", {}).values():
            verify(correction["path"], correction["sha256"])
        for report in ws.state["reports"].values():
            obj = read_json(ws.path(report["path"]))
            checksum = digest(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode())
            require(checksum == report["sha256"], "archived report checksum mismatch")
            raw = ws.path(report["raw_path"])
            require(digest(raw.read_bytes()) == raw.stem, "raw report checksum mismatch")
        for record in ws.state.get("supplemental_reports", {}).values():
            obj = read_json(ws.path(record["path"]))
            require(digest(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()) == record["sha256"], "supplemental archive checksum mismatch")
            raw = ws.path(record["raw_path"])
            require(digest(raw.read_bytes()) == raw.stem, "supplemental raw checksum mismatch")
            count += 1
        return {"verified_artifacts": count}
    check("durable-artifacts", verify_artifacts)
    def verify_audit():
        from .engine import digest
        entries = imports(ws)
        require(not any(e["outcome"] == "audit-unreadable" for e in entries), "unreadable import audit; inspect work_queue")
        for entry in entries:
            require(digest(ws.path(entry["raw_path"]).read_bytes()) == entry["import_id"], "raw import checksum mismatch")
        return {"verified_imports": len(entries)}
    check("import-audit", verify_audit)
    def active_release():
        active = read_json(ws.path(".invo-learn/active.json"))
        release = ws.path(active["release"])
        require(release.parent == ws.root / ".invo-learn/releases", "invalid active release path")
        manifest = read_json(release / "manifest.json")
        for name, checksum in manifest["files"].items():
            require(digest(ws.path(active["release"] + "/" + name).read_bytes()) == checksum, "modified installed release: " + name)
        return {"version": active["version"]}
    check("active-release", active_release)
    def git_root():
        if not (ws.root / ".git").exists():
            return "No local repository (--no-git workspace); no backup verification attempted"
        result = subprocess.run(["git", "-C", str(ws.root), "rev-parse", "--show-toplevel"],
                                capture_output=True, text=True, check=True, timeout=10)
        require(str(ws.root).replace("\\", "/").lower() == result.stdout.strip().lower(), "workspace Git root mismatch")
        return "Workspace is the Git root"
    check("git-root", git_root)
    queue = work_queue(ws, today)
    outcomes = last_outcomes(ws)
    if any(value.get("record_error") for value in outcomes.values()):
        checks.append({"check": "operation-audit", "status": "needs-attention", "reason": "A saved operation outcome is unreadable"})
    return {"status": "healthy" if all(c["status"] == "ok" for c in checks) else "needs-attention",
            "checks": checks, "work_queue": queue, "next_action": queue[0] if queue else {"action": "choose-next-lesson"},
            "last_operations": outcomes, "network": "not checked; diagnostics are offline"}
