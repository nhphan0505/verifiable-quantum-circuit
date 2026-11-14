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
        expected = {'_initialize_audit_affine': '0233bea0498f33abd589b0a9c8b9baae102ac8f650bcacce6b112d2e0f9b4c1b', '_initialize_postpass': '1ad3e98703ac6c124e9afad8407a15b51ce9c39eda0c0b155ba564344f629970'}
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
