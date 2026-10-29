# 04: Study an assignment from an explicitly requested verified reference

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Answer yes to the upfront-solution question, save the planner's worked reference with requirement checks, and issue a reference-led lesson whose report retains exact context lineage.

**Blocked by:** 03 — Study a course-owned assignment without an upfront solution.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 17, 18, 20, 32.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study → requested reference, verified context and reference-led lesson/report. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Reference-led planning requires the explicit yes and a saved, verified reference; verification records actual checks and limitations without inventing results.
- [x] Preserve reference artifacts, revisions, requirement associations and correction provenance.
- [x] Select relevant reference context instead of automatically attaching all solution artifacts. Retain flat-upload, preflight, attachment-budget, source-fidelity and verified-reduction guarantees.
- [x] Reference/plan changes do not mutate issued packets or detach later reports from their original context.
- [x] Verify the reference-led installed journey through S1, including rejection of premature planning and preserved no-reference behavior.

## Answer

Added `record-reference` and `invo_learn/reference_solution.py`. Only this
assignment's explicit yes authorizes saving a reference. Immutable revisions
preserve artifact bytes/names/checksums, requirement/deliverable/criterion
associations, actual verification methods/results/evidence, limitations, previous
revision links and explicit correction provenance. Check records bind to the
exact artifact hashes checked. Verification is derived from complete governing
coverage and passing checks; unchecked/failed/incomplete revisions remain saved
without authorizing reference-led planning. Actual check execution is performed
by the planning agent, not by executing command strings from input data.

Reference-led plans pin the verified reference ID/revision/manifest hash and
select named exact source-line excerpts. New references and explicit new solution
decisions produce new plan snapshots even for otherwise identical lesson specs.
The same preflight/prepare path counts selected excerpts/limitations rather than
automatically attaching complete solution sets. Packet and report contexts retain
selected excerpt hashes. Changed references do not rewrite earlier artifacts,
packets or report associations; first main returns using superseded references
are held for objective-specific relevance review before credit. Existing content
investigation/correction/impact review remains required for teaching/grading
errors, separately from revision provenance.

Offline doctor now verifies assignment snapshots, plans and every saved reference
manifest/artifact. Found and fixed a Windows fidelity defect: text writes doubled
embedded reference CRLFs. START-HERE now uses atomic UTF-8 byte writes, preserving
selected original line bytes while leaving issued archives immutable.

Also implemented the spec's explicit later solution-choice change with
`assignment-choice --new-decision`, stable decision IDs and append-only choice
history. Earlier references/plans and actual packet/help history remain intact;
a later no choice omits optional reference context without pretending older
references never existed. Ordinary resumes retain the existing answer.

Seven installed S1 tests cover premature/no-yes refusal, actual executed synthetic
checks, unchecked revisions, stale-check hashes, selected context/preflight parity,
exact CRLF fidelity, corrections/new-plan identity, late original reports,
integrity diagnostics/refusal, explicit later choice history, and verified
reference with both guided/independent implementation. After merging ticket 05,
validation passed: reference journeys (7), implementation (5), no-reference
assignments (4), workflow (54), side-chat (6), syntax references (4), targeted doctor
(1), and the worked example. Synthetic checks validate contracts, not live learner
independence or exhaustive program correctness. Accepted S1/component v0.1 and
complementary timing/pending views remain unchanged. Parent owns final release,
full integrated verification and map pointers.
