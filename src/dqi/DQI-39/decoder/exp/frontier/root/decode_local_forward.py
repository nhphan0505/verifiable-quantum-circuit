"""Reuse the jet's cached inverse for local scalar heads where it fits."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
KIT_ROOT = HERE.parents[2]
sys.path[:0] = [str(KIT_ROOT / 'exp/r-main/narrow240'), str(HERE.parent / 'a03')]
import decode_combo as combo
from jet_norm6 import replacement_ids
from exp.jet24 import pro_jet as jet
from exp.inverse12_escape import joint


def inverse24_forward_cached(b, x, K=None):
    if b.num_allocated_qubits + 43 > 889:
        return fallback(b, x, K)
    cols, back, _ = jet.extension_columns(K)
    jet.linear_inplace(b, x, cols)
    out, F = jet.cached_inverse(b, x, jet.PLAN24, True)
    fm = b.alloc_bits(1)
    b.hmr(F, fm[0])
    b.free(F)
    b.z(fm[0])
    mask = b.alloc_bits(24)
    b.bit_store(mask, False)
    b.cx(fm[0], mask[0])
    jet.phase_product_quantum99(b, x, out, mask)
    b.free(mask)
    b.free(fm)
    mu = b.alloc_bits(24)
    b.hmr(x, mu)
    b.swap(x, out)
    b.free(out)
    jet.linear_inplace(b, x, back)
    return mu


fallback = joint.inverse24_forward190
replacement = combo.xsub.private_rebind(inverse24_forward_cached, combo.synth.replacements)


def install(entry):
    replacements = replacement_ids(entry, joint.inverse24_forward190, replacement)
    assert replacements
    scope = dict(entry.__globals__)
    scope['extraction'] = combo.xsub.private_rebind(scope['extraction'], replacements)
    return combo.xsub.clone(entry, scope)


decode = install(combo.decode)
