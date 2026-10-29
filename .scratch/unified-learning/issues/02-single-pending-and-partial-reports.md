# 02: Reconcile partial lessons through one workspace-wide pending slot

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Prepare an ordinary course lesson, return an in-progress report, preserve incomplete progress, and release or explicitly retire its checkout so another lesson can start. Enforce one pending handoff across all courses, with reusable behavior for later assignment handoffs.

**Blocked by:** 01 — Install and use the single invo-learn entry point.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 34, 35, 36, 37, 38, 39, 41, 42, 43, 44.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → pending handoff, report archives and mailbox. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Preparing in a second course is blocked while any main handoff is pending, including competing writers; validation failure leaves the existing mailbox and archive unchanged.
- [x] In-progress returns are saved exactly and record only actual evaluated progress. Resolving or retiring the checkout does not mark unfinished objectives or the lesson complete.
- [x] Restaging and explicit replacement preserve issued originals; paused work can resume later through a fresh handoff.
- [x] Main and supplemental reports retain their distinct effects: a supplement does not create another checkout or independently close the main one.
- [x] Malformed, repaired, duplicate and late returns retain conservative evidence behavior without reopening retired checkouts or duplicating progress.
- [x] An installed two-course journey verifies the whole cycle at S1; update superseded per-course concurrency expectations rather than preserving contradictory behavior.

## Answer

The serialized prepare operation now checks every prepared main handoff in the
workspace before creating packet artifacts or touching the mailbox. The existing
operation lock also prevents competing installed-command writers from issuing two
packets. Study updates defer for any pending main handoff, including when a course
argument is supplied. Explicit replacement retains its original archive.

Main v1 reports accept optional `session_status` (`completed` or `in-progress`);
legacy omission preserves the earlier completed-report meaning. New empty report
templates start in-progress. A partial return releases the pending slot with
`paused` lesson history while projecting only its actual evaluated evidence.
Status exposes lesson history separately from current course understanding and
retention. Fresh packets resume study; archived returns and issued bytes remain
unchanged. Side reports retain their separate coverage/help effect and never
release the main slot. Late first returns for retired packets are preserved and
quarantined through existing objective-specific import relevance review; accepted
late evidence does not reopen or close another checkout. Duplicate protection and
linked formatting repairs remain intact.

`tests/test_single_pending.py` verifies six installed S1 journeys: cross-course
refusal with unchanged mailbox/archive bytes, evaluated partial progress without
completion/retention claims, reviewed late returns, competing subprocess writers,
malformed/repaired partial returns without invented progress, and separate side
reports. Updated superseded concurrency expectations in workflow, automation and
replacement tests. Updated canonical instructions, generated workspace guidance,
report template/schema and user documentation.

Validation: 6 installed S1 tests, 54 workflow tests, 14 automation tests, 6 side-chat
tests, the targeted installed replacement/relevance journey, and
`python examples/worked_example.py` passed. Accepted seam S1/component v0.1 and
complementary timing v0.3/pending-boundary v0.2 remain unchanged. The parent owns
the map resolution pointer and the final integrated full-suite run.
