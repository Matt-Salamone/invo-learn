# Unified learning implementation

## Notes

The approved [spec](spec.md) and numbered [tickets](issues/) define the task
graph. Implementation uses `codex/unified-learning`; ticket branches merge into
that integration branch. The accepted S1 seam and component v0.1, timing v0.3
and pending-boundary v0.2 views remain the verification contract.

Only reusable code, instructions and synthetic fixtures belong here. Actual
learner reports, inventories and migration results remain private.

## Decisions-so-far

- [01](issues/01-canonical-entry-point.md): installed setup, intake, study and
  maintenance share the sole invo-learn entry point. Implementation `a159d2c`;
  all 106 tests and the worked example passed before integration.
- Baseline: all 105 existing tests passed before implementation. Local PlantUML
  1.2024.8 regenerated the accepted component view and its preview was inspected.
- [14](issues/14-collect-checked-out-chat-reports.md): owner reminded to obtain
  actual in-progress reports. The human prerequisite remains unresolved.

## Fog

- Final private cutover (15) requires the actual reports (14), explicitly
  identified private repositories, verified private bindings, and a completed
  public release (13). Public synthetic verification cannot satisfy these gates.
