---
name: invo-learn-setup
description: Guide initial invo-learn setup with explained, one-question-at-a-time choices and install one learner workspace without a public source clone.
---

# Set up one learning workspace

Read the public README and docs/user/guide.md at
https://github.com/Matt-Salamone/invo-learn. Python 3.10+ and Git suffice;
no model API or server is needed. This skill sets up learning, not development
of the public harness. An existing learner workspace should be reused.

## Conversational intake

Ask **one question per turn**, briefly explain the choice in everyday language,
then **stop and wait for the learner's answer**. Do not bundle fields into one
question, send a questionnaire, or continue dependent setup while waiting.
Silence and elapsed time are not acceptance of defaults. Honor answers already
supplied; a learner may explicitly choose defaults for the remaining questions.
Save answers in private temporary notes so an interrupted setup can resume.

Start by explaining: "You'll use one folder for your courses and progress. The
mailbox inside it, or on your Desktop, is where you give me materials and pick up
lesson files. I'll guide you through each choice."

Collect these choices in order, skipping only already answered choices:

1. **Workspace:** explain that the current new/empty folder can be the learner's
   only workspace. Ask where to keep it; recommend the current folder when suitable.
   Do not ask them to clone or open a second repository. A public developer checkout
   is not suitable for learner records; explain that distinction if encountered.
2. **Name:** ask what name to use; do not infer it from the computer account.
3. **Teaching style:** explain "I can use a short explanation, have you try a
   question, then give feedback." Ask whether that suits them or they prefer another style.
4. **Supplemental research:** explain "Your files define what we study. With this
   enabled, I may look up extra explanations or examples and label them separately;
   they won't silently add course requirements." Ask whether to allow it; recommend off.
5. **Prerequisite help:** explain "If a missing background skill makes something
   hard, I can suggest a short catch-up lesson. You can still choose to move on."
   Ask whether they want that or another approach. Store it as the remediation preference.
6. **Mailbox location:** explain both directions: put course resources here and
   say "materials ready"; later pick up agent-prepared lesson files here. Recommend
   `mailbox/` inside the workspace, offering a dedicated Desktop folder if preferred.
   Ask for the location. An external folder must be new/empty and dedicated to learning.
7. **Optional scheduling:** explain "I can plan around study time or deadlines;
   you can also study whenever you want. Review dates in the records work either
   way, without automatic notifications." Ask "Do you want a schedule, time budget,
   or deadlines?" Keep schedule null if declined. Gather any requested details one
   question at a time. Do not create an automation or calendar event implicitly.

After answers, summarize the chosen settings in plain language. Use documented
defaults only for choices the learner explicitly skipped or delegated. Do not
restart the interview or add a redundant final approval question.

## Install in the chosen folder

Use `setup_workspace.py` from the public repository. Read it before executing.
Download it to a temporary tools location, not the learner's chosen folder (which
must remain new/empty). It downloads a temporary archive, installs the pinned
harness inside the chosen folder, and removes the temporary source automatically.
No public checkout or permanent second workspace is needed.

Save preferences as private temporary JSON, then run:

```sh
python <temporary-path>/setup_workspace.py <chosen-folder> --name <name> --preferences <private-preferences.json> --mailbox <location>
```

For a developer who already has a trusted source checkout, the equivalent
`python -m invo_learn bootstrap <chosen-folder> --name <name> ...` remains available.
Never put real learner data in the public source checkout or a public fork. Keep
default Git initialization; use --no-git only if files-only setup was requested.
No remote is created. A hosted private remote requires an explicit request and
visibility verification before pushing. Do not auto-update the installed harness.

Work from the chosen learner folder for subsequent commands. Read its AGENTS.md,
START-HERE.md and installed `.agents/skills/invo-learn/SKILL.md`; run
`python learn.py status`. Show its actual path and the actual mailbox path.
Explain that records and archived originals live in the workspace and the agent
handles filing; the learner only exchanges files via the mailbox and reports via chat.

## First course

Continue with `.agents/skills/invo-learn-add-course/SKILL.md`. Reuse a supplied
course name/materials; otherwise ask only "What course or skill would you like to
add first?" and wait. Do not leave the learner with only a list of CLI commands
or upload instructions without an actual course/material destination.
