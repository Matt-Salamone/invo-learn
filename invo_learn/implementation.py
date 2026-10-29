"""Explicit implementation choices and deliverable progress, separate from mastery."""
import copy
import uuid

from .contracts import fields, require, string, strings


QUESTION = "Would you like guidance while implementing your own assignment deliverable?"


def begin(ws, tid, aid, reason):
    from .assignments import checked_assignment, checked_plan
    record = checked_assignment(ws, tid, aid)
    string(reason, "actual transition to implementation")
    require(record["active_plan"] is not None, "accept an assignment lesson plan before reaching implementation")
    checked_plan(ws, record, record["active_plan"])
    if "implementation" in record:
        current = record["implementation"]
        return {"status": "already-started", "decision": copy.deepcopy(current["decision"]),
                "question": QUESTION if current["decision"] is None else None}
    record["implementation"] = {"reason": reason, "decision": None, "decision_history": [], "progress": []}
    ws.save("implementation-reached", {"track_id": tid, "assignment_id": aid})
    return {"status": "reached", "question": QUESTION, "decision": None}


def current(ws, tid, aid):
    from .assignments import checked_assignment
    record = checked_assignment(ws, tid, aid)
    require("implementation" in record, "reach implementation before asking about guidance")
    return record, record["implementation"]


def choose(ws, tid, aid, guided, reason, new_decision=False):
    record, implementation = current(ws, tid, aid)
    require(type(guided) is bool, "guidance requires an explicit yes or no")
    string(reason, "actual learner guidance choice")
    existing = implementation["decision"]
    if existing is not None and not new_decision:
        require(existing["guided"] == guided, "guidance already answered; record an explicit new decision to change it")
        return {"status": "already-recorded", "decision": copy.deepcopy(existing)}
    if existing is not None:
        implementation["decision_history"].append(copy.deepcopy(existing))
    decision = {"id": "decision-" + uuid.uuid4().hex[:12], "guided": guided, "reason": reason}
    implementation["decision"] = decision
    ws.save("implementation-guidance-choice", {"track_id": tid, "assignment_id": aid, "decision": decision})
    return {"status": "recorded", "decision": copy.deepcopy(decision)}


def validate_progress(record, payload, objective_ids):
    fields(payload, ("deliverables", "checks", "assistance", "limitations"))
    strings(payload["limitations"], "implementation limitations")
    require(isinstance(payload["deliverables"], list), "deliverables must be a list")
    seen = set()
    for item in payload["deliverables"]:
        fields(item, ("deliverable", "status", "evidence"))
        require(item["deliverable"] in record["spec"]["deliverables"] and item["deliverable"] not in seen,
                "unknown or duplicate implementation deliverable")
        seen.add(item["deliverable"])
        require(item["status"] in ("not-started", "in-progress", "completed"), "invalid deliverable status")
        string(item["evidence"], "actual deliverable evidence")
    require(isinstance(payload["checks"], list), "implementation checks must be a list")
    seen = set()
    for check in payload["checks"]:
        fields(check, ("criterion", "result", "method", "evidence"))
        require(check["criterion"] in record["spec"]["criteria"] and check["criterion"] not in seen,
                "unknown or duplicate implementation criterion")
        seen.add(check["criterion"])
        require(check["result"] in ("passed", "failed", "limited"), "invalid implementation check result")
        string(check["method"], "actual implementation check method")
        string(check["evidence"], "actual implementation check evidence")
    require(isinstance(payload["assistance"], list), "implementation assistance must be a list")
    for help_item in payload["assistance"]:
        fields(help_item, ("question", "help", "timing", "objective_ids"))
        string(help_item["question"], "implementation question")
        string(help_item["help"], "actual implementation help")
        require(help_item["timing"] in ("before-answer", "after-answer", "unknown"), "invalid implementation help timing")
        strings(help_item["objective_ids"], "implementation help objectives")
        require(set(help_item["objective_ids"]) <= set(objective_ids), "help references unknown implementation objective")


def update_completion(record, reports=None):
    deliverables, checks = {}, {}
    for event in record["implementation"]["progress"]:
        if event.get("report_id") and reports is not None and reports[event["report_id"]]["invalidated"]:
            continue
        for item in event["progress"]["deliverables"]:
            deliverables[item["deliverable"]] = item["status"]
        for item in event["progress"]["checks"]:
            checks[item["criterion"]] = item["result"]
    complete = (all(deliverables.get(name) == "completed" for name in record["spec"]["deliverables"])
                and all(checks.get(name) == "passed" for name in record["spec"]["criteria"]))
    record["completion"] = "completed" if complete else "in-progress" if deliverables or checks else "not-started"


def record_independent(ws, tid, aid, payload):
    from .engine import atomic, digest
    record, implementation = current(ws, tid, aid)
    decision = implementation["decision"]
    require(decision is not None, "record an explicit guidance choice before implementation work")
    require(decision["guided"] is False, "return guided-session progress through its actual main report")
    validate_progress(record, payload, ws.track(tid)["objectives"])
    for prior in implementation["progress"]:
        if prior.get("decision_id") == decision["id"] and prior["progress"] == payload:
            return {"status": "already-recorded", "progress_id": prior["id"], "completion": record["completion"]}
    pid = "progress-" + uuid.uuid4().hex[:12]
    path = f"tracks/{tid}/assignments/{aid}/implementation/{pid}.json"
    event = {"id": pid, "decision_id": decision["id"], "progress": copy.deepcopy(payload), "source": "independent-work"}
    atomic(ws.path(path), event)
    implementation["progress"].append(event | {"path": path, "sha256": digest(ws.path(path).read_bytes())})
    update_completion(record, ws.state["reports"])
    ws.save("implementation-progress", {"track_id": tid, "assignment_id": aid, "progress_id": pid})
    return {"status": "recorded", "progress_id": pid, "completion": record["completion"]}


def next_actions(record, context):
    implementation = record.get("implementation")
    if implementation is not None and implementation["decision"] is None:
        return [{"action": "ask-implementation-guidance", **context, "question": QUESTION}]
    return []


def prepare_context(ws, tid, record, selection, spec, context):
    if selection.get("phase") != "implementation":
        return spec, context
    _, implementation = current(ws, tid, record["id"])
    decision = implementation["decision"]
    require(decision is not None, "record an explicit guidance choice before preparing implementation")
    require(decision["guided"] is True, "independent implementation has no chatbot checkout; record actual work instead")
    context["implementation"] = {"decision_id": decision["id"], "guided": True,
        "deliverables": copy.deepcopy(record["spec"]["deliverables"]), "criteria": copy.deepcopy(record["spec"]["criteria"])}
    spec["context"] += (
        "\n\n## Guided implementation\n\n"
        "The learner edits and runs their own deliverable; the planner maintains records and the chatbot guides. "
        "Guide one manageable implementation step at a time using explanations, prompts and hints first. "
        "Give direct code or worked steps when the learner explicitly requests them; record the actual help and its timing. "
        "An earlier no to an upfront reference does not prohibit requested help during this chosen guidance session. "
        "Record actual deliverable progress and criterion checks in implementation_progress, including partial work and limitations. "
        "Describe requested code, worked steps and task-specific explanations in assistance with affected objective_ids, question and "
        "before-answer/after-answer/unknown timing. Neutral syntax-sheet lookup alone is not assistance. "
        "Keep completed deliverables separate from fresh independent assessment; completion and assisted work do not certify mastery. "
        "Use a fresh unaided check after guided work and later review for retention. "
        "If interrupted, return session_status=in-progress without inventing completed work.\n")
    return spec, context


def report_template(lesson):
    if "implementation" not in lesson.get("assignment_context", {}):
        return {}
    return {"implementation_progress": {"deliverables": [], "checks": [], "assistance": [], "limitations": []}}


def validate_report(obj, lesson):
    implementation = lesson.get("assignment_context", {}).get("implementation")
    if implementation is None:
        require("implementation_progress" not in obj, "implementation progress requires an issued implementation session")
        return
    require("implementation_progress" in obj, "implementation session needs actual progress, including an empty partial record")
    validate_progress({"spec": implementation}, obj["implementation_progress"], lesson["objective_ids"])


def record_report(ws, lesson, obj):
    if "implementation_progress" not in obj:
        return
    context = lesson["assignment_context"]
    record, implementation = current(ws, lesson["track_id"], context["assignment_id"])
    implementation["progress"].append({"id": obj["report_id"], "report_id": obj["report_id"],
        "decision_id": context["implementation"]["decision_id"], "source": "main-report",
        "progress": copy.deepcopy(obj["implementation_progress"]), "lesson_id": lesson["id"]})


def recompute_track(ws, tid):
    for record in ws.track(tid).get("assignments", {}).values():
        if "implementation" in record:
            update_completion(record, ws.state["reports"])
