# 07: Inspect older learning and assignment records through invo-learn

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Use canonical commands to inspect older course/assignment snapshots and returned reports, including solution-revision-based packet associations, without installing old entry points or converting the source workspace.

**Blocked by:** 01 — Install and use the single invo-learn entry point.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 40, 49, 55.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → migration legacy readers → immutable legacy snapshots and report-context results. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Read the supported historical course and assignment record/report forms using synthetic fixtures representative of the existing formats.
- [x] Return useful status, original identifiers, context associations and provenance without rewriting source bytes or creating learner progress.
- [x] Resolve reports to exact original packets/revisions, retaining raw malformed or unresolved input for diagnosis; broken associations are never silently guessed.
- [x] Do not require compatibility wrappers or old skill/command names.
- [x] Verify read-only status/report inspection through S1 with before/after source hashes and installed commands.


## Answer

Implemented original read-only readers in invo_learn/legacy.py and installed canonical legacy-status/legacy-report commands. They retain source identity and available origin commit, resolve exact historical packet/revision associations, validate known artifacts and hashes, and diagnose malformed, unresolved or invalid returns without modifying source records or adding progress. See docs/user/legacy-records.md.

Validation: python -m unittest discover -s tests -p test_legacy.py -v — 8 installed S1 tests pass, including before/after filesystem hashes, course fenced main returns, both supplemental forms, old solution revisions, wrong identifiers, malformed returns and missing/damaged packet originals. Reused accepted component v0.1 / S1 and complementary timing v0.3 and pending v0.2 views. No legacy helper code copied; no learner data used.
