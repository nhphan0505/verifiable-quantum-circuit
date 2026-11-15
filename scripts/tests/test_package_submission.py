"""Check shared packaging determinism, component bytes, and input rejection."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location(
    'package_submission', Path(__file__).resolve().parents[2] / 'src/common/package_submission.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.components = self.root / 'components'
        self.components.mkdir()
        for name in ['submission.npz', 'angle_k_0.kmb', 'angle_k_1.kmb']:
            (self.components / name).write_bytes(name.encode())

    def test_deterministic_and_preserves_components(self):
        a, b = self.root / 'a.zip', self.root / 'b.zip'
        first = module.package_dfthcsos(self.components, a)
        (self.components / 'angle_k_0.kmb').touch()
        second = module.package_dfthcsos(self.components, b)
        self.assertEqual(first['artifact_sha256'], second['artifact_sha256'])
        with zipfile.ZipFile(a) as z:
            self.assertEqual(set(first['component_sha256']), set(z.namelist()))
            for name in z.namelist():
                self.assertEqual(z.read(name), (self.components / name).read_bytes())
        with self.assertRaises(FileExistsError):
            module.package_dfthcsos(self.components, a)
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_gap_and_extra_rejected_without_output(self):
        output = self.root / 'out.zip'
        (self.components / 'angle_k_1.kmb').rename(self.components / 'angle_k_2.kmb')
        with self.assertRaises(ValueError):
            module.package_dfthcsos(self.components, output)
        self.assertFalse(output.exists())
        (self.components / 'angle_k_2.kmb').rename(self.components / 'angle_k_1.kmb')
        (self.components / 'notes.txt').write_text('not a component')
        with self.assertRaises(ValueError):
            module.package_dfthcsos(self.components, output)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
