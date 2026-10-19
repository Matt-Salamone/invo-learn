# Build prompt: invo-learn

Onboarding revision: see the first bullet in requirements.md. Learners now open
one learning folder, receive explained questions one at a time with a wait for
each answer, and use the same mailbox for incoming resources and outgoing lessons.
The dedicated course/material skills cover initial and additional uploads. Earlier
references to separate repositories concern public development versus learner data,
not a requirement for learners to clone and manage a second project.

You are taking over implementation of invo-learn, an agentic teaching and tutoring harness. Build a working first version in https://github.com/Matt-Salamone/invo-learn. Use the current checkout if available; otherwise obtain the repository and follow its instructions. The requirements interview is finished. Read `docs/design/requirements.md` and `docs/research/agentic-tutoring-harnesses.md`, then implement rather than starting another broad interview. This brief requires no access to the original conversation.

## Product and division of responsibility

This is a hybrid system. A planning agent such as Codex, Cursor, or a local agent owns planning, bookkeeping, durable learner state, curriculum changes, and future study decisions. A separate chatbot such as ChatGPT teaches from an agent-prepared prompt and context. The learner manually uploads the handoff into a fresh chatbot conversation, completes the lesson, copies one chatbot-generated report, and pastes it to the planning agent. Automated chatbot integration is outside the initial scope.

The chatbot may adapt explanations, exercises, sequence, and pacing within assigned objectives. Begin with a brief understanding check, then give longer, detailed, comprehensive explanations before practice, including conceptual mechanisms, causal reasoning, worked examples and useful visuals with readable static alternatives, adapting to learner preferences and performance. Small prerequisite repairs may happen within a lesson. Large gaps should trigger a suggestion to pause and return to the planning agent for one or more prerequisite lessons. Advancement is advisory: recommend remediation and explain gaps, allow explicit learner overrides, and retain unresolved gaps in the learning map.

Make liberal use of meaningful visuals in lessons, including interactive diagrams,
charts or simulations when supported and useful, with readable static alternatives
and verbal explanations. Teach self-contained explanations and questions without
source/page/file commentary or requiring learners to consult uploads. Materials
still ground accuracy and define scope; retain provenance in planning records and
tutor context, supplying it separately on explicit request. Visual hints are
assistance and must not leak solutions into independent assessments.

Use a flexible diagnose/model/attempt/targeted-response/independent-check/recall-and-transfer
arc, branching on reasoning and error type rather than enforcing a fixed quiz
sequence. Fade support after guided work and keep prior failures; fresh independent
assessment may explicitly resolve them. Success after review teaching is relearning,
not retention. During normal study, check GitHub before each
new handoff, after processing reports and their plans/private backups. Automatically install newer compatible trusted versions unless opted out;
offline checks leave study available and update status unknown.

End every teaching-chatbot turn with a compact progress bar for completed lesson
checkpoints and a separate provisional mastery summary for the assigned objectives.
Adapt checkpoint totals with explanation, count learner work only after evaluation,
and leave interrupted lessons incomplete. Mastery labels follow the evidence rules
for guided work, independent assessment and delayed retention; completing the
session does not imply mastery. Keep the final footer outside the report JSON.

## Public package and private workspace

The public repository distributes the harness/skills, reusable supporting tools, templates, documentation, and synthetic examples. Each learner has an independent private working repository containing all their courses, skills, and paths. Do not use a public fork as the private repository or put real learner data into the public package.

Provide a dedicated setup skill and a clear README entrypoint so a friend can give their agent the public repository URL and have it perform setup. Setup should create an independent private workspace, install a versioned copy of the harness, collect a few global preferences, and establish a shared learner profile/overview with separate track records. New tracks inherit defaults, briefly confirm relevant preferences, and permit overrides. Supplemental research and remedial preferences are examples. Support a local private workspace without requiring a hosted GitHub remote; create a private remote when requested and authorized. Harness updates default to automatic compatible trusted installation before lessons/reviews and preserve learner preferences and study records.

Let the agent know about all active tracks so it can coordinate priorities. Scheduling, time budgets, and deadlines are optional. Setup and course intake may ask, “Do you want to create a schedule, time budget, or add deadlines?” If the learner does not request or supply these, no calendar or time-budget management is required. When enabled, let the agent handle details rather than prescribing an elaborate scheduling algorithm in the skill.

## Material intake and coverage

Uploaded material defines the learning scope. Aim to cover everything in it by default and generate an inspectable coverage map linked to sources. Let the learner adjust the map and plan. Distinguish covered, deferred, and unassessed objectives; track coverage separately from demonstrated understanding and retention. New uploads should propose plan changes for review.

Accept materials of any type rather than rejecting unknown extensions. If material is not directly usable, the agent must ask permission to create an automatic workflow to transform it into something workable. Preserve the originals and distinguish derived artifacts. Do not promise every input can be interpreted without appropriate tools. Supplemental research is a course-level option; label supplemental content separately and keep uploaded material authoritative for scope.

## Reusable mailbox handoff

Use one mailbox folder for every handoff, even a single self-contained packet. Setup lets the learner choose its location, defaulting to `mailbox/` at the private repository root; an external location such as `Desktop/mailbox` is allowed.

Before preparing a handoff, clear the mailbox and put everything needed for the current lesson there. The agent chooses a packet, excerpts, original files, or a combination according to relevance, context size, fidelity, and convenience. Include usable teaching instructions and relevant learner context. The learner uploads everything in the mailbox into a fresh chatbot conversation.

The mailbox is temporary staging. Preserve original materials and durable lesson artifacts elsewhere. Constrain clearing to the configured, dedicated mailbox; reject configurations that could clear the workspace, source/archive folders, or unrelated directories. Preserve any returned report durably before reusing the mailbox.

## Report and record updates

The chatbot compiles one structured report that can be copied or downloaded in a single step. Require objectives attempted, assessment questions and learner answers, hints/assistance, grading rationale, misconceptions, and recommended next steps. Include enough evidence to assess progress, proportional to the lesson. Do not require the learner to reconstruct the conversation or collect the full transcript.

The learner only copies the report and pastes it to the planning agent. The agent handles persistence, parsing, record updates, and subsequent planning without additional import chores. Choose a practical report contract and validation approach. Do not invent missing evidence or silently treat contradictory evidence as mastery; handle uncertainties in the records and subsequent planning. Prevent duplicate imports from duplicating progress or review updates.

Use independent answers/work appropriate to each objective, unfamiliar applications where useful, and later reviews to establish retention. Heavily hinted answers do not demonstrate independent understanding or retention. Preserve enough evidence to revisit a judgment.

## Spaced repetition

Include durable review state across all tracks. Match reviews to the objective: recall for facts, explain-back for concepts, and fresh application problems for skills. Record performance and assistance, and use review outcomes to update future review needs. Use the same mailbox/chatbot/report cycle for review sessions where appropriate.

The owner did not select a review algorithm. Choose a simple, inspectable, adjustable policy that actually supports repeated review over time. Distinguish spaced-review due dates from optional calendar/time-budget planning. Do not add arbitrary hard locks on new learning.

## Implementation discretion and delivery

Keep the package focused and portable across agent hosts. Use skills for orchestration and executable helpers where deterministic behavior materially improves reliability, especially state persistence, validation, mailbox handling, and updates. Choose the stack and storage format; keep learner records inspectable and avoid an unnecessary server, dashboard, or proprietary model dependency. Do not build a standalone teaching chatbot as a replacement for the agreed manual hybrid workflow.

Unanswered decisions include transformation-workflow reuse, external conversion services, optional initial placement assessment, and precise review intervals. They are not agreed requirements. Resolve implementation details with practical documented defaults; request user decisions only when an actual permission requirement or essential blocker arises. In particular, preserve the required transformation-workflow approval.

Deliver a coherent end-to-end implementation, not only a plan or placeholder skills. Include install/setup guidance, concise usable skills, packet/report contracts, durable workspace conventions, explicit upgrade behavior, and a synthetic worked example. Respect source-project licenses if reusing implementation assets.

Validate meaningful behavior with tests and an end-to-end synthetic exercise: bootstrap a private workspace, add materials for at least two tracks, build a coverage map, stage a lesson, ingest a representative pasted report, update evidence and review state, and prepare a subsequent lesson/review. Verify that mailbox reuse preserves originals and durable artifacts; malformed/duplicate reports do not fabricate or duplicate learning evidence; hinted responses do not become independent mastery; and upgrades preserve learner records. Do not require a real paid chatbot session to exercise these contracts.

When done, report what was built, how to use it, what was tested, and material limitations. Keep the public project free of real learner materials, credentials, and private study records.

## Workflow revision (0.4.0)

The default agent workflow saves/ingests reports and updates plans, then automatically
commits/pushes completed work to a verified bound private learner remote. After a
handoff or regeneration, do the same. Scope commits to related reviewed files only,
preserve exact originals/reports/archives/checksums, never push learner data to the
public harness, create remotes/change visibility silently, force-push or claim an
unverified push. No suitable remote or backup failure leaves successful work local.
Duplicates with no changes create no empty commit. auto_backup=false opts out.

Before each lesson/review, automatically install the latest compatible trusted
candidate using existing compatibility/customization checks, backups and recovery.
Save/ingest reports before updates. Unavailable/incompatible/safely failed updates
allow installed-version study when safe, with an accurate status. auto_update=false
opts out. Existing installations receive this after one authorized upgrade; missing
workflow keys inherit true while every explicit stored choice survives. Preserve
legacy teaching styles whose choice provenance is unknown. Regenerated packets use
new active instructions; old archives remain immutable. Detailed default teaching
still skips demonstrated knowledge, asks one manageable question, gives specific
feedback, fades help and uses fresh independent assessments. Completion remains
separate from understanding and delayed retention.
