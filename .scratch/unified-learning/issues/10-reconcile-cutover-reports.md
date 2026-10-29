# 10: Gate migration on actual in-progress lesson reports

**Status:** ready-for-agent

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Supply actual or synthetic in-progress returns for every checked-out source lesson, reconcile the old checkouts into preserved incomplete history, and report whether the staged destination is eligible for cutover.

**Blocked by:** 08 — Rehearse a lossless combined-workspace import.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 37, 38, 40, 41, 52, 53, 57.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → migration / report readers → reconciled staged sessions and cutover eligibility. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Inventory all checked-out sessions and remind the learner to obtain their in-progress reports. Missing required returns block final cutover.
- [ ] Save exact returned reports and verify original packet/context associations before resolving pending checkouts.
- [ ] Retire reconciled legacy checkouts without pretending unfinished lessons are complete; retain their progress for later resumption through one pending slot.
- [ ] Duplicate reports/reconciliation retries are idempotent. Valid late returns remain readable without reopening multiple pending sessions.
- [ ] A malformed return or broken association cannot be replaced with fabricated evidence; report an actionable integrity problem and preserve sources.
- [ ] Verify eligible, missing-report, invalid-association and retry journeys through installed S1 commands; use only synthetic returns in public tests.
