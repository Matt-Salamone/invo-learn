"""Planner links new assessments to advisory migration study needs."""
import copy

from .contracts import KINDS, evidence_outcome, fields, require, string, strings
from .revisions import effective_item


def needs(ws):
    migration = ws.state.get("migration", {})
    return {**migration.get("legacy_study_actions", {}),
            **migration.get("reconciliation", {}).get("fresh_study", {})}


def validate_links(ws, tid, spec):
    links = spec.get("legacy_study_links", [])
    require(isinstance(links, list), "legacy_study_links must be a list")
    known, seen = needs(ws), set()
    for link in links:
        fields(link, ("study_need_id", "objective_ids", "reason"))
        nid = link["study_need_id"]
        require(isinstance(nid, str) and nid in known and nid not in seen, "unknown or duplicate migration study need")
        seen.add(nid)
        require(ws.state["migration"].get("status") == "active", "fresh-study links require an active migration")
        require(known[nid]["track_id"] == tid, "study need must belong to the assigned course")
        strings(link["objective_ids"], "justified study target objectives")
        require(link["objective_ids"] and len(set(link["objective_ids"])) == len(link["objective_ids"])
                and set(link["objective_ids"]) <= set(spec["objective_ids"]), "study targets must be unique assigned objectives")
        string(link["reason"], "planner justification from governing requirements")
    return copy.deepcopy(links)


def recompute(ws, tid):
    """Rebuild from actual effective reports, so late help/withdrawals can reopen needs."""
    for nid, need in needs(ws).items():
        if need["track_id"] != tid:
            continue
        linked = {lid: link for lid, lesson in ws.state["lessons"].items()
                  for link in lesson.get("legacy_study_links", []) if link["study_need_id"] == nid}
        targets = sorted(set(need.get("objective_ids", []))
                         | {oid for link in linked.values() for oid in link["objective_ids"]})
        if not targets:
            continue
        progress = {}
        records = sorted((r for r in ws.state["reports"].values() if r["lesson_id"] in linked),
                         key=lambda r: (r["report"]["completed_on"], ws.state["lessons"][r["lesson_id"]]["sequence"]))
        for record in records:
            if record["invalidated"]:
                continue
            lesson = ws.state["lessons"][record["lesson_id"]]
            for original in record["report"]["objectives"]:
                oid = original["objective_id"]
                if oid not in linked[lesson["id"]]["objective_ids"]:
                    continue
                item, _ = effective_item(ws, record, original)
                if item is None or (item["coverage"] == "unassessed" and not item["assessments"]):
                    continue
                success, conflict, _ = evidence_outcome(item["assessments"], KINDS[ws.track(tid)["objectives"][oid]["kind"]])
                qualified = success and not conflict and item["coverage"] == "covered" and item["judgment"] == "demonstrated"
                # No-work placeholders or helped practice do not withdraw an earlier proof.
                # Rebuilding still removes a proof whose own report/help is invalidated.
                if not qualified and not conflict and oid in progress:
                    continue
                progress[oid] = {"objective_id": oid, "report_id": record["report"]["report_id"],
                                 "lesson_id": lesson["id"], "demonstrated": qualified}
        passed = sorted(oid for oid, item in progress.items() if item["demonstrated"])
        status = "completed" if set(passed) == set(targets) else "pending"
        view = {"target_objective_ids": targets, "demonstrated_objective_ids": passed,
                "evidence": [progress[oid] for oid in sorted(progress)]}
        if need.get("status") != status or need.get("study_progress") != view:
            need.setdefault("study_history", []).append({"status": status, "progress": copy.deepcopy(view)})
        need.update(status=status, study_progress=view)
