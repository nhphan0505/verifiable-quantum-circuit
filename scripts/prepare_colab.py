"""Package local Colab inputs without installing extra dependencies.

Run from any directory with .venv/Scripts/python.exe scripts/prepare_colab.py.
Official verifier sources and reference data must match data_manifest.json;
missing or changed inputs abort before writing either ZIP. The dev harness is
included as maintained project code. ZIP entries use stable ordering/timestamps
so identical inputs produce identical archives. A sidecar records input and
archive SHA-256 values. Outputs are regenerated in artifacts/colab, outside Git.
No circuits are compiled or verified by this utility.
"""

import hashlib
import json
from pathlib import Path
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def prepare(root=ROOT):
    root = Path(root)
    manifest = json.loads((root / 'data_manifest.json').read_text(encoding='utf-8-sig'))
    expected = {key.replace('\\', '/'): value for key, value in manifest['files'].items()}
    official = sorted(key for key in expected if key.startswith('verifiers/') and key.endswith('.py'))
    actual = sorted(p.relative_to(root).as_posix() for p in (root / 'verifiers').rglob('*.py'))
    if actual != official:
        raise ValueError('Verifier Python file set differs from data_manifest.json')
    reference = ['verifiers/dfthcsos/FeMoCo76o113e.fcidump',
                 'verifiers/dfthcsos/FeMoCo76o113e.fixed_shifts.npz']
    inputs = {}
    for name in official + reference + ['src/common/dev_verify.py']:
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(f'Missing {name}; restore organizer data as described in DATA.md')
        inputs[name] = sha(path)
        if name != 'src/common/dev_verify.py' and inputs[name] != expected[name]:
            raise ValueError(f'SHA-256 mismatch: {name}')
    output = root / 'artifacts/colab'
    output.mkdir(parents=True, exist_ok=True)
    bundles = {
        'gqa_verifiers.zip': [(name, name) for name in official + ['src/common/dev_verify.py']],
        'dfthcsos_reference.zip': [(name, Path(name).name) for name in reference],
    }
    archives = {}
    for filename, entries in bundles.items():
        with tempfile.NamedTemporaryFile(dir=output, suffix='.partial', delete=False) as temp:
            temporary = Path(temp.name)
        try:
            with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
                for source, target in sorted(entries):
                    info = zipfile.ZipInfo(target, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    with (root / source).open('rb') as stream, archive.open(info, 'w') as dest:
                        while block := stream.read(8 * 1024 * 1024):
                            dest.write(block)
            temporary.replace(output / filename)
        finally:
            temporary.unlink(missing_ok=True)
        archives[filename] = sha(output / filename)
    record = {'inputs_sha256': inputs, 'archives_sha256': archives}
    (output / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    for filename, digest in archives.items():
        print(f'{output / filename}\nSHA-256: {digest}')
    return record


if __name__ == '__main__':
    prepare()
