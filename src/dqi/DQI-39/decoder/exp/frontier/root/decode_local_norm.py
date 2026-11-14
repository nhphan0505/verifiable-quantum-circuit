"""Retain a nested norm in local GF(2^24) inverse reverses when width allows."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / 'exp/r-main/narrow240'), str(HERE.parent / 'a03')]
import decode_combo as combo
import exact_subs as xs
from jet_norm6 import replacement_ids
from exp.inverse12_escape import joint
from exp.inverse12_escape.joint import *


def inverse12_keep_both_norms(b, x):
    to, frm, K = tower(12)
    linear_inplace(b, x, to)
    D = b.alloc_qubits(6)
    norm_xor_noscratch(b, x, D, K)
    u = inverse6_init19(b, D)
    t = b.alloc_qubits(12)
    b.cx(x[6:], x[:6])
    mul_xor_noscratch(b, x[:6], u, t[:6])
    mul_xor_noscratch(b, x[6:], u, t[6:])
    b.cx(x[6:], x[:6])
    linear_inplace(b, x, frm)
    linear_inplace(b, t, frm)
    return t, u, D


def erase_norm_with_both(b, t, N, u, D):
    to, frm, K = tower(12)
    linear_inplace(b, t, to)
    linear_inplace(b, N, to)
    m = b.alloc_bits(12)
    b.hmr(N, m)
    b.free(N)
    L = b.alloc_qubits(6)
    f = field(6)
    def coefficient():
        for j in range(6):
            for i in range(6):
                for r in bits(f.mul(1 << i, 1 << j)):
                    b.ccx(m[r], t[i], L[j])
                    b.ccx(m[r], t[i+6], L[j])
                    b.ccx(m[r+6], t[i+6], L[j])
    coefficient()
    b.cz(L, D)
    coefficient()
    b.free(L)
    b.free(m)
    dm = b.alloc_bits(6)
    b.hmr(D, dm)
    b.free(D)
    xs.phase_inverse6_quad4(b, u, dm)
    b.free(dm)
    ar._erase_norm(b, t, u, K)
    b.free(u)
    linear_inplace(b, t, frm)


def inverse24_reverse_both_norms(b, x, mask, K=None):
    if b.num_allocated_qubits + 48 > 889:
        return fallback(b, x, mask, K)
    cols, back, _ = extension_columns(K)
    linear_inplace(b, x, cols)
    to, frm, K24 = tower(24)
    linear_inplace(b, x, to)
    N = b.alloc_qubits(12)
    norm_xor_noscratch(b, x, N, K24)
    t, u, D = inverse12_keep_both_norms(b, N)
    out = b.alloc_qubits(12)
    mul_xor_noscratch(b, x[12:], t, out)
    erase_product(b, out, N, x[12:])
    mul_xor_noscratch(b, x[:12], t, x[12:])
    erase_product(b, x[12:], N, x[:12])
    b.cx(out, x[12:])
    b.swap(x[:12], x[12:])
    b.swap(x[12:], out)
    b.free(out)
    erase_norm_with_both(b, t, N, u, D)
    ar._erase_norm(b, x, t, K24)
    b.free(t)
    linear_inplace(b, x, frm)
    b.cz(x, mask)
    b.free(mask)
    linear_inplace(b, x, back)


fallback = joint.inverse24_reverse209
replacement = xs.private_rebind(inverse24_reverse_both_norms, combo.synth.replacements)


def install(entry):
    replacements = replacement_ids(entry, joint.inverse24_reverse209, replacement)
    assert replacements
    scope = dict(entry.__globals__)
    for name in ('extraction', 'synthesize'):
        scope[name] = xs.private_rebind(scope[name], replacements)
    return xs.clone(entry, scope)


decode = install(combo.decode)
