"""Build the fixed INV-66 circuit from the recovered arithmetic generator.

The source constructs the 64-row coefficient code, consumed-root arithmetic,
balanced division/phase and inverse cleanup with typed owner/debt helpers.
The private upstream source/search procedure is not claimed to be recovered. The circuit phases by the verifier's 1/sqrt(x) contract and restores x
and scratch according to external evidence, not a new verifier run. The original precursor is generated first; the separate INV-66 postprocessing module applies the HMR/CZ
correction, preserving the fixed output bytes. There are no numerical tuning parameters.

Run: python src/invsqrt/INV-66/solution.py --config
src/invsqrt/INV-66/configs/reconstructed.json
Output: artifacts/invsqrt/INV-66/reconstructed.kmb (never silently overwritten).
Build requires a clean committed checkout and repository-pinned Python/packages.
No original KMB/KMX, external bundle, cache or download is a build input.
New build_only provenance records hashes and a CPython file/import audit.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.metadata
import io
import json
import os
import subprocess
import sys
import uuid


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    track, experiment_id = here.parent.name, here.name
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=here/'configs/reconstructed.json')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    config = args.config.resolve()
    if config.parent != (here/'configs').resolve() or config.suffix != '.json':
        raise ValueError('Config must be a JSON directly inside this experiment configs/')
    if config.stem != 'reconstructed':
        raise ValueError('Only the fixed reconstructed config is supported')
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError('Use Python 3.13')
    packages = {p: importlib.metadata.version(p) for p in ('kickmix', 'numpy', 'scipy')}
    if packages != {'kickmix': '1.0.0', 'numpy': '2.5.4', 'scipy': '1.18.1'}:
        raise RuntimeError('Install the repository requirements.txt pins')
    def git(*command):
        return subprocess.check_output(['git', *command], cwd=root)
    if git('status', '--porcelain').strip():
        raise RuntimeError('Build requires a clean committed checkout')
    commit = git('rev-parse', 'HEAD').decode().strip()
    pp_path = here/'postprocessing/solution.py'
    shared_source = root/'src/invsqrt/INV-51/circuit.py'
    finishing_paths = [root/f'src/invsqrt/postprocessing/PP-{index:03d}/solution.py' for index in range(1,5)]
    inputs = [here/name for name in (
        'solution.py','circuit.py','arithmetic_helpers.py','cleanup.py','finishing.py',
        'lookup_certificate.py','recovery_model.py','data/lookup64_certificates.json',
        'data/cleanup64.json','data/arithmetic_helpers.json','data/phase_parameters.json')]
    inputs += [config, root/'requirements.txt', shared_source, *finishing_paths, pp_path]

    input_records = []
    for path in inputs:
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if data != git('show', commit+':'+relative):
            raise RuntimeError('Checkout bytes differ from source commit: '+relative)
        input_records.append({'path': relative, 'sha256': digest(data)})
    settings = json.loads(config.read_text(encoding='utf-8'))
    expected = 'e46d90c36d1beb3ce7731a3e0b5c3659b3cda7f5f290b73c6c34513d96c005b6'
    if settings != {'expected_sha256': expected, 'expected_bytes': 198590}:
        raise ValueError('Config must describe the fixed target; changing the target requires a new source decision')
    output = (args.output or root/f'artifacts/{track}/{experiment_id}/{config.stem}.kmb').resolve()
    if output.name != config.stem+'.kmb' or not output.is_relative_to(root/'artifacts'):
        raise ValueError('Output must be named after the config inside this checkout artifacts/')
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-exact-'+uuid.uuid4().hex[:8]
    run_dir = root/f'results/{track}/{experiment_id}/{config.stem}/build_only/{run_id}'
    run_dir.mkdir(parents=True, exist_ok=False)
    work_dir = root/f'artifacts/{track}/{experiment_id}/{run_id}-finishing'
    if work_dir.exists(): raise FileExistsError(work_dir)
    assert work_dir.resolve().is_relative_to((root/'artifacts').resolve())
    reads, writes, imports = set(), set(), set()
    runtime_roots = {Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve()}
    source_root = here.resolve()
    def permitted_read(path):
        return (path.is_relative_to(source_root) or path.is_relative_to(shared_source.parent.resolve())
                or any(path.is_relative_to(p.parent.resolve()) for p in [pp_path, *finishing_paths])
                or any(path.is_relative_to(p) for p in runtime_roots) or path == output
                or path.is_relative_to(run_dir) or path.is_relative_to(work_dir))
    def audit(event, arguments):
        if event.startswith('socket.') or event in ('subprocess.Popen', 'os.system'):
            raise RuntimeError('No network or subprocesses are permitted during circuit construction')
        if event == 'import' and len(arguments) > 1 and isinstance(arguments[1], str):
            path = Path(arguments[1]).resolve()
            if not permitted_read(path):
                raise RuntimeError('Import outside declared source/runtime: '+str(path))
            imports.add(str(path))
        if event != 'open' or not isinstance(arguments[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(arguments[0])).resolve()
        mode = arguments[1]
        flags = arguments[2] or 0
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        if writing:
            if path != output and not path.is_relative_to(run_dir) and not path.is_relative_to(work_dir):
                raise RuntimeError('Write outside fresh artifact/evidence output: '+str(path))
            writes.add(str(path))
        else:
            if not permitted_read(path):
                raise RuntimeError('Read outside declared source/runtime: '+str(path))
            reads.add(str(path))
    sys.dont_write_bytecode = True
    sys.addaudithook(audit)
    from circuit import build_circuit, POSTPROCESSING_REPORT
    circuit = build_circuit(work_dir)
    buffer = io.BytesIO()
    circuit.to_file(buffer, format='kmb')
    data = buffer.getvalue()
    if len(data) != settings['expected_bytes'] or digest(data) != expected:
        raise RuntimeError('Generated circuit does not match the fixed target: '+digest(data))
    with output.open('xb') as stream:
        stream.write(data)
    def write_json(name, value):
        (run_dir/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    dependency_audit = {
        'mechanism': 'CPython open/import audit; all circuit serialization uses BytesIO, final file write uses Python open',
        'source_inputs_checked_against_commit': input_records,
        'read_paths': sorted(reads), 'import_paths': sorted(imports),
        'write_paths': sorted(writes), 'network_or_subprocesses_during_construction': False,
        'limitations': ['interpreter startup and Git snapshot preflight occur before audit installation', 'native package internal OS reads are outside CPython hooks; the recovered arithmetic uses the declared shared source and mathematical data; PP-001..PP-004 read only intermediates produced in this fresh work directory, then PP-005 rewrites that new circuit'],
    }
    write_json('dependency_audit.json', dependency_audit)
    relative_source = (here/'solution.py').relative_to(root).as_posix()
    config_relative = config.relative_to(root).as_posix()
    hashes = {i['path']: i['sha256'] for i in input_records}
    provenance = {
        'track': track, 'experiment_id': experiment_id, 'config_name': config.stem,
        'source_commit': commit, 'source_path': relative_source,
        'source_sha256': hashes[relative_source], 'build_config_path': config_relative,
        'build_config_sha256': hashes[config_relative],
        'artifact_path': output.relative_to(root).as_posix(), 'artifact_sha256': digest(data),
        'build_command': [sys.executable, *sys.argv], 'build_run': None,
        'environment': {'python': sys.version, 'packages': packages, 'platform': sys.platform, 'dependencies': input_records},
        'reconstruction_level': 'ARITHMETIC_GENERATOR', 'dependency_audit': 'dependency_audit.json',
        'postprocessing': dict(POSTPROCESSING_REPORT),
        'generated_work_directory': work_dir.relative_to(root).as_posix(),
    }
    write_json('provenance.json', provenance)
    print(json.dumps({'status': 'BUILT', 'artifact': str(output), 'sha256': digest(data), 'bytes': len(data), 'evidence': str(run_dir)}, indent=2))


if __name__ == '__main__':
    main()
