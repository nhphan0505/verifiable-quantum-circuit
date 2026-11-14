"""Retain a small first-state projection to erase the third scalar product.

This adds no unproved value promise. Every measured output character is
paid from the cached linear state and the product's still-live inputs.
"""
from pathlib import Path
from functools import lru_cache
import sys

HERE = Path(__file__).resolve().parent
KIT_ROOT = HERE.parents[2]
sys.path[:0] = [str(KIT_ROOT / 'exp/r-main/narrow240'), str(HERE.parent / 'a03')]
import decode_combo as combo
import retained_core_safe27 as ret
from jet_norm6 import replacement_ids
from retained_core_safe27 import *
from exp.mul99.kernels import tensor99_extension
from exp.arithmetic.division import phase_product24
from replay_erase import scalar_erase_second24


@lru_cache(None)
def projection(k):
    terms = tensor99_extension(K)
    first = [w for _, w in terms[:9]]
    states = {frozenset((0,)): ()}
    for _ in range(k):
        following = {}
        for span, basis in states.items():
            for value in first:
                if value in span:
                    continue
                grown = span | {v ^ value for v in span}
                following.setdefault(grown, basis + (value,))
        states = following
    span, columns = max(states.items(), key=lambda s: (sum(w in s[0] for _, w in terms), s[1]))
    columns = list(columns)
    pivots = {}
    def add(value):
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                return True
        return False
    for value in columns:
        assert add(value)
    for value in (1 << i for i in range(24)):
        if add(value):
            columns.append(value)
    to = tuple(ar.inverse_columns(columns))
    projected = tuple((m, m, ar.apply(to, w) & ~((1 << k) - 1)) for m, w in terms)
    return to, tuple(columns), tuple(t for t in projected if t[2])


def copy_first_projection(b, first_state, q1, k):
    to, _, _ = projection(k)
    cache = b.alloc_qubits(k)
    columns = [ar.apply(to, emul(q1, 1 << i)) & ((1 << k) - 1) for i in range(24)]
    ar.linear_xor(b, first_state, cache, columns)
    return cache


def erase_third_step(b, head, N, D, q, ct, cache):
    # The standard reverse step starts by exposing D3 as N and D2 as D.
    scalepair(b, N, inv(q))
    b.swap(N, D)
    k = len(cache)
    to, back, terms = projection(k)
    ar.linear_inplace(b, N, to)
    a, h = head
    cx(b, h, a, ct)
    xsub.accumulator(b, combine(head), D, N, terms)
    m = b.alloc_bits(k)
    b.hmr(N[:k], m)
    b.cz(cache, m)
    original_mask = b.alloc_bits(24)
    b.bit_store(original_mask, False)
    for j, column in enumerate(to):
        for i in ar.bits(column & ((1 << k) - 1)):
            b.cx(m[i], original_mask[j])
    phase_product24(b, combine(head), D, original_mask, K)
    b.free(original_mask)
    b.free(m)
    b.cx(cache, N[:k])
    cx(b, h, a, ct)
    ar.linear_inplace(b, N, back)
    ar.linear_xor(b, N, cache, [column & ((1 << k) - 1) for column in to])
    b.free(cache)


def full_core_phase(b, N, heads, params, ct, masks, pole, dirty):
    selected = CACHE_BY_HEADS.get(len(heads), 0)
    D = b.alloc_qubits(24)
    b.x(D[0])
    cache = None
    for i, (head, (q, c)) in enumerate(zip(heads, params)):
        ref.external_scalar_step(b, head, N, D, q, ct, first=i == 0)
        if i == 0 and selected:
            cache = copy_first_projection(b, D, params[1][0], selected)
    b.cswap(pole, N, D)
    A, g = D[:12], D[12:]
    zero_affine_character(b, g, A, masks['g'], masks['f'][0])
    zero = b.alloc_bits(12)
    b.bit_store(zero, False)
    masks['i'] = zero
    b.cz(g, masks['g'])
    b.cz(A, masks['h'])
    f = ar.field(12)
    for j in range(12):
        for r in ar.bits(f.mul(K, 1 << j)):
            b.cz(g[j], masks['h'][r])
    core.affine_inverse_g_character(b, A, g, masks)
    for m in masks.values():
        b.free(m)
    b.cswap(pole, N, D)
    fm = b.alloc_bits(1)
    b.hmr(pole, fm[0])
    b.free(pole)
    b.push_condition(fm[0])
    clean_zero_phase24(b, D)
    b.pop_condition()
    b.free(fm)
    for i in reversed(range(len(heads))):
        if i == 2 and cache is not None:
            erase_third_step(b, heads[i], N, D, params[i][0], ct, cache)
        elif i == 1:
            scalar_erase_second24(b, heads[i], N, D, params[i][0], ct, params[0][0])
        else:
            ref.external_scalar_step(b, heads[i], N, D, params[i][0], ct, True, first=i == 0)
    b.x(D[0])
    b.free(D)


def install(entry, cache_by_gi):
    env = dict(full_core_phase.__globals__, CACHE_BY_HEADS={2 * gi: k for gi, k in cache_by_gi.items()})
    candidate = combo.xsub.clone(full_core_phase, env)
    candidate = combo.xsub.private_rebind(candidate, combo.synth.replacements)
    changes = replacement_ids(entry, ret.full_core_phase, candidate)
    assert changes
    scope = dict(entry.__globals__)
    scope['extraction'] = combo.xsub.private_rebind(scope['extraction'], changes)
    return combo.xsub.clone(entry, scope)


CACHE_BY_HEADS = {}
