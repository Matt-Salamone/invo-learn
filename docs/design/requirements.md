# Requirements interview

Status: interview closed at the owner's request. The agreed requirements below define the build brief. Unanswered choices remain implementation decisions; recommendations from unanswered interview questions are not accepted requirements. See [the build prompt](build-prompt.md).

## Agreed behavior

- A planning agent (Codex, Cursor, or a local agent) manages lesson planning, bookkeeping, learner state, and future study decisions.
- A separate chatbot conducts lessons, questions, practice, and quizzes from an agent-produced prompt and context, then returns a report for the agent to ingest.
- Manual handoffs are sufficient. Encourage a fresh chatbot conversation for each lesson. Handoff automation is a possible future extension.
- Use one reusable mailbox folder for every lesson handoff, including handoffs containing only one self-contained packet. Setup asks for its location; default to `mailbox/` at the private workspace repository root. The learner may choose a location such as `Desktop/mailbox`.
- Before preparing a handoff, clear the mailbox and stage everything needed for the current lesson there. The agent selects packets, source excerpts, original files, or a combination according to relevance, context size, fidelity, and convenience. The learner uploads everything in the mailbox to a fresh chatbot conversation.
- The mailbox is temporary staging. Original materials and durable lesson records remain preserved elsewhere in the private workspace.
- Uploaded learning materials define learning scope. Supplemental research is an optional course-level preference; distinguish supplemental content from the supplied material.
- The chatbot may adapt explanations, exercise selection, sequence, and pacing within the assigned lesson objectives. The planning agent owns curriculum changes, durable progress records, and future planning.
- Begin with a brief check of existing understanding, then alternate short explanations, learner attempts, and feedback. Adapt the balance to preferences and performance.
- Track coverage separately from demonstrated understanding. Use independent answers or work appropriate to each objective, unfamiliar applications where useful, and later reviews to establish retention.
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
- Setup should create an independent private workspace and install a versioned copy of the public harness. Harness updates are explicit and preserve preferences and study records.
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
