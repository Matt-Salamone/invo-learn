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
complete target workflow. The two-choice structure of v0.2 was accepted in round 2;
its Q1/Q2 guidance labels are resolved by the responsibilities below. See its
[source](assignment-modes-v02.puml) and [SVG](assignment-modes-v02.svg).
The source links back to this record. Rendering used local PlantUML 1.2024.8 and
Temurin 25.0.5; the initial PNG preview and revised discussion preview were inspected.

## Accepted decisions (October 29, 2026, round 2)

- During guided implementation, the teaching chatbot guides manageable steps;
  the learner edits and runs the assignment. The planner manages context,
  progress, and returned reports through the existing manual handoff workflow.
- Guidance starts with explanations, prompts and hints. Direct code or worked
  steps are allowed when requested. Record actual help; assisted implementation
  is completion evidence, while fresh independent checks establish understanding.
- Each assignment belongs to one course or track. An assignment without a course
  can use a standalone track.
- There are no assumed defaults for upfront solution generation or guided
  implementation. The agent asks at the decision point every time, without
  inheriting an answer from a prior assignment or stored preference. The precise
  timing of these two questions remains to be confirmed.
- Teaching without source-title/page commentary is the combined product default.
  Apply it to existing learner settings during migration as explicitly requested;
  do not silently preserve a conflicting old presentation preference. This changes
  presentation, not source grounding or durable provenance. Explicit overrides
  remain possible. Treatment of already issued immutable packets remains open.

## Accepted decisions (October 29, 2026, round 3)

- Ask about upfront solution generation before planning lessons. Ask about guided
  implementation when the learner reaches implementation. Each new decision
  requires an answer; resuming the same already-answered step retains that answer.
  The learner explicitly accepted the proposed-design timing view v0.3:
  [source](assignment-modes-v03.puml), [SVG](assignment-modes-v03.svg).
- Preserve outstanding handoffs and accept reports from their original packets.
  Update stored presentation settings immediately during migration. New or
  regenerated packets use the new presentation style; issued originals remain
  immutable and can retain their old commentary.
- Preserve original assessments and assistance records. Connect legacy evidence
  conservatively to course objectives and reviews. Independent assignment evidence
  can establish demonstrated understanding where justified, not delayed retention.
  Existing reference solutions and their provenance remain historical facts.
- Import complete files and records, including untracked learner work, into the
  destination repositories. Record originating commits. The destinations get
  explicit migration commits; the original repositories retain their complete
  recoverable Git histories rather than interleaving their commit graphs.
- invo-learn is the single user-facing entry point, with one combined installer
  and updater. Remove obsolete skill and command names; provide no compatibility
  wrappers. Older reports and records remain readable. Workspace migration is
  explicit; ordinary updates must not silently reorganize learner data.

## Open frontier

- Concurrent pending handoffs for a course's ordinary study and its assignments.
- Public implementation, private rehearsal and verified migration order.
- Legacy repository retirement and removal of obsolete installed entry points.
- Preservation, behavior and recovery checks required before cutover.
- Treatment of uncertain evidence mappings versus integrity failures.

Private inventories and learner content are deliberately absent from this public
design record.
