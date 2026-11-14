"""An all-input first Hermite row using one outside numerator coordinate.

The current numerator bank is homogeneous: Aj=A(beta_j)/Q'(beta_j),
not a bank of separately divided Uj.  A fixed invertible linear map
exposes C=sum Kij(Aj) into A[1].  The row is completed by writing its
outside d into that numerator word, whose coefficient is always one.
No rank predicate, zero-Ui control, or external source word is assumed.

The output retains old Z[0] in the former A[1].  Hence the remaining
semantic bank dimensions change; a global Schur rebalance is still needed.
"""
from pathlib import Path
from functools import lru_cache
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'exp/next/a22')]
from pivot_bridge import divide_pair, rotated_affine_conjugate
from nonlinear_pair import ar
from coefficient_entry import geometry, normalize, pair
from exp.decoder.common import linear_words, emul, einv
from exp.mul99.kernels import mul24_xor99_zero


def bar(x): return x^(x>>12)


@lru_cache(None)
def k_columns(t):
    p,q=einv(t),einv(t^1)
    return tuple(emul(p,1<<j)^emul(q,bar(1<<j)) for j in range(24))


@lru_cache(None)
def real_columns():
    p=einv(64|4096)
    return tuple(emul(p,1<<j) for j in range(12))


def expose_outside(b, bank, real, reverse=False):
    target=bank[1]
    if not reverse: ar.linear_inplace(b,target,k_columns(2))
    for j in range(2,17):
        ar.linear_xor(b,bank[j],target,k_columns(2*j))
    ar.linear_xor(b,real,target,real_columns())
    if reverse: ar.linear_inplace(b,target,ar.inverse_columns(k_columns(2)))


def enter(b,A,B,reverse=False):
    """Monic coefficient pair <-> normalized homogeneous evaluations.

    This is entirely fixed binary linear/affine work: no quotient bank,
    relocation flag, measurement, or nonlinear operation is introduced.
    """
    rows,leads,_=geometry()
    if not reverse:
        linear_words(b,A,rows);linear_words(b,B,rows)
        for w,c in zip(B,leads):b.gf2_iadd(c,target=w)
        normalize(b,A);normalize(b,B)
    else:
        normalize(b,A,True);normalize(b,B,True)
        for w,c in zip(B,leads):b.gf2_iadd(c,target=w)
        linear_words(b,B,rows,True);linear_words(b,A,rows,True)


def view(A,B):
    return [pair(A,j) for j in range(17)],A[-1],[pair(B,j) for j in range(17)],B[-1]


def first_pivot(b,A,ar0,B,br0,reverse=False):
    """Emit U0,V0 in A0,B0; old B0 moves to A1; all other words restore.

    The emitted V0 is the completed safe-denominator formula on all
    inputs.  If B0!=0, it is the actual derivative of the current monic
    rational pair.  Common-factor poles are not silently called derivatives.
    """
    U,Z,C,E=A[0],B[0],A[1],B[1]
    if not reverse:
        divide_pair(b,Z,U)
        expose_outside(b,A,ar0)
        expose_outside(b,B,br0)
        mul24_xor99_zero(b,U,E,C,2048);b.cx(U,C)
        rotated_affine_conjugate(b,U[12:],Z,C)
        expose_outside(b,B,br0,True)
    else:
        expose_outside(b,B,br0)
        rotated_affine_conjugate(b,U[12:],Z,C,True)
        b.cx(U,C);mul24_xor99_zero(b,U,E,C,2048)
        expose_outside(b,B,br0,True)
        expose_outside(b,A,ar0,True)
        divide_pair(b,Z,U,True)
