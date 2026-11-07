"""Check local grading orchestration with synthetic files and a fake verifier.

These tests exercise path selection, ZIP rejection, timeout evidence and output
layout without simulating a circuit or changing actual research results.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('local_grade', REPO / 'src/common/local_grade.py')
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)


class LocalGrading(unittest.TestCase):
    def setUp(self):
        base = (REPO / 'artifacts').resolve()
        base.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.temp.name).resolve()
        assert self.root.parent == base
        self.addCleanup(self.temp.cleanup)
        for name in ['src/common/dev_verify.py', 'src/invsqrt/INV-123/configs/test.json',
                     'artifacts/invsqrt/INV-123/test.kmb']:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('{}')

    def run_fake(self, timeout=False):
        class Process:
            returncode = 0
            def __init__(self, cmd, **kwargs):
                kwargs['stdout'].write(json.dumps({'status': 'PASS', 'score': 1}))
                self.first = True
            def wait(self, timeout=None):
                if timeout and self.first:
                    self.first = False
                    raise subprocess.TimeoutExpired('fake', timeout)
            def kill(self):
                self.returncode = -1
        with patch.object(grader.importlib.metadata, 'version', return_value='test'), patch.object(grader.subprocess, 'Popen', Process):
            return grader.grade(self.root, 'invsqrt', 'dev_5min' if timeout else 'smoke', 'INV-123', 'owner', 'test')

    def test_output_layout_and_missing_provenance(self):
        out = self.run_fake()
        self.assertEqual(out.parent, self.root / 'results/invsqrt/INV-123/test/smoke')
        self.assertEqual(json.loads((out / 'metadata.json').read_text())['status'], 'PASS')
        self.assertTrue((out / 'review.json').is_file())

    def test_timeout_does_not_save_score(self):
        out = self.run_fake(timeout=True)
        self.assertEqual(json.loads((out / 'metadata.json').read_text())['status'], 'TIMEOUT')
        self.assertFalse((out / 'verifier.json').exists())

    def test_missing_config_never_creates_run(self):
        with self.assertRaises(FileNotFoundError):
            grader.grade(self.root, 'invsqrt', 'smoke', 'INV-123', 'owner', 'other')
        self.assertFalse((self.root / 'results').exists())

    def test_wrong_track_id_rejected(self):
        with self.assertRaises(ValueError):
            grader.grade(self.root, 'dqi', 'smoke', 'INV-123', 'owner', 'test')


if __name__ == '__main__':
    unittest.main()
