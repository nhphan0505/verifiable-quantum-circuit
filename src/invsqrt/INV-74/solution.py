"""Build the fixed INV-74 Q44 circuit and record exact-build provenance.

The implementation is explicitly GATE_LEVEL_PYTHON. It preserves all gates,
measurement slots, rational angles, condition scopes and register declarations;
it does not claim recovered arithmetic, numerical approximation bounds, or a
new verifier PASS. The expected phase contract is supplied by the invsqrt
verifier, not established by the transcription itself. See DESCRIPTION.md.

Run with repository-pinned Python 3.13:
python src/invsqrt/INV-74/solution.py --config src/invsqrt/INV-74/configs/reconstructed.json
Inputs are only committed circuit.py/config and pinned runtime packages.
Original KMB/KMX, scratch, bundles and external files are never build inputs.
Output/provenance are new paths; existing outputs are never overwritten.
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
    args = parser.parse_args()
    config = args.config.resolve()
    if config.parent != (here/'configs').resolve() or config.name != 'reconstructed.json':
        raise ValueError('Only configs/reconstructed.json within this experiment is supported')
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError('Use Python 3.13')
    packages = {p: importlib.metadata.version(p) for p in ('kickmix', 'numpy', 'scipy')}
    if packages != {'kickmix':'1.0.0','numpy':'2.5.4','scipy':'1.18.1'}:
        raise RuntimeError('Install repository requirements.txt pins')
    def git(*command):
        return subprocess.check_output(['git', *command], cwd=root)
    if git('status','--porcelain').strip():
        raise RuntimeError('Build requires a clean committed checkout')
    commit = git('rev-parse','HEAD').decode().strip()
    inputs = [here/'solution.py', here/'circuit.py', here/'arithmetic_prefix.py',
              here.parent/'INV-51/circuit.py', config, root/'requirements.txt']
    records = []
    for path in inputs:
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if data != git('show',commit+':'+relative):
            raise RuntimeError('Input differs from committed snapshot: '+relative)
        records.append({'path':relative,'sha256':digest(data)})
    settings = json.loads(config.read_text(encoding='utf8'))
    target = {'expected_sha256':'47b318383a03c52e08a5c222c5600fd52e004b468f53fad038082fc0f26386ef','expected_bytes':200369}
    if settings != target:
        raise ValueError('Config must describe the fixed Q44 target')
    output = root/f'artifacts/{track}/{experiment_id}/{config.stem}.kmb'
    if output.exists():
        raise FileExistsError(output)
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-exact-'+uuid.uuid4().hex[:8]
    run = root/f'results/{track}/{experiment_id}/{config.stem}/build_only/{run_id}'
    run.mkdir(parents=True,exist_ok=False)
    output.parent.mkdir(parents=True,exist_ok=True)
    runtime_roots = {Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()}
    reads, writes, imports = set(),set(),set()
    def permitted(path):
        return path in inputs or path == output or path.is_relative_to(run) or any(path.is_relative_to(p) for p in runtime_roots)
    def audit(event, arguments):
        if event.startswith('socket.') or event in ('subprocess.Popen','os.system'):
            raise RuntimeError('No network/subprocess permitted during construction')
        if event == 'import' and len(arguments)>1 and isinstance(arguments[1],str):
            path = Path(arguments[1]).resolve()
            if not permitted(path):
                raise RuntimeError('Import outside declared inputs/runtime: '+str(path))
            imports.add(str(path))
        if event != 'open' or not isinstance(arguments[0],(str,bytes,os.PathLike)):
            return
        path = Path(os.fsdecode(arguments[0])).resolve()
        mode,flags = arguments[1],arguments[2] or 0
        writing = (isinstance(mode,str) and any(c in mode for c in 'wax+')) or bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
        if writing:
            if path != output and not path.is_relative_to(run):
                raise RuntimeError('Write outside fresh output: '+str(path))
            writes.add(str(path))
        else:
            if not permitted(path):
                raise RuntimeError('Read outside declared inputs/runtime: '+str(path))
            reads.add(str(path))
    # Point cache probes into this fresh run; never read checkout cache files.
    sys.pycache_prefix = str(run / "disabled-cache")
    sys.dont_write_bytecode = True
    sys.addaudithook(audit)
    from circuit import build_circuit
    circuit = build_circuit()
    buffer = io.BytesIO()
    circuit.to_file(buffer,format='kmb')
    data = buffer.getvalue()
    if len(data) != target['expected_bytes'] or digest(data) != target['expected_sha256']:
        raise RuntimeError('Generated circuit mismatches target: '+digest(data))
    with output.open('xb') as stream:
        stream.write(data)
    def write(name,value):
        (run/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
    hashes = {r['path']:r['sha256'] for r in records}
    source_relative = (here/'solution.py').relative_to(root).as_posix()
    config_relative = config.relative_to(root).as_posix()
    write('dependency_audit.json',{'mechanism':'CPython open/import audit; network and subprocess denied during construction','inputs_checked_against_commit':records,'read_paths':sorted(reads),'write_paths':sorted(writes),'import_paths':sorted(imports),'limitations':['interpreter startup and Git preflight precede audit','native runtime internal OS reads are outside CPython hooks']})
    write('provenance.json',{'track':track,'experiment_id':experiment_id,'config_name':config.stem,'source_commit':commit,'source_path':source_relative,'source_sha256':hashes[source_relative],'build_config_path':config_relative,'build_config_sha256':hashes[config_relative],'artifact_path':output.relative_to(root).as_posix(),'artifact_sha256':digest(data),'build_command':[sys.executable,*sys.argv],'build_run':None,'environment':{'python':sys.version,'platform':sys.platform,'packages':packages,'dependencies':records},'reconstruction_level':'GATE_LEVEL_PYTHON','dependency_audit':'dependency_audit.json'})
    write('reconstruction_check.json',{'status':'RECONSTRUCTED_EXACT','source_commit':commit,'input_sha256':target['expected_sha256'],'input_bytes':target['expected_bytes'],'output_sha256':digest(data),'output_bytes':len(data),'comparison':'generated bytes match separately measured input byte length and SHA-256; separate comparison should also compare every byte','reconstruction_level':'GATE_LEVEL_PYTHON','num_qubits':circuit.num_qubits,'num_bits':circuit.num_bits,'limitations':['Arithmetic generator not recovered','No verifier run or score established','Original input not read during construction']})
    print(json.dumps({'artifact':str(output),'sha256':digest(data),'bytes':len(data),'run':str(run),'source_commit':commit}))


if __name__ == '__main__':
    main()
