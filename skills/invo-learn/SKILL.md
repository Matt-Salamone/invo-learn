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

Use add-track with a stable lowercase ID and title. Inherit global defaults;
briefly confirm relevant supplemental-research/remediation preferences, allowing
per-track overrides. Offer optional schedule/time budget/deadlines. If absent,
leave schedule null; spaced-review dates still work. Coordinate supplied
constraints and priorities across tracks; no calendar integration is required.

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
invalid or contradictory assessments cannot establish independent mastery.
Uncertainty remains visible; use fresh assessments. If a grading/source dispute
invalidates a report, use dispute with the reason; original evidence is retained
and progress/reviews are recomputed. Revise plan.md, explain the result briefly,
and prepare the next agreed lesson/review. Only delayed independent review passes
establish retention. Prefer concise observable judgments to mastery percentages.
