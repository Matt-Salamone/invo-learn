"""Source-preserving context reduction and inspectable packet preflight."""
import copy
import uuid

from .contracts import fields, require, string, strings


def assessment(value):
    fields(value, ("basis", "relevance", "uncertainty"))
    for name in value:
        string(value[name], name)


def source(ws, tid, selection):
    from .engine import digest
    fields(selection, ("material_id",), ("derived_id",))
    materials = ws.track(tid)["materials"]
    require(selection["material_id"] in materials, "unknown attachment")
    material = materials[selection["material_id"]]
    require(material["status"] == "usable", "source needs inspection/approved transformation")
    if "derived_id" in selection:
        item = next((d for d in material["derived"] if d["id"] == selection["derived_id"]), None)
        require(item is not None, "unknown derived artifact")
        relative = item["path"]
    else:
        item, relative = material, material["original"]
    path = ws.path(relative)
    data = path.read_bytes()
    require(digest(data) == item["sha256"], "source checksum changed")
    return path, data, copy.deepcopy(item)


def reduce_context(ws, tid, spec):
    from .engine import atomic_bytes, digest
    fields(spec, ("material_id", "mode", "source_locator", "assessment", "critical_details", "omissions", "limitations"),
           ("derived_id", "pages", "content", "method"))
    assessment(spec["assessment"])
    string(spec["source_locator"], "source locator")
    for name in ("omissions", "limitations"):
        strings(spec[name], name)
    selection = {k: spec[k] for k in ("material_id", "derived_id") if k in spec}
    path, data, parent = source(ws, tid, selection)
    if spec["mode"] == "text-pages":
        pages = spec.get("pages")
        require(isinstance(pages, list) and pages and all(type(p) is int and p > 0 for p in pages)
                and len(set(pages)) == len(pages), "unique positive page numbers required")
        try:
            originals = data.decode("utf-8-sig").split("\f")
        except UnicodeError as exc:
            raise ValueError("text-pages needs readable UTF-8; inspect or obtain conversion permission first") from exc
        require(max(pages) <= len(originals), "page outside source")
        content = "\n\n".join(originals[p - 1] for p in pages)
        method = "Select form-feed-delimited text pages in supplied order"
    else:
        require(spec["mode"] == "summary", "reduction mode must be summary or text-pages")
        content, method = spec.get("content"), spec.get("method")
        string(content, "planner-authored summary")
        string(method, "summary method")
    require(isinstance(spec["critical_details"], list) and spec["critical_details"], "critical detail verification required")
    for detail in spec["critical_details"]:
        fields(detail, ("detail", "evidence"))
        string(detail["detail"], "critical detail")
        string(detail["evidence"], "retained passage")
        require(detail["evidence"] in content, "critical detail passage absent from reduction")
    did = "d-" + uuid.uuid4().hex[:12]
    relative = f"tracks/{tid}/materials/derived/{did}/context.txt"
    encoded = content.encode("utf-8")
    record = {"id": did, "path": relative, "sha256": digest(encoded), "bytes": len(encoded),
              "note": "Verified packet reduction; passage presence is not semantic proof",
              "reduction": {k: copy.deepcopy(v) for k, v in spec.items() if k != "content"}}
    record["reduction"].update(source_path=path.relative_to(ws.root).as_posix(),
                               source_sha256=parent["sha256"], method=method)
    atomic_bytes(ws.path(relative), encoded)
    ws.track(tid)["materials"][spec["material_id"]]["derived"].append(record)
    ws.save("context-reduced", {"track_id": tid, "derived_id": did})
    return record


def preflight(ws, tid, spec):
    """Metrics are measured; semantic checks remain explicit planner attestations."""
    track = ws.track(tid)
    require(isinstance(spec, dict), "lesson spec must be an object")
    string(spec.get("context"), "source-grounded teaching context")
    require(isinstance(spec.get("attachments"), list), "attachments must be a list")
    review = spec.get("quality_review")
    if review is not None:
        fields(review, ("assessment", "critical_details", "omissions", "limitations", "checks"), ("budget_bytes",))
        assessment(review["assessment"])
        for name in ("critical_details", "omissions", "limitations"):
            strings(review[name], name)
        require(review["critical_details"], "name the details checked for completeness")
        fields(review["checks"], ("self_contained", "critical_details_verified", "assessment_safe", "references_verified"))
        require(all(type(v) is bool for v in review["checks"].values()), "packet checks must be booleans")
        require("budget_bytes" not in review or type(review["budget_bytes"]) is int and review["budget_bytes"] > 0,
                "budget_bytes must be a positive integer")
    included, warnings = [], []
    for selection in spec["attachments"]:
        path, data, record = source(ws, tid, selection)
        entry = {**selection, "name": path.name, "bytes": len(data), "sha256": record["sha256"]}
        try:
            entry["text_characters"] = len(data.decode("utf-8-sig"))
        except UnicodeError:
            entry["text_characters"] = None
        if "reduction" in record:
            entry["reduction"] = record["reduction"]
            warnings.extend(record["reduction"]["limitations"] + record["reduction"]["omissions"])
        included.append(entry)
    # Includes explanatory context, not provider-specific token or binary upload estimates.
    context_bytes = len((spec["context"] + spec.get("supplemental_context", "")).encode("utf-8"))
    total = context_bytes + sum(f["bytes"] for f in included)
    if review is None:
        warnings.append("Planner content checks not recorded; inspect the packet in a fresh-chat dry run")
    else:
        warnings.extend(review["limitations"] + review["omissions"])
        warnings.extend("Packet check failed: " + k for k, v in review["checks"].items() if not v)
        if "budget_bytes" in review and total > review["budget_bytes"]:
            warnings.append("Selected context exceeds the planner's byte budget; reduce or split it")
    assigned_materials = {r["material_id"] for oid in spec.get("objective_ids", []) if oid in track["objectives"]
                          for r in track["objectives"][oid]["sources"]}
    inventory = [item for item in track.get("section_inventory", []) if item["material_id"] in assigned_materials]
    for item in inventory:
        if not item["complete"]:
            warnings.append("Incomplete source inspection: " + item["material_id"] + ": " + item["inspection_note"])
    return {"included": included, "attachment_count": len(included), "context_bytes": context_bytes,
            "selected_bytes": total, "quality_review": copy.deepcopy(review), "warnings": warnings,
            "source_inventory": copy.deepcopy(inventory),
            "content_checked": review is not None and all(review["checks"].values()),
            "limit_note": "Byte/text counts are measured; upload/token limits and semantic completeness are not verified"}


def objective_context(obj):
    """Bound handoff history without discarding durable evidence or current gaps."""
    result = copy.deepcopy({k: v for k, v in obj.items() if k != "evidence"})
    evidence = obj.get("evidence", [])
    uncertainties = result.get("uncertainties", [])
    result["uncertainties"] = uncertainties[-10:]
    if len(uncertainties) > 10:
        result["earlier_uncertainty_count"] = len(uncertainties) - 10
    gaps = result.get("gaps", {})
    resolved = [key for key, gap in gaps.items() if gap["status"] in ("resolved", "withdrawn")]
    if len(resolved) > 3:
        omitted = set(resolved[:-3])
        result["gaps"] = {key: gap for key, gap in gaps.items() if key not in omitted}
        result["earlier_closed_gap_count"] = len(omitted)
    result["evidence_summary"] = {"reports": len(evidence),
        "recent_reports": [{k: e[k] for k in ("report_id", "completed_on", "mode", "invalidated")}
                           for e in evidence[-3:]],
        "note": "Detailed attempts remain in private records; current understanding/retention are authoritative packet context"}
    return result


def report_template(lesson):
    return {"schema_version": 1, "report_id": "report-" + uuid.uuid4().hex[:12],
            "lesson_id": lesson["id"], "track_id": lesson["track_id"], "completed_on": None,
            "objectives": [{"objective_id": oid, "coverage": "unassessed", "judgment": "uncertain",
                            "assessments": [], "gaps": [], "resolved_gaps": []} for oid in lesson["objective_ids"]],
            "misconceptions": [], "prerequisite_gaps": [], "recommended_next_steps": [], "suspected_errors": []}
