# Agentic tutoring harnesses: research for invo-learn

Research date: **2026-10-14**. Primary sources: live GitHub repository files, default-branch commit metadata, and the original project website. This is a design survey, not a security audit, deployment test, or learning-outcome evaluation. No surveyed project was installed or executed. A documented feature is distinguished below from source-inspected behavior. Commit dates describe the latest default-branch commit returned during this survey; they do not establish release quality or maintenance commitments.

## Main finding

“Learn Anything” refers to unrelated projects and to several generations of one older project. The most useful starting references for a personal tutor are **Nar101** for assessment integrity, **naeemdev360** for enforceable progression, and **ChenChenyaqi** for portability and a local learning workspace. **Nalu** is the strongest inspected example of a standalone application with a real bounded tool loop. These are architectural judgments from the inspected sources, not evidence that one tutor teaches better.

A useful working distinction: a tutoring harness observes an attempt, changes learner state, chooses a teaching action, checks evidence, and resumes across sessions. A resource graph, course generator, or document chatbot can supply ingredients without implementing that loop.

## Disambiguating the original Learn Anything lineage

### 1. Historical mind-map site: preserved in PlainRubbish/learn-anything

The historical README describes a React mind-map search interface backed by Elasticsearch 5.5.2, map/suggestion endpoints, and curated topic connections. This is a learning-resource navigator, with no adaptive learner-assessment loop evidenced by those sources. Its graph and prerequisite navigation are useful design references, but curated resources are not mastery evidence. Local setup is documented; its old dependencies would require fresh compatibility work. [README](https://github.com/PlainRubbish/learn-anything/blob/5961d373d6cadd8de0d3b954ae18284411de78e9/README.md)

MIT is present in an actual license file. The latest preserved commit inspected is **2017-09-24**, titled “MIT license”; this date belongs to this preserved repository, not every historical branch or the live site. [License](https://github.com/PlainRubbish/learn-anything/blob/5961d373d6cadd8de0d3b954ae18284411de78e9/LICENSE), [commit](https://github.com/PlainRubbish/learn-anything/commit/5961d373d6cadd8de0d3b954ae18284411de78e9)

### 2. Later knowledge platform: preserved in NotShaman/learn-anything.xyz

The later source snapshot contains a Solid website, Tauri desktop work, NativeScript mobile work, Grafbase GraphQL, and EdgeDB. Its README explicitly labels parts of setup and desktop work as incomplete. The schema records topics the user wants to learn/is learning/has learned, links, notes, and personal/global wikis. Those completion categories are useful persistent state, but they do not record assessed independent performance. Its separate AI aspirations should not be read as a verified autonomous teaching loop. [README](https://github.com/NotShaman/learn-anything.xyz/blob/91d8078ed8709a50b61499aa5fd32a894c0dac0a/readme.md), [schema](https://github.com/NotShaman/learn-anything.xyz/blob/91d8078ed8709a50b61499aa5fd32a894c0dac0a/grafbase/edgedb/dbschema/default.esdl)

Latest inspected snapshot commit: **2023-12-18**. No standalone license file was visible in its root listing; reuse permissions were not independently established. [Commit](https://github.com/NotShaman/learn-anything.xyz/commit/91d8078ed8709a50b61499aa5fd32a894c0dac0a)

**Current identity caveat:** on the research date, the official `learn-anything/learn-anything.xyz` URL redirects to **linsa-io/linsa**, whose public main branch contains a placeholder README, `.gitignore`, and `soon.ts`. The README says public development is postponed. Its sole current commit is **2026-01-17**. The live `learn-anything.xyz` page still exposes a topic-search input; the fetched page does not establish its deployed backend version. Do not equate preserved fork contents with current hosted behavior. [Current repository](https://github.com/linsa-io/linsa), [commit](https://github.com/linsa-io/linsa/commit/4df4f96f7271eadb4f708df396936c69be35218d), [website](https://learn-anything.xyz/)

### 3. Original lineage's AI/task services: linsa-io/tasks

The old `learn-anything/ai` URL currently redirects here. This is a collection of task services—Markdown RAG chat, similar questions, topic suggestions, crawling, and subtask generation—not a documented mastery tutor. The README acknowledges a mixture of complete and incomplete work. The Markdown-chat instructions use Python/Streamlit and Cloudflare Workers AI and themselves question that implementation. No longitudinal learner model or assessment gate was identified in the inspected documentation. Useful idea: expose retrieval and topic expansion as replaceable tools rather than making the knowledge graph the tutor. [README](https://github.com/linsa-io/tasks/blob/33cce426a06ff992164678828ff52ddecb66657b/readme.md), [Markdown chat](https://github.com/linsa-io/tasks/blob/33cce426a06ff992164678828ff52ddecb66657b/chat-with-markdown/readme.md)

MIT license file verified. Latest inspected default-branch commit: **2024-07-10**. [License](https://github.com/linsa-io/tasks/blob/33cce426a06ff992164678828ff52ddecb66657b/license), [commit](https://github.com/linsa-io/tasks/commit/33cce426a06ff992164678828ff52ddecb66657b)

## Modern tutor projects with similar names

### 4. ChenChenyaqi/learn-anything: portable tutor skills plus local dashboard

This is a TypeScript CLI that generates instructions/commands for many coding assistants, with six learning commands for topic setup, explanation, practice, quiz, review, and status. The existing assistant supplies the model and tools; this project is not an independent inference service. Its bundled Vue dashboard reads local `.learn/topics/<topic>/` data, including JSON state, session notes, exercises, and quizzes. Optional Context7 integration supplies documentation verification. The adapter design is a practical portability reference; support for many clients is a repository claim, not independently tested here. [README](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/README.md)

Source inspected: state has concept status, confidence, practice/explanation counts, and timestamps. Review prioritizes confidence, recency, and status through a prompt-specified formula; it is not an SM-2 scheduler. Practice creates starter files, reviews learner code, and optionally runs it. Consequently, its TDD branding does not imply mandatory executable tests. It suggests prerequisite work rather than using a hard progression gate in the inspected workflow. [Schema](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/learn-protocol/schema.ts), [review](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/templates/workflows/learn-review.ts), [practice](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/templates/workflows/learn-practice.ts)

MIT. Latest inspected default-branch commit: **2026-08-20**. Extend templates, client adapters, and state helpers; model portability inherits the host assistant's capabilities. [Commit](https://github.com/ChenChenyaqi/learn-anything/commit/83b33cb6f897c3ee26b341abee800976dfa34b66)

### 5. Nar101/learn-anything: source-grounded, evidence-aware tutoring protocol

An Agent Skill for compatible assistants rather than a standalone app. It teaches one current lesson segment at a time, adapts provisional future lessons, and supports either provided material or agent-researched sources. It separates source claims, tutor synthesis, and application assumptions. Local YAML/Markdown course packages preserve learner state, sources, reviews, assessment files, user notes, and tutor summaries. [README](https://github.com/Nar101/learn-anything/blob/632817b900ea271bae9440096176a61c2e9d371b/README.md)

The skill explicitly freezes answers/rubrics before asking, distinguishes exposure, guided performance, independence, transfer, and delayed retention, limits what hinted answers can prove, and withdraws invalid assessments. It separates content progress from mastery. Source manifests map claims to evidence; resume loads current state and due reviews rather than full history. Deterministic parsing/validation precedes model work, with narrowly scoped research delegation and final judgments retained by the tutor. These are **protocol instructions**, so compliance still depends on the host agent. [Skill](https://github.com/Nar101/learn-anything/blob/632817b900ea271bae9440096176a61c2e9d371b/SKILL.md)

Its Python validator checks package structure, status values, source policy, assessment preflight/freeze fields, and other invariants. That can detect recorded inconsistencies; it cannot establish the truth of sources or independently verify that a learner worked unaided. MIT. Latest inspected commit: **2026-08-02**. Extensibility lies in templates, rubrics, reference protocols, and validator; model/tool support comes from the host. [Validator](https://github.com/Nar101/learn-anything/blob/632817b900ea271bae9440096176a61c2e9d371b/scripts/validate_course.py), [commit](https://github.com/Nar101/learn-anything/commit/632817b900ea271bae9440096176a61c2e9d371b)

### 6. naeemdev360/learn-anything-skill: executable progression and review gates

A host-agent skill plus a local Python course state machine and HTML progress dashboard. It plans a project-centered course, generates lessons just in time, and uses quiz, closed-book explain-back, assignment, module tests, placement tests, and a final project. Answer keys live separately in `.grading/`. Its documented lesson pass requires every component to meet the threshold, rather than averaging away a weak component. [Skill](https://github.com/naeemdev360/learn-anything-skill/blob/78a0d412f981a591628efa1a7c66fb6439b1d894/SKILL.md)

Inspected Python enforces ordered unlocking and weakest-component passing, persists JSON and an event log, schedules expanding reviews, and blocks starting new work when the review backlog reaches its threshold. Explicit learner overrides are logged. This is stronger progression enforcement than prompt instructions alone, but the tutor supplies the numerical grades; the script does not assess actual work independently. Source fidelity is less explicitly specified than Nar's manifest/preflight protocol. Local files are portable and inspectable; hidden grading folders are not a security boundary against their owner. [Runtime](https://github.com/naeemdev360/learn-anything-skill/blob/78a0d412f981a591628efa1a7c66fb6439b1d894/scripts/course.py)

MIT license file verified. Latest inspected commit: **2026-08-25**, adding engagement and more answerable assessments while retaining the gate. Extend references/templates and Python policy; model portability inherits the agent host. [License](https://github.com/naeemdev360/learn-anything-skill/blob/78a0d412f981a591628efa1a7c66fb6439b1d894/LICENSE), [commit](https://github.com/naeemdev360/learn-anything-skill/commit/78a0d412f981a591628efa1a7c66fb6439b1d894)

### 7. chenly255/2sigma: document-centered adaptive mastery skill

Generates numbered Markdown lessons, then adapts the next lesson from holistic evaluation of the learner's answers. Six modes cover papers, concepts, domains, technology stacks, repositories, and exam review. A profile and knowledge tree persist alongside the course. Application questions and optional challenge questions test more than repetition. An optional Marker/uv script splits PDFs; new modes are added through reference instructions. [README](https://github.com/chenly255/2sigma/blob/6b505c20d8c1afee676dd9c922766b57503d5881/README.md)

Its core skill routes long explanations to files and uses chat for brief coordination. Progress is Markdown checkboxes and host-agent judgment, with no deterministic mastery gate or spaced-review scheduler in the inspected core skill. That makes it simpler, but a poor fit if fluent live conversation is the primary interface. Tools and inference come from the host. The README declares MIT, but no standalone license file appeared in the inspected root listing. Latest inspected commit: **2026-03-26**. Its “10x faster” wording is marketing, not a measured result established by this survey. [Skill](https://github.com/chenly255/2sigma/blob/6b505c20d8c1afee676dd9c922766b57503d5881/SKILL.md), [commit](https://github.com/chenly255/2sigma/commit/6b505c20d8c1afee676dd9c922766b57503d5881)

## Standalone runtime comparisons

### 8. olliegilbey/nalu: bounded agent loop with deterministic application state

A Next.js/TypeScript web application using tRPC, Supabase/PostgreSQL, and an OpenAI-compatible provider abstraction. Its documented flow scopes a topic, assesses the starting point, teaches conversationally, and schedules review; it describes itself as an early solo MVP. Running the frontend locally still requires database/provider configuration in the documented setup. [README](https://github.com/olliegilbey/nalu/blob/84405b62128259b44b650deeccabf4a97693705d/README.md)

Inspected code builds a fresh `ToolLoopAgent` per turn attempt with a hard step bound, read-only learner-history lookups, and staged teaching/assessment emissions. The agent does not own XP or stage transitions; deterministic application code owns those. Questionnaire validation requires concept names, keys/rubrics, and unique question IDs. Its SM-2 function deterministically schedules reviews from a validated 0–5 quality score; that score still originates in evaluation. Per-step token accounting, retries, and telemetry make it a useful runtime/cost reference. [Agent](https://github.com/olliegilbey/nalu/blob/84405b62128259b44b650deeccabf4a97693705d/src/lib/agents/waveMidTurnAgent.ts), [tools](https://github.com/olliegilbey/nalu/blob/84405b62128259b44b650deeccabf4a97693705d/src/lib/course/waveTurnTools.ts), [SM-2](https://github.com/olliegilbey/nalu/blob/84405b62128259b44b650deeccabf4a97693705d/src/lib/spaced-repetition/sm2.ts)

Provider URL/model/key are configurable, but the inspected adapter assumes structured outputs, streaming usage, and provider-specific preparation, so endpoint compatibility does not prove every local model works. No license file was visible in the root, and README's licence section is blank: study the architecture, but do not assume permission to copy code. Latest inspected commit: **2026-10-14**, removing an unnecessary review lookup. [Provider](https://github.com/olliegilbey/nalu/blob/84405b62128259b44b650deeccabf4a97693705d/src/lib/llm/provider.ts), [commit](https://github.com/olliegilbey/nalu/commit/84405b62128259b44b650deeccabf4a97693705d)

### 9. mousam100/Montessori-Agentic-AI-Tutor: auditable classroom prototype

BLUE V5 is a Streamlit student/teacher prototype with learner profiles, JSON memory, homework, safety triage, and teacher alerts. The orchestrator selects teaching actions, retrieves memory/PDF/web context, calls Anthropic, and updates state. It is useful if the product includes teacher oversight; those capabilities are extra scope for a personal adult tutor. MIT license verified. Latest inspected commit: **2026-05-20**. [README](https://github.com/mousam100/Montessori-Agentic-AI-Tutor), [orchestrator](https://github.com/mousam100/Montessori-Agentic-AI-Tutor/blob/8c3314f97b3159a8af9e4921a925047285c83e46/core/orchestrator.py), [license](https://github.com/mousam100/Montessori-Agentic-AI-Tutor/blob/8c3314f97b3159a8af9e4921a925047285c83e46/LICENSE), [commit](https://github.com/mousam100/Montessori-Agentic-AI-Tutor/commit/8c3314f97b3159a8af9e4921a925047285c83e46)

**Important source-level limitation:** reflection increases mastery for phrases like “got it” and for neutral turns. It therefore measures a conversational heuristic, not demonstrated mastery. This directly contrasts with Nar's evidence model. The implementation is an instructive warning against treating a numeric field named mastery as proof of learning. Provider portability would require changing the service layer; local UI hosting does not mean offline inference. [Reflection](https://github.com/mousam100/Montessori-Agentic-AI-Tutor/blob/8c3314f97b3159a8af9e4921a925047285c83e46/core/reflection.py), [state](https://github.com/mousam100/Montessori-Agentic-AI-Tutor/blob/8c3314f97b3159a8af9e4921a925047285c83e46/core/state.py)

### 10. Moniaar/Ufuq: useful proposed architecture, insufficient implementation

The README describes offline-first MCP agents for tutoring, translation, quizzes, RAG, and syncing, with SQLite/Chroma, local Hugging Face models, and optional cloud inference. However, the inspected default-branch root contains **only README.md and requirements.txt**. Files needed by its own startup instructions—`app.py`, `download_models.py`, and `mcp_runtime.py`—are absent. Treat this as a documented blueprint, not a runnable tutor reference. No implementation of memory, gating, retrieval, or model fallback was verified. The README declares MIT, but there is no separate license file in that listing. Latest inspected commit: **2026-09-22**. [Repository and file listing](https://github.com/Moniaar/Ufuq), [commit](https://github.com/Moniaar/Ufuq/commit/cb93ed0c390665ef793059b45befb18475d4ed60)

## Design recommendations for discussion, not accepted requirements

1. **Choose the delivery surface first.** A skill running in an existing assistant makes a personal prototype cheap and portable; a standalone application gives direct control of UI, identity, tools, budgets, and state transitions. A library with a skill adapter can preserve both options, but building both interfaces initially adds work.
2. **Separate tutor judgment from state authority.** Let the model propose teaching actions and grades; validate transitions and persist evidence in ordinary code. Combine Nar's evidence distinctions with naeemdev360/Nalu-style deterministic gates rather than letting a prompt rewrite mastery freely.
3. **Define success as observable independent performance.** Record task, rubric version, answer, hint level, attempts, transfer, and delayed recall separately. A pass percentage, positive sentiment, or completed lesson is insufficient on its own.
4. **Make source provenance and invalidation first-class.** Preserve links/page locations and distinguish source claims from tutor synthesis. Freeze grading criteria, allow an ungradable outcome, and withdraw evidence when a bad question or source error is found.
5. **Generate a revisable route, then only the next useful lesson.** Keep enough of the map for orientation without pre-generating a full course that ignores subsequent learner feedback.
6. **Prefer one accountable tutor with bounded tool use initially.** Multiple agents are useful when a concrete research/verification role earns its additional latency and cost. A collection of named agents alone does not establish a better teaching loop.
7. **Keep personal learner data out of the public project by default.** Distinguish distributable engine/examples from private attempts, notes, source materials, credentials, and learner state. This is a proposed product boundary, not a conclusion about the requested repository's present contents.
8. **Test the learning contract and grader, not just the UI.** Example acceptance cases: hinted success does not become independent evidence; an invalid question withdraws its grade; resume does not lose misconceptions; overdue review follows the chosen policy; tool budget exhaustion preserves state. Meaningful outcome checks should include fresh tasks and delayed retention, not stars or marketing claims.

## Foundational interview decisions

Start with a real learning scenario and one observable finish line. Then resolve these dependencies one at a time:

- Who is the first learner: the owner alone, adult peers, or students with teachers? Which concrete domain should the first version prove?
- What should the learner independently produce at the end: working code, an explanation, decisions in unfamiliar cases, exam answers, or another artifact?
- Where will sessions happen: this assistant, a CLI, a browser app, voice, or a combination? Is standalone hosting essential?
- What may the tutor do autonomously: browse, read PDFs, execute code, create exercises, choose the next topic, schedule review, or modify the learner's project?
- Should it primarily teach a user's chosen source, research current sources, or do both with explicit boundaries?
- Should advancement be strictly gated, recommendatory, or freely overrideable? Does overdue review block new learning?
- What evidence warrants mastery, and how should hints, repeated questions, and disagreements with grading affect that evidence?
- Must memory survive model/provider changes? Should persistence start as local files, SQLite, or a service database?
- Are local models/offline operation requirements, or is provider portability enough? What are tolerable latency and session cost?
- Which capabilities are explicitly outside the first version: multi-user collaboration, teacher dashboards, gamification, knowledge sharing, notifications, voice, or generated visuals?

The highest-value initial tradeoff is between **a personal agent skill with rigorous durable state** and **an independent tutoring runtime**. The findings support either; the user's intended experience must decide.
