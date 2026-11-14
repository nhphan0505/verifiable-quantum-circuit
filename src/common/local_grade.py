"""Grade one local artifact and preserve evidence in the experiment's results tree.

The notebook supplies track, experiment ID, owner and config name. This
module validates paths and hashes the actual KMB/ZIP, then runs kickmix-engine
with full official settings or a reduced smoke check. Windows delegates to
WSL; Linux/macOS use the kernel Python. At most four threads bound simulator resource use. Task 3 ZIPs are checked and
extracted into temporary storage under ignored artifacts, cleaned after grading.
Interruption keeps logs and metadata without inventing a score. A matching
build record is copied as provenance only when identity and artifact hash match;
otherwise review.json records the missing evidence for the coding agent to fix.
No score tables or historical runs are modified. Use via the local notebook.
"""

from pathlib import Path
import datetime
import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine_runtime import runtime, preflight

PREFIXES = {'invsqrt': 'INV', 'dqi': 'DQI', 'dfthcsos': 'DFT'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def grade(root, track, experiment_id, owner, config_name, mode="full"):
    root = Path(root).resolve()
    if mode not in {'smoke', 'full'}:
        raise ValueError('MODE must be smoke or full')
    if track not in PREFIXES:
        raise ValueError('Invalid TRACK')
    if not re.fullmatch(PREFIXES[track] + r'-(BASELINE|[1-9][0-9]*)', experiment_id):
        raise ValueError('EXPERIMENT_ID does not match TRACK')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', config_name) or not owner.strip():
        raise ValueError('Invalid CONFIG_NAME or empty OWNER')
    config = root / f'src/{track}/{experiment_id}/configs/{config_name}.json'
    artifact = root / f'artifacts/{track}/{experiment_id}/{config_name}'
    artifact = artifact.with_suffix('.zip' if track == 'dfthcsos' else '.kmb')
    if not config.is_file() or not artifact.is_file():
        raise FileNotFoundError(f'Require config {config} and compiled artifact {artifact}')
    if not artifact.resolve().is_relative_to(root / 'artifacts'):
        raise ValueError('Artifact symlink escapes artifacts/')
    if track == 'dfthcsos':
        for name in ['FeMoCo76o113e.fcidump', 'FeMoCo76o113e.fixed_shifts.npz']:
            if not (root / 'verifiers/dfthcsos' / name).is_file():
                raise FileNotFoundError(f'Restore reference data: {name}; see DATA.md')
    prefix, runtime_root = runtime(root)
    engine_info = preflight(prefix)
    if sys.platform == 'win32':
        # Share only bridge control files; result records remain in the usual tree.
        bridge_base = root / 'artifacts'
        bridge_base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.engine-bridge-', dir=bridge_base) as control:
            control = Path(control)
            linux_control = runtime_root + '/' + control.relative_to(root).as_posix()
            args = [track, experiment_id, owner, config_name, mode]
            code = ("import sys,os,json;from pathlib import Path;"
                    "sys.path.insert(0,sys.argv[1]+'/src/common');"
                    "from local_grade import grade;"
                    "Path(sys.argv[2]+'/pid').write_text(str(os.getpid()));"
                    "out=grade(sys.argv[1],*sys.argv[3:]);"
                    "Path(sys.argv[2]+'/result').write_text(str(out.relative_to(sys.argv[1])))")
            bridge = subprocess.Popen(prefix + ['-c', code, runtime_root, linux_control, *args])
            try:
                if bridge.wait() != 0:
                    raise RuntimeError('WSL grading failed; inspect output and saved results.')
            except KeyboardInterrupt:
                pidfile = control / 'pid'
                if pidfile.is_file():
                    pid = pidfile.read_text().strip()
                    if pid.isdecimal():
                        subprocess.run(['wsl.exe', '--exec', '/bin/kill', '-INT', pid], check=False)
                bridge.wait(timeout=30)
                raise
            return root / (control / 'result').read_text().strip()
    artifact_hash = sha(artifact)
    # Preflight ZIP before creating a run or extracting files.
    if track == 'dfthcsos':
        with zipfile.ZipFile(artifact) as archive:
            names = archive.namelist()
            indices = sorted(int(n[8:-4]) for n in names if re.fullmatch(r'angle_k_(0|[1-9][0-9]*)\.kmb', n))
            if (len(names) != len(set(names)) or 'submission.npz' not in names or not indices
                    or indices != list(range(len(indices)))
                    or any(n != 'submission.npz' and not re.fullmatch(r'angle_k_(0|[1-9][0-9]*)\.kmb', n) for n in names)):
                raise ValueError('ZIP requires submission.npz and contiguous angle_k_*.kmb at root only')
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-local-' + mode + '-' + uuid.uuid4().hex[:6]
    out = root / f'results/{track}/{experiment_id}/{config_name}/{mode}/{run_id}'
    out.mkdir(parents=True, exist_ok=False)
    meta = dict(track=track, experiment_id=experiment_id, config_name=config_name,
                run_id=run_id, owner=owner, verification_level=mode, status='RUNNING',
                python=sys.version, packages={p: importlib.metadata.version(p) for p in ['kickmix', 'numpy', 'scipy']},
                upload_artifact={'name': artifact.name, 'sha256': artifact_hash, 'size_bytes': artifact.stat().st_size},
                artifact_path=artifact.relative_to(root).as_posix(),
                verifier_sha256={p.relative_to(root).as_posix(): sha(p) for p in (root / 'verifiers').rglob('*.py')},
                timeout_seconds=None)
    if engine_info:
        meta.update(python=engine_info['python'], packages=engine_info['packages'], engine=dict(name='kickmix-engine', version='0.6.0', platform=engine_info['platform'], kernel=engine_info['kernel']))
    # Preserve all matching build candidates; do not guess when hashes have multiple origins.
    matches = []
    for record in (out.parents[1] / 'build_only').glob('*/provenance.json'):
        try:
            p = json.loads(record.read_text(encoding='utf-8-sig'))
            if (p.get('artifact_sha256') == artifact_hash and p.get('track') == track
                    and p.get('experiment_id') == experiment_id and p.get('config_name') == config_name):
                matches.append((record, p))
        except (OSError, ValueError):
            continue
    if len(matches) == 1:
        record, provenance = matches[0]
        provenance = dict(provenance, build_run=record.parent.relative_to(root).as_posix())
        write_json(out / 'provenance.json', provenance)
    else:
        write_json(out / 'review.json', {'missing_provenance': True, 'matching_builds': [p.parent.relative_to(root).as_posix() for p, _ in matches],
                                      'note': 'Agent must identify build evidence; do not infer source commit from current HEAD.'})
    workspace = None
    try:
        submission = artifact
        if track == 'dfthcsos':
            workspace = tempfile.TemporaryDirectory(prefix='.verify-', dir=artifact.parent)
            submission = Path(workspace.name).resolve()
            assert submission.parent == artifact.parent.resolve()
            with zipfile.ZipFile(artifact) as archive:
                archive.extractall(submission)
        verifier = root / 'verifiers' / track / ('verify.py' if track == 'dfthcsos' else f'verify_submission_{track}.py')
        cmd = [sys.executable, '-m', 'kickmix_engine', 'verify', track, str(submission),
               '--verifier', str(verifier.parent if track == 'dfthcsos' else verifier), '--threads', str(min(4, os.cpu_count() or 1))]
        if mode == 'smoke':
            cmd += {'invsqrt': ['--max-x', '4096', '--shots-per-x', '1'],
                    'dqi': ['--num-shots', '4096'],
                    'dfthcsos': ['--shots-per-address', '1']}[track]
        meta['verify_command'] = cmd
        meta['submission_sha256'] = {p.name: sha(p) for p in ([submission] if submission.is_file() else submission.iterdir()) if p.is_file()}
        write_json(out / 'config.json', dict(track=track, experiment_id=experiment_id, config_name=config_name, mode=mode, command=cmd))
        write_json(out / 'metadata.json', meta)
        env = dict(os.environ, KICKMIX_ENGINE_VERIFIERS=str(root / 'verifiers'), PYTHONPATH=str(root / 'verifiers'), OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONIOENCODING='utf-8')
        print('Running:', cmd, flush=True)
        with (out / 'verify.stdout.txt').open('w', encoding='utf-8') as stdout, (out / 'verify.stderr.txt').open('w', encoding='utf-8') as stderr:
            process = subprocess.Popen(cmd, cwd=root, env=env, stdout=stdout, stderr=stderr, start_new_session=os.name != 'nt')
            try:
                process.wait(timeout=meta['timeout_seconds'])
            except BaseException:
                if os.name != 'nt':
                    import signal
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
                raise
        meta['exit_code'] = process.returncode
        raw = (out / 'verify.stdout.txt').read_text(encoding='utf-8')
        try:
            result = json.loads(raw)
            (out / 'verifier.json').write_text(raw, encoding='utf-8')
            meta['status'] = 'PASS' if process.returncode == 0 and result.get('status') == 'PASS' else 'FAIL'
            print(json.dumps(result, indent=2))
        except (ValueError, AttributeError):
            meta['status'] = 'ERROR'
            print((out / 'verify.stderr.txt').read_text(encoding='utf-8')[-6000:])
    except KeyboardInterrupt:
        meta['status'] = 'INTERRUPTED'
        print('Stopped; no valid score.')
    except Exception as exc:
        meta['status'] = 'ERROR'
        meta['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        meta['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        write_json(out / 'metadata.json', meta)
        if workspace:
            workspace.cleanup()
        print(meta['status'], 'Saved:', out)
    return out
