"""Completed in-place multiplication/division by q=x^2+x+2048 modulo B.

Only the existing two 35-word banks are supplied.  B is monic of degree
35 and is preserved.  When B mod q is nonzero, the selected map is the
ordinary quotient-ring operation.  A common-q input follows the explicit
safe-divisor permutation completion, so no semantic cancellation is claimed.
"""
from functools import lru_cache
import shrinking as s
from exp.decoder.common import combine, cx, divmodp, linear_words

ar=s.ar
K=2048


@lru_cache(None)
def qadic_matrix(n):
    cols=[]
    for j in range(n):
        p=[0]*j+[1];out=[]
        for _ in range((n+1)//2):
            p,r=divmodp(p,[K,1,1]);out+=(r+[0,0])[:2]
        cols.append(out[:n])
    return tuple(tuple(cols[j][i] for j in range(n)) for i in range(n))


@lru_cache(None)
def leader(n):
    p=[0]*n+[1];out=[]
    for _ in range((n+2)//2):
        p,r=divmodp(p,[K,1,1]);out+=(r+[0,0])[:2]
    assert out[n]==1
    return tuple(out[:n])


def frame(b,A,B,reverse=False):
    if reverse:
        for w,c in zip(B,leader(len(B))):b.gf2_iadd(c,target=w)
    linear_words(b,A,qadic_matrix(len(A)),reverse)
    linear_words(b,B,qadic_matrix(len(B)),reverse)
    if not reverse:
        for w,c in zip(B,leader(len(B))):b.gf2_iadd(c,target=w)


def residue_carry(b,U,V,lo,hi,carry):
    u,h=U[:12],U[12:];v,t=V[:12],V[12:]
    b.cx(lo,hi);ar.mul_xor0(b,u,v,lo);b.cx(lo,hi)
    cx(b,carry,lo,K);ar.mul_xor0(b,h,t,carry);cx(b,carry,lo,K)
    b.cx(h,u);b.cx(t,v);ar.mul_xor0(b,u,v,hi);b.cx(t,v);b.cx(h,u)


@lru_cache(None)
def rotate_swaps(n):
    labels=list(range(n));want=list(range(2,n))+[0,1];pairs=[]
    for i,k in enumerate(want):
        if labels[i]!=k:
            j=labels.index(k);labels[i],labels[j]=labels[j],labels[i];pairs.append((i,j))
    return tuple(pairs)


def divide_qadic(b,A,B,reverse=False):
    n=len(A);assert n==len(B) and n>=3 and n%2
    U=combine(A[:2]);V=combine(B[:2]);u,h=A[:2]
    def rotate(undo=False):
        for i,j in (reversed(rotate_swaps(n)) if undo else rotate_swaps(n)):
            b.swap(A[i],A[j])
    def body(undo=False):
        ar.mul_xor0(b,h,B[1],A[2])
        indices=range(1,(n-1)//2)
        for i in (reversed(indices) if undo else indices):
            residue_carry(b,U,combine(B[2*i:2*i+2]),A[2*i],A[2*i+1],A[2*i+2])
        ar.mul_xor0(b,u,B[-1],A[-1]);cx(b,h,A[-1],K)
    def upper():
        ar.mul_xor0(b,h,B[-1],u);b.cx(h,u)
    if not reverse:
        s.divide_pair(b,V,U)
        body();upper();rotate()
    else:
        rotate(True);upper();body(True)
        s.divide_pair(b,V,U,True)


def apply(b,A,B,multiply=False):
    """A <- q*A mod B for multiply=True; else A <- A/q mod B."""
    frame(b,A,B)
    divide_qadic(b,A,B,multiply)
    frame(b,A,B,True)
