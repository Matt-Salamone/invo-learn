# Trusted harness updates

Save and ingest returned reports FIRST, update records and plan.md, and finish
that report's backup using the invo-learn instructions. Inspect mailbox uploads before reuse.
Never make a network update the first action on a returned report.

Before planning/preparing a lesson or review, run:

```sh
python learn.py study-update --track <id>
```

Any pending main handoff defers study-update across the whole workspace, with
or without --track. Ingest its returned main report or explicitly retire it before
preparing another lesson. Preserve all existing records and archived packet bytes.
Inspect any reports actually returned in the mailbox or chat before updating.

Missing auto_update defaults to true. This choice authorizes compatible trusted
updates each time without a separate request. Honor global or track
preferences auto_update=false; check-updates remains a read-only manual check.
New setup explains this default before consent. Older installations keep their
old behavior until one explicitly authorized upgrade to 0.4.0 or later; explain
the new workflow and allow an opt-out before that upgrade. Preserve all stored
preferences, including old default-looking teaching values: their provenance
cannot be reliably inferred. Missing workflow keys inherit true, explicit false
survives. If an older CLI rejects the new preference keys, retain the chosen
opt-outs in private setup notes and apply them with the new preferences command
immediately after the upgrade, before any study preparation. No repeated consent is needed after choosing the workflow.

study-update checks the fixed public source at
https://github.com/Matt-Salamone/invo-learn, downloads main into a temporary tools
location only when newer, checks its version matches the announced version, and
uses upgrade in a fresh process. It sends no learner records. The Git snapshot
is the trust boundary; this is not signed-release verification or arbitrary URL
installation. A race in VERSION is refused and retried next time. The latest
candidate must pass existing package/state/report/Python compatibility checks;
if incompatible, stay on the installed version rather than bypass checks.

prepare also checks automatically. After activation it invokes the new learn.py
process, so generated packets use newly active code/templates. After study-update,
reread the newly active invo-learn instructions and docs before writing the lesson spec. Never edit old
packet archives: restage is byte-preserving recovery; regeneration requires a new
prepare and lesson ID after report ingestion or explicitly requested abandonment.

For a one-time upgrade of an older installation, an explicitly selected trusted
checkout, or an opted-out learner requesting a particular update:

```sh
python learn.py upgrade --source <trusted-public-checkout>
python learn.py status
```

The low-level upgrade does not fetch. It installs an immutable versioned bundle,
keeps prior bundles and pre-update state/activation backups, refreshes managed
skills and switches activation. It checks installed-file/skill/runner modifications,
same-version collisions, downgrades, schemas and Python compatibility. Preferences,
plans, originals/derived files, exact reports, archived lessons and review state
are preserved. Never change a manifest or force overwrite a conflict.

Explain unavailable/failed/incompatible outcomes accurately. Continue studying on
the installed version when safe; never call it current after failed verification.
Customization conflicts require preserving the custom files and resolving the
conflict with the learner. Caught export failures roll back; an interrupted export
can require restoring managed skills from the unchanged active release. Inspect
active.json and the lock before recovery; verify no process is running before
removing a stale lock. Unsupported schemas need an implemented migration.
If activation succeeded but preparation failed, retain the new activation and
retry preparation or restage its completed packet as appropriate. Do not duplicate
a pending lesson or repeat evidence ingestion to fix a backup failure.

After a completed handoff or processed report/plan, follow the invo-learn instructions for
automatic scoped private backup step. Include related update bundles/exports and
recovery backups when reviewing the completed file scope. Report installation,
learning and Git backup outcomes separately.

## End-of-interaction synchronization

When this interaction changes learner-workspace files, follow its AGENTS.md and
the active invo-learn commit/push instructions before the final response.
This includes stopping to wait for an onboarding answer after saving records.
Keep learner data in the verified private workspace and preserve explicit backup
opt-outs; a missing remote leaves a local commit with an explained push limitation.

## Layout compatibility and older installed bundles

A trusted code/template update preserves records and their layout. A candidate
requiring a different workspace_layout or state_schema returns migration-required,
keeps the installed release and learner records intact, and requires explicit
rehearsal/activation through invo-learn migration operations. Do not rewrite state,
move learner folders, fake a compatible marker or rehash archives to make an
ordinary update succeed. Offline checks remain unavailable/unknown and safe
installed-version study remains possible.

The automatic updater validates the downloaded candidate before running its
upgrader in a fresh source interpreter. Preparation then uses the newly active
installed runner. This permits compatible packaging changes while retaining old
immutable bundles and current customization/backup checks.

For an older installed runner that cannot understand the combined package,
use the same temporary trusted setup helper in explicit upgrade mode:

```sh
python <temporary-tools>/setup_workspace.py <existing-private-workspace> --upgrade
```

Read the helper before executing it and obtain it from the trusted public repo.
It downloads temporary source, runs the current canonical upgrade operation and
removes the source afterward. Existing name, mailbox, preferences and opt-outs
are retained; this is maintenance, not another setup interview. Do not edit old
installed releases or add wrappers for their obsolete names. Known generated
workspace guidance is refreshed; custom AGENTS.md stays unchanged and its result
identifies any guidance that needs a careful pointer merge.

## Exact bytes through private Git backup

New setup installs a scoped managed block in .gitattributes so immutable originals,
packets, raw/normalized reports, reference artifacts, migration returns and
installed bundles survive Git checkout without newline conversion. The policy
preserves existing custom rule bytes and unrelated rule effects. Effective rules
that conflict with protected bytes are reported without overwriting those rules.

For an existing workspace use `python learn.py protect-record-bytes` during
explicit maintenance. It verifies existing archive checksums first, preserves
prior attribute bytes in .invo-learn/attribute-backups/, appends the scoped policy,
and verifies effective Git rules. No Git workspace still gets the tracked policy;
effective rules can be verified after Git initialization. If archived bytes have
already changed, preserve them for diagnosis and restore the correct original
copy; never silently update recorded checksums to accept changed evidence.

Include .gitattributes and related attribute-backup files in the individually
reviewed upgrade/maintenance commit scope. The private backup helper checks both
working and staged attribute rules before publishing, so an uncommitted policy
cannot leave a later clone unprotected. It retains the existing private-remote
identity/visibility checks, explicit file scopes, ordinary pushes and remote SHA
verification. It creates no remote and does not change visibility. Report local
maintenance success separately from backup status.
