"""Use the exact initialized inverse at remaining basic GF64 producers."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
KIT_ROOT = HERE.parents[2]
sys.path[:0] = [str(KIT_ROOT / 'exp/r-main/narrow240'), str(HERE.parent / 'a03')]
import decode_combo as combo
import exact_subs as xs
from jet_norm6 import replacement_ids
from exp.inverse_width_subspaces import kernel19 as basic


def inverse6_initialized18(b, x, z=None, keep_norm=False):
    if z is None and not keep_norm:
        return xs.inverse6_init18(b, x)
    return fallback(b, x, z, keep_norm)


fallback = basic.inverse6_xor19
replacement = xs.private_rebind(inverse6_initialized18, combo.synth.replacements)


def install(entry):
    replacements = replacement_ids(entry, basic.inverse6_xor19, replacement)
    assert replacements
    scope = dict(entry.__globals__)
    for name in ('extraction', 'synthesize'):
        scope[name] = xs.private_rebind(scope[name], replacements)
    return xs.clone(entry, scope)


decode = install(combo.decode)
