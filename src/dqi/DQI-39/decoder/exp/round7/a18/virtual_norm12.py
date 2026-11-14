"""Exact zero-scratch scaling by r^2+r+K in GF4096.

The source retains its Artin--Schreier kernel bit in the fixed trace slot.
The arithmetic never reads that slot. K must have absolute trace one.
"""
from pathlib import Path
from contextlib import contextmanager
from functools import lru_cache
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'exp/next/a13'),str(ROOT/'exp/new/a16')]
from virtual_norm import ar,norm_scale3,encoded_norm3,regular_matrix12,mul_xor_noscratch


def regular_matrix6(b,x,r,inverse=False):
    to,back,K=ar.tower(6);ar.linear_inplace(b,x,to);a,z=x[:3],x[3:]
    if inverse:
        b.swap(a,z);mul_xor_noscratch(b,r,a,z)
        with encoded_norm3(b,r,K) as apply:apply([z],True)
        mul_xor_noscratch(b,r,z,a);b.cx(z,a)
    else:
        b.cx(z,a);mul_xor_noscratch(b,r,z,a)
        with encoded_norm3(b,r,K) as apply:apply([z])
        mul_xor_noscratch(b,r,a,z);b.swap(a,z)
    ar.linear_inplace(b,x,back)


def trace_scale6(b,x,source,inverse=False):
    """Scale canonical GF64 x by trace-one source in tower coordinates.

    Source bit3 is virtual1 and may hold any protected spectator bit.
    """
    a,g=source[:3],source[3:];to,back,K=ar.tower(6)
    norm_scale3(b,a,g,True)
    if inverse:
        ar.linear_inplace(b,x,to)
        norm_scale3(b,x[:3],g,True);norm_scale3(b,x[3:],g,True)
        ar.linear_inplace(b,x,back)
        regular_matrix6(b,x,a,True)
    else:
        regular_matrix6(b,x,a)
        ar.linear_inplace(b,x,to)
        norm_scale3(b,x[:3],g);norm_scale3(b,x[3:],g)
        ar.linear_inplace(b,x,back)
    norm_scale3(b,a,g)


@lru_cache(None)
def encoding(K):
    f=ar.field(12);to12,back12,_=ar.tower(12);to6,back6,_=ar.tower(6)
    def convert(value):
        value=ar.apply(to12,value)
        return (value&63)|(ar.apply(to6,value>>6)<<6)
    trace_slot=9
    assert all(((convert(f.square(1<<i)^(1<<i))>>trace_slot)&1)==0 for i in range(12))
    assert (convert(K)>>trace_slot)&1
    cols=tuple(convert(f.square(1<<i)^(1<<i)) ^ ((1<<trace_slot)if i==0 else 0)for i in range(12))
    constant=convert(K)^(1<<trace_slot)
    return cols,tuple(ar.inverse_columns(cols)),constant


@contextmanager
def encoded_norm12(b,r,K):
    cols,back,constant=encoding(K)
    ar.linear_inplace(b,r,cols);b.gf2_iadd(constant,target=r)
    a,g=r[:6],r[6:];to12,back12,_=ar.tower(12)
    trace_scale6(b,a,g,True)
    def apply(targets,inverse=False):
        for x in targets:
            if inverse:
                ar.linear_inplace(b,x,to12)
                trace_scale6(b,x[:6],g,True);trace_scale6(b,x[6:],g,True)
                ar.linear_inplace(b,x,back12)
                regular_matrix12(b,x,a,True)
            else:
                regular_matrix12(b,x,a)
                ar.linear_inplace(b,x,to12)
                trace_scale6(b,x[:6],g);trace_scale6(b,x[6:],g)
                ar.linear_inplace(b,x,back12)
    yield apply
    trace_scale6(b,a,g)
    b.gf2_iadd(constant,target=r);ar.linear_inplace(b,r,back)
