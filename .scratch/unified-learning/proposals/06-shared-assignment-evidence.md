# 06: Turn assignment work into conservative course evidence and reviews

**Status:** needs-info

Draft proposal: awaiting approval of the breakdown. Publish after approval as ready-for-agent.

**What to build:** Return assignment lesson and implementation evidence, then demonstrate the difference between assisted completion, fresh independent understanding and delayed retention in the shared course plan.

**Blocked by:** 05 — Choose and complete guided or independent implementation.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 28, 43, 44, 45, 46, 60.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → assistance-qualified course evidence, fresh checks and review planning. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Use justified objective associations to share assignment learning with course coverage, gaps and spaced reviews; do not infer mastery merely from deliverable completion.
- [ ] Requested solutions, hints and task-specific side-chat help qualify the affected evidence with actual timing. Neutral syntax lookup follows its existing allowance.
- [ ] Preserve failed and assisted observations; a fresh independent check can establish understanding without deleting prior attempts.
- [ ] Later review distinguishes independent retention from success after reteaching. A side report alone never certifies mastery or closes another handoff.
- [ ] Include late main/side report order, duplicate imports and relevant context corrections while preserving original records.
- [ ] Verify an installed sequence from guided work to fresh assessment and later review at S1, with corresponding inspectable course outcomes.
