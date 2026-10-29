# 06: Turn assignment work into conservative course evidence and reviews

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Return assignment lesson and implementation evidence, then demonstrate the difference between assisted completion, fresh independent understanding and delayed retention in the shared course plan.

**Blocked by:** 05 — Choose and complete guided or independent implementation.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 28, 43, 44, 45, 46, 60.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → assistance-qualified course evidence, fresh checks and review planning. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Use justified objective associations to share assignment learning with course coverage, gaps and spaced reviews; do not infer mastery merely from deliverable completion.
- [x] Requested solutions, hints and task-specific side-chat help qualify the affected evidence with actual timing. Neutral syntax lookup follows its existing allowance.
- [x] Preserve failed and assisted observations; a fresh independent check can establish understanding without deleting prior attempts.
- [x] Later review distinguishes independent retention from success after reteaching. A side report alone never certifies mastery or closes another handoff.
- [x] Include late main/side report order, duplicate imports and relevant context corrections while preserving original records.
- [x] Verify an installed sequence from guided work to fresh assessment and later review at S1, with corresponding inspectable course outcomes.

## Answer

Actual task-specific help from implementation progress now qualifies the matching
course assessment on a projected copy. Exact question/objective matches with
before-answer or unknown timing cannot certify independence; an unknown objective
scope still qualifies the exact task without broadening to unrelated questions.
Post-answer help alone leaves the prior answer independent. Supplemental and main
reports work in either order, and inspectable `assistance_qualifications` link
effective judgments to the original help records without rewriting observations.
Reference context alone is tutor material, not proof of learner exposure; actual
help annotations govern. Neutral syntax lookup remains permitted.

Five synthetic installed S1 journeys passed, covering guided completion versus
fresh understanding and delayed retention; late side help and both return orders;
failed/guided review attempts followed by relearning; content correction, scoped
review, duplicates and disputes; and unknown-scope help with exact/unrelated tasks.
Five implementation, six supplemental and seventeen quality/recovery regressions
plus the worked example also passed. Accepted component v0.1, timing v0.3 and
pending-boundary v0.2 continue to cover the seam. These tests validate conservative
bookkeeping, not the honesty or quality of actual learner/chatbot judgments.
