# Add a course

Read AGENTS.md, state.json, OVERVIEW.md and `python learn.py status` in the learner
workspace. Reuse an existing course when the learner is adding resources to it;
route that request directly to `add-materials.md`.
"Course" is the learner-facing name for a track, including a non-school skill.

Ask **one question per turn**, explain it briefly, and **stop and wait for an
answer**. Never bundle preference questions or treat silence as agreement.
Reuse answers from this conversation and inherited defaults; do not repeat setup.

1. Ask what course or skill to add, if not already supplied. Use a stable lowercase
   course ID and create it with `python learn.py add-course <id> --title <title>`.
2. Ask what they want to be able to do or prepare for, if unknown. Save their goal
   in `tracks/<id>/plan.md`; do not invent course requirements from it.
3. Explain the inherited teaching style, whether extra researched explanations are
   allowed, and how catch-up help works, in plain language. Ask one question:
   "Would you like to use those settings for this course?" If they want changes,
   discuss each requested choice separately and store only per-course overrides.
   The new default is detailed mechanisms, causal reasoning and worked examples
   before practice with useful visuals; honor any stored alternative. Also explain
   inherited automatic compatible updates and private backups and their
   auto_update/auto_backup opt-outs; do not reset existing choices.
4. If no course scheduling constraints were supplied, explain that study time and
   deadlines are optional and ask whether they want any for this course. Wait.
   Gather requested details one at a time; otherwise inherit defaults (null when
   no scheduling was requested). Do not imply automatic reminders.

Use `preferences <private-json> --track <id>` for course overrides. A short
prerequisite lesson is a recommendation; the learner may still choose to advance.
Supplemental research means opt-in extra explanations/examples, labeled separately
from uploaded sources and unable to silently enlarge course requirements.

Continue to `add-materials.md` with this course selected.
That operation provides the actual mailbox path, waits for files, preserves originals,
and proposes a source-linked plan for review. Do not prepare a lesson before the
learner has reviewed and approved its coverage map.

## End-of-interaction synchronization

When this interaction changes learner-workspace files, follow its AGENTS.md and
the active invo-learn commit/push instructions before the final response.
This includes stopping to wait for an onboarding answer after saving records.
Keep learner data in the verified private workspace and preserve explicit backup
opt-outs; a missing remote leaves a local commit with an explained push limitation.
