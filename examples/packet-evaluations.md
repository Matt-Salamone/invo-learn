# Fresh-chat packet evaluation

Generate synthetic cases using only the installed CLI:

```sh
python examples/packet_evaluation.py
python examples/packet_evaluation.py --output /path/outside/public-checkout/evaluation-cases
```

The default verifies construction in a temporary directory and removes it.
`--output` retains new/empty output outside this checkout. Everything is synthetic;
do not replace fixtures with real learner material in the public project. No model
API, paid session or teaching host is required to generate cases.

The cases cover a novice needing a visual and a hint, a cold delayed review, a
conflict between correct source material and an unverified teaching note, and a
missing-context candidate that must be refused before issuance. The generated
`evaluation-cases.json` lists immutable packet folders, learner scripts and criteria.
The cold review uses explicitly synthetic dates, never real learner retention.

For actual instruction QA, use a separate fresh teaching conversation per issued
packet. Give the chatbot **only every file in the listed packet**, with no planner
history. Follow the learner script with actual answers and record the resulting
single report. Check each listed criterion against specific observed responses,
including whether the tutor knew all necessary context, asked an appropriate
independent question, recorded assistance, and disclosed suspected content errors.
Mark each criterion met/not-met/uncertain with an excerpt or observation explaining
the judgment. Keep the private evaluation record beside the generated case.

The missing-context case is a planner-only refusal check and has no teaching packet.
Repair its content and repeat preflight before requesting any real teaching.
When a generated packet exposes a quality problem, fix the source instructions or
packet builder and regenerate a new case; retain earlier observations for comparison.

Construction checks and report validation cannot score explanation quality, honest
independence or learning efficacy. Human/agent fresh-chat observations complement
the deterministic installed-CLI tests; no live teaching result is claimed by the
generator or the automated suite.
