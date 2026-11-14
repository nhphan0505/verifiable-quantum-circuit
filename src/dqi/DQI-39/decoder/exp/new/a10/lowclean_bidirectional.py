"""Completed multiply/divide contexts without scalar source inversion.

For every y, the source-preserving multiplication by y+[y=0] is a
permutation. Its inverse follows the reverse target-factor order. The
source ratio is formed by that same recursive division and restored by
ordinary completed multiplication, so no inv0 source is ever required.
"""
from pathlib import Path
from contextlib import contextmanager
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'exp/new/a07'))
from lowclean_zerochart import ar,chart
from lowclean import permutation3,controlled_linear,zero_toggle,mul_xor_noscratch


@contextmanager
def source(b,y,inverse=False):
    n=len(y)
    if n==3:
        f=ar.field(3);permutation3(b,y,'log')
        alpha=f.invert(2) if inverse else 2
        cols=tuple(f.mul(alpha,1<<i) for i in range(3))
        def apply(targets):
            for j in range(3):
                pre=tuple(f.pow(1<<i,1<<((3-j)%3)) for i in range(3))
                post=tuple(f.pow(1<<i,1<<j) for i in range(3))
                for x in targets:
                    ar.linear_inplace(b,x,pre);controlled_linear(b,x,cols,y[j]);ar.linear_inplace(b,x,post)
        yield apply
        permutation3(b,y,'log',True)
        return
    assert n in (6,12)
    m=n//2;to,back,K=ar.tower(n);ar.linear_inplace(b,y,to)
    r,g=y[:m],y[m:]
    F=b.alloc_qubits(1)[0];zero_toggle(b,g,F,r);b.cswap(F,r,g)
    scale_many(b,[r],g,True)
    forward_cols=tuple((1<<j)|(1<<(m+j)) for j in range(m))+tuple(1<<j for j in range(m))
    correction=tuple(ar.inverse_columns(forward_cols)) if inverse else forward_cols
    def apply(targets):
        for x in targets:ar.linear_inplace(b,x,to)
        halves=[(x[:m],x[m:]) for x in targets]
        if inverse:
            scale_many(b,[v for pair in halves for v in pair],g,True)
            for x in targets:controlled_linear(b,x,correction,F)
            for a,z in halves:b.swap(a,z);mul_xor_noscratch(b,r,a,z)
            chart(b,r,F,K);scale_many(b,[z for a,z in halves],r,True);chart(b,r,F,K,True)
            for a,z in halves:mul_xor_noscratch(b,r,z,a);b.cx(z,a)
        else:
            for a,z in halves:b.cx(z,a);mul_xor_noscratch(b,r,z,a)
            chart(b,r,F,K);scale_many(b,[z for a,z in halves],r);chart(b,r,F,K,True)
            for a,z in halves:mul_xor_noscratch(b,r,a,z);b.swap(a,z)
            for x in targets:controlled_linear(b,x,correction,F)
            scale_many(b,[v for pair in halves for v in pair],g)
        for x in targets:ar.linear_inplace(b,x,back)
    yield apply
    scale_many(b,[r],g);b.cswap(F,r,g);zero_toggle(b,g,F,r);b.free(F)
    ar.linear_inplace(b,y,back)


def scale_many(b,targets,y,inverse=False):
    with source(b,y,inverse) as apply:apply(targets)


def scale(b,x,y,inverse=False):
    scale_many(b,[x],y,inverse)
