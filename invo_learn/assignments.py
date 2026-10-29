"""Course-owned assignments and explicit requirements-led learning decisions."""
import copy
import uuid

from .contracts import fields, identifier, require, string, strings


def get(ws, tid, aid):
    assignments = ws.track(tid).get("assignments", {})
    require(aid in assignments, "unknown assignment")
    return assignments[aid]


def add(ws, tid, aid, spec):
    from .engine import atomic, digest
    identifier(aid)
    fields(spec, ("title", "requirements", "deliverables", "criteria", "material_ids"))
    string(spec["title"], "assignment title")
    for key in ("requirements", "deliverables", "criteria", "material_ids"):
        strings(spec[key], key)
        require(spec[key] and len(spec[key]) == len(set(spec[key])), f"unique nonempty {key} required")
    track = ws.track(tid)
    require(set(spec["material_ids"]) <= track["materials"].keys(), "assignment uses unknown materials")
    require(any(track["materials"][mid]["role"] == "primary" for mid in spec["material_ids"]), "assignment requires authoritative primary material")
    assignments = track.setdefault("assignments", {})
    existing = assignments.get(aid)
    if existing:
        require(existing["spec"] == spec, "assignment ID already exists with different requirements; preserve its original identity")
        return {"status": "already-recorded", "assignment_id": aid, "track_id": tid}
    snapshot = copy.deepcopy(spec)
    path = f"tracks/{tid}/assignments/{aid}/assignment.json"
    require(not ws.path(path).exists(), "unregistered assignment archive exists; inspect recovery before reusing its identity")
    atomic(ws.path(path), snapshot)
    record = {"id": aid, "track_id": tid, "spec": snapshot, "path": path,
              "sha256": digest(ws.path(path).read_bytes()), "solution_choice": None,
              "plans": {}, "active_plan": None, "completion": "not-started"}
    assignments[aid] = record
    ws.save("assignment-added", {"track_id": tid, "assignment_id": aid})
    return {"status": "added", "track_id": tid, "assignment_id": aid}


def choose_solution(ws, tid, aid, generate, reason):
    record = get(ws, tid, aid)
    require(type(generate) is bool, "solution choice requires explicit yes or no")
    string(reason, "actual learner solution choice")
    existing = record["solution_choice"]
    if existing is not None:
        require(existing["generate"] == generate, "solution choice already recorded; changing it requires a new explicit decision with preserved exposure history")
        return {"status": "already-recorded", "choice": copy.deepcopy(existing)}
    record["solution_choice"] = {"generate": generate, "reason": reason}
    ws.save("assignment-solution-choice", {"track_id": tid, "assignment_id": aid, "generate": generate})
    return {"status": "recorded", "choice": copy.deepcopy(record["solution_choice"])}


def planning_basis(record):
    require(record["solution_choice"] is not None, "record an explicit solution choice before assignment planning")
    require(record["solution_choice"]["generate"] is False, "requested reference must be completed and verified before planning")
    return "requirements"


def checked_assignment(ws, tid, aid):
    from .engine import digest, read_json
    record = get(ws, tid, aid)
    path = ws.path(record["path"])
    require(path.is_file() and digest(path.read_bytes()) == record["sha256"], "assignment requirements archive checksum changed")
    require(read_json(path) == record["spec"], "assignment requirements differ from their immutable archive")
    return record


def check_materials(ws, tid, material_ids):
    from .engine import digest
    materials = ws.track(tid)["materials"]
    result = []
    for mid in material_ids:
        require(mid in materials and materials[mid]["status"] == "usable", "assignment material needs inspection or approved transformation")
        material = materials[mid]
        require(digest(ws.path(material["original"]).read_bytes()) == material["sha256"], "assignment material checksum changed")
        result.append({"material_id": mid, "sha256": material["sha256"]})
    return result


def validate_plan(ws, tid, record, spec):
    fields(spec, ("rationale", "lessons"))
    string(spec["rationale"], "assignment plan rationale")
    require(isinstance(spec["lessons"], list) and spec["lessons"], "assignment plan needs lessons")
    seen = set()
    objectives = ws.track(tid)["objectives"]
    for lesson in spec["lessons"]:
        fields(lesson, ("id", "title", "objective_ids", "material_ids"))
        identifier(lesson["id"])
        require(lesson["id"] not in seen, "duplicate assignment plan lesson")
        seen.add(lesson["id"])
        string(lesson["title"], "assignment lesson title")
        for key in ("objective_ids", "material_ids"):
            strings(lesson[key], key)
            require(lesson[key] and len(lesson[key]) == len(set(lesson[key])), f"unique nonempty {key} required")
        require(set(lesson["objective_ids"]) <= objectives.keys(), "assignment plan needs accepted course objectives")
        require(set(lesson["material_ids"]) <= set(record["spec"]["material_ids"]), "plan material outside assignment scope")
        for oid in lesson["objective_ids"]:
            require(objectives[oid]["scope"] == "included", "accept a scope change before planning deferred objectives")
            require({source["material_id"] for source in objectives[oid]["sources"]} <= set(lesson["material_ids"]),
                    "assignment lesson must retain its objective source grounding")
        check_materials(ws, tid, lesson["material_ids"])


def propose_plan(ws, tid, aid, spec):
    from .engine import atomic, digest
    record = checked_assignment(ws, tid, aid)
    basis = planning_basis(record)
    validate_plan(ws, tid, record, spec)
    for pid, prior in record["plans"].items():
        if prior["spec"] == spec and prior["basis"] == basis:
            return {"status": "already-recorded", "plan_id": pid, "basis": basis}
    pid = "plan-" + uuid.uuid4().hex[:12]
    path = f"tracks/{tid}/assignments/{aid}/plans/{pid}.json"
    snapshot = {"id": pid, "assignment_id": aid, "basis": basis, "spec": copy.deepcopy(spec),
                "assignment_sha256": record["sha256"], "solution_choice": copy.deepcopy(record["solution_choice"]),
                "materials": check_materials(ws, tid, record["spec"]["material_ids"])}
    atomic(ws.path(path), snapshot)
    record["plans"][pid] = {**snapshot, "path": path, "sha256": digest(ws.path(path).read_bytes()), "status": "proposed"}
    ws.save("assignment-plan-proposed", {"track_id": tid, "assignment_id": aid, "plan_id": pid})
    return {"status": "proposed", "plan_id": pid, "basis": basis}


def checked_plan(ws, record, pid):
    from .engine import digest, read_json
    require(pid in record["plans"], "unknown assignment plan")
    plan = record["plans"][pid]
    path = ws.path(plan["path"])
    require(path.is_file() and digest(path.read_bytes()) == plan["sha256"], "assignment plan archive checksum changed")
    snapshot = read_json(path)
    require(all(plan.get(key) == value for key, value in snapshot.items()), "assignment plan differs from its immutable archive")
    return plan


def accept_plan(ws, tid, aid, pid, approval):
    record = checked_assignment(ws, tid, aid)
    plan = checked_plan(ws, record, pid)
    string(approval, "actual learner assignment-plan approval")
    validate_plan(ws, tid, record, plan["spec"])
    if record["active_plan"] == pid:
        return {"status": "already-accepted", "plan_id": pid}
    plan.update(status="accepted", approval=approval)
    record["active_plan"] = pid
    ws.save("assignment-plan-accepted", {"track_id": tid, "assignment_id": aid, "plan_id": pid})
    return {"status": "accepted", "plan_id": pid}


def prepare_context(ws, tid, spec):
    """Build a verified selected context without creating files or dummy solutions."""
    import json
    if "assignment" not in spec:
        return spec, None
    selection = spec["assignment"]
    fields(selection, ("assignment_id", "plan_id", "lesson_id"), ("phase",))
    require(selection.get("phase", "study") in ("study", "implementation"), "invalid assignment session phase")
    record = checked_assignment(ws, tid, selection["assignment_id"])
    basis = planning_basis(record)
    plan = checked_plan(ws, record, selection["plan_id"])
    require(plan["status"] == "accepted" and record["active_plan"] == plan["id"], "accept the assignment plan before preparing its lesson")
    lesson = next((lesson for lesson in plan["spec"]["lessons"] if lesson["id"] == selection["lesson_id"]), None)
    require(lesson is not None, "unknown assignment plan lesson")
    require(set(spec["objective_ids"]) == set(lesson["objective_ids"]), "packet objectives differ from the accepted assignment lesson")
    require({a["material_id"] for a in spec["attachments"]} <= set(lesson["material_ids"]), "attachment outside selected assignment lesson material")
    materials = check_materials(ws, tid, lesson["material_ids"])
    expected_materials = {m["material_id"]: m["sha256"] for m in plan["materials"]}
    require(all(expected_materials[m["material_id"]] == m["sha256"] for m in materials), "assignment material differs from accepted plan lineage")
    context = {"assignment_id": record["id"], "assignment_sha256": record["sha256"], "plan_id": plan["id"],
               "plan_sha256": plan["sha256"], "plan_lesson_id": lesson["id"], "materials": materials}
    text = "\n\n## Assignment requirements and selected learning context\n\n" + json.dumps({
        "title": record["spec"]["title"], "requirements": record["spec"]["requirements"],
        "deliverables": record["spec"]["deliverables"], "criteria": record["spec"]["criteria"],
        "lesson": lesson, "basis": basis, "lineage": context}, indent=2, ensure_ascii=False)
    text += ("\nTeach this self-contained conceptual lesson from the governing requirements and selected material. "
             "Keep provenance for tutor reference and provide it separately when asked; omit source-title/page commentary in teaching. "
             "The learner declined an upfront reference solution. During conceptual study do not generate or inject a task-specific completed solution. "
             "Use meaningful visuals with readable alternatives and neutral syntax lookup when coding. "
             "Assignment deliverable completion is separate from independent understanding and delayed retention.\n")
    enriched = copy.deepcopy(spec)
    enriched["context"] += text
    from .implementation import prepare_context as implementation_context
    return implementation_context(ws, tid, record, selection, enriched, context)


def validate_report_context(obj, lesson):
    expected = lesson.get("assignment_context")
    if expected is None:
        require("assignment_context" not in obj, "unexpected assignment context for course packet")
    else:
        require(obj.get("assignment_context") == expected, "report assignment context does not match exact issued packet lineage")


def next_actions(ws):
    actions = []
    for tid, track in ws.state["tracks"].items():
        for aid, record in track.get("assignments", {}).items():
            context = {"track_id": tid, "assignment_id": aid}
            from .implementation import next_actions as implementation_actions
            actions.extend(implementation_actions(record, context))
            if record["solution_choice"] is None:
                actions.append({"action": "ask-assignment-solution-choice", **context,
                    "question": "Would you like me to generate and verify a reference solution before planning the assignment lessons?"})
            elif not record["plans"]:
                actions.append({"action": "prepare-requested-reference" if record["solution_choice"]["generate"] else "propose-assignment-plan", **context})
            else:
                for pid, plan in record["plans"].items():
                    if plan["status"] == "proposed":
                        actions.append({"action": "review-assignment-plan", **context, "plan_id": pid})
    return actions
