"""Validate collaboration records using only Python's standard library.

Run python scripts/check_repo.py before PRs; CI also supplies --base/--branch.
Checks source syntax/docstrings, configs, experiment titles/IDs/links, scores,
run identity and provenance. Git snapshots verify recorded source/config hashes
without requiring ignored circuits or organizer datasets. Historical exceptions
are explicit paths in legacy_runs.json, never all runs of a baseline ID.
Experiment branches may modify only their own directories and tracking rows.
This checks consistency, not algorithm correctness, GitHub ownership or full
verification. No circuit is compiled or simulated.
"""

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TRACKS = {'invsqrt': 'INV', 'dqi': 'DQI', 'dfthcsos': 'DFT'}
NAME = r'[A-Za-z0-9][A-Za-z0-9_-]*'
HASH = r'[0-9a-f]{64}'


class Audit:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.errors = []
        self.git_available = (self.root / '.git').exists()

    def require(self, condition, message):
        if not condition:
            self.errors.append(message)
        return bool(condition)

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.PIPE)

    def read(self, path):
        return path.read_text(encoding='utf-8-sig')

    def load(self, path):
        try:
            value = json.loads(self.read(path), parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
            if not isinstance(value, dict):
                raise ValueError('expected JSON object')
            return value
        except (OSError, ValueError) as exc:
            self.errors.append(f'{path}: invalid/missing JSON: {exc}')
            return {}

    def target(self, origin, link):
        path = (origin.parent / link.split('#')[0]).resolve()
        if not self.require(path.is_relative_to(self.root), f'{origin}: link escapes repository: {link}'):
            return None
        return path

    def evidence(self, run, track, mode, meta, result):
        stdout = run / 'verify.stdout.txt'
        if stdout.is_file():
            self.require(self.load(stdout) == result, f'{run}: stdout JSON differs from verifier.json')
        if mode != 'full' or result.get('status') != 'PASS':
            return
        command = meta.get('verify_command', meta.get('command', []))
        filename = 'verify.py' if track == 'dfthcsos' else f'verify_submission_{track}.py'
        self.require(isinstance(command, list) and any(str(x).replace(chr(92), '/').endswith(f'/verifiers/{track}/{filename}') for x in command), f'{run}: full requires official verifier command')
        expected = {
            'invsqrt': {'--n-p': 10, '--width': 22, '--max-x': 3133452, '--beta': 1,
                        '--precision-bits': 24, '--shots-per-x': 64, '--eta': 218, '--system-qubits': 6540},
            'dqi': {'--m': 4095, '--n': 70, '--degree': 12, '--r': 2016,
                    '--num-shots': 102400, '--log2-delta': -128},
            'dfthcsos': {'--shots-per-address': 64},
        }[track]
        # Only exact option names are accepted; argparse abbreviations are ambiguous here.
        other = {'--format', '--seed', '--salt'}
        other |= {'--tree-edges'} if track == 'dfthcsos' else {'--batch-size', '--max-workers'}
        seen = set()
        for i, token in enumerate(command if isinstance(command, list) else []):
            if not isinstance(token, str) or not token.startswith('--'):
                continue
            key, sep, value = token.partition('=')
            self.require(key in expected or key in other, f'{run}: unrecognized full option {key}')
            self.require(key not in seen, f'{run}: duplicate option {key}')
            seen.add(key)
            if key in expected:
                try:
                    from fractions import Fraction
                    value = value if sep else command[i + 1]
                    self.require(Fraction(str(value)) == expected[key], f'{run}: non-official full setting {key}')
                except (ValueError, IndexError, ZeroDivisionError):
                    self.errors.append(f'{run}: invalid full setting {key}')
        shots = result.get('verified_shots')
        required = {'invsqrt': 200540928, 'dqi': 102400}.get(track)
        if required:
            self.require(shots == required, f'{run}: incorrect full verified_shots')
        else:
            self.require(type(shots) is int and shots > 0 and shots % 64 == 0, f'{run}: full DFTHC shots must be positive multiple of 64')
        if track == 'dqi':
            for key, value in {'m': 4095, 'n': 70, 'degree': 12, 'r': 2016, 'log2_delta': -128}.items():
                self.require(result.get(key) == value, f'{run}: incorrect full DQI {key}')

    def comparison(self, label, baseline_meta, candidate_meta, mode, same_run=False):
        def environment(meta):
            env = meta.get('environment', {})
            packages = meta.get('packages', env.get('packages', {}))
            python = meta.get('python', env.get('python', ''))
            version = re.match(r'[0-9]+[.][0-9]+[.][0-9]+', str(python))
            return (version.group() if version else None,
                    tuple(packages.get(p) for p in ['kickmix', 'numpy', 'scipy']))
        a, b = environment(baseline_meta), environment(candidate_meta)
        self.require(a == b and a[0] and all(a[1]), f'{label}: incompatible/missing comparison environment')
        # Baseline self-ratio is an identity, including historical records with missing hashes.
        if same_run:
            return
        for key in ['verifier_sha256'] + (['dev_harness_sha256'] if mode == 'dev_5min' else []):
            self.require(bool(baseline_meta.get(key)) and baseline_meta.get(key) == candidate_meta.get(key), f'{label}: incompatible/missing {key}; use a matching baseline')

    def immutable_results(self, base):
        # Compare against the actual base tree, including working-tree changes locally.
        for name in self.git('ls-tree', '-r', '--name-only', base, '--', 'results').decode().splitlines():
            parts = Path(name).parts
            if len(parts) != 7 or parts[1] not in TRACKS:
                continue
            # Existing evidence/provenance/reviews are append-only; new sidecars are allowed.
            path = self.root / name
            self.require(path.is_file() and path.read_bytes() == self.git('show', f'{base}:{name}'), f'immutable result modified/deleted: {name}; add a new run or sidecar')

    def provenance(self, run, track, exp, config, mode, meta):
        p = self.load(run / 'provenance.json')
        for key, value in [('track', track), ('experiment_id', exp), ('config_name', config)]:
            self.require(p.get(key) == value, f'{run}: provenance {key} mismatch')
        for key in ['source_sha256', 'build_config_sha256', 'artifact_sha256']:
            self.require(bool(re.fullmatch(HASH, str(p.get(key, '')))), f'{run}: invalid {key}')
        commit = p.get('source_commit', '')
        self.require(bool(re.fullmatch(r'[0-9a-f]{40}', str(commit))), f'{run}: require full source_commit SHA')
        self.require(bool(p.get('build_command')) and isinstance(p.get('environment'), dict) and bool(p['environment']), f'{run}: missing build_command/environment')
        source = f'src/{track}/{exp}/solution.py'
        cfg = f'src/{track}/{exp}/configs/{config}.json'
        artifact = f'artifacts/{track}/{exp}/{config}' + ('.zip' if track == 'dfthcsos' else '.kmb')
        for key, expected in [('source_path', source), ('build_config_path', cfg), ('artifact_path', artifact)]:
            self.require(p.get(key) == expected, f'{run}: {key} must be {expected}')
        if self.git_available and re.fullmatch(r'[0-9a-f]{40}', str(commit)):
            try:
                self.git('merge-base', '--is-ancestor', commit, 'HEAD')
                for path, key in [(source, 'source_sha256'), (cfg, 'build_config_sha256')]:
                    self.require(hashlib.sha256(self.git('show', f'{commit}:{path}')).hexdigest() == p.get(key), f'{run}: {key} differs from Git snapshot')
            except subprocess.CalledProcessError:
                self.errors.append(f'{run}: source commit missing/not ancestor of HEAD, or files absent at commit')
        if mode != 'build_only':
            self.require(meta.get('upload_artifact', {}).get('sha256') == p.get('artifact_sha256'), f'{run}: upload hash differs from build provenance')
            build = self.root / str(p.get('build_run', ''))
            expected_parent = self.root / f'results/{track}/{exp}/{config}/build_only'
            if self.require(build.parent == expected_parent and build.is_dir(), f'{run}: missing/invalid build_run path'):
                original = self.load(build / 'provenance.json')
                for key in ['source_commit', 'source_sha256', 'build_config_sha256', 'artifact_sha256']:
                    self.require(p.get(key) == original.get(key), f'{run}: {key} differs from build_run')

    def run(self):
        legacy = set(self.load(self.root / 'scripts/legacy_runs.json').get('runs', []))
        manifest = self.load(self.root / 'data_manifest.json').get('files', {})
        for name, digest in manifest.items():
            name = name.replace('\\', '/')
            if name.startswith('verifiers/') and name.endswith('.py'):
                path = self.root / name
                self.require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest, f'{name}: organizer verifier missing/modified')
        for track, prefix in TRACKS.items():
            folder = self.root / 'src' / track
            index = folder / 'EXPERIMENTS.md'
            indexed = {}
            for line in self.read(index).splitlines():
                match = re.match(r'\| (' + prefix + r'-(?:BASELINE|[1-9][0-9]*)) \| \[(.*)\]\(([^)]+)\) \| (.*?) \|', line)
                if not match:
                    continue
                exp, title, link, issue = match.groups()
                self.require(exp not in indexed, f'{index}: duplicate {exp}')
                indexed[exp] = title
                self.require(link == f'{exp}/DESCRIPTION.md', f'{index}: wrong description path for {exp}')
                if not exp.endswith('-BASELINE'):
                    self.require(bool(re.search(r'https://github\.com/[^/\s]+/[^/\s]+/issues/' + exp.split('-')[1] + r'(?:\)|$)', issue)), f'{index}: missing/mismatched Issue URL for {exp}')
            for experiment in folder.iterdir():
                if not experiment.is_dir() or experiment.name == '__pycache__':
                    continue
                exp = experiment.name
                self.require(bool(re.fullmatch(prefix + r'-(?:BASELINE|[1-9][0-9]*)', exp)), f'{experiment}: invalid ID')
                desc = experiment / 'DESCRIPTION.md'
                if self.require(desc.is_file(), f'{experiment}: missing DESCRIPTION.md'):
                    title = self.read(desc).splitlines()[0].removeprefix('# ')
                    self.require(title == indexed.get(exp) and title.startswith(f'[{exp}] '), f'{desc}: title differs from index/ID')
                configs = list((experiment / 'configs').glob('*.json'))
                if (experiment / 'solution.py').exists():
                    self.require(bool(configs), f'{experiment}: solution.py requires at least one config')
                if configs:
                    self.require((experiment / 'solution.py').is_file(), f'{experiment}: configs require solution.py')
                for config in configs:
                    self.require(bool(re.fullmatch(NAME, config.stem)), f'{config}: invalid config name')
                    self.require(isinstance(self.load(config), dict), f'{config}: require JSON object')
            for exp in indexed:
                self.require((folder / exp / 'DESCRIPTION.md').is_file(), f'{index}: missing experiment {exp}')
            self.scores(folder / 'SCORES.md', track, indexed)
            for run in (self.root / 'results' / track).glob('*/*/*/*'):
                if not run.is_dir():
                    continue
                exp, config, mode, run_id = run.relative_to(self.root / 'results' / track).parts
                self.require(exp in indexed, f'{run}: unknown experiment')
                self.require((folder / exp / 'configs' / f'{config}.json').is_file(), f'{run}: missing build config')
                self.require(mode in {'build_only', 'smoke', 'dev_5min', 'full'}, f'{run}: invalid mode')
                if (run / 'verifier.json').is_file():
                    self.evidence(run, track, mode, self.load(run / 'metadata.json'), self.load(run / 'verifier.json'))
                if run.relative_to(self.root).as_posix() in legacy:
                    continue
                meta = self.load(run / 'metadata.json') if mode != 'build_only' else {}
                if mode != 'build_only':
                    for key, value in [('track', track), ('experiment_id', exp), ('config_name', config), ('run_id', run_id), ('verification_level', mode)]:
                        self.require(meta.get(key) == value, f'{run}: metadata {key} mismatch')
                    self.load(run / 'config.json')
                    if meta.get('status') == 'PASS':
                        result = self.load(run / 'verifier.json')
                        self.require(result.get('status') == 'PASS' and meta.get('exit_code') == 0, f'{run}: PASS lacks verifier evidence')
                self.provenance(run, track, exp, config, mode, meta)
        for subtree in ['src', 'scripts', 'notebooks', 'docs', 'results']:
            for path in (self.root / subtree).rglob('*'):
                if path.suffix == '.json':
                    self.load(path)
                elif path.suffix == '.py':
                    try:
                        tree = ast.parse(self.read(path))
                        self.require(bool(ast.get_docstring(tree)), f'{path}: missing module docstring')
                    except SyntaxError as exc:
                        self.errors.append(f'{path}: {exc}')
                elif path.suffix == '.md' and subtree != 'scripts':
                    self.links(path)
        for path in self.root.glob('*.md'):
            self.links(path)
        notebook = self.load(self.root / 'notebooks/GQA_Grade_Submission.ipynb')
        pins = {}
        for filename in ['requirements.txt', 'requirements-colab.txt']:
            packages = [line.strip() for line in self.read(self.root / filename).splitlines() if line.strip() and not line.startswith('#')]
            self.require(all(re.fullmatch(r'[A-Za-z0-9_-]+==[0-9][A-Za-z0-9.]*', p) for p in packages), f'{filename}: dependencies must have exact version pins')
            pins[filename] = packages
        self.require(self.read(self.root / '.python-version').strip() == '3.13', 'Python minor must match documented 3.13 baseline')
        install = '\n'.join(''.join(cell.get('source', [])) for cell in notebook.get('cells', []))
        expected = None
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                for node in ast.parse(''.join(cell.get('source', []))).body:
                    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'EXPECTED_PACKAGES' for t in node.targets):
                        expected = ast.literal_eval(node.value)
        self.require(expected == dict(p.split('==') for p in pins['requirements.txt']), 'Notebook dependency pins differ from requirements.txt')
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = ''.join(cell['source'])
                try:
                    ast.parse('\n'.join('pass' if l.startswith(('%', '!')) else l for l in source.splitlines()))
                except SyntaxError as exc:
                    self.errors.append(f'Notebook syntax: {exc}')
        print(f'Historical runs exempt from new provenance schema: {len(legacy)}')

    def links(self, path):
        for link in re.findall(r'\]\(([^)]+)\)', self.read(path)):
            if '://' in link or any(c in link for c in '<>') or link.startswith('#'):
                continue
            target = self.target(path, link)
            if target:
                # Stage 02 descriptions legitimately reference the planned implementation.
                if path.name == 'DESCRIPTION.md' and not (path.parent / 'solution.py').exists() and link in {'solution.py', 'configs/'}:
                    continue
                self.require(target.exists(), f'{path}: broken local link {link}')

    def scores(self, path, track, indexed):
        rows = {}
        results = {}
        metadata = {}
        targets = {}
        for line in self.read(path).splitlines():
            cells = [s.strip() for s in line.strip('|').split('|')]
            if cells[0] not in indexed:
                if re.match(r'(INV|DQI|DFT)-', cells[0]):
                    self.errors.append(f'{path}: score row has unknown experiment {cells[0]}')
                continue
            exp = cells[0]
            self.require(exp not in rows, f'{path}: duplicate score row {exp}')
            rows[exp] = cells
            if not self.require(len(cells) == 7, f'{path}: expected seven score columns'):
                continue
            for score_col, ratio_col, run_col, mode in [(1, 3, 5, 'full'), (2, 4, 6, 'dev_5min')]:
                if cells[score_col] == '—':
                    self.require(cells[ratio_col] == '—' and cells[run_col] == '—', f'{path}: empty score has ratio/run')
                    continue
                match = re.search(r'\]\(([^)]+)\)', cells[run_col])
                if not self.require(bool(match), f'{path}: score lacks result link'):
                    continue
                target = self.target(path, match[1])
                if not target:
                    continue
                rel = target.relative_to(self.root).parts
                if not self.require(len(rel) == 7 and rel[:3] == ('results', track, exp) and rel[4] == mode and rel[-1] == 'verifier.json', f'{path}: incorrect run path/mode'):
                    continue
                result = self.load(target)
                meta = self.load(target.parent / 'metadata.json')
                try:
                    value = float(cells[score_col])
                    self.require(math.isfinite(value) and value > 0 and math.isclose(value, result['score'], rel_tol=1e-12), f'{path}: score differs from verifier')
                    self.require(result.get('status') == meta.get('status') == 'PASS' and meta.get('verification_level') == mode, f'{path}: score must reference PASS in correct mode')
                    results[exp, mode] = result
                    metadata[exp, mode] = meta
                    targets[exp, mode] = target
                except (ValueError, KeyError, TypeError):
                    self.errors.append(f'{path}: invalid score/verifier')
        for exp, cells in rows.items():
            for mode, ratio_col in [('full', 3), ('dev_5min', 4)]:
                if len(cells) != 7 or cells[ratio_col] == '—':
                    continue
                baseline = results.get((TRACKS[track] + '-BASELINE', mode))
                candidate = results.get((exp, mode))
                if not self.require(bool(baseline and candidate), f'{path}: ratio has no baseline/candidate'):
                    continue
                baseline_key = (TRACKS[track] + '-BASELINE', mode)
                self.comparison(path, metadata[baseline_key], metadata[exp, mode], mode, targets[baseline_key] == targets[exp, mode])
                if mode == 'dev_5min':
                    for key in ['profile_version', 'input_sha256', 'verified_shots']:
                        self.require(candidate.get(key) == baseline.get(key), f'{path}: incompatible baseline {key}')
                    for key, value in baseline.get('profile', {}).items():
                        if key != 'submission':
                            self.require(candidate.get('profile', {}).get(key) == value, f'{path}: incompatible dev profile {key}')
                try:
                    ratio = float(cells[ratio_col].removesuffix('×'))
                    self.require(abs(ratio - baseline['score'] / candidate['score']) <= .0051, f'{path}: incorrect improvement ratio')
                except (ValueError, KeyError, ZeroDivisionError):
                    self.errors.append(f'{path}: invalid improvement ratio')

    def scope(self, base, branch):
        if not self.git_available:
            self.errors.append('--base requires Git repository')
            return
        self.immutable_results(base)
        match = re.match(r'exp/((INV|DQI|DFT)-[1-9][0-9]*)(?:-|$)', branch)
        files = self.git('diff', '--name-only', f'{base}...HEAD').decode().splitlines()
        if branch.startswith('exp/'):
            self.require(bool(match), 'Experiment branch must use exp/<ID>-<name>')
        if not match:
            print('Infrastructure branch: experiment scope restriction not applied')
            return
        exp, prefix = match.groups()
        track = next(t for t, p in TRACKS.items() if p == prefix)
        shared = {f'src/{track}/{name}.md' for name in ['EXPERIMENTS', 'SCORES']}
        for name in files:
            allowed = name.startswith((f'src/{track}/{exp}/', f'results/{track}/{exp}/')) or name in shared
            self.require(allowed, f'experiment branch modified outside its scope: {name}')
            if name in shared:
                diff = self.git('diff', '--unified=0', f'{base}...HEAD', '--', name).decode()
                for line in diff.splitlines():
                    if line.startswith(('+++', '---')) or not line.startswith(('+', '-')):
                        continue
                    self.require(bool(re.match(r'\|\s*' + re.escape(exp) + r'\s*\|', line[1:])), f'{name}: changed tracking content outside row {exp}')

    def tracked_files(self):
        for name in self.git('ls-files').decode().splitlines():
            self.require(not name.startswith(('artifacts/', '.venv/')) and not name.endswith(('.kmb', '.so')), f'tracked binary/environment: {name}')
            path = self.root / name
            self.require(not path.is_file() or path.stat().st_size < 10 * 1024 * 1024, f'tracked file >=10 MiB: {name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='Git base SHA/ref for PR scope check')
    parser.add_argument('--branch', default='', help='PR head branch; exp/<ID>-... enables scope enforcement')
    args = parser.parse_args()
    audit = Audit(ROOT)
    audit.run()
    if audit.git_available:
        audit.tracked_files()
    if args.base:
        audit.scope(args.base, args.branch)
    if not audit.git_available:
        print('Git absent: commit snapshots and PR scope not checked')
    for error in audit.errors:
        print('ERROR:', error)
    print(f'Repository checks: {len(audit.errors)} error(s)')
    return bool(audit.errors)


if __name__ == '__main__':
    sys.exit(main())
