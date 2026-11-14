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
        expected = {'_initialize_relocate_cs2': '946318d7f9581b34d7d3103b32420943337518e8733b3eb8468df74c7cbc5b7b'}
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
