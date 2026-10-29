# Read older records without migrating

The installed invo-learn command can inspect historical course workspaces
(`state.json`, schema version 1) and assignment workspaces (`.invo/state.json`,
state version 1). No old skill or command installation is needed.

```text
python learn.py legacy-status <source-workspace>
python learn.py legacy-report <source-workspace> <returned-report-file>
```

These commands read the source and return JSON. They do not initialize it, change
its files, import learning evidence, install tooling, or convert its layout.
Use a source snapshot or the original workspace; keep returned files private.
Origin identity and available Git HEAD, original packet identities, pending
sessions, evidence and known artifact integrity problems are inspectable.

A report is associated with its exact issued packet, including the historical
solution revision for an assignment or lesson context for course study. A later
solution or plan change does not rewrite that association. Main and supplemental
returns remain distinct. An `associated` result means that the supported structure
and known artifact checks passed; it never proves correctness, independence or
retention and adds no progress.

`malformed`, `unresolved` and `invalid` results explain the problem and retain the
original file unchanged. Output includes its absolute location, exact byte count
and SHA-256; parsed data is included when possible. Obtain missing actual evidence
or restore damaged originals rather than guessing associations or answers.
Course returns may use a complete JSON code fence. Recorded hashes, byte counts,
required instruction files and snapshot metadata are checked where available;
old artifacts without a recorded digest cannot gain retrospective checksum proof.

Inspection is separate from deliberate migration. Explicit migration operations
must preserve complete repositories and working files, reconcile actual returns
or a recorded owner waiver, and validate the staged destination before activation.
