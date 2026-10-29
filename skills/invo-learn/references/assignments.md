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
history. If yes, complete and verify the requested reference before proposing
a reference-led plan. If no, generate no task-specific completed solution and
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

## Implementation and the second decision

When conceptual lessons are complete, or the learner explicitly chooses to start
their implementation, record that actual transition. Do not ask about guidance
during intake and do not infer an answer from the reference-solution choice.

```sh
python learn.py begin-implementation <course> <assignment> --reason "<actual transition or learner override>"
```

Ask the returned question, **"Would you like guidance while implementing your own
assignment deliverable?"** Explain that the chatbot can guide manageable steps
while the learner edits and runs their work, or the learner can implement
independently. Wait for the answer, then record only the matching choice:

```sh
python learn.py implementation-choice <course> <assignment> --guidance yes --reason "<actual answer>"
python learn.py implementation-choice <course> <assignment> --guidance no --reason "<actual answer>"
```

Resume the same stored answer. A later explicitly requested change uses
`--new-decision`; this retains earlier decisions, issued packet identities and
assistance. It does not retire a pending handoff or erase prior exposure.

For guidance, prepare an existing accepted assignment lesson with
`"phase": "implementation"` inside the lesson spec's `assignment` selection.
Use the normal preflight, mailbox, report and global pending-slot operations.
The packet pins the guidance decision and deliverable criteria. The chatbot
starts with explanations, prompts and hints, gives direct code or worked steps
when requested, and records actual help with its timing. The learner edits and
runs the deliverable; the planner records evidence and future study decisions.
An earlier no to an upfront reference does not prohibit requested help now.

For independent implementation, create no chatbot checkout. Inspect the learner's
actual work and runs, then save a private progress JSON and record it:

```sh
python learn.py record-implementation <course> <assignment> <actual-progress.json>
```

Both that JSON and a guided main report's `implementation_progress` use:

```json
{
  "deliverables": [{
    "deliverable": "Exact registered deliverable text",
    "status": "in-progress",
    "evidence": "What the learner actually produced or ran"
  }],
  "checks": [{
    "criterion": "Exact registered criterion text",
    "result": "limited",
    "method": "The check actually performed",
    "evidence": "Its observed result"
  }],
  "assistance": [{
    "question": "Actual task or question helped with",
    "help": "Actual explanation, hint, requested code or worked step",
    "timing": "before-answer",
    "objective_ids": ["assigned-objective-id"]
  }],
  "limitations": ["Unchecked behavior or missing evidence"]
}
```

Deliverable status is `not-started`, `in-progress` or `completed`; criterion result
is `passed`, `failed` or `limited`. Assistance timing is `before-answer`,
`after-answer` or `unknown`. Empty lists preserve an interrupted session with no
evaluated work. Neutral syntax lookup alone does not count as assistance.
Use only actual returns and checks; save no invented work to fill a template.

The main report also keeps its ordinary objective assessments and exact
`assignment_context`. Return `session_status: "in-progress"` when interrupted.
Side reports remain supplemental and never certify implementation completion.
Deliverables are complete only when all registered deliverables have recorded
completion evidence and every criterion has a recorded passing check. Session
completion alone is insufficient. Neither independent-work records nor assisted
deliverable completion establishes course mastery. Use fresh independent
assessment and later delayed review for understanding and retention, preserving
all prior assistance and failures.

## Shared course evidence

Use the accepted course objective links in the assignment plan; matching a
deliverable title or finishing a project does not establish understanding.
Ordinary course lessons, assignment lessons and implementation sessions share
the same objective evidence, gaps and spaced-review policy.

Record all actual requested solutions, hints, worked steps and task-specific
explanations with the affected objective and exact assessed question. In a guided
main report, `implementation_progress.assistance` supplements the ordinary
assessment assistance fields. Known before-answer help or unknown timing on the
same objective and task qualifies the claim of independence, even if the raw
assessment incorrectly says `independent: true`. Post-answer explanation alone
does not downgrade an earlier independent answer. The projection keeps original
questions/answers unchanged and exposes `assistance_qualifications` in the course
evidence summary, linking the recorded help and its source report.
An empty objective scope does not erase known help: an exact question match in
the same issued session still qualifies that task, while the original unknown
scope remains recorded. Unrelated questions do not qualify other assessments.

The same rules apply to supplemental side reports, regardless of whether they
arrive before or after the main report. A late supplement qualifies its original
task without downgrading a later fresh task. Inspect unmatched task descriptions
as planner bookkeeping, preserving uncertainty rather than guessing that all
questions received the same help. Neutral syntax lookup alone remains permitted.
Tutor-only reference excerpts and generating a reference are not proof the
learner saw a solution; record actual learner exposure/help instead of inferring
it merely from packet lineage.

After assisted work, use a fresh independent task to demonstrate understanding.
Keep prior failed and guided attempts in their original reports. A fresh pass
after repair during a review is relearning; only a later cold independent review
can demonstrate retention. Context corrections, relevance dispositions and
disputes apply through the existing append-only review workflow; original packets
and reports stay recoverable.
