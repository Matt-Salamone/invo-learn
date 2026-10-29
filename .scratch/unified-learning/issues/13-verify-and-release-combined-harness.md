# 13: Verify and release the complete combined public harness

**Status:** claimed

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Run the integrated installed product through all four assignment modes, sequential multi-course study and migration/recovery; finish public documentation and publish a versioned combined distribution only when the full contract passes.

**Blocked by:** 04 — Study an assignment from an explicitly requested verified reference; 11 — Activate, retry and recover an explicitly migrated workspace; 12 — Update the combined harness without silently migrating data.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 60, 61, 62.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study / migration / installer → complete synthetic installed journey and immutable release. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Exercise reference/no-reference × guided/independent implementation with explicit question timing and unchanged historical exposure.
- [ ] Run a two-track installed journey covering sequential handoffs, main/side reports, independent checks, delayed review, legacy rehearsal, report gates, activation and next study.
- [ ] Run the required unittest suite, worked example and targeted installed-command journeys; teaching packet evaluations retain their documented limits.
- [ ] Confirm only invo-learn is delivered as the learner entry point and all supported older records remain readable.
- [ ] Review code/assets transferred from the public assignment product for license/attribution obligations; exclude all real learner data and credentials.
- [ ] Keep VERSION and changelog aligned; publish a new immutable version rather than changing an already distributed version. Document setup, both choices, partial reporting, single checkout, migration and recovery.
- [ ] Carry the accepted S1/component and complementary diagram references into the verification evidence; do not claim synthetic tests prove live account setup or learner independence.
