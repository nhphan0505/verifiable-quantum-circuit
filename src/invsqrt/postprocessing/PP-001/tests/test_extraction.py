"""Guard unchanged extracted algorithms and reject unsupported stages."""
import ast
import hashlib
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('extracted_pp', HERE / 'solution.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ExtractionTests(unittest.TestCase):
    def test_algorithm_unchanged(self):
        tree = ast.parse((HERE / 'solution.py').read_text(encoding='utf-8'))
        expected = {'_initialize_audit_pairs': '96d1af6d84810ba98e4d2717b36fe064c7d71f0968178e33089b6b734198598e', '_initialize_hold_pass': '19fe3716809f94bdd44a49e88ab8ab1ad08ea67d4db83b5d8bb02c94bfc4d99a'}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in expected:
                self.assertEqual(hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest(), expected.pop(node.name))
        self.assertFalse(expected)

    def test_unknown_stage_rejected(self):
        with self.assertRaises(ValueError):
            module.run(None, 'not-a-stage', [])

    def test_unknown_factory_rejected(self):
        with self.assertRaises(ValueError):
            module.initialize({}, 'not-a-factory')
