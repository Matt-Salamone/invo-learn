# 03: Study a course-owned assignment without an upfront solution

**Status:** ready-for-agent

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Add an assignment to a course or standalone track, explicitly decline an upfront solution, approve a requirements-grounded plan, take a lesson and ingest its report without any reference-solution record.

**Blocked by:** 02 — Reconcile partial lessons through one workspace-wide pending slot.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 6, 7, 8, 13, 14, 15, 16, 19, 20, 29, 31, 32, 33.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → course-owned assignment, lesson packet and returned report. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Persist requirements, deliverables, criteria and course ownership separately from course objectives and learning evidence.
- [ ] An unanswered solution decision stops dependent planning; prior assignments and stored preferences cannot answer it. Resuming the same answered step retains its answer.
- [ ] After an explicit no, plan, prepare, ingest and inspect the assignment lesson without fabricating solution artifacts or a solution revision.
- [ ] The assignment handoff uses the global pending slot from ticket 02 and the existing mailbox/archive preservation behavior.
- [ ] Packets use relevant governing material and no-source-commentary teaching by default, with provenance, meaningful visuals and applicable neutral syntax references preserved.
- [ ] Verify the installed no-reference lesson/report journey at S1 and show assignment completion remains separate from course understanding.
