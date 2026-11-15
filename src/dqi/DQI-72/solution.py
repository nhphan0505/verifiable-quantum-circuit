"""Rebuild the supplied DQI v7 circuit from readable Python gate emitters.

The fixed decoder accepts seventy little-endian 12-bit quantum syndrome words
S0..S69 and 4095 classical mask words E0..E4094. It applies the Reed-Solomon
error/mask phase and restores syndrome/workspace using the upstream adaptive
gauge, retained-norm extraction, synthesis, converter, scan and reverse schedule.
The emitters retain measurement cleanup and conditional phase corrections;
no numerical precision, compiler schedule or gate optimization is changed.

Only the upstream path/provenance bootstrap is replaced. Decoder modules are
ordinary tracked Python files; the build reads no original KMB/KMX, external
bundle or historical build cache. Every Python file-open is checked and recorded
against checkout/runtime roots. Exactness is checked separately after emission;
the static assertions here do not constitute verifier PASS.

Run with Python 3.13 and the repository-pinned requirements:
python src/dqi/DQI-72/solution.py --config src/dqi/DQI-72/configs/reconstructed.json
The default artifact path is inferred from this file and the config stem.
Use a fresh output directory; existing artifacts/reports are never overwritten.
Copyright in derived emitters remains with Syed Asad Ali; see LICENSE/NOTICE.
"""
from pathlib import Path
import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TRACK = HERE.parent.name
EXPERIMENT = HERE.name


def digest(path):
    """Hash a generated artifact using bounded memory."""
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    """Emit one fixed circuit and record the actual dependency read set."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 13) or not __debug__:
        parser.error('Use ordinary Python 3.13 without optimization.')
    config = args.config.resolve(strict=True)
    if config.parent != (HERE / 'configs').resolve() or config.suffix != '.json':
        parser.error('Config must resolve directly inside this experiment configs directory.')
    output = (args.output or REPO/'artifacts'/TRACK/EXPERIMENT/(config.stem+'.kmb')).resolve()
    if output.suffix != '.kmb':
        parser.error('Output must end in .kmb.')
    audit_path = output.with_suffix('.file-audit.json')
    report_path = output.with_suffix('.build.json')
    if any(path.exists() for path in (output, audit_path, report_path)):
        parser.error('Use a new artifact path; existing output/report/audit is preserved.')
    output.parent.mkdir(parents=True, exist_ok=True)
    runtime_roots = tuple(dict.fromkeys(Path(p).resolve() for p in (sys.prefix, sys.base_prefix)))
    accesses = {}

    def audit(event, values):
        if event == 'subprocess.Popen':
            raise RuntimeError('This emitter does not use subprocesses.')
        if event != 'open' or not isinstance(values[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(values[0])).resolve()
        mode = values[1]
        flags = values[2] or 0
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        if writing:
            if path not in (output, audit_path, report_path):
                raise RuntimeError(f'Unexpected build write: {path}')
        elif not path.is_relative_to(REPO) and not any(path.is_relative_to(root) for root in runtime_roots):
            raise RuntimeError(f'Input outside checkout/runtime: {path}')
        accesses.setdefault((str(path), 'write' if writing else 'read'), 0)
        accesses[(str(path), 'write' if writing else 'read')] += 1

    sys.dont_write_bytecode = True
    sys.addaudithook(audit)
    settings = json.loads(config.read_text(encoding='utf-8'))
    expected = dict(schema_version=1, j_min=15, scan_positions=4095,
                    max_qubits=889, expected_static_toffoli=384003,
                    expected_instructions=52930855, expected_classical_bits=53911)
    if settings != expected:
        parser.error('Only the fixed reconstructed configuration is supported.')
    packages = {name: importlib.metadata.version(name) for name in ('kickmix', 'numpy', 'scipy')}
    if packages != {'kickmix':'1.0.0', 'numpy':'2.5.4', 'scipy':'1.18.1'}:
        parser.error('Install the repository-pinned requirements.')
    sys.path.insert(0, str(HERE/'decoder'))
    import kickmix as km
    import v7_pipeline as pipeline
    pipeline.configure()
    started = time.monotonic()
    stages = []

    def stage(value):
        row = dict(stage=value, elapsed_seconds=time.monotonic()-started)
        stages.append(row)
        print(json.dumps(row), flush=True)

    builder = km.CircuitBuilder()
    builder.set_max_qubits(settings['max_qubits'])
    syndromes = [builder.create_quantum_register(12, f'S{i}') for i in range(70)]
    masks = [builder.create_classical_register(12, f'E{i}') for i in range(4095)]
    contract = pipeline.emit(builder, syndromes, masks, j_min=settings['j_min'],
                             scan_positions=settings['scan_positions'], stage=stage)
    assert builder.num_allocated_qubits == 840
    circuit = builder.finish_circuit()
    del builder
    gc.collect()
    stats = circuit.operation_statistics()
    assert circuit.num_qubits == settings['max_qubits']
    assert circuit.num_bits == settings['expected_classical_bits']
    assert len(circuit) == settings['expected_instructions']
    assert stats.num_toffoli_like == settings['expected_static_toffoli']
    assert dict(stats).get('Z_POW', 0) == 0
    summary = dict(num_qubits=circuit.num_qubits, num_bits=circuit.num_bits,
                   instructions=len(circuit), static_toffoli_like=stats.num_toffoli_like,
                   operation_statistics=dict(stats))
    # Kickmix writes in native code, so explicitly include this output in the audit.
    accesses[(str(output), 'native_write')] = 1
    circuit.to_file(output, format='kmb')
    del circuit
    gc.collect()
    report = dict(status='BUILT', track=TRACK, experiment_id=EXPERIMENT,
                  config_name=config.stem, artifact_sha256=digest(output),
                  artifact_bytes=output.stat().st_size, **summary,
                  environment=dict(python=sys.version, platform=platform.platform(), packages=packages),
                  build_command=[sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                  cwd=str(Path.cwd()), elapsed_seconds=time.monotonic()-started,
                  contract=contract, stages=stages,
                  limitations=['No verifier run', 'Exact comparison is a separate operation'])
    with report_path.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    with audit_path.open('x', encoding='utf-8') as stream:
        json.dump(dict(checkout=str(REPO), runtime_roots=[str(p) for p in runtime_roots],
                       entrypoint=str(Path(__file__).resolve()), subprocesses_allowed=False,
                       accesses=[dict(path=p, operation=op, count=n) for (p,op),n in sorted(accesses.items())],
                       scope='Python audit open events; native artifact output explicitly recorded'),
                  stream, indent=2); stream.write('\n')
    print(json.dumps({k:report[k] for k in ('status','artifact_sha256','artifact_bytes','num_qubits','static_toffoli_like')}), flush=True)


if __name__ == '__main__':
    main()
