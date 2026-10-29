# 14: Resolve report collection or accept lost unreported progress

**Status:** resolved

Breakdown approved by the owner on October 29, 2026, then explicitly revised by
the owner during implementation. The owner waived collection and accepted lost
unreported progress. No additional human action is required for this prerequisite.

**What to build:** Record the owner's explicit report-collection waiver so tickets
10 and 15 can retire missing-return checkouts as incomplete, preserving all existing
evidence and artifacts and planning fresh checks without fabricated reports.

**Blocked by:** None (can start immediately).

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 52, 53.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** Explicit owner loss acceptance →
private checkout-specific waiver records → S1 reconciliation. This resolves the
human prerequisite; tickets 10 and 15 perform machine validation and cutover.

## Acceptance criteria

- [x] Offer collection of actual in-progress returns before cutover.
- [x] Record the owner's explicit acceptance of lost unreported progress and
  authorization to reconcile without further intervention.
- [x] Require incomplete retirement with no invented reports, learner responses,
  completion, independent understanding or retention credit.
- [x] Keep private inventories, artifacts and any existing reports out of this
  public decision record; delegate actual validation to tickets 10 and 15.

## Superseded original criteria

The following original collection route is retained for decision history. The
owner's waiver replaces its mandatory-return gate.

- [ ] Remind the learner to obtain reports from every checked-out main lesson chat across the source workspaces; this can begin while public implementation proceeds.
- [ ] Require actual chatbot returns. Do not author substitute learner answers, reconstruct missing assessments as facts or mark unfinished sessions complete.
- [ ] Save returned reports only in the verified private workspace; this public ticket contains no report contents, private inventory or materials.
- [ ] Keep the prerequisite unresolved while any checked-out chat's required report is missing. Machine validation and reconciliation are performed by tickets 10 and 15.
- [ ] This prerequisite requires actual human chat returns, not an AFK code task; an implementation agent must wait rather than fabricate completion.

## Comments

October 29, 2026 implementation run: reminded the owner to obtain actual
in-progress reports from every checked-out main lesson chat and retain the
returns privately. This public ticket remains unresolved; no private reports or
inventory have been supplied to this implementation run.

## Answer

October 29, 2026: the owner explicitly waived collecting lesson-chat returns,
accepted loss of unreported progress and authorized autonomous reconciliation.
This human prerequisite is resolved by that decision, not by receipt of reports.
Tickets 10 and 15 must preserve existing evidence/artifacts, record the waiver,
retire missing-return checkouts as incomplete and arrange fresh checks or
relearning where needed. Do not fabricate reports, answers or completion. The
spec's owner revision supersedes the original mandatory-return criteria above.
