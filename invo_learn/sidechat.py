"""Side-chat coverage and assistance, separate from formal lesson reports."""
import copy
import json
import uuid

from .contracts import fields, identifier, require, string, strings


def template(lesson):
    return ({'assignment_context': copy.deepcopy(lesson['assignment_context'])} if 'assignment_context' in lesson else {}) | {'schema_version': 1, 'report_type': 'side-chat',
            'report_id': 'side-' + uuid.uuid4().hex[:12], 'lesson_id': lesson['id'],
            'track_id': lesson['track_id'], 'map_revision': lesson['map_revision'],
            'content_revision': lesson.get('content_revision', 0),
            'discussions': [], 'remaining_questions': [], 'assessment_help': []}


def instructions(lesson):
    return '''# Select a chat role

Use the same complete upload set in both chats. Opening with "Side chat" selects
the supplemental role below. "Go" or a request to teach START-HERE.md selects
the lesson role. Retain that role throughout this conversation. All lesson
assessment, progress-footer and main-report instructions apply ONLY to the lesson
role. Both roles use the assigned context and source attachments.

## Visual explanations in both roles

Favor useful UML: class diagrams for structures/relationships, sequence diagrams
for calls and callbacks, activity diagrams for control flow, and state diagrams
for lifecycles. Accompany diagrams with code and prose, using another representation
when clearer. Present relevant code/visual context before asking about it; keep
assessment reasoning for the learner. Label authored examples accurately and keep
the packet's source fidelity, uncertainty and assistance rules.

## Side-chat role

Answer learner-initiated clarifications, tangents and requests for depth without
starting the lesson, advancing checkpoints or claiming mastery. Direct explanations
or solutions are allowed when asked. Record help related to an assessed exercise
and whether it preceded the answer, followed it, or its timing is unknown. Preserve
actual learner responses when supplied; engagement is not independent assessment.

On request, return one supplemental JSON report using the exact template below.
Each discussion is {question, explanation, source_reference}, optionally with
learner_response and objective_ids (only known IDs; [] for unscoped tangents).
remaining_questions is a list of text descriptions. Each assessment_help item is
{objective_id, question, help, timing}, where timing is "before-answer",
"after-answer", or "unknown". Copy the exact exercise question where possible.
The template is empty of evidence. Preserve all identity/revision fields. Use a
distinct report_id for a new report and reuse it when returning the same report.
Return this separately from the main lesson report. Either report may arrive
first, including a late supplement. If the side chat is unused, no side report
is required. The planning agent combines context while preserving separate reports.

```json
''' + json.dumps(template(lesson), indent=2) + '\n```\n\n# Lesson role only\n\n'


def ingest(ws, obj, lesson, raw_path):
    from .engine import atomic, digest
    fields(obj, ('schema_version', 'report_type', 'report_id', 'lesson_id', 'track_id',
                 'map_revision', 'content_revision', 'discussions', 'remaining_questions', 'assessment_help'), ('assignment_context',))
    from .assignments import validate_report_context
    validate_report_context(obj, lesson)
    require(type(obj['schema_version']) is int and obj['schema_version'] == 1, 'unsupported supplemental schema')
    for key in ('report_id', 'lesson_id', 'track_id'):
        identifier(obj[key])
    require(obj['lesson_id'] == lesson['id'] and obj['track_id'] == lesson['track_id'], 'supplement does not match lesson/track')
    for key in ('map_revision', 'content_revision'):
        require(type(obj[key]) is int and obj[key] == lesson.get(key, 0), 'supplement revision does not match its issued lesson')
    require(isinstance(obj['discussions'], list) and obj['discussions'], 'supplement needs actual discussions')
    for item in obj['discussions']:
        fields(item, ('question', 'explanation', 'source_reference'), ('learner_response', 'objective_ids'))
        for key in ('question', 'explanation', 'source_reference'):
            string(item[key], key)
        if 'learner_response' in item:
            require(isinstance(item['learner_response'], str), 'actual learner response must be text')
        strings(item.get('objective_ids', []), 'discussion objectives')
        require(set(item.get('objective_ids', [])) <= set(lesson['objective_ids']), 'unknown discussion objective')
    strings(obj['remaining_questions'], 'remaining questions')
    require(isinstance(obj['assessment_help'], list), 'assessment_help must be a list')
    for item in obj['assessment_help']:
        fields(item, ('objective_id', 'question', 'help', 'timing'))
        require(item['objective_id'] in lesson['objective_ids'], 'unknown assessment-help objective')
        string(item['question'], 'exercise question')
        string(item['help'], 'help provided')
        require(item['timing'] in ('before-answer', 'after-answer', 'unknown'), 'invalid help timing')
    canonical = digest(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode())
    rid = obj['report_id']
    require(rid not in ws.state['reports'], 'report_id already belongs to a formal report')
    existing = ws.state.get('supplemental_reports', {}).get(rid)
    if existing:
        require(existing['sha256'] == canonical, 'supplemental report_id conflict; preserve the earlier report')
        return {'status': 'duplicate', 'report_id': rid}
    dest = ws.path('reports/supplemental/' + rid + '.json')
    atomic(dest, obj)
    ws.state.setdefault('supplemental_reports', {})[rid] = {
        'sha256': canonical, 'lesson_id': lesson['id'], 'track_id': lesson['track_id'],
        'path': dest.relative_to(ws.root).as_posix(), 'raw_path': raw_path.relative_to(ws.root).as_posix(),
        'report': copy.deepcopy(obj), 'evidence_level': 'covered'}
    # A side report never changes lesson status/report_id or the active packet.
    ws.recompute(lesson['track_id'])
    ws.save('side-report-ingested', {'report_id': rid, 'lesson_id': lesson['id']})
    return {'status': 'supplemental-recorded', 'report_id': rid, 'track_id': lesson['track_id']}


def qualify(ws, lesson_id, item):
    """Project known/uncertain prior help without editing original assessments."""
    result = copy.deepcopy(item)
    help_items = [h for r in ws.state.get('supplemental_reports', {}).values()
                  if r['lesson_id'] == lesson_id for h in r['report']['assessment_help']
                  if h['objective_id'] == item['objective_id'] and h['timing'] != 'after-answer']
    for attempt in result['assessments']:
        matches = [h for h in help_items if h['question'] == attempt['question']]
        if matches:
            attempt.update(independent=False, assistance='answer-revealed',
                           assistance_details='Side-chat assistance: ' + '; '.join(h['help'] for h in matches))
    return result


def project_coverage(ws, tid):
    track = ws.track(tid)
    for record in ws.state.get('supplemental_reports', {}).values():
        if record['track_id'] != tid:
            continue
        for discussion in record['report']['discussions']:
            for oid in discussion.get('objective_ids', []):
                objective = track['objectives'][oid]
                objective['coverage'] = 'covered'
        # Supplemental discussion alone establishes no understanding or retention.
