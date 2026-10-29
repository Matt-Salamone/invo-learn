"""Append-only content investigations, evidence dispositions and scoped gaps."""
import copy
import uuid

from .contracts import KINDS, evidence_outcome, fields, qualifies, require, string, strings


def concern(ws, tid, spec, origin_report=None):
    fields(spec, ("objective_ids", "claim", "reasoning", "source_reference"))
    track = ws.track(tid)
    strings(spec["objective_ids"], "affected objectives")
    require(spec["objective_ids"] and set(spec["objective_ids"]) <= track["objectives"].keys(), "unknown concern objectives")
    for key in ("claim", "reasoning", "source_reference"):
        string(spec[key], key)
    cid = "concern-" + uuid.uuid4().hex[:12]
    item = {"id": cid, "track_id": tid, **copy.deepcopy(spec), "origin_report": origin_report,
            "status": "suspected", "investigations": []}
    ws.state.setdefault("concerns", {})[cid] = item
    return item


def record_concern(ws, tid, spec):
    item = concern(ws, tid, spec)
    ws.save("concern-recorded", {"concern_id": item["id"]})
    return item


def investigate(ws, cid, spec):
    fields(spec, ("sources_examined", "reasoning", "conclusion"))
    require(cid in ws.state.get("concerns", {}), "unknown concern")
    item = ws.state["concerns"][cid]
    strings(spec["sources_examined"], "sources examined")
    require(spec["sources_examined"], "actual sources examined are required")
    string(spec["reasoning"], "investigation reasoning")
    require(spec["conclusion"] in ("confirmed", "unconfirmed"), "invalid investigation conclusion")
    require(item["status"] != "corrected", "record a new concern for further corrections")
    item["investigations"].append(copy.deepcopy(spec) | {"content_revision": ws.track(item["track_id"]).get("content_revision", 0)})
    item["status"] = spec["conclusion"]
    ws.save("concern-investigated", {"concern_id": cid, "conclusion": spec["conclusion"]})
    return item


def correct(ws, cid, spec):
    from .engine import atomic_bytes, digest
    fields(spec, ("base_revision", "context", "checks", "limitations", "announcement"))
    require(cid in ws.state.get("concerns", {}), "unknown concern")
    item = ws.state["concerns"][cid]
    track = ws.track(item["track_id"])
    revision = track.get("content_revision", 0)
    require(item["status"] == "confirmed" and item["investigations"][-1]["content_revision"] == revision,
            "a confirmed investigation of the current content revision is required")
    require(type(spec["base_revision"]) is int and spec["base_revision"] == revision, "stale correction revision")
    for key in ("context", "announcement"):
        string(spec[key], key)
    strings(spec["limitations"], "correction limitations")
    require(isinstance(spec["checks"], list) and spec["checks"], "correction verification required")
    for check in spec["checks"]:
        fields(check, ("check", "result", "evidence"))
        string(check["check"], "check")
        string(check["evidence"], "verification evidence")
        require(check["result"] in ("passed", "limited", "failed"), "invalid correction check result")
    require(any(c["result"] == "passed" for c in spec["checks"])
            and not any(c["result"] == "failed" for c in spec["checks"]), "fix failed checks before applying correction")
    correction_id = "correction-" + uuid.uuid4().hex[:12]
    relative = f"tracks/{item['track_id']}/corrections/{correction_id}.md"
    data = (spec["context"] + "\n").encode("utf-8")
    affected = set(item["objective_ids"])
    while True:
        expanded = affected | {oid for oid, objective in track["objectives"].items()
                               if set(objective["prerequisites"]) & affected}
        if expanded == affected:
            break
        affected = expanded
    record = {"id": correction_id, "concern_id": cid, "track_id": item["track_id"],
              "objective_ids": sorted(affected), "reported_objective_ids": item["objective_ids"][:], "revision": revision + 1,
              "path": relative, "sha256": digest(data), **copy.deepcopy(spec), "affected_lessons": []}
    for lid, lesson in ws.state["lessons"].items():
        if lesson["track_id"] != item["track_id"] or not set(lesson["objective_ids"]) & affected:
            continue
        record["affected_lessons"].append(lid)
        lesson.setdefault("context_reviews", {})[correction_id] = {"status": "pending", "reason": spec["announcement"]}
        if lesson["report_id"]:
            for oid in set(lesson["objective_ids"]) & affected:
                ws.state.setdefault("evidence_reviews", []).append({"report_id": lesson["report_id"], "objective_id": oid,
                    "assessment_ids": [], "status": "pending", "reason": spec["announcement"], "correction_id": correction_id})
    atomic_bytes(ws.path(relative), data)
    ws.state.setdefault("corrections", {})[correction_id] = record
    track["content_revision"] = revision + 1
    item.update(status="corrected", correction_id=correction_id)
    ws.recompute(item["track_id"])
    ws.save("content-corrected", {"correction_id": correction_id, "announcement": spec["announcement"]})
    return record


def review_context(ws, lid, spec):
    fields(spec, ("correction_id", "status", "reason"))
    require(lid in ws.state["lessons"], "unknown lesson")
    lesson = ws.state["lessons"][lid]
    require(spec["correction_id"] in lesson.get("context_reviews", {}), "correction does not affect this lesson")
    require(spec["status"] in ("safe-to-resume", "replace", "pending"), "invalid context review status")
    string(spec["reason"], "context relevance reason")
    lesson["context_reviews"][spec["correction_id"]] = copy.deepcopy(spec)
    ws.state.setdefault("context_review_history", []).append({"lesson_id": lid, **copy.deepcopy(spec)})
    ws.save("context-reviewed", {"lesson_id": lid, **spec})
    return {"lesson_id": lid, **spec}


def context_ready(lesson):
    return all(r["status"] == "safe-to-resume" for r in lesson.get("context_reviews", {}).values())


def stale_reasons(ws, lesson):
    reasons = []
    if not context_ready(lesson):
        reasons.append("Issued context is affected by a content correction")
    for correction in ws.state.get("corrections", {}).values():
        if (correction["track_id"] == lesson["track_id"]
                and correction["revision"] > lesson.get("content_revision", 0)
                and set(correction["objective_ids"]) & set(lesson["objective_ids"])):
            reasons.append("Report uses earlier teaching content: " + correction["id"])
    if lesson.get("replaced_by"):
        reasons.append("Report belongs to a replaced packet")
    elif lesson["status"] == "abandoned":
        reasons.append("Late report belongs to an explicitly retired packet")
    return reasons


def correction_context(ws, tid, oids):
    from .engine import digest
    notes = []
    for correction in ws.state.get("corrections", {}).values():
        if correction["track_id"] == tid and set(correction["objective_ids"]) & set(oids):
            data = ws.path(correction["path"]).read_bytes()
            require(digest(data) == correction["sha256"], "correction artifact checksum changed")
            notes.append(f"### Correction {correction['id']} (revision {correction['revision']})\n"
                         + data.decode("utf-8") + "\nLimitations: " + "; ".join(correction["limitations"]))
    return "\n\n".join(notes)


def latest_dispositions(reviews):
    layers = {}
    for review in reviews:
        for aid in review["assessment_ids"] or ["*"]:
            layers[(review.get("correction_id", "manual"), aid)] = review
    return layers


def effective_item(ws, record, item):
    """Return a projected copy and dispositions; never edit observed evidence."""
    reviews = [r for r in ws.state.get("evidence_reviews", [])
               if r["report_id"] == record["report"]["report_id"] and r["objective_id"] == item["objective_id"]]
    layers = latest_dispositions(reviews)
    whole = [r for (_, aid), r in layers.items() if aid == "*"]
    if record["invalidated"] or any(r["status"] in ("withdrawn", "pending") for r in whole):
        return None, reviews
    result = copy.deepcopy(item)
    for review in reviews:
        if "judgment" in review:
            result["judgment"] = review["judgment"]
    for attempt in result["assessments"]:
        decisions = [r for (_, aid), r in layers.items() if aid == attempt["assessment_id"]]
        if any(r["status"] == "pending" for r in decisions):
            return None, reviews
        if any(r["status"] == "withdrawn" for r in decisions):
            attempt.update(valid=False, result="ungradable", independent=False)
    from .sidechat import qualify
    from .implementation import qualify as implementation_qualify
    return implementation_qualify(ws, record["lesson_id"], qualify(ws, record["lesson_id"], result)), reviews


def review_evidence(ws, spec):
    fields(spec, ("report_id", "objective_id", "assessment_ids", "status", "reason"),
           ("correction_id", "judgment", "replacement"))
    require(spec["report_id"] in ws.state["reports"], "unknown report")
    record = ws.state["reports"][spec["report_id"]]
    item = next((o for o in record["report"]["objectives"] if o["objective_id"] == spec["objective_id"]), None)
    require(item is not None, "objective not in report")
    strings(spec["assessment_ids"], "assessment IDs")
    require(len(set(spec["assessment_ids"])) == len(spec["assessment_ids"])
            and set(spec["assessment_ids"]) <= {a["assessment_id"] for a in item["assessments"]}, "unknown/duplicate assessment")
    require(spec["status"] in ("retained", "withdrawn", "pending"), "invalid evidence status")
    string(spec["reason"], "evidence review reason")
    if "correction_id" in spec:
        correction = ws.state.get("corrections", {}).get(spec["correction_id"])
        require(correction and record["lesson_id"] in correction["affected_lessons"]
                and spec["objective_id"] in correction["objective_ids"], "unrelated correction review")
        require(not spec["assessment_ids"], "resolve correction relevance for the whole affected objective")
    if "judgment" in spec:
        require(spec["judgment"] in ("demonstrated", "needs-practice", "uncertain"), "invalid reviewed judgment")
    if "replacement" in spec:
        replacement = spec["replacement"]
        fields(replacement, ("report_id", "assessment_id"))
        other = ws.state["reports"].get(replacement["report_id"])
        require(other and other["report"]["track_id"] == record["report"]["track_id"], "unknown replacement report")
        target = next((o for o in other["report"]["objectives"] if o["objective_id"] == spec["objective_id"]), None)
        require(target and any(a["assessment_id"] == replacement["assessment_id"] for a in target["assessments"]),
                "replacement must reference actual evidence for the same objective")
    ws.state.setdefault("evidence_reviews", []).append(copy.deepcopy(spec))
    ws.recompute(record["report"]["track_id"])
    ws.save("evidence-reviewed", spec)
    return copy.deepcopy(spec)


def validate_gap_links(ws, report):
    known = {}
    for record in ws.state["reports"].values():
        if record["report"]["track_id"] == report["track_id"] and record["report"]["report_id"] != report["report_id"]:
            for item in record["report"]["objectives"]:
                for gap in item.get("gaps", []):
                    known[gap["id"]] = (item["objective_id"], record["report"]["completed_on"])
    for item in report["objectives"]:
        for gap in item.get("gaps", []):
            require(gap["id"] not in known, "gap ID already exists; resolve it rather than redefining it")
            known[gap["id"]] = (item["objective_id"], report["completed_on"])
        for repair in item.get("resolved_gaps", []):
            target = known.get(repair["gap_id"])
            require(target and target[0] == item["objective_id"] and target[1] <= report["completed_on"],
                    "gap resolution needs an existing earlier gap for this objective")


def project_gaps(ws, tid, records):
    track = ws.track(tid)
    for objective in track["objectives"].values():
        objective["gaps"] = {}
    track["unscoped_notes"] = []
    for record in records:
        report = record["report"]
        if not record["invalidated"] and (report["misconceptions"] or report["prerequisite_gaps"]):
            track["unscoped_notes"].append({"report_id": report["report_id"],
                "misconceptions": report["misconceptions"], "prerequisite_gaps": report["prerequisite_gaps"]})
        for original in report["objectives"]:
            objective = track["objectives"][original["objective_id"]]
            item, reviews = effective_item(ws, record, original)
            for gap in original.get("gaps", []):
                status = "open" if item is not None else "withdrawn"
                if item is None and not record["invalidated"] and any(r["status"] == "pending" for r in latest_dispositions(reviews).values()):
                    status = "pending"
                if item is not None and gap["assessment_ids"]:
                    support = [a for a in item["assessments"] if a["assessment_id"] in gap["assessment_ids"]]
                    if not any(a["valid"] for a in support):
                        status = "withdrawn"
                objective["gaps"][gap["id"]] = {**copy.deepcopy(gap), "report_id": report["report_id"],
                    "status": status, "resolutions": []}
            if item is None:
                continue
            success, contradiction, _ = evidence_outcome(item["assessments"], KINDS[objective["kind"]])
            for repair in item.get("resolved_gaps", []):
                gap = objective["gaps"].get(repair["gap_id"])
                attempt = next(a for a in item["assessments"] if a["assessment_id"] == repair["assessment_id"])
                if (gap and gap["status"] in ("open", "resolved") and success and not contradiction
                        and item["judgment"] == "demonstrated" and item["coverage"] == "covered"
                        and attempt.get("phase") == "assessment" and qualifies(attempt, KINDS[objective["kind"]])):
                    gap["status"] = "resolved"
                    gap["resolutions"].append({"report_id": report["report_id"], **copy.deepcopy(repair)})
