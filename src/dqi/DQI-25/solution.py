"""DQI-25: cache repeated EEA control products with X-measurement cleanup.

Inherits DQI-19 at c0cf9df (Apache-2.0, src/LICENSE.txt), hash checked at
import. Keeps rank42 control_input arithmetic, 222 main EEA steps and native
Chien/Forney. Only the adjacent shift/metadata/swap tail is rewritten.
Two clean bits hold ctrl[0]*(1+flag), ctrl[3]*(1+flag). These inputs never
change throughout that tail, including either step ordering. Shift and
metadata reuse those bits; swap uses ctrl[3]+cached[1]=ctrl[3]*flag.
Cleanup restores the complemented flag, calls del_and with original inputs,
then restores flag. Kickmix del_and implements HMR with CZ phase correction.
No quantum-controlled measurement, approximate arithmetic, dirty cache or
assumption that ctrl is one-hot is used. Cache lives only within the tail;
builder reserves its wires and must show full peak Q no larger than reference.
Savings predicted: 3 init_and per step, 444 forward/reverse steps =1332 T.
No repeated quadratic forms occur in the 42-term tensor on independent input
bits; this conservative first config uses a proved local control-product
reuse instead of speculative cross-multiplier equivalence.

Run Python 3.13 with pinned packages from repo root:
  ./.venv/bin/python src/dqi/DQI-25/solution.py --config src/dqi/DQI-25/configs/control_cache.json
--validate-segments runs component value/phase/cleanup comparisons only;
--audit-tensor proves normalized quadratic signatures are distinct.
Neither action runs a grader or creates a decoder PASS. Member grades local.
Config resolves directly under this experiment; TRACK/ID/output inferred
from __file__. Commit source/config before submission build. Artifact ignored.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import kickmix as km

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HELPER = ROOT / 'src/dqi/DQI-19/solution.py'
HELPER_SHA256 = '3798b608825c8ca741aaf4cf1d7913d87b650f2be55242a35dc769b8cd47c298'
if hashlib.sha256(HELPER.read_bytes()).hexdigest() != HELPER_SHA256:
    raise ValueError('DQI-19 helper differs from pinned source')
spec = importlib.util.spec_from_file_location('dqi25_parent', HELPER)
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)
_active, _xor_threshold = parent._active, parent._xor_threshold

class CachedDecoder(parent.ProosAndZalkaDecoder):
    """Retain two control products across three adjacent EEA tail operations."""
    def _cached_tail(self, builder, reg_a, reg_b, n_A, n_B, n_a, n_b,
                     n_q, flag, ctrl, it, *, is_adjoint):
        cache = builder.alloc_qubits(2)
        builder.x(flag)
        builder.init_and(km.array([ctrl[0], ctrl[3]]), flag, cache)
        builder.x(flag)
        self._tail_cache = cache
        steps = [
            lambda: self._shift_b_array_right(builder, reg_b, n_B, n_b, flag, ctrl, it, is_adjoint=is_adjoint),
            lambda: self._update_metadata(builder, n_B, n_b, n_q, flag, ctrl, is_adjoint=is_adjoint),
            lambda: self._swap_a_and_b(builder, reg_a, reg_b, n_A, n_B, n_a, n_b, flag, ctrl),
        ]
        for step in (reversed(steps) if is_adjoint else steps):
            step()
        builder.x(flag)
        builder.del_and(km.array([ctrl[0], ctrl[3]]), flag, cache)
        builder.x(flag)
        builder.free(cache)
        self._tail_cache = None

    def _synchronized_eea(self, builder: km.CircuitBuilder,
                          reg_a: Sequence[km.array], reg_b: Sequence[km.array],
                          n_A: km.array, n_B: km.array, n_a: km.array,
                          n_b: km.array, n_q: km.array, flag,
                          counter: km.array, halting_counter: km.array, *,
                          n_iters: int, is_adjoint: bool) -> None:
        """Runs `n_iters` steps of the reversible synchronized EEA."""
        eea_step = builder.mark('eea_step')
        for it in (range(n_iters - 1, -1, -1) if is_adjoint else range(n_iters)):
            with eea_step:
                if is_adjoint:
                    self._update_counter(builder, counter, flag, is_adjoint=True)

                is_c3 = builder.alloc_qubits(1)[0]
                builder.init_and(counter[0], counter[1], is_c3)
                if is_adjoint:
                    self._update_halting_counter(builder, n_A, n_B, n_b, halting_counter,
                                                 flag, is_c3, is_adjoint=True)

                is_hc_zero = builder.alloc_qubits(1)[0]
                builder.flip_if_equal(halting_counter, 0, target=is_hc_zero)
                ctrl = self._counter_controls(builder, counter, is_c3, is_hc_zero)

                steps = [
                    lambda: self._update_flag(builder, reg_b, n_A, n_B, n_a, n_b, n_q,
                                              flag, ctrl),
                    lambda: self._multiply_and_add_or_sub(builder, reg_a, reg_b, n_A, n_a,
                                                          n_q, ctrl, it,
                                                          is_adjoint=is_adjoint),
                    lambda: self._cached_tail(builder, reg_a, reg_b, n_A, n_B, n_a, n_b,
                                               n_q, flag, ctrl, it, is_adjoint=is_adjoint),
                ]
                for step in (reversed(steps) if is_adjoint else steps):
                    step()

                self._del_counter_controls(builder, counter, is_c3, is_hc_zero, ctrl)
                builder.flip_if_equal(halting_counter, 0, target=is_hc_zero)
                builder.free(is_hc_zero)

                if not is_adjoint:
                    self._update_halting_counter(builder, n_A, n_B, n_b, halting_counter,
                                                 flag, is_c3, is_adjoint=False)
                builder.del_and(counter[0], counter[1], is_c3)
                builder.free(is_c3)
                if not is_adjoint:
                    self._update_counter(builder, counter, flag, is_adjoint=False)


    def _shift_b_array_right(self, builder: km.CircuitBuilder,
                             reg_b: Sequence[km.array], n_B: km.array, n_b: km.array,
                             flag, ctrl, it: int, *, is_adjoint: bool) -> None:
        """Shifts the active slice of `reg_b` by one slot."""
        with builder.mark('shift_b_array_right'):
            c0_hc, c1_hc, c2_hc, c3_hc = ctrl
            m = len(reg_b)
            lim_B = m - 2
            lim_b = min(m - 2, it // 2 + 1)

            nf = self._tail_cache
            c0_nf, c3_nf = nf

            ctrl_nB = builder.alloc_qubits(1)[0]
            builder.cx(km.array([c0_nf, c1_hc]), ctrl_nB)

            order = range(1, m) if is_adjoint else range(m - 1, 0, -1)
            with (
                builder.unary_iteration(n_B, control=ctrl_nB) as cur_B_ge,
                builder.unary_iteration(n_b, control=c2_hc) as cur_b_ge,
                builder.unary_iteration(n_B, control=c3_nf) as cur_B_lt,
            ):
                do_shift = builder.alloc_qubits(1)[0]

                def endpoint(i: int) -> None:
                    _xor_threshold(builder, cur_B_ge, lim_B, do_shift, ctrl_nB, m - i + 1,
                                   at_least=True)
                    _xor_threshold(builder, cur_b_ge, lim_b, do_shift, c2_hc, i,
                                   at_least=True)
                    _xor_threshold(builder, cur_B_lt, lim_B, do_shift, c3_nf, m - i,
                                   at_least=False)

                prev = None
                for i in order:
                    if prev is None:
                        endpoint(i)
                    else:
                        builder.cx(
                            km.array([
                                _active(cur_B_ge, m - max(prev, i) + 1, lim_B),
                                _active(cur_b_ge, min(prev, i), lim_b),
                                _active(cur_B_lt, m - max(prev, i), lim_B),
                            ]),
                            do_shift,
                        )
                    prev = i
                    builder.cswap(do_shift, reg_b[i - 1], reg_b[i])

                endpoint(prev)
                builder.free(do_shift)

            builder.cx(km.array([c0_nf, c1_hc]), ctrl_nB)
            builder.free(ctrl_nB)



    def _update_metadata(self, builder: km.CircuitBuilder, n_B: km.array, n_b: km.array,
                         n_q: km.array, flag, ctrl, *, is_adjoint: bool) -> None:
        """Updates the polynomial degree registers `(n_B, n_b, n_q)`."""
        with builder.mark('update_metadata'):
            c0_hc, c1_hc, c2_hc, c3_hc = ctrl
            nf = self._tail_cache
            c0_nf, c3_nf = nf

            sign = -1 if is_adjoint else 1
            updates = [
                [(n_q, 1, c0_hc), (n_B, -1, c0_nf)],
                [(n_B, -1, c1_hc)],
                [(n_b, 1, c2_hc)],
                [(n_b, 1, c3_nf), (n_q, -1, c3_hc)],
            ]
            for step in (reversed(updates) if is_adjoint else updates):
                for target, offset, control in (reversed(step) if is_adjoint else step):
                    builder.iadd(sign * offset, target=target, control=control)




    def _swap_a_and_b(self, builder: km.CircuitBuilder, reg_a: Sequence[km.array],
                      reg_b: Sequence[km.array], n_A: km.array, n_B: km.array,
                      n_a: km.array, n_b: km.array, flag, ctrl) -> None:
        """Swaps `(reg_a, n_A, n_a)` and `(reg_b, n_B, n_b)` at the end of a division round."""
        with builder.mark('swap_a_and_b'):
            c3_hc = ctrl[3]
            swap_ctrl = builder.alloc_qubits(1)[0]
            builder.cx(km.array([c3_hc, self._tail_cache[1]]), swap_ctrl)
            lhs = km.array([q for r in (n_A, n_a, *reg_a) for q in r])
            rhs = km.array([q for r in (n_B, n_b, *reg_b) for q in r])
            builder.cswap(swap_ctrl, lhs, rhs)
            builder.cx(km.array([c3_hc, self._tail_cache[1]]), swap_ctrl)
            builder.free(swap_ctrl)


def audit_tensor():
    """Exact quadratic signatures on independent masked-lhs and rhs inputs."""
    signatures = []
    for left, right, output in parent.rank42_tensor():
        signatures.append(frozenset((i, j+12) for i in range(12) for j in range(12)
                                   if (left >> i & 1) and (right >> j & 1)))
    if len(set(signatures)) != 42:
        raise AssertionError('Unexpected duplicate tensor quadratic signature')
    return {'terms':42, 'pairs_checked':861, 'equal_quadratic_signatures':0,
            'scope':'single rank42 tensor, independent masked lhs/rhs boundary; not a global no-cache proof',
            'selected_route':'two cached EEA tail products; third affine reuse c3*flag=c3 XOR c3*(1+flag)'}


def _tail_fixture(cached, *, it, adjoint):
    builder = km.CircuitBuilder()
    degree, m, width = 3, 7, 4
    regs = {}
    def reg(name, n):
        regs[name] = builder.create_quantum_register(n, name)
        return regs[name]
    a = [reg(f'a{i}', degree) for i in range(m)]
    b = [reg(f'b{i}', degree) for i in range(m)]
    nA,nB,na,nb,nq = [reg(k,width) for k in ('nA','nB','na','nb','nq')]
    flag = reg('flag',1)[0]; ctrl=reg('ctrl',4)
    boundary=sum(len(v) for v in regs.values())
    decoder=(CachedDecoder if cached else parent.ProosAndZalkaDecoder)(4,km.GF2Field(degree),multiplication_strategy='control_input')
    if cached:
        decoder._cached_tail(builder,a,b,nA,nB,na,nb,nq,flag,ctrl,it,is_adjoint=adjoint)
    else:
        steps=[lambda: decoder._shift_b_array_right(builder,b,nB,nb,flag,ctrl,it,is_adjoint=adjoint),
               lambda: decoder._update_metadata(builder,nB,nb,nq,flag,ctrl,is_adjoint=adjoint),
               lambda: decoder._swap_a_and_b(builder,a,b,nA,nB,na,nb,flag,ctrl)]
        for step in (reversed(steps) if adjoint else steps): step()
    return builder.finish_circuit(),regs,boundary


def validate_product_identity():
    """Exhaustive Boolean inputs for the cached-product fanout/cleanup identity."""
    import numpy as np
    b=km.CircuitBuilder(); x=b.create_quantum_register(8,'input')
    c0,c3,f=x[:3]; cache=b.alloc_qubits(2)
    b.x(f); b.init_and(km.array([c0,c3]),f,cache); b.x(f)
    b.cx(cache, x[3:5]); b.cx(cache, x[5:7])
    b.cx(km.array([c3,cache[1]]),x[7])
    b.x(f); b.del_and(km.array([c0,c3]),f,cache); b.x(f)
    circuit=b.finish_circuit(); ids=np.arange(256)
    initial=np.array([(ids>>i)&1 for i in range(8)],dtype=bool)
    expected=initial.copy(); p=initial[0]&~initial[2]; q=initial[1]&~initial[2]
    expected[3]^=p; expected[4]^=q; expected[5]^=p; expected[6]^=q
    expected[7]^=initial[1]&initial[2]
    for seed in range(2500,2532):
        sim=km.Simulator(256,seed=seed,debug_print=False); sim.use_same_registers_as(circuit)
        sim.write_across_shots(x,initial); sim.do(circuit)
        if not np.array_equal(sim.read_across_shots(x),expected): raise AssertionError('Product fanout identity')
        if sim.read_across_shots(cache).any() or sim.read_phase_flipped_across_shots().any():
            raise AssertionError('Product cleanup or phase')
    return {'exhaustive_boolean_inputs':256,'measurement_seeds':32,'cases':8192,
            'value_errors':0,'phase_errors':0,'workspace_errors':0,
            'proof':'p=c0*(1+f), q=c3*(1+f); c3+q=c3*f; factors unchanged until del_and',
            'measurement_note':'32 simulator HMR seeds, not forced exhaustive outcome enumeration'}


def validate_segments():
    """Differential value/phase/ancilla checks, no submission grading."""
    import numpy as np
    report=[]; checked=0
    for it in (0,2,221):
        for adjoint in (False,True):
            old,oreg,boundary=_tail_fixture(False,it=it,adjoint=adjoint)
            new,nreg,nboundary=_tail_fixture(True,it=it,adjoint=adjoint)
            assert boundary==nboundary
            assert old.operation_statistics().num_toffoli_like-new.operation_statistics().num_toffoli_like==3
            for seed in (2501,2502,2503):
                shots=4096; rng=np.random.default_rng(seed)
                values={name:rng.integers(0,2,(len(reg),shots),dtype=np.uint8).astype(bool) for name,reg in oreg.items()}
                # Every one-hot-or-zero ctrl and flag combination occurs; metadata stays within cursor bounds.
                idx=np.arange(shots)
                values['ctrl']=np.array([(idx%5)==i for i in range(4)],dtype=bool)
                values['flag']=((idx>>4)&1).astype(bool)[None,:]
                for k,v in [('nA',3),('nB',3),('na',1),('nb',1),('nq',2)]:
                    values[k]=np.array([np.full(shots,(v>>i)&1,dtype=bool) for i in range(4)])
                sims=[]
                for circuit,regs in ((old,oreg),(new,nreg)):
                    sim=km.Simulator(shots,seed=seed,debug_print=False)
                    sim.use_same_registers_as(circuit)
                    for name,reg in regs.items(): sim.write_across_shots(reg,values[name])
                    sim.do(circuit)
                    anc=km.array([km.q(i) for i in range(boundary,circuit.num_qubits)])
                    if sim.read_across_shots(anc).any(): raise AssertionError(f'Nonzero tail workspace: cached={circuit is new}, it={it}, adjoint={adjoint}')
                    sims.append(sim)
                for name in oreg:
                    if not np.array_equal(sims[0].read_across_shots(oreg[name]),sims[1].read_across_shots(nreg[name])):
                        raise AssertionError('Tail output mismatch: '+name)
                if not np.array_equal(sims[0].read_phase_flipped_across_shots(),sims[1].read_phase_flipped_across_shots()):
                    raise AssertionError('Tail phase mismatch')
                checked+=shots
            report.append({'iteration':it,'adjoint':adjoint,'reference_q':old.num_qubits,'cached_q':new.num_qubits,
                           'reference_t':old.operation_statistics().num_toffoli_like,'cached_t':new.operation_statistics().num_toffoli_like})
    return {'scope':'isolated reduced EEA tail, arbitrary arrays, one-hot-or-zero controls and bounded metadata, both orderings; not decoder PASS',
            'cases':checked,'measurement_seeds':[2501,2502,2503],'value_errors':0,'phase_errors':0,'workspace_errors':0,'segments':report,'product_identity':validate_product_identity(), 'limitations':['Reduced tail tests respect inherited one-hot controls and unary cursor metadata bounds; arbitrary out-of-bound metadata can leave workspace even in reference. Algebraic cache identity is separately exhaustive on independent controls.','HMR seeds sample outcomes; correctness on every outcome follows the unchanged-factor del_and identity, not finite sampling.']}


def build_candidate():
    builder=km.CircuitBuilder()
    syndromes=[builder.create_quantum_register(12,name=f'S{i}') for i in range(70)]
    masks=[builder.create_classical_register(12,name=f'E{j}') for j in range(4095)]
    CachedDecoder(70,km.GF2Field(12),multiplication_strategy='control_input').build_syndrome_decoding_mbuc(
        builder,syndromes=syndromes,error_mbuc=masks,n_iters=222)
    return builder.finish_circuit()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=HERE/'configs/control_cache.json')
    parser.add_argument('--validate-segments',action='store_true')
    parser.add_argument('--audit-tensor',action='store_true')
    parser.add_argument('--overwrite',action='store_true')
    args=parser.parse_args()
    if args.validate_segments:
        print(json.dumps(validate_segments(),indent=2)); return
    if args.audit_tensor:
        print(json.dumps(audit_tensor(),indent=2)); return
    path=args.config.resolve()
    if path.parent!=(HERE/'configs').resolve() or path.suffix!='.json':
        raise ValueError('Config must resolve directly inside this experiment configs/')
    import re
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',path.stem): raise ValueError('Invalid config stem')
    config=json.loads(path.read_text())
    expected={'m':4095,'n':70,'degree':12,'multiplication_strategy':'control_input','cache_route':'eea_tail_pair'}
    if config!=expected: raise ValueError('Only the certified official-size eea_tail_pair config is supported')
    output=ROOT/'artifacts'/HERE.parent.name/HERE.name/(path.stem+'.kmb')
    if output.exists() and not args.overwrite: raise FileExistsError(output)
    circuit=build_candidate(); stats=circuit.operation_statistics()
    if circuit.num_qubits>1893: raise AssertionError('Cache increases reference Q_max')
    if stats.num_toffoli_like!=5044893-1332: raise AssertionError('Unexpected full static savings')
    output.parent.mkdir(parents=True,exist_ok=True)
    circuit.to_file(str(output),format='kmb')
    print(json.dumps({'status':'BUILT','artifact_path':str(output.relative_to(ROOT)),
                     'num_qubits':circuit.num_qubits,'static_toffoli_like':stats.num_toffoli_like,
                     'num_instructions':stats.num_instructions,'reference_t':5044893,'saved_t':1332},indent=2))


if __name__=='__main__':
    main()
