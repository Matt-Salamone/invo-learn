# Explicit private migration rehearsal

Ordinary updates do not combine learner workspaces. Rehearse consolidation with
the installed invo-learn command, using a private plan file:

```text
python learn.py migration-rehearse <plan.json>
python learn.py migration-status <rehearsal-directory>
```

The plan contains `destination` (the existing private course workspace to retain),
`assignments` (a list of `{source, track_id}` associations), and `stage` (a new
private rehearsal directory). Use absolute paths. Each `source` is an older
assignment workspace; its `track_id` must identify its course in the destination.
A standalone project can use its own course/track. The stage must be independent
of all sources, external mailboxes and enclosing repositories. No source remotes
or repository visibility settings are changed.

Rehearsal first checks known original material, packet and report hashes and Git
history integrity. Missing or damaged required originals stop before copying.
It then preserves complete source trees, including ignored files, untracked work,
empty directories, old tools, issued packets, reports, existing reference solutions
and full standalone `.git` directories. A dedicated external mailbox is preserved
separately. Original identifiers, commits and distinct origins remain inspectable,
even when files have identical bytes. Source workspaces remain unchanged.

The stage contains `migration-manifest.json`, complete originals under `sources/`,
any `external-mailboxes/`, and a combined `workspace/`. The manifest records exact
file hashes and byte counts, directory inventories and deterministic associations.
`migration-status` verifies both preserved snapshots and the unchanged source
baseline. It refuses changed snapshots, changed sources or unexpected stage edits.
Repeating the same request and stage verifies it without duplicating records.
An incomplete stage is preserved for inspection; use a new stage if no completed
manifest was published. Never remove unrelated files to make a path reusable.

The combined state retains existing course learning, reports and review policy.
Assignments belong to their associated course and keep exact old contexts in
`legacy/`; imported materials retain their original source identities. Historical
reference artifacts and exposure remain recorded, while new decisions have no
inferred yes/no answer. Pedagogical evidence projection is a later explicit step.
Rehearsal preserves existing teaching preferences and adds a presentation override
for self-contained teaching with no source commentary. Original settings and
issued packet bytes stay unchanged in their archives.

The stage is inactive: ordinary study mutations require later explicit activation.
Read-only status is available. Preservation, evidence projection, actual-report
reconciliation or recorded waiver, and activation are separate checks. A rehearsal
does not retire source checkouts, certify learning, or complete the private cutover.
An older destination's installed harness must also be upgraded through its normal
integrity/customization checks before the combined workspace is activated.

Linked-worktree `.git` files, shared object stores and shallow histories are
refused rather than copied incompletely. First make and verify a complete independent
private repository copy. Symlink/junction inputs are also refused. Never normalize
altered original bytes or replace their recorded hashes to bypass integrity checks;
any recovery must preserve the current bytes and establish the exact expected
original checksum on a private copy before a new rehearsal.

For implementation, `invo_learn.migration.load_rehearsal(stage)` returns the stage
root and manifest. Later explicit projection/reconciliation operations verify the
stage, make scoped changes, and use `save_rehearsal(stage, manifest)` to record the
resulting workspace inventory. Immutable source snapshots remain unchanged.

## Reconcile checked-out lessons

```text
python learn.py migration-checkouts <rehearsal-directory>
python learn.py migration-reconcile <rehearsal-directory> <returns-and-waivers.json>
```

The read-only inventory lists every originally prepared course lesson and
outstanding assignment packet, including checkouts absent from the last-staged
pointer. Offer collecting their actual in-progress chatbot returns. The agent
saves actual input files privately outside the frozen source trees and staged
workspace, then supplies a payload with a `reports` list. Each selection is
`{origin_key, file}`; use the exact origin key returned by the inventory and the
absolute private path of the actual return. Empty reports lists are allowed.

Returned bytes are archived unchanged inside the canonical workspace under
`migration-records/<migration-id>/returns/`. Original packet, assignment and
solution-revision associations are validated before any checkout is resolved.
Malformed, incorrectly associated or canonically conflicting returns remain
preserved with actionable diagnostics and block reconciliation. An evidence-backed
repair selection adds `repair_of` (the rejected raw SHA-256) and `repair_note`;
it must supply an actual corrected file. The original stays unchanged. Never
invent an answer or alter an association by guessing to satisfy validation.

If the learner explicitly accepts losing unreported progress, the payload may
also contain `waivers`, with one selection per identified checkout:

```json
{
  "reports": [],
  "waivers": [
    {
      "origin_key": "<inventoried origin key>",
      "packet_id": "<original checkout ID>",
      "accept_lost_progress": true,
      "reason": "Actual learner acceptance of losing this checkout's unreported progress"
    }
  ]
}
```

This is an explicit decision record, never a saved or inferred default. Waivers
retain all existing observations and artifacts, retire the selected checkout as
incomplete, and schedule a fresh demonstration or relearning in the ordinary
study queue. They add no reports, learner responses, mastery or retention credit.
Waivers do not override source damage or a malformed/broken actual return.

Actual course returns follow existing evidence rules. Assignment returns retain
their original observations for separate conservative evidence projection. An
old return without an explicit completion field remains incomplete; an explicit
`session_status: "in-progress"` may represent no observations yet. Main and
supplemental returns remain distinct: a side report never closes the main checkout.
Valid late main returns after retirement remain historical and cannot reopen the
pending slot. Repeating exact returns or decisions adds no duplicate progress.

Reconciliation `eligible: true` satisfies only the report/waiver gate. Preservation,
evidence projection, installed-code checks and explicit activation are still
required. The frozen source snapshots retain their original pending statuses;
the canonical reconciliation ledger records their retirement. Stage writes use
`migration.lock` outside the workspace inventory. After an interrupted process,
verify that no writer remains before recovering its lock and inspecting the
preserved stage; never claim activation from an incomplete operation.

## Conservative evidence projection

```text
python learn.py --today YYYY-MM-DD migration-project <rehearsal-directory>
python learn.py migration-status <rehearsal-directory>
```

Use the learner-local date. Projection reads preserved historical assignment
observations and actual reconciled returns, preserving their original questions,
answers, assistance and provenance. It does not guess course objective links from
titles, filenames or deliverable completion. Without a justified link, no mapped
credit is awarded. Instead, the ordinary study queue receives due-now
`fresh-demonstration` or `relearn-legacy-topic` actions grounded in the assignment's
governing material and actual criterion. These are planner study actions, not a
learner-facing mapping-review queue or a lock on other study.

Old assignment reports do not record all modern freshness, validity, grading and
assessment-kind evidence. Even an old `independent` label with a justified topic
link can establish at most coverage; it cannot establish modern independent
understanding or delayed retention. Assisted work stays assisted. Matching actual
side-chat help with before-answer or unknown timing qualifies the old task;
post-answer help alone does not rewrite its earlier answer. Existing compatible
course evidence, understanding and review dates remain intact.

The projection artifact is `.invo-learn/migration-projection.json` in the staged
workspace. Canonical status exposes `tracks.<course>.legacy_evidence`, including
unchanged observations, provenance and any derived coverage credit. Status's
ordinary work queue exposes the fresh-study needs. Repeating projection with the
same inputs changes no files or progress. Metadata variants of the same actual
observation keep distinct return provenance without duplicating the observation.
Historical late returns remain historical and receive no newly mapped credit.

The planner may add a justified association after inspecting the governing scope
and accepted course objectives, without asking the learner to review mapping
flags. Use `migration-project <stage> --links <private-links.json>` with:

```json
{
  "links": [{
    "observation_id": "legacy-observation-from-projection",
    "objective_id": "accepted-objective-in-the-assignment-course",
    "reason": "Actual evidence and scope supporting this relationship"
  }]
}
```

Associations are recorded additions, not inferred mappings. They add at most
coverage and never postpone the existing fresh-study due date. Omitting the
links file on a retry retains the recorded associations. Unknown objectives and
conflicting justifications are rejected before writes; preserve the current
stage and rehearse separately when correcting a mistaken association.

`migration-status` reports `projection_current`. Actual main or supplemental
returns received after projection can make it false, including a valid empty
partial return. Run projection again deliberately after reconciliation; a
completed old projection is insufficient for activation when its inputs changed.
For implementation, `migration_projection.projection_current(ws, manifest,
stage)` supplies the same gate. The stage lock serializes projection with report
reconciliation; source originals and immutable packet/report bytes are untouched.
