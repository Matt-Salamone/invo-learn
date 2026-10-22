---
name: invo-learn
description: Plan source-grounded learning tracks, stage manual chatbot lessons or spaced reviews, and ingest pasted invo-learn reports into a private learner workspace.
---

# Plan, hand off, and record learning

Work from the private workspace root. Read AGENTS.md, state.json, OVERVIEW.md and
all active tracks' plan.md files. `python learn.py status` lists inherited
preferences, pending maps, source gaps and cross-track due reviews. Use the
active release path in `.invo-learn/active.json` to read docs/user/guide.md and
docs/user/contracts.md for JSON shapes and recovery. `python learn.py --help`
lists the tools. Use these helpers for durable state; keep flexible lesson plans,
priorities and notes in `tracks/<id>/plan.md`.

## New or changed tracks

Use `../invo-learn-add-course/SKILL.md` for a new course or skill and
`../invo-learn-add-materials/SKILL.md` for first or additional resources. Explain
each unfamiliar choice, ask one question per turn, and stop and wait for an answer.
Reuse existing courses and preferences when receiving later uploads. The mailbox
is the shared interface for resources, lesson packets, and returned reports;
always say which action is next and give its actual path.

Use add-material for EVERY uploaded file, regardless of extension. Originals are
copied into durable track storage. UTF-8 text is automatically usable. For other
formats, inspect with available reading tools; if directly usable, record tools,
coverage and limitations with inspect-material. If unusable, FIRST ask permission
to create a specific local automatic transformation workflow, naming tools,
outputs and likely fidelity loss. Only after actual permission, record it with
approve-transform, create/run the workflow, inspect its output, and use add-derived
with that approval. Approval is per material and single use; no silent reuse or
external conversion services. If local conversion is unavailable, retain an
explicit source gap and explain what is needed. Never invent readable content.

Inspect all primary material and propose a source-linked coverage map aiming to
cover it all, using propose-map. Account for every source or explain a source gap.
Show objectives, locators, prerequisites, deferrals and missing/unassessed areas
for learner review; accept-map only after approval (existing explicit approval
counts). Subsequent uploads propose additions/changes rather than silently
changing scope. Preserve existing objective IDs; changed meaning requires a new
ID and deferral of the old one. Supplemental research is opt-in per track, labeled
separately, and cannot expand authoritative uploaded scope on its own.

## Next lesson or review

Before preparing a lesson/review, save and ingest every returned report FIRST,
update its records and plan, then finish the report backup below. Inspect the
mailbox for reports/resources before updating or staging. Read
`../invo-learn-update/SKILL.md` and run `python learn.py study-update --track <id>`.
The default automatically installs a newer compatible trusted release without a
separate request each time. Honor auto_update=false. After activation, reread the
new active study/update skills and templates before writing or regenerating the
lesson spec. prepare also checks automatically and runs newly active code in a
fresh interpreter. Offline, incompatible or safely failed updates leave study
available; explain the actual result and never call an unverified version current.
Do not retry conflicts by overwriting custom files. Do not update during teaching
questions. restage recovers an immutable archived packet; to regenerate with new
instructions, ingest its report or obtain explicit abandonment, then prepare a
new lesson ID. Keep the previous archive and checksums.

Inspect independent evidence, misconceptions and unresolved prerequisites. Pick
the next useful objectives, recommending remediation with a clear explanation.
Advancement is advisory. Record an explicit learner override with override while
retaining the gap. Include due reviews according to relevance and preferences;
no review backlog locks new work. Match fact/concept/skill reviews to recall,
explain-back/fresh application and choose unfamiliar tasks where useful.

Write a private lesson spec with source-grounded context and selected original
or derived attachment IDs. Choose a packet, excerpts, originals or combination
according to fidelity, context size and convenience; include source locators and
relevant learner context. prepare archives the complete packet durably and
replaces the dedicated mailbox, preserving its previous contents in snapshots.
Never manually delete mailbox contents. Preserve/ingest a returned report before
reuse. Check pending lessons for the requested course using status, not only
active_lesson (the last staged packet). If that course has a pending lesson,
request its report or record an explicitly requested abandonment before preparing
another in the same course. Pending lessons in other courses do not block new
lessons or reviews. Preserve their prepared status and immutable packets; guarded
prepare snapshots the shared mailbox. restage can switch the mailbox to any
prepared lesson by ID without abandoning other courses. Reports can arrive in
any course order and are matched by lesson/track IDs. Never infer abandonment
from a course switch. Inspect and ingest actual returned reports before switching;
an absent report from a different course is not a blocker.

Create lessons that stand on their own: include the definitions, reasoning,
examples and figure descriptions needed to teach the objectives without asking
the learner to consult uploads. Keep source locators for tutor reference and
coverage records; learner-facing explanations and questions must not narrate
sources (such as "page 6 of the slides says") or assume the learner has them open.
Ground the content in the materials without making source commentary the lesson.
Provide provenance separately only when the learner asks; disclose missing or
uncertain content rather than inventing it.

Make liberal use of meaningful visuals in lessons. In the teaching context,
identify useful diagrams, charts, annotated examples or simulations and explain
what they should make clear. Prefer interactive visuals when supported and useful;
include a readable static or text-based alternative when interaction is unavailable.
Visuals need labels and a verbal explanation, and assessment visuals must not
reveal answers or disguise hints as independent work. These teaching rules also
apply to review handoffs; keep retrieval unaided before supplying visual help.

Default to longer, detailed, comprehensive explanations before practice, covering
conceptual mechanisms, causal reasoning and justified worked examples. Supply enough
context for this depth, with useful diagrams and supported interactive visuals
plus readable static alternatives. Honor explicit learner teaching preferences.

Plan a flexible arc: diagnose -> visual model/example -> learner attempt ->
diagnose the attempt -> targeted response -> fresh independent check -> recall
and transfer. Supply likely misconceptions, alternative representations and
useful transfer tasks in context, without scripting every turn. Skip unnecessary
explanation for prior knowledge; show novices a worked example when needed.
The chatbot should fade support after sound reasoning, probe correct answers
with weak reasoning, repair local errors, change representation for conceptual
errors, and try a new unaided task after guided success. Repeated difficulty calls
for a smaller task or prerequisite check, not an endless quiz. Keep one question
at a time and wait for answers. Retrieve before teaching in reviews.

Use chronological diagnostic/practice/assessment annotations in new reports as
described in docs/user/contracts.md. Retain earlier mistakes and assistance;
fresh unaided assessment can explicitly resolve earlier failures. Guided practice
never counts as independent performance, and relearning during a review never
counts as retention. Legacy reports without annotations keep conservative grading.

Require a compact lesson progress bar and separate provisional mastery summary
at the end of every teaching-chatbot turn, including opening, pause and report
turns. Plan meaningful checkpoints for the assigned lesson; the chatbot can adapt
their total for repair or skipped steps and must explain revisions. Completion
tracks delivered teaching/evaluated attempts, never turns elapsed or mastery.
Mastery tracks each objective's unassessed/guided/independent/retained or uncertain/
needs-review evidence using the report rules, including prior packet records.
Hints cannot earn independence; retention requires cold delayed review. Keep
footer text outside report JSON; the planning agent remains the durable authority.

Before preparing/restaging, inspect the mailbox for new course resources and
returned reports. Register new resources via the add-materials skill and ingest
reports first. Ask about ambiguous files rather than silently archiving unprocessed
uploads. Snapshots are recovery copies, not evidence that intake was completed.

Tell the learner: "Upload every visible file in the mailbox into a fresh chatbot
conversation. Ask it to teach START-HERE.md and return the JSON report. Paste that
one report back here." The chatbot teaches; you own curriculum and records.

## A report pasted into this chat

Automatically save the exact pasted report in a PRIVATE temporary/input file and
run ingest on it (or send it on stdin). This is your bookkeeping, never an import
chore for the learner. Use the learner's actual local completion date; `--today`
may correct host timezone but must not simulate retention for real learning.
ingest preserves the raw paste before validation, then atomically commits
validated evidence. Exact/semantic duplicate imports are idempotent. Missing or
invalid fields add no learning evidence. Inspect errors and the preserved input;
fix formatting only when unambiguous, never invent answers, hints or rationale.
For missing evidence ask the chatbot to regenerate the SAME single report; the
learner still only pastes it. Report ID conflicts require inspection, not renaming
the ID to force a second import.

Inspect the updated evidence and next-step recommendations. Hinted, repeated,
invalid or unresolved contradictory assessments cannot establish independent mastery.
Uncertainty remains visible; use fresh assessments. If a grading/source dispute
invalidates a report, use dispute with the reason; original evidence is retained
and progress/reviews are recomputed. Revise plan.md, explain the result briefly,
and prepare the next agreed lesson/review. Only delayed independent review passes
establish retention. Prefer concise observable judgments to mastery percentages.

## Automatically back up completed learning work

After successful prepare/regeneration or restage recovery, and after successful
report ingestion AND plan.md updates, automatically run backup unless the effective
auto_backup preference is false. This is agent bookkeeping; no per-operation
confirmation is needed. Direct CLI/library calls do not replace this agent step.

Inspect Git status and diffs first. Enumerate only completed operation files,
including state, generated views, updated plan, exact raw report, normalized report,
new durable packets/snapshots, and related registered originals not yet backed up.
Include active bundles/exports/backups after an update. Preserve all bytes and
checksums; do not rewrite archives to modernize them. Never use git add ., -A,
a directory scope, an empty commit, or include unrelated edits. If a shared file
contains unrelated changes, leave it for review instead of committing the mixture.

Use `python learn.py backup --paths <file1> <file2> ... --message "Prepare lesson <id>" --track <id>`
(or a report-specific message). File paths are workspace-relative, individually
reviewed; include prerequisite unpushed history files only if they are related.
The helper refuses pre-staged changes or unrelated unpushed history, verifies a
private independent GitHub destination, commits the scope, pushes without force,
and checks the remote branch SHA. A duplicate ingest with no changed files needs
no backup; a new raw representation or an outstanding failed backup may be backed
up without duplicating evidence or creating an empty commit.

A remote must be explicitly identified as this learner workspace's independent
private repository. If already authorized, verify it and bind it once using
`python learn.py configure-backup --remote origin --repository OWNER/REPO`.
No silent remote creation or visibility change. Never bind the public harness or
a fork. The helper needs Git and authenticated gh for private identity/visibility
verification. If absent or unverifiable, retain work locally and explain the exact
setup needed. Other hosts require a separately verified manual backup workflow.

A failed backup attempt does not block the next safe update/lesson. Explain the
failure and keep the completed work local.

Report learning success separately from backup status. If commit/push fails,
preserve the successful operation and explain the failure; retry the backup scope,
not ingestion/preparation. Commit failure may leave scoped files staged; inspect
and resolve that index before retrying. Never claim a push succeeded without the
verified remote SHA. Respect auto_backup=false globally or per track; set it via
preferences, not by disabling validation.
