# Using invo-learn

For packet checks/reduction, objective-specific gaps, report repair, correction
investigations, evidence relevance and offline recovery, see
[quality and recovery](quality-and-recovery.md). The agent handles these operations;
the learner still uploads one mailbox and returns one pasted report.

Give your planning agent the public repository URL and ask it to use the setup
skill. It installs **one learning workspace** containing the harness, shared
profile and all your courses. You do not need a public clone or a second project.
Python 3.10+ and Git are the only dependencies. No
paid chatbot session, API key, server, dashboard, or proprietary model is needed
to set up or test the workflow. Choose a chatbot that can read your lesson uploads.

## Setup and discovery

Ask the agent to set up the current new/empty folder. Its first question is
**"Would you like to set up using all defaults?"** It briefly explains those
defaults and stops until you answer. Yes uses the current new/empty folder,
the generic name "Learner", the teaching/research/catch-up defaults below,
`mailbox/` in that folder, and no schedule; already supplied choices are retained.
No starts a guided interview, explaining and asking one choice at a time.
You can also request a specific exception and use defaults for everything else.
It never infers your name or acceptance from your computer account or silence.
Preferences mean:

- **Teaching style:** longer, detailed, comprehensive explanations before practice,
  with conceptual mechanisms, causal reasoning, worked examples and useful visuals.
  Demonstrated knowledge skips unnecessary explanation; explicit overrides win.
- **Automatic updates:** compatible trusted updates before lessons/reviews; opt out
  with auto_update=false.
- **Automatic private backups:** agent commits/pushes completed handoffs and processed
  reports/plans to a verified private learner remote; opt out with auto_backup=false.
  No remote is created automatically; without one, completed work stays local.
- **Supplemental research:** optional extra explanations/examples beyond your
  files, labeled separately; your files still define course scope. Off by default.
- **Prerequisite help:** suggest catch-up lessons when missing background skills
  cause difficulty; you can still choose to move on.
- **Scheduling:** optional study times, time budgets, or deadlines. Review dates
  work without a schedule; there are no automatic notifications or calendar events.
- **Mailbox:** the place you drop off course materials and pick up lesson files.

The agent downloads and reads `setup_workspace.py` into temporary tools storage.
For manual setup, run that script with a new/empty destination:

```sh
python /temporary/tools/setup_workspace.py /path/to/my-learning --name "Learner"
```

Optional flags: `--mailbox <new-or-empty-dedicated-folder>` (relative to the private
root or absolute, including an external location), `--preferences <JSON-file>`.
The agent briefly collects defaults and offers optional scheduling. Example prefs:

```json
{
  "teaching_style": "detailed mechanisms and worked examples with visuals before practice",
  "auto_update": true,
  "auto_backup": true,
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

The installer downloads an archive into temporary storage, installs a pinned
bundle, and removes the temporary source. There is no permanent source clone.
Developers can still bootstrap from a trusted checkout using `python -m invo_learn
bootstrap <new-learner-folder> --name "Learner"`; learner records must not go into
the public developer checkout. Setup never alters an existing nonempty folder.

Stay in the learning workspace with your agent. START-HERE.md explains how to begin.
AGENTS.md routes to the installed
skills in `.agents/skills/`. For hosts that do not discover that location, ask
them to read AGENTS.md and the skill directly, or configure their project skill
search path to `.agents/skills`. There is no global configuration modification.
The versioned bundle includes reference docs at the release path in
`.invo-learn/active.json`.

## Normal learner workflow

1. Say **"Add a course"** or name the course/skill. The add-course skill explains
   each choice, asks one question at a time, and waits. It inherits global settings,
   supports course overrides, and offers optional scheduling. The agent gives you
   the actual mailbox path. Put the course resources there and say **"materials
   ready"**; attachments or existing file paths also work. The agent copies and
   registers originals in durable course storage. You do not file them manually.
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
5. Review the outcome and next steps. The agent recommends catch-up help when
   needed; you can explicitly override progression while retaining the gaps.
6. For additional uploads, say **"Add materials to [course name]"**, drop the new
   resources in the same mailbox, and say **"materials ready."** The add-materials
   skill files them in that existing course and proposes coverage changes for your
   review. Existing objective IDs, evidence, and review progress are preserved.
   Uploading files alone does not approve a new plan.

The mailbox is a two-way exchange, not permanent source storage. The agent
distinguishes new resources, old handoff files, and returned reports. Add new
resources alongside a pending lesson without overwriting its files; intake does
not abandon that lesson. Ambiguous files/course destinations get one clarification
at a time. Originals are copied to `tracks/<id>/materials/originals/`; mailbox
copies remain until guarded lesson staging snapshots them. A lesson remains durably
archived in lessons/. Each course may have one pending lesson at a time. Preparing
another in that same course requires its report or explicit abandonment; a pending
lesson in another course does not block preparation. Switching courses snapshots
the shared mailbox and keeps other lessons prepared, with their archives intact.
Use status to list pending lesson IDs by course; active_lesson identifies only the
last staged packet. restage <lesson-id> restores any prepared packet to the mailbox,
and abandon <lesson-id> explicitly abandons only that prepared lesson. Reports can
arrive in any course order and are matched by lesson/track IDs. A course switch
never abandons a lesson. Inspect/ingest actual returned reports before switching.
Course-specific study-update defers only for that course's pending lesson; without
--track it defers for any pending lesson. Updates preserve archived packets. All
old mailbox files (including unexpected downloaded reports) are copied into
inbox/mailbox-snapshots before any clearing. Snapshots are preserved but do not
automatically become learning evidence; the agent inspects/ingests returned reports.
Do not repurpose the mailbox or put unrelated personal files there.

## How lessons teach

The default gives longer, detailed, comprehensive explanations before practice:
conceptual mechanisms, causal reasoning and worked examples with justified steps.
Explicit learner preferences override this depth. A cold review starts with retrieval
before repair teaching, so explanation cannot contaminate retention evidence.

The chatbot follows a flexible arc: diagnose, build a visual model with an example,
invite an attempt, diagnose that attempt, choose a targeted response, check fresh
independent work, and close with recall and transfer. It asks one manageable
question at a time and waits for your answer. Prior knowledge can skip unnecessary
explanation; beginners may need a worked example before attempting a whole task.

Good reasoning leads to less support or a changed application. A correct answer
with weak reasoning leads to a why/prediction/boundary question. A small mistake
gets a focused correction; a conceptual error gets a different representation.
After hints, you try a distinct unaided task. Repeated difficulty calls for a
smaller task, prerequisite help or a pause. These choices replace a fixed
concept/example/quiz sequence and avoid repeating the same unsuccessful repair.

Reports keep diagnostic, practice and assessment attempts in order. An early
failure can be explicitly resolved by a later fresh unaided assessment without
discarding the mistake. Practice alone does not prove understanding. Reviews ask
for retrieval before teaching; success after reteaching is relearning and prompts
another review rather than establishing retention. Older reports keep their
original conservative grading rules.

Lessons make liberal use of meaningful visuals, including interactive diagrams,
charts or simulations when supported; readable static alternatives work in other
chatbots. Explanations and questions stand on their own without slide/page
commentary or requests to consult uploads. The materials still define scope and
ground accuracy; source links stay in the coverage map and tutor context, and
you can ask for provenance separately. Visual hints count as assistance.

These teaching behaviors depend on the chatbot following its handoff. The runtime
validates the returned evidence and updates records; it does not control chat
turns, render interactive lessons or inspect the full teaching conversation.

Every teaching-chatbot turn ends with a compact progress bar and a separate
provisional mastery summary, including the first turn, pauses and the final report:

```text
Lesson progress: [####------] 4/10 checkpoints | Now: fresh application
Mastery (provisional): 1/3 objectives independent; 0/3 retained | Current: equality — guided
```

The chatbot briefly names lesson checkpoints at the start. A question counts only
after you answer and receive feedback. Repairs or skipped steps may change the
total, with an explanation; stopping early does not force the bar to 100%.
Completing a lesson can leave mastery gaps. Mastery labels reflect evidence for
each objective: unassessed, guided, independent, retained, needs-review or uncertain.
Retained objectives are included in the independent count. Hints cannot establish
independence, immediate success cannot establish retention, and conflicting
evidence can lower the displayed status. The footer uses existing packet records
and current attempts; only report ingestion updates your durable records. On the
final turn, it appears outside the report's JSON block so copying the report works
as before. These displays require the chatbot to follow the handoff instructions.

## Agent tool recipes

From the private root (the learner need not run these):

```sh
python learn.py status
python learn.py check-updates
python learn.py add-course algebra --title "Algebra"
python learn.py add-material algebra /path/to/mailbox/notes.pdf
python learn.py inspect-material algebra <material-id> --note "Read pages 1-8 with PDF tool; equations preserved"
python learn.py propose-map algebra /private/path/map.json
python learn.py accept-map algebra <proposal-id> --approval "Learner approved this coverage map"
python learn.py prepare algebra /private/path/lesson.json
python learn.py ingest /private/path/exact-pasted-report.txt
```

`add-track` remains an alias for add-course; internal track IDs and record paths
are unchanged. Direct mailbox intake copies bytes into durable storage, retaining
the staging copy. Retrying identical mailbox bytes for the same course and role
reuses the material record. The agent checks original integrity before reuse.

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

## Automatic updates and migration

Before each lesson/review, the agent saves/ingests returned reports, revises their
plans, and completes their backup first. Then `study-update --track <id>` checks
the trusted public VERSION and automatically installs a newer compatible snapshot
from the fixed public repository. prepare checks too, and after activation starts
a fresh interpreter so the handoff uses newly active code and templates. The agent
rereads new instructions before generating its spec. Updates require no separate
request once this default is chosen. `check-updates` remains read-only.

Use `preferences <private.json>` with `{"auto_update": false}` to opt out (or
`--track <id>` for a course override). A manually requested update still uses
`upgrade --source <trusted-public-checkout>`. No learner records are sent upstream.
The trusted main snapshot is not cryptographically signed. A version/download
race, unavailable Git/network, incompatible candidate or modified managed file
leaves study on the installed version when safe. The result is explained; failed
verification never means current. There is no search through historical releases
for a compatible candidate if latest is incompatible.

Existing installs need one authorized upgrade to 0.4.0 or later. The agent explains
these changed defaults and opt-outs before that upgrade. If the old CLI rejects
new keys, retain chosen opt-outs in private notes and apply them through the new
preferences command immediately after upgrading, before study. Thereafter missing
workflow keys inherit true, while explicit true/false values and every stored
teaching style survive. Legacy styles may look like old defaults; without reliable
choice provenance they are preserved. To adopt the new teaching style in such a
workspace, explicitly set teaching_style to the detailed style above (or ask the
agent to do it). Missing teaching_style inherits the new default. New tracks
inherit effective global settings, and track overrides still win. No schema
migration rewrites records. A preferences change does not rewrite old packets.

Existing compatibility/customization checks, immutable releases, pre-update
state/activation backups and export rollback remain. Reports, source bytes and
checksums, plans, evidence, lesson archives and review state survive. Never force
an overwrite, bypass a conflict or downgrade. After interrupted skill export,
restore managed skills from the unchanged active release before retrying; inspect
activation and verify no process is alive before clearing a stale operation lock.
restage recovers the existing archive exactly. Regeneration with new instructions
means prepare a new lesson ID after ingestion or explicit abandonment of the old
one; keep the old archive. An activated update may remain active if a later
preparation fails; retry preparation or recover its pending packet, not the update.

## Automatic private Git backup

The agent, rather than the teaching chatbot or low-level record mutation, performs
this default step after a prepared/regenerated lesson (including successful
restage recovery), or a successfully ingested report AND updated plan. It reviews
Git status/diffs and lists only the completed operation files, including related
originals, exact raw input, normalized report, archive, views, plan and any update
bundles/backups. It then runs:

```sh
python learn.py configure-backup --remote origin --repository OWNER/PRIVATE-REPO
python learn.py backup --paths state.json OVERVIEW.md tracks/math/plan.md OTHER-COMPLETED-FILES --message "Process report <id>" --track math
```

configure-backup is a one-time binding of an already explicitly identified learner
remote to this workspace ID. The agent must include the actual individual files,
not the illustrative placeholder, a directory, or all changes indiscriminately.
Creating a remote/private repository still requires an explicit request; the
helper never creates one, changes visibility, force-pushes or targets the public
harness. Direct CLI/library mutations save learning work but do not substitute
for the agent's final backup step after its plan edits.

Verification currently supports independent GitHub repositories through Git and
authenticated `gh api`. Both fetch and push must have one identical direct URL,
no Git URL rewrites, matching the workspace binding; the API must confirm private
visibility, identity and push access. Forks and the public harness are refused.
Visibility is checked again before push. Other hosts/unverifiable privacy, no
remote, no credentials or no Git mean local work is retained and the agent explains
the missing setup. No automatic remote creation occurs.

Only explicitly reviewed completed files enter the commit. Existing staged
changes and unpushed history outside the scope cause refusal. This includes
changes in each pending commit, so reverted unrelated changes are not hidden.
If a completed file also contains unrelated edits, the agent must resolve that
scope before backup. A push uses the current branch explicitly, without force,
and verifies its SHA with ls-remote. Remote divergence fails safely; resolve it
without force or discarding learner records. A failed commit can leave the scoped
files staged; inspect them before retry. A failed push leaves a local commit;
retry backup, not the successful learning operation. A failed backup attempt does
not block the next safe update or lesson; explain it and keep work local. Unknown verification is
reported as backup failure, never a successful push.

Opt out with `{"auto_backup": false}` via preferences, globally or per track.
An unchanged duplicate report requires no commit; a different exact raw paste
can be saved/backed up without duplicating evidence. The helper never creates an
empty commit and supports retrying a previously failed push. Report learning,
update and backup outcomes separately. Local-only work is still completed study;
it has no verified remote backup until setup and push succeed.

## Limits

Tooling validates recorded evidence; it cannot verify a chatbot's rubric, truth
of an answer, claimed independence, or completeness of a source interpretation.
Inspect rationale and use later fresh reviews. Complex formats require available
reader/conversion tools and explicit transformation permission. Very large sources
need agent-selected excerpts/chunks. The system coordinates a single learner's
tracks, not simultaneous users or concurrent agents. File locking prevents concurrent
writes; network filesystems and hostile filesystem races are outside the guarantee.
Scheduling is a plan/preference, not calendar API integration or background reminders.
