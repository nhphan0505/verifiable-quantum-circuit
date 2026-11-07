"""Check CI rejects PDF/link-only resource directories, across all tracks."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('research_notes', ROOT / 'scripts/check_research_notes.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ResearchNotes(unittest.TestCase):
    def setUp(self):
        base = ROOT / 'artifacts'
        base.mkdir(exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def resource(self, track, kind, name):
        path = self.root / 'research' / track / kind / name
        path.mkdir(parents=True)
        return path

    def test_pdf_only_and_link_only_rejected(self):
        paper = self.resource('invsqrt', 'papers', 'arxiv-2308.12352')
        (paper / 'paper.pdf').write_bytes(b'PDF fixture')
        discussion = self.resource('dqi', 'discussions', 'decoder')
        (discussion / 'source.json').write_text('{"source_url":"https://example.org/discussion"}')
        self.assertEqual(2, len(module.check(self.root)))

    def test_empty_or_wrong_filename_rejected(self):
        source = self.resource('shared', 'discussions', 'qrom')
        (source / 'source.md').write_text('Discussion snapshot')
        self.assertEqual(1, len(module.check(self.root)))
        (source / 'note.md').write_text('  \n')
        self.assertTrue(any('empty' in error for error in module.check(self.root)))

    def test_notes_for_all_tracks_pass(self):
        for track in ('invsqrt', 'dqi', 'dfthcsos', 'shared'):
            for kind in ('papers', 'discussions'):
                source = self.resource(track, kind, 'resource')
                (source / 'note.md').write_text('# Note\nContent with evidence.', encoding='utf-8')
        self.assertEqual([], module.check(self.root))

    def test_loose_resources_rejected_but_placeholders_allowed(self):
        parent = self.root / 'research/shared/papers'
        parent.mkdir(parents=True)
        (parent / '.gitkeep').touch()
        self.assertEqual([], module.check(self.root))
        (parent / 'loose.pdf').write_bytes(b'PDF fixture')
        self.assertEqual(1, len(module.check(self.root)))
