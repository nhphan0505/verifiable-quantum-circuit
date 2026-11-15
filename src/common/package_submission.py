"""Package already-built DFTHC components without compiling or optimizing them.

Run from any working directory with Python 3.13, without third-party packages::

    python /path/to/repo/src/common/package_submission.py --input-dir COMPONENTS --output submission.zip

COMPONENTS must contain only submission.npz and contiguous angle_k_0.kmb,
angle_k_1.kmb, ... files. This checks layout, not circuit or Hamiltonian validity.
Files are streamed unchanged into a deterministic ZIP_STORED archive at its root.
Existing outputs are refused. No timestamps, source paths, or optimization state
are imported into the ZIP. Output serialization is a new container convention;
it does not promise the hash of an unavailable original submission ZIP.
"""

import argparse
import hashlib
from pathlib import Path
import re
import shutil
import tempfile
import zipfile


def package_dfthcsos(input_dir: Path, output: Path) -> dict:
    """Return output/component hashes after publishing a complete ZIP exclusively."""
    root = Path(input_dir).resolve(strict=True)
    output = Path(output).absolute()
    if not root.is_dir():
        raise ValueError('input-dir must be a directory')
    entries = list(root.iterdir())
    if any(p.is_symlink() or not p.is_file() for p in entries):
        raise ValueError('Components must be regular files, without symlinks/subdirectories')
    loaders = {}
    for path in entries:
        if path.name == 'submission.npz':
            continue
        match = re.fullmatch(r'angle_k_(0|[1-9][0-9]*)\.kmb', path.name)
        if match is None:
            raise ValueError(f'Unexpected component: {path.name}')
        loaders[int(match[1])] = path
    if not (root / 'submission.npz').is_file() or not loaders:
        raise ValueError('Require submission.npz and at least angle_k_0.kmb')
    if sorted(loaders) != list(range(len(loaders))):
        raise ValueError('ANGLE indices must be contiguous from zero')
    paths = [root / 'submission.npz'] + [loaders[k] for k in range(len(loaders))]
    if any(p.stat().st_size == 0 for p in paths):
        raise ValueError('Empty component')
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if output.parent.resolve() == root:
        raise ValueError('Output must be outside the components directory')
    output.parent.mkdir(parents=True, exist_ok=True)
    hashes = {}
    # Build off to the side, then publish exclusively; failed serialization leaves
    # no submission ZIP and never replaces an existing user's output.
    with tempfile.TemporaryFile(dir=output.parent) as temporary:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_STORED) as archive:
            for path in paths:
                info = zipfile.ZipInfo(path.name, (1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o600 << 16
                digest = hashlib.sha256()
                with path.open('rb') as source, archive.open(info, 'w', force_zip64=True) as target:
                    while block := source.read(1 << 20):
                        target.write(block)
                        digest.update(block)
                hashes[path.name] = digest.hexdigest()
        temporary.seek(0)
        with output.open('xb') as target:
            shutil.copyfileobj(temporary, target)
    with output.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    return {'artifact_path': str(output), 'artifact_sha256': digest,
            'component_sha256': hashes}


def main():
    """Parse explicit component/output paths and print the packaging record."""
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package_dfthcsos(args.input_dir, args.output), indent=2))


if __name__ == '__main__':
    main()
