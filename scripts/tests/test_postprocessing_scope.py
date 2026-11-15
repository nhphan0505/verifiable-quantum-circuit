"""Exercise combined experiment/PP scope against real committed Git trees."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    'pp_scope_checker', Path(__file__).resolve().parents[2] / 'scripts/check_repo.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CombinedPostprocessingScope(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('scripts/check_repo.py', 'class Audit:\n    pass\n')
        self.write('src/common/postprocessing/METHODS.md', '| Method | Description |\n| --- | --- |\n')
        self.git('init')
        self.git('config', 'core.autocrlf', 'false')
        self.base = self.commit()

    def git(self, *args):
        return subprocess.check_output(
            ['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', *args],
            cwd=self.root, stderr=subprocess.PIPE).decode().strip()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8', newline='\n')

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-m', 'scope fixture')
        return self.git('rev-parse', 'HEAD')

    def add_method(self, scope='invsqrt'):
        self.path = f'src/{scope}/postprocessing/PP-007/solution.py'
        code = 'def rewrite(circuit):\n    return circuit\n'
        self.write(self.path, code)
        self.write(self.path.replace('solution.py', 'DESCRIPTION.md'), '# [PP-007] Method\n')
        self.write(self.path.replace('solution.py', 'tests/test_method.py'), '# semantic test fixture\n')
        digest = hashlib.sha256(code.encode()).hexdigest()
        self.manifest = {
            'postprocessing': {'method': 'PP-007', 'path': self.path, 'sha256': digest},
            'dependencies': [{'path': self.path, 'sha256': digest}],
        }
        self.save_manifest()
        self.write('src/common/postprocessing/METHODS.md',
                   '| Method | Description |\n| --- | --- |\n| PP-007 | Method |\n')

    def save_manifest(self):
        self.write('src/invsqrt/INV-123/reconstruction.json', json.dumps(self.manifest))

    def audit(self):
        audit = module.Audit(self.root)
        audit.scope(self.base, 'exp/INV-123-reconstruct')
        return audit.errors

    def test_declared_method_and_own_catalog_row_allowed(self):
        self.add_method()
        self.write('src/invsqrt/INV-123/solution.py', '"""Experiment."""\n')
        self.commit()
        self.assertEqual([], self.audit())

    def test_common_method_allowed(self):
        self.add_method('common')
        self.commit()
        self.assertEqual([], self.audit())

    def test_undeclared_method_rejected(self):
        self.add_method()
        self.manifest.pop('postprocessing')
        self.save_manifest()
        self.commit()
        self.assertTrue(any('outside its scope' in e for e in self.audit()))

    def test_other_method_rejected(self):
        self.add_method()
        self.write('src/invsqrt/postprocessing/PP-008/solution.py', '# unrelated\n')
        self.commit()
        self.assertTrue(any('PP-008' in e for e in self.audit()))

    def test_other_track_rejected(self):
        self.add_method('dqi')
        self.commit()
        self.assertTrue(any('same-track/common' in e for e in self.audit()))

    def test_dependency_hash_required(self):
        self.add_method()
        self.manifest['dependencies'] = []
        self.save_manifest()
        self.commit()
        self.assertTrue(any('matching dependency hash' in e for e in self.audit()))

    def test_committed_source_hash_required(self):
        self.add_method()
        self.write(self.path, '# changed without updating dependency pin\n')
        self.commit()
        self.assertTrue(any('hash differs from HEAD' in e for e in self.audit()))

    def test_working_tree_declaration_cannot_expand_scope(self):
        self.add_method()
        path = self.root / 'src/invsqrt/INV-123/reconstruction.json'
        data = path.read_text()
        path.unlink()
        self.commit()
        path.write_text(data)
        self.assertTrue(any('outside its scope' in e for e in self.audit()))

    def test_unrelated_catalog_row_rejected(self):
        self.add_method()
        with (self.root / 'src/common/postprocessing/METHODS.md').open('a') as f:
            f.write('| PP-008 | Unrelated method |\n')
        self.commit()
        self.assertTrue(any('outside declared PP rows' in e for e in self.audit()))

    def test_catalog_header_rejected(self):
        self.add_method()
        self.write('src/common/postprocessing/METHODS.md', '# Replaced catalog\n| PP-007 | Method |\n')
        self.commit()
        self.assertTrue(any('outside declared PP rows' in e for e in self.audit()))

    def test_unrelated_experiment_and_verifier_rejected(self):
        self.add_method()
        self.write('src/invsqrt/INV-999/solution.py', '# unrelated\n')
        self.write('verifiers/invsqrt/verify_submission_invsqrt.py', '# changed\n')
        self.commit()
        errors = self.audit()
        self.assertTrue(any('INV-999' in e for e in errors))
        self.assertTrue(any('verifiers/' in e for e in errors))

    def add_policy_upgrade(self):
        self.write('scripts/check_repo.py', 'class Audit:\n    def experiment_postprocessing(self):\n        pass\n')
        self.write('scripts/tests/test_postprocessing_scope.py', '# focused regression tests\n')
        self.write('docs/REPOSITORY_CHECKS.md', '# scope policy documentation\n')

    def test_legacy_policy_upgrade_has_bounded_scope(self):
        self.add_method()
        self.add_policy_upgrade()
        self.commit()
        self.assertEqual([], self.audit())

    def test_upgrade_does_not_allow_workflow_changes(self):
        self.add_method()
        self.add_policy_upgrade()
        self.write('.github/workflows/repo-checks.yml', '# unrelated workflow edit\n')
        self.commit()
        self.assertTrue(any('.github/workflows' in e for e in self.audit()))

    def test_upgrade_does_not_allow_arbitrary_tests(self):
        self.add_method()
        self.add_policy_upgrade()
        self.write('scripts/tests/test_other.py', '# unrelated\n')
        self.commit()
        self.assertTrue(any('test_other.py' in e for e in self.audit()))

    def test_infrastructure_rejected_once_base_supports_pp(self):
        self.add_policy_upgrade()
        self.base = self.commit()
        self.add_method()
        self.write('scripts/check_repo.py', '# another infrastructure change\n')
        self.commit()
        self.assertTrue(any('outside its scope: scripts/check_repo.py' in e for e in self.audit()))


if __name__ == '__main__':
    unittest.main()
