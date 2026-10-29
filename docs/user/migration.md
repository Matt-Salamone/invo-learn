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
