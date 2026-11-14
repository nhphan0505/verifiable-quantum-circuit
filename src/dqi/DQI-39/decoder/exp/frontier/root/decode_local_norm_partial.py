"""Use partial nested norms at additional local inverse-reverse sites."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_local_norm import *
from quantum_phase6 import phase_quantum_character


def inverse12_keep_partial_norm(b, x, keep):
    to, frm, K = tower(12)
    linear_inplace(b, x, to)
    D = b.alloc_qubits(6)
    norm_xor_noscratch(b, x, D, K)
    u = inverse6_init19(b, D)
    if keep < 6:
        dm = b.alloc_bits(6)
        b.bit_store(dm, False)
        b.hmr(D[keep:], dm[keep:])
        b.free(D[keep:])
        ar._phase_norm(b, x, dm, K)
        b.free(dm)
    t = b.alloc_qubits(12)
    b.cx(x[6:], x[:6])
    mul_xor_noscratch(b, x[:6], u, t[:6])
    mul_xor_noscratch(b, x[6:], u, t[6:])
    b.cx(x[6:], x[:6])
    linear_inplace(b, x, frm)
    linear_inplace(b, t, frm)
    return t, u, D[:keep]


def erase_norm_with_partial(b, t, N, u, D):
    to, frm, K = tower(12)
    linear_inplace(b, t, to)
    linear_inplace(b, N, to)
    m = b.alloc_bits(12)
    b.hmr(N, m)
    b.free(N)
    L = b.alloc_qubits(1)[0]
    f = field(6)
    def coefficient(j):
        for i in range(6):
            for r in bits(f.mul(1 << i, 1 << j)):
                b.ccx(m[r], t[i], L)
                b.ccx(m[r], t[i+6], L)
                b.ccx(m[r+6], t[i+6], L)
    for j in range(6):
        coefficient(j)
        if j < len(D):
            b.cz(L, D[j])
        else:
            phase_quantum_character(b, u, L, 1 << j)
        coefficient(j)
    b.free(L)
    b.free(m)
    dm = b.alloc_bits(6)
    b.bit_store(dm, False)
    b.hmr(D, dm[:len(D)])
    b.free(D)
    xs.phase_inverse6_quad4(b, u, dm)
    b.free(dm)
    ar._erase_norm(b, t, u, K)
    b.free(u)
    linear_inplace(b, t, frm)


def inverse24_reverse_partial(b, x, mask, K=None):
    keep = min(6, 889 - b.num_allocated_qubits - 42)
    if keep < 4:
        return fallback(b, x, mask, K)
    cols, back, _ = extension_columns(K)
    linear_inplace(b, x, cols)
    to, frm, K24 = tower(24)
    linear_inplace(b, x, to)
    N = b.alloc_qubits(12)
    norm_xor_noscratch(b, x, N, K24)
    t, u, D = inverse12_keep_partial_norm(b, N, keep)
    out = b.alloc_qubits(12)
    mul_xor_noscratch(b, x[12:], t, out)
    erase_product(b, out, N, x[12:])
    mul_xor_noscratch(b, x[:12], t, x[12:])
    erase_product(b, x[12:], N, x[:12])
    b.cx(out, x[12:])
    b.swap(x[:12], x[12:])
    b.swap(x[12:], out)
    b.free(out)
    erase_norm_with_partial(b, t, N, u, D)
    ar._erase_norm(b, x, t, K24)
    b.free(t)
    linear_inplace(b, x, frm)
    b.cz(x, mask)
    b.free(mask)
    linear_inplace(b, x, back)


replacement = xs.private_rebind(inverse24_reverse_partial, combo.synth.replacements)


def install(entry):
    replacements = replacement_ids(entry, joint.inverse24_reverse209, replacement)
    assert replacements
    scope = dict(entry.__globals__)
    scope['extraction'] = xs.private_rebind(scope['extraction'], replacements)
    return xs.clone(entry, scope)


decode = install(combo.decode)
