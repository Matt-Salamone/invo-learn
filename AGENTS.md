# Public invo-learn package

This checkout distributes tools, skills, contracts, documentation and synthetic
examples. Real learner data belongs in an independent private workspace, never
in this checkout or a public fork.

For a request to set up study using this repository, read
`skills/invo-learn-setup/SKILL.md` and follow it. For implementation, read
`docs/design/build-prompt.md` and `docs/design/requirements.md`.

The runtime uses Python's standard library (3.10+). Verify changes with
`python -m unittest discover -s tests -v` and `python examples/worked_example.py`.
Keep VERSION and CHANGELOG.md aligned; a distributed version is immutable.
Skills are portable instructions; never assume a particular agent/model API.
