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
- **Versioned immutable bundles:** explicit trusted-checkout updates, checksummed
  installation, conflict refusal and schema compatibility checks. Version 1 needs
  no data migration. Future incompatible migrations are outside this release.
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
  can be disputed and withdrawn as a whole; precise assessment-level correction
  can be a future feature. No placement assessment is mandatory.
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
- **Routine update awareness:** one read-only GitHub version check per resumed
  study session, after handling reports and before a new handoff. Five-second
  timeout, no learner data sent, offline study allowed. Installation still needs
  an explicit learner request and the existing versioned upgrade procedure.
- **Dedicated mailbox:** new/empty adoption only, owner/path marker, root/protected
  folder/link checks, full snapshots before clearing, pending-report barrier.
  External mailboxes allowed. Filesystem attack races and concurrent hostile access
  are outside scope; keep the dedicated directory under learner control.

The implementation is original. Surveyed projects informed the design; no source
code or assets from them were copied.
