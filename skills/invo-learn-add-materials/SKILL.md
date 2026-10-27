---
name: invo-learn-add-materials
description: Receive first or additional course resources through the invo-learn mailbox, preserve originals, and propose coverage changes for learner review without losing existing progress.
---

# Receive course materials

Work in the learner workspace. Read AGENTS.md, state.json, OVERVIEW.md, the selected
course's plan.md and `python learn.py status`. If the course is ambiguous, ask
which course these resources belong to and wait. Reuse the selected existing
course; do not create another course or repeat its preference interview.
For a new course, use `../invo-learn-add-course/SKILL.md` first.

Ask **one question per turn**, explain unfamiliar choices, and **stop and wait**
where a learner answer is needed. Already supplied answers/files count; silence does not.

## Explain the exchange

Show a clickable link or exact absolute path to the configured mailbox. Say:
"Put this course's syllabus, notes, slides, or other resources in [mailbox],
then tell me 'materials ready.' I will save the originals in the course records.
This same mailbox is where you'll pick up lesson files later."
The learner may instead attach files or give existing paths; the agent handles
the same filing. Do not create a separate incoming folder. Do not require the
learner to move resources into internal course directories or run import commands.
If they have no materials, ask for a syllabus, resource, or written outline of
what to cover; do not invent source-grounded coverage. Discuss research only if
they request help finding sources, observing their research preference.

Wait until files are supplied or the learner says they are ready. If the mailbox
already contains a lesson, explain that they should add new files alongside it
without replacing lesson files. Preserve the pending lesson and any returned
report; intake can occur while a lesson is pending, but it does not abandon it.

## File and inspect the resources

Inspect mailbox contents. Use archived packet names/checksums and registered
original checksums to distinguish old handoff files from new uploads. Never sweep
every file into a course blindly: exclude the ownership marker, generated lesson
instructions/metadata/schema and already registered copies. Inspect a possible
returned report and ingest it as evidence only through the report workflow, not
as study material. If a file's role/course is unclear, ask one targeted question.

For every selected upload (any extension), use:

```sh
python learn.py add-material <course-id> <absolute-file-path>
```

This accepts files directly from the mailbox, copies their bytes into durable
`tracks/<id>/materials/originals/` storage and registers them. Retry of an identical
mailbox upload for that course/role reuses the record. Verify returned originals
and hashes. Leave mailbox copies until prepare/restage snapshots the full mailbox;
never manually clear it, and never remove an upload before durable registration.
For nested folders register each selected file, preserving source locators in notes.

Read every primary resource. For directly readable non-text formats record tool,
coverage and limitations with inspect-material. If a local conversion workflow
is needed, explain tools, outputs and fidelity loss and ask permission before
creating/running it; then use approve-transform and add-derived. Preserve originals.
Unusable sources stay visible as gaps. See the active release's user guide/contracts.

## First plan or additional-material update

For a first upload, propose a source-linked coverage map covering the supplied
resources. For later uploads, compare against the accepted map and existing
evidence; explain added objectives, expanded source links, proposed deferrals,
prerequisite changes, and source gaps. Preserve objective IDs and existing
progress; changed objective meaning requires a new ID and deferral of the old one.
Do not reset the course or silently replace the accepted map.

Use propose-map and show the proposed plan/change summary with source locators.
For new objectives, include observable success_criteria. Inventory the source's
sections with source_sections and section_inventory: link each section to the
matching objectives or explain an omission/deferral. Record inspection limits
explicitly; inventory completeness is not demonstrated learner understanding.
Read the active release's docs/user/quality-and-recovery.md for the exact shapes.
Preserve existing evidenced criteria and section identity across later proposals;
changed objective meaning needs a new ID. Legacy maps remain readable without
inventing criteria or section associations retrospectively.
Ask the learner to approve or revise it, then **stop and wait**. Only use
accept-map after actual approval; an upload alone is not map approval. Update the
adaptive plan after acceptance, retaining the pending lesson/report barrier within that same course.
Explain the next step: ask for the next lesson when ready; later resources use
this same "add materials to <course>" → mailbox → "materials ready" process.

## End-of-interaction synchronization

When this interaction changes learner-workspace files, follow its AGENTS.md and
the active invo-learn skill's commit/push instructions before the final response.
This includes stopping to wait for an onboarding answer after saving records.
Keep learner data in the verified private workspace and preserve explicit backup
opt-outs; a missing remote leaves a local commit with an explained push limitation.
