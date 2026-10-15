# Verification

Run from the public checkout:

```sh
python -m unittest discover -s tests -v
python examples/worked_example.py
```

The final local run used Windows and Python 3.13.2: **39 tests run, 38 passed,
1 skipped**. The skipped test attempts to create a Windows directory junction;
creation was unavailable in the execution environment. The symlink preservation
test passed. Junction rejection is implemented using Windows lstat reparse tags
so it also works with Python 3.10/3.11, but a real junction could not be exercised
in this run. The ordinary default temp directory was restricted here, so TEMP
and TMP were pointed at an allowed scratch directory outside the public checkout.
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

The standalone synthetic worked example also passed. It runs the installed CLI
for report ingestion, coordinates two tracks, preserves a downloaded report during
mailbox reuse, distinguishes assisted understanding from independent work and
delayed retention, tests a synthetic newer release, and prepares subsequent repair.
All three SKILL.md files passed the skill-creator frontmatter validator. Whitespace
checks passed. No real learner records, credentials or source materials were used.

The GitHub Actions workflow is configured for Windows and Ubuntu on Python 3.10
and 3.13. Those CI jobs have not been run from this local implementation session.
No real chatbot, external conversion service, calendar connector, or hosted
private-remote creation was exercised. Assertions validate the workflow and
evidence contract, not real-world learning efficacy or a model's grading accuracy.
