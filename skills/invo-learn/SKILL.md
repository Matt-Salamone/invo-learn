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

Once per resumed study session, before preparing the next lesson/review, run
`python learn.py check-updates` to compare the installed version with the public
GitHub main branch. Save/ingest any pasted report FIRST. The check sends no learner
data and never installs code. If newer, briefly describe the available version
and link its changelog; use `../invo-learn-update/SKILL.md` only when the learner
requests the update. Otherwise continue studying on the installed version.
Do not repeat the same notice during the session. If unavailable/offline, mention
that once and continue; do not claim the package is current. Do not check during
individual teaching questions or make updating a prerequisite for study.

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
reuse. If the current lesson has no report, request it, or record an explicitly
requested abandonment; do not silently discard a pending session. restage safely
recovers an interrupted staging operation.

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
