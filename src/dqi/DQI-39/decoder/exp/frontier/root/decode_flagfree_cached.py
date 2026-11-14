"""Flag-free cached inverses at scalar sites that do not need a zero flag."""
from pathlib import Path
from functools import lru_cache
import sys
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a03')]
import decode_local_forward_sheared as sheared
import decode_local_forward_partial as partial
import decode_local_forward as old_forward
import decode_cached12 as old_cached12
from decode_local_forward import combo, jet, joint, replacement_ids
from exp.noscratch import schedules, kernels
from exp.inverse_search import inverse20 as invref
xs = combo.xsub


def inverse6_initialized_nine(b, x):
    """Preserve x and return inverse0(x), using the quadratic tower."""
    to, back, constant = jet.tower(6)
    jet.linear_inplace(b, x, to)
    norm = b.alloc_qubits(3)
    schedules.norm_xor_noscratch(b, x, norm, constant)
    reciprocal = kernels.inverse3_noscratch(b, norm)
    jet.ar._erase_norm(b, x, norm, constant)
    b.free(norm)
    out = b.alloc_qubits(6)
    b.cx(x[3:], x[:3])
    kernels.mul_xor_noscratch(b, x[:3], reciprocal, out[:3])
    kernels.mul_xor_noscratch(b, x[3:], reciprocal, out[3:])
    b.cx(x[3:], x[:3])
    jet.ar._erase_norm(b, out, reciprocal, constant)
    b.free(reciprocal)
    jet.linear_inplace(b, x, back)
    jet.linear_inplace(b, out, back)
    return out


def leaf_fast(b, x, with_zero):
    assert not with_zero
    return xs.inverse6_init18(b, x), None


def leaf_narrow(b, x, with_zero):
    assert not with_zero
    return inverse6_initialized_nine(b, x), None


def make_cached12(leaf):
    return xs.clone(jet.cached_inverse,
                    dict(jet.cached_inverse.__globals__, inverse6_fixed18=leaf))


CACHED12 = (make_cached12(leaf_fast), make_cached12(leaf_narrow))
CACHED24 = tuple(xs.clone(sheared.cached_inverse_partial,
    dict(sheared.cached_inverse_partial.__globals__, cached_inverse=inner))
    for inner in CACHED12)


@lru_cache(None)
def choose_outer(space):
    options = []
    for narrow, inner_width in enumerate((22, 19)):
        for count in range(7):
            if max(21-count+inner_width, 36) > space:
                continue
            columns, _ = sheared.partial_layout(count)
            rebuild = sum(bool(jet.apply(columns, v) >> (21-count))
                          for _, _, v in jet.PLAN24['terms'])
            options.append((3*narrow + rebuild, count, narrow))
    return min(options)[1:] if options else None


def inverse24_forward_flagfree(b, x, K=None):
    selection = choose_outer(889-b.num_allocated_qubits)
    if selection is None:
        return joint.inverse24_forward190(b, x, K)
    count, narrow = selection
    columns, back, _ = jet.extension_columns(K)
    jet.linear_inplace(b, x, columns)
    out, flag = CACHED24[narrow](b, x, jet.PLAN24, count, False)
    assert flag is None
    transcript = b.alloc_bits(24)
    b.hmr(x, transcript)
    b.swap(x, out)
    b.free(out)
    jet.linear_inplace(b, x, back)
    return transcript


def inverse_initialized_flagfree12(b, x, target=None):
    space = 889-b.num_allocated_qubits
    if len(x) != 12 or target is not None or space < 19:
        return invref.inverse_initialized(b, x, target)
    out, flag = CACHED12[space < 22](b, x, jet.PLAN12, False)
    assert flag is None
    return out


def install(entry):
    replacements = {}
    forward = xs.private_rebind(inverse24_forward_flagfree, combo.synth.replacements)
    initialized = xs.private_rebind(inverse_initialized_flagfree12, combo.synth.replacements)
    for old in (joint.inverse24_forward190, old_forward.inverse24_forward_cached,
                partial.inverse24_forward_partial):
        replacements.update(replacement_ids(entry, old, forward))
    for old in (invref.inverse_initialized, old_cached12.inverse_initialized_cached12):
        replacements.update(replacement_ids(entry, old, initialized))
    assert replacements
    scope = dict(entry.__globals__)
    for name in ('extraction', 'synthesize'):
        scope[name] = xs.private_rebind(scope[name], replacements)
    return xs.clone(entry, scope)


decode = install(combo.decode)
