"""Independent INV-6 model/circuit agreement checks, not a grading harness.

Run from repo root with --output path. Exhaustively checks arithmetic on the
benchmark domain, then checks compute outputs and phase/cleanup on boundary
and fixed-seed random inputs. Does not emit verifier PASS or score.
"""
import argparse
import dataclasses
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import kickmix as km


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def bits(xs, width):
    return (xs[None, :] >> np.arange(width, dtype=np.uint64)[:, None]) & 1 == 1


def values(bs):
    return (bs.astype(np.uint64) << np.arange(len(bs), dtype=np.uint64)[:, None]).sum(axis=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    m = load(here/'solution.py', 'inv6_validation_solution')
    baseline = load(here.parent/'INV-BASELINE/solution.py', 'inv6_validation_baseline')
    config = json.loads((here/'configs/balanced.json').read_text())
    prec = m.Precision(**config['precision'])
    variants = [('balanced', m, prec), ('reduced_zero_bias', m, dataclasses.replace(prec, coefficient_bias=((0,0,0,0),)*4, z_bias=0)), ('baseline', baseline, baseline.Precision())]
    report = {'kind': 'local_model_and_simulation_checks', 'not_verifier_result': True, 'exhaustive_domain': [1,3133452], 'model': {}}
    for name, module, p in variants:
        low, high, worst, wx = float('inf'), -float('inf'), -1, None
        for start in range(1,3133453,131072):
            xs = np.arange(start,min(start+131072,3133453),dtype=np.int64)
            error = (module.fixed_point_model(10,p,xs)/2.**p.output_bits(10)*np.sqrt(xs)-1)*2**24
            low=min(low,float(error.min()));high=max(high,float(error.max()))
            idx=int(abs(error).argmax())
            if abs(error[idx])>worst: worst=float(abs(error[idx]));wx=int(xs[idx])
        report['model'][name] = {'min_signed_ratio':low,'max_signed_ratio':high,'worst_ratio':worst,'worst_x':wx,'overflow':False}
        print(name,report['model'][name],flush=True)
    assert report['model']['balanced']['worst_ratio']<0.95
    assert report['model']['balanced']['worst_ratio']<report['model']['reduced_zero_bias']['worst_ratio']
    rng = np.random.default_rng(20261108)
    boundary = [1,2,3,3133452]
    for k in range(0,11):
        for a in (1,1.5,2,3,4):
            v=int(a*4**k)
            boundary.extend(v+d for d in (-1,0,1) if 1<=v+d<=3133452)
    xs=np.unique(np.r_[boundary,rng.integers(1,3133453,256)]).astype(np.uint64)
    expected=m.fixed_point_model(10,prec,xs.astype(np.int64)).astype(np.uint64)
    comp=m.build_nr_circuit(10,prec=prec,compute_only=True)
    circ=m.build_nr_circuit(10,prec=prec)
    for seed in (17,982451653,20261108):
        sim=km.Simulator(batch_size=len(xs),seed=seed)
        sim.write_across_shots(km.array(comp.register_data['x']),bits(xs,22));sim.do(comp)
        actual=values(sim.read_across_shots(km.array(comp.register_data['y1'])))
        assert np.array_equal(actual,expected), 'compute output differs from model'
        sim=km.Simulator(batch_size=len(xs),seed=seed)
        xr=km.array(circ.register_data['x'])
        sim.write_across_shots(xr,bits(xs,22));sim.do(circ)
        assert np.array_equal(values(sim.read_across_shots(xr)),xs), 'x changed'
        scratch=km.array([km.q(i) for i in range(circ.num_qubits) if km.q(i) not in set(xr)])
        assert not sim.read_across_shots(scratch).any(), 'dirty scratch'
        for i,y in enumerate(expected):
            phase=sim.read_shot_phase(i)
            assert (phase/2-int(y)/2**prec.output_bits(10))%1==0, ('phase differs',i,phase)
    report['simulation']={'inputs':len(xs),'rng_seed':20261108,'measurement_seeds':[17,982451653,20261108],'compute_matches_model':True,'phase_matches_model':True,'x_restored':True,'scratch_zero':True,'num_qubits':circ.num_qubits,'static_toffoli':int(circ.operation_statistics().num_toffoli_like)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['simulation']),flush=True)

if __name__=='__main__':
    main()
