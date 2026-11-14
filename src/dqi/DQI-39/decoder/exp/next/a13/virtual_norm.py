"""Anisotropic norm multipliers with no fresh wire or measurement.

The source is encoded as its Artin--Schreier image's trace-one
coordinates plus the omitted kernel bit.  The multiplier never reads
that kernel bit.  This is a component, not a whole-decoder width claim.
"""
from pathlib import Path
from contextlib import contextmanager
from functools import lru_cache
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'exp/new/a16'),str(ROOT/'exp/new/a10'),
             str(ROOT/'exp/new/a07'),str(ROOT/'exp/next/a04')]
from lowclean_norm5log7 import ar,norm_scale3,mul_xor_noscratch


@lru_cache(None)
def norm_encoding(n,K):
    """Output in the field's tower coordinates; store input bit0 in trace slot."""
    f=ar.field(n)
    if n==3:
        to=tuple(1<<i for i in range(n));trace_slot=0
    elif n==6:
        to,_,_=ar.tower(6);trace_slot=3
    else:raise ValueError(n)
    columns=tuple(ar.apply(to,f.square(1<<i)^(1<<i)) ^
                  ((1<<trace_slot) if i==0 else 0) for i in range(n))
    constant=ar.apply(to,K)^(1<<trace_slot)
    assert not constant>>trace_slot&1
    return columns,tuple(ar.inverse_columns(columns)),constant,trace_slot


@contextmanager
def encoded_norm3(b,r,K):
    columns,back,c,_=norm_encoding(3,K)
    ar.linear_inplace(b,r,columns);b.gf2_iadd(c,target=r)
    # Actual q=r_old²+r_old+K has trace bit0=1. norm_scale3
    # uses only its two remaining coordinates.
    yield lambda targets,inverse=False: [norm_scale3(b,x,r,inverse) for x in targets]
    b.gf2_iadd(c,target=r);ar.linear_inplace(b,r,back)


@contextmanager
def encoded_norm6(b,r,K):
    columns,back,c,_=norm_encoding(6,K)
    ar.linear_inplace(b,r,columns);b.gf2_iadd(c,target=r)
    a,g=r[:3],r[3:]
    # g's true trace bit is1. Its stored bit0 instead holds the outer
    # Artin--Schreier kernel. The restricted scaler ignores that bit.
    norm_scale3(b,a,g,True)
    to6,back6,K6=ar.tower(6)
    def apply(targets,inverse=False):
        for x in targets:
            ar.linear_inplace(b,x,to6)
            u,v=x[:3],x[3:]
            if inverse:
                norm_scale3(b,u,g,True);norm_scale3(b,v,g,True)
                b.swap(u,v);mul_xor_noscratch(b,a,u,v)
                with encoded_norm3(b,a,K6) as qa:qa([v],True)
                mul_xor_noscratch(b,a,v,u);b.cx(v,u)
            else:
                b.cx(v,u);mul_xor_noscratch(b,a,v,u)
                with encoded_norm3(b,a,K6) as qa:qa([v])
                mul_xor_noscratch(b,a,u,v);b.swap(u,v)
                norm_scale3(b,u,g);norm_scale3(b,v,g)
            ar.linear_inplace(b,x,back6)
    yield apply
    norm_scale3(b,a,g)
    b.gf2_iadd(c,target=r);ar.linear_inplace(b,r,back)


def regular_matrix12(b,x,r,inverse=False):
    """Apply [[r,K],[1,r+1]] or its inverse to a12-bit target.

    r is a6-bit canonical source, K is the GF4096/GF64 tower constant.
    This is invertible for ALL64 r and uses no scratch.
    """
    to,back,K=ar.tower(12);ar.linear_inplace(b,x,to)
    a,z=x[:6],x[6:]
    if inverse:
        b.swap(a,z);mul_xor_noscratch(b,r,a,z)
        with encoded_norm6(b,r,K) as qa:qa([z],True)
        mul_xor_noscratch(b,r,z,a);b.cx(z,a)
    else:
        b.cx(z,a);mul_xor_noscratch(b,r,z,a)
        with encoded_norm6(b,r,K) as qa:qa([z])
        mul_xor_noscratch(b,r,a,z);b.swap(a,z)
    ar.linear_inplace(b,x,back)
