"""Neutral reference packaging; content selection remains the planner's judgment."""


def prepare(spec):
    coding = spec.get('coding', False)
    if type(coding) is not bool:
        raise ValueError('coding must be a boolean')
    if not coding:
        if 'syntax_cheatsheet' in spec:
            raise ValueError('Omit syntax_cheatsheet for noncoding lessons')
        return None
    text = spec.get('syntax_cheatsheet')
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Coding lessons require nonempty syntax_cheatsheet Markdown')
    return text.encode('utf-8')


def instructions(has_reference):
    if not has_reference:
        return ''
    return """## Permitted syntax reference (both chat roles)

The attached syntax-cheatsheet.md is a permitted neutral reference during coding
assessments. Present it or the relevant entries before asking the learner to code.
Signatures, parameters, return values, constants and incidental syntax on this
sheet are not memorization objectives. Neutral lookup does not count as assistance
or prevent independent evidence; do not record lookup alone as assessment_help.
Assess reasoning and implementation. Explanations, solutions and task-specific
hints beyond the neutral sheet still count as assistance and retain their timing.
Do not add worked examples, solution skeletons, assembly instructions,
lifecycle/dependency ordering or component-combination hints to this reference.
Exclude any entry whose memorization is itself being assessed. If the sheet leaks
a task solution, withhold that entry and report the issue; do not call hinted work
independent. Preserve earlier evidence and all packet/report identifiers.

"""
