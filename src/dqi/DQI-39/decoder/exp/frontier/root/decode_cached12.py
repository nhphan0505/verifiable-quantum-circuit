"""Reuse the cached GF4096 inverse in front-half initialized producers."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
KIT_ROOT = HERE.parents[2]
sys.path[:0] = [str(KIT_ROOT / 'exp/r-main/narrow240'), str(HERE.parent / 'a03')]
import decode_combo as combo
import exact_subs as xs
from jet_norm6 import replacement_ids
from exp.jet24 import pro_jet as jet
from exp.inverse_search import inverse20 as invref


def inverse_initialized_cached12(b, x, target=None):
    if len(x) != 12 or target is not None or b.num_allocated_qubits + 22 > 889:
        return initialized_fallback(b, x, target)
    out, F = jet.cached_inverse(b, x, jet.PLAN12, True)
    fm = b.alloc_bits(1)
    b.hmr(F, fm[0])
    b.free(F)
    b.z(fm[0])
    mask = b.alloc_bits(12)
    b.bit_store(mask, False)
    b.cx(fm[0], mask[0])
    jet.ar.phase_product(b, x, out, mask)
    b.free(mask)
    b.free(fm)
    return out


def inverse_zero_cached12(b, x):
    if b.num_allocated_qubits + 22 > 889:
        return zero_fallback(b, x)
    return jet.cached_inverse(b, x, jet.PLAN12, True)


initialized_fallback = invref.inverse_initialized
zero_fallback = xs.inverse_zero
initialized_replacement = xs.private_rebind(inverse_initialized_cached12, combo.synth.replacements)
zero_replacement = xs.private_rebind(inverse_zero_cached12, combo.synth.replacements)


def install(entry):
    replacements = replacement_ids(entry, invref.inverse_initialized, initialized_replacement)
    replacements.update(replacement_ids(entry, xs.inverse_zero, zero_replacement))
    assert replacements
    scope = dict(entry.__globals__)
    for name in ('extraction', 'synthesize'):
        scope[name] = xs.private_rebind(scope[name], replacements)
    return xs.clone(entry, scope)


decode = install(combo.decode)
