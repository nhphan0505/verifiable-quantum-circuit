"""A predicate-controlled GF8 multiplier with one borrowed dirty flag.

The field inversion J is an involution and J M J = inverse(M).
Consequently J^d M^(d xor p) M^(-d) J^d = M^p, including x=0.
All other borrowed wires are returned. No clean ancilla or measurement.
"""
from pathlib import Path
from functools import lru_cache
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'exp/next/a13'),str(ROOT/'exp/next/a11'),str(ROOT/'exp/new/a16'),
             str(ROOT/'exp/new/a10'),str(ROOT/'exp/new/a07')]
from virtual_norm import ar,norm_scale3
from lowclean import PERMS,mcx_dirty,controlled_linear
from constant_scale import factor


def controlled_inverse3(b,x,h,borrow):
    # Move every fixed linear operation to the end. Each nonlinear gate is
    # conjugated by the accumulated free linear frame, and the final linear
    # map is controlled in rank-two rather than three CNOT factors.
    columns=tuple(1<<j for j in range(3))
    for op,*args in PERMS['inverse']['gates']:
        if op=='ccx':
            ar.linear_inplace(b,x,columns)
            mcx_dirty(b,[h,x[args[0]],x[args[1]]],x[args[2]],borrow)
            ar.linear_inplace(b,x,tuple(ar.inverse_columns(columns)))
        elif op=='cx':
            a,z=args
            columns=tuple(v^(((v>>a)&1)<<z) for v in columns)
        else:raise AssertionError(op)
    for w,f in factor(columns):
        p=next(i for i in range(3) if f>>i&1)
        others=[i for i in range(3) if i!=p and f>>i&1]
        for i in others:b.cx(x[i],x[p])
        q=next(i for i in range(3) if i!=p and w>>i&1)
        direction=[i for i in range(3) if i not in(p,q) and w>>i&1]
        for i in direction:b.cx(x[q],x[i])
        b.ccx(h,x[p],x[q])
        for i in reversed(direction):b.cx(x[q],x[i])
        for i in reversed(others):b.cx(x[i],x[p])


class ControlledNormBuilder:
    def __init__(self,b,h,borrow):self.b=b;self.h=h;self.borrow=borrow
    def cx(self,*args):return self.b.cx(*args)
    def swap(self,*args):return self.b.swap(*args)
    def ccx(self,a,c,z):return mcx_dirty(self.b,[self.h,a,c],z,self.borrow)


def controlled_norm3(b,x,y,key,borrow,inverse=False):
    assert len(x)==len(y)==3 and len(borrow)>=8
    h=borrow[0];scratch=borrow[1:]
    controlled_inverse3(b,x,h,scratch)
    mcx_dirty(b,key,h,scratch)
    norm_scale3(ControlledNormBuilder(b,h,scratch),x,y,inverse)
    mcx_dirty(b,key,h,scratch)
    norm_scale3(ControlledNormBuilder(b,h,scratch),x,y,not inverse)
    controlled_inverse3(b,x,h,scratch)


def controlled_linear_factor(b,x,columns,h):
    for w,f in factor(tuple(columns)):
        p=next(i for i in range(len(x)) if f>>i&1)
        others=[i for i in range(len(x)) if i!=p and f>>i&1]
        for i in others:b.cx(x[i],x[p])
        q=next(i for i in range(len(x)) if i!=p and w>>i&1)
        direction=[i for i in range(len(x)) if i not in(p,q) and w>>i&1]
        for i in direction:b.cx(x[q],x[i])
        b.ccx(h,x[p],x[q])
        for i in reversed(direction):b.cx(x[q],x[i])
        for i in reversed(others):b.cx(x[i],x[p])


def controlled_norm_pair(b,targets,y,key,borrow,inverse=False,scalar=1):
    h=borrow[0];scratch=borrow[1:];f=ar.field(3)
    for x in targets:controlled_inverse3(b,x,h,scratch)
    mcx_dirty(b,key,h,scratch)
    for x in targets:
        norm_scale3(ControlledNormBuilder(b,h,scratch),x,y,inverse)
        if scalar!=1:controlled_linear_factor(b,x,tuple(f.mul(scalar,1<<j)for j in range(3)),h)
    mcx_dirty(b,key,h,scratch)
    for x in targets:
        norm_scale3(ControlledNormBuilder(b,h,scratch),x,y,not inverse)
        if scalar!=1:controlled_linear_factor(b,x,tuple(f.mul(f.invert(scalar),1<<j)for j in range(3)),h)
    for x in targets:controlled_inverse3(b,x,h,scratch)


def controlled_involution(b,x,columns,key,borrow):
    assert tuple(ar.apply(columns,v) for v in columns)==tuple(1<<j for j in range(len(x)))
    frame,back,rank=involution_frame(tuple(columns))
    h=borrow[0];scratch=borrow[1:]
    ar.linear_inplace(b,x,frame)
    mcx_dirty(b,key,h,scratch)
    for j in range(rank):b.ccx(h,x[j],x[rank+j])
    mcx_dirty(b,key,h,scratch)
    for j in range(rank):b.ccx(h,x[j],x[rank+j])
    ar.linear_inplace(b,x,back)


@lru_cache(None)
def involution_frame(columns):
    n=len(columns);nil=tuple(v^(1<<j)for j,v in enumerate(columns))
    def append(rows,v):
        while v:
            k=v.bit_length()-1
            if k in rows:v^=rows[k]
            else:rows[k]=v;return True
        return False
    image={};pre=[];out=[]
    for j,v in enumerate(nil):
        if append(image,v):pre.append(1<<j);out.append(v)
    basis=pre+out;rows={}
    for v in basis:assert append(rows,v)
    for v in range(1,1<<n):
        if len(basis)==n:break
        if ar.apply(nil,v)==0 and append(rows,v):basis.append(v)
    assert len(basis)==n
    back=tuple(basis);frame=tuple(ar.inverse_columns(back));rank=len(pre)
    want=tuple((1<<j)^((1<<(rank+j))if j<rank else 0)for j in range(n))
    actual=tuple(ar.apply(frame,ar.apply(columns,v))for v in back)
    assert actual==want
    return frame,back,rank
