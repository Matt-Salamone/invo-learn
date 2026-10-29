# 11: Activate, retry and recover an explicitly migrated workspace

**Status:** ready-for-agent

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Activate a rehearsed destination only after evidence projection, report reconciliation and preservation checks pass, then demonstrate safe retries and recovery from a representative interruption.

**Blocked by:** 09 — Replace uncertain migration credit with fresh study automatically; 10 — Gate migration on actual in-progress lesson reports.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 41, 50, 51, 54, 56, 57.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → explicit migration → validated staged state → active destination / recovery. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Require explicit migration and all recorded cutover checks; no normal update or status operation can implicitly activate staged learner data.
- [ ] Verify required inventory, original hashes and report associations before activation; integrity failure retains usable originals and reports cutover as incomplete.
- [ ] Use the existing serialized/atomic persistence discipline as appropriate so interrupted activation is recoverable and cannot claim false success.
- [ ] Repeat migration/activation without duplicate sources, reports, progress or reviews.
- [ ] The activated destination is usable through S1, retains incomplete history, and enforces the global pending-slot rule.
- [ ] Demonstrate recovery on synthetic copies with preserved source repositories/histories and no destructive replacement of unrelated or untracked work.
