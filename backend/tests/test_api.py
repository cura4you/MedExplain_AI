import json
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend import main

client = TestClient(main.app)
COMPLETE = {'summary': 'A synthetic report explanation.', 'key_findings': ['No pleural effusion.'],
    'recommendations': ['Discuss the report with a clinician.'], 'disclaimer': 'Unsafe replacement notice.'}

class ApiTests(unittest.TestCase):
    def test_health(self):
        self.assertEqual(client.get('/health').json(), {'status': 'ok'})

    def test_all_six_report_types(self):
        with patch.object(main, 'AI_BASE_URL', 'https://provider.invalid'), patch.object(main, 'AI_MODEL', 'fixture'), patch.object(main, 'call_hosted_inference', return_value=json.dumps(COMPLETE)):
            for kind in ['radiology', 'lab', 'pathology', 'clinical', 'discharge', 'other']:
                result = client.post('/api/analyze', json={'report_text': ' Synthetic text. ', 'report_type': kind})
                self.assertEqual(result.status_code, 200)
                self.assertEqual(result.json()['source'], 'hosted_model')
                self.assertFalse(result.json()['parse_warning'])

    def test_validation_empty_whitespace_type_length(self):
        for data in [{}, {'report_text':'','report_type':'lab'}, {'report_text':'  \n ','report_type':'lab'},
                     {'report_text':'text','report_type':'invented'}, {'report_text':'x'*20001,'report_type':'lab'}]:
            self.assertEqual(client.post('/api/analyze', json=data).status_code, 422)

    def test_validates_and_strips_text(self):
        self.assertEqual(main.AnalyzeRequest(report_text=' report ',report_type='lab').report_text,'report')

    def test_disclaimer_cannot_be_replaced(self):
        r = main.parse_structured_response(json.dumps(COMPLETE), 'hosted_model')
        self.assertEqual(r.disclaimer, main.DISCLAIMER)

    def test_markdown_json(self):
        r = main.parse_structured_response('```json\n'+json.dumps(COMPLETE)+'\n```', 'hosted_model')
        self.assertFalse(r.parse_warning)

    def test_alias_multiline_and_bullets(self):
        r = main.parse_structured_response('**Overview:** First line.\nContinued summary.\nFindings:\n- No pleural effusion.\n- Heart size normal.\nNext steps:\n- Discuss with clinician.\nDisclaimer: Not medical advice.', 'fixture')
        self.assertEqual(r.summary, 'First line. Continued summary.')
        self.assertEqual(r.key_findings, ['No pleural effusion.', 'Heart size normal.'])
        self.assertFalse(r.parse_warning)

    def test_missing_summary_warns(self):
        self.assertTrue(main.parse_structured_response('Findings: incomplete', 'fixture').parse_warning)

    def test_missing_other_sections_warns(self):
        self.assertTrue(main.parse_structured_response('Summary: alone', 'fixture').parse_warning)

    def test_invalid_list_members_warns(self):
        self.assertTrue(main.parse_structured_response(json.dumps({**COMPLETE,'key_findings':[12,{}]}), 'fixture').parse_warning)

    def test_empty_lists_allowed(self):
        r=main.parse_structured_response(json.dumps({**COMPLETE,'key_findings':[], 'recommendations':[]}), 'fixture')
        self.assertEqual(r.key_findings, [])
        self.assertFalse(r.parse_warning)

    def test_output_bounds(self):
        r=main.parse_structured_response(json.dumps({**COMPLETE,'summary':'x'*7000,'key_findings':['x'*1100]*30}), 'fixture')
        self.assertTrue(r.parse_warning)
        self.assertEqual(len(r.summary),6000)
        self.assertEqual(len(r.key_findings),20)
        self.assertEqual(len(r.key_findings[0]),1000)

    def test_fallback_preserves_negation_in_quote(self):
        r=main.fallback_parse('No pleural effusion. No pneumonia.', 'radiology')
        self.assertEqual(r.source,'fallback')
        self.assertTrue(all('Text mention only' in x for x in r.key_findings))
        self.assertTrue(any('No pleural effusion.' in x for x in r.key_findings))
        self.assertIn('No medical interpretation', r.summary)

    def test_unknown_fallback_does_not_imply_normal(self):
        r=main.fallback_parse('Unrecognized words', 'other')
        self.assertEqual(r.key_findings,[])
        self.assertNotIn('no specific findings',r.summary)

    def test_word_boundaries(self):
        self.assertEqual(main.fallback_parse('Massachusetts protocol.', 'other').key_findings,[])

    def test_provider_failure_explicit_fallback(self):
        with patch.object(main, 'AI_BASE_URL', 'https://provider.invalid'), patch.object(main,'AI_MODEL','fixture'),patch.object(main,'call_hosted_inference',side_effect=TimeoutError('secret provider failure')):
            data=client.post('/api/analyze',json={'report_text':'No pneumonia.','report_type':'radiology'}).json()
            self.assertEqual(data['source'],'fallback')
            self.assertNotIn('secret',json.dumps(data))
            self.assertEqual(data['disclaimer'],main.DISCLAIMER)

    def test_hf_prompt_echo_removed(self):
        text='Synthetic input'; prompt=main.build_prompt(text,'lab')
        with patch.object(main,'AI_BASE_URL',''),patch.object(main,'MODEL_LOCAL_PATH',''),patch.object(main,'call_hf_inference',return_value=[{'generated_text':prompt+json.dumps(COMPLETE)}]):
            data=client.post('/api/analyze',json={'report_text':text,'report_type':'lab'}).json()
            self.assertEqual(data['summary'],COMPLETE['summary'])

    def test_non_string_provider_output_falls_back(self):
        with patch.object(main,'AI_BASE_URL',''),patch.object(main,'MODEL_LOCAL_PATH',''),patch.object(main,'call_hf_inference',return_value=[{'generated_text':123}]):
            self.assertEqual(client.post('/api/analyze',json={'report_text':'test','report_type':'lab'}).json()['source'],'fallback')

    def test_unconfigured_hf_does_not_call_network(self):
        with patch.object(main,'HF_INFERENCE_URL',''),patch.object(main.httpx,'Client') as network:
            with self.assertRaises(ValueError): main.call_hf_inference('prompt')
            network.assert_not_called()

    def test_invalid_local_path_fails_honestly(self):
        with patch.object(main,'MODEL_LOCAL_PATH','/missing/local/checkpoint'):
            self.assertEqual(client.post('/api/analyze',json={'report_text':'test','report_type':'lab'}).json()['source'],'fallback')

if __name__=='__main__': unittest.main()
