# Teaching-cycle comparison

Research date: **2026-10-15**. Baseline: invo-learn **0.2.1**, as inspected before
the teaching-presentation changes for **0.2.2**. This is a source and protocol
comparison, not a trial of the tutors or a measured learning-outcome comparison.
Implementation follow-up: **0.3.0** adopts the flexible arc and branching policy
below. Optional ordered attempt annotations and explicit failure-resolution links
address the same-report failure limitation while preserving legacy semantics.
See the [current contract](../user/contracts.md#ordered-attempts) for exact rules.
The earlier [harness survey](agentic-tutoring-harnesses.md) provides architecture
and implementation context. This follow-up re-read available first-party skill
pages and an official learning-science practice guide. Some revision-specific
URLs were unavailable; those comparisons cite readable default-branch pages and
do not claim that a new commit or deployed behavior was verified.

## Finding

Our evidence and record-handling rules are more explicit than our teaching rules.
The baseline does **not** prescribe a fixed `concept → example → quiz → concept`
sequence. It asks the chatbot to check understanding, alternate short explanations,
attempts, and feedback, and adapt. That gives the chatbot considerable discretion
over when to demonstrate, probe, give hints, vary a representation, retry, or move
on. A repetitive concept/quiz pattern is therefore compatible with the baseline
instructions even when it is a poor lesson. This is an inference from the
[handoff template](../../invo_learn/templates/chatbot.md) and
[planning skill](../../skills/invo-learn/SKILL.md), not a diagnosis of a private
lesson transcript.

The most useful improvement is an explicit **decision policy after each learner
attempt**, with frequent purposeful visuals and self-contained explanations.
Adding more quizzes alone would leave that gap in place. The presentation rules
were the authorized 0.2.2 change; the broader decision policy was subsequently
accepted and implemented in 0.3.0.

## What invo-learn did at the 0.2.1 baseline

The outer cycle is:

1. The planning agent reads durable evidence, prerequisites, preferences, and due
   reviews; selects objectives from an accepted source-linked coverage map; and
   prepares a packet.
2. The learner uploads the packet to a fresh teaching conversation.
3. The teaching chatbot checks starting understanding, teaches and assesses within
   assigned objectives, and returns one structured report.
4. The planning agent imports that report, updates evidence and reviews, revises
   the plan, and prepares the next lesson or review.

The chatbot can change explanations, exercises, order, and pacing inside the
assigned objectives. Small prerequisite repairs fit inside the lesson; large gaps
prompt a recommendation to return to the planning agent. Advancement is advisory,
explicit overrides are recorded, and a review backlog does not lock new work.
These boundaries come from the [requirements](../design/requirements.md),
[planning skill](../../skills/invo-learn/SKILL.md), and
[packet preparation](../../invo_learn/engine.py).

Inside the lesson, the 0.2.1 instructions require:

- A brief understanding check, then short explanations, learner attempts, and
  specific feedback, with one manageable question at a time.
- Recall for facts, explain-back for concepts, and fresh application for skills;
  unfamiliar applications where useful.
- Choosing a question and rubric before the learner attempts it; recording actual
  work, assistance, rubric, rationale, and outcome.
- Keeping failed and assisted attempts. Any hint or revealed solution makes that
  attempt guided rather than independent. Repeated answers are not fresh evidence.
- Treating ambiguous or invalid questions as ungradable, reporting skipped
  objectives as unassessed, and avoiding invented learner evidence.
- A single final JSON report rather than requiring a learner-created summary or
  full transcript.

These are [chatbot instructions](../../invo_learn/templates/chatbot.md), not a
runtime controller of the remote conversation. The Python code cannot observe
whether the tutor actually waited, froze a rubric before asking, used a diagram,
or accurately recorded the conversation.

What Python does enforce is consequential: the
[report validator](../../invo_learn/contracts.py) checks structure, IDs, dates,
allowed values, and coverage of assigned objectives. Its qualifying-evidence
predicate requires a valid, fresh, unaided, independent pass with a nonempty answer
and the appropriate assessment kind. The
[state projection](../../invo_learn/engine.py) requires covered status and a
demonstrated tutor judgment as well. It separates coverage, understanding, and
retention; only a successful delayed review can establish retention. Review
intervals default to **1, 3, 7, 14, 30, 60 days**, are adjustable, and do not advance
because of an early review. The model still supplies the truth of the reported
answers, grades, freshness, and assistance.

One limitation matters when designing a more adaptive lesson: **any valid failed
assessment for an objective in the same report prevents that report from
establishing demonstrated understanding**, even if a later fresh independent
assessment passes. The runtime records the conflict and requests fresh
reassessment. This is conservative, but it does not distinguish an early
diagnostic failure from unresolved failure after remediation. Do not hide the
earlier failure to get a pass. A future change would need an explicit ordered
diagnostic/practice/assessment model and a defensible rule for resolved errors.

## What the closest alternatives do

### Nar101: explicit segment progression and repair

Nar's skill describes a larger segment cycle: orientation and purpose, an
explanation, learner output, rubric feedback or retry, a segment gate, then the
next segment. Lesson closure adds unaided recall and a changed transfer task
before moving on. Reviews retrieve before showing old answers. It separates
exposure, guided performance, independent performance, transfer, and durability.
These are host-agent instructions rather than automatic proof that the teaching
occurred. Its default long-form segments and strict prerequisite progression
would change our desired conversational/advisory experience if copied wholesale.
[Core skill](https://raw.githubusercontent.com/Nar101/learn-anything/632817b900ea271bae9440096176a61c2e9d371b/SKILL.md).

Its feedback reference specifies finding the first consequential error, explaining
why it matters, supplying the smallest useful correction, and eliciting another
attempt. A six-level help ladder runs from self-check to complete demonstration;
after a demonstration, the learner compares the error and tries a variation.
Repeated failure triggers checks of prerequisites, task size, abstraction, and
misconceptions. This is a useful source for making our word “adapt” operational.
[Feedback strategies](https://github.com/Nar101/learn-anything/blob/main/references/feedback-strategies.md).

### naeemdev360: active conversation plus multiple demonstrations

Its teaching loop generates a lesson, traced worked examples, a quiz, an
explain-back, and an assignment. Conversation includes prediction before
explanation, several exchanges per concept, contextual callbacks, and smaller
steps or additional examples when needed. Quiz questions arrive individually;
struggling with core questions triggers targeted reteaching and fresh questions.
The learner must pass every component, with module tests and a final project
beyond individual lessons. The skill calls a Python gate for progression and
review backlog limits, while the tutor supplies grades. Unlike our strict
independence rule, its first two hint levels do not reduce quiz scores. Borrow
its concrete teaching actions and multiple forms of output, while preserving our
distinction between guided success and independent evidence. Its enforced backlog
locks conflict with our agreed advisory policy.
[Teaching loop and review rules](https://github.com/naeemdev360/learn-anything-skill/blob/main/SKILL.md).

### ChenChenyaqi: explanation and practice as separate modes

The explanation workflow goes from map position to precise mechanism, bounded
analogy, complete code example, misconceptions, and Socratic checks; the learner
then chooses a deeper direction or practice. It explicitly provides an answer
when the learner is unsure and says its questions guide discovery rather than
test knowledge. That makes it a useful explanation mode, but those exchanges
cannot automatically count as independent assessment in our system. Its saved
session is designed to be readable without the chat. We can borrow the coherent
mechanism/example/limits structure while keeping teaching assistance separate
from an unaided check.
[Explanation workflow](https://github.com/ChenChenyaqi/learn-anything/blob/main/packages/cli/src/core/templates/workflows/learn-explain.ts).

### 2sigma: a document-to-document loop

The core skill writes a lesson file with a plain-language explanation followed
by rephrasing, novel application, and optional challenge questions. Before writing
the next file, the tutor evaluates overall comprehension and either advances or
reinforces from a different angle. This provides an explicit decision between
advance and repair, but a coarser feedback rhythm than our conversational handoff:
long explanations belong in files and chat explanations are limited. Its core
does not specify our deterministic evidence qualification or delayed-retention
projection. Borrow novel application and alternate-angle reteaching, without
adopting a file-first teaching interface.
[Core workflow](https://github.com/chenly255/2sigma/blob/main/SKILL.md).

### Nalu and the other surveyed projects

Nalu's documented learner cycle is topic selection, scope clarification, baseline
assessment, adaptive conversation, and spaced review. Its application can control
conversation stages directly, whereas our remote chatbot is governed by a packet.
The earlier survey inspected its bounded tool loop and deterministic state
authority; this follow-up could read the README but could not re-fetch those
runtime files. That prior finding is architectural context rather than a newly
verified micro-teaching policy.
[Nalu README](https://github.com/olliegilbey/nalu),
[prior source inspection](agentic-tutoring-harnesses.md#8-olliegilbeynalu-bounded-agent-loop-with-deterministic-application-state).

The older Learn Anything knowledge maps and task services are weaker comparators
for lesson sequencing: the earlier survey did not identify an evidence-driven
teaching loop. Ufuq lacked the implementation needed to verify its proposed tutor.
Montessori BLUE supplies an action-oriented prototype, but its inspected mastery
heuristic could increase on conversational acknowledgments; we should retain
actual performance evidence rather than copy that signal. These are the
[prior survey's scoped findings](agentic-tutoring-harnesses.md), not new execution
or deployment tests.

## Recommended teaching policy, implemented in 0.3.0

A useful default arc is **diagnose → build a model with a visual and example →
learner attempt → diagnose the attempt → targeted next action → fresh independent
check → recall and transfer closure**. It should branch instead of demanding
every phase for every objective. A knowledgeable learner can start with a fresh
application; a novice may need demonstration before attempting a whole problem.
This is a design recommendation synthesized from the comparisons, not a proven
optimal universal sequence.

After each attempt, use an explicit next-action rule:

- Correct with sound reasoning: reduce support or vary the context; advance when
  there is adequate evidence, rather than repeating the explanation automatically.
- Correct result with weak reasoning: ask for the mechanism, a prediction, or a
  boundary case; do not treat a lucky answer as understanding.
- Local execution error: identify the first consequential mistake and request a
  focused correction, rather than restarting the whole concept.
- Conceptual error: change representation, use a counterexample or worked example,
  then request a fresh attempt.
- Assisted success: record it as guided, fade help, and try a distinct unaided task.
- Repeated difficulty: shrink the task, inspect a prerequisite, or recommend a
  pause according to the size of the gap.

Keep a predictable lesson purpose, but avoid turning the arc into mandatory
headings or a quiz after every paragraph. During a review, ask for retrieval
before supplying a recap. At closure, have the learner reconstruct the key idea
and apply it in a changed setting. These are teaching recommendations; resolving
the same-report failure limitation requires a separate contract/runtime design.

There is independent support for several ingredients. The US Institute of
Education Sciences recommends alternating worked examples and problem solving,
combining graphics with words, relating concrete and abstract representations,
spaced study, retrieval quizzes, and explanatory questions. Its guide also
recommends reducing worked examples as expertise increases. It rates evidence
for worked examples and graphics as moderate, and explanatory questions and
quiz re-exposure as strong. These ratings concern those practices, not any
surveyed AI harness, and do not establish that interactivity always outperforms
a clear static diagram.
[IES practice guide](https://ies.ed.gov/ncee/wwc/PracticeGuide/1),
[full guide](https://ies.ed.gov/ncee/WWC/Docs/PracticeGuide/20072004.pdf).

## The two authorized presentation rules for 0.2.2

**Use visuals liberally.** Diagrams, charts, annotated examples, timelines, and
other representations should appear frequently where they explain relationships,
processes, or change. Interactive visuals are particularly useful when the learner
can predict, manipulate a variable, and explain the outcome. Use them when the
teaching host supports them; supply a clear static fallback otherwise. Visuals
should carry explanatory work, have labels and nearby explanation, and not reveal
the answer during an independent assessment. This implements the owner's
preference; a host-independent packet cannot guarantee an interactive renderer.

**Teach a self-contained lesson.** The learner should receive the definitions,
examples, diagrams, and information needed in the lesson itself. Replace
“page 6 of the slides says…” with a direct explanation of the concept. Do not
assume that the learner opens the attachment, recognizes a filename, or remembers
the source's numbering. Keep source locators and provenance available to the
planning agent and tutor for verification and coverage. Source-grounded scope
remains essential; routine source narration in teaching does not. This distinction
preserves the [agreed coverage requirement](../design/requirements.md) while
implementing the owner's requested teaching experience.

These are instruction and packet-authoring changes. Already archived lessons and
independently installed private harness versions do not acquire them
automatically; those require an explicit update and a newly prepared lesson.
