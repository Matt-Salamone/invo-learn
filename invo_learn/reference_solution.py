"""Immutable planner reference artifacts, attested checks and selected excerpts."""
import copy
import uuid
from pathlib import Path

from .contracts import fields, identifier, require, string, strings


def checked(ws, assignment, reference_id=None, verified=True):
    from .engine import digest, read_json
    reference_id = reference_id or assignment.get("active_reference")
    references = assignment.get("references", {})
    require(reference_id in references, "requested reference must be saved and verified before planning")
    record = references[reference_id]
    path = ws.path(record["path"])
    require(path.is_file() and digest(path.read_bytes()) == record["sha256"], "reference manifest checksum changed")
    snapshot = read_json(path)
    require(all(record.get(key) == value for key, value in snapshot.items()), "reference differs from its immutable manifest")
    require(snapshot["assignment_sha256"] == assignment["sha256"], "reference requirements association changed")
    for artifact in snapshot["artifacts"]:
        original = ws.path(artifact["path"])
        require(original.is_file() and digest(original.read_bytes()) == artifact["sha256"], "reference artifact checksum changed")
    require(not verified or snapshot["verified"], "requested reference must pass all governing checks before planning")
    return record


def save(ws, tid, aid, spec):
    from .assignments import checked_assignment
    from .engine import atomic, atomic_bytes, digest, no_links
    assignment = checked_assignment(ws, tid, aid)
    require(assignment["solution_choice"] is not None and assignment["solution_choice"]["generate"] is True,
            "reference generation requires this assignment's explicit yes")
    fields(spec, ("provenance", "artifacts", "sections", "checks", "limitations"), ("correction_of", "correction_reason"))
    string(spec["provenance"], "actual reference provenance")
    strings(spec["limitations"], "reference limitations")
    require(isinstance(spec["artifacts"], list) and spec["artifacts"], "reference artifacts required")
    payloads = {}
    for artifact in spec["artifacts"]:
        fields(artifact, ("id", "file", "description"))
        identifier(artifact["id"])
        require(artifact["id"] not in payloads, "duplicate reference artifact ID")
        string(artifact["description"], "reference artifact description")
        source = no_links(Path(artifact["file"])).resolve()
        require(source.is_file(), "reference artifact file missing")
        payloads[artifact["id"]] = (source, source.read_bytes(), artifact["description"])
    require(isinstance(spec["sections"], list), "reference sections must be a list")
    sections, section_ids = [], set()
    for section in spec["sections"]:
        fields(section, ("id", "artifact_id", "start_line", "end_line", "purpose"))
        identifier(section["id"])
        require(section["id"] not in section_ids, "duplicate reference section ID")
        section_ids.add(section["id"])
        string(section["purpose"], "selected reference section purpose")
        require(section["artifact_id"] in payloads, "section has unknown reference artifact")
        try:
            lines = payloads[section["artifact_id"]][1].decode("utf-8-sig").splitlines(keepends=True)
        except UnicodeError as exc:
            raise ValueError("selected reference sections require readable UTF-8; retain opaque originals separately") from exc
        require(type(section["start_line"]) is int and type(section["end_line"]) is int
                and 1 <= section["start_line"] <= section["end_line"] <= len(lines), "reference section line range invalid")
        text = "".join(lines[section["start_line"] - 1:section["end_line"]])
        sections.append(copy.deepcopy(section) | {"sha256": digest(text.encode("utf-8")), "text": text})
    require(isinstance(spec["checks"], list), "reference checks must be a list")
    covered = {key: set() for key in ("requirements", "deliverables", "criteria")}
    for check in spec["checks"]:
        fields(check, ("requirements", "deliverables", "criteria", "method", "result", "evidence", "artifact_sha256"))
        require(check["artifact_sha256"] == {aid: digest(data) for aid, (_, data, _) in payloads.items()},
                "checked artifact hashes differ from the reference bytes; rerun verification for this revision")
        for key in covered:
            strings(check[key], "checked " + key)
            require(set(check[key]) <= set(assignment["spec"][key]), "reference check refers to unknown " + key)
            if check["result"] == "passed":
                covered[key].update(check[key])
        require(any(check[key] for key in covered), "each reference check needs governing associations")
        for key in ("method", "evidence"):
            string(check[key], "actual reference check " + key)
        require(check["result"] in ("passed", "failed", "not-run"), "invalid reference check result")
    verified = bool(spec["checks"]) and all(c["result"] == "passed" for c in spec["checks"]) and all(
        covered[key] == set(assignment["spec"][key]) for key in covered)
    correction = None
    if "correction_of" in spec:
        require(spec["correction_of"] == assignment.get("active_reference"), "correction must name the current reference revision")
        prior = checked(ws, assignment, spec["correction_of"], verified=False)
        string(spec.get("correction_reason"), "reference correction reason")
        correction = {"id": prior["id"], "sha256": prior["sha256"], "reason": spec["correction_reason"]}
    else:
        require("correction_reason" not in spec, "correction reason requires correction_of")
    reference_id = "reference-" + uuid.uuid4().hex[:12]
    revision = len(assignment.get("references", {})) + 1
    directory = f"tracks/{tid}/assignments/{aid}/references/{reference_id}"
    artifacts = []
    for artifact_id, (source, data, description) in payloads.items():
        path = f"{directory}/artifacts/{artifact_id}/{source.name}"
        atomic_bytes(ws.path(path), data)
        artifacts.append({"id": artifact_id, "path": path, "sha256": digest(data), "bytes": len(data),
                          "original_name": source.name, "origin_path": str(source), "description": description})
    snapshot = {"id": reference_id, "revision": revision, "assignment_sha256": assignment["sha256"],
                "provenance": spec["provenance"], "artifacts": artifacts, "sections": sections,
                "checks": copy.deepcopy(spec["checks"]), "limitations": copy.deepcopy(spec["limitations"]),
                "verified": verified, "previous_reference": assignment.get("active_reference"), "correction": correction}
    path = f"{directory}/reference.json"
    atomic(ws.path(path), snapshot)
    assignment.setdefault("references", {})[reference_id] = {**snapshot, "path": path, "sha256": digest(ws.path(path).read_bytes())}
    assignment["active_reference"] = reference_id
    ws.save("assignment-reference-saved", {"track_id": tid, "assignment_id": aid, "reference_id": reference_id, "verified": verified})
    return {"status": "recorded", "reference_id": reference_id, "revision": revision, "verified": verified}


def ready(assignment):
    reference = assignment.get("references", {}).get(assignment.get("active_reference"))
    return bool(reference and reference["verified"])


def planning_reference(ws, assignment):
    if not assignment["solution_choice"]["generate"]:
        return None
    reference = checked(ws, assignment)
    return {key: reference[key] for key in ("id", "revision", "sha256")}


def validate_sections(ws, assignment, lesson):
    selected = lesson.get("reference_sections", [])
    strings(selected, "selected reference sections")
    require(len(selected) == len(set(selected)), "duplicate reference section selection")
    if not assignment["solution_choice"]["generate"]:
        require(not selected, "no-reference lessons cannot inject reference context")
        return
    reference = checked(ws, assignment)
    require(selected and set(selected) <= {s["id"] for s in reference["sections"]}, "select relevant verified reference sections for each reference-led lesson")


def require_current_plan(ws, assignment, plan):
    require(plan["solution_choice"] == assignment["solution_choice"], "solution decision changed; propose and accept a plan for the current explicit choice")
    current = planning_reference(ws, assignment)
    require(plan.get("reference") == current, "reference changed; propose and accept a new plan for the current revision")
    return current


def selected_context(ws, assignment, plan, lesson):
    reference = require_current_plan(ws, assignment, plan)
    if reference is None:
        return None, ("The learner declined an upfront reference solution. During conceptual study do not generate or inject a task-specific completed solution. ")
    record = checked(ws, assignment, reference["id"])
    sections = {s["id"]: s for s in record["sections"]}
    chosen = [sections[sid] for sid in lesson["reference_sections"]]
    lineage = {**reference, "sections": [{"id": s["id"], "sha256": s["sha256"]} for s in chosen]}
    text = "\n\n## Selected verified reference excerpts (tutor context)\n\n"
    for section in chosen:
        text += (f"Section {section['id']}: {section['purpose']}\n"
                 f"Original artifact {section['artifact_id']}, lines {section['start_line']}-{section['end_line']}.\n"
                 + section["text"] + "\n")
    text += ("Verification limitations: " + "; ".join(record["limitations"]) + "\n"
             "The planner recorded actual verification methods/results in the private reference manifest. "
             "Treat verification as documented evidence with these limits, not a proof of every possible behavior. "
             "Use only these selected reference excerpts to ground teaching. Begin with explanations and prompts; "
             "give direct task-specific code/worked steps when the learner requests them and record actual help/timing. "
             "Fresh independent checks must use new tasks after assisted work.\n")
    return lineage, text


def stale_reasons(ws, lesson):
    context = lesson.get("assignment_context", {})
    issued = context.get("reference")
    if not issued:
        return []
    assignment = ws.track(lesson["track_id"]).get("assignments", {}).get(context["assignment_id"])
    if not assignment:
        return ["Assignment reference association is missing; inspect the preserved original packet"]
    active = assignment.get("references", {}).get(assignment.get("active_reference"))
    if active is None or any(issued[key] != active[key] for key in ("id", "revision", "sha256")):
        return ["Issued packet uses an earlier reference revision; review objective relevance before progress credit"]
    return []
