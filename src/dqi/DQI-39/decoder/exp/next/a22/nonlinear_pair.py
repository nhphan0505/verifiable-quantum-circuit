"""All-source completion of (a*bar(z)+d)/z in the existing target pair.

a is one GF(4096) source word, d is one GF(2^24) source pair, and z is
the existing GF(2^24) denominator pair.  All sources are restored.  No
24-qubit source or target companion is allocated.  This is a local
Schur/Hermite component, not a decoder or a complete direct return.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/'exp/next/a02'), str(ROOT/'exp/next/a17')]
from schur_scalar import inverse_apply, scale, zero_toggle, ar
from rank_completed_pair import matrix_bar, ratio, conditional_T, point_swap
from universal_rank_completion import closed_inverse


def unit_swap(b, y, F):
    """Conditioned transposition of 0 and 1; no retained target flag."""
    Z = b.alloc_qubits(1)[0]
    zero_toggle(b, y[1:], Z)
    b.ccx(F, Z, y[0])
    zero_toggle(b, y[1:], Z)
    b.free(Z)


def selected_point_swap(b, y, F, g, reverse=False, hc=0):
    """Use 0<->hc+beta on d!=0, 0<->1 on d=0, only when F=1.

    The zero flag of the projective source pivot g is retired immediately;
    it need not remain live through the 24-bit inverse.
    """
    D = b.alloc_qubits(1)[0]
    zero_toggle(b, g, D)
    G = b.alloc_qubits(1)[0]
    b.init_and(F, D, G)
    if reverse:
        unit_swap(b, y, G)
    b.cx(G, F)
    point_swap(b, y, F, hc)
    b.cx(G, F)
    if not reverse:
        unit_swap(b, y, G)
    b.del_and(F, D, G)
    b.free(G)
    zero_toggle(b, g, D)
    b.free(D)


def completed_core(b, y, F, g, reverse=False, hc=0):
    """A02's normalized map with an explicit all-ray d=0 completion.

    F=0: inverse0(y).
    F=1,D=0: A02's all-input completion of (bar(y)+1)/y.
    F=1,D=1: G(swap_01(y)), with G=1+inverse0(T(y)).
      This agrees with bar(y)/y on {1} union {s+beta}, and maps 0 to 0.
    """
    if not reverse:
        selected_point_swap(b, y, F, g, hc=hc)
        conditional_T(b, y, F)
        closed_inverse(b, y)
        b.cx(F, y[0])
    else:
        b.cx(F, y[0])
        closed_inverse(b, y)
        conditional_T(b, y, F)
        selected_point_swap(b, y, F, g, True, hc)


def completed_affine_conjugate(b, a, d, z, reverse=False, hc=0):
    """Complete the affine-conjugate quotient for every a,d,z.

    The actual quotient is obtained for d!=0 and nonsingular output, and
    for one selected point on every collapsed fiber.  Remaining fiber
    coordinates are encoded in unused target points.  d=0 has an explicit
    projective-ray completion rather than being mistaken for termination.
    Each direction closes every measurement character locally.
    """
    assert len(a) == 12 and len(d) == len(z) == 24
    assert 0 <= hc < 4096
    r, g = d[:12], d[12:]
    F, I = b.alloc_qubits(2)
    zero_toggle(b, a, F)
    b.x(F)                         # F = [a != 0]
    zero_toggle(b, g, I)
    b.cswap(I, r, g)               # g is nonzero iff d is nonzero
    b.x(I)                         # I = [original imag(d) != 0]

    # d = g*v, where v=r+beta on I and v=1 otherwise.  The clipped g=1
    # source gives safe(d)=1 when d=0.  All transforms stay in d's bank.
    def prepare(gi):
        scale(b, r, g, gi, True)
        if not reverse:
            scale(b, z[:12], g, gi, True)
            scale(b, z[12:], g, gi, True)
    inverse_apply(b, g, prepare)

    def scalar(divide):
        def action(ai):
            scale(b, z[:12], a, ai, divide)
            scale(b, z[12:], a, ai, divide)
        inverse_apply(b, a, action)

    if not reverse:
        matrix_bar(b, z, r, I, True)
        scalar(False)
        completed_core(b, z, F, g, hc=hc)
        ratio(b, z, r, I)
        scalar(False)
    else:
        scalar(True)
        ratio(b, z, r, I, True)
        completed_core(b, z, F, g, True, hc)
        scalar(True)
        matrix_bar(b, z, r, I)

    def restore(gi):
        if reverse:
            scale(b, z[:12], g, gi, False)
            scale(b, z[12:], g, gi, False)
        scale(b, r, g, gi, False)
    inverse_apply(b, g, restore)

    b.x(I)
    b.cswap(I, r, g)
    zero_toggle(b, g, I)
    b.x(F)
    zero_toggle(b, a, F)
    b.free([F, I])


def completed_outside_pivot(b, ui, uj, uk, zi, zj, zk,
                            tj=2, tk=4, reverse=False, hc=0):
    """Actual A17 way in, nonlinear target pivot, explicit inverse.

    At outside rank two, zj contains actual d_i and zi receives the local
    nonlinear completion.  At lower ranks, the A17 source is a completed
    coordinate, not raw d_i; the composition remains a permutation.  The
    physical lower-rank interpretation is an open global alignment task.
    zj and zk retain all outside kernel coordinates in their existing B
    storage.  The three quotient values are preserved.
    """
    from rank_block import completed_full_outside_row
    if not reverse:
        completed_full_outside_row(b, ui, uj, uk, zj, zk, tj, tk, fast=True)
        completed_affine_conjugate(b, ui[12:], zj, zi, hc=hc)
    else:
        completed_affine_conjugate(b, ui[12:], zj, zi, True, hc)
        completed_full_outside_row(b, ui, uj, uk, zj, zk, tj, tk,
                                   True, fast=True)
