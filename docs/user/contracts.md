# Contracts and evidence policy (v1, with optional ordered attempts since 0.3.0)

The CLI validates these contracts with the Python standard library. The chatbot
receives the JSON Schema in every packet; Python additionally checks assigned
objectives, duplicate keys/IDs, calendar dates, lesson identity and conflicts.
IDs are lowercase letters/digits/hyphens, 1-64 characters. Unknown fields are
rejected so misspellings cannot silently change semantics.

## Coverage map proposal

```json
{
  "rationale": "Cover all uploaded sections; repair prerequisites first",
  "objectives": [{
    "id": "solve-linear",
    "title": "Solve linear equations using inverse operations",
    "kind": "skill",
    "sources": [{"material_id": "m-from-intake", "locator": "Section 1, examples 1-3"}],
    "prerequisites": [],
    "scope": "included",
    "reason": ""
  }],
  "source_gaps": []
}
```

kind is fact/concept/skill; scope is included/deferred (a reason is required for
deferral). Source gaps contain material_id and reason, including unavailable or
deliberately omitted sections. Every primary material must have objective links
or an explicit gap. Locators make coverage inspectable; source-level accounting
does not automatically prove every page was mapped. The agent must inspect all
sections and the learner can revise the map. Proposals do not alter accepted
objectives until accept-map records learner approval. New material or accepted
revisions make older proposals stale. Existing evidenced objective meaning and
kind are immutable; defer and add a new ID when scope changes. Prerequisites must
be other map objectives and acyclic. Deferred objectives retain all evidence.

## Lesson spec supplied by the planning agent

```json
{
  "objective_ids": ["solve-linear"],
  "mode": "lesson",
  "context": "Apply the same inverse operation to both sides to preserve equality. Work through 2x + 3 = 11 with a labeled balance diagram; then assess a fresh equation without hints.",
  "attachments": [{"material_id": "m-from-intake"}],
  "supplemental_context": ""
}
```

mode is lesson/review. Attachments may be empty for a self-contained packet;
each may include derived_id to stage a registered conversion instead of an original.
Context must be nonempty and source-grounded. Supplemental context requires the
track opt-in and is labeled separately. Each packet includes START-HERE.md with
instructions/context, lesson.json with frozen metadata, report.schema.json and
selected sources. Source checksums and the full durable packet are retained.

Default context supplies longer, detailed, comprehensive explanations before
practice, conceptual mechanisms, causal reasoning and justified worked examples.
Honor explicit style overrides and skip demonstrated knowledge.
Context should supply enough definitions, reasoning, examples and figure details
for a self-contained lesson, plus useful visual teaching ideas. Make liberal use
of visuals, including interactive diagrams/charts when supported and useful, with
readable static alternatives otherwise. Explain visuals in words. Source locators
and attachments are tutor references for scope and accuracy: explanations and
questions should teach directly without mentioning pages/files or asking learners
to consult uploads. Provenance can be supplied separately on explicit request.
Visual hints count as assistance; assessment visuals must not reveal the answer.
These are planning/tutor instructions, not content checks enforced by the CLI.

## Report

```json
{
  "schema_version": 1,
  "report_id": "report-linear-1",
  "lesson_id": "lesson-from-packet",
  "track_id": "algebra",
  "completed_on": "2026-10-14",
  "objectives": [{
    "objective_id": "solve-linear",
    "coverage": "covered",
    "judgment": "demonstrated",
    "assessments": [{
      "assessment_id": "q-1",
      "question": "Solve 4x + 3 = 19 and explain each operation.",
      "learner_answer": "Subtract 3 to get 4x=16; divide both sides by 4, so x=4.",
      "rubric": "Before attempt: preserve equality and apply inverse operations; correct x and reasoning.",
      "rationale": "Correct value, equality preserved, operations explained.",
      "result": "pass",
      "assistance": "none",
      "assistance_details": "",
      "kind": "application",
      "fresh": true,
      "independent": true,
      "valid": true,
      "phase": "assessment",
      "before_teaching": false,
      "resolves": []
    }]
  }],
  "misconceptions": [],
  "recommended_next_steps": ["Try a delayed fresh equation review"],
  "prerequisite_gaps": []
}
```

Report every assigned objective exactly once. Skipped objectives use unassessed,
uncertain and empty assessments. Capture actual questions, learner work and rubric
decided before the attempt; assessment IDs are unique within the report.
result is pass/fail/ungradable; assistance is none/light/heavy/answer-revealed;
kind is recall/explain-back/application. Every assessment flag is boolean.
invalid questions use valid=false and ungradable. Empty answers cannot prove
understanding. The tutor's judgment alone cannot establish demonstration.

### Ordered attempts

New handoffs include **phase**, **before_teaching** and **resolves** on every
attempt. All three fields are supplied together, and every attempt for that
objective must be annotated or none may be. The assessments array is chronological;
phase is assigned before the attempt, not retroactively to improve a grade.

- phase is diagnostic (a starting probe), practice (guided work or repair), or
  assessment (a check of independent performance). Only assessment passes qualify
  as demonstrated understanding; a successful diagnostic can justify moving
  directly to an assessment rather than unnecessary instruction.
- before_teaching is true only before any explanation, example, recap or help
  for that objective in this session. Once false, it cannot become true later.
  It captures teaching that may not otherwise appear in the report, without
  requiring a full transcript. It does not replace assistance or freshness flags.
- resolves is an array of earlier valid failure IDs for the **same objective**
  and performance kind, otherwise []. Only a fresh, valid, unaided assessment pass
  can resolve a failure. Its preselected rubric must test the earlier gap and
  its rationale must explain why that gap is resolved. Every unresolved failure
  still blocks demonstrated understanding; later failures need their own repair.
  Neither a practice pass nor an unrelated success resolves an earlier mistake.

For example, a failed diagnostic `q-start`, assisted practice `q-guided`, and a
fresh assessment `q-check` with resolves=["q-start"] can establish understanding.
The first two attempts remain in the evidence. The identical sequence with an
empty resolves list remains uncertain. Keep resolved mistakes in attempt history;
use top-level misconceptions/prerequisite_gaps for gaps still needing attention.

Legacy v1 reports omit all three fields and retain their original conservative
semantics, including any-failure blocking. Old records are not rewritten or
inferred to have phases. Update the harness before importing annotated reports
into an older installation, whose strict reader will reject the new fields.
No package/state/report schema migration is required for this optional v1
extension. The runtime checks annotations and references, but the accuracy of
the phase, timing, rubric and asserted repair remains the tutor's responsibility.

## Deterministic projection

- Coverage records covered versus unassessed independently of grades. Deferral is
  a map scope choice, not a grade. Overviews display all of these separately.
- Understanding is demonstrated only for judgment=demonstrated, covered content
  and a fresh, valid, independent passing answer with **no assistance**, of the
  matching kind. For annotated reports, the pass must have phase=assessment and
  all valid failures must have been explicitly resolved by qualifying later
  assessments. Otherwise a passing judgment is uncertain. In legacy reports,
  any valid failure blocks demonstration. Hinted/lightly assisted work is retained
  but cannot qualify. Prior attempts remain available for agent review.
- Retention is demonstrated only by a qualifying **review** performed on/after
  the prior due date and on a later calendar day. An early review cannot advance
  intervals or postpone an already scheduled due date. No immediate lesson answer
  establishes retention. For annotated reports, the qualifying review must also
  precede teaching/help: no failed attempt, practice, assistance or before_teaching=false
  may occur for that objective in the session. Success after repair demonstrates
  relearning, sets retention=needs-review, resets the interval to the first step
  and records a lapse. A later cold review can restore retention. Claims of
  independence/freshness and teaching timing are still tutor assertions.
  An invalid question alone is not a learner failure: a distinct valid cold
  replacement may establish retention if no teaching/help or valid failure occurred.
- The default increasing intervals are **1, 3, 7, 14, 30, 60 days**. The first
  independent lesson pass schedules step 0; each delayed review pass advances one
  step, capped at 60 days and repeated indefinitely. Without qualifying evidence,
  failed, hinted, invalid, unassessed-but-attempted or uncertain performance resets
  to step 0 for next-day practice; review failures also record a lapse. Skipped objectives leave existing
  review state alone. No calendar schedule is needed and no backlog blocks work.
- Reports are projected in completion-date order, with lesson preparation order
  breaking same-day ties. Exact/normalized duplicates
  never append evidence or move dates. Whole-report disputes withdraw all its
  judgments and recompute due dates from remaining valid reports. Original evidence
  and withdrawal reasons remain inspectable. Interval changes recompute all tracks.

Structural errors reject the whole report, preserving raw input. Semantic conflicts
that can be recorded without guessing are stored conservatively with uncertainty.
Every assessment's full evidence is stored in state.json and the archived report;
no full transcript is required.
