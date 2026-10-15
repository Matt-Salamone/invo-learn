# invo-learn

A portable learning harness: your planning agent manages sources, coverage, lesson
plans, evidence and spaced reviews. A separate chatbot teaches each lesson and
returns one structured report. You upload the reusable mailbox into a fresh chat,
then paste the report back; your agent handles the bookkeeping.

## Start here

Give your agent this request:

> Set up invo-learn in this folder using
> https://github.com/Matt-Salamone/invo-learn and skills/invo-learn-setup/SKILL.md.
> Explain each choice, ask me one question at a time, and wait for my answer.
> Then help me add my first course.

Start in a new/empty folder. You keep **one learning workspace** containing all
your courses and progress. Your agent downloads the harness temporarily and
installs it inside that folder; you do not need to clone this public repository,
manage a second workspace, or switch projects after setup. **Python 3.10+ and Git**
are the only dependencies. No API key or server is required.

For manual installation, download and inspect
[setup_workspace.py](setup_workspace.py) into a temporary tools location, then run:

```sh
python /path/to/setup_workspace.py /path/to/my-learning --name "Your name"
```

The first setup question is **"Would you like to set up using all defaults?"**
The agent explains the defaults before asking and waits for your answer. Say yes
to skip the individual setup questions, or no to customize one choice at a time.

The agent-led setup explains and collects teaching style, whether to look up
extra explanations beyond your files, whether to suggest catch-up lessons for
missing background skills, and optional study times/deadlines. Manual installation
uses defaults; `--preferences <private.json>` supplies alternatives and
`--mailbox <path>` chooses a dedicated mailbox, including on your Desktop.
Setup creates a local Git repository with no remote. Your learning records stay
out of the public package; a hosted private backup is optional.

## Add your first course

In your learning workspace, tell your agent **"Add a course"** (or name a skill).
It uses [invo-learn-add-course](skills/invo-learn-add-course/SKILL.md), asking and
explaining one choice at a time. When it gives you your mailbox path, put the
course's syllabus, notes, slides, or other resources there and say **"materials
ready."** You can also attach files or give paths. The agent saves the originals
and proposes a source-linked plan for you to review before starting a lesson.

## Add more material later

Say **"Add materials to [course name]"**, put the new resources in the **same mailbox**,
and say **"materials ready."** The
[add-materials skill](skills/invo-learn-add-materials/SKILL.md) files them in the
existing course and proposes plan changes without resetting your progress.
You review changes before they become the accepted plan.

## Take a lesson

Ask for the next lesson. When your agent says the mailbox is ready, upload every
visible file into a fresh chatbot conversation. Ask it to teach `START-HERE.md`
and return the JSON report. Paste that one report back to your planning agent.
The agent updates your records and plans the next lesson or review.

Lessons use visuals liberally, including interactive diagrams and charts when
supported. Teaching stands on its own without slide/page commentary or asking
you to consult uploads; source links remain in the coverage map for reference.
The teaching arc branches on your reasoning: diagnose, model/example, attempt,
targeted feedback, fresh independent check, recall and transfer. Early mistakes
stay in the record and can be explicitly resolved by later independent work.
Success after reteaching in a review counts as relearning rather than retention.
Every chatbot turn ends with a lesson progress bar and a separate provisional
mastery summary. Completion tracks lesson checkpoints; mastery tracks independent
performance and delayed retention, with durable records updated from the report.

The mailbox is the interface in both directions: you drop off resources and pick
up lesson files there. Originals and lessons are archived elsewhere in your one
workspace before the agent reuses it. Add new files alongside an unfinished
lesson without overwriting its files; the agent preserves the pending session.
Do not manually clear the mailbox.

Read the [usage guide](docs/user/guide.md), [contracts](docs/user/contracts.md),
[documented defaults](docs/user/decisions.md), and [worked example](examples/README.md).
The [setup](skills/invo-learn-setup/SKILL.md), [study](skills/invo-learn/SKILL.md), and
[update](skills/invo-learn-update/SKILL.md) skills work through ordinary files and
commands across agent hosts. No API key or application server is required.

## Verify or develop

```sh
python -m unittest discover -s tests -v
python examples/worked_example.py
python -m invo_learn --help
```

See [verification results and limits](docs/user/testing.md). CI is configured for
Windows/Ubuntu and Python 3.10/3.13; local validation used Windows/Python 3.13.

The synthetic example creates a temporary independent workspace with two tracks,
coverage, a lesson/report cycle and a delayed review. It requires no real chatbot.
Developers with an existing source checkout may still use `python -m invo_learn
bootstrap <new-learner-folder> --name "Your name"`. Real learner records never
belong in this public development checkout or a public fork.

Updates are explicit: from your learning workspace run `python learn.py upgrade
--source /path/to/trusted/newer-public-checkout`. Versions are immutable; records
and preferences are preserved.
During normal study, the agent runs `python learn.py check-updates` once per
resumed session. It checks the public GitHub version without sending learner
data or installing code; unavailable checks do not interrupt study.

Report validation cannot independently verify the chatbot's judgments or unaided
work. Complex materials require appropriate reading/conversion tools and permission
before automatic transformation workflows. This version has no automated chatbot
integration, calendar connector or background scheduler.

Design context: [requirements](docs/design/requirements.md), [build prompt](docs/design/build-prompt.md),
[source-inspected research](docs/research/agentic-tutoring-harnesses.md), and
[teaching-cycle comparison](docs/research/teaching-cycle-comparison.md).
