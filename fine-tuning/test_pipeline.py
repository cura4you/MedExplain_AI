import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent

def run(script,*args):
    return subprocess.run([sys.executable,str(ROOT/'fine-tuning'/script),*args],cwd=ROOT,capture_output=True,text=True)

class PipelineTests(unittest.TestCase):
    def test_deterministic_disjoint_case_split_and_requested_size(self):
        with tempfile.TemporaryDirectory() as directory:
            a=Path(directory)/'a';b=Path(directory)/'b'
            for out in [a,b]:
                self.assertEqual(run('prepare_data.py','--total','120','--eval-ratio','0.2','--output-dir',str(out)).returncode,0)
            for name in ['train_data.jsonl','eval_data.jsonl']:
                self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())
            train=[json.loads(x) for x in (a/'train_data.jsonl').read_text().splitlines()]
            evaluation=[json.loads(x) for x in (a/'eval_data.jsonl').read_text().splitlines()]
            self.assertEqual(len(train)+len(evaluation),120)
            self.assertEqual(len({r['report_type'] for r in train}),6)
            self.assertEqual(len({r['report_type'] for r in evaluation}),6)
            result=run('validate_data.py','--train-path',str(a/'train_data.jsonl'),'--eval-path',str(a/'eval_data.jsonl'),'--output-path',str(a/'validation.json'))
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads((a/'validation.json').read_text())['cross_split_template_case_overlap'],0)

    def test_cross_type_reordered_cases_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory)
            completion='Summary: test\nKey findings: test\nRecommendations: test\nDisclaimer: test'
            train={'prompt':'User report type: lab\nUser report text: The report notes anemia and edema.','completion':completion,'report_type':'lab'}
            evaluation={'prompt':'User report type: radiology\nUser report text: The report notes edema and anemia.','completion':completion,'report_type':'radiology'}
            (d/'train').write_text(json.dumps(train)+'\n');(d/'eval').write_text(json.dumps(evaluation)+'\n')
            result=run('validate_data.py','--train-path',str(d/'train'),'--eval-path',str(d/'eval'),'--output-path',str(d/'report.json'))
            self.assertNotEqual(result.returncode,0)
            r=json.loads((d/'report.json').read_text())
            self.assertEqual(r['cross_split_overlap'],0)
            self.assertEqual(r['cross_split_template_case_overlap'],1)
            self.assertFalse(r['passed'])

    def test_invalid_generation_args_rejected(self):
        for args in [('--total','-1'),('--eval-ratio','1'),('--eval-ratio','0')]:
            self.assertNotEqual(run('prepare_data.py',*args).returncode,0)

    def test_old_evaluation_command_does_not_claim_model_run(self):
        result=run('evaluate_model.py')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('did not run a model',result.stderr)

    def test_reference_metrics_identify_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'metrics.json'
            result=run('dataset_metrics.py','--output-path',str(output))
            self.assertEqual(result.returncode,0)
            data=json.loads(output.read_text())
            self.assertFalse(data['model_inference_performed'])
            self.assertIn('Reference completion',data['scope'])

if __name__=='__main__':unittest.main()
