# 09: Replace uncertain migration credit with fresh study automatically

**Status:** needs-info

Draft proposal: awaiting approval of the breakdown. Publish after approval as ready-for-agent.

**What to build:** Evaluate rehearsed legacy learning records, retaining justified course evidence while turning ambiguous assignment/objective associations into automatic fresh assessment or relearning needs.

**Blocked by:** 08 — Rehearse a lossless combined-workspace import; 06 — Turn assignment work into conservative course evidence and reviews.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 45, 46, 47, 48.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → migration → staged evidence projection → automatic course checks / relearning. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Preserve every original observation and assistance record regardless of whether it earns mapped credit.
- [ ] Map only justified relationships; matching titles, filenames or completed deliverables alone do not establish understanding.
- [ ] Ambiguous mappings yield no unsupported credit and schedule fresh demonstration or relearning without requiring the learner to review mapping flags.
- [ ] Do not upgrade assisted work into independent understanding or imported independent work into delayed retention.
- [ ] Retain unaffected compatible course progress and reviews; conservative handling is scoped to the uncertain associations.
- [ ] Verify installed rehearsal/status outputs at S1 for justified, assisted and ambiguous legacy records and the resulting next-study actions.
