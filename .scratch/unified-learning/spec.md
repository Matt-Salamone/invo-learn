# Unified learning and assignment workflows

Status: needs-info

Draft: product decisions are confirmed. Finalization and `ready-for-agent` status
await confirmation of the proposed S1 testing seam and component view v0.1.
This is a reusable public specification; private learner inventories are excluded.

## Problem Statement

Course study and assignment learning currently use separate products with
overlapping material intake, lesson planning, manual chatbot handoffs, evidence
reports and recovery mechanisms. Their workspace structures, update mechanisms
and evidence rules differ. The assignment workflow also requires the planning
agent to complete a reference solution before it can plan lessons or issue
packets, preventing a learning-first workflow without a completed answer.

The learner wants one product and one private workspace, assignments integrated
with continuing course study, an optional upfront solution, and optional guided
implementation after conceptual lessons. Existing learning records and original
work must survive consolidation without overstating understanding or retention.

## Solution

Use invo-learn as the single public product, user-facing skill and command entry
point, with one installer/updater. Consolidate the assignment capabilities into
its course-oriented private workspace. Each assignment belongs to one course or
track; an assignment without an existing course can use a standalone track.

Before planning an assignment's lessons, ask whether the agent should generate
and verify a reference solution. Plan directly from requirements and materials
when the answer is no. When the learner reaches final implementation, ask whether
they want guidance. Both choices are explicit at each new decision point, without
saved or inferred yes/no defaults, and all four combinations are supported.

Continue the manual planner/mailbox/chatbot/report workflow. The chatbot teaches
concepts and optionally guides implementation; the learner edits and runs their
work. The planning agent maintains durable records. Share coverage, objectives,
learning gaps and reviews across assignment learning and ordinary course study,
while distinguishing assignment completion, understanding and retention.

Allow only one pending handoff across the entire workspace. Migrate explicitly,
after rehearsals and preservation checks, keeping original artifacts and histories
recoverable. Unknown evidence mappings yield no unsupported progress credit and
automatically lead to fresh demonstration or relearning, not a manual mapping
review task for the learner.

## User Stories

1. As a learner, I want one invo-learn entry point, so that I do not choose between overlapping learning products.
2. As a learner, I want one installer/updater, so that setup and maintenance follow one understandable process.
3. As a learner, I want one private workspace containing all my courses and assignments, so that my agent can coordinate study.
4. As a learner, I want the public package kept separate from my records, so that reusable development work never publishes my learning data.
5. As a learner, I want setup choices explained one at a time, so that I can make informed decisions without managing infrastructure.
6. As a learner, I want assignments attached to their course, so that their learning contributes to the relevant curriculum.
7. As a learner, I want a standalone track for an assignment without a course, so that the same workflow applies outside formal classes.
8. As a learner, I want requirements, deliverables and acceptance criteria recorded separately from course objectives, so that finishing the assignment is not confused with mastering the subject.
9. As a learner, I want arbitrary material types preserved, so that unsupported formats do not silently disappear.
10. As a learner, I want permission requested before a new automatic conversion workflow, so that source handling respects the existing intake contract.
11. As a learner, I want primary materials to define scope and optional supplements to remain labeled, so that outside explanations do not silently expand my workload.
12. As a learner, I want source-linked coverage maps and inspectable plans, so that I can understand and adjust what will be taught.
13. As a learner, I want an explicit upfront-solution question before assignment lesson planning, so that the agent does not assume I want a completed reference.
14. As a learner, I want a recorded yes or no for each new solution decision, so that prior assignments and preferences cannot choose for me.
15. As a learner, I want resuming an already-answered decision to retain its answer, so that interrupted work does not restart intake.
16. As a learner, I want lesson planning without a solution, so that I can learn toward an assignment without the agent first completing it.
17. As a learner, I want a requested reference solution verified against requirements, so that lessons do not depend on an unchecked answer.
18. As a learner, I want solution artifacts and their revisions preserved when they exist, so that later corrections retain provenance.
19. As a learner, I want no-solution packets to work without dummy solution records, so that their identity and evidence do not rely on invented context.
20. As a learner, I want task-specific completed solutions omitted when none was requested, so that packet preparation does not bypass my choice.
21. As a learner, I want an explicit guidance question when I reach implementation, so that guidance is chosen when it becomes relevant.
22. As a learner, I want guidance available with or without an upfront solution, so that these two choices remain independent.
23. As a learner, I want independent implementation available with or without an upfront solution, so that viewing a reference does not force guided work.
24. As a learner, I want the chatbot to guide manageable implementation steps while I edit and run the work, so that I remain the implementer.
25. As a learner, I want explanations, prompts and hints first, so that guidance helps me reason through the task.
26. As a learner, I want direct code and worked steps when I request them, so that help can adapt to my needs.
27. As a learner, I want actual help recorded, so that assisted completion is not presented as independent understanding.
28. As a learner, I want fresh independent checks after assisted work, so that I can demonstrate understanding separately.
29. As a learner, I want lessons to default to self-contained teaching without source-title/page commentary, so that I can focus on the explanation.
30. As a learner, I want existing presentation settings moved to that default during my explicit migration, so that the merged workspace behaves consistently.
31. As a learner, I want source grounding and provenance retained despite that presentation choice, so that explanations remain traceable when requested.
32. As a learner, I want useful visuals, neutral coding syntax references and optional side chats retained, so that consolidation preserves useful teaching tools.
33. As a learner, I want one reusable mailbox, so that handoffs stay simple.
34. As a learner, I want one pending handoff across all courses and assignments, so that separate checked-out lessons cannot conflict.
35. As a learner, I want preparation in another course or assignment blocked while a handoff is pending, so that the workspace-wide rule is reliable.
36. As a learner, I want restaging or explicit replacement to preserve originals, so that recovery does not overwrite issued packets.
37. As a learner, I want an in-progress report for an interrupted lesson, so that actual progress survives without claiming completion.
38. As a learner, I want paused progress retained after an old handoff is reconciled, so that I can resume through a future handoff.
39. As a learner, I want the planner to save and ingest my returned report, so that I do not perform manual import bookkeeping.
40. As a learner, I want late reports associated with their exact original packet, so that migration does not invalidate real work.
41. As a learner, I want duplicate reports and repeated migrations to be harmless, so that retries do not duplicate progress or reviews.
42. As a learner, I want malformed reports preserved without adding learning evidence, so that repair is possible without fabricated progress.
43. As a learner, I want main and supplemental reports kept distinct, so that a side chat does not finish a lesson or certify mastery.
44. As a learner, I want assistance timing and prior observations preserved, so that later explanations do not rewrite earlier assessment history.
45. As a learner, I want assignment learning connected to course objectives and reviews, so that useful learning continues after a deadline.
46. As a learner, I want coverage, independent understanding and delayed retention kept distinct, so that progress summaries remain meaningful.
47. As a learner, I want ambiguous legacy evidence to trigger fresh assessment or relearning, so that I do not need to review mapping flags myself.
48. As a learner, I want original evidence preserved even when it earns no mapped credit, so that uncertainty does not erase my history.
49. As a learner, I want old reports and records readable without old command names, so that data compatibility does not require two products.
50. As a learner, I want workspace migration to be explicit, so that routine updates never silently reorganize my data.
51. As a learner, I want migration rehearsed on private copies first, so that preservation and recovery are demonstrated before cutover.
52. As a learner, I want a reminder to obtain in-progress reports from every checked-out lesson chat before final cutover, so that all outstanding work can be reconciled.
53. As a learner, I want cutover to wait for those actual reports, so that no missing evidence is invented to resolve pending sessions.
54. As a learner, I want all original materials, packets, reports and untracked work preserved, so that consolidation does not lose files outside normal tracking.
55. As a learner, I want originating identifiers and commits retained, so that migrated records can be traced to their source.
56. As a learner, I want the original repositories and full Git histories recoverable, so that migration does not rewrite history.
57. As a learner, I want integrity failures to stop cutover, so that missing or altered originals cannot become the new authoritative workspace.
58. As a learner, I want old repositories archived only after verified success, so that recovery remains available during transition.
59. As a learner, I want compatible trusted updates and scoped private backups retained, so that normal study remains maintainable after consolidation.
60. As a developer, I want synthetic installed-workflow tests, so that the reusable package can be verified without exposing real learner data or paying for chatbot sessions.
61. As a developer, I want one main behavioral testing seam, so that tests verify useful outcomes without depending on internal module structure.
62. As a developer, I want accepted diagrams and test decisions carried into future tickets, so that fresh implementation sessions retain the agreed design.

## Implementation Decisions

### Product and orchestration

- Extend the existing invo-learn workspace application rather than maintaining
  two independently evolving runtime products. Reuse material preservation,
  packet preparation, report ingestion, correction/recovery, review scheduling,
  versioned installation and private backup behavior where their contracts fit.
- The sole user-facing skill/command entry is invo-learn. Setup, intake, course
  study, assignment study, reporting, maintenance and explicit migration are
  operations within it. Internal modules and bootstrap helpers are implementation
  details, not additional named learner entry points. Remove obsolete names and
  aliases from the delivered interface; do not add compatibility wrappers.
- Preserve the Python standard-library runtime and portable agent instructions.
  Do not assume a particular model, agent host, proprietary model interface or
  chatbot integration. Keep existing explained, one-question-at-a-time onboarding.

### Assignment planning and packet context

- Add course-owned assignment identity, governing requirements, deliverables,
  criteria, accepted lesson plan, optional reference solution and implementation
  progress. Keep course objectives and assignment deliverables distinct.
- Model solution generation and guided implementation as separate explicit
  decisions whose unanswered state is meaningful. An absent choice is not false.
  The relevant operation cannot proceed by inheriting a stored preference or a
  prior assignment's answer. Keep a recorded answer when resuming that same step.
- Ask the solution question before assignment lesson planning. Ask the guidance
  question at the transition to implementation, not as an intake default. Preserve
  actual historical exposure and help when the learner requests a later change.
- A requested upfront reference is completed and verified before its reference-led
  lesson plan. The no-upfront-solution path plans directly from authoritative
  requirements and material; it must not demand or fabricate a solution revision.
- Identify new packet/report context by immutable assignment, plan, material and
  packet lineage, with a solution reference only when one actually exists. Retain
  the ability to interpret legacy solution-revision-based contexts through readers.
- Select relevant packet context rather than indiscriminately injecting every
  solution artifact. Preserve preflight, readable flat uploads, context-reduction
  verification, source fidelity, corrections and attachment-budget behavior.

### Teaching, implementation and evidence

- The planner owns durable state and future planning. The chatbot teaches and
  assesses within assigned objectives and can guide actual implementation. The
  learner edits and runs their work. Direct code/worked steps are permitted when
  requested, with actual assistance and assessment timing represented in reports.
- Default to explanations, prompts and hints before requested direct solutions.
  Assistance can establish assignment completion but not independent mastery.
  Use fresh independent assessment and later review to establish understanding
  and retention according to the existing evidence rules.
- Maintain detailed self-contained teaching, meaningful visuals with readable
  alternatives, neutral syntax lookup rules and optional supplemental side chats.
  Side reports never create a second pending main handoff or independently close it.
- Make no-source-commentary presentation the combined default and apply it to
  the owner's existing stored settings during explicit migration. Keep provenance
  and source grounding. Preserve issued bytes; only newly prepared or regenerated
  packets adopt the new instructions. Explicit later overrides remain possible.
- Extend report handling to represent incomplete sessions and implementation
  progress without inventing completion. Save exact returns, validate context,
  preserve assistance, support repairs, and maintain duplicate protection. Preserve
  reports that arrive late after reconciliation as historical evidence; do not
  recreate multiple pending sessions or silently apply irrelevant observations.
- Map legacy evidence only when the relationship is justified. Preserve uncertain
  originals but award no unsupported mapped progress. Automatically schedule fresh
  checks or relearning; do not create a learner-facing manual mapping-review queue.
  No imported independent observation alone proves delayed retention.

### One pending handoff

- Enforce one pending handoff across the whole private workspace, covering ordinary
  lessons, assignment lessons, reviews and implementation sessions. This replaces
  the previously accepted per-course concurrency behavior.
- Enforce the invariant through existing serialized workspace writes, not just
  agent instructions or a last-staged pointer. Another course or assignment cannot
  bypass it. Reject invalid preparation before changing existing packet bytes or
  staging. Explicit replacement must retain the old issued archive.
- Preserve original artifacts and paused progress after a report or explicit
  retirement resolves a pending handoff. In-progress work remains incomplete and
  can be resumed with a future packet through the same single pending slot.

### Migration and older data

- Keep older records/reports readable through internal readers and provenance
  associations, independent of removed public skill or command names. Reading
  legacy data does not implicitly authorize workspace conversion.
- Implement deliberate migration/rehearsal operations within invo-learn. Use
  private snapshots/copies and a preservation manifest to import complete learner
  state, sources, derived artifacts, original packets/reports, reference solutions,
  working files including untracked work, preferences and review history.
- Retain original identifiers and origin commits. If destination identities must
  differ, keep deterministic origin-scoped associations and unchanged original
  payloads so old reports remain attributable. Do not infer associations merely
  from matching titles or filenames.
- Repeated migration must not duplicate materials, progress, reviews or imports.
  Identical file content may share storage only if provenance and original identity
  remain intact; storage deduplication is not a prerequisite for this build.
- Import files and records with explicit destination migration commits. Keep
  source repositories and their complete histories recoverable; do not splice
  unrelated commit graphs or rewrite either repository's history.
- Before actual private cutover, remind the learner to obtain an in-progress
  report from every checked-out lesson chat. Wait for the actual returns, preserve
  and reconcile them, and retire old pending handoffs while preserving incomplete
  progress. Public implementation and synthetic tests may proceed meanwhile.
- Missing files, altered original bytes or broken report associations are
  integrity failures that stop cutover. Uncertain pedagogical mappings instead
  retain history without credit and generate new study needs automatically.
- Demonstrate recovery on rehearsal copies. A failed or interrupted migration
  must not destroy the usable source workspaces or falsely mark cutover complete.
  Activate the destination only after reconciliation and preservation succeed.

### Distribution, updates and retirement

- Keep one immutable versioned distribution and one installer/updater, with aligned
  release version and changelog. Reusing assignment assets must respect licenses.
- Preserve compatible trusted auto-updates and opt-outs, checksum/customization
  checks, accurate offline status, backups and recovery. Ordinary updates may
  replace harness code/templates but must not reorganize learner data. If a new
  state layout is necessary, require explicit migration and retain a usable prior
  installation rather than silently converting it or corrupting progress.
- Preserve scoped commit/push to verified existing remotes. Public commits contain
  reusable code, documentation and synthetic fixtures only. Real learner records
  go only to the verified private destination. Do not create/change remotes, expose
  private contents or force-push as part of consolidation.
- Implement/test public behavior, rehearse on private copies, and then migrate
  the actual private workspaces after all gates pass. After verified success,
  add relocation notes and archive the superseded public assignment package and
  private assignment repository as read-only. Remove obsolete installed entry
  points only after verifying the working destination.

## Testing Decisions

### Proposed main seam S1 (confirmation pending)

Use the public invo-learn command workflow as the main behavioral test seam.
Exercise installed commands and their observable results, including bootstrap,
intake, planning choices, preparation, ingestion, status, update and explicit
migration. Assert returned outcomes and preserved filesystem artifacts rather
than private helper calls, internal dictionaries or implementation call order.

The command adapter dispatches into study, migration and installation/update
modules. These responsibilities do not require separate parallel public testing
interfaces or new mock-only abstractions. Existing lower-level tests may remain
where they verify useful invariants, but new end-to-end acceptance behavior crosses
S1. Bootstrap uses a controlled release input and verifies the same installed
workflow rather than assuming a permanent public source clone.

Use real temporary files, independent synthetic workspaces and temporary Git
repositories. Control release downloads, remote responses and learner-local dates
as environmental inputs. Inject failures at external operations where useful to
verify preservation; do not replace the whole persistence/ingestion path with mocks.
Live remote visibility/branch verification is also required during actual private
backup and final cutover; synthetic tests do not prove the live account setup.

### Behaviors and observable outcomes

- Install a synthetic learner workspace and confirm that only the canonical
  skill/command entry point is delivered and all required operations work after
  the temporary download is removed.
- Exercise all four solution/guidance combinations with synthetic requirements
  and reports. Show that unanswered decisions stop the dependent operation; prior
  choices and preferences cannot silently fill them. Resumption retains the same
  answered step. The no-solution path creates no fabricated solution identity.
- Prepare course, assignment, review and implementation handoffs in sequence.
  Show that any pending handoff blocks another across all courses/assignments,
  including concurrent writer attempts, without corrupting the existing mailbox.
  Test explicit replacement, partial report reconciliation, retirement and resume.
- Ingest independent, assisted, failed, incomplete, duplicate, malformed, repaired,
  stale and late reports from both supported origins. Assert exact raw preservation,
  stable packet associations, no duplicate progress, no fake completion, no
  assistance-to-independent promotion and no immediate retention claims.
- Test source fidelity, selected solution context, default presentation, neutral
  syntax lookup, useful visual instructions and supplemental reports. Verify that
  issued packets remain unchanged when templates/settings change.
- Rehearse migration using synthetic legacy snapshots with overlapping sources,
  origin-scoped identifiers, tracked and untracked work, old solution references,
  outstanding sessions, and ambiguous objective mappings. Assert inventory/hash
  preservation, continued legacy readability, idempotence, no manual mapping queue,
  conservative credit, and automatically planned assessment/relearning.
- Show that absent in-progress reports prevent private cutover. Show that missing
  or damaged originals and broken report links prevent activation. Exercise a
  representative interrupted migration and recover usable sources/destination
  without discarding original history or claiming success.
- Exercise routine compatible updates and incompatible layout changes. Assert
  preserved learner data, explicit migration requirements, backup/rollback,
  customization protection, opt-outs and truthful unavailable/offline outcomes.
- Use an end-to-end installed journey that creates two tracks, adds assignments,
  performs handoffs sequentially, ingests reports, schedules reviews, migrates
  synthetic older data and prepares the next handoff through the same interface.
- Require the existing unittest suite and worked example to pass, with obsolete
  per-course concurrency expectations updated to the newly agreed global rule.
  Add targeted installed-command migration/assignment checks rather than relying
  only on direct engine calls.

### Prior art and limits

Existing onboarding tests cover temporary downloads, independent workspace setup,
installed subprocess commands and upload preservation. Existing workflow tests
cover pending handoffs, immutable packets, duplicate imports and reviews. Existing
update/automation tests cover trusted releases, rollback, active installed code
and scoped private backups. Existing side-chat, syntax-reference, quality/recovery
and packet-evaluation tests provide the relevant report and teaching-contract
examples. Reuse these patterns while replacing superseded concurrency behavior.

Portable packet evaluations complement deterministic command tests. Synthetic
reports verify how the harness handles evidence, not whether a chatbot actually
taught correctly, whether a learner worked unaided, or whether its grading was
accurate. Preserve that limitation; no paid/live chatbot session is a prerequisite
for deterministic acceptance of the package.

## Diagrams

- Proposed component view **v0.1**, scope: command seam S1, study, explicit
  migration, installer/updater and their private artifact dependencies. It is
  awaiting confirmation; no new module layout is yet an accepted implementation
  decision. Save its authoritative source and SVG beside this spec, with reciprocal
  links and an agreed version identity, after confirmation. Temporary previews do
  not constitute accepted diagram references for downstream tickets.
- Accepted proposed-design timing view **v0.3**:
  [source](../../docs/design/assignment-modes-v03.puml),
  [SVG](../../docs/design/assignment-modes-v03.svg).
  Scope: two independent choices at their decision points and manual study flow.
- Accepted proposed-design pending-boundary view **v0.2**:
  [source](../../docs/design/pending-boundaries-v02.puml),
  [SVG](../../docs/design/pending-boundaries-v02.svg).
  Scope: course-owned assignments and one workspace-wide pending handoff.

The component view describes dependencies, not execution order. The timing view
describes the learner flow, not low-level internal calls. These are target designs,
not claims that the current release already implements them. Future tickets must
identify their observable S1 path and reuse the accepted views while scope holds.

## Out of Scope

- Automated chatbot integration, autonomous message sending to lesson chats, or
  requiring a particular agent/model interface.
- Having the planning agent implement the learner's final deliverable by default.
- Learner-facing manual review of uncertain migration mappings.
- Compatibility aliases/wrappers for removed skill or command names, or operating
  two independently evolving public learning products after consolidation.
- Concurrent pending handoffs per course, per assignment or per chat role.
- Rewriting issued packets, original reports, assessment observations or unrelated
  Git histories; retroactively pretending old reference solutions never existed.
- Silent conversion during ordinary updates, public storage of real learner data,
  or using a public fork as the private learner workspace.
- New scheduling algorithms, a server/dashboard, new model dependencies, or
  unrelated changes to the existing intake permission and learning-evidence rules.

## Further Notes

The owner confirmed the final product plan and the pending-boundary diagram on
October 29, 2026. The [confirmed decision record](../../docs/design/unification-interview.md)
contains the accepted discussion. This spec supersedes the earlier per-course
pending-session requirement only in the explicitly agreed direction above.

Source inspection found a reusable installed-command interface in invo-learn and
hard solution prerequisites in the assignment workflow. Consolidation is therefore
a lifecycle/context-contract extension as well as a packaging change. Internal
module/file organization and exact schema encodings remain implementation choices
within the behavior specified here; do not make them additional learner decisions.

The private destination remains the owner's existing private learning workspace;
the existing assignment joins its corresponding course. Concrete private paths,
inventories and materials belong in private migration records, not this public spec.

After testing-seam confirmation, finalize this spec with `Status: ready-for-agent`
and durable accepted component artifacts. Then derive dependency-ordered vertical
tickets; ticket decomposition and implementation are subsequent phases.
