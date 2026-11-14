"""Share each low-clean source chart across every simultaneous target."""
from types import FunctionType
import lowclean as old
from lowclean import (ar,permutation3,controlled_linear,constant_scale,
    zero_toggle,chart,mul_xor_noscratch)


def scale3_many(b,targets,y):
    f=ar.field(3);permutation3(b,y,'log')
    alpha=tuple(f.mul(2,1<<i) for i in range(3))
    for j in range(3):
        pre=tuple(f.pow(1<<i,1<<((3-j)%3)) for i in range(3))
        post=tuple(f.pow(1<<i,1<<j) for i in range(3))
        for x in targets:
            ar.linear_inplace(b,x,pre);controlled_linear(b,x,alpha,y[j]);ar.linear_inplace(b,x,post)
    permutation3(b,y,'log',True)


def scale_many(b,targets,y):
    n=len(y);assert all(len(x)==n for x in targets)
    if n==3:scale3_many(b,targets,y);return
    assert n in (6,12)
    m=n//2;to,back,K=ar.tower(n)
    ar.linear_inplace(b,y,to)
    for x in targets:ar.linear_inplace(b,x,to)
    halves=[(x[:m],x[m:]) for x in targets]
    r,g=y[:m],y[m:]
    F=b.alloc_qubits(1)[0];zero_toggle(b,g,F,r);b.cswap(F,r,g)
    inverse(b,g);scale(b,r,g);inverse(b,g)
    for a,z in halves:b.cx(z,a);mul_xor_noscratch(b,r,z,a)
    qF=chart(b,r,F,K)
    scale_many(b,[z for a,z in halves],r)
    chart(b,r,F,K,True)
    for a,z in halves:mul_xor_noscratch(b,r,a,z);b.swap(a,z)
    f=ar.field(m);qi=f.invert(qF)
    cols=tuple(f.mul(qi,1<<j)|(f.mul(qi,1<<j)<<m) for j in range(m))+tuple(1<<j for j in range(m))
    for x in targets:controlled_linear(b,x,cols,F)
    scale_many(b,[v for pair in halves for v in pair],g)
    scale(b,r,g);b.cswap(F,r,g);zero_toggle(b,g,F,r);b.free(F)
    ar.linear_inplace(b,y,back)
    for x in targets:ar.linear_inplace(b,x,back)


def scale(b,x,y):
    return scale_many(b,[x],y)


_scope=dict(old.inverse.__globals__,scale=scale)
inverse=FunctionType(old.inverse.__code__,_scope,'inverse')
_scope['inverse']=inverse


def zeros(b,n):
    m=b.alloc_bits(n);b.bit_store(m,False);return m


def stream(b,x):
    inverse(b,x);return zeros(b,len(x))


def scale_defer(b,x,y):
    scale(b,x,y);return zeros(b,len(x))


def many_defer(b,targets,y):
    scale_many(b,targets,y)
    return [zeros(b,len(x)) for x in targets]


def inverse_phase(b,x,mask):
    inverse(b,x);b.cz(x,mask);inverse(b,x)
