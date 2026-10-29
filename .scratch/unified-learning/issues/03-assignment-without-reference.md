# 03: Study a course-owned assignment without an upfront solution

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Add an assignment to a course or standalone track, explicitly decline an upfront solution, approve a requirements-grounded plan, take a lesson and ingest its report without any reference-solution record.

**Blocked by:** 02 — Reconcile partial lessons through one workspace-wide pending slot.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 6, 7, 8, 13, 14, 15, 16, 19, 20, 29, 31, 32, 33.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → course-owned assignment, lesson packet and returned report. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Persist requirements, deliverables, criteria and course ownership separately from course objectives and learning evidence.
- [x] An unanswered solution decision stops dependent planning; prior assignments and stored preferences cannot answer it. Resuming the same answered step retains its answer.
- [x] After an explicit no, plan, prepare, ingest and inspect the assignment lesson without fabricating solution artifacts or a solution revision.
- [x] The assignment handoff uses the global pending slot from ticket 02 and the existing mailbox/archive preservation behavior.
- [x] Packets use relevant governing material and no-source-commentary teaching by default, with provenance, meaningful visuals and applicable neutral syntax references preserved.
- [x] Verify the installed no-reference lesson/report journey at S1 and show assignment completion remains separate from course understanding.

## Answer

Added course-owned assignment records and commands in `invo_learn/assignments.py`.
Assignments archive authoritative requirements, deliverables, criteria and material
IDs separately from course objectives/evidence. A standalone project uses an
ordinary track and the same assignment operations. Intake starts with an
unanswered solution choice. Planning requires an actual recorded answer; resuming
retains the same choice and a different assignment starts unanswered.

After an explicit no, propose and accept an immutable requirements-led lesson
plan using accepted course objectives and relevant assignment materials. The
normal prepare/preflight commands accept an assignment-plan lesson selector,
validate requirements/plan/source hashes and preserve the original planner spec.
They account for generated assignment context through the same preflight and use
the existing global pending slot and guarded mailbox/archive. No reference record,
solution revision or placeholder artifact is required or created.

Main and optional side templates echo exact assignment/plan/material lineage.
Foreign or missing report context adds no evidence; valid reports use the existing
conservative course projection and never imply assignment deliverable completion.
Status exposes assignment decisions/plans separately, with actionable unanswered
choice and plan-review entries. Canonical internal assignment instructions explain
the first question, actual approvals, standalone tracks, no-source-commentary
teaching, selected context, useful visuals and neutral coding references.

Four installed S1 journeys in `tests/test_assignments.py` cover choice gating and
resumption, a no-reference plan/lesson/main-and-side-report cycle, forged lineage,
standalone coding packets and preflight parity, global-slot/restage preservation,
requested-but-unverified reference refusal, and damaged-source refusal. Original
planner-spec preservation was also observed red then green. Validation passed:
these 4 journeys, 54 workflow tests, 6 global-pending tests, 6 side-chat tests,
4 syntax-reference tests, 7 onboarding tests, and the worked example. The accepted
S1/component v0.1, timing v0.3 and pending-boundary v0.2 agreements are unchanged.
Reference generation and implementation choices extend this module in tickets
04/05; final integrated release/version verification belongs to ticket 13.
