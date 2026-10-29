# 10: Gate migration on actual in-progress lesson reports

**Status:** ready-for-agent

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Reconcile checked-out source lessons using actual returns or explicit learner acceptance of lost unreported progress, preserve incomplete history, and report whether the staged destination is eligible for cutover. Use synthetic returns and waivers only in public tests.

**Blocked by:** 08 — Rehearse a lossless combined-workspace import.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 37, 38, 40, 41, 52, 53, 57.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → migration / report readers → reconciled staged sessions and cutover eligibility. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Inventory all checked-out sessions and offer collecting in-progress reports. Missing returns block final cutover unless an explicit recorded loss-acceptance waiver covers those checkouts. The owner supplied that waiver for their cutover on October 29, 2026 (ticket 14).
- [ ] Save exact returned reports and verify original packet/context associations before resolving pending checkouts.
- [ ] Retire reconciled legacy checkouts without pretending unfinished lessons are complete; retain their progress for later resumption through one pending slot.
- [ ] Duplicate reports/reconciliation retries are idempotent. Valid late returns remain readable without reopening multiple pending sessions.
- [ ] A malformed return or broken association cannot be replaced with fabricated evidence; report an actionable integrity problem and preserve sources.
- [ ] Verify eligible, missing-report, invalid-association and retry journeys through installed S1 commands; use only synthetic returns in public tests.
- [ ] Verify waiver-driven retirement with no synthetic learner evidence: preserve existing observations/artifacts, keep sessions incomplete, and schedule fresh checks/relearning for uncertain progress. An explicit waiver does not bypass altered-file or broken-report integrity failures.
