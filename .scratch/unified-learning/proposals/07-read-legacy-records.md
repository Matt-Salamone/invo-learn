# 07: Inspect older learning and assignment records through invo-learn

**Status:** needs-info

Draft proposal: awaiting approval of the breakdown. Publish after approval as ready-for-agent.

**What to build:** Use canonical commands to inspect older course/assignment snapshots and returned reports, including solution-revision-based packet associations, without installing old entry points or converting the source workspace.

**Blocked by:** 01 — Install and use the single invo-learn entry point.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 40, 49, 55.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → migration legacy readers → immutable legacy snapshots and report-context results. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Read the supported historical course and assignment record/report forms using synthetic fixtures representative of the existing formats.
- [ ] Return useful status, original identifiers, context associations and provenance without rewriting source bytes or creating learner progress.
- [ ] Resolve reports to exact original packets/revisions, retaining raw malformed or unresolved input for diagnosis; broken associations are never silently guessed.
- [ ] Do not require compatibility wrappers or old skill/command names.
- [ ] Verify read-only status/report inspection through S1 with before/after source hashes and installed commands.
