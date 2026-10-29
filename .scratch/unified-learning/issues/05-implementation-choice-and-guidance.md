# 05: Choose and complete guided or independent implementation

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** At the transition to implementation, ask a fresh guidance question and either prepare a guided implementation session or record independent implementation progress. The chatbot guides; the learner edits and runs the deliverable.

**Blocked by:** 03 — Study a course-owned assignment without an upfront solution.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 21, 22, 23, 24, 25, 26, 27.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → implementation decision, optional guidance packet and progress report. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] The guidance decision is asked when implementation is reached, without a saved/inferred yes or no; resumption retains an answer to the same decision.
- [x] Guide in manageable steps using explanations, prompts and hints first; permit direct code or worked steps when requested, recording actual help and timing.
- [x] An independent choice does not create a spurious chatbot checkout. A guided session uses the one global pending slot and records partial as well as completed work.
- [x] Implementation completion is inspectable against assignment deliverables but does not itself establish independent understanding.
- [x] The guidance decision does not depend on whether an upfront solution exists. Demonstrate the no-reference path now; the release matrix combines it with ticket 04.
- [x] Verify the installed decision → packet/work → report/status paths at S1, including the learner/planner/chatbot responsibility split.

## Answer

Implemented explicit `begin-implementation`, `implementation-choice` and
`record-implementation` operations through the canonical installed command seam.
Guidance starts unanswered at the actual transition; resumed answers persist and
an explicitly requested later decision preserves earlier choices and help.
Guided packets select `assignment.phase: implementation`, pin the decision and
criteria, and retain the global pending slot. Main reports record partial or
completed deliverables, actual criterion checks, help and timing separately from
course assessments. Independent work creates no chatbot checkout or mastery.
All deliverables and criteria require actual completion/check evidence; session
completion alone does not complete the assignment. Invalidated completion remains
withdrawn even when later independent partial work is recorded.

Verification: five installed S1 implementation journeys passed, plus four
assignment, six global pending-slot and six side-report regression journeys and
the worked example. Tests use only synthetic workspaces and reports. Reused
accepted component v0.1 / timing v0.3 / pending-boundary v0.2; the local renderer
was probed and the unchanged accepted component preview inspected. The four-mode
reference/guidance matrix remains the release ticket's integrated verification.
