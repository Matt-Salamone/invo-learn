# 08: Rehearse a lossless combined-workspace import

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Explicitly rehearse importing older course and assignment workspaces into a private staged destination, attaching assignments to their courses and preserving all original material and work without activating the destination.

**Blocked by:** 03 — Study a course-owned assignment without an upfront solution; 07 — Inspect older learning and assignment records through invo-learn.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 30, 48, 50, 51, 54, 55, 56.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → explicit migration → read-only sources, staged destination and preservation manifest. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Inventory and preserve records, sources, derived artifacts, issued packets, raw reports, existing solutions, tracked files and untracked learner work.
- [x] Retain original IDs and origin commits, with deterministic origin-scoped associations where canonical IDs differ. Identical bytes do not erase distinct provenance.
- [x] Preserve compatible existing course state; do not discard established learning merely because an assignment mapping needs later conservative projection.
- [x] Apply the agreed no-source-commentary default to migrated settings while preserving exact issued packet bytes.
- [x] Produce inspectable staged results and a preservation manifest; do not activate, change source remotes, splice Git histories or mutate source workspaces.
- [x] Verify both a successful installed rehearsal and a missing/damaged-input refusal at S1; pedagogy projection and final cutover remain separate subsequent slices.

## Answer

Implemented explicit installed migration-rehearse and migration-status commands, with the existing course workspace as both the preserved baseline and eventual activation destination. The independent private stage holds complete raw source trees including full standalone Git histories, ignored/untracked work and external mailboxes, a hash/byte/directory preservation manifest, stable origin associations, and an inactive combined workspace. Existing course objectives, reports and reviews survive unchanged; assignments and their exact legacy contexts join their course without inferred decisions or progress credit. Custom teaching preferences retain their text plus an explicit no-source-commentary presentation override. See docs/user/migration.md.

Validation: 8 installed S1 migration tests and 8 installed legacy reader tests pass. Journeys cover source/snapshot byte equality and Git commits, identical-byte origins, retry idempotence, damaged/missing original refusal, altered course report hashes, external mailbox preservation, inactive-stage study refusal, linked-Git refusal and confined manifest paths. Reused accepted component v0.1 / S1, timing v0.3 and pending v0.2 views. Projection, report/waiver reconciliation and activation remain tickets 09-11. No private learner inputs were used.
