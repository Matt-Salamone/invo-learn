# Using invo-learn

Give your planning agent the public repository URL and ask it to use the setup
skill. It creates a **separate private local repository** containing one shared
profile and all your tracks. Python 3.10+ and Git are the only dependencies. No
paid chatbot session, API key, server, dashboard, or proprietary model is needed
to set up or test the workflow. Choose a chatbot that can read your lesson uploads.

## Setup and discovery

From a checkout of the public package:

```sh
python -m invo_learn bootstrap ../invo-learn-private --name "Learner"
```

Optional flags: `--mailbox <new-or-empty-dedicated-folder>` (relative to the private
root or absolute, including an external location), `--preferences <JSON-file>`.
The agent briefly collects defaults and offers optional scheduling. Example prefs:

```json
{
  "teaching_style": "short explanations with visual examples, then practice",
  "supplemental_research": false,
  "remediation": "recommend short prerequisite lessons; let me override",
  "schedule": null
}
```

Setup initializes a new Git repository with no remote, no inherited public history
and no commit requiring an identity. `--no-git` permits an explicitly chosen
files-only workspace. Local privacy means no publishing by the harness; access
permissions and backup/encryption follow your computer's configuration. A hosted
private remote is optional and requires an explicit request. Verify visibility
before pushing. Never use a public fork as your learner workspace.

Open the private workspace with your agent. AGENTS.md routes to the installed
skills in `.agents/skills/`. For hosts that do not discover that location, ask
them to read AGENTS.md and the skill directly, or configure their project skill
search path to `.agents/skills`. There is no global configuration modification.
The versioned bundle includes reference docs at the release path in
`.invo-learn/active.json`.

## Normal learner workflow

1. Tell the agent your course or skill and provide its materials. It inherits
   defaults, confirms relevant overrides, and offers optional scheduling.
2. Review the source-linked coverage map and proposed lessons. Later uploads
   produce proposed changes for review. Unreadable materials remain visible gaps
   until readable or converted with your permission; originals are always retained.
3. Ask for the next lesson or due review. The agent stages all relevant files in
   your chosen mailbox. Upload **every visible file** in that folder into a **fresh
   chatbot conversation**. Ask: "Teach START-HERE.md, then return the invo-learn
   JSON report."
4. Learn with the chatbot, then copy its one complete JSON report back to the
   planning agent. The agent handles saving/importing and updates your records.
   You do not reconstruct a transcript or run an import command.
5. Review the outcome and next steps. The agent recommends remediation when
   needed; you can explicitly override progression while retaining the gaps.

The mailbox is temporary staging, not source storage. A lesson remains durably
archived in lessons/. Reuse requires its report or an explicit abandonment. All
old mailbox files (including unexpected downloaded reports) are copied into
inbox/mailbox-snapshots before any clearing. Snapshots are preserved but do not
automatically become learning evidence; the agent inspects/ingests returned reports.
Do not repurpose the mailbox or put unrelated personal files there.

## Agent tool recipes

From the private root (the learner need not run these):

```sh
python learn.py status
python learn.py add-track algebra --title "Algebra"
python learn.py add-material algebra /path/to/notes.pdf
python learn.py inspect-material algebra <material-id> --note "Read pages 1-8 with PDF tool; equations preserved"
python learn.py propose-map algebra /private/path/map.json
python learn.py accept-map algebra <proposal-id> --approval "Learner approved this coverage map"
python learn.py prepare algebra /private/path/lesson.json
python learn.py ingest /private/path/exact-pasted-report.txt
```

The tools print JSON IDs to use in subsequent specs. Contract shapes and a complete
example report are in [contracts.md](contracts.md) and the public examples folder.
`python learn.py --help` lists all commands. Global `--workspace` and `--today`
options go **before** the subcommand. `--today YYYY-MM-DD` defaults to system local
date; the agent supplies learner-local date if the host differs. Never fabricate
elapsed time for real retention. stdin is also supported for ingest.

Use preferences with a JSON file and optional --track to change global defaults
or overrides. Review intervals are independent of calendars: `review-policy 1 3
7 14 30 60` adjusts the shared policy and recomputes due dates from evidence.
`override <track> <objective-ids...> --reason <explicit-learner-request>` records
advisory progression choices. `dispute <report-id> --reason <explanation>` withdraws
the whole report from progress calculations, retaining it for audit; reassess
with a fresh lesson. This conservative first version has no partial regrading UI.

If a file needs transformation, describe the proposed LOCAL workflow and ask the
learner before creating it. Record consent using approve-transform, then execute
the approved workflow with available tools and register its inspected output
with add-derived. The helper does not run arbitrary converters or certify that
consent occurred; the skill is responsible for actual permission. Approval is
single-use for that material and workflow. No external service uploads or
automatic reuse across other materials are authorized by that approval.

## Records and recovery

`state.json` is the authoritative, inspectable database: profile, track overrides,
source provenance, accepted/pending maps, lesson metadata, report evidence, due
reviews, transformation approvals, progression overrides and an event history.
It is atomically replaced under a single-writer lock. The report and raw input
are durable before evidence is committed. Overview/coverage Markdown are generated
views; `tracks/<id>/plan.md` is an agent-editable adaptive plan preserved by render.
Original files, derived artifacts, packets and report JSON live outside the mailbox.

Malformed reports keep their raw input in inbox/reports and add no evidence.
Duplicate reports return duplicate without changing progress/review dates.
Conflicting IDs or a second report for one lesson are rejected. The agent may
remove unambiguous formatting errors; it must never fill missing learning evidence.
Use a regenerated complete report for rejected input, or fresh reassessment for
a disputed accepted report. The tool accepts raw JSON or one fenced JSON block;
it deliberately does not guess JSON from mixed prose.

After an interrupted prepare, restage the active lesson ID. Packet checksums,
mailbox ownership and link checks run before clearing. If an operation.lock file
remains after a crash, verify no process is operating on the workspace before
removing that one lock. If render fails after a committed mutation, resolve the
filesystem problem then run render. An interrupted import can be retried; source
files left outside state are recovery artifacts, never evidence by themselves.
Back up the **entire** private repository; review state alone omits originals.

## Explicit updates

Ask the agent to update, or run from the private root:

```sh
python learn.py upgrade --source /path/to/trusted-public-checkout
python learn.py status
```

The checkout's VERSION must be newer and immutable. harness.json declares the
package/state/report schemas and minimum Python version, checked before installation.
No network fetching or silent
auto-update occurs. Managed harness/skill customization conflicts are rejected.
Prior releases plus pre-update state/activation backups remain under .invo-learn/;
learner profile, overrides, plans, reports, materials and reviews remain intact.
The current updater supports state schema 1; future incompatible schemas require
an explicit migration implementation. Downgrades are rejected. A crash during
skill export may require restoring the managed skills from the unchanged active
release before retrying; ordinary caught failures roll back those exports.

## Limits

Tooling validates recorded evidence; it cannot verify a chatbot's rubric, truth
of an answer, claimed independence, or completeness of a source interpretation.
Inspect rationale and use later fresh reviews. Complex formats require available
reader/conversion tools and explicit transformation permission. Very large sources
need agent-selected excerpts/chunks. The system coordinates a single learner's
tracks, not simultaneous users or concurrent agents. File locking prevents concurrent
writes; network filesystems and hostile filesystem races are outside the guarantee.
Scheduling is a plan/preference, not calendar API integration or background reminders.
