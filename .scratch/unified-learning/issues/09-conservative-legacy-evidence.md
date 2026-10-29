# 09: Replace uncertain migration credit with fresh study automatically

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Evaluate rehearsed legacy learning records, retaining justified course evidence while turning ambiguous assignment/objective associations into automatic fresh assessment or relearning needs.

**Blocked by:** 08 — Rehearse a lossless combined-workspace import; 06 — Turn assignment work into conservative course evidence and reviews.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 45, 46, 47, 48.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → migration → staged evidence projection → automatic course checks / relearning. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Preserve every original observation and assistance record regardless of whether it earns mapped credit.
- [x] Map only justified relationships; matching titles, filenames or completed deliverables alone do not establish understanding.
- [x] Ambiguous mappings yield no unsupported credit and schedule fresh demonstration or relearning without requiring the learner to review mapping flags.
- [x] Do not upgrade assisted work into independent understanding or imported independent work into delayed retention.
- [x] Retain unaffected compatible course progress and reviews; conservative handling is scoped to the uncertain associations.
- [x] Verify installed rehearsal/status outputs at S1 for justified, assisted and ambiguous legacy records and the resulting next-study actions.

## Answer

Added explicit `migration-project <stage> [--links <private-file>]` through S1.
Original observations, actual help/timing, origin/packet context and raw returns
remain preserved. Unknown mappings add no credit and create learner-local due-now
fresh-demonstration or relearning actions grounded in governing material. Optional
planner-justified links add at most coverage: historical assignment labels lack
the modern grading/freshness proof needed for independent understanding, and no
imported independent label establishes delayed retention. Existing compatible
course learning/reviews remain unchanged. Historical late returns add no new
mapped credit; metadata variants retain provenance without duplicate observations.

Projection uses the shared stage lock and verifies source/stage preservation.
`migration-status` exposes `projection_current`; the matching Python guard also
detects changed reconciled or supplemental inputs. Activation must require that
guard, refreshing projection after actual returns change. Source snapshots and
issued packets/reports are never rewritten.

Verification: five installed projection journeys passed, plus nine reconciliation,
eight rehearsal/preservation and five shared-evidence journeys and the worked
example. All fixtures are synthetic. Tests reuse accepted S1/component v0.1,
timing v0.3 and pending-boundary v0.2; they establish bookkeeping behavior, not the
truth of a learner's reported performance or a planner's semantic justification.

## Release integration note

The pending fresh-study actions are advisory and retain original needs/history.
This slice schedules them without guessing objective links. The complete
migration-to-next-study journey in ticket 13 still needs an explicit planner-owned
packet linkage and retirement from actual fresh assessment, particularly for
unknown-scope needs. This must not become a learner-facing mapping-review queue
or award mastery merely by clearing an action.
