# Unified learning implementation

## Notes

The approved [spec](spec.md) and numbered [tickets](issues/) define the task
graph. Implementation uses `codex/unified-learning`; ticket branches merge into
that integration branch. The accepted S1 seam and component v0.1, timing v0.3
and pending-boundary v0.2 views remain the verification contract.

Only reusable code, instructions and synthetic fixtures belong here. Actual
learner reports, inventories and migration results remain private.

## Decisions-so-far

- [02](issues/02-single-pending-and-partial-reports.md#answer): all courses
  share one serialized pending slot; partial returns retain incomplete history
  and release the checkout. Implementation `70c3d0c`; six installed S1 checks,
  lifecycle/automation/side-chat regressions and the worked example passed.
- [07](issues/07-read-legacy-records.md#answer): canonical legacy inspection
  retains original identities and exact packet/revision associations without
  converting sources or adding progress. Implementation `538089d`; eight installed
  S1 legacy tests passed with before/after source hashes.
- [01](issues/01-canonical-entry-point.md): installed setup, intake, study and
  maintenance share the sole invo-learn entry point. Implementation `a159d2c`;
  all 106 tests and the worked example passed before integration.
- Baseline: all 105 existing tests passed before implementation. Local PlantUML
  1.2024.8 regenerated the accepted component view and its preview was inspected.
- [14](issues/14-collect-checked-out-chat-reports.md): resolved by the owner's
  explicit October 29 loss-acceptance waiver. Preserve existing evidence and
  retire missing-return checkouts incomplete; schedule fresh checks/relearning.

## Fog

- Final private cutover (15) requires actual-return reconciliation or recorded
  explicit waivers, identified private repositories, verified private bindings,
  and a completed public release (13). Public synthetic verification cannot
  satisfy live integrity and remote-verification gates.
