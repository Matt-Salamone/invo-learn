# Contracts and evidence policy (v1)

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
  "context": "Source m-from-intake, section 1: ...accurate excerpts or synthesis...",
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
      "valid": true
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

## Deterministic projection

- Coverage records covered versus unassessed independently of grades. Deferral is
  a map scope choice, not a grade. Overviews display all of these separately.
- Understanding is demonstrated only for judgment=demonstrated, covered content
  and a fresh, valid, independent passing answer with **no assistance**, of the
  matching kind. Any valid failing assessment in the same objective report makes
  an otherwise passing judgment uncertain. Hinted/lightly assisted work is retained
  but cannot qualify. A new independent pass can establish performance in a later
  report; prior gaps remain visible for agent review.
- Retention is demonstrated only by a qualifying **review** performed on/after
  the prior due date and on a later calendar day. An early review cannot advance
  intervals or postpone an already scheduled due date. No immediate lesson answer
  establishes retention. Claims of independence/freshness are still tutor assertions.
- The default increasing intervals are **1, 3, 7, 14, 30, 60 days**. The first
  independent lesson pass schedules step 0; each delayed review pass advances one
  step, capped at 60 days and repeated indefinitely. Failed, hinted, invalid,
  unassessed-but-attempted or uncertain attempts reset to step 0 for next-day
  practice; review failures also record a lapse. Skipped objectives leave existing
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
