"""Exact forward inverse-norm retention in the retired-root lifetime.

Install after A08's scalar installer on the private converter graph.  The
default two six-bit caches occupy the twelve wires that A07 frees during
forward descent; neither cache survives the selected frame's return.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'research/agents/a08'))
import scalar_compact_v3 as scalar

ar, xs = scalar.ar, scalar.xs


def first_inverse_with_t(b, x):
    """Return inv0(x), [x=0], and t=inv0(Norm(x)); retire raw Norm(x)."""
    to, frm, K = ar.tower(12)
    ar.linear_inplace(b, x, to)
    norm = b.alloc_qubits(6)
    scalar.norm_xor_noscratch(b, x, norm, K)
    t, F = xs.inverse6_joint18_12extra(b, norm)
    ar._erase_norm(b, x, norm, K)
    b.free(norm)
    out = b.alloc_qubits(12)
    b.cx(x[6:], x[:6])
    scalar.mul_xor_noscratch(b, x[:6], t, out[:6])
    scalar.mul_xor_noscratch(b, x[6:], t, out[6:])
    b.cx(x[6:], x[:6])
    ar.linear_inplace(b, x, frm)
    ar.linear_inplace(b, out, frm)
    return out, F, t


def inverse_from_t_and_retire(b, x, t, zero_flag):
    """Reuse t, then repay its HMR character against Norm(inv0(x))."""
    to, frm, K = ar.tower(12)
    F = zero_flag(b, t)
    ar.linear_inplace(b, x, to)
    out = b.alloc_qubits(12)
    b.cx(x[6:], x[:6])
    scalar.mul_xor_noscratch(b, x[:6], t, out[:6])
    scalar.mul_xor_noscratch(b, x[6:], t, out[6:])
    b.cx(x[6:], x[:6])
    # inv0(Norm(x)) = Norm(inv0(x)), also at x=0.
    ar._erase_norm(b, out, t, K)
    b.free(t)
    ar.linear_inplace(b, x, frm)
    ar.linear_inplace(b, out, frm)
    return out, F


def install(cv, levels=(11, 5)):
    """Patch only forward inverse production; keep all existing phase tokens."""
    cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
    short = cells['core'].cell_contents.__globals__
    scope = scalar.scope_of(cv)
    original_inverse = scope['inverse_zero']
    original_solve = scope['look_solve']
    levels = frozenset(levels)
    frames = []

    def inverse_zero(b, x):
        if not frames:
            return original_inverse(b, x)
        m, phase, g, reverse = frames[-1]
        if reverse or m not in levels or list(x) != list(g[-1]):
            return original_inverse(b, x)
        caches = phase.setdefault('_a12_forward_norm', {})
        if m not in caches:
            ai, F, caches[m] = first_inverse_with_t(b, x)
            return ai, F
        return inverse_from_t_and_retire(
            b, x, caches.pop(m), scope['fresh_zero_flag'])

    def inverse_apply_safe(b, a, action, incoming=None, defer=False):
        ai, F = inverse_zero(b, a)
        scope['consume'](b, ai, F, incoming)
        b.cx(F, a[0])
        b.cx(F, ai[0])
        action(ai)
        b.cx(F, ai[0])
        b.cx(F, a[0])
        return scope['erase'](b, a, ai, F, defer)

    def solve(b, f, g, payloads, H=None, parent=None, reverse=False, phase=None):
        m = len(f) - 1
        frames.append((m, phase, g, reverse))
        try:
            out = original_solve(b, f, g, payloads, H, parent, reverse, phase)
            if not reverse and m in levels:
                assert m not in phase.get('_a12_forward_norm', {})
            return out
        finally:
            frames.pop()

    scope.update(inverse_zero=inverse_zero,
                 inverse_apply_safe=inverse_apply_safe, look_solve=solve)
    short['old'].look_solve = solve
    return cv
