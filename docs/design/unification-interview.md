# Learning and assignment unification interview

Status: final plan and revised diagram confirmed on October 29, 2026.
The interview is complete and implementation is authorized, subject to the private
report/cutover gate below. Latest-round decisions supersede earlier open notes.
This work extends the prior requirements; it does not reopen unrelated decisions
in requirements.md.

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

## Accepted decisions (October 29, 2026, round 4)

- Allow exactly one pending handoff across the entire learner workspace, including
  all courses and assignments. Reject the proposed per-course/per-assignment pending
  slots. This explicitly supersedes the per-course concurrency requirement added in
  invo-learn 0.4.1. Preserve paused work and issued artifacts without treating them
  as simultaneously checked-out handoffs.
- Before final private cutover, remind the learner to visit every checked-out
  lesson chat and obtain an in-progress report. Wait for the actual reports, save
  and reconcile them, and retire the old pending handoffs before cutover. Do not
  fabricate missing reports or mark unfinished lessons complete. Preserve partial
  progress and history for later resumption through the single pending slot.
  Public implementation and synthetic verification can proceed while reports
  are being collected; the private cutover cannot.
- Implement and test the public combined package first, rehearse migration on
  private copies, then migrate the actual workspace only after preservation checks
  pass and the in-progress reports above have been reconciled.
- After successful migration, add relocation notes and archive the superseded
  public assignment package and private assignment repository as read-only.
  Preserve their histories. Remove obsolete installed entry points after the
  working destination has been verified.
- Verify all four solution/guidance combinations and explicit choice timing;
  outstanding/late report readability; conservative assistance/retention semantics;
  original materials, packets, reports, learner work and provenance preservation;
  idempotent migration; one user-facing invo-learn entry point; non-reorganizing
  ordinary updates; and recovery on rehearsal copies. Run the existing tests,
  worked example and targeted installed-command checks. Update concurrency checks
  to assert the single workspace-wide pending limit.
- Do not give the learner a manual mapping-review queue. Preserve ambiguous legacy
  evidence unchanged, give no unsupported progress credit, and automatically plan
  fresh demonstration or relearning. Err toward repeated learning rather than
  uncertain credit. Missing files, changed original bytes and broken report
  associations are integrity failures: stop cutover and retain usable originals.

## Final confirmation

The learner explicitly confirmed the final plan and revised workspace-wide
pending-boundary view v0.2 on October 29, 2026. This is an accepted proposed design,
not a current-implementation claim: [source](pending-boundaries-v02.puml),
[SVG preview](pending-boundaries-v02.svg). The earlier per-course/per-assignment
sketch was rejected. The source links back to this record; its regenerated local
PNG preview was inspected before saving the accepted artifacts.

Confirmation authorizes public implementation and the agreed staged migration,
subject to the report/cutover gate. Subsequent spec synthesis should carry forward
these decisions and define implementation/testing seams without reopening the
completed product interview.

Private inventories and learner content are deliberately absent from this public
design record.
