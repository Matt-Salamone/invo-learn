# 12: Update the combined harness without silently migrating data

**Status:** ready-for-agent

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Update a combined installation through the single maintenance entry point, distinguishing safe code/template updates from layout changes that require explicit migration.

**Blocked by:** 03 — Study a course-owned assignment without an upfront solution; 07 — Inspect older learning and assignment records through invo-learn.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 2, 50, 59.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → installer / updater → installed bundle, compatibility outcome and preserved records. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [ ] Compatible trusted updates preserve learner records, preferences, artifacts, opt-outs and existing backup/customization checks.
- [ ] A release requiring a new learner-data layout reports the explicit migration requirement rather than silently reorganizing records.
- [ ] Keep a usable compatible installation or demonstrate rollback when activation fails; do not prepare packets using stale code after an update succeeds.
- [ ] Offline/unavailable checks stay truthful and do not prevent safe installed-version study or imply that an update was checked successfully.
- [ ] Verify compatible, incompatible, customized, opted-out, unavailable and failed-update cases through installed S1 commands with controlled release responses.
- [ ] Retain scoped backups to verified existing private remotes; no public learner publication, new remote, visibility change or forced history rewrite.
