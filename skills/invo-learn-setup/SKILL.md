---
name: invo-learn-setup
description: Set up invo-learn from its public repository into an independent private learner workspace, with a pinned harness and shared defaults for multiple learning tracks.
---

# Set up a learner workspace

Use the public package at https://github.com/Matt-Salamone/invo-learn. If already
checked out, use it; otherwise clone to a tools/cache directory. Read its README
and docs/user/guide.md. Python 3.10+ and Git suffice; no model API or server is needed.

Choose a NEW private directory outside the public checkout (e.g. a sibling
`invo-learn-private`). It must be independent, never a fork of the public repo.
Briefly collect learner name, preferred explanation/practice style, default
supplemental-research preference, remedial preference, and mailbox location.
Offer: "Do you want a schedule, time budget, or deadlines?" These are optional;
leave schedule null when not requested. Use documented defaults for unspecified
preferences. Default mailbox to `mailbox/` at the private root. An external folder
is allowed only when new/empty and dedicated to this learner's staging.

Save supplied preferences as private JSON or omit --preferences for defaults.
From the public checkout run:

```sh
python -m invo_learn bootstrap <private-directory> --name <learner-name>
```

Optional flags: --mailbox <location>, --preferences <private-json-file>.
Do not use --no-git unless a files-only setup is explicitly preferred. No remote
is created by default. Only when requested and authorized, create a separate
PRIVATE remote, verify its visibility before pushing, and never upload these
records to the public package. Host-specific account tooling is optional.

Open the private directory as the agent's workspace. Read its AGENTS.md and
`.agents/skills/invo-learn/SKILL.md`; the installer supplies discoverable skills.
Hosts without automatic skill discovery can read the same files directly.
Run `python learn.py status`, explain where materials and records live, and give
the learner the mailbox upload/report-paste instructions. Begin track intake
only when a track/materials are supplied. Never seed real learner records into
the public package. Do not auto-update the installed harness.
