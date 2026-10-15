"""Offline synthetic lesson cycles; no real learner data or paid chatbot required."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PUBLIC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PUBLIC))
from invo_learn.engine import Workspace, atomic, digest
from invo_learn.install import bootstrap, package, upgrade


def assessment(aid="q-1", kind="application", assistance="none", result="pass"):
    question, answer, rubric = {
        "application": ("Solve 4x + 3 = 19 and explain the operations.",
                        "Subtract 3 on both sides, then divide by 4: x=4; 4(4)+3=19.",
                        "Before attempt: correct x; preserve equality and explain inverse operations."),
        "explain-back": ("Why must an inverse operation be applied to both sides?",
                         "To preserve equality; applying it on only one side changes the equation.",
                         "Before attempt: explain equality preservation in the learner's own words."),
        "recall": ("For 500g of flour, recall the salt mass at 2%.", "10 grams.",
                   "Before attempt: state 10g without help.")}[kind]
    return {"assessment_id": aid, "question": question, "learner_answer": answer,
            "rubric": rubric, "rationale": "Meets the recorded criteria." if result == "pass" else "Does not meet criteria.",
            "result": result, "assistance": assistance,
            "assistance_details": "Tutor supplied the equality principle before the answer." if assistance != "none" else "",
            "kind": kind, "fresh": True, "independent": assistance == "none", "valid": True}


def make_report(lesson, completed_on, items, report_id="report-synthetic-1"):
    return {"schema_version": 1, "report_id": report_id, "lesson_id": lesson["id"], "track_id": lesson["track_id"],
            "completed_on": completed_on, "objectives": items, "misconceptions": [],
            "recommended_next_steps": ["Use fresh delayed review questions; repair hinted concepts"],
            "prerequisite_gaps": []}


def item(oid, a=None, judgment="demonstrated"):
    return {"objective_id": oid, "coverage": "covered", "judgment": judgment,
            "assessments": [a or assessment()]}


def map_spec(mid, objectives):
    return {"rationale": "Cover every section of these synthetic uploaded notes.", "source_gaps": [],
            "objectives": [{"id": oid, "title": title, "kind": kind,
                "sources": [{"material_id": mid, "locator": locator}], "prerequisites": pre,
                "scope": "included", "reason": ""} for oid, title, kind, locator, pre in objectives]}


def spec(oids, mode="lesson", attachments=None):
    return {"objective_ids": oids, "mode": mode,
            "context": "Synthetic algebra source: apply the same inverse operation on both sides. For ax+b=c, subtract b, divide by nonzero a, and check. Use new coefficients on review.",
            "attachments": attachments or [], "supplemental_context": ""}


def call(ws, method, *args, **kwargs):
    with ws.locked():
        return getattr(ws, method)(*args, **kwargs)


def run_example(base):
    base = Path(base).resolve()
    root = base / "learner-private"
    bootstrap(PUBLIC, root, "Synthetic learner", git=True)
    ws = Workspace(root)
    call(ws, "add_track", "algebra", "Synthetic algebra")
    call(ws, "add_track", "bread", "Synthetic bread", {"teaching_style": "brief recall and practical examples"})
    for filename in ("algebra.md", "bread.md"):
        (ws.mailbox() / filename).write_bytes((PUBLIC / "examples/materials" / filename).read_bytes())
    math = call(ws, "add_material", "algebra", root / "mailbox/algebra.md")
    bread = call(ws, "add_material", "bread", root / "mailbox/bread.md")
    math_map = map_spec(math["id"], [
        ("inverse", "Explain equality-preserving inverse operations", "concept", "Inverse operations", []),
        ("solve", "Solve linear equations and check the result", "skill", "Linear equations", ["inverse"])])
    bread_map = map_spec(bread["id"], [("salt", "Recall salt mass at 2% for 500g flour", "fact", "Salt", [])])
    for tid, mapping in (("algebra", math_map), ("bread", bread_map)):
        proposed = call(ws, "propose_map", tid, mapping)
        call(ws, "accept_map", tid, proposed["proposal_id"], "Synthetic learner approved all sections")
    first = call(ws, "prepare", "algebra", spec(["inverse", "solve"], attachments=[{"material_id": math["id"]}]), "2026-10-14")
    lesson = ws.state["lessons"][first["lesson_id"]]
    report = make_report(lesson, "2026-10-14", [item("inverse", assessment("q-inverse", "explain-back", "heavy")),
                                                item("solve", assessment("q-solve"))])
    # Simulate a downloaded report in staging AND the learner's single report paste.
    atomic(ws.mailbox() / "returned-report.json", report)
    atomic(root / "synthetic-paste.json", report)
    cli = subprocess.run([sys.executable, str(root / "learn.py"), "--today", "2026-10-14", "ingest", str(root / "synthetic-paste.json")],
                         text=True, capture_output=True, check=True)
    assert json.loads(cli.stdout)["status"] == "imported"
    ws = Workspace(root)
    duplicate = call(ws, "ingest", "```json\n" + json.dumps(report, indent=4) + "\n```", "2026-10-14")
    assert duplicate["status"] == "duplicate"
    assert ws.track("algebra")["objectives"]["inverse"]["understanding"] == "needs-practice"
    assert ws.track("algebra")["objectives"]["solve"]["understanding"] == "demonstrated"
    assert ws.track("algebra")["objectives"]["solve"]["retention"] == "unassessed"
    bread_spec = spec(["salt"], attachments=[{"material_id": bread["id"]}])
    bread_spec["context"] = "Synthetic bread source, Salt: at 2% of flour mass, 500g flour calls for 10g salt. Assess recall without hints."
    second = call(ws, "prepare", "bread", bread_spec, "2026-10-14")
    bread_report = make_report(ws.state["lessons"][second["lesson_id"]], "2026-10-14", [item("salt", assessment("q-salt", "recall"))], "report-bread-1")
    call(ws, "ingest", json.dumps(bread_report), "2026-10-14")
    due = ws.status("2026-10-15")["due_reviews"]
    assert {d["track_id"] for d in due} == {"algebra", "bread"}
    third = call(ws, "prepare", "algebra", spec(["solve"], "review"), "2026-10-15")
    review_a = assessment("q-fresh-review")
    review_a.update(question="Solve 5x - 7 = 18 and check.", learner_answer="Add 7 to both sides: 5x=25. Divide by 5: x=5; 25-7=18.")
    review_report = make_report(ws.state["lessons"][third["lesson_id"]], "2026-10-15", [item("solve", review_a)], "report-review-1")
    call(ws, "ingest", json.dumps(review_report), "2026-10-15")
    solve = ws.track("algebra")["objectives"]["solve"]
    assert solve["retention"] == "demonstrated" and solve["review"]["due_on"] == "2026-10-18"
    assert ws.path(math["original"]).read_bytes() == (PUBLIC / "examples/materials/algebra.md").read_bytes()
    assert (root / "lessons" / first["lesson_id"] / "packet/START-HERE.md").exists()
    assert list((root / "inbox/mailbox-snapshots").rglob("returned-report.json"))
    # Exercise a newer synthetic release; it is NOT a real published version.
    _, _, files, _ = package(PUBLIC)
    future = base / "synthetic-package-next"
    for name, data in files.items():
        p = future / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    (future / "VERSION").write_text("0.2.2\n", encoding="utf-8")
    before = copy.deepcopy(ws.state)
    with ws.locked():
        updated = upgrade(ws, future)
    assert ws.state["profile"] == before["profile"] and ws.state["tracks"] == before["tracks"]
    assert ws.state["reports"] == before["reports"] and ws.state["lessons"] == before["lessons"]
    final = call(ws, "prepare", "algebra", spec(["inverse"]), "2026-10-15")
    return {"synthetic_only": True, "workspace": str(root), "tracks": ["algebra", "bread"],
            "duplicate_import": duplicate["status"], "hinted_concept": "needs-practice",
            "independent_skill": "demonstrated", "delayed_retention": "demonstrated",
            "next_skill_review": "2026-10-18", "cross_track_due_count": len(due),
            "mailbox_originals_packets_and_return_preserved": True,
            "synthetic_upgrade": updated["version"], "next_handoff": final["lesson_id"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, help="new external directory; retain the synthetic workspace for inspection")
    args = p.parse_args()
    if args.output:
        if args.output.exists():
            p.error("--output must be a new directory")
        result = run_example(args.output)
        print(json.dumps(result, indent=2))
    else:
        with tempfile.TemporaryDirectory(prefix="invo-learn-example-") as temp:
            result = run_example(temp)
            result["workspace"] = "temporary workspace verified and removed; use --output to retain"
            print(json.dumps(result, indent=2))
