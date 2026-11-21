"""Check pinned-pack failure handling with small synthetic fixtures."""

import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

spec = spec_from_file_location("chemistry_pp", Path(__file__).resolve().parents[1] / "solution.py")
pp = module_from_spec(spec)
spec.loader.exec_module(pp)


class ChemistryPackTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.pack = self.root / "submission_final.pack"
        self.name = "dfthcsos/angle_k_0.kmb"
        self.member = b"loader bytes"
        with ZipFile(self.pack, "w") as archive:
            archive.writestr(self.name, self.member)
            archive.writestr("dqi.kmb", b"unrelated task")
        self.pack_hash = hashlib.sha256(self.pack.read_bytes()).hexdigest()
        self.output = self.root / "out.zip"

    def test_extracts_only_pinned_chemistry_members(self):
        with patch.object(pp, "MILESTONE_PACK_SHA", self.pack_hash), patch.object(
            pp, "EXPECTED_DFTHCSOS", {self.name: hashlib.sha256(self.member).hexdigest()}
        ):
            folder = pp.extract_milestone(self.pack, self.root)
        self.assertEqual([path.name for path in folder.iterdir()], ["angle_k_0.kmb"])
        self.assertEqual((folder / "angle_k_0.kmb").read_bytes(), self.member)
        self.assertEqual(hashlib.sha256(self.pack.read_bytes()).hexdigest(), self.pack_hash)

    def test_rejects_bad_pack_before_publishing(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            pp.apply(self.pack, self.output, verifier_data=self.root)
        self.assertFalse(self.output.exists())

    def test_rejects_bad_member_digest(self):
        with patch.object(pp, "MILESTONE_PACK_SHA", self.pack_hash), patch.object(
            pp, "EXPECTED_DFTHCSOS", {self.name: "0" * 64}
        ):
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                pp.extract_milestone(self.pack, self.root)

    def test_refuses_occupied_output(self):
        self.output.write_bytes(b"existing")
        with self.assertRaises(FileExistsError):
            pp.apply(self.pack, self.output, verifier_data=self.root)
        self.assertEqual(self.output.read_bytes(), b"existing")
