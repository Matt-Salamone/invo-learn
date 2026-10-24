# Upgrade ideas from invo-assignment

**Follow-up:** the owner authorized all ten suggestions after this comparison.
Their invo-learn 0.5.0 implementation is documented in
[quality and recovery](../user/quality-and-recovery.md). Findings below retain
the source-inspection baseline and distinguish it from subsequent implementation.
The implementation also preserves the newer 0.4.1 per-course pending-lesson
workflow integrated before publication; the baseline comparison below predates it.

Research date: **2026-10-24**. Baseline: local invo-learn **0.4.0**, commit
`efd93bb0701d7504d6db0318475e8df70828ad9f`. Compared with invo-assignment's
default branch, latest returned commit
[`efa939cd9be49fbdc3fc8aeac79cde69a9811052`](https://github.com/Matt-Salamone/invo-assignment/commit/efa939cd9be49fbdc3fc8aeac79cde69a9811052),
dated 2026-10-23. Also inspected a separate, locally installed invo-assignment
**0.1.0** skill; that installation contains implementation files absent from the
remote snapshot. Its exact source commit was not established. These are design
recommendations, not accepted new requirements or measured learning improvements.
No runtime changes or learning trials were made.

## Main finding

**The remote and installed skill differ.** The inspected invo-assignment GitHub
snapshot contains a specification, diagrams, and development configuration;
its README explicitly says an installable skill and helpers are not implemented.
The recursive commit tree corroborates that boundary. The installed 0.1.0 skill,
however, has Python helpers and operational references worth adapting. Do not
assume those files are published on the linked repository or share its commit.
[README](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/README.md),
[commit tree](https://github.com/Matt-Salamone/invo-assignment/tree/efa939cd9be49fbdc3fc8aeac79cde69a9811052)

The strongest additions are a **content-correction lifecycle**, **packet reduction
with verification**, and **tests through the installed CLI**. Most of the shared
manual handoff and evidence foundation already exists in invo-learn.

## Locally implemented patterns worth adapting

The following source files are relative to the **installed invo-assignment 0.1.0
skill root**, not the pinned remote repository. These are source-inspected
behaviors, not newly executed or tested claims:

- `scripts/reductions.py` and `references/reductions.md`: size/relevance assessment,
  UTF-8 page selection or planner-authored summaries, source/derivative hashes,
  explicit omissions, and retained evidence passages for critical details.
  Literal passage presence does not establish semantic completeness, and the
  helper does not itself trim native PDFs.
- `scripts/packets.py` and `references/packets.md`: byte-count manifest, size
  assessment, and a `report-template.json` prefilled with packet metadata alongside
  the report contract. This last item is a small practical improvement over
  invo-learn's schema alone; placeholders must never count as learner evidence.
- `scripts/reports.py` and `references/reports.md`: preserved import outcomes,
  `needs-review` for stale/affected context, selection of relevant observations,
  and `repair_of`/`repair_note` links for corrected formatting. invo-learn already
  preserves raw rejected reports, but lacks this structured repair/review queue.
- `scripts/corrections.py`, `scripts/eligibility.py`, and
  `references/corrections.md`: suspicion, investigation, revertible correction,
  and explicit lesson/evidence/packet impact assessments. Relevant earlier work
  can survive while affected context requires review.
- `scripts/workspace.py`: rejection of targets under enclosing repositories,
  exact workspace Git-root checks, installed skill version recording, and a
  persisted `next_action`. The latter can improve invo-learn status/resume without
  adopting assignment-specific state or restricting the learner's choices.

Adapt selected records and algorithms behind invo-learn's existing atomic writes,
locks, schemas, and privacy boundaries. Transplanting the assignment runtime
wholesale would replace different product contracts and evidence semantics.

## Recommended transfers, in priority order

### 1. Packet preflight and verified context reduction — high priority

invo-assignment requires assessing size and relevance before issuing a packet,
reducing unwieldy context into summaries or selected-page derivatives, preserving
references, and checking that lesson-critical detail survives. It proposes testing
actual retained page content, not filenames alone.
[Packet preparation](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/.scratch/assignment-workflow/spec.md#teaching-and-packet-preparation),
[testing decisions](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/.scratch/assignment-workflow/spec.md#testing-decisions)

invo-learn already chooses attachments, preserves originals/derivatives, records
hashes, and tells agents to consider context size. It does not have a deterministic
packet size/relevance review. Add a preflight result with file count/bytes,
approximate text size where readable, selected sections, reduction rationale,
omitted relevant context, and content QA. Treat estimates as estimates; do not
hardcode one provider's limits. Keep PDF reading/reduction optional so the core
runtime remains standard-library only.
[Current preparation](../../invo_learn/engine.py),
[planning skill](../../skills/invo-learn/SKILL.md)

The assignment spec authorizes routine packet summaries/trimming separately from
new intake conversions. invo-learn's current per-material, single-use transformation
permission is stricter. Introduce an explicit distinction if adopting this rule;
do not silently reinterpret existing consent.
[Current transformation policy](../user/decisions.md),
[current material intake](../../skills/invo-learn-add-materials/SKILL.md)

### 2. Suspected content errors, investigation, and impact review — high priority

The assignment spec asks tutors to report suspected errors with reasoning/source
locations. The planner investigates against governing material before correcting,
saves a revertible correction, informs the learner, and checks affected pending
packets and earlier evidence. A tutor assertion alone is insufficient.
[Correction lifecycle](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/.scratch/assignment-workflow/spec.md#plan-adaptation-solution-corrections-and-restoration)

Adapt this to incorrect lesson context, examples, rubrics, and coverage mappings.
Add structured content concerns and a durable correction record connecting the
claim, investigation, corrected artifact, and affected objectives/lessons. Flag a
pending affected packet before continuation; preserve its issued snapshot and
make replacement explicit. Existing packet/source checksums catch byte changes,
not a conceptually wrong explanation.
[Current report contract](../user/contracts.md),
[current packet integrity and disputes](../../invo_learn/engine.py)

### 3. Preserve valid evidence when one part is wrong — high priority

invo-assignment specifies evaluating old-version reports for relevance rather than
accepting or discarding every observation automatically. Its correction workflow
also reviews which prior evidence was actually affected.
[Report import](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/.scratch/assignment-workflow/spec.md#lesson-evidence-and-report-import)

invo-learn currently withdraws an entire disputed report, then recomputes progress
and review dates. Add append-only assessment/objective-level invalidation and
replacement links, retaining the original report and unaffected work. Recompute
from those dispositions. This is a substantive evidence-policy change requiring
careful backward compatibility, not just a new free-text report field.
[Whole-report dispute](../../invo_learn/engine.py),
[documented limitation](../user/decisions.md)

Do not add redundant packet identifiers simply to mirror the assignment spec:
invo-learn's unique lesson ID already identifies an immutable packet with objective
and map snapshots. Explicit content/template revisions would be useful for future
correction relevance and traceability, while ordinary harness updates should not
invalidate evidence by themselves.
[Current frozen lesson metadata](../../invo_learn/engine.py)

### 4. Check enclosing Git ancestry at setup — high priority, small change

The assignment spec requires resolving the target's actual location and Git root,
rejecting initialization inside installed tooling, the development checkout,
another assignment, or an unrelated enclosing repository.
[Initialization boundaries](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/.scratch/assignment-workflow/spec.md#distribution-and-repository-boundaries)

invo-learn already rejects source overlap, links, and nonempty targets. Its bootstrap
does not inspect enclosing Git ancestry before initializing an empty nested folder.
Add that check to prevent a learner workspace accidentally living under another
project's repository; provide an actionable explanation. Preserve the existing
one-workspace experience rather than adopting one repository per assignment.
[Current bootstrap](../../invo_learn/install.py)

### 5. Test complete journeys through the installed CLI — medium priority

The assignment spec chooses a public workspace-operations boundary: temporary
repositories, observable files/status/history, complete cycles, malformed reports,
stale revisions, correction/restoration, pending-packet replacement, and fresh-session
resume. Tests should survive internal refactors.
[Testing boundary](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/.scratch/assignment-workflow/spec.md#testing-decisions)

invo-learn has substantial behavior tests, injected-failure checks, installed-CLI
onboarding tests, and a synthetic worked example. Many workflow assertions still
call Workspace methods and inspect state directly. Add a few coherent installed
CLI journeys, especially corrections and resume after a fresh process; retain useful
focused tests instead of rewriting the entire suite. No assignment tests exist to
copy at the inspected commit.
[Current workflow tests](../../tests/test_workflow.py),
[onboarding tests](../../tests/test_onboarding.py),
[worked example](../../examples/worked_example.py)

### 6. Explicit policy for routine versus substantial plan changes — medium priority

The assignment spec permits routine practice/remediation/reduced teaching
automatically, while substantial scope or workload changes require approval.
[Plan adaptation](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/.scratch/assignment-workflow/spec.md#plan-adaptation-solution-corrections-and-restoration)

invo-learn already permits adaptive lessons and requires approval of coverage maps.
Clarify that practice and pacing within accepted objectives are routine; adding
authoritative scope, changing objective meaning, or materially increasing an agreed
workload needs review. Record what changed and why in a short plan decision log.
This primarily strengthens portable instructions, rather than introducing another
approval for each lesson.
[Current planning skill](../../skills/invo-learn/SKILL.md),
[map contract](../user/contracts.md#coverage-map-proposal)

### 7. Optional goal or assignment brief within an existing track — later

The assignment spec establishes required deliverables, constraints, rubric coverage,
and consequential uncertainties before planning; it begins teaching with understanding
the instructions.
[Intake and solution requirements](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/.scratch/assignment-workflow/spec.md#intake-and-the-initial-solution)

For invo-learn, an optional exam/project/skill goal could connect a due date,
observable success criteria, and existing objectives. An opening session could
unpack those criteria when useful. Keep deadlines and pacing optional. Do not
adopt the assignment harness's mandatory complete-worked-solution stage as the
default course-learning flow: that changes this product's purpose and can expose
answers before independent assessment.
[Current requirements](../design/requirements.md)

## Already present: avoid rebuilding these

Manual fresh-chat packets and returned reports; private learner/source separation;
original preservation and source provenance; structured actual-answer/assistance
evidence; duplicate import guards; resumable durable state; progression overrides;
immutable packet archives and hashes; and pending-session protection are already
implemented. invo-learn additionally has cross-track spaced reviews, delayed
retention rules, compatible updates, and private-backup checks that the assignment
spec does not replace. invo-learn currently allows one outstanding packet across
the workspace; assignment's one-per-assignment rule is a different concurrency
choice, not an automatic improvement with one shared mailbox.
[Current guide](../user/guide.md),
[contracts](../user/contracts.md),
[runtime](../../invo_learn/engine.py),
[assignment responsibilities](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/.scratch/assignment-workflow/spec.md#responsibilities-and-durable-state)

## Additional invo-learn priorities

These follow from the current harness rather than requiring assignment code:

- Put explicit success criteria on objectives and account for source sections,
  extending the current free-text locators/material-level coverage accounting.
  Preserve a distinction between an inspected section and demonstrated learning.
  [Coverage contract](../user/contracts.md#coverage-map-proposal)
- Associate misconceptions and prerequisite gaps with objective IDs. The current
  report has report-wide string lists, and recompute repeats those strings under
  each attempted objective, which can obscure which gap actually needs repair.
  [Report validator](../../invo_learn/contracts.py),
  [evidence projection](../../invo_learn/engine.py)
- Add actionable status/health diagnostics for unresolved imports, pending
  handoffs, source gaps, and backup/update failures. Reuse existing state instead
  of introducing a server or mandatory dashboard.
  [Current CLI](../../invo_learn/cli.py),
  [status](../../invo_learn/engine.py)

## Reuse boundary and verification limits

The inspected recursive tree has no license file, and fetching root LICENSE
returned 404. Reuse permission for verbatim documents or assets was not established;
confirm it before copying them into a distributed package. The recommendations
above can be implemented as original invo-learn behavior. There is no runtime
code to transplant from the pinned remote revision; the locally installed helpers
need provenance and reuse permission established before verbatim distribution.
[Inspected repository tree](https://github.com/Matt-Salamone/invo-assignment/tree/efa939cd9be49fbdc3fc8aeac79cde69a9811052),
[design explicitly describes proposed behavior](https://github.com/Matt-Salamone/invo-assignment/blob/efa939cd9be49fbdc3fc8aeac79cde69a9811052/docs/design/README.md)

Source inspection used the connected GitHub metadata, commit search, and pinned file
reads. The connector did not expose a read-tree operation; a read-only GitHub REST
tree request supplied the complete file inventory. Local installed references and
the reduction/workspace helpers were read, with targeted inspection of the other
helper entry points. No invo-assignment code was run. The current invo-learn
baseline passed all 72 unit tests and the synthetic worked example. The test suite
needed TEMP/TMP directed to an allowed scratch location in this environment;
these checks establish deterministic workflow behavior, not teaching efficacy.
