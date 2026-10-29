# 04: Study an assignment from an explicitly requested verified reference

**Status:** needs-info

Draft proposal: awaiting approval of the breakdown. Publish after approval as ready-for-agent.

**What to build:** Answer yes to the upfront-solution question, save the planner's worked reference with requirement checks, and issue a reference-led lesson whose report retains exact context lineage.

**Blocked by:** 03 — Study a course-owned assignment without an upfront solution.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 17, 18, 20, 32.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → requested reference, verified context and reference-led lesson/report. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Reference-led planning requires the explicit yes and a saved, verified reference; verification records actual checks and limitations without inventing results.
- [ ] Preserve reference artifacts, revisions, requirement associations and correction provenance.
- [ ] Select relevant reference context instead of automatically attaching all solution artifacts. Retain flat-upload, preflight, attachment-budget, source-fidelity and verified-reduction guarantees.
- [ ] Reference/plan changes do not mutate issued packets or detach later reports from their original context.
- [ ] Verify the reference-led installed journey through S1, including rejection of premature planning and preserved no-reference behavior.
