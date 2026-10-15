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
    fields(prefs, (), ("teaching_style", "supplemental_research", "remediation", "schedule"))
    for key in ("teaching_style", "remediation"):
        if key in prefs:
            string(prefs[key], key)
    if "supplemental_research" in prefs:
        require(type(prefs["supplemental_research"]) is bool, "supplemental_research must be boolean")
    if "schedule" in prefs:
        require(prefs["schedule"] is None or isinstance(prefs["schedule"], dict),
                "schedule must be null or an object with learner-supplied constraints")


def report(obj, lesson, today):
    fields(obj, ("schema_version", "report_id", "lesson_id", "track_id", "completed_on",
                 "objectives", "misconceptions", "recommended_next_steps", "prerequisite_gaps"))
    require(type(obj["schema_version"]) is int and obj["schema_version"] == 1, "unsupported report schema")
    for key in ("report_id", "lesson_id", "track_id"):
        identifier(obj[key])
    require(obj["lesson_id"] == lesson["id"] and obj["track_id"] == lesson["track_id"],
            "report does not match lesson/track")
    completed = date(obj["completed_on"])
    require(date(lesson["prepared_on"]) <= completed <= date(today),
            "report date is before the lesson or in the future")
    for key in ("misconceptions", "recommended_next_steps", "prerequisite_gaps"):
        strings(obj[key], key)
    require(isinstance(obj["objectives"], list), "objectives must be a list")
    ids, assessment_ids = set(), set()
    for item in obj["objectives"]:
        fields(item, ("objective_id", "coverage", "judgment", "assessments"))
        oid = identifier(item["objective_id"])
        require(oid in lesson["objective_ids"] and oid not in ids, "unknown or duplicate objective")
        ids.add(oid)
        require(item["coverage"] in ("covered", "unassessed"), "invalid coverage")
        require(item["judgment"] in ("demonstrated", "needs-practice", "uncertain"), "invalid judgment")
        require(isinstance(item["assessments"], list), "assessments must be a list")
        for a in item["assessments"]:
            fields(a, ("assessment_id", "question", "learner_answer", "rubric", "rationale", "result",
                       "assistance", "assistance_details", "kind", "fresh", "independent", "valid"))
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
    require(ids == set(lesson["objective_ids"]), "report must include every assigned objective; use unassessed when skipped")
    return obj


def qualifies(a, kind):
    return (a["valid"] and a["result"] == "pass" and a["assistance"] == "none"
            and not a["assistance_details"].strip()
            and a["independent"] and a["fresh"] and bool(a["learner_answer"].strip())
            and a["kind"] == kind)


KINDS = {"fact": "recall", "concept": "explain-back", "skill": "application"}
