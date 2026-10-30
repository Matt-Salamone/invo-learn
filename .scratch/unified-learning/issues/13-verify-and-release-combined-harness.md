# 13: Verify and release the complete combined public harness

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Run the integrated installed product through all four assignment modes, sequential multi-course study and migration/recovery; finish public documentation and publish a versioned combined distribution only when the full contract passes.

**Blocked by:** 04 — Study an assignment from an explicitly requested verified reference; 11 — Activate, retry and recover an explicitly migrated workspace; 12 — Update the combined harness without silently migrating data.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 60, 61, 62.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → study / migration / installer → complete synthetic installed journey and immutable release. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Exercise reference/no-reference × guided/independent implementation with explicit question timing and unchanged historical exposure.
- [x] Run a two-track installed journey covering sequential handoffs, main/side reports, independent checks, delayed review, legacy rehearsal, report gates, activation and next study.
- [x] Run the required unittest suite, worked example and targeted installed-command journeys; teaching packet evaluations retain their documented limits.
- [x] Confirm only invo-learn is delivered as the learner entry point and all supported older records remain readable.
- [x] Review code/assets transferred from the public assignment product for license/attribution obligations; exclude all real learner data and credentials.
- [x] Keep VERSION and changelog aligned; publish a new immutable version rather than changing an already distributed version. Document setup, both choices, partial reporting, single checkout, migration and recovery.
- [x] Carry the accepted S1/component and complementary diagram references into the verification evidence; do not claim synthetic tests prove live account setup or learner independence.


## Answer

0.8.0 is published at [the immutable versioned release](https://github.com/Matt-Salamone/invo-learn/releases/tag/v0.8.0).
The parent verified all four Windows/Linux Python 3.10/3.13 CI jobs in
[run 40944655679](https://github.com/Matt-Salamone/invo-learn/actions/runs/40944655679),
fast-forwarded the existing main upstream, and verified its remote SHA and the
annotated tag's peeled target as `ad78efde560dfd595057b6e38a57b49ecb9e50d8`.
The release is published, neither draft nor prerelease. The 47-file canonical
payload exposes exactly one skill entry point. No distributed payload is changed
by this publication record.

The installed S1 workflow now closes both projected legacy-study actions and
reconciliation waiver needs through justified frozen links in new packets.
Known targets and prior linked targets are retained across subset handoffs.
Actual effective fresh independent evidence must support every target; partial
progress and history survive. Withdrawals, prior-help qualification or actual
later contradictory failures can reopen needs. Unassessed/withdrawn later work
preserves earlier valid proof. Imported labels never become fresh proof.

Public package text is canonical LF at packaging only. Equivalent LF/CRLF sources
produce the same version payload and maintenance result. Every runtime module,
including activation, late ingest, package entry files and migration-study code,
is required before install, as is the MIT license. Learner originals, old
bundles, raw reports and issued packets keep exact bytes.

Review reproduced and repaired an activation integrity gap: unchanged baseline
files omitted from the write journal are now checked at resume and before
finalization. Changed/missing originals stop cutover without overwriting the
new work; unrelated newly added files survive. Checks exclude Git internals,
operation locks and Python caches. Public documentation and the single portable
skill cover choice timing, partial sessions, migration/recovery, waived progress,
late returns and follow-up fresh study.

Verification uses the accepted S1/component v0.1, choice timing v0.3 and pending
boundary v0.2. The first integrated candidate passed 192 tests in 576.098 seconds;
review fixes require the final integrated recheck recorded below. Worked example
passed, and packet evaluation produced four synthetic cases (three prepared,
one correctly refused), with teaching_evaluated=false.

No invo-assignment helper implementation/assets were transplanted; the older
format readers were authored for this harness. The source distribution and its
own frozen 0.7.0 public fixture carry MIT licensing. All fixtures are synthetic.
No live learner records, chatbot efficacy/independence, paid service, hosted
private-remote creation or live unreleased archive download was tested.


A further installed regression reproduced late course supplements being intercepted
as historical after an actual main report had already been reconciled. Valid late
supplements now reach the normal side-chat projection after exact association
checks, so prior/unknown help qualifies the credited original and after-answer
explanations preserve independence. Exact reconciled main duplicates stay normal
duplicates. Waived course and legacy assignment returns remain historical with no
new credit or reopened slot. The original main archive/raw bytes remain unchanged.


## Final verification — ready for publication

Candidate `b1c2dbd` passed `python -m unittest discover -s tests -v`:
**197 tests, none skipped, 635.782 seconds**, Windows/Python 3.14. Targeted
activation/recovery tests passed 14/14 (143.272 seconds), side-chat 6/6
(3.649 seconds), and migration fresh-study 4/4 (49.466 seconds). The latter
projection code is unchanged in the final candidate and all four are included
in the full run. Both `python examples/worked_example.py` and
`python examples/packet_evaluation.py` passed on the final code.

The parent verified separate standards/spec reviews; the identified issues were
reproduced through installed S1 commands and repaired before this final run.
VERSION and CHANGELOG.md agree on 0.8.0. The parent owns verified publication,
release CI and marking this ticket resolved after publication. No learner data,
map edit, remote change, push, release tag or publication was made by this worker.

## Published patch verification — October 30, 2026

Cutover verification found that the generated overview retained the temporary
activation candidate's mailbox even though final state had the correct live
mailbox. The installed-command regression reproduced the defect before repair.
The final-state overview and coverage views now enter the checked candidate
before its journal inventory is frozen, retaining journal recovery and state-last
completion. Direct activation, interruption/resume, external mailboxes and
already-active retries are covered.

Published immutable [v0.8.1](https://github.com/Matt-Salamone/invo-learn/releases/tag/v0.8.1)
at `d82cbfc454742aca9bee529b5e223e303c85e64f`; main and the annotated tag's peeled
target were verified. VERSION and CHANGELOG agree. All four Windows/Linux
Python 3.10/3.13 jobs passed in
[CI 41040858839](https://github.com/Matt-Salamone/invo-learn/actions/runs/41040858839).
Local full suite: **197 tests, none skipped, 624.101 seconds**; all 14 targeted
activation checks and both examples passed. Separate standards and specification
reviews each reported zero findings. The downloaded public archive's 47 packaged
hashes match the reviewed manifest; only VERSION and the activation module differ
from 0.8.0. The published 0.8.0 payload is unchanged.
