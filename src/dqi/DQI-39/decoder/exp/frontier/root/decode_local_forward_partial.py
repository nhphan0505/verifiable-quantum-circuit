"""Retire selected raw norm directions during the nested cached inverse."""
from pathlib import Path
from functools import lru_cache
import inspect
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from decode_local_forward import *

OMITTED = (212, 324, 32, 75, 2)


@lru_cache(None)
def partial_layout(count):
    omitted = list(OMITTED[:count])
    span = {0}
    for row in omitted:
        assert row not in span
        span |= {v ^ row for v in tuple(span)}
    kept = []
    for row in (1 << j for j in range(9)):
        if row not in span:
            kept.append(row)
            span |= {v ^ row for v in tuple(span)}
    rows = [1 << j for j in range(12)] + [v << 12 for v in kept + omitted]
    columns = [sum(((row >> j) & 1) << i for i, row in enumerate(rows))
               for j in range(21)]
    return tuple(columns), tuple(jet.inverse_columns(columns))


def retire_raw(b, x, raw, count):
    columns, back = partial_layout(count)
    jet.linear_inplace(b, raw, columns)
    mask = b.alloc_bits(count)
    b.hmr(raw[21-count:], mask)
    b.free(raw[21-count:])
    for left, right, vector in jet.PLAN24['terms']:
        removed = jet.apply(columns, vector) >> (21-count)
        if not removed:
            continue
        with jet.ref.expose_pair(b, x, left << 1, right << 1) as (a, c):
            for i in jet.bits(removed):
                b.ccz(a, c, mask[i])
    b.free(mask)
    return list(raw[:21-count])


def rebuild_raw(b, x, raw, count):
    columns, back = partial_layout(count)
    removed = b.alloc_qubits(count)
    for left, right, vector in jet.PLAN24['terms']:
        projected = jet.apply(columns, vector) >> (21-count)
        if not projected:
            continue
        with jet.ref.expose_pair(b, x, left << 1, right << 1) as (a, c):
            jet.rankone_xor(b, a, c, removed, projected)
    raw = list(raw) + list(removed)
    jet.linear_inplace(b, raw, back)
    return raw


source = inspect.getsource(jet.cached_inverse)
source = source.replace('def cached_inverse(b, x, plan, with_zero=True):',
                        'def cached_inverse_partial(b, x, plan, count, with_zero=True):')
source = source.replace('    D = raw[:h]',
                        '    raw = retire_raw(b, x, raw, count)\n    D = raw[:h]')
source = source.replace("    linear_inplace(b, raw, plan['reduce'])",
                        "    raw = rebuild_raw(b, x, raw, count)\n    linear_inplace(b, raw, plan['reduce'])")
environment = dict(jet.cached_inverse.__globals__, retire_raw=retire_raw,
                   rebuild_raw=rebuild_raw)
exec(compile(source, __file__, 'exec'), environment)
cached_inverse_partial = environment['cached_inverse_partial']


def inverse24_forward_partial(b, x, K=None):
    omitted = max(0, b.num_allocated_qubits + 43 - 889)
    if omitted > len(OMITTED):
        return fallback(b, x, K)
    cols, back, _ = jet.extension_columns(K)
    jet.linear_inplace(b, x, cols)
    if omitted:
        out, F = cached_inverse_partial(b, x, jet.PLAN24, omitted, True)
    else:
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


replacement = combo.xsub.private_rebind(inverse24_forward_partial, combo.synth.replacements)


def install(entry):
    replacements = replacement_ids(entry, joint.inverse24_forward190, replacement)
    replacements.update(replacement_ids(entry, inverse24_forward_cached, replacement))
    assert replacements
    scope = dict(entry.__globals__)
    scope['extraction'] = combo.xsub.private_rebind(scope['extraction'], replacements)
    return combo.xsub.clone(entry, scope)


decode = install(combo.decode)
