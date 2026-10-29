# Historical public package fixture

`invo-learn-0.7.0.zip` contains only the public distribution files from commit
`214178c` (VERSION, harness metadata, runtime, skills, user docs and the MIT license).
It is frozen to exercise an actual older installer/runtime without rewriting
that installed release. All learner workspaces created from it in tests are
synthetic and temporary. The ZIP has deterministic entry timestamps; it contains
no learner data, local configuration, credentials or repository metadata.
