# Verification

Run from the public checkout:

```sh
python -m unittest discover -s tests -v
python examples/worked_example.py
```

The current local run used Windows and Python 3.14: **72 tests passed, none
skipped**. Both symlink preservation and Windows directory junction rejection were
exercised successfully. Junction rejection uses Windows lstat reparse tags so it
also works with Python 3.10/3.11. The ordinary default temp directory was restricted
here, so TEMP and TMP were pointed at an allowed scratch directory outside the
public checkout. Git's shell helper required running the suite outside the sandbox.
Normal local runs use the system temp directory.

The suite covers independent setup (including a real new Git repository with no
remote), external/dedicated mailbox checks, preservation of originals and durable
packets, pending-session protection, nested mailbox content and metadata-name
collisions, source/packet integrity, malformed and duplicate-key reports, fenced
Windows line endings, duplicate/conflicting imports, false/hinted/contradictory
demonstrations, review timing/expansion/reset/capped repetition, evidence withdrawal,
map approval/staleness/prerequisites, supplemental opt-in, material-specific
transformation approval, private preferences/plans, update conflicts/schema
compatibility and recovery from injected state/activation write failures.

Flexible-arc tests cover explicit repair of diagnostic failures, preservation of
guided/failed attempts, unresolved and later failures, cross-objective/forward
resolution rejection, malformed/mixed annotations, practice-versus-assessment
evidence, relearning versus cold retention, visual hints, invalid-question
replacement, duplicate replay and evidence withdrawal. Update checks use mocked
GitHub responses to verify numeric versions, offline/invalid/oversized responses,
and unchanged private state. Status remains offline. The standalone worked
example also exercises diagnostic failure -> guided practice -> fresh repair.

Onboarding tests also cover temporary-archive installation with no source clone,
a working installed CLI and exported course/material skills, explicit preferences,
external mailbox ownership, refusal to overwrite existing files, archive traversal
rejection, durable mailbox intake, repeat-intake idempotence, and later uploads
without overwriting a pending lesson or changing an accepted map before approval.
They use a local archive fixture in place of the network response so the unreleased
package is tested, not whichever version is currently on GitHub.

The standalone synthetic worked example also passed. It receives resources via
the mailbox and runs the installed CLI
for report ingestion, coordinates two tracks, preserves a downloaded report during
mailbox reuse, distinguishes assisted understanding from independent work and
delayed retention, tests a synthetic newer release, and prepares subsequent repair.
The five portable skills retain name/description frontmatter. Whitespace
checks passed. No real learner records, credentials or source materials were used.
An independent synthetic forward-test checked novice repair, review relearning,
and faster pacing for a prepared learner; it did not measure learning outcomes.

The GitHub Actions workflow is configured for Windows and Ubuntu on Python 3.10
and 3.13. Those CI jobs have not been run from this local implementation session.
No live archive download of this unreleased version, real chatbot, external conversion service, calendar connector, or hosted
private-remote creation was exercised. Assertions validate the workflow and
evidence contract, not real-world learning efficacy or a model's grading accuracy.

## 0.4.0 workflow checks

Synthetic automation tests cover inherited detailed teaching and explicit shorter
styles, missing workflow defaults, global/track opt-outs and preference validation,
compatible activation in a fresh interpreter using new templates, incompatible or
customized releases, download/version races, pending-report deferral, immutable
restaging and regenerated handoffs. Existing tests cover caught activation rollback,
interrupted staging and state-write recovery, exact raw report bytes/checksums,
duplicate evidence and retained review state.

Backup tests use real Git commits and a temporary local bare repository, with
mocked GitHub API identity/visibility responses and redirected local transport.
They exercise scoped pushes and SHA verification, unrelated untracked/staged or
unpushed changes, no empty duplicate commits, missing/public/wrong-workspace or
unverified remotes, public visibility/forks/wrong identity/multiple destinations,
commit failure, push failure/retry and false push acknowledgement. Report/plan
backup failures preserve successful learning state and artifact bytes. No live
GitHub private repository, remote creation, credentials, or learner data is used.
Git's shell transport needed execution outside the restricted sandbox for local
bare-repository tests. The normal temp path was restricted; tests used an allowed
external scratch path. This is an environment constraint, not a learner requirement.

Course isolation tests prepare two synthetic courses without reporting the first,
check same-course duplicate prevention while the other is visible, restore either
packet, import reports across course switches, and abandon only a named pending
lesson. A corrupt hidden packet cannot replace the visible packet or its pointer.
Course-specific updates preserve another course's pending record and packet bytes.
