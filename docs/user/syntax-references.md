# Coding lesson syntax references

For every new lesson or review requiring the learner to write code, the planning
agent authors a standalone `syntax-cheatsheet.md` and includes it in the preserved
packet and shared flat mailbox. Omit it for lessons without coding. Decide from
the actual exercises, not merely an objective's kind or the presence of code in
a source. Keep the sheet within the saved attachment/size budget by combining or
reducing other context; never silently omit the reference or exceed the budget.

Include only language/API signatures, parameter meanings, return values,
constants and syntax that are not assessed memorization objectives. Select entries
from the lesson's actual sources and environment; verify uncertain signatures and
label version or access limitations. Exclude worked examples, solution skeletons,
application assembly instructions, lifecycle/dependency ordering and hints about
combining components. Review neutrality against the actual assessment tasks;
structural validation cannot establish that the content is safe or accurate.

Declare the sheet a permitted reference before coding assessments. Neutral lookup
does not count as assistance and does not prevent independent evidence of reasoning
and implementation. Both lesson and side chats follow this rule. Explanations,
solutions and task-specific hints beyond the sheet still count as assistance;
record their timing and preserve earlier failed/assisted attempts. Do not list
mere neutral lookup as assessment_help in a supplemental report. If memorization
itself is assessed, exclude the tested entries from the permitted reference.

New issuance specs explicitly set `coding` to true or false. For true, also supply
`syntax_cheatsheet` as the complete UTF-8 Markdown content, not a path; the builder
requires nonempty text and preserves the exact bytes as `syntax-cheatsheet.md`.
For false, omit `syntax_cheatsheet`. Legacy specs without either field retain their
behavior; the planning agent must classify new lessons explicitly. Resuming or
restaging a packet restores its issued bytes and never regenerates the reference.
Preserve historical packets, upload views, reports and identifiers. An in-progress
chat can receive a separately requested neutral reference without replacing its
packet, regrading past answers or changing its report identifiers.
