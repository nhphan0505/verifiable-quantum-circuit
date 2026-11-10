"""DQI-43: combine packed Schur extraction/conversion with rank-42 products.

Sources: DQI-23 c5b70b1a7618057000cc9af35794c8e733e5eb1c and DQI-19
c0cf9dfb45b62ba7eeb8588c87b0066409880046, Apache-2.0 (src/LICENSE.txt).
Read-only helpers are checked against pinned byte hashes before loading.
Only SchurDecoder.multiply_add changes: arbitrary target ^= control*lhs*rhs
uses 12 temporary masked-input ANDs and 42 bilinear ANDs, with X measurement
and CZ phase correction supplied by native del_and. Inputs/control remain
unchanged through cleanup; every temporary returns to zero. Factors, target
and control must be disjoint. A host True control uses 42 unmasked ANDs.

The field is exactly Kickmix GF(2^12); no rounding, valuation cutoff, or
offline mask fitting is used. Keep the original Schur reciprocal, routing,
normalization, norm-to-GF(64) inverse, square_add, Chien/Forney runtime-mask
phase, and inverse extraction/conversion. Syndrome words are restored and
ancilla must be clean. Added parity scratch can increase peak qubits; measure
the whole circuit rather than treating a primitive T saving as score saving.

Component validation independently checks the bilinear tensor, arbitrary
target/control values, input restoration, phase and workspace, plus field12
decoders with forced valuation jumps. It is not official decoder grading.
Use Python 3.13 and pinned packages from repo root:
  python src/dqi/DQI-43/solution.py --config src/dqi/DQI-43/configs/schur_rank42.json
  python src/dqi/DQI-43/solution.py --validate-components
Source/config must be committed before submission compilation. Config must
resolve directly under this ID's configs/. Artifacts default to the inferred
track/ID and config stem; deliberate rebuilds require --overwrite. The member
runs the unchanged notebook grader after BUILT/provenance handoff.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import time

import kickmix as km

EXPERIMENT = Path(__file__).resolve().parent
ROOT = EXPERIMENT.parents[2]
DEPENDENCIES = {
    'schur': ('DQI-23', '18f7e197dc832236b95cef3b87013cce15373d7327554efb1fdb2bd2f618f492'),
    'rank42': ('DQI-19', '3798b608825c8ca741aaf4cf1d7913d87b650f2be55242a35dc769b8cd47c298'),
}


def load_helper(name):
    experiment_id, expected = DEPENDENCIES[name]
    path = EXPERIMENT.parent / experiment_id / 'solution.py'
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f'Pinned {experiment_id} helper changed')
    spec = importlib.util.spec_from_file_location('dqi43_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCHUR = load_helper('schur')
RANK42 = load_helper('rank42')


def multiply_add(builder, lhs, rhs, target, control):
    """Exact arbitrary-target rank-42 update, with disjoint live factors."""
    if any(len(word) != 12 for word in (lhs, rhs, target)):
        raise ValueError('Rank-42 requires three 12-bit words')
    sets = [set(word) for word in (lhs, rhs, target)]
    if any(sets[i] & sets[j] for i in range(3) for j in range(i)):
        raise ValueError('Rank-42 operands and target must be disjoint')
    if control is not True and any(control in word for word in sets):
        raise ValueError('Control must be disjoint from all operands')
    if control is True:
        scratch = builder.alloc_qubits(3)
        a, b, term = scratch
        previous_l = previous_r = 0
        for left, right, output in RANK42.rank42_tensor():
            RANK42._xor_mask(builder, lhs, left ^ previous_l, a)
            RANK42._xor_mask(builder, rhs, right ^ previous_r, b)
            builder.init_and(a, b, term)
            builder.cx(term, km.array([target[i] for i in range(12) if output >> i & 1]))
            builder.del_and(a, b, term)
            previous_l, previous_r = left, right
        RANK42._xor_mask(builder, lhs, previous_l, a)
        RANK42._xor_mask(builder, rhs, previous_r, b)
        builder.free(scratch)
    else:
        RANK42.rank42_ixor(builder, lhs, rhs, target=target, field=km.GF2Field(12),
                          control=control, strategy='control_input')


class SchurRank42(SCHUR.SchurDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.gf.degree != 12 or self.gf.modulus != km.GF2Field(12).modulus:
            raise ValueError('This experiment only supports the pinned GF(2^12)')
        self.product_calls = 0

    def multiply_add(self, lhs, rhs, target, control):
        self.product_calls += 1
        multiply_add(self.b, lhs, rhs, target, control)


def build_circuit(m, n, degree, *, metrics=None):
    if degree != 12 or not (2 <= n <= m <= 4095 and n % 2 == 0):
        raise ValueError('Require degree=12, even n and 2<=n<=m<=4095')
    b = km.CircuitBuilder()
    syndromes = [b.create_quantum_register(12, f'S{i}') for i in range(n)]
    masks = [b.create_classical_register(12, f'E{j}') for j in range(m)]
    decoder = SchurRank42(b, km.GF2Field(12), syndromes, masked_cleanup='hmr')
    if metrics is None:
        decoder.build(masks)
    else:
        cursor = b.alloc_qubits(decoder.capacity.bit_length())
        previous_t = previous_ops = previous_calls = 0
        def record(name):
            nonlocal previous_t, previous_ops, previous_calls
            c = b.finish_circuit(); stats = c.operation_statistics()
            metrics[name] = {'static_toffoli_like': stats.num_toffoli_like - previous_t,
                             'instructions': stats.num_instructions - previous_ops,
                             'multiply_add_calls': decoder.product_calls - previous_calls,
                             'qubits_allocated_so_far': c.num_qubits}
            previous_t, previous_ops = stats.num_toffoli_like, stats.num_instructions
            previous_calls = decoder.product_calls
            print(json.dumps({'stage': name, **metrics[name]}), flush=True)
        with b.mark('forward_schur'):
            decoder.extraction(cursor); decoder.conversion()
        record('forward_schur')
        with b.mark('chien_forney'):
            decoder.phase(masks)
        record('chien_forney')
        with b.mark('reverse_schur'):
            decoder.conversion(reverse=True); decoder.extraction(cursor, reverse=True)
        record('reverse_schur')
        b.free(cursor)
    return b.finish_circuit()


def validate_components():
    """Field12 tensor/kernel and reduced decoder checks, not a grader."""
    import numpy as np
    gf = km.GF2Field(12)
    terms = RANK42.rank42_tensor()
    for i in range(12):
        for j in range(12):
            actual = 0
            for left, right, output in terms:
                if (left >> i & 1) and (right >> j & 1): actual ^= output
            assert actual == gf.mul(1 << i, 1 << j), 'Bilinear tensor mismatch'
    def bits(values):
        return np.array([(values >> i) & 1 for i in range(12)], dtype=bool)
    def clean(sim, circuit, input_count):
        anc = km.array([km.q(i) for i in range(input_count, circuit.num_qubits)])
        assert not sim.read_across_shots(anc).any(), 'Dirty workspace'
    def product(x, y):
        a=x.copy(); out=np.zeros_like(a)
        for i in range(12):
            out ^= np.where((y >> i) & 1, a, 0).astype(a.dtype)
            a <<= 1
            a ^= np.where(a & 4096, gf.modulus, 0).astype(a.dtype)
        return out
    report={'verification_level':'component checks, not official decoder grading',
            'tensor_basis_pairs':144,'measurement_seeds':[4301,4302,4303],'kernels':[]}
    for controlled in (False, True):
        b=km.CircuitBuilder()
        regs=[b.create_quantum_register(12,k) for k in ('x','y','z')]
        ctrl=b.create_quantum_register(1,'c')[0] if controlled else True
        multiply_add(b,*regs,ctrl); circuit=b.finish_circuit()
        assert circuit.operation_statistics().num_toffoli_like == (54 if controlled else 42)
        cases=0
        for seed in report['measurement_seeds']:
            count=65536; rng=np.random.default_rng(seed)
            x=rng.integers(0,4096,count,dtype=np.uint32)
            y=rng.integers(0,4096,count,dtype=np.uint32)
            x[:4096]=np.arange(4096); y[:4096]=0
            x[4096:8192]=0; y[4096:8192]=np.arange(4096)
            x[8192:12288]=np.arange(4096); y[8192:12288]=np.arange(4096)
            z=rng.integers(0,4096,count,dtype=np.uint32)
            p=product(x,y)
            for value in ((False,True) if controlled else (True,)):
                sim=km.Simulator(count,seed=seed,debug_print=False); sim.use_same_registers_as(circuit)
                for reg,word in zip(regs,(x,y,z)): sim.write_across_shots(reg,bits(word))
                if controlled: sim.write_across_shots(ctrl,np.full(count,value,dtype=bool))
                sim.do(circuit)
                for reg,expected in zip(regs,(x,y,z ^ p if value else z)):
                    assert np.array_equal(sim.read_across_shots(reg),bits(expected)), 'Kernel word mismatch'
                if controlled: assert np.all(sim.read_across_shots(ctrl)==value), 'Control changed'
                clean(sim,circuit,37 if controlled else 36)
                assert not sim.read_phase_flipped_across_shots().any(), 'Kernel phase mismatch'
                cases+=count
        report['kernels'].append({'controlled':controlled,'cases':cases,'qubits':circuit.num_qubits,
                                  'static_toffoli_like':circuit.operation_statistics().num_toffoli_like})
    report['decoders']=[]
    for n in (2,4,8):
        m=15
        circuit=build_circuit(m,n,12)
        for seed in report['measurement_seeds']:
            count=128; rng=np.random.default_rng(seed)
            syndrome=np.zeros((n,count),dtype=np.uint32)
            masks=rng.integers(0,4096,(m,count),dtype=np.uint32)
            phase=np.zeros(count,dtype=bool)
            for case in range(count):
                weight=case%(n//2+1)
                positions=list(map(int,rng.choice(m,weight,replace=False)))
                values=list(map(int,rng.integers(1,4096,weight)))
                if case==0: positions=[]; values=[]
                elif case==1: positions=[0]; values=[1]
                elif case==2: positions=[m-1]; values=[4095]
                elif 3<=case<3+n//2:
                    weight=case-2; positions=list(range(weight)); values=[]
                    roots=[gf.pow(gf.primitive_element,j) for j in positions]
                    for i,a in enumerate(roots):
                        den=a
                        for j,other in enumerate(roots):
                            if i!=j: den=gf.mul(den,a ^ other)
                        values.append(gf.invert(den))
                for j,e in zip(positions,values):
                    for i in range(n): syndrome[i,case]^=gf.mul(e,gf.pow(gf.primitive_element,(i+1)*j))
                    phase[case]^=bool((e & int(masks[j,case])).bit_count()&1)
            sim=km.Simulator(count,seed=seed,debug_print=False); sim.use_same_registers_as(circuit)
            for i in range(n): sim.write_across_shots(circuit.register_data[f'S{i}'],bits(syndrome[i]))
            for j in range(m): sim.write_across_shots(circuit.register_data[f'E{j}'],bits(masks[j]))
            sim.do(circuit)
            for i in range(n):
                assert np.array_equal(sim.read_across_shots(circuit.register_data[f'S{i}']),bits(syndrome[i])), 'Syndrome not restored'
            clean(sim,circuit,n*12)
            assert np.array_equal(sim.read_phase_flipped_across_shots(),phase), 'Decoder phase mismatch'
        report['decoders'].append({'degree':12,'m':m,'n':n,'cases':384,'forced_valuation_jumps':list(range(1,n//2+1)),
                                   'qubits':circuit.num_qubits,'static_toffoli_like':circuit.operation_statistics().num_toffoli_like})
    report.update(value_errors=0,phase_errors=0,workspace_errors=0,
                  limitations=['Seeded measurement checks do not enumerate all outcomes.',
                               'Reduced decoders cover weights through 4; full-size weight 35 and long jumps remain for member grading.',
                               'No official dev/full verifier invoked.'])
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=EXPERIMENT/'configs/schur_rank42.json')
    parser.add_argument('--validate-components',action='store_true')
    parser.add_argument('--overwrite',action='store_true')
    args=parser.parse_args()
    path=args.config.resolve()
    if path.parent!=(EXPERIMENT/'configs').resolve() or path.suffix!='.json' or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',path.stem):
        raise ValueError('Use a named JSON config directly in this experiment configs/')
    config=json.loads(path.read_text(encoding='utf-8'))
    if config!={'m':4095,'n':70,'degree':12,'multiplication_strategy':'control_input','masked_cleanup':'hmr'}:
        raise ValueError('Only the predeclared exact Schur rank-42 config is supported')
    if args.validate_components:
        print(json.dumps(validate_components(),indent=2)); return
    output=ROOT/'artifacts'/EXPERIMENT.parent.name/EXPERIMENT.name/(path.stem+'.kmb')
    if output.exists() and not args.overwrite: raise FileExistsError(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    started=time.monotonic(); stages={}
    circuit=build_circuit(config['m'],config['n'],config['degree'],metrics=stages)
    stats=circuit.operation_statistics()
    if circuit.num_qubits>910 or circuit.num_qubits**2*stats.num_toffoli_like>=900**2*11620060:
        raise ValueError('Predeclared Q/static resource screening failed')
    temporary=output.with_suffix('.kmb.part')
    try:
        circuit.to_file(str(temporary),format='kmb'); temporary.replace(output)
    finally: temporary.unlink(missing_ok=True)
    print(json.dumps({'status':'BUILT','qubits':circuit.num_qubits,'static_toffoli_like':stats.num_toffoli_like,
                      'instructions':stats.num_instructions,'artifact_bytes':output.stat().st_size,
                      'elapsed_seconds':time.monotonic()-started,'stages':stages}),flush=True)


if __name__=='__main__': main()
