"""Fraction-free paired continued-fraction routing with three virtual leaders.

The q-adic banks store n lower words each, n odd. The virtual coefficients
are A[n]=a1, A[n+1]=a2, B[n]=beta. No monicity or eta!=0 promise is used.
All clipped quotient characters close inside the borrowed GF24 helpers.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'exp/next/a06')]
from paired_coefficient import closed_scale24,qadic_matrix,K
from exp.decoder.common import ar,combine,cx,linear_words,mul
from exp.mul99.kernels import mul24_xor99


def leader_first(b,U,z,leaders,reverse=False,carry=None,k=K):
    a1,a2,beta=leaders;u,h=U[:12],U[12:]
    def add_copies():
        b.cx(a2,a1)
        if carry is not None:cx(b,a2,carry,k)
    if reverse:
        ar.mul_xor0(b,h,z,a1);ar.mul_xor0(b,u,beta,a1)
    add_copies();ar.mul_xor0(b,h,beta,a2);add_copies()
    if not reverse:
        ar.mul_xor0(b,u,beta,a1);ar.mul_xor0(b,h,z,a1)


def leader_last(b,W,z,leaders,reverse=False):
    a1,a2,beta=leaders;w,s=W[:12],W[12:]
    if reverse:ar.mul_xor0(b,s,a2,beta)
    ar.mul_xor0(b,w,a2,z);ar.mul_xor0(b,s,a1,z)
    if not reverse:ar.mul_xor0(b,s,a2,beta)


def leader_step(b,U,W,z,leaders,reverse=False):
    if not reverse:
        leader_first(b,U,z,leaders);leader_last(b,W,z,leaders)
    else:
        leader_last(b,W,z,leaders,True);leader_first(b,U,z,leaders,True)


def pivot(b,A,B,leaders,reverse=False,k=K):
    n=len(A);m=(n-1)//2
    assert n==len(B) and n>=3 and n%2
    U=combine(A[:2]);W=combine(B[:2]);a1,a2,beta=leaders
    u,h=A[:2];s=B[1];z=B[-1]
    def first_body():
        for i in range(1,m):
            mul24_xor99(b,U,combine(B[2*i:2*i+2]),combine(A[2*i:2*i+2]),k)
            ar.mul_xor0(b,h,B[2*i-1],A[2*i])
        ar.mul_xor0(b,u,z,A[-1]);ar.mul_xor0(b,h,B[-2],A[-1])
    def second_body():
        if m==1:return
        for i in range(1,m-1):
            mul24_xor99(b,W,combine(A[2*i+2:2*i+4]),combine(B[2*i:2*i+2]),k)
            ar.mul_xor0(b,s,A[2*i+1],B[2*i])
        mul24_xor99(b,W,combine([A[-1],a1]),combine(B[-3:-1]),k)
        ar.mul_xor0(b,s,A[-2],B[-3])
    def second_head(divide):
        source=combine(A[2:4]) if m>1 else combine([A[-1],a1])
        closed_scale24(b,W,source,divide,k)
    if not reverse:
        closed_scale24(b,U,W,True,k)
        first_body();leader_first(b,U,z,leaders,carry=A[-1],k=k)
        second_head(True);second_body();leader_last(b,W,z,leaders)
    else:
        leader_last(b,W,z,leaders,True);second_body();second_head(False)
        leader_first(b,U,z,leaders,True,carry=A[-1],k=k);first_body()
        closed_scale24(b,U,W,False,k)
    return U,W,list(A[2:]),list(B[2:])


def qframe(b,A,B,leaders,k=K,reverse=False):
    a1,a2,beta=leaders
    linear_words(b,list(A)+[a1,a2],qadic_matrix(len(A)+2,k),reverse)
    linear_words(b,list(B)+[beta],qadic_matrix(len(B)+1,k),reverse)


def frames_for(A,B):
    A=list(A);B=list(B);frames=[];j=0
    while len(A)>=3:
        c=2*j;k=K^mul(c,c)^c
        frames.append((A,B,k));A=A[2:];B=B[2:];j+=1
    return frames,A,B


def sweep(b,A,B,reverse=False):
    """Exact70-word permutation; all virtual leader qubits returned to0.

    Heads are raw continued-fraction heads, not original Hermite jets.
    The final denominator tail is the initial q-adic top coordinate.
    """
    frames,C,D=frames_for(A,B)
    leaders=[b.alloc_qubits(12)for _ in range(3)];b.x(leaders[2][0])
    z=B[-1]
    if not reverse:
        qframe(b,A,B,leaders,frames[0][2])
        for j,(a,d,k) in enumerate(frames):
            pivot(b,a,d,leaders,k=k)
            if j+1<len(frames):
                qframe(b,a[2:],d[2:],leaders,k,True)
                qframe(b,a[2:],d[2:],leaders,frames[j+1][2])
        for a,d,k in reversed(frames):
            leader_step(b,combine(a[:2]),combine(d[:2]),z,leaders,True)
    else:
        for a,d,k in frames:
            leader_step(b,combine(a[:2]),combine(d[:2]),z,leaders)
        for j in reversed(range(len(frames))):
            a,d,k=frames[j]
            pivot(b,a,d,leaders,True,k)
            if j:
                qframe(b,a,d,leaders,k,True)
                qframe(b,a,d,leaders,frames[j-1][2])
        qframe(b,A,B,leaders,frames[0][2],True)
    b.x(leaders[2][0])
    for x in leaders:b.free(x)
    return [(a[:2],d[:2])for a,d,k in frames],C,D
