# Practical defaults

- **Python 3.10+ standard library and JSON files:** cross-host portability without
  a server or package-install dependency. Single state commit prevents half-imported
  progress; lock serializes writers. File artifacts precede the commit, so a crash
  may leave recoverable unused files, never automatic learning evidence.
- **Private workspace per learner:** independent Git initialization, no remote
  by default, all tracks share profile/review policy; track overrides inherit live
  global defaults. The learner opens one folder. Setup downloads temporary source
  instead of asking them to clone the public project and switch to a second folder.
  Developer checkouts remain separate from real learner records.
- **Guided choices:** explain each preference and ask one question per turn,
  stopping until answered. Defaults require an explicit skip/delegation, not silence.
- **One mailbox in both directions:** first/later course uploads and prepared
  lessons share the learner-facing exchange folder. The agent registers selected
  resources before staging lessons, distinguishes returned reports and handoff
  metadata, and snapshots all staging copies. No separate incoming folder is needed.
- **Versioned immutable bundles:** automatic compatible trusted-source updates (opt-out), checksummed
  installation, conflict refusal and schema compatibility checks. Compatible
  maintenance preserves the existing data layout. Consolidating supported older
  workspaces uses explicit preservation, report-or-waiver reconciliation,
  conservative projection and activation; other incompatible layouts require an
  implemented migration. See [migration](migration.md).
- **Any file extension accepted:** conservative UTF-8 usability detection plus
  agent inspection with available tools. Permission is needed to create a converter,
  not for ordinary reading. Per-material, single-use, local-only workflow consent;
  external services and automatic reuse are left out of v1. Original and derived
  hashes/provenance remain separate.
- **Reviewable maps:** uploaded primary materials define scope; incomplete source
  interpretation is recorded as gaps. New uploads never silently alter accepted
  objectives. Supplemental material is opt-in and labeled, not new scope authority.
- **Conservative grading:** no numeric mastery or gates. All assistance disqualifies
  independent evidence. Annotated chronological attempts allow a fresh unaided
  assessment to explicitly resolve earlier failures while preserving all attempts;
  unresolved failures remain uncertain. Legacy reports retain any-failure blocking.
  Review relearning resets review needs rather than demonstrating retention. Reports
  can be disputed and withdrawn as a whole or reviewed with append-only
  objective/assessment dispositions. Original observations remain immutable;
  pending/withdrawn work cannot establish new demonstration. No placement
  assessment is mandatory. See [quality and recovery](quality-and-recovery.md).
- **Self-contained visual teaching:** make liberal use of meaningful visuals,
  interactive when the host supports them, with readable static alternatives.
  Explain content directly without page/file commentary or assuming the learner
  can consult uploads. Provenance remains in maps and tutor context and is supplied
  separately on request. Visual hints are assistance. The handoff instructs these
  behaviors; the runtime does not inspect or enforce the teaching conversation.
- **Adjustable expanding reviews:** 1/3/7/14/30/60 days, repeated at the maximum;
  next-day reset after nonindependent performance. This is an inspectable heuristic,
  not a claim of optimal pedagogy or a calibrated memory model.
- **Optional scheduling:** null by default. Agent-maintained constraints/plan when
  requested, without calendar integration, background jobs or budget locks.
- **Flexible teaching arc:** diagnose, visual model/example, attempt, targeted
  repair or reduced support, fresh independent check, recall/transfer. Branch on
  the learner's reasoning rather than enforcing a fixed quiz sequence. Teaching
  behavior remains portable instructions, while evidence handling is deterministic.
- **Progress and mastery displays:** every chatbot turn ends with a portable text
  progress bar based on completed lesson checkpoints and a separate provisional
  summary of objective evidence. Checkpoint totals can adapt with explanation;
  finishing a session does not imply mastery. Independent/retained labels follow
  report evidence rules and can fall after new conflicting evidence. The display
  changes no schema or durable state and stays outside the final report JSON.
- **Automatic study updates:** reports and plans/backup first, then check/install
  the latest compatible trusted candidate before a lesson/review. Existing checks,
  backup and rollback remain. New preparation uses the activated interpreter and
  templates; restage preserves archived bytes. Offline/failure never means current.
- **Scoped private backup:** the agent commits/pushes reviewed changes after every
  interaction, including handoffs, report/plan updates, intake and maintenance.
  Explicit file scope and a bound verified private GitHub remote prevent public or unrelated publication. Failures preserve study success.
  No remote is created. Both workflows have boolean global/track opt-outs; existing
  stored choices survive, and missing workflow keys inherit true after one upgrade.
- **Detailed default teaching:** longer comprehensive mechanisms, causal reasoning,
  worked examples and useful visuals before practice; prior knowledge and explicit
  style preferences adapt the depth. Legacy stored teaching values are preserved.
- **One pending main handoff:** all courses, assignments, reviews and guided
  implementation sessions share one slot. An actual in-progress main report
  releases it while preserving incomplete history; explicit retirement retains the
  issued packet. Supplemental reports leave the slot unchanged. Resume with a new
  packet after the previous session is resolved.
- **Independent assignment choices:** ask about an upfront verified reference
  before lesson planning and implementation guidance only at that later transition.
  Each requires an actual answer and keeps its own decision/exposure history.
- **Dedicated mailbox:** new/empty adoption only, owner/path marker, root/protected
  folder/link checks, full snapshots before clearing, pending-report barrier.
  External mailboxes allowed. Filesystem attack races and concurrent hostile access
  are outside scope; keep the dedicated directory under learner control.

The implementation is original. Surveyed projects informed the design; no source
code or assets from them were copied. The supported legacy assignment readers
are original compatibility implementations; no old assignment helper was copied
verbatim. The frozen public 0.7.0 test distribution comes from this project's
commit `214178c` and retains its MIT license; it contains no learner records.
