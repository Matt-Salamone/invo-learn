# 01: Install and use the single invo-learn entry point

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Set up a synthetic private learner workspace through the sole invo-learn entry point, then complete the existing course intake, lesson/report and status workflow through that installed interface. Consolidate the named skills and entry points without changing learner layout implicitly.

**Blocked by:** None (can start immediately).

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 1, 2, 3, 4, 5, 9, 10, 11, 12, 33, 59, 60, 61.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → command adapter → installer / study → installed bundle and private artifacts. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] One canonical learner skill/command is installed; setup, course/material intake, reporting and maintenance are operations within it. Obsolete public names and aliases are not delivered as wrappers.
- [x] A fresh installed journey remains usable after temporary public source downloads are removed, with explained setup choices and existing material-intake permissions preserved.
- [x] Existing course lessons, raw reports, mailbox originals, coverage and reviews remain usable; legacy data is not silently reorganized by installation.
- [x] Include any necessary command/installer prefactoring within this end-to-end slice, preserving existing meaningful regression checks.
- [x] Verify at S1 with a real temporary private workspace and an installed subprocess command; keep all fixtures synthetic and public/private isolation intact.

## Answer

The package and installer now deliver only `skills/invo-learn/SKILL.md` as the
learner skill. Setup, course intake, material intake and maintenance instructions
live in its internal `references/` directory, with existing explained questions,
actual conversion consent, private isolation and update/backup rules preserved.
The obsolete `add-track` command alias was removed; `add-course` remains the
course/standalone-track operation. README, generated workspace guidance and the
usage guide point to the canonical entry.

S1 verification extends `tests/test_onboarding.py`: install from a controlled
archive, verify temporary source removal, invoke installed subprocess commands
from an unrelated directory, intake an arbitrary-extension original, accept a
coverage map, prepare a lesson, ingest its exact return, inspect understanding
and review state, and verify originals/raw report/packet bytes remain preserved.
Single-skill delivery and obsolete-alias refusal were observed failing before
implementation, then passing. The accepted component view v0.1 and S1 remain
unchanged. The parent re-probed the local renderer and inspected the accepted view.

Validation: onboarding tests (7), complete unittest suite (106), and
`python examples/worked_example.py`. No learner layout conversion or real data
was involved. Release version publication is deferred to ticket 13.
