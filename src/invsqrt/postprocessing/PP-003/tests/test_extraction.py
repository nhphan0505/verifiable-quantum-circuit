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
        expected = {'_initialize_merge_zpow': '2af80aa4a35673c14802c3eebde9d7325e2e0d0ca9a4961d27ee11fe89f64ec5'}
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
