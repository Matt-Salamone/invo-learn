# Unified learning implementation

## Notes

The approved [spec](spec.md) and numbered [tickets](issues/) define the task
graph. Implementation uses `codex/unified-learning`; ticket branches merge into
that integration branch. The accepted S1 seam and component v0.1, timing v0.3
and pending-boundary v0.2 views remain the verification contract.

Only reusable code, instructions and synthetic fixtures belong here. Actual
learner reports, inventories and migration results remain private.

## Decisions-so-far

- [13 verification ready](issues/13-verify-and-release-combined-harness.md#final-verification--ready-for-publication):
  candidate `50fe174` records 197 passing tests with none skipped on final runtime
  `b1c2dbd`, both examples passing and repaired review findings. Version/changelog
  agree on 0.8.0; ticket 13 remains claimed until verified immutable publication
  and release CI. Standards review reported no findings; spec/integrity regressions
  were fixed and independently checked before the final suite.
- [13 documentation](issues/13-verify-and-release-combined-harness.md): interim
  slice `317cf91` routes unified study, migration and maintenance through invo-learn
  and documents release verification limits. Static links, frontmatter and diff
  checks passed; ticket 13 remains claimed until runtime/release verification.
- [11](issues/11-activate-and-recover-migration.md#answer): activation requires
  preservation, projection and reconciliation gates, journals owned writes for
  recovery and retains late returns as historical evidence. Implementation
  `7f7490e`; 11 activation, eight rehearsal, nine reconciliation and five projection
  checks passed. Ticket 13 must require both migration_activation.py and
  migration_late.py in release completeness checks.
- [12 CI correction](issues/12-updates-without-data-reorganization.md#answer):
  `b6665a2` canonicalizes Windows temporary-directory aliases before portable
  attribute containment checks. All 14 maintenance tests passed, including the
  real-alias regression and an external Git-listing escape guard.
- [12](issues/12-updates-without-data-reorganization.md#answer): compatible
  maintenance preserves records and portable Git bytes; layout changes require
  explicit migration and managed guidance respects customization. Implementation
  `60512ca`; 90 targeted checks, the worked example and an actual 0.7 upgrade /
  autocrlf clone smoke check passed. Release packaging must include ticket 11.
- [09](issues/09-conservative-legacy-evidence.md#answer): preserved legacy
  observations earn no unsupported mastery; uncertain associations schedule fresh
  demonstration or relearning, while compatible course progress stays intact.
  Implementation `f3c14e3` / `7e40a2d`; projection, reconciliation, rehearsal and
  evidence checks plus the worked example passed. Ticket 13 must link advisory
  needs to planner-selected packets and close them only from actual fresh evidence.
- [10](issues/10-reconcile-cutover-reports.md#answer): source checkouts require
  exact actual returns or explicit lost-progress waivers; reconciliation preserves
  incomplete history and does not itself authorize activation. Implementation
  `f911426`; nine reconciliation and eight legacy checks passed. Shared stage
  locking is `5d8ce83`; evidence projection remains ticket 09's separate gate.
- [06](issues/06-shared-assignment-evidence.md#answer): shared course evidence
  qualifies task-specific implementation and side-chat help using actual timing,
  preserving raw attempts and separate fresh assessment/review outcomes.
  Implementation `7cfc9f3`; five evidence and seven reference checks passed after
  integration, alongside 28 related checks and the worked example.
- [04](issues/04-verified-reference-path.md#answer): an explicit reference
  request requires saved verification before planning; selected solution context
  retains immutable revision lineage and composes with implementation guidance.
  Implementation `50a4782` / `c406bd3`; 81 targeted checks, post-08 smoke checks
  and the worked example passed.
- [08](issues/08-lossless-migration-rehearsal.md#answer): explicit rehearsal
  preserves source snapshots and hashes, stages course-owned assignments and
  leaves the destination inactive. Implementation `8681e35`; eight installed
  migration checks and eight legacy-reader checks passed against ticket 05.
- [05](issues/05-implementation-choice-and-guidance.md#answer): a fresh guidance
  decision at implementation supports guided handoffs and independent work;
  progress remains separate from mastery. Implementation `c8e3754`; five installed
  implementation journeys, relevant regressions and the worked example passed.
- [03](issues/03-assignment-without-reference.md#answer): course-owned
  assignments retain explicit solution decisions and approved requirements-led
  plans; no-reference lessons use the shared pending slot and exact lineage.
  Implementation `6fd8584`; installed assignment and relevant regression checks
  plus the worked example passed.
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

- [13](issues/13-verify-and-release-combined-harness.md#answer): resolved after
  publishing [v0.8.0](https://github.com/Matt-Salamone/invo-learn/releases/tag/v0.8.0).
  All four CI jobs passed; main and the annotated tag target were verified at
  `ad78efde560dfd595057b6e38a57b49ecb9e50d8`. Ticket 15 is now unblocked by the
  release and the owner's recorded missing-report waiver.
- [13 patch](issues/13-verify-and-release-combined-harness.md#published-patch-verification--october-30-2026):
  [v0.8.1](https://github.com/Matt-Salamone/invo-learn/releases/tag/v0.8.1) fixes
  the generated overview's temporary mailbox path within the activation journal.
  All 197 local tests, four CI jobs and both examples passed; standards/spec
  reviews found no issues. The original 0.8.0 distribution remains immutable.
- [15 partial](issues/15-private-cutover-and-retirement.md#answer--private-cutover-verified-retirement-pending):
  actual private cutover to published 0.8.1 and the ordinary private backup push
  are verified. Existing evidence and preferences remain preserved; waived
  checkouts retired incomplete. Retirement remains pending explicit approval
  after automatic approval review rejected the prepared operation. The ticket
  remains claimed; concrete preservation and backup evidence stays private.

## Fog

- Ticket 15 still requires explicit retirement approval, execution of the prepared
  relocation/archive and obsolete-entry-point retirement, and verification of the
  final private completion backup. Cutover, missing-report waivers, publication
  and the initial private backup have passed their gates.
