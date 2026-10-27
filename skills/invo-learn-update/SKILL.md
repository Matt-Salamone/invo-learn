---
name: invo-learn-update
description: Automatically update before lessons or reviews, handle explicit upgrades, and recover failed invo-learn installations without losing learner records.
---

# Trusted harness updates

Save and ingest returned reports FIRST, update records and plan.md, and finish
that report's backup using the study skill. Inspect mailbox uploads before reuse.
Never make a network update the first action on a returned report.

Before planning/preparing a lesson or review, run:

```sh
python learn.py study-update --track <id>
```

Pending sessions defer study-update only for the requested course; a workspace-wide
check without --track defers while any session is pending. A pending lesson in
another course does not block this course's update or preparation. Upgrades must
preserve all pending records and archived packets unchanged. Ingest any reports
actually returned in the mailbox or chat before updating.

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
reread newly active skills/docs before writing the lesson spec. Never edit old
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

After a completed handoff or processed report/plan, follow the study skill's
automatic scoped private backup step. Include related update bundles/exports and
recovery backups when reviewing the completed file scope. Report installation,
learning and Git backup outcomes separately.

## End-of-interaction synchronization

When this interaction changes learner-workspace files, follow its AGENTS.md and
the active invo-learn skill's commit/push instructions before the final response.
This includes stopping to wait for an onboarding answer after saving records.
Keep learner data in the verified private workspace and preserve explicit backup
opt-outs; a missing remote leaves a local commit with an explained push limitation.
