"""Actual monic coefficient entry for the first full 35-node pivot.

This entry is fully closed in measurement phase.  The only live new quantum
state at its end is the explicitly returned common-x relocation flag.
No original extraction/synthesis transcript is consumed here.
"""
from functools import lru_cache
from pivot_rotate import divide_pair
from nonlinear_pair import inverse_apply, scale, ar
from schur_scalar import x_relocate
from exp.decoder.common import linear_words, mul, inv, emul, einv, eev, pmul


@lru_cache(None)
def geometry():
    rows, leads = [], []
    nodes = [64+2*j | 4096 for j in range(17)]
    Q = [0, 1]
    for j in range(17):
        c = 64+2*j
        Q = pmul(Q, [mul(c, c)^c^2048, 1, 1])
    deriv = [Q[j] if j & 1 else 0 for j in range(1, len(Q))]
    normalizers = []
    for node in nodes:
        values, power = [], 1
        for _ in range(35):
            values.append(power)
            power = emul(power, node)
        rows.append(tuple(x & 4095 for x in values))
        rows.append(tuple(x >> 12 for x in values))
        leads += [power & 4095, power >> 12]
        normalizers.append(eev(deriv, node))
    rows.append(tuple([1]+[0]*34)); leads.append(0)
    normalizers.append(eev(deriv, 0))
    assert all(normalizers)
    return tuple(rows), tuple(leads), tuple(normalizers)


def pair(words, j):
    return list(words[2*j])+list(words[2*j+1])


def normalize(b, B, reverse=False):
    _, _, constants = geometry()
    for j in range(17):
        c = constants[j] if reverse else einv(constants[j])
        ar.linear_inplace(b, pair(B, j), [emul(c, 1 << k) for k in range(24)])
    c = constants[-1] if reverse else inv(constants[-1])
    ar.linear_inplace(b, B[-1], [mul(c, 1 << k) for k in range(12)])


def enter(b, A, B):
    """(Acoeff,Bcoeff) -> (U=A/B, Z=B/Q′), returning one coherent flag."""
    assert len(A) == len(B) == 35
    F = x_relocate(b, A, B)
    rows, leads, _ = geometry()
    linear_words(b, A, rows)
    linear_words(b, B, rows)
    for word, c in zip(B, leads):
        b.gf2_iadd(c, target=word)
    for j in range(17):
        divide_pair(b, pair(B, j), pair(A, j))
    inverse_apply(b, B[-1], lambda bi: scale(b, A[-1], B[-1], bi, True))
    normalize(b, B)
    return F


def leave(b, A, B, F):
    normalize(b, B, True)
    inverse_apply(b, B[-1], lambda bi: scale(b, A[-1], B[-1], bi, False))
    for j in reversed(range(17)):
        divide_pair(b, pair(B, j), pair(A, j), True)
    rows, leads, _ = geometry()
    for word, c in zip(B, leads):
        b.gf2_iadd(c, target=word)
    linear_words(b, B, rows, True)
    linear_words(b, A, rows, True)
    x_relocate(b, A, B, True, F)


def pivot_view(A, B):
    return [pair(A, j) for j in range(17)], A[-1], [pair(B, j) for j in range(17)], B[-1]
