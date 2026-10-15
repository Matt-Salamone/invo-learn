# invo-learn

A portable learning harness: your planning agent manages sources, coverage, lesson
plans, evidence and spaced reviews. A separate chatbot teaches each lesson and
returns one structured report. You upload the reusable mailbox into a fresh chat,
then paste the report back; your agent handles the bookkeeping.

## Start here

Give your agent this request:

> Set up invo-learn from https://github.com/Matt-Salamone/invo-learn using
> skills/invo-learn-setup/SKILL.md. Create an independent private learner workspace
> outside the public checkout, then help me add a learning track.

Or, with **Python 3.10+ and Git**, clone the public package and run:

```sh
git clone https://github.com/Matt-Salamone/invo-learn.git
cd invo-learn
python -m invo_learn bootstrap ../invo-learn-private --name "Your name"
```

Open the private directory with your agent and ask it to read AGENTS.md. Setup
copies a pinned harness and skills there; it creates no remote. You can choose a
dedicated external mailbox with --mailbox. Scheduling and supplemental research
are optional. Real study data belongs in the private workspace, never this public
repo or a public fork.

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
Updates are explicit: from your private workspace run `python learn.py upgrade
--source /path/to/trusted/newer-public-checkout`. Versions are immutable; records
and preferences are preserved.

Report validation cannot independently verify the chatbot's judgments or unaided
work. Complex materials require appropriate reading/conversion tools and permission
before automatic transformation workflows. This version has no automated chatbot
integration, calendar connector or background scheduler.

Design context: [requirements](docs/design/requirements.md), [build prompt](docs/design/build-prompt.md),
[source-inspected research](docs/research/agentic-tutoring-harnesses.md).
