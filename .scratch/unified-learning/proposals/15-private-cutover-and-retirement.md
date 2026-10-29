# 15: Migrate the private workspaces and retire superseded repositories

**Status:** needs-info

Draft proposal: awaiting approval of the breakdown. Publish after approval as ready-for-agent.

**What to build:** Use the released combined harness to inventory and rehearse the owner's explicitly identified private workspaces, reconcile the actual reports, perform verified cutover into the existing private learning destination, and then retire the superseded repositories and entry points.

**Blocked by:** 13 — Verify and release the complete combined public harness; 14 — Collect in-progress reports from every checked-out lesson chat.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 4, 30, 51, 52, 53, 54, 55, 56, 57, 58, 59.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 on verified private inputs → rehearsal / reconcile / activate → verified private Git backup and read-only retirement. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Execute with owner-identified source/destination repositories and verified existing private remote bindings; retain concrete paths, inventories, origin commits and results in private migration notes only.
- [ ] Rehearse on private copies and verify preservation, conservative evidence, report associations and recovery before touching the active destination. Recheck that every required actual report has been returned and reconciled.
- [ ] Preserve all sources, issued artifacts, reports, existing reference solutions, tracked/untracked learner work and complete source Git histories; apply the agreed presentation default to migrated settings.
- [ ] Activate only after all checks pass, verify normal installed study and the single pending slot, and commit/push reviewed related private changes using ordinary pushes with remote SHA verification.
- [ ] On integrity, visibility, backup or association problems, retain the usable originals and report the concrete limitation; do not erase work or claim a verified cutover that did not happen.
- [ ] Only after verified success, add relocation notes and archive the superseded public assignment and private assignment repositories read-only. Public relocation notes must not expose private learner details.
- [ ] Remove obsolete entry points from managed installations after verifying the destination, preserving frozen original snapshots and unrelated user tools. Report completion without publishing private migration evidence.
