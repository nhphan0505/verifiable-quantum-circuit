"""Use a measured AND for the synthesis correction predicate.

The shared-factor kernel is the root's existing exact correction.  This
variant changes only its F=[d=0] AND NOT pole predicate cleanup.
"""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'exp/r-main/narrow240'))
import decode_combo as combo


def term_correction_with_inverse(b, p, q, d, u, v, pole, qi,
                                 reverse=False, token=None, Z=None):
    if reverse:
        Z = guarded.fresh_zero_flag(b, d)
        b.cz(Z, token[0])
        b.free(token)
    F = b.alloc_qubits(1)[0]
    b.x(pole)
    b.init_and(Z, pole, F)
    b.x(pole)
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
    b.x(pole)
    b.del_and(Z, pole, F)
    b.x(pole)
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
    new = combo.xsub.clone(term_correction_with_inverse, dict(old.__globals__))
    scope = dict(entry.__globals__)
    scope['synthesize'] = combo.xsub.private_rebind(synth, {id(old): new})
    return combo.xsub.clone(entry, scope)


decode = install(combo.decode)
