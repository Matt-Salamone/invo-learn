# Changelog

## 0.4.1

Pending lessons are scoped to courses. A different course can prepare a lesson
or run study-update while another awaits its report. Same-course duplicate
preparation remains blocked. status and the overview expose pending lessons per
course; restage can restore any prepared packet, and abandonment targets a named
prepared lesson. Shared mailbox switches retain snapshots and immutable archives,
and reports may be imported in any course order. Existing state and report
schemas are unchanged; active_lesson remains the last staged packet.

## 0.4.0

Default lessons explain concepts comprehensively before practice, including
mechanisms, causal reasoning, justified worked examples and meaningful visuals.
Adaptive questions, feedback, faded help and independent/delayed evidence remain.
Existing stored teaching preferences and archived packets are preserved.

Study automatically installs a newer compatible release from the trusted public
source before preparing lessons/reviews, unless auto_update=false. The updater
uses existing compatibility, checksum, customization, backup and recovery checks;
prepare re-enters newly active code. Save/ingest reports and finish their plans
and backup before updates. Offline/failed checks never imply current status.

The default agent workflow commits and pushes completed lessons and processed
reports/plans with explicit file scope, unless auto_backup=false. A new helper
requires a workspace-bound, freshly verified private independent GitHub remote,
refuses unrelated staged/unpushed changes, never force-pushes and verifies the
remote SHA. Backup failure preserves learning success. GitHub verification needs
authenticated gh; no remote or visibility is created/changed automatically.

Existing installations need one authorized upgrade to receive this workflow.
Missing workflow keys default true; all stored values (including legacy short
teaching styles and explicit opt-outs) survive. No state/report schema change.

## 0.3.1

Every teaching-chatbot turn ends with a compact progress bar based on completed
lesson checkpoints and a separate provisional mastery summary for assigned
objectives. Checkpoint totals adapt with explanation; pending answers and early
stops do not fabricate progress. Mastery labels follow independent-performance
and delayed-retention evidence, separately from session completion. Footers stay
outside the final report JSON. These are portable chatbot instructions; durable
evidence continues through the existing validated report workflow.

## 0.3.0

Lessons use a flexible arc with explicit choices for sound reasoning, weak
reasoning, local errors, conceptual errors and assisted success. Tutors fade
support, repair misconceptions and close with recall/transfer without a fixed
quiz sequence. The v1 report format adds optional chronological attempt phases,
before-teaching flags and explicit failure-resolution links. Fresh independent
assessment can resolve earlier failures without deleting them; practice cannot
establish understanding and success after review teaching is relearning rather
than retention. Legacy reports retain their prior grading semantics.

Normal study checks GitHub once per resumed session with a read-only
check-updates command. New versions are offered, never installed automatically;
offline checks leave study available and update status unknown.

## 0.2.2

Lesson planning and chatbot handoffs require liberal use of meaningful visuals,
including interactive diagrams/charts when supported and readable static
alternatives otherwise. Lessons teach self-contained explanations without source
page/file commentary or requiring the learner to consult uploads. Provenance
remains in coverage records and tutor context, available separately on request.
Visual hints count as assessment assistance. These are portable teaching
instructions; the runtime does not enforce chatbot presentation behavior.

## 0.2.1

Setup first explains the defaults and asks whether to use them all. A yes skips
individual setup questions; a no keeps the explained, one-question-at-a-time
interview. Explicit exceptions are preserved, and silence never selects defaults.

## 0.2.0

Guided setup asks and explains one choice at a time. A standalone installer
downloads the package temporarily and creates one learner workspace without a
source clone. Dedicated add-course and add-materials skills guide first and later
uploads through the same mailbox used for lesson handoffs. Mailbox originals can
be registered directly, with repeat intake avoiding duplicate material records.
New materials continue to require review of proposed coverage changes.

## 0.1.0

First working manual hybrid workflow: independent private setup, portable planning
skills, source intake and permission ledger, approved coverage maps, guarded reusable
mailbox, structured report/evidence ingestion, adjustable cross-track spaced reviews,
explicit versioned upgrades, and a synthetic two-track worked example.
