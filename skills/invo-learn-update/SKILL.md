---
name: invo-learn-update
description: Explicitly upgrade a private invo-learn workspace from a trusted public harness checkout while preserving learner preferences, materials, evidence and review state.
---

# Explicit harness update

Act only on a learner's request to update. Read `.invo-learn/active.json` in the
private workspace and the desired public checkout's VERSION and CHANGELOG.md.
Obtain the requested release from https://github.com/Matt-Salamone/invo-learn in a
separate tools/cache checkout. Avoid changing a public checkout with unrelated
local edits; an independent clone is an appropriate alternative.

Routine study uses `python learn.py check-updates` for a read-only version check
against GitHub. An available update is a notice, not permission to install it;
continue normal study unless an update is requested. Network failure must not
block lessons or be reported as proof that the installed version is current.

From the private workspace run:

```sh
python learn.py upgrade --source <trusted-public-checkout>
python learn.py status
```

The helper installs an immutable versioned bundle, keeps prior bundles and a
pre-update state/activation backup, refreshes managed skills, and explicitly
switches the active release. It checks installed-file modifications and rejects
same-version content changes, downgrades and incompatible state schemas. It
does not overwrite learner preferences, plans, original/derived materials,
reports, lessons or review records. It does not fetch code or update itself.

If custom harness/skill files conflict, preserve those custom files privately and
explain the conflict. Never force an overwrite or edit a manifest to bypass the
check. Resolve the customization with the learner, then retry. For unsupported
schemas, stop the update with records intact; a documented migration must exist
before proceeding. Read the newly installed skills/docs after success and
report the installed version and any behavior changes.
