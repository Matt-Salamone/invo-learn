"""Strict structural validation; tutor judgments remain reviewable claims."""
import datetime as dt
import re


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value),
            "IDs must be lowercase letters, digits and hyphens (1-64 characters)")
    return value


def string(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be nonempty text")
    return value


def strings(value, label):
    require(isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value),
            f"{label} must be a list of nonempty strings (may be empty)")


def date(value):
    require(isinstance(value, str), "date must be YYYY-MM-DD")
    try:
        result = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise Invalid("date must be YYYY-MM-DD") from exc
    require(result.isoformat() == value, "date must be YYYY-MM-DD")
    return result


def fields(obj, required, optional=()):
    require(isinstance(obj, dict), "expected an object")
    require(set(required) <= obj.keys(), f"missing fields: {sorted(set(required) - obj.keys())}")
    require(not (obj.keys() - set(required) - set(optional)),
            f"unknown fields: {sorted(obj.keys() - set(required) - set(optional))}")


def preferences(prefs):
    fields(prefs, (), ("teaching_style", "supplemental_research", "remediation", "schedule", "auto_update", "auto_backup"))
    for key in ("teaching_style", "remediation"):
        if key in prefs:
            string(prefs[key], key)
    for key in ("supplemental_research", "auto_update", "auto_backup"):
        if key in prefs:
            require(type(prefs[key]) is bool, f"{key} must be boolean")
    if "schedule" in prefs:
        require(prefs["schedule"] is None or isinstance(prefs["schedule"], dict),
                "schedule must be null or an object with learner-supplied constraints")


def report(obj, lesson, today):
    fields(obj, ("schema_version", "report_id", "lesson_id", "track_id", "completed_on",
                 "objectives", "misconceptions", "recommended_next_steps", "prerequisite_gaps"), ("suspected_errors", "session_status", "assignment_context"))
    from .assignments import validate_report_context
    validate_report_context(obj, lesson)
    require(type(obj["schema_version"]) is int and obj["schema_version"] == 1, "unsupported report schema")
    for key in ("report_id", "lesson_id", "track_id"):
        identifier(obj[key])
    require(obj["lesson_id"] == lesson["id"] and obj["track_id"] == lesson["track_id"],
            "report does not match lesson/track")
    require(obj.get("session_status", "completed") in ("completed", "in-progress"), "invalid session_status")
    completed = date(obj["completed_on"])
    require(date(lesson["prepared_on"]) <= completed <= date(today),
            "report date is before the lesson or in the future")
    for key in ("misconceptions", "recommended_next_steps", "prerequisite_gaps"):
        strings(obj[key], key)
    require(isinstance(obj["objectives"], list), "objectives must be a list")
    ids, assessment_ids = set(), set()
    for item in obj["objectives"]:
        fields(item, ("objective_id", "coverage", "judgment", "assessments"), ("gaps", "resolved_gaps"))
        oid = identifier(item["objective_id"])
        require(oid in lesson["objective_ids"] and oid not in ids, "unknown or duplicate objective")
        ids.add(oid)
        require(item["coverage"] in ("covered", "unassessed"), "invalid coverage")
        require(item["judgment"] in ("demonstrated", "needs-practice", "uncertain"), "invalid judgment")
        require(isinstance(item["assessments"], list), "assessments must be a list")
        phased = any(isinstance(a, dict) and "phase" in a for a in item["assessments"])
        earlier, teaching_started = {}, False
        for a in item["assessments"]:
            fields(a, ("assessment_id", "question", "learner_answer", "rubric", "rationale", "result",
                       "assistance", "assistance_details", "kind", "fresh", "independent", "valid"),
                   ("phase", "before_teaching", "resolves"))
            aid = identifier(a["assessment_id"])
            require(aid not in assessment_ids, "duplicate assessment_id")
            assessment_ids.add(aid)
            for key in ("question", "rubric", "rationale"):
                string(a[key], key)
            require(isinstance(a["learner_answer"], str), "learner_answer must be text; empty means no answer")
            require(isinstance(a["assistance_details"], str), "assistance_details must be text")
            require(a["result"] in ("pass", "fail", "ungradable"), "invalid assessment result")
            require(a["assistance"] in ("none", "light", "heavy", "answer-revealed"), "invalid assistance")
            require(a["kind"] in ("recall", "explain-back", "application"), "invalid assessment kind")
            for key in ("fresh", "independent", "valid"):
                require(type(a[key]) is bool, f"{key} must be boolean")
            annotations = {"phase", "before_teaching", "resolves"} & a.keys()
            require(not annotations or len(annotations) == 3, "attempt annotations require phase, before_teaching and resolves together")
            require(not phased or len(annotations) == 3, "annotate every attempt for an objective or use the legacy format throughout")
            if annotations:
                require(a["phase"] in ("diagnostic", "practice", "assessment"), "invalid attempt phase")
                require(type(a["before_teaching"]) is bool, "before_teaching must be boolean")
                require(not (teaching_started and a["before_teaching"]), "attempt order cannot return to before_teaching after teaching")
                teaching_started = teaching_started or not a["before_teaching"]
                require(isinstance(a["resolves"], list), "resolves must be a list")
                for resolved in a["resolves"]:
                    identifier(resolved)
                require(len(a["resolves"]) == len(set(a["resolves"])), "duplicate resolution reference")
                for resolved in a["resolves"]:
                    prior = earlier.get(resolved)
                    require(prior is not None and prior["valid"] and prior["result"] == "fail",
                            "resolves must reference an earlier valid failure for the same objective")
                    require(prior["kind"] == a["kind"], "resolution must assess the same kind of performance")
                require(not a["resolves"] or (a["phase"] == "assessment" and qualifies(a, a["kind"])),
                        "only a fresh unaided valid assessment pass may resolve failures")
            earlier[aid] = a
        gap_ids = set()
        require(isinstance(item.get("gaps", []), list), "gaps must be a list")
        for gap in item.get("gaps", []):
            fields(gap, ("id", "kind", "description", "assessment_ids"))
            identifier(gap["id"])
            require(gap["id"] not in gap_ids, "duplicate gap ID")
            gap_ids.add(gap["id"])
            require(gap["kind"] in ("misconception", "prerequisite"), "invalid gap kind")
            string(gap["description"], "gap description")
            strings(gap["assessment_ids"], "gap assessment IDs")
            require(set(gap["assessment_ids"]) <= earlier.keys(), "gap references unknown assessment")
        require(isinstance(item.get("resolved_gaps", []), list), "resolved_gaps must be a list")
        resolved_ids = set()
        for resolution in item.get("resolved_gaps", []):
            fields(resolution, ("gap_id", "assessment_id", "rationale"))
            identifier(resolution["gap_id"])
            require(resolution["gap_id"] not in resolved_ids, "duplicate gap resolution")
            resolved_ids.add(resolution["gap_id"])
            string(resolution["rationale"], "gap repair rationale")
            attempt = earlier.get(resolution["assessment_id"])
            assigned = next(o for o in lesson["objective_snapshot"] if o["id"] == oid)
            require(attempt is not None and attempt.get("phase") == "assessment"
                    and qualifies(attempt, KINDS[assigned["kind"]]), "gap repair requires an actual fresh unaided assessment of the assigned kind")
    require(ids == set(lesson["objective_ids"]), "report must include every assigned objective; use unassessed when skipped")
    require(isinstance(obj.get("suspected_errors", []), list), "suspected_errors must be a list")
    for error in obj.get("suspected_errors", []):
        fields(error, ("objective_ids", "claim", "reasoning", "source_reference"))
        strings(error["objective_ids"], "affected objectives")
        require(error["objective_ids"] and set(error["objective_ids"]) <= ids, "unknown error objective")
        for key in ("claim", "reasoning", "source_reference"):
            string(error[key], key)
    return obj


def qualifies(a, kind):
    return (a["valid"] and a["result"] == "pass" and a["assistance"] == "none"
            and not a["assistance_details"].strip()
            and a["independent"] and a["fresh"] and bool(a["learner_answer"].strip())
            and a["kind"] == kind)


def evidence_outcome(assessments, kind):
    """Return success, unresolved failure, and cold review success; retain all attempts."""
    if not assessments or "phase" not in assessments[0]:
        success = any(qualifies(a, kind) for a in assessments)
        return success, any(a["valid"] and a["result"] == "fail" for a in assessments), success
    unresolved, success, cold_success, cold = set(), False, False, True
    for a in assessments:
        failed = a["valid"] and a["result"] == "fail"
        cold = (cold and a["before_teaching"] and a["phase"] != "practice"
                and a["assistance"] == "none" and not a["assistance_details"].strip() and not failed)
        if failed:
            unresolved.add(a["assessment_id"])
        if a["phase"] == "assessment" and qualifies(a, kind):
            success = True
            unresolved.difference_update(a["resolves"])
            cold_success = cold_success or cold
    # A later lapse or relearning does not become evidence of retained knowledge.
    return success, bool(unresolved), cold_success and cold


KINDS = {"fact": "recall", "concept": "explain-back", "skill": "application"}
