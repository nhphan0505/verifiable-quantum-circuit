"""Share the masked inverse across the two synthesis tail corrections."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'exp/r-main/narrow240'))
import decode_combo as base


def term_correction_with_inverse(b, p, q, d, u, v, pole, qi,
                                 reverse=False, token=None, Z=None):
    if reverse:
        Z = guarded.fresh_zero_flag(b, d)
        b.cz(Z, token[0])
        b.free(token)
    F = b.alloc_qubits(1)[0]
    b.cx(Z, F)
    b.ccx(Z, pole, F)
    factor = b.alloc_qubits(12)
    b.init_and(F, qi, factor)
    if reverse:
        ar.mul_xor0(b, v, factor, u)
        ar.mul_xor0(b, p, factor, v)
    else:
        ar.mul_xor0(b, p, factor, v)
        ar.mul_xor0(b, v, factor, u)
    b.del_and(F, qi, factor)
    b.free(factor)
    b.ccx(Z, pole, F)
    b.cx(Z, F)
    b.free(F)
    if reverse:
        return Z
    zm = b.alloc_bits(1)
    b.hmr(Z, zm[0])
    b.free(Z)
    return zm


def install(entry):
    synth = entry.__globals__['synthesize']
    tail = synth.__globals__['tail_inplace']
    finish = tail.__globals__['tail_finish']
    old = finish.__globals__['term_correction_with_inverse']
    new = base.xsub.clone(term_correction_with_inverse, dict(old.__globals__))
    return base.xsub.private_rebind(entry, {id(old): new})


decode = install(base.decode)
