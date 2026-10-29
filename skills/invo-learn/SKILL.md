---
name: invo-learn
description: Set up and maintain one private learning workspace, add courses and materials, plan lessons and assignments, stage chatbot handoffs, and ingest returned reports.
---

# invo-learn

Use this single entry point for the whole learning workflow. For first setup,
read `references/setup.md` before creating learner files. It explains defaults,
asks one question per turn, and waits for each answer. For an existing workspace,
continue below. For a new course read `references/add-course.md`; for first or
later uploads read `references/add-materials.md`. For automatic updates, explicit
upgrades or recovery read `references/update.md`. These are internal operation
instructions, not separately invoked skills.

Work from the private workspace root. Read AGENTS.md, state.json, OVERVIEW.md and
all active tracks' plan.md files. `python learn.py status` lists inherited
preferences, pending maps, source gaps and cross-track due reviews. Use the
active release path in `.invo-learn/active.json` to read docs/user/guide.md and
docs/user/contracts.md for JSON shapes and recovery. `python learn.py --help`
lists the tools. Use these helpers for durable state; keep flexible lesson plans,
priorities and notes in `tracks/<id>/plan.md`.

For packet size/relevance checks, verified context reduction, structured gaps,
report repairs, content concerns, stale-report/evidence review, explicit packet
replacement, or pacing decisions, read the active release's
`docs/user/quality-and-recovery.md`. Use status's next_action/work_queue to resume
unfinished bookkeeping. Use doctor for offline integrity/recovery diagnostics;
its health result does not establish teaching quality or fresh remote status.

## New or changed tracks

Use `references/add-course.md` for a new course or skill and
`references/add-materials.md` for first or additional resources. Explain
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

Before writing a new lesson/review spec, read the active release's
`docs/user/syntax-references.md`. Classify whether its exercises require coding
with `coding`; for coding lessons author `syntax_cheatsheet` so prepare preserves
a standalone permitted syntax reference in the packet and mailbox.

Before preparing a lesson/review, save and ingest every returned report FIRST,
update its records and plan, then finish the report backup below. Inspect the
mailbox for reports/resources before updating or staging. Read
`references/update.md` and run `python learn.py study-update --track <id>`.
The default automatically installs a newer compatible trusted release without a
separate request each time. Honor auto_update=false. After activation, reread the
new active invo-learn instructions and templates before writing or regenerating the
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

Record routine changes to practice, explanation depth or pacing within accepted
scope using plan-decision. Propose substantial scope/workload changes and wait
for actual approval before applying them; accept scope changes through the map
workflow too. Use estimates only when timing constraints are supplied, disclose
workload mismatches, and record the learner's choice. Existing plan.md stays yours
to maintain; the generated decision log preserves the reasons across chats.

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

Inspect size and relevance using preflight, supply quality_review checks in new
lesson specs, and compare retained critical details against sources. Reduce
oversized/extraneous usable context through reduce-context with provenance,
omissions and limitations. Ordinary summaries/excerpts of usable sources are
authorized packet preparation; a new intake conversion still needs the explicit
approval above. Check the actual final packet including metadata overhead.
Inspect the issued folder in isolation using the portable evaluation cases in
the package; source integrity alone does not prove the lesson can be taught.

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
returned reports. Register new resources via the material-intake operation and ingest
reports first. Ask about ambiguous files rather than silently archiving unprocessed
uploads. Snapshots are recovery copies, not evidence that intake was completed.

Tell the learner: "Upload every visible file in the mailbox into a fresh chatbot
conversation and send Go. Optionally upload the same files into a second chat
and send Side chat. Return the main report and, if used, its separate side report." The chatbot teaches; you own curriculum and records.

## Optional side chat and UML

Read the active release's docs/user/side-chat.md for shared uploads, role selection,
the lightweight supplemental contract and evidence interpretation. New packets
embed both setups and the side report template in START-HERE.md. Send Go for the
lesson or Side chat in a second chat with the same files. Both favor useful UML
with code/prose and other visuals when clearer. The side chat answers questions
without advancing the lesson or certifying mastery. Direct help is allowed when
asked and its relationship/timing to assessed questions must be recorded.

Ingest both report types through the same command, preserving each separately.
Side reports can arrive before or after the main report and never close a pending
lesson or add formal assessments. Review remaining_questions and unmatched help;
matching pre-answer/unknown assistance qualifies independent evidence without
rewriting archived answers. Unscoped tangents do not expand the accepted map.
Show the current supplemental report records from state.json when planning.

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

Link supported formatting repairs to their original import ID with --repair-of
and --repair-note. Handle needs-review imports using objective-by-objective
relevance decisions. Preserve valid observations from unchanged context. Use
scoped review-evidence dispositions for individual invalid questions instead of
withdrawing useful unrelated work. Keep gaps objective-specific; resolve them
only through matching fresh unaided assessment evidence. Never reinterpret old
report-wide notes as if the chatbot had associated them with particular objectives.

Investigate suspected_errors against actual governing sources before correcting
content. Record confirmed corrective addenda, tell the learner the announcement,
and review every affected packet/evidence flag, including prerequisite dependents.
Retain original sources, reports and packet bytes. Resume only reviewed-safe
context; replace a pending packet with a new ID only on the learner's explicit
choice. Correction/relevance judgments are not new learner observations.

Inspect the updated evidence and next-step recommendations. Hinted, repeated,
invalid or unresolved contradictory assessments cannot establish independent mastery.
Uncertainty remains visible; use fresh assessments. If a grading/source dispute
invalidates a report, use dispute with the reason; original evidence is retained
and progress/reviews are recomputed. Revise plan.md, explain the result briefly,
and prepare the next agreed lesson/review. Only delayed independent review passes
establish retention. Prefer concise observable judgments to mastery percentages.

## Commit and push after every user interaction

Before the final response to EVERY user interaction that changes workspace files,
automatically commit and push the reviewed interaction scope, unless the learner
explicitly opts out with auto_backup=false. This includes planning, preference,
intake, supplemental-report and recovery work, not only lesson/report milestones.
Use the scoped backup helper below for a verified private remote; with no remote,
commit reviewed changes locally and explain that push remains unavailable. No
empty commit is needed when nothing changed. Retry pending task pushes without
repeating completed learning operations. Direct helper calls do not replace this
agent end-of-turn step.

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
