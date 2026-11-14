"""Compare extracted finishing passes with a pre-migration INV-51 build.

Set INV51_REFERENCE_BUILD to the original build directory to run this optional
integration test. It needs its raw/final intermediates, pinned Kickmix runtime,
and several minutes. Outputs live only in a TemporaryDirectory; no grading or
experiment records are written. Run unittest discover in this directory.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]


@unittest.skipUnless(os.environ.get('INV51_REFERENCE_BUILD'), 'requires original build intermediates')
class PipelineTests(unittest.TestCase):
    def test_exact_finishing_pipeline(self):
        reference = Path(os.environ['INV51_REFERENCE_BUILD']).resolve()
        engine = ROOT / 'src/invsqrt/INV-51/circuit.py'
        with tempfile.TemporaryDirectory(prefix='inv51-pp-refactor-') as directory:
            output = Path(directory)

            def run(stage, *args):
                completed = subprocess.run(
                    [sys.executable, '-X', 'utf8', str(engine), stage, *map(str, args)],
                    capture_output=True, timeout=600,
                    env={**os.environ, 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1',
                         'OPENBLAS_NUM_THREADS': '1'})
                self.assertEqual(completed.returncode, 0,
                                 completed.stdout.decode('utf-8', errors='replace') +
                                 completed.stderr.decode('utf-8', errors='replace'))
                print('Completed:', stage, flush=True)

            def compare(name, original):
                self.assertEqual((output/name).read_bytes(),
                                 (reference/'final'/original).read_bytes(), name)
                print('EXACT:', name, flush=True)

            run('tools/hold_pass.py', reference/'raw/raw.kmx',
                reference/'final/s1.pairs.json', '--out', output/'hold.kmx', '--Q', 46)
            compare('hold.kmx', 's2.kmx')
            run('tools/postpass.py', output/'hold.kmx', reference/'final/r1.audit.json',
                '--out', output/'rewrite.kmx')
            compare('rewrite.kmx', 'r1.kmx')
            run('tools/merge_zpow.py', output/'rewrite.kmx', '--out', output/'zpow.kmx')
            compare('zpow.kmx', 'zpow.kmx')
            run('agents/micro47/scripts/relocate_cs2.py', output/'zpow.kmx', output/'final.kmx')
            compare('final.kmx', 'final_text.kmx')
            run('tools/kmx_to_kmb.py', output/'final.kmx', '--out', output/'final.kmb')
            self.assertEqual(hashlib.sha256((output/'final.kmb').read_bytes()).hexdigest(),
                             '321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177')
