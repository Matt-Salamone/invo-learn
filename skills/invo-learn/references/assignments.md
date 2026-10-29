# Assignment study

An assignment belongs to a course. Reuse the matching course when one exists.
For a standalone project, create an ordinary track with `add-course` and a title
that describes the project, then use the same workflow. Keep assignment
requirements, deliverables and acceptance criteria separate from course learning
objectives. Preserve uploaded originals through the existing material intake;
conversion workflows still require actual learner permission.

## Intake and the first decision

Read the governing requirements and materials, register them with add-material,
and propose/accept the source-linked course map through the existing approval
workflow. Register the assignment:

```sh
python learn.py add-assignment <course> <assignment> <private-assignment.json>
```

The JSON contains `title`, nonempty string lists `requirements`, `deliverables`
and `criteria`, and `material_ids` referencing registered authoritative materials.
For example, criteria describe observable deliverable checks; they are not claims
of independent understanding. The command archives the requirements separately
from course objectives and starts with an unanswered solution choice.

Before planning this assignment's lessons, ask exactly one explained question:
**"Would you like me to generate and verify a reference solution before planning
the assignment lessons?"** Explain that yes uses a verified reference as one
planning input; no plans directly from the requirements and materials. Wait for
an actual answer. Prior assignments, global preferences, silence and defaults
cannot choose it. On resume read the stored answer and retain it. Record the
actual answer and its reason:

```sh
python learn.py assignment-choice <course> <assignment> --solution yes --reason "<actual learner answer>"
python learn.py assignment-choice <course> <assignment> --solution no --reason "<actual learner answer>"
```

Run only the command matching the answer. Repeating that answer is harmless;
a conflicting answer requires an explicit new decision preserving exposure
history. When the learner explicitly requests a later change, explain and ask the
solution question again, wait for the actual answer, then pass `--new-decision`
with that answer and reason. Prior choices, reference artifacts, issued packets
and actual help remain in history; do not pretend earlier exposure never occurred.
A new choice requires a newly proposed/accepted plan, even if its answer matches
an earlier decision. If yes, read `reference-solutions.md`, complete and verify the requested reference,
then propose a reference-led plan. If no, generate no task-specific completed solution and
create no dummy solution revision or placeholder artifact.

## Requirements-led lessons

After a no answer, propose a requirements-grounded plan. A private plan JSON has
`rationale` and a nonempty `lessons` list. Each lesson has a stable `id`, `title`,
`objective_ids` from the accepted course map, and relevant `material_ids` from the
assignment. Include the source material grounding each selected objective.

```sh
python learn.py propose-assignment-plan <course> <assignment> <private-plan.json>
python learn.py accept-assignment-plan <course> <assignment> <plan-id> --approval "<actual learner approval>"
```

Show the proposed sequence and scope, then wait for actual approval. Existing
explicit approval counts. The plan is an inspectable immutable snapshot; a later
plan keeps the earlier plan and issued packets recoverable.

Prepare a normal private lesson spec with the existing context, attachments,
objectives and quality checks, plus:

```json
{
  "assignment": {
    "assignment_id": "solver",
    "plan_id": "plan-example",
    "lesson_id": "inverse"
  }
}
```

The nested lesson_id identifies a lesson in that accepted assignment plan. It is
separate from the runtime lesson_id generated for each new packet. Use the
normal `preflight` and `prepare` commands. Both validate the same assignment and
plan hashes, selected material lineage and accepted objectives; the existing
packet budget includes the added assignment context. Select usable relevant
attachments instead of uploading every material indiscriminately. Preserve
source grounding and useful visuals. Teach self-contained explanations without
source-title/page commentary, providing provenance separately on request. For
coding lessons use the existing neutral syntax sheet rules.

Preparation uses the one workspace-wide pending main handoff. Return its report
or explicitly retire it before preparing anything else. The packet archives
requirements/plan/material identity in assignment_context. Main and optional
side-report templates copy that exact context; retain it unchanged. Ingest both
through the ordinary report command. Missing or mismatched assignment lineage is
preserved privately without adding evidence. Old issued course packets do not
need this new field.

Course understanding, coverage, gaps and reviews continue to use actual returned
assessment evidence. Conceptual lesson success does not mark the assignment
deliverable complete. A requested reference or assisted work cannot prove
independent understanding or delayed retention. Ask about implementation guidance
only at the later transition to implementation, separately from this upfront
solution decision. The learner edits and runs their final work.
