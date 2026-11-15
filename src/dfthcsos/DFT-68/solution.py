"""Rebuild frozen DFTHC factorization and 15 algebraic ANGLE loaders (DFT-68).

Inherited compiler/data: Syed Asad Ali, Apache-2.0; LICENSE.txt and NOTICE.txt.
data.json stores numeric arrays and explicit Boolean product plans, not KMB/KMX.
The compiler retains address completion, GF(2) coordinates, endpoint helpers,
low/high caches and HMR/CZ phase repayment. No fitting/search is rerun. Loader
correctness is limited to the legal endpoint assumption described upstream;
official grading is separate. This build preserves all original array bits.

Windows Python 3.13 and pinned requirements, no WSL/author engine needed:
python src/dfthcsos/DFT-68/solution.py --config src/dfthcsos/DFT-68/configs/reconstructed.json

Paths resolve from this file, config must belong to this experiment. Output is
artifacts/dfthcsos/DFT-68/reconstructed.zip; existing output is refused. Components
are checked against published hashes before shared deterministic packaging.
Build-only provenance and input-open audit are new records, not verifier PASS.
"""

import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
import kickmix as km

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRACK, EXPERIMENT = HERE.parent.name, HERE.name
sys.path.insert(0, str(ROOT / 'src/common'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def record(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def complete(words):
    """Upstream reversible Mobius completion of the twelve unused addresses."""
    assert words.shape == (1220, 75)
    a = np.zeros((1232, 75), dtype=np.uint8)
    a[:1220] = words
    f = a.reshape(77, 16, 75)
    for b in range(4):
        for low in range(16):
            if low & (1 << b):
                f[:, low] ^= f[:, low ^ (1 << b)]
    for b in range(7):
        for high in range(77):
            if high & (1 << b):
                f[high] ^= f[high ^ (1 << b)]
    f[76, 4:] = 0
    for b in range(7):
        for high in range(77):
            if high & (1 << b):
                f[high] ^= f[high ^ (1 << b)]
    for b in range(4):
        for low in range(16):
            if low & (1 << b):
                f[:, low] ^= f[:, low ^ (1 << b)]
    assert np.array_equal(a[:1220], words)
    return a


def write_npz(path, arrays):
    """Write fresh NPY members with upstream Unix ZIP/ZIP64 metadata on any OS."""
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_STORED) as archive:
        for name, array in arrays.items():
            info = zipfile.ZipInfo(name + '.npy', (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o600 << 16
            with archive.open(info, 'w', force_zip64=True) as stream:
                np.lib.format.write_array(stream, array, allow_pickle=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config.resolve(strict=True)
    if config_path.parent != HERE / 'configs' or config_path.suffix != '.json':
        raise ValueError('Config must resolve inside this experiment configs/')
    config = json.loads(config_path.read_text(encoding='utf-8'))
    if config != {'batch_size': 5, 'word_bits': 8, 'plan_set': 'author_frozen_v12'}:
        raise ValueError('Only the frozen reconstructed configuration is supported')
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError('Python 3.13 required')
    for package, version in [('kickmix', '1.0.0'), ('numpy', '2.5.4')]:
        if importlib.metadata.version(package) != version:
            raise RuntimeError(f'Require {package}=={version}')
    head = git('rev-parse', 'HEAD').decode().strip()
    dependencies = [HERE / name for name in ['solution.py', 'circuit.py', 'data.json', 'reconstruction.json']]
    dependencies += [config_path, ROOT / 'src/common/package_submission.py']
    dependency_hashes = {}
    for path in dependencies:
        relative = path.relative_to(ROOT).as_posix()
        if path.read_bytes() != git('show', f'{head}:{relative}'):
            raise RuntimeError(f'Uncommitted build dependency: {relative}')
        dependency_hashes[relative] = sha(path)
    output = ROOT / 'artifacts' / TRACK / EXPERIMENT / (config_path.stem + '.zip')
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='build-', dir=output.parent)).resolve()
    components = work / 'components'
    sources = work / 'sources'
    components.mkdir()
    sources.mkdir()
    reads = set()
    created = set()
    allowed = [HERE, ROOT / 'src/common', Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve(), work]

    def audit(event, values):
        if event != 'open' or isinstance(values[0], int):
            return
        path, mode, flags = values
        if mode is not None and mode[:1] in {'w', 'x'}:
            resolved = Path(path).resolve()
            if resolved.is_relative_to(output.parent):
                created.add(resolved)
            return
        if mode is not None and not ('r' in mode or '+' in mode):
            return
        if mode is None and flags & os.O_WRONLY and not flags & os.O_RDWR:
            return
        resolved = Path(path).resolve()
        reads.add(str(resolved))
        if resolved not in created and resolved != output and not any(resolved.is_relative_to(base) for base in allowed):
            raise RuntimeError(f'Unexpected build input: {resolved}')

    sys.addaudithook(audit)
    import circuit
    from package_submission import package_dfthcsos
    data = json.loads((HERE / 'data.json').read_text(encoding='utf-8'))
    arrays = {name: np.asarray(item['values'], dtype=item['dtype']).reshape(item['shape'])
              for name, item in data['arrays'].items()}
    words = complete(arrays['angle_words'])
    write_npz(components / 'submission.npz', arrays)
    reports = []
    for k, plan in enumerate(data['plans']):
        source = sources / f'angle_k_{k}.kmx'
        if k == 0:
            report = circuit.emit_k0_emit(plan, words, source, data['k0_events'])
        else:
            report = circuit.emit_plan_emit(plan, words, source)
        km.Circuit.from_file(source, format='kmx').to_file(components / f'angle_k_{k}.kmb', format='kmb')
        reports.append(report)
        print(f'Compiled ANGLE_{k}: {report["toffoli_count"]} Toffoli', flush=True)
    manifest = json.loads((HERE / 'reconstruction.json').read_text(encoding='utf-8'))
    got = {path.name: sha(path) for path in components.iterdir()}
    if got != manifest['expected_components']:
        raise RuntimeError(f'Component hash mismatch: {got}')
    packaged = package_dfthcsos(components, output)
    # Repack from the same fresh components to establish deterministic container bytes.
    again = package_dfthcsos(components, work / 'repeat.zip')
    if packaged['artifact_sha256'] != again['artifact_sha256']:
        raise RuntimeError('Nondeterministic package')
    audit_paths = sorted(reads)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT / 'results' / TRACK / EXPERIMENT / config_path.stem / 'build_only' / (stamp + '-' + work.name)
    run.mkdir(parents=True, exist_ok=False)
    relative = lambda p: p.relative_to(ROOT).as_posix()
    provenance = {'track': TRACK, 'experiment_id': EXPERIMENT, 'config_name': config_path.stem,
                  'source_commit': head, 'source_path': relative(HERE / 'solution.py'),
                  'source_sha256': sha(HERE / 'solution.py'), 'build_config_path': relative(config_path),
                  'build_config_sha256': sha(config_path), 'artifact_path': relative(output),
                  'artifact_sha256': packaged['artifact_sha256'], 'build_run': None,
                  'build_command': [sys.executable, str(HERE / 'solution.py'), '--config', str(config_path)],
                  'dependency_sha256': dependency_hashes,
                  'environment': {'python': sys.version, 'os': platform.platform(),
                                  'packages': {p: importlib.metadata.version(p) for p in ['kickmix', 'numpy', 'scipy']}}}
    record(run / 'provenance.json', provenance)
    record(run / 'build.json', {'status': 'BUILT', 'components': got, 'compiler_reports': reports,
                              'deterministic_zip': True, 'work_path': relative(work),
                              'original_zip_comparison': 'UNAVAILABLE'})
    record(run / 'dependency_audit.json', {'read_paths': audit_paths,
           'unexpected_inputs': [], 'scope': 'Python open audit after explicit config, snapshot and runtime checks; no compiler subprocesses; Git used only for provenance.'})
    print(json.dumps({'status': 'BUILT', 'artifact': relative(output), 'sha256': packaged['artifact_sha256'],
                      'build_record': relative(run)}, indent=2))


if __name__ == '__main__':
    main()
