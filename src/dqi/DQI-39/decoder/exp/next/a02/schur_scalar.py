"""One exact in-place scalar Schur pivot on a monic rational pair.

The value interpretation uses B(0)!=0 and p=R'(0)!=0.  The circuit is an
all-input reversible completion: every scalar division clips zero to one.
All scalar HMR characters close within each call, in either direction.
No checker or simulator state is inspected.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'playbook/kit'),str(ROOT/'playbook/kit/decoder')]
from exp.safe_scalar.converter import inverse_apply, scale, zero_toggle, ar


def x_relocate(b,A,B,reverse=False,flag=None):
    """Replace a common x by x+1 on the B(0)=0 chart.

    On all inputs this is a controlled invertible triangular linear map.
    Its quantum flag remains live until the exact inverse recomputes it.
    """
    n=len(A)
    assert len(B)==n
    if not reverse:
        flag=b.alloc_qubits(1)[0]
        zero_toggle(b,B[0],flag)
        for W in (A,B):
            for i in range(n-1):
                for j in range(12):b.ccx(flag,W[i+1][j],W[i][j])
        b.cx(flag,B[-1][0])
        return flag
    b.cx(flag,B[-1][0])
    for W in (B,A):
        for i in reversed(range(n-1)):
            for j in reversed(range(12)):b.ccx(flag,W[i+1][j],W[i][j])
    zero_toggle(b,B[0],flag)
    b.free(flag)


def pivot(b,A,B,reverse=False):
    """Map n+n coefficient words into u,p and two (n-1)-word banks.

    Inputs store A[0:n] and the non-leading coefficients B[0:n]; B_n=1.
    The output handles are u=A[0], p=A[1], C=B[:-1], D=A[2:]+B[-1:].
    C has degree<n-1 and D is implicitly monic of degree n-1.
    """
    n=len(A)
    assert n==len(B) and n>=2
    u,p=A[:2]
    D=list(A[2:])+[B[-1]]

    def head(ai):
        if not reverse:
            scale(b,u,B[0],ai,True)
            for i in range(1,n):ar.mul_xor0(b,u,B[i],A[i])
            scale(b,p,B[0],ai,True)
        else:
            scale(b,p,B[0],ai,False)
            for i in reversed(range(1,n)):ar.mul_xor0(b,u,B[i],A[i])
            scale(b,u,B[0],ai,False)

    def body(pi):
        if not reverse:
            for i in range(2,n):ar.mul_xor0(b,p,B[i-1],A[i])
            for i in range(2,n):scale(b,A[i],p,pi,True)
            ar.mul_xor0(b,u,pi,B[-1])
            for i in range(n-1):scale(b,B[i],p,pi,False)
            for i in range(1,n-1):ar.mul_xor0(b,p,D[i-1],B[i])
            for i in range(n-1):ar.mul_xor0(b,u,D[i],B[i])
        else:
            for i in reversed(range(n-1)):ar.mul_xor0(b,u,D[i],B[i])
            for i in reversed(range(1,n-1)):ar.mul_xor0(b,p,D[i-1],B[i])
            for i in reversed(range(n-1)):scale(b,B[i],p,pi,True)
            ar.mul_xor0(b,u,pi,B[-1])
            for i in reversed(range(2,n)):scale(b,A[i],p,pi,False)
            for i in reversed(range(2,n)):ar.mul_xor0(b,p,B[i-1],A[i])

    if not reverse:
        inverse_apply(b,B[0],head)
        inverse_apply(b,p,body)
    else:
        inverse_apply(b,p,body)
        inverse_apply(b,B[0],head)
    return u,p,list(B[:-1]),D
