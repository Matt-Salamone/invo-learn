# Learning and assignment unification interview

Status: interview in progress. These are accepted product decisions, not an
implementation authorization or a complete build brief. Unanswered recommendations
remain proposals. This work extends the prior requirements; it does not reopen
unrelated decisions in requirements.md.

## Accepted decisions (October 29, 2026, round 1)

- invo-learn becomes the combined public product. The learner's existing private
  learning workspace becomes the combined private destination. Public source and
  private learner records remain separate.
- Retain the existing upfront-reference-solution workflow and add a workflow
  that plans lessons directly from assignment requirements and course materials
  without first generating a completed reference solution.
- The learner accepted the initial activity view, v0.1, with an extension:
  guided implementation of the final assignment must be optional with either
  upfront-solution choice. Solution generation and implementation guidance are
  independent choices. Guidance responsibilities and assistance limits remain open.
- Assignment learning contributes to shared course coverage, learning gaps and
  spaced reviews. Assignment completion remains separate from demonstrated
  understanding and delayed retention.

The accepted initial proposed-design view is preserved as
[PlantUML source](assignment-modes-v01.puml) and
[SVG preview](assignment-modes-v01.svg). Its independent-implementation-only ending
is superseded by the explicit guided-implementation extension above; it is not the
complete target workflow. A revised v0.2 sketch is under discussion, not yet accepted.
The source links back to this record. Rendering used local PlantUML 1.2024.8 and
Temurin 25.0.5; the initial PNG preview and revised discussion preview were inspected.

## Open frontier

- Guided implementation: who edits/runs the actual deliverable, and how much
  task-specific help is provided by default?
- Assignment organization within courses, including assignments without a course.
- Initial mode defaults and later switching between modes.
- Source presentation policy: the existing products differ on showing source
  titles/sections during teaching.

Later decisions include legacy packets/reports and evidence, migration recovery,
compatibility entry points, distribution, repository retirement and verification.
Private inventories and learner content are deliberately absent from this public
design record.
