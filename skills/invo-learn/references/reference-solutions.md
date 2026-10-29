# Verified reference solutions

Use this operation only after this assignment's explicit upfront-solution yes.
Read its governing requirements, deliverables, criteria and materials. Complete
the requested planner reference and actually verify it using appropriate tools
or inspected evidence. Preserve all generated artifacts. This is a planning
reference; the learner still edits/runs final work and the later implementation
guidance choice remains independent.

For each check record the actual method, observed result, evidence, governing
requirement/deliverable/criterion associations, and hashes of the exact artifacts
checked. Capture hashes before verification and confirm they are unchanged after
it; rerun affected checks after editing reference bytes. Record limitations and
unperformed checks honestly. Never substitute an expected output for an observed
one or mark unavailable checks passed.

Save a private JSON input and run:

```sh
python learn.py record-reference <course> <assignment> <private-reference.json>
```

The input has:

- `provenance`: actual author/source and verification circumstances.
- `artifacts`: nonempty entries `{id, file, description}`, where file identifies
  an existing generated artifact. The helper preserves exact original bytes and
  names in a new immutable revision, with original path and checksum provenance.
- `sections`: relevant readable excerpts `{id, artifact_id, start_line, end_line,
  purpose}`. Line numbers start at one and include both endpoints. The helper
  selects exact UTF-8 lines and hashes them; it does not invent a summary.
  Preserve opaque artifacts too, selecting readable context only where usable.
- `checks`: `{requirements, deliverables, criteria, method, result, evidence,
  artifact_sha256}`. The three association fields are string lists matching the
  assignment's exact declarations (each may be empty, but every check needs an
  association). result is `passed`, `failed` or `not-run`. method and evidence
  describe actual work/results or why it could not be performed.
  artifact_sha256 maps every artifact ID to the hash of the bytes checked.
- `limitations`: a string list describing remaining uncertainty or restricted
  verification scope. An empty list asserts no known limitations; do not hide
  missing tests there or pretend representative checks are exhaustive proof.

The helper validates associations and hashes and derives verified=true only when
all recorded checks pass and together cover every declared requirement,
deliverable and criterion. It preserves unverified revisions without permitting
reference-led planning. It records attestations; it does not execute command
strings supplied in data or independently prove their semantic claims. Actual
verification is the planning agent's responsibility.

For a changed reference, save a new revision with fresh checks. To identify a
correction add `correction_of` naming the current reference ID and a concrete
`correction_reason`. The manifest retains the earlier revision/hash, original
artifacts, checks and limitations. If the correction changes teaching or grading,
use the existing content concern/investigation/correction workflow in
`docs/user/quality-and-recovery.md` and review affected packets/evidence too.
Reference revision provenance does not replace that impact review.

## Reference-led plans and selected packets

After verification, propose/accept the assignment plan normally. Each planned
lesson additionally names a nonempty `reference_sections` list of relevant
section IDs. Choose only what grounds that lesson. The immutable plan pins the
reference ID, revision and manifest hash. Changing the active reference requires
a new plan, even when lesson titles and objectives stay the same. Preserve old
plans and issued packets.

The normal preflight and prepare commands verify reference manifests, artifact
bytes and selected section identity. Selected excerpts and documented limitations
are included as tutor context in the existing flat START-HERE.md; complete
reference artifact sets are not automatically attached. Existing material
reduction, source verification, neutral syntax sheets, quality checks and budget
measurements still apply. A selection is exact excerpting, not a claim that the
excerpt alone is a semantically complete explanation. Inspect the resulting
self-contained lesson and provide necessary conceptual context separately.

Main and side reports copy the resulting assignment_context.reference exactly,
including selected section hashes. Reference changes preserve old issued bytes
and report associations. A first main return using an older reference revision
is preserved and held for objective-specific relevance review before new credit;
that review does not rewrite the learner's original observations. Generating or
verifying a reference does not itself establish learner understanding or
retention, and selecting a reference does not mark the assignment complete.
