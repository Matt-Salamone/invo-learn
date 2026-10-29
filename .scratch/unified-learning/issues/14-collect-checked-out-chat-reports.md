# 14: Collect in-progress reports from every checked-out lesson chat

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved. Actual learner chat returns are required.

**What to build:** Before final private cutover, the learner visits every checked-out lesson chat, requests an in-progress report, and returns it to the planning agent. The agent preserves the exact returns privately for the migration gate.

**Blocked by:** None (can start immediately).

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 52, 53.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** Learner lesson chats → actual report returns → private saved inputs for S1 reconciliation. This is an external human prerequisite, not an implementation slice; S1 validates its actual returns before cutover.

## Acceptance criteria

- [ ] Remind the learner to obtain reports from every checked-out main lesson chat across the source workspaces; this can begin while public implementation proceeds.
- [ ] Require actual chatbot returns. Do not author substitute learner answers, reconstruct missing assessments as facts or mark unfinished sessions complete.
- [ ] Save returned reports only in the verified private workspace; this public ticket contains no report contents, private inventory or materials.
- [ ] Keep the prerequisite unresolved while any checked-out chat's required report is missing. Machine validation and reconciliation are performed by tickets 10 and 15.
- [ ] This prerequisite requires actual human chat returns, not an AFK code task; an implementation agent must wait rather than fabricate completion.

## Comments

October 29, 2026 implementation run: reminded the owner to obtain actual
in-progress reports from every checked-out main lesson chat and retain the
returns privately. This public ticket remains unresolved; no private reports or
inventory have been supplied to this implementation run.

## Answer

October 29, 2026: the owner explicitly waived collecting lesson-chat returns,
accepted loss of unreported progress and authorized autonomous reconciliation.
This human prerequisite is resolved by that decision, not by receipt of reports.
Tickets 10 and 15 must preserve existing evidence/artifacts, record the waiver,
retire missing-return checkouts as incomplete and arrange fresh checks or
relearning where needed. Do not fabricate reports, answers or completion. The
spec's owner revision supersedes the original mandatory-return criteria above.
