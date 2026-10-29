# 12: Update the combined harness without silently migrating data

**Status:** resolved

Breakdown approved by the owner on October 29, 2026. Work only when the listed blockers are resolved.

**What to build:** Update a combined installation through the single maintenance entry point, distinguishing safe code/template updates from layout changes that require explicit migration.

**Blocked by:** 03 — Study a course-owned assignment without an upfront solution; 07 — Inspect older learning and assignment records through invo-learn.

**Spec:** [Unified learning and assignment workflows](../spec.md). User stories: 2, 50, 59.

**Diagrams:** accepted proposed-design component view v0.1 ([source](../unification-components-v01.puml), [SVG](../unification-components-v01.svg)); accepted timing view v0.3 ([source](../../../docs/design/assignment-modes-v03.puml), [SVG](../../../docs/design/assignment-modes-v03.svg)); accepted single-pending view v0.2 ([source](../../../docs/design/pending-boundaries-v02.puml), [SVG](../../../docs/design/pending-boundaries-v02.svg)).

**End-to-end path and verification seam:** S1 → installer / updater → installed bundle, compatibility outcome and preserved records. Use the accepted S1 public command workflow and assert returned outcomes plus preserved filesystem artifacts. Internal layout remains an implementation choice.

## Acceptance criteria

- [x] Compatible trusted updates preserve learner records, preferences, artifacts, opt-outs and existing backup/customization checks.
- [x] A release requiring a new learner-data layout reports the explicit migration requirement rather than silently reorganizing records.
- [x] Keep a usable compatible installation or demonstrate rollback when activation fails; do not prepare packets using stale code after an update succeeds.
- [x] Offline/unavailable checks stay truthful and do not prevent safe installed-version study or imply that an update was checked successfully.
- [x] Verify compatible, incompatible, customized, opted-out, unavailable and failed-update cases through installed S1 commands with controlled release responses.
- [x] Retain scoped backups to verified existing private remotes; no public learner publication, new remote, visibility change or forced history rewrite.
- [x] Protect checksum-bearing originals, issued packets, reports and installed
  bundle bytes from Git line-ending conversion in fresh workspaces and explicit
  maintenance/migration. Preserve existing custom attribute rules and verify a
  synthetic checkout/clone round trip; never silently rehash altered archives.

## Answer

Added optional workspace_layout metadata (older absence means layout 1) and
explicit migration-required results for layout/state-schema changes. Upgrade
checks the requirement before activation or record changes. Compatible trusted
updates validate the candidate, run its upgrader in a fresh source interpreter,
and prepare with newly active installed code. Existing preferences, opt-outs,
managed-file customization checks, immutable old releases and rollback remain.
Known generated AGENTS.md is refreshed through a safe literal read of the verified
old installer; custom guidance stays untouched. The same temporary setup helper
supports explicit --upgrade for older installed runners that cannot parse the
combined package, without editing their saved releases or adding old-name wrappers.

Added git_bytes.py and protect-record-bytes. New bootstrap and compatible
maintenance verify existing durable hashes, then install a scoped tracked
.gitattributes policy for sources, packets, reports, reference/legacy/migration
records and installed bundles. Existing custom rule bytes are retained with
attribute backups; conflicting effective rules are diagnosed and preserved.
Local attribute overrides are checked against portable rules without modifying
user Git configuration. Corrupted archives are refused, never silently rehashed.
Scoped backup validates working and staged rules, requiring the portable policy
in the reviewed commit. Existing private remote identity/visibility checks,
ordinary pushes and remote SHA verification are retained.

Twelve installed S1 maintenance journeys cover compatible/fresh-code updates,
layout and state-schema refusal without reorganization, offline/opt-out/customized
cases, download/activation failures and restored exports, explicit attributes,
custom root/local rules, no rehash of corrupt originals, and real autocrlf=true
clone/checkout hash equality. A scoped private-backup journey uses controlled
private metadata/local bare transport, rejects a scope missing .gitattributes,
then verifies the remote SHA and cloned bytes. The frozen public 0.7.0 fixture
(public code/docs/license only; commit 214178c) demonstrates an actual older
installation upgrading while its old bundle and preferences remain unchanged.

Validation passed: installed maintenance (12), workflow (54), automation (14),
updates (3), onboarding (7), and python examples/worked_example.py. The controlled
transport/fault tests do not claim live account permissions or network behavior.
Accepted S1/component v0.1 and complementary diagrams remain unchanged. Parent
owns map pointers, final module completeness after ticket 11, release version,
full integrated validation and the interaction push.
