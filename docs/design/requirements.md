# Requirements interview

Status: interview closed at the owner's request. The agreed requirements below define the build brief. Unanswered choices remain implementation decisions; recommendations from unanswered interview questions are not accepted requirements. See [the build prompt](build-prompt.md).

## Agreed behavior

- **Onboarding revision:** the learner uses one workspace, with a temporarily
  downloaded harness installed inside it; no public clone and second learner
  project are required. Setup explains unfamiliar preferences, asks one question
  per turn, and stops for an answer. Dedicated add-course and add-materials skills
  guide first and later uploads through the same mailbox used for lesson handoffs.
  These revisions supersede earlier bootstrap/distribution wording below where it
  implied a learner must manage two folders. Developer source and learner records
  still have separate purposes; no real records enter the public source repository.
- A planning agent (Codex, Cursor, or a local agent) manages lesson planning, bookkeeping, learner state, and future study decisions.
- A separate chatbot conducts lessons, questions, practice, and quizzes from an agent-produced prompt and context, then returns a report for the agent to ingest.
- Manual handoffs are sufficient. Encourage a fresh chatbot conversation for each lesson. Handoff automation is a possible future extension.
- Use one reusable mailbox folder for every lesson handoff, including handoffs containing only one self-contained packet. Setup asks for its location; default to `mailbox/` at the private workspace repository root. The learner may choose a location such as `Desktop/mailbox`.
- Before preparing a handoff, clear the mailbox and stage everything needed for the current lesson there. The agent selects packets, source excerpts, original files, or a combination according to relevance, context size, fidelity, and convenience. The learner uploads everything in the mailbox to a fresh chatbot conversation.
- The mailbox is temporary staging. Original materials and durable lesson records remain preserved elsewhere in the private workspace.
- Uploaded learning materials define learning scope. Supplemental research is an optional course-level preference; distinguish supplemental content from the supplied material.
- The chatbot may adapt explanations, exercise selection, sequence, and pacing within the assigned lesson objectives. The planning agent owns curriculum changes, durable progress records, and future planning.
- Begin with a brief check of existing understanding, then give longer, detailed, comprehensive explanations before practice, including conceptual mechanisms, causal reasoning, worked examples and useful visuals with readable static alternatives. Adapt the balance to preferences and performance.
- Use a flexible diagnose/model/attempt/targeted-response/independent-check/recall-and-transfer arc. Branch on reasoning and error type, fade assistance, and vary representation rather than repeating a fixed explanation/quiz sequence. Keep failed/guided attempts; allow fresh independent assessments to explicitly resolve earlier failures. Review success after teaching is relearning, not retention.
- Make liberal use of meaningful visuals in lessons, including interactive diagrams and charts when supported, with readable static alternatives and verbal explanations. Visual hints count as assistance during assessment.
- Teach self-contained lessons without directly mentioning source pages/files or requiring the learner to consult uploaded materials. Sources still ground accuracy and define scope; keep provenance in planning records and tutor context, supplying it separately on explicit learner request.
- Track coverage separately from demonstrated understanding. Use independent answers or work appropriate to each objective, unfamiliar applications where useful, and later reviews to establish retention.
- End every teaching-chatbot turn with a lesson progress bar based on meaningful completed checkpoints and a separate provisional mastery summary for assigned objectives. Mastery follows independent-performance and delayed-retention evidence, never turn counts or lesson completion. Adapt checkpoint totals transparently; keep final footers outside the report JSON and durable updates with the planning agent.
- The chatbot compiles one structured report that the learner can copy or download in a single step. Include objectives attempted, assessment questions and learner answers, hints or assistance, grading rationale, misconceptions, and recommended next steps.
- Keep report evidence proportional to the lesson; do not reproduce every explanation or conversational exchange. The learner should not need to reconstruct the conversation. Full transcripts are neither required nor routinely collected and are outside the initial scope.
- To return a lesson report, the learner only copies it from the chatbot and pastes it to the planning agent. The agent handles persistence, ingestion, record updates, and other bookkeeping without requiring additional learner involvement in the import workflow. Preserve the report durably before reusing the mailbox.
- If an objective is not demonstrated, recommend remediation and explain prerequisite gaps while allowing an explicit learner override. Keep unresolved gaps visible in the learning map.
- Match spaced reviews to the objective: recall for facts, explain-back for concepts, and fresh problems for skills. Record assistance and performance; heavily hinted answers do not establish independent retention.
- Accept uploaded material of any type. If material is not directly usable, ask the learner for permission to create an automatic workflow that transforms it into a workable form. Do not restrict intake to a fixed list of extensions.
- Brief prerequisite repair may happen within a lesson. For a large prerequisite gap, the chatbot should suggest pausing and returning to the planning agent to plan one or more prerequisite lessons.
- Include spaced repetition.
- One agent should be aware of all courses, skills, and learning paths to coordinate scheduling and priorities.
- Scheduling, time budgets, and deadlines are optional. Offer them during setup and when adding a track; if the learner does not supply or request them, the agent need not manage them. Let the agent handle the details rather than prescribing a scheduling algorithm in the skill.
- When scheduling is enabled, coordinate due reviews and current priorities across tracks, considering supplied deadlines and allowing learner overrides.
- Support college course study and non-school skills, initially for the owner and friends.
- Distribute the harness/skill package from the public project. Each learner's working repository is separate and private.
- A friend should be able to give their agent the public repository link and have the agent set up their learning environment.
- Use one private workspace per learner containing all learning tracks, with a shared learner profile and overview and separate track records.
- Setup should create an independent private workspace and install a versioned copy of the public harness. Harness updates default to automatic compatible trusted installation before lessons/reviews and preserve preferences and study records.
- During normal study, check GitHub before preparing the next lesson/review, after processing returned reports and their plans/private backups. Automatically install newer compatible trusted versions unless opted out; network failures must not block study or imply that the package is current.
- A dedicated setup skill should collect a few global defaults. New tracks inherit them, with relevant preferences briefly confirmed and per-track overrides supported.
- Aim to cover all uploaded material by default and generate an inspectable coverage map. The learner can adjust coverage and priorities; distinguish covered, deferred, and unassessed objectives.
- Additional uploads propose changes to the learning plan for learner review.

## Decisions left to the builder

- Exact workspace bootstrap/update mechanics and which preferences setup collects.
- Material transformation permissions/reuse, learning-map structure, and lesson packet/report contracts.
- Report validation/recovery without learner import chores, and grading disputes.
- Review scheduling policy and chatbot review sessions.
- Learner-state persistence, report ingestion/recovery, and cross-agent portability.
- Detailed first-version scope and acceptance criteria within the agreed end-to-end workflow.

The final interview questions about transformation-workflow reuse, external conversion services, initial placement assessment, and a specific review-interval policy were not answered. Choose practical defaults where needed, document the reasoning, and preserve the explicit requirement to ask permission before creating a transformation workflow. Do not resume a broad requirements interview.

## Research

See [the source-inspected survey](../research/agentic-tutoring-harnesses.md). Its recommendations remain proposals unless accepted in this interview.

## Authorized upgrade scope (0.5.0)

The owner requested implementation of all ten suggestions from the
[invo-assignment comparison](../research/invo-assignment-upgrade-comparison.md):
packet size/relevance/completeness checks and verified reduction; content-error
investigation/correction/impact review; selective evidence dispositions and stale
report relevance; objective-specific gaps; prefilled reports and linked repairs;
observable criteria and source-section accounting; actionable resume/health;
routine versus substantial plan/pacing decisions; installed-CLI journeys and
portable fresh-chat evaluations; and enclosing-repository setup isolation.
Keep the manual handoff, standard-library portability, private records, actual
consent for intake conversion, immutable originals/packets, and conservative
independence/delayed-retention semantics. Existing v1 state/reports remain readable.

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

## Independent course sessions (0.4.1)

Allow one pending handoff per course, rather than one per workspace. A pending
report in another course must not block new lessons/reviews or course-specific
study updates. Keep prepared status and immutable packets for every course.
The shared mailbox shows one packet at a time; guarded switching snapshots all
previous contents. Inspect and ingest reports actually returned before switching.
List pending IDs per course, restore any prepared packet by ID, and accept reports
in any course order. Require report ingestion or explicit abandonment only before
preparing another lesson in the same course. active_lesson remains the last staged
packet for backward compatibility, not a workspace-wide pending-session lock.
