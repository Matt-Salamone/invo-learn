# Public invo-learn package

This checkout distributes tools, skills, contracts, documentation and synthetic
examples. Real learner data belongs in an independent private workspace, never
in this checkout or a public fork.

For a request to set up study using this repository, read
`skills/invo-learn/SKILL.md` and follow its setup reference. For implementation, read
`docs/design/build-prompt.md` and `docs/design/requirements.md`.
Setup gives learners one workspace using a temporary source download; it must
explain choices, ask one question at a time, and wait for answers. Course setup
and later uploads use the invo-learn course and material operations and the same mailbox
as lesson handoffs. Requests to improve the harness are development, not learner setup.

The runtime uses Python's standard library (3.10+). Verify changes with
`python -m unittest discover -s tests -v` and `python examples/worked_example.py`.
Keep VERSION and CHANGELOG.md aligned; a distributed version is immutable.
Skills are portable instructions; never assume a particular agent/model API.

## Commit and push after each interaction

Before the final response to every user interaction, inspect Git status/diffs,
validate the changes as appropriate, commit the files changed for that interaction,
and push to the verified existing upstream. Skip an empty commit when nothing
changed. Retry an outstanding task push without repeating completed operations.
Stage reviewed task files explicitly; leave unrelated learner/user work intact.
Use an ordinary push, preserve history, and verify the remote branch SHA. If the
remote is absent, unavailable or rejects the push, retain the local commit and
report the exact limitation. Create or change remotes only on explicit request.
Learner records go only to the learner's verified private repository; public
development checkouts contain reusable code, instructions and synthetic examples.
This is an agent end-of-turn responsibility, including planning, preferences,
intake and report work; direct helper calls do not perform it automatically.

## Lesson and side-chat roles

Read `docs/user/side-chat.md` when changing packet generation, supplemental reports or evidence
projection. Favor useful UML with accompanying code/prose; choose another visual
when clearer. Preserve existing issued packets and original assessment records.

## Agent skills

### Issue tracker

Before creating, reading, or updating issues and wayfinding maps, read
`docs/agents/issue-tracker.md`. Issues use local Markdown under `.scratch/`.

### Triage labels

Before triaging issues, read `docs/agents/triage-labels.md` for the status vocabulary.

### Domain docs

Before exploring domain behavior or terminology, read `docs/agents/domain.md`.
This repo uses a single-context glossary and ADR layout.

### UML rendering

Before rendering UML, read `docs/agents/uml-rendering.md` and use the `uml` skill
to verify local availability.
