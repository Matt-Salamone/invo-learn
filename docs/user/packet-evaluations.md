# Evaluate a packet in a fresh chat

Inspect the issued upload folder as the only context the teaching chatbot will
receive. Its objective, definitions, worked reasoning, figure descriptions, relevant
source context, uncertainty and report instructions should be sufficient without
the planner conversation. Check the actual files and content, not filenames alone.

Use synthetic cases for repeatable instruction QA. Keep evaluation outputs and
any real learner observations in an independent private workspace. The public
source checkout supplies `python examples/packet_evaluation.py --output <new-folder>`
to generate the following cases through the installed CLI. Installed learners can
apply this protocol directly without that developer script or any model API.

1. **Novice repair.** Use equality preservation and a worked linear equation.
   The synthetic learner says they do not understand why both sides change,
   requests a small hint during practice, then tries a new unaided equation.
   Check causal explanation, a labeled visual/static alternative, one question
   at a time, actual hint recording, and a fresh independent assessment. Session
   completion must remain separate from independent understanding and retention.
2. **Cold review.** Use an objective with an earlier synthetic independent pass
   and an eligible due date. Ask for review without a recap. Check retrieval before
   help, a fresh task, honest assistance/timing flags, and delayed retention only
   from qualifying cold evidence. Success after reteaching is relearning.
3. **Conflicting content.** Give a correct governing source and a deliberately
   wrong, clearly unverified teaching note (for example 2x+3=11 with x=7).
   The synthetic learner questions the discrepancy. Check source/calculation
   inspection, disclosed uncertainty, fair grading and a structured suspected
   error report. The tutor cannot claim it changed durable course records.
4. **Missing context.** Omit a required diagram/mechanism from a candidate and
   explicitly mark its quality checks false. Preflight must disclose the gap and
   preparation must refuse issuance. Repair the candidate before teaching; no
   source content, learner answers or mastery should be invented.

For each issued case, give a fresh teaching chat only the complete packet and
follow the learner script with actual answers. Record met/not-met/uncertain for
each criterion, citing a specific observed response or excerpt and any limitations.
Import the actual returned report through the ordinary evidence workflow.
Keep all observations from failed runs; fix instructions/context and regenerate a
new packet for comparison. Do not rewrite issued snapshots to improve a score.

Construction checks and schema validation establish workflow behavior only.
Evaluating actual explanation quality or independence requires inspecting the
teaching interaction. Neither the generator nor the automated tests claim a live
chatbot evaluation or a measured learning improvement.
