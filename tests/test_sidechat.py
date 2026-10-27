import copy
import json
import test_workflow as support
import unittest
from invo_learn.contracts import Invalid
from invo_learn.sidechat import template


class SideChatTests(unittest.TestCase):
    setUp = support.WorkflowTests.setUp
    prepare = support.WorkflowTests.prepare
    report = support.WorkflowTests.report
    ingest = support.WorkflowTests.ingest
    objective = support.WorkflowTests.objective

    def side_report(self, lesson):
        report = template(lesson)
        report['discussions'] = [{'question': 'Why does this work?', 'explanation': 'A synthetic explanation',
                                  'source_reference': 'Synthetic algebra source', 'objective_ids': ['solve']}]
        return report

    def test_side_only_keeps_lesson_pending_and_adds_no_mastery(self):
        lesson = self.prepare()
        side = self.side_report(lesson)
        result = self.ingest(side)
        self.assertEqual(result['status'], 'supplemental-recorded')
        self.assertEqual(self.ws.state['lessons'][lesson['id']]['status'], 'prepared')
        self.assertFalse(self.ws.state['reports'])
        self.assertEqual(self.objective()['coverage'], 'covered')
        self.assertEqual(self.objective()['understanding'], 'unassessed')
        self.assertIsNone(self.objective()['review'])

    def test_help_before_or_after_main_projects_same_result_without_rewriting(self):
        lesson = self.prepare()
        main = self.report(lesson)
        side = self.side_report(lesson)
        side['assessment_help'] = [{'objective_id': 'solve', 'question': main['objectives'][0]['assessments'][0]['question'],
                                    'help': 'Supplied the answer', 'timing': 'before-answer'}]
        self.ingest(main)
        before = copy.deepcopy(self.ws.state['reports'])
        self.assertEqual(self.objective()['understanding'], 'demonstrated')
        self.ingest(side)
        self.assertEqual(self.ws.state['reports'], before)
        self.assertNotEqual(self.objective()['understanding'], 'demonstrated')
        self.assertEqual(self.ws.state['lessons'][lesson['id']]['status'], 'reported')
        self.assertEqual(self.ingest(side)['status'], 'duplicate')
        side['discussions'][0]['explanation'] = 'Conflicting reuse'
        with self.assertRaisesRegex(Invalid, 'conflict'):
            self.ingest(side)

    def test_wrong_revision_rejected_and_raw_input_preserved(self):
        lesson = self.prepare()
        side = self.side_report(lesson)
        side['map_revision'] += 1
        with self.assertRaisesRegex(Invalid, 'revision'):
            self.ingest(side)
        self.assertFalse(self.ws.state.get('supplemental_reports'))
        self.assertTrue(list((self.root/'inbox/reports').glob('*.txt')))

    def test_role_setup_is_inside_existing_start_file(self):
        lesson = self.prepare()
        text = (self.ws.mailbox()/'START-HERE.md').read_text(encoding='utf-8')
        self.assertIn('"report_type": "side-chat"', text)
        self.assertIn(lesson['id'], text)
        self.assertFalse((self.ws.mailbox()/'side-chat.md').exists())

    def test_unknown_timing_before_main_blocks_independence(self):
        lesson = self.prepare()
        main = self.report(lesson)
        side = self.side_report(lesson)
        side['assessment_help'] = [{'objective_id': 'solve', 'question': main['objectives'][0]['assessments'][0]['question'],
                                    'help': 'Explained the exercise', 'timing': 'unknown'}]
        self.ingest(side)
        self.ingest(main)
        self.assertNotEqual(self.objective()['understanding'], 'demonstrated')
        self.assertEqual(len(self.ws.state['reports']), 1)

    def test_post_answer_explanation_preserves_independence_and_integrity_check(self):
        from invo_learn.workflow import doctor
        lesson = self.prepare()
        main = self.report(lesson)
        side = self.side_report(lesson)
        side['assessment_help'] = [{'objective_id': 'solve', 'question': main['objectives'][0]['assessments'][0]['question'],
                                    'help': 'Explained after the answer', 'timing': 'after-answer'}]
        self.ingest(main)
        self.ingest(side)
        self.assertEqual(self.objective()['understanding'], 'demonstrated')
        self.assertEqual(doctor(self.ws, '2026-10-14')['status'], 'healthy')
        archive = self.ws.state['supplemental_reports'][side['report_id']]['path']
        self.ws.path(archive).write_text('{}', encoding='utf-8')
        self.assertEqual(doctor(self.ws, '2026-10-14')['status'], 'needs-attention')
