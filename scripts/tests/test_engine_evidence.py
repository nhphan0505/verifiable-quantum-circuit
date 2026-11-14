"""Engine records must retain the official full problem and verifier identity."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('engine_audit', Path(__file__).resolve().parents[1] / 'check_repo.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EngineEvidence(unittest.TestCase):
    def audit(self, options=(), version='0.6.0'):
        with tempfile.TemporaryDirectory() as directory:
            audit = module.Audit(directory)
            meta = {'engine': {'name': 'kickmix-engine', 'version': version},
                    'verify_command': ['python', '-m', 'kickmix_engine', 'verify', 'dqi', 'test.kmb',
                                       '--verifier', '/repo/verifiers/dqi/verify_submission_dqi.py',
                                       '--threads', '4', *options]}
            result = dict(status='PASS', verified_shots=102400, m=4095, n=70, degree=12, r=2016, log2_delta=-128)
            audit.evidence(Path(directory), 'dqi', 'full', meta, result)
            return audit.errors

    def test_full_engine_accepted(self):
        self.assertEqual(self.audit(), [])

    def test_reduced_profile_rejected_as_full(self):
        self.assertTrue(any('non-official full setting' in e for e in self.audit(['--num-shots', '4096'])))

    def test_unpinned_engine_rejected(self):
        self.assertTrue(any('identity' in e for e in self.audit(version='0.7.0')))
