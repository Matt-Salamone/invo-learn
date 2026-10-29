# 02: Reconcile partial lessons through one workspace-wide pending slot

**Status:** ready-for-agent

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Prepare an ordinary course lesson, return an in-progress report, preserve incomplete progress, and release or explicitly retire its checkout so another lesson can start. Enforce one pending handoff across all courses, with reusable behavior for later assignment handoffs.

**Blocked by:** 01 — Install and use the single invo-learn entry point.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 34, 35, 36, 37, 38, 39, 41, 42, 43, 44.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → pending handoff, report archives and mailbox. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Preparing in a second course is blocked while any main handoff is pending, including competing writers; validation failure leaves the existing mailbox and archive unchanged.
- [ ] In-progress returns are saved exactly and record only actual evaluated progress. Resolving or retiring the checkout does not mark unfinished objectives or the lesson complete.
- [ ] Restaging and explicit replacement preserve issued originals; paused work can resume later through a fresh handoff.
- [ ] Main and supplemental reports retain their distinct effects: a supplement does not create another checkout or independently close the main one.
- [ ] Malformed, repaired, duplicate and late returns retain conservative evidence behavior without reopening retired checkouts or duplicating progress.
- [ ] An installed two-course journey verifies the whole cycle at S1; update superseded per-course concurrency expectations rather than preserving contradictory behavior.
