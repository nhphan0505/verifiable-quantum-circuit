"""Exercise standalone byte preservation and rejection without a large release KMB."""

import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
import unittest

import kickmix

spec = spec_from_file_location("passthrough", Path(__file__).resolve().parents[1] / "solution.py")
pp = module_from_spec(spec)
spec.loader.exec_module(pp)


class PassThroughTests(unittest.TestCase):
    def setUp(self):
        folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.source = folder / "input.kmb"
        self.output = folder / "output.kmb"
        kickmix.Circuit("X q0\n").to_file(self.source, format="kmb")
        self.original = self.source.read_bytes()
        self.digest = hashlib.sha256(self.original).hexdigest()

    def test_publishes_exact_circuit(self):
        self.assertEqual(pp.apply(self.source, self.output, expected_sha256=self.digest), self.digest)
        self.assertEqual(self.output.read_bytes(), self.original)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_rejects_wrong_digest_without_output(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            pp.apply(self.source, self.output, expected_sha256="0" * 64)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_refuses_existing_output(self):
        self.output.write_bytes(b"existing")
        with self.assertRaises(FileExistsError):
            pp.apply(self.source, self.output, expected_sha256=self.digest)
        self.assertEqual(self.output.read_bytes(), b"existing")

    def test_rejects_malformed_digest(self):
        with self.assertRaisesRegex(ValueError, "64 lowercase"):
            pp.apply(self.source, self.output, expected_sha256="bad")
        self.assertFalse(self.output.exists())
