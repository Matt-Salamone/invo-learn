# 11: Activate, retry and recover an explicitly migrated workspace

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Activate a rehearsed destination only after evidence projection, report reconciliation and preservation checks pass, then demonstrate safe retries and recovery from a representative interruption.

**Blocked by:** 09 — Replace uncertain migration credit with fresh study automatically; 10 — Gate migration on actual in-progress lesson reports.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 41, 50, 51, 54, 56, 57.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → explicit migration → validated staged state → active destination / recovery. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Require explicit migration and all recorded cutover checks; no normal update or status operation can implicitly activate staged learner data.
- [x] Verify required inventory, original hashes and report associations before activation; integrity failure retains usable originals and reports cutover as incomplete.
- [x] Use the existing serialized/atomic persistence discipline as appropriate so interrupted activation is recoverable and cannot claim false success.
- [x] Repeat migration/activation without duplicate sources, reports, progress or reviews.
- [x] The activated destination is usable through S1, retains incomplete history, and enforces the global pending-slot rule.
- [x] Demonstrate recovery on synthetic copies with preserved source repositories/histories and no destructive replacement of unrelated or untracked work.

## Answer

Implemented explicit activation and interruption recovery through installed migration-activate and migration-recover commands. The verified source/stage, current projection, exact actual-report associations and explicit waiver records gate a checked current-code candidate. Known copied runners are guarded before old bundles can mutate rehearsals; customized runners are preserved/refused. The destination retains its Git directory, remote bindings, unrelated work and mailbox binding. An immutable file plan plus small batched cursor journals the overlay; active state is published only after installed-runtime, archive and byte-policy checks. Resume and owned-write rollback preserve conflicts/newer work instead of overwriting them. Cached plans cannot omit newer staged returns.

Activation also records verified original archive receipts. Ordinary post-cutover ingest now accepts original-format retired course and assignment returns into separate historical archives with exact raw preservation, no mastery/retention credit and no pending-slot changes, independent of old stage paths. See docs/user/migration.md and invo_learn/migration_activation.py / migration_late.py.

Validation: 11 installed activation/recovery journeys pass (107.2s), plus 8 rehearsal, 9 reconciliation and 5 projection regression journeys. Tests include a real frozen public 0.7.0 installation, immutable old bundles, copied-old-runner refusal, source changes, byte/history preservation, cross-course pending enforcement, external mailboxes, interruption/resume, rollback/retry, late original reports and archive tamper refusal, and stale cached plans after new actual returns. Reused agreed S1/component v0.1, timing v0.3 and pending v0.2 decisions. Windows byte-policy path fix is included. All inputs were synthetic; these checks do not prove live teaching or learner independence.
