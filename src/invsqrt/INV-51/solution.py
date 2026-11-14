"""Compile Fusion invsqrt directly from the integrated Python generator and data.

Issue #51; owner nhphan0505. Upstream Syed Asad Ali, Apache-2.0; see NOTICE.txt,
LICENSE.txt and upstream_changes.json. Source/data in engine/ are readable and
editable, with integrity checked against engine_manifest.json before build.
No external source bundle, Linux engine, input submission or precompiled circuit
is used. The pipeline computes normalization/root/residual, coefficient/seed/product,
divider/phase endpoint, inverse cleanup and deterministic gate finishing passes.
The target is 46-qubit phase exp(2*pi*i/sqrt(x)), x=1..3133452, restoring x/scratch.
Exact bytes and HMR corrections must match INV-51. No optimization or new score is
claimed. Historical source/proof-receipt hash checks were replaced by the committed
integrated-source manifest; arithmetic/ownership/phase assertions remain.

Use Windows repo .venv with Python 3.13 and pinned requirements:
python src/invsqrt/INV-51/solution.py --config src/invsqrt/INV-51/configs/reconstructed.json
Outputs artifacts/invsqrt/INV-51/reconstructed.kmb and build_only provenance.
Each stage times out at 600 seconds; Windows memory limits are not enforced.
This command does not run official grading. See DESCRIPTION.md for validation.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRACK, EXPERIMENT = HERE.parent.name, HERE.name


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def relative_path(path):
    """Describe a runtime path relative to the checkout, using POSIX separators."""
    return Path(os.path.relpath(Path(path).resolve(), ROOT)).as_posix()


def build_command(config_path):
    """Equivalent invocation from repo root; preserves the actual Python runtime."""
    return subprocess.list2cmdline([relative_path(sys.executable),
        (HERE/'solution.py').relative_to(ROOT).as_posix(), '--config',
        config_path.relative_to(ROOT).as_posix()])


def load_config(value):
    path = Path(value).resolve()
    if path.parent != (HERE / 'configs').resolve() or path.suffix != '.json':
        raise ValueError('Config must resolve directly inside this experiment configs/')
    config = json.loads(path.read_text(encoding='utf-8'))
    if set(config) != {'expected_sha256', 'stage_timeout_seconds'}:
        raise ValueError('Unexpected configuration keys')
    if config['stage_timeout_seconds'] != 600:
        raise ValueError('First reconstruction has a fixed 600-second stage limit')
    return path, config


def check_committed(config_path):
    head = git('rev-parse', 'HEAD').decode().strip()
    prefix = HERE.relative_to(ROOT).as_posix()
    tracked = git('ls-files', '-z', prefix).decode().split('\0')
    for relative in filter(None, tracked):
        if (ROOT / relative).read_bytes() != git('show', f'{head}:{relative}'):
            raise RuntimeError(f'Uncommitted source/dependency metadata: {relative}')
    for path in [HERE/'solution.py', HERE/'circuit.py', config_path, HERE/'engine_manifest.json']:
        if path.relative_to(ROOT).as_posix() not in tracked:
            raise RuntimeError(f'Untracked implementation file: {path}')
    return head


def prepare_engine(config, work):
    tree = HERE/'_components'
    manifest = json.loads((HERE/'engine_manifest.json').read_text(encoding='utf-8'))
    records=[]
    for relative, expected in manifest['files'].items():
        path=(HERE/relative).resolve()
        if not path.is_relative_to(HERE) or sha(path)!=expected:
            raise RuntimeError(f'Integrated source integrity mismatch: {relative}')
        records.append({'path':path.relative_to(ROOT).as_posix(),'sha256':expected})
    return tree, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    config_path, config = load_config(args.config)
    if os.name != 'nt' or sys.version_info[:2] != (3, 13) or sys.prefix == sys.base_prefix:
        raise RuntimeError('Run with Python 3.13 in the repository Windows .venv')
    packages = {name: importlib.metadata.version(name) for name in ['kickmix','numpy','scipy']}
    if packages != {'kickmix':'1.0.0','numpy':'2.5.4','scipy':'1.18.1'}:
        raise RuntimeError(f'Package versions differ from repository pins: {packages}')
    head = check_committed(config_path)
    artifact_dir = ROOT/'artifacts'/TRACK/EXPERIMENT
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact = artifact_dir/(config_path.stem+'.kmb')
    if artifact.exists():
        raise FileExistsError(f'Output already exists: {artifact}; preserve it and use a new config')
    work = Path(tempfile.mkdtemp(prefix='build-', dir=artifact_dir))
    tree, dependencies = prepare_engine(config, work)
    env = {**os.environ, 'PYTHONUTF8':'1', 'PYTHONIOENCODING':'utf-8', 'PYTHONDONTWRITEBYTECODE':'1', 'OPENBLAS_NUM_THREADS':'1',
           'OMP_NUM_THREADS':'1', 'MKL_NUM_THREADS':'1'}
    for key in ['DIVIDER_FORCE_CAP','DIVIDER_PLACEHOLDER','DIVIDER_RETIRE','LD_FIRST_JSON','LEAD_SECOND_JSON',
                'TK46_SECOND_JSON','W2_E_HOLD','W2_F_HOLD','W2_R2','W2_V10_G1','W2_V9_FORM','W2_V9_PLACEHOLDER','FG','NARROW']:
        env.pop(key, None)
    stages=[]

    def run(label, script, *arguments):
        command=[sys.executable, '-X', 'utf8', str(HERE/'circuit.py'), script.relative_to(tree).as_posix(), *map(str,arguments)]
        print(f'{label}: {script.name}', flush=True)
        with (work/(label+'.log')).open('xb') as log:
            result=subprocess.run(command, cwd=HERE, env=env, stdout=log, stderr=subprocess.STDOUT,
                                  timeout=config['stage_timeout_seconds'])
        stages.append({'stage':label,'command':[relative_path(v) if Path(str(v)).is_absolute() else str(v) for v in command],
                       'command_base':'.','cwd':HERE.relative_to(ROOT).as_posix(),
                       'returncode':result.returncode})
        if result.returncode:
            raise RuntimeError(f'{label} failed ({result.returncode}); see {work/(label+".log")}')

    patch_args=[]; posts=[]; width=None
    for line in 'patch patch_fwd_narrow.py\npatch patch_w47_body.py\npatch patch_endpoint_v9e2.py\npatch patch_hret_sat_s15k7a.py\npatch patch_seedinv.py\npatch patch_coefdisp.py\npatch patch_coef2_q46.py\npatch patch_h2ret.py\npatch patch_proddisp.py\npatch patch_donor_first60.py\npatch patch_ld_first20_56b8.py\npatch patch_second46_c19_70nb1.py\npatch patch_q47_decoder_resynth2.py\nwith patch_endpoint_walk8.py\nwith q46_loaders.py\nQ 46\npost agents/micro47/scripts/relocate_cs2.py\n'.splitlines():
        kind, name=line.split(maxsplit=1)
        if kind=='patch': patch_args.extend(['--patch',tree/'patches'/name])
        elif kind=='post': posts.append(tree/name)
        elif kind=='Q': width=int(name)
        elif kind!='with': raise ValueError(f'Unknown patch order entry: {line}')
    if width!=46 or len(patch_args)!=26 or len(posts)!=1:
        raise RuntimeError('Unexpected author build plan')
    raw=work/'raw'; final=work/'final';final.mkdir()
    run('01_generator',tree/'tools/build_variant.py','--out',raw,'--name','raw','--Q',width,*patch_args)
    tools=tree/'tools'
    run('02_affine',tools/'audit_affine.py',raw/'raw.kmx','--out',final/'s1.audit.json')
    run('03_pairs',tools/'audit_pairs.py',raw/'raw.kmx','--live',final/'s1.audit.live.npy','--out',final/'s1.pairs.json')
    run('04_hold',tools/'hold_pass.py',raw/'raw.kmx',final/'s1.pairs.json','--out',final/'s2.kmx','--Q',width)
    current=final/'s2.kmx'
    for index in range(1,5):
        audit=final/f'r{index}.audit.json'
        run(f'05_affine_{index}',tools/'audit_affine.py',current,'--out',audit)
        if not json.loads(audit.read_text())['findings']: break
        following=final/f'r{index}.kmx'
        run(f'06_rewrite_{index}',tools/'postpass.py',current,audit,'--out',following)
        current=following
    run('07_merge_zpow',tools/'merge_zpow.py',current,'--out',final/'zpow.kmx')
    run('08_compile_prepost',tools/'kmx_to_kmb.py',final/'zpow.kmx','--out',final/'prepost.kmb')
    run('09_relocate',posts[0],final/'zpow.kmx',final/'final_text.kmx')
    run('10_compile',tools/'kmx_to_kmb.py',final/'final_text.kmx','--out',final/'reconstructed.kmb')
    output=final/'reconstructed.kmb'
    got=sha(output)
    write_json(work/'adapter_build.json',{'source_commit':head,'stages':stages,'dependencies':dependencies,
               'sha256':got,'expected_sha256':config['expected_sha256'],'official_verifier':False,
               'author_final_proof_run':False,'unix_rlimits_enforced':False})
    if got!=config['expected_sha256']:
        raise RuntimeError(f'MISMATCH: {got}; retained outputs in {work}')
    with artifact.open('xb') as dest, output.open('rb') as source:
        shutil.copyfileobj(source,dest)
    run_id=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-exact-'+work.name[6:]
    record=ROOT/'results'/TRACK/EXPERIMENT/config_path.stem/'build_only'/run_id
    record.mkdir(parents=True,exist_ok=False)
    environment={'python':sys.version,'platform':platform.platform(),'packages':packages,
                 'executable':relative_path(sys.executable),'unix_rlimits_enforced':False}
    provenance={'track':TRACK,'experiment_id':EXPERIMENT,'config_name':config_path.stem,'source_commit':head,
        'source_path':(HERE/'solution.py').relative_to(ROOT).as_posix(),'source_sha256':sha(HERE/'solution.py'),
        'build_config_path':config_path.relative_to(ROOT).as_posix(),'build_config_sha256':sha(config_path),
        'artifact_path':artifact.relative_to(ROOT).as_posix(),'artifact_sha256':sha(artifact),
        'build_command':build_command(config_path),
        'build_command_base':'.',
        'environment':environment,'build_run':None,'dependency_hashes':dependencies,
        'adapter_work_directory':work.relative_to(ROOT).as_posix()}
    write_json(record/'provenance.json',provenance)
    write_json(record/'build.json',{'status':'BUILT','artifact_sha256':got,'bytes':artifact.stat().st_size,
        'expected_hash_matches':True,'official_verifier':False,'author_final_proof_run':False,
        'limitations':['Independent byte comparison with original is recorded separately.','No grading run.']})
    shutil.copyfile(final/'reconstructed.build.json',record/'author_compile_report.json')
    shutil.copyfile(work/'adapter_build.json',record/'adapter_build.json')
    print(json.dumps({'status':'BUILT','artifact':str(artifact),'sha256':got,'run':str(record)},indent=2))


if __name__ == '__main__':
    main()
