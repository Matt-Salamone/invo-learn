# 15: Migrate the private workspaces and retire superseded repositories

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Use the released combined harness to inventory and rehearse the owner's explicitly identified private workspaces, reconcile the actual reports, perform verified cutover into the existing private learning destination, and then retire the superseded repositories and entry points.

**Blocked by:** 13 — Verify and release the complete combined public harness; 14 — Collect in-progress reports from every checked-out lesson chat.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 4, 30, 51, 52, 53, 54, 55, 56, 57, 58, 59.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 on verified private inputs → rehearsal / reconcile / activate → verified private Git backup and read-only retirement. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Execute with owner-identified source/destination repositories and verified existing private remote bindings; retain concrete paths, inventories, origin commits and results in private migration notes only.
- [x] Rehearse on private copies and verify preservation, conservative evidence, report associations and recovery before touching the active destination. Reconcile available actual reports and record the owner's October 29 waiver for missing-return checkouts (ticket 14); retire those incomplete and plan fresh checks/relearning without invented progress.
- [x] Preserve all sources, issued artifacts, reports, existing reference solutions, tracked/untracked learner work and complete source Git histories; apply the agreed presentation default to migrated settings.
- [x] Activate only after all checks pass, verify normal installed study and the single pending slot, and commit/push reviewed related private changes using ordinary pushes with remote SHA verification.
- [x] On integrity, visibility, backup or association problems, retain the usable originals and report the concrete limitation; do not erase work or claim a verified cutover that did not happen.
- [x] Only after verified success, add relocation notes and archive the superseded public assignment and private assignment repositories read-only. Public relocation notes must not expose private learner details.
- [x] Remove obsolete entry points from managed installations after verifying the destination, preserving frozen original snapshots and unrelated user tools. Report completion without publishing private migration evidence.

## Answer — private cutover and retirement verified

The actual private cutover, retirement and final scoped ordinary private backup
push are verified. Source/destination bindings, private nonfork visibility and remote
branch SHAs were checked. Full raw source trees, ignored/untracked work, issued
artifacts and complete Git histories are preserved with inventories, exact-byte
archives and independently checked ordinary Git backup blobs. Concrete evidence
and paths remain private.

Rehearsal verified interruption/resume recovery, normal installed status/doctor,
the workspace-wide pending-slot refusal and preservation of existing reports,
objective/review state, preferences and custom synchronization guidance. The
owner's October 29 waiver was recorded separately for each missing-return
checkout. Those sessions retired incomplete; conservative fresh-study needs
remain, without invented reports, answers or assessment credit.

The active destination now uses published 0.8.1. Its standard maintenance upgrade
corrected the generated overview's temporary mailbox reference while preserving
the immutable 0.8.0 bundle and all learner state except the maintenance event.
Both releases' payload hashes and the actual mailbox were independently checked.
Staged byte attributes and preservation-artifact hashes passed before the ordinary
private push; preserved original whitespace was verified as data, not rewritten.

After inspecting the concrete retirement proposal, the owner explicitly approved
all prepared actions. Exact approved relocation bytes were written and scoped
ordinary pushes verified before both superseded repositories were archived
read-only. The active private destination remains private and writable. The exact
obsolete global entry-point tree was preserved and retired; unrelated tools and
the original untracked learner work remain intact. Public relocation additions
contain only the canonical public project URL and reusable guidance.

The final private completion backup retains approval, proposal, relocation,
retirement and patch verification evidence as ordinary Git blobs. Staged artifact
hashes and byte counts, portable byte attributes and the remote branch SHA were
verified. Installed status/doctor passed after retirement, the main pending slot
is empty, and the destination working tree is clean. Concrete evidence remains
private; all acceptance criteria are complete.

## Comments

October 30, 2026: automatic approval review initially rejected the retirement
operation before execution because repository archival and global entry-point
retirement lacked direct explicit authorization for their reversal cost. Exact
drafts, hashes, diffs and targets were then prepared privately. The owner explicitly
approved all prepared retirement actions before execution resumed. The earlier
blocker is retained as decision history and is now superseded by the verified
approved completion above.
