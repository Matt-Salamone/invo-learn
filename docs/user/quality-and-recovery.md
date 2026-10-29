# Packet quality, corrections and recovery

These operations are agent bookkeeping in the private learner workspace. The
learner still uploads the mailbox into a fresh teaching chat and pastes one report
back. Use `python learn.py --help` for command arguments. JSON examples below are
private input files passed as the positional `file` argument. All claims about
reading, consent, semantic completeness and independent answers require actual
evidence; structural validation cannot establish them.

## Packet preflight and reduction

Before preparing a lesson, inspect the actual source content, objectives and
context as if the new chatbot had only the upload folder. Add `quality_review` to
the existing lesson spec:

```json
{
  "assessment": {
    "basis": "Inspected both source sections and their byte sizes",
    "relevance": "Every included passage supports equality and inverse operations",
    "uncertainty": "The target chatbot's upload/token limits are unknown"
  },
  "critical_details": ["Why equality is preserved", "Worked derivation and substitution check"],
  "omissions": ["Unrelated discussion deferred in the accepted map"],
  "limitations": [],
  "checks": {
    "self_contained": true,
    "critical_details_verified": true,
    "assessment_safe": true,
    "references_verified": true
  },
  "budget_bytes": 20000
}
```

Run `python learn.py preflight <track> <lesson-spec.json>` before `prepare`.
It measures context/attachment bytes and text character counts when readable,
reports source hashes and derivation records, and discloses uncertainty. The
optional byte budget applies to selected source/context bytes; generated protocol,
metadata and manifest bytes add overhead. `prepare` returns the actual complete
packet byte count. These counts are not tokenizer or provider-limit guarantees.
Exceeding a chosen context budget is advisory; an explicitly failed content check
prevents issuing the packet. Older specs without reviews still work with a warning.

For oversized or irrelevant material that is already usable, run
`python learn.py reduce-context <track> <reduction.json>`:

```json
{
  "material_id": "m-from-intake",
  "mode": "summary",
  "source_locator": "Lecture 1, sections 1-2",
  "content": "Apply the same inverse operation to both sides to preserve equality.",
  "method": "Summarized the inspected usable lecture text",
  "assessment": {
    "basis": "Inspected the full source and relevant sections",
    "relevance": "Retains the principle needed for this lesson",
    "uncertainty": "Upload limits unknown"
  },
  "critical_details": [{"detail": "Equality preservation", "evidence": "both sides to preserve equality"}],
  "omissions": ["Worked examples must be supplied separately in lesson context"],
  "limitations": []
}
```

Use `mode: "text-pages"` with `pages: [1, 3]` to select form-feed-delimited UTF-8
pages instead of providing `content`/`method`. A `derived_id` can select an existing
usable derivative. Source bytes are checked; each reduction has a new ID, immutable
output, source/derivative hashes, locators, critical-detail passages, omissions and
limitations. Attach it using `{material_id, derived_id}`. Passage checks prove
literal presence only; compare meaning and completeness against the source.
The core does not trim native PDFs or convert unreadable files.

**Permission boundary:** routine summaries and excerpts of already usable sources
are ordinary packet preparation. Creating/running an intake conversion workflow
to make unusable material readable still requires the explained, material-specific,
single-use approval. Reduction cannot mark an unusable source usable or consume
an invented approval. Original and previously issued files remain preserved.

New packets contain `packet-manifest.json`, a `report-template.json` with exact IDs,
and the existing teaching instructions/schema. The template contains no answers
and has `completed_on: null`, so it cannot be imported unchanged. Manifest payload
bytes exclude the manifest itself; private `staged_files` hashes cover every file.
Current objective state/gaps and a small recent-report summary replace full attempt
histories in new handoffs. Full attempts remain in durable reports and records.

## Criteria and section coverage

New map objectives should include `success_criteria`, a nonempty list of observable
explanations or work. Criteria become immutable after evidence exists; changed
meaning requires a new objective ID. Preserve legacy objectives without inventing
criteria or reinterpreting their evidence.

A map can additionally carry:

```json
{
  "source_sections": [
    {"id": "equality", "material_id": "m-from-intake", "locator": "Section 1", "objective_ids": ["balance"], "reason": ""},
    {"id": "appendix", "material_id": "m-from-intake", "locator": "Appendix", "objective_ids": [], "reason": "Learner deferred the appendix"}
  ],
  "section_inventory": [
    {"material_id": "m-from-intake", "complete": true, "inspection_note": "Read the whole source and listed every section"}
  ]
}
```

Every primary material needs an inventory record. Every listed section needs
matching source-backed objective links or an explicit reason it is unmapped.
Incomplete inspection is recorded with `complete: false` and its limitations.
Subsequent maps retain section IDs/identity and account for previous sections.
An accepted inventory is a source-inspection claim, not proof all pages were read,
that all scope was taught, or that the learner demonstrated understanding.
Maps still require learner approval; inspection and learning remain separate.

## Report imports and formatting repair

`ingest` saves exact raw text before parsing, and writes an outcome ledger at
`inbox/imports/<import-id>.json`. Invalid input adds no learning evidence. Status
shows rejected and quarantined imports so a fresh planning chat can resume.
Exact successful replay changes neither evidence nor the ledger. A different
formatting representation gets its own raw record without duplicate progress.

Repair only formatting supported by the actual returned report:

```sh
python learn.py ingest corrected.json --repair-of <rejected-import-id> --repair-note "Removed trailing comma; evidence unchanged"
```

Both representations and the repair link survive. Successful linked repairs
settle the rejected input in the work queue. Missing questions, answers, assistance
or rationale require returning to the lesson conversation; never fill them in from
assumptions. Imports revalidate all fields, identities, dates, duplicate conflicts
and evidence rules. A crash after state commit but before writing the outcome can
be recovered by replaying the same report; inspect records rather than redoing the
lesson. Backup should include raw reports, outcome/repair ledgers and state.

## Objective-specific gaps

Optional fields on each report objective are:

```json
{
  "gaps": [{"id": "gap-balance", "kind": "misconception", "description": "Changes only one side", "assessment_ids": ["q-start"]}],
  "resolved_gaps": [{"gap_id": "gap-from-an-earlier-report", "assessment_id": "q-final", "rationale": "Fresh explanation independently repairs that specific gap"}]
}
```

Gap IDs are unique within the track; kind is misconception/prerequisite. Assessment
references belong to this objective in the report. A resolution refers to an
existing gap for the same objective and an actual fresh unaided assessment of its
assigned kind. Qualifying consistent evidence and a demonstrated judgment are
needed before the projection marks it resolved. Withdrawing the resolving evidence
reopens the gap. Guided practice and unrelated independent passes cannot resolve it.
Legacy report-wide notes remain in `unscoped_notes`, rather than being assigned
to every attempted objective. Raw legacy evidence is preserved unchanged.

## Suspected errors and immutable corrections

Tutors can include optional `suspected_errors` entries with `objective_ids`, `claim`,
`reasoning`, and `source_reference`. Ingestion records suspicions once, separately
from learning evidence. The planner can also use `record-concern <track> <file>`
with the same shape. A suspicion never becomes a correction automatically.

1. `investigate <concern-id> <file>` takes `sources_examined` (nonempty list),
   `reasoning`, and `conclusion` (confirmed/unconfirmed). Examine the actual sources,
   assignment conventions where applicable, and reasoning. Preserve unconfirmed
   findings too. A confirmed investigation is bound to the current content revision.
2. `correct <concern-id> <file>` takes `base_revision` (integer), corrected teaching
   `context`, nonempty `checks` (`{check, result, evidence}`), `limitations`, and an
   `announcement`. At least one check must pass and none may fail; limited checks
   remain disclosed. Explain the announcement to the learner after success.
3. The correction is a new immutable addendum, never an overwrite of original
   course material or an issued packet. It records the concern, verification,
   previous/current revision and affected objectives, including transitive
   prerequisite dependents. New packets receive relevant addenda in revision order.
4. Existing affected lessons and evidence are flagged for relevance review.
   `review-context <lesson-id> <file>` takes `correction_id`, `status`
   (safe-to-resume/replace/pending), and `reason`. Each correction needs its own
   decision. An affected pending packet cannot restage until assessed safe.
5. Review previous evidence separately as described below. Successful learner work
   on unchanged material should survive with an explicit relevance reason.

Corrections are revertible through history: preserve earlier addenda and add a new
investigated corrective revision when a correction itself is wrong. Version control
retains completed changes through the existing private-backup workflow. A later
approved map can change coverage; correction addenda do not expand accepted scope.

## Scoped evidence review and stale reports

`review-evidence <file>` records an append-only disposition:

```json
{
  "report_id": "report-one",
  "objective_id": "solve",
  "assessment_ids": ["q-ambiguous"],
  "status": "withdrawn",
  "reason": "Confirmed ambiguous question; retain the other independent assessment"
}
```

Status is retained/withdrawn/pending. Empty assessment IDs address the whole
objective. Original questions, answers and report bytes remain unchanged. Pending
evidence contributes no new demonstration. Withdrawn assessments become invalid
in the projection, while their teaching/assistance chronology remains conservative.
The existing whole-report `dispute` remains available. Optional `judgment` can review
the objective judgment, but cannot make nonqualifying evidence independent.
An optional `replacement: {report_id, assessment_id}` links actual replacement
evidence for the same objective; it does not fabricate an answer or bypass grading.

To resolve a correction's evidence flag, include `correction_id` and review the
whole objective (`assessment_ids: []`). Each correction and manual review is an
independent layer: retaining one cannot silently clear another pending/withdrawn
layer. Revised dispositions recompute understanding, retention and due dates from
the retained observations. No review relabels guided work as independent work.

A report from an older affected context or explicitly replaced packet is preserved
with `status: needs-review` and no new evidence. Run
`review-import <import-id> <decisions.json>`, supplying every assigned objective:

```json
{
  "balance": {"status": "retained", "reason": "The assessed principle and question are unchanged"},
  "solve": {"status": "withdrawn", "reason": "Old context gave an incorrect procedure"}
}
```

All original identifiers and evidence rules still apply. An invalid review decision
leaves the valid report awaiting review. An old report never closes a different
current handoff. Ordinary harness updates alone do not invalidate content/evidence.
There is one pending main packet across the workspace. The work queue includes all
courses, and explicit replacement preserves the named packet's issued archive.
Last-staged context remains identified by active_lesson; status also retains paused
and retired lesson history.

Use `replace <pending-lesson-id> <lesson-spec.json> --reason "<explicit learner decision>"`
to create a replacement with a new ID. Invalid specs preserve the pending lesson;
successful replacement preserves its archive and links both IDs. Abandonment also
remains explicit. Inspect/ingest reports before either operation; replacement is
not a shortcut for discarding a returned report.

## Plan decisions and optional pacing

`plan-decision <track> <file>` takes `kind` (routine/substantial), `reason`, accepted
`objective_ids`, and `changes`. Routine practice, alternate explanations and pacing
within approved scope can apply immediately. Adding scope, changing objective
meaning, or materially increasing agreed workload is substantial and remains pending
until actual learner `approval` is recorded. Accept coverage-map changes separately.

Optional fields are `minutes`, `available_minutes`, `preferred_lesson_minutes`
(positive integers) and `deadline` (YYYY-MM-DD). Missing pacing is valid. Estimates
exceeding supplied available time require a learner decision even for routine
changes. To approve a stored pending proposal, repeat its exact payload and add
`proposal_id` and `approval`. Edited scope/pacing requires a new proposal.
Decisions and reasons survive in state and a generated `plan-decisions.json`;
existing agent-written `plan.md` is preserved. Software validates records, while
the planner classifies the significance of natural-language changes.

## Resume and offline health

`status` derives `next_action` and `work_queue` from durable imports, concerns,
pending evidence/context, plans/maps and source gaps. Due reviews remain advisory.
`doctor` verifies mailbox ownership, original/derived/packet/correction checksums,
report archives, the active installed release, and the workspace Git root. It
reports recorded CLI backup/update failures and recovery actions without network
access, deleting locks or modifying records. A healthy integrity result does not
mean there is no pending learning work, nor that remote backup/update status was
freshly verified. Retry the failed operation after addressing its actual cause.

Setup rejects enclosing Git directories/worktree markers and learner-state roots,
including with `--no-git`, before creating private files. Inherited Git directory,
worktree/common-directory or index overrides must be cleared before setup too.
Source/tooling overlap,
mailbox ownership, link rejection and private-remote verification remain in force.
All extensions are optional v1 fields. Existing workspaces need no destructive
migration; old reports, explicit preferences and immutable archives survive upgrades.

See [the packet evaluation cases](packet-evaluations.md) for portable
fresh-chat quality checks that complement deterministic helper tests.
