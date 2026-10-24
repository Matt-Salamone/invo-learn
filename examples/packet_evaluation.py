"""Generate synthetic fresh-chat evaluation packets through the installed CLI.

No chatbot is contacted. Retain cases with --output OUTSIDE the public checkout.
Without --output, verify packet construction in a temporary directory and remove it.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PUBLIC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PUBLIC))
from invo_learn.contracts import require
from invo_learn.engine import no_links, within
from examples.worked_example import assessment, phased


def run_cases(destination):
    destination = no_links(destination).resolve()
    require(not within(destination, PUBLIC) and not within(PUBLIC, destination), "evaluation output must be outside the public checkout")
    require(not destination.exists() or destination.is_dir() and not any(destination.iterdir()), "evaluation output must be new or empty")
    destination.mkdir(parents=True, exist_ok=True)
    cases = []
    for name in ("novice", "cold-review", "source-conflict", "missing-context"):
        folder = destination / name
        folder.mkdir()
        counter = 0
        def write(obj):
            nonlocal counter
            counter += 1
            path = folder / f"input-{counter}.json"
            path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
            return path
        prefs = write({"auto_update": False, "auto_backup": False})
        workspace = folder / "workspace"
        setup = subprocess.run([sys.executable, "-m", "invo_learn", "bootstrap", str(workspace), "--name", "Synthetic evaluator",
                                "--no-git", "--preferences", str(prefs)], cwd=PUBLIC, capture_output=True, text=True)
        require(setup.returncode == 0, setup.stderr)
        def cli(*args, day="2026-10-14", expected=0):
            result = subprocess.run([sys.executable, str(workspace / "learn.py"), "--today", day, *map(str, args)],
                                    capture_output=True, text=True)
            require(result.returncode == expected, result.stdout + result.stderr)
            return json.loads(result.stdout if expected == 0 else result.stderr)
        cli("add-course", "algebra", "--title", "Synthetic packet evaluation")
        source = folder / "source.txt"
        source.write_text("Applying the same inverse operation to both sides preserves equality. "
                          "For 2x+3=11, subtract 3 from both sides and divide by 2: x=4. Check 2(4)+3=11.\n", encoding="utf-8")
        material = cli("add-material", "algebra", source)
        objective = {"id": "equality", "title": "Solve and justify a linear equation", "kind": "skill",
            "sources": [{"material_id": material["id"], "locator": "whole synthetic source"}], "prerequisites": [],
            "scope": "included", "reason": "", "success_criteria": ["Preserve equality, justify inverse operations and check a fresh solution"]}
        mapping = {"rationale": "One synthetic source and objective", "objectives": [objective], "source_gaps": []}
        proposal = cli("propose-map", "algebra", write(mapping))
        cli("accept-map", "algebra", proposal["proposal_id"], "--approval", "Synthetic evaluation scope")
        spec = {"objective_ids": ["equality"], "mode": "lesson", "context": source.read_text(),
                "attachments": [{"material_id": material["id"]}], "supplemental_context": ""}
        if name == "cold-review":
            first = cli("prepare", "algebra", write(spec))
            template = json.loads((workspace / "mailbox/report-template.json").read_text())
            template.update(report_id="synthetic-baseline", completed_on="2026-10-14")
            template["objectives"][0].update(coverage="covered", judgment="demonstrated", assessments=[phased(assessment())])
            cli("ingest", write(template))
            spec["mode"] = "review"
            prepared = cli("prepare", "algebra", write(spec), day="2026-10-15")
            learner = ["Start the review.", "I can solve a fresh problem without a recap.", "After attempting it: ask for the single report."]
            expected = ["Retrieve before explanation or hints", "Use a fresh equation", "Keep actual assistance and before_teaching flags", "Retention only from qualifying delayed cold evidence"]
        elif name == "source-conflict":
            spec["context"] += "\nUnverified teaching note: the worked equation has x=7."
            prepared = cli("prepare", "algebra", write(spec))
            learner = ["The teaching note says x=7, but substitution gives 17. Which is right?", "Ask for the single report."]
            expected = ["Inspect the conflicting source and calculation", "Disclose the suspected error with reasoning", "Do not grade the learner against the wrong worked value", "Report suspected_errors without claiming durable correction"]
        elif name == "missing-context":
            spec["context"] = "Teach the mechanism in the unavailable diagram."
            spec["attachments"] = []
            spec["quality_review"] = {"assessment": {"basis": "Inspected candidate", "relevance": "Required figure absent", "uncertainty": "Cannot recover missing labels"},
                "critical_details": ["Missing figure mechanism"], "omissions": ["Required diagram unavailable"], "limitations": ["Insufficient context"],
                "checks": {"self_contained": False, "critical_details_verified": False, "assessment_safe": False, "references_verified": False}}
            prepared = cli("prepare", "algebra", write(spec), expected=2)
            require(cli("status")["active_lesson"] is None, "failed candidate must not issue a lesson")
            learner = ["Planner-only case: repair the missing context before issuing a packet."]
            expected = ["Preflight discloses the missing figure", "Preparation refuses explicit failed quality checks", "No invented source detail or learner evidence"]
        else:
            prepared = cli("prepare", "algebra", write(spec))
            learner = ["I do not understand why we change both sides.", "Ask for a small hint after the first practice attempt.", "Try a new unaided equation, then request the single report."]
            expected = ["Explain equality causally with a labeled visual and static alternative", "Ask one manageable question and wait", "Record the hint as assistance", "Use a different unaided assessment", "Separate completion, independence and retention"]
        cases.append({"id": name, "synthetic_only": True, "workspace": str(workspace),
                      "packet": str(workspace / "lessons" / prepared["lesson_id"] / "packet") if "lesson_id" in prepared else None,
                      "learner_script": learner, "criteria": expected, "construction_outcome": "refused-as-expected" if name == "missing-context" else "prepared"})
    (destination / "evaluation-cases.json").write_text(json.dumps({"synthetic_only": True, "cases": cases,
        "limits": "Construction verified through the CLI; no chatbot behavior or learning outcome has been evaluated"}, indent=2) + "\n", encoding="utf-8")
    return {"synthetic_only": True, "case_count": len(cases), "prepared": 3, "refused_as_expected": 1,
            "teaching_evaluated": False, "cases_file": str(destination / "evaluation-cases.json")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output:
        result = run_cases(args.output)
    else:
        with tempfile.TemporaryDirectory(prefix="invo-packet-evaluation-") as folder:
            result = run_cases(Path(folder) / "cases")
        result["cases_file"] = "Temporary synthetic cases verified and removed"
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
