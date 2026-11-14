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
        for name in ['src/invsqrt/INV-123/configs/test.json',
                     'artifacts/invsqrt/INV-123/test.kmb']:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('{}')

    def run_fake(self, interrupted=False, mode="full"):
        class Process:
            returncode = 0
            pid = 12345
            def __init__(self, cmd, **kwargs):
                kwargs['stdout'].write(json.dumps({'status': 'PASS', 'score': 1}))
                self.first = True
            def wait(self, timeout=None):
                if interrupted and self.first:
                    self.first = False
                    raise KeyboardInterrupt()
            def kill(self):
                self.returncode = -1
        with patch.object(grader.os, 'killpg', create=True), patch.object(grader.importlib.metadata, 'version', return_value='test'), patch.object(grader.subprocess, 'Popen', Process), patch.object(grader.sys, 'platform', 'linux'), patch.object(grader, 'runtime', return_value=(['python'], str(self.root))), patch.object(grader, 'preflight', return_value={'python': '3.13.14', 'packages': {'kickmix-engine': '0.6.0'}, 'platform': 'Linux', 'kernel': {'selected': 'baseline'}}):
            return grader.grade(self.root, 'invsqrt', 'INV-123', 'owner', 'test', mode=mode)

    def test_full_engine_records_runtime_and_default_options(self):
        out = self.run_fake()
        meta = json.loads((out / 'metadata.json').read_text())
        self.assertEqual(meta['engine']['version'], '0.6.0')
        self.assertEqual(meta['verify_command'][1:5], ['-m', 'kickmix_engine', 'verify', 'invsqrt'])
        self.assertNotIn('--max-x', meta['verify_command'])
        self.assertIsNone(meta['timeout_seconds'])
        self.assertNotIn('--max-workers', meta['verify_command'])
        self.assertEqual(meta['python'], '3.13.14')

    def test_smoke_uses_reduced_engine_options(self):
        out = self.run_fake(mode='smoke')
        meta = json.loads((out / 'metadata.json').read_text())
        self.assertEqual(meta['verification_level'], 'smoke')
        self.assertEqual(meta['verify_command'][-4:], ['--max-x', '4096', '--shots-per-x', '1'])
        self.assertEqual(out.parent.name, 'smoke')

    def test_dev_is_rejected_before_run(self):
        with self.assertRaises(ValueError):
            grader.grade(self.root, 'invsqrt', 'INV-123', 'owner', 'test', mode='dev_5min')
        self.assertFalse((self.root / 'results').exists())

    def test_output_layout_and_missing_provenance(self):
        out = self.run_fake()
        self.assertEqual(out.parent, self.root / 'results/invsqrt/INV-123/test/full')
        self.assertEqual(json.loads((out / 'metadata.json').read_text())['status'], 'PASS')
        self.assertTrue((out / 'review.json').is_file())

    def test_interruption_does_not_save_score(self):
        out = self.run_fake(interrupted=True)
        self.assertEqual(json.loads((out / 'metadata.json').read_text())['status'], 'INTERRUPTED')
        self.assertFalse((out / 'verifier.json').exists())

    def test_missing_config_never_creates_run(self):
        with self.assertRaises(FileNotFoundError):
            grader.grade(self.root, 'invsqrt', 'INV-123', 'owner', 'other')
        self.assertFalse((self.root / 'results').exists())

    def test_wrong_track_id_rejected(self):
        with self.assertRaises(ValueError):
            grader.grade(self.root, 'dqi', 'INV-123', 'owner', 'test')


if __name__ == '__main__':
    unittest.main()
