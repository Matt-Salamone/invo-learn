# 01: Install and use the single invo-learn entry point

**Status:** ready-for-agent

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Set up a synthetic private learner workspace through the sole invo-learn entry point, then complete the existing course intake, lesson/report and status workflow through that installed interface. Consolidate the named skills and entry points without changing learner layout implicitly.

**Blocked by:** None (can start immediately).

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 1, 2, 3, 4, 5, 9, 10, 11, 12, 33, 59, 60, 61.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → command adapter → installer / study → installed bundle and private artifacts. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] One canonical learner skill/command is installed; setup, course/material intake, reporting and maintenance are operations within it. Obsolete public names and aliases are not delivered as wrappers.
- [ ] A fresh installed journey remains usable after temporary public source downloads are removed, with explained setup choices and existing material-intake permissions preserved.
- [ ] Existing course lessons, raw reports, mailbox originals, coverage and reviews remain usable; legacy data is not silently reorganized by installation.
- [ ] Include any necessary command/installer prefactoring within this end-to-end slice, preserving existing meaningful regression checks.
- [ ] Verify at S1 with a real temporary private workspace and an installed subprocess command; keep all fixtures synthetic and public/private isolation intact.
