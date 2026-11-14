"""Regression checks for malformed records and PR scope without circuit builds.

Fixtures copy only small repository documents/source/records into an isolated,
ignored workspace. Tests alter fixture data, including real Git snapshots, to
confirm the audit rejects incorrect scores, metadata and provenance hashes.
Run python -m unittest discover -s scripts/tests -v from the repository root.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_repo', REPO / 'scripts/check_repo.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RepositoryChecks(unittest.TestCase):
    def setUp(self):
        base = (REPO / 'artifacts').resolve()
        base.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.root = Path(self.temp.name).resolve()
        assert self.root.parent == base
        self.addCleanup(self.temp.cleanup)
        for folder in ['src', 'scripts', 'results', 'verifiers', 'docs', 'instructions', 'templates', 'notebooks', 'research']:
            for source in (REPO / folder).rglob('*'):
                if source.is_file() and source.suffix in {'.py', '.md', '.json', '.ipynb', '.txt', '.pdf'}:
                    target = self.root / source.relative_to(REPO)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
        for source in list(REPO.glob('*.md')) + [REPO / 'data_manifest.json']:
            shutil.copyfile(source, self.root / source.name)
        for filename in ['requirements.txt', '.python-version']:
            shutil.copyfile(REPO / filename, self.root / filename)
        # Root docs link to these files/directories, too.
        shutil.copytree(REPO / '.github', self.root / '.github')
        self.audit = module.Audit(self.root)

    def test_research_note_identity_and_hash(self):
        folder = self.root / 'research/dqi/discussions/decoder-errors'
        folder.mkdir(parents=True)
        (folder / 'source.md').write_text('Discussion snapshot', encoding='utf-8')
        note = folder / 'note.md'
        note.write_text('# Decoder errors\nStatus: draft\nTrack: dqi\nSource: internal snapshot\nVersion: 2026-11-07\n', encoding='utf-8')
        source = dict(track='dqi', kind='discussions', source_id='decoder-errors', title='Decoder errors',
                      version='2026-11-07', accessed_at='2026-11-07', coverage='Full supplied thread',
                      source_file='source.md', source_sha256=hashlib.sha256((folder / 'source.md').read_bytes()).hexdigest())
        (folder / 'source.json').write_text(json.dumps(source))
        self.audit.research()
        self.assertEqual([], self.audit.errors)
        # A project snapshot must hash Git blobs, not CRLF checkout bytes.
        source['project_snapshot'] = {'commit': 'a' * 40, 'files': {'src/example.py': hashlib.sha256(b'line\n').hexdigest()}}
        (folder / 'source.json').write_text(json.dumps(source))
        self.audit.git_available = True
        real_repository = module.Audit(REPO)
        self.audit.git = lambda *args: (b'line\n' if args == ('show', 'a' * 40 + ':src/example.py')
                                       else real_repository.git(*args))
        self.audit.research()
        self.assertEqual([], self.audit.errors)
        source['project_snapshot']['files']['src/example.py'] = hashlib.sha256(b'line\r\n').hexdigest()
        (folder / 'source.json').write_text(json.dumps(source))
        self.audit.research()
        self.assertTrue(any('project_snapshot hash differs from Git blob' in e for e in self.audit.errors))
        self.audit.errors.clear()
        del source['project_snapshot']
        (folder / 'source.json').write_text(json.dumps(source))
        (folder / 'source.md').write_text('Changed snapshot')
        self.audit.research()
        self.assertTrue(any('source hash mismatch' in e for e in self.audit.errors))
        self.audit.errors.clear()
        note.write_text('# Missing metadata')
        self.audit.research()
        self.assertTrue(any('missing metadata' in e for e in self.audit.errors))

    def test_personal_research_scope_allows_multiple_sources_not_code(self):
        self.audit.git_available = True
        self.audit.immutable_results = lambda base: None
        files = ['research/invsqrt/papers/arxiv-2308.12352/note.md', 'research/dqi/discussions/decoder-errors/note.md', 'research/README.md']
        row = '+| paper | invsqrt | [note](invsqrt/papers/arxiv-2308.12352/note.md) |'
        self.audit.git = lambda *args: (row if '--unified=0' in args else '\n'.join(files)).encode()
        branch = 'research/test-user'
        self.audit.scope('base', branch)
        self.assertEqual([], self.audit.errors)
        files.append('src/dqi/DQI-BASELINE/solution.py')
        self.audit.scope('base', branch)
        self.assertTrue(any('outside its scope' in e for e in self.audit.errors))
        self.audit.errors.clear()
        files.pop()
        row = '+Changed workflow instructions'
        self.audit.scope('base', branch)
        self.assertTrue(any('changed index outside resource rows' in e for e in self.audit.errors))

    def test_current_records_pass(self):
        self.audit.run()
        self.assertEqual([], self.audit.errors)

    def test_bad_title_and_config_fail(self):
        desc = self.root / 'src/invsqrt/INV-BASELINE/DESCRIPTION.md'
        desc.write_text('# Wrong title\n', encoding='utf-8')
        config = desc.parent / 'configs/baseline.json'
        config.write_text('{broken', encoding='utf-8')
        self.audit.run()
        self.assertTrue(any('title differs' in e for e in self.audit.errors))
        self.assertTrue(any('invalid/missing JSON' in e for e in self.audit.errors))

    def test_wrong_score_and_ratio_fail(self):
        path = self.root / 'src/invsqrt/SCORES.md'
        text = path.read_text(encoding='utf-8').replace('2076443.1049173493', '1').replace('1.00×', '2.00×')
        path.write_text(text, encoding='utf-8')
        self.audit.run()
        self.assertTrue(any('score differs' in e for e in self.audit.errors))
        self.assertTrue(any('incorrect improvement' in e for e in self.audit.errors))

    def test_new_run_cannot_use_legacy_exemption(self):
        run = self.root / 'results/invsqrt/INV-BASELINE/baseline/build_only/new-run'
        run.mkdir(parents=True)
        self.audit.run()
        self.assertTrue(any('provenance.json' in e for e in self.audit.errors))

    def test_pre_git_build_requires_matching_historical_evidence(self):
        build = next((self.root / 'results/dqi/DQI-BASELINE/baseline/build_only').iterdir())
        original = json.loads((build / 'metadata.json').read_text())
        run = self.root / 'results/dqi/DQI-BASELINE/baseline/dev_5min/test-regrade'
        run.mkdir(parents=True)
        digest = original['artifacts'][0]['sha256']
        p = dict(provenance_type='pre_git_build', track='dqi', experiment_id='DQI-BASELINE',
                 config_name='baseline', source_commit=None, build_config_path=None,
                 build_config_sha256=None, source_path=original['source'],
                 source_sha256=original['source_sha256'], artifact_sha256=digest,
                 build_run=build.relative_to(self.root).as_posix(), limitations='No Git commit at build time')
        record = run / 'provenance.json'
        record.write_text(json.dumps(p))
        meta = {'upload_artifact': {'sha256': digest}}
        self.audit.provenance(run, 'dqi', 'DQI-BASELINE', 'baseline', 'dev_5min', meta)
        self.assertEqual([], self.audit.errors)
        p['artifact_sha256'] = 'a' * 64
        record.write_text(json.dumps(p))
        self.audit.provenance(run, 'dqi', 'DQI-BASELINE', 'baseline', 'dev_5min', meta)
        self.assertTrue(any('artifact hash differs' in e for e in self.audit.errors))

    def test_verifier_change_fails(self):
        path = self.root / 'verifiers/invsqrt/verify_submission_invsqrt.py'
        path.write_text('"""Changed."""\n', encoding='utf-8')
        self.audit.run()
        self.assertTrue(any('organizer verifier missing/modified' in e for e in self.audit.errors))

    def test_notebook_dependency_drift_fails(self):
        path = self.root / 'requirements.txt'
        path.write_text(path.read_text().replace('numpy==2.5.4', 'numpy==2.4.6'))
        self.audit.run()
        self.assertTrue(any('Notebook dependency pins differ' in e for e in self.audit.errors))

    def test_full_settings_for_all_tracks(self):
        cases = {
            'invsqrt': ({'verified_shots': 200540928}, 'verify_submission_invsqrt.py', '--precision-bits', '10'),
            'dqi': ({'verified_shots': 102400, 'm': 4095, 'n': 70, 'degree': 12, 'r': 2016, 'log2_delta': -128}, 'verify_submission_dqi.py', '--num-shots', '4096'),
            'dfthcsos': ({'verified_shots': 254464}, 'verify.py', '--shots-per-address', '4'),
        }
        for track, (result, filename, flag, value) in cases.items():
            result['status'] = 'PASS'
            meta = {'verify_command': ['python', f'/root/verifiers/{track}/{filename}', 'artifact']}
            run = self.root / 'synthetic'
            self.audit.errors.clear()
            self.audit.evidence(run, track, 'full', meta, result)
            self.assertEqual([], self.audit.errors)
            meta['verify_command'] += [flag + '=' + value]
            self.audit.evidence(run, track, 'full', meta, result)
            self.assertTrue(any('non-official' in e for e in self.audit.errors))
            meta['verify_command'] = meta['verify_command'][:-1]
            result['verified_shots'] = 1
            self.audit.errors.clear()
            self.audit.evidence(run, track, 'full', meta, result)
            self.assertTrue(self.audit.errors)

    def test_scores_allow_different_environment_and_verifier(self):
        # Keep actual scores/PASS evidence; change only the comparison context.
        for number, path in enumerate(self.root.glob('results/**/metadata.json')):
            meta = json.loads(path.read_text(encoding='utf-8'))
            meta.update(python=f'3.13.{number}', packages={'kickmix': str(number)},
                        verifier_sha256={'verify.py': f'{number:064x}'},
                        dev_harness_sha256=f'{number + 1:064x}')
            path.write_text(json.dumps(meta), encoding='utf-8')
        self.audit.run()
        self.assertEqual([], self.audit.errors)

    def test_stdout_catches_matching_forged_table(self):
        run = next(self.root.glob('results/invsqrt/*/*/full/*'))
        result = json.loads((run / 'verifier.json').read_text())
        result['score'] = 1
        # Even when the table is changed to match, the original stdout still disagrees.
        table = self.root / 'src/invsqrt/SCORES.md'
        table.write_text(table.read_text(encoding='utf-8').replace('2076774.233715282', '1'), encoding='utf-8')
        (run / 'verifier.json').write_text(json.dumps(result))
        self.audit.run()
        self.assertTrue(any('stdout JSON differs' in e for e in self.audit.errors))

    def test_git_snapshots_and_scope(self):
        def git(*args):
            return subprocess.check_output(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', *args], cwd=self.root, stderr=subprocess.PIPE)
        git('init')
        git('config', 'core.autocrlf', 'false')
        git('add', '.')
        git('commit', '-m', 'fixture base')
        base = git('rev-parse', 'HEAD').decode().strip()
        self.audit.git_available = True
        old = next(self.root.glob('results/invsqrt/*/*/full/*/verify.stdout.txt'))
        original = old.read_bytes()
        old.write_bytes(b'changed')
        self.audit.immutable_results(base)
        self.assertTrue(any('immutable result' in e for e in self.audit.errors))
        self.audit.errors.clear()
        old.unlink()
        self.audit.immutable_results(base)
        self.assertTrue(any('immutable result' in e for e in self.audit.errors))
        self.audit.errors.clear()
        old.write_bytes(original)
        (old.parent / 'additional_review.json').write_text('{}')
        self.audit.immutable_results(base)
        self.assertEqual([], self.audit.errors)
        run = self.root / 'results/invsqrt/INV-BASELINE/baseline/build_only/fixture'
        run.mkdir(parents=True)
        source = 'src/invsqrt/INV-BASELINE/solution.py'
        cfg = 'src/invsqrt/INV-BASELINE/configs/baseline.json'
        p = dict(track='invsqrt', experiment_id='INV-BASELINE', config_name='baseline',
                 source_commit=base, source_path=source,
                 source_sha256=hashlib.sha256((self.root / source).read_bytes()).hexdigest(),
                 build_config_path=cfg, build_config_sha256=hashlib.sha256((self.root / cfg).read_bytes()).hexdigest(),
                 artifact_path='artifacts/invsqrt/INV-BASELINE/baseline.kmb', artifact_sha256='a' * 64,
                 build_command=['python', source, '--config', cfg], environment={'python': '3.13'})
        record = run / 'provenance.json'
        record.write_text(json.dumps(p))
        self.audit.provenance(run, 'invsqrt', 'INV-BASELINE', 'baseline', 'build_only', {})
        self.assertEqual([], self.audit.errors)
        p['source_sha256'] = 'b' * 64
        record.write_text(json.dumps(p))
        self.audit.provenance(run, 'invsqrt', 'INV-BASELINE', 'baseline', 'build_only', {})
        self.assertTrue(any('differs from Git snapshot' in e for e in self.audit.errors))
        self.audit.errors.clear()
        git('add', '.')
        git('commit', '-m', 'outside experiment scope')
        self.audit.scope(base, 'exp/INV-123-test')
        self.assertTrue(any('outside its scope' in e for e in self.audit.errors))


if __name__ == '__main__':
    unittest.main()
