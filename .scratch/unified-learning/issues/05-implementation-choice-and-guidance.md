# 05: Choose and complete guided or independent implementation

**Status:** ready-for-agent

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** At the transition to implementation, ask a fresh guidance question and either prepare a guided implementation session or record independent implementation progress. The chatbot guides; the learner edits and runs the deliverable.

**Blocked by:** 03 — Study a course-owned assignment without an upfront solution.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 21, 22, 23, 24, 25, 26, 27.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → implementation decision, optional guidance packet and progress report. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] The guidance decision is asked when implementation is reached, without a saved/inferred yes or no; resumption retains an answer to the same decision.
- [ ] Guide in manageable steps using explanations, prompts and hints first; permit direct code or worked steps when requested, recording actual help and timing.
- [ ] An independent choice does not create a spurious chatbot checkout. A guided session uses the one global pending slot and records partial as well as completed work.
- [ ] Implementation completion is inspectable against assignment deliverables but does not itself establish independent understanding.
- [ ] The guidance decision does not depend on whether an upfront solution exists. Demonstrate the no-reference path now; the release matrix combines it with ticket 04.
- [ ] Verify the installed decision → packet/work → report/status paths at S1, including the learner/planner/chatbot responsibility split.
