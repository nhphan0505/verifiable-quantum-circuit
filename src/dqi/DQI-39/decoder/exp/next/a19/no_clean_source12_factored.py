"""Factor the fixed exceptional row into a subfield scalar and involution.

The scalar7 is absorbed into the shared pair of GF8 norm multipliers;
the remaining fixed matrix is an involution controlled by a dirty flag.
"""
from contextlib import contextmanager
from functools import lru_cache
import no_clean_source12_norm100 as prior
from no_clean_source12_norm100 import (ar,Tape,replay,inverse6_dirty,
    one_plus_zeta,mcx_dirty,key_scale6,logarithm,regular_matrix12,
    controlled_mul,controlled_norm3)
from dirty_norm_control import controlled_norm_pair,controlled_involution


def compose(a,b):return tuple(ar.apply(a,v)for v in b)


@lru_cache(None)
def compiled():
    chunks,off,off_back=prior.correction_program()
    t12,b12,_=ar.tower(12);t6,b6,_=ar.tower(6)
    f=ar.field(6);scalar=7
    embedded=ar.apply(b6,scalar)
    lam6=tuple(f.mul(embedded,1<<j)for j in range(6))
    lam=tuple(ar.apply(b12,(ar.apply(t12,1<<j)&63)|(ar.apply(lam6,ar.apply(t12,1<<j)>>6)<<6))for j in range(12))
    invlam=tuple(ar.inverse_columns(lam));U=compose(invlam,off)
    assert compose(U,U)==tuple(1<<j for j in range(12))
    assert compose(lam,U)==off and compose(U,lam)==off
    norm_indices=[i for i,(k,_)in enumerate(chunks)if k=='norm']
    first,second,last=norm_indices;assert second==first+1
    a1,a2=chunks[first][1][0],chunks[second][1][0]
    assert a1[3:]==a2[3:]
    prefix=tuple(1<<j for j in range(12));frames=[]
    for i,(kind,data)in enumerate(chunks):
        if kind=='op':
            name,args=data;touched=[6<=j<18 for j in args]
            if any(touched):
                assert all(touched)
                if name=='cx':
                    a,z=[j-6 for j in args]
                    prefix=tuple(v^(((v>>a)&1)<<z)for v in prefix)
                elif name=='swap':
                    a,z=[j-6 for j in args]
                    prefix=tuple(v^((((v>>a)^(v>>z))&1)*((1<<a)|(1<<z)))for v in prefix)
                else:assert name=='ccx'
        local=compose(prefix,compose(lam,tuple(ar.inverse_columns(prefix))))
        frames.append((local,tuple(ar.inverse_columns(local))))
    # At the shared pair, the transported scalar acts as multiplication7
    # on both three-bit targets, with all other target wires untouched.
    want=list(1<<j for j in range(12));f3=ar.field(3)
    for args in(a1,a2):
        wires=[j-6 for j in args[:3]]
        for k,j in enumerate(wires):want[j]=sum(((f3.mul(scalar,1<<k)>>v)&1)<<wires[v]for v in range(3))
    assert frames[first][0]==tuple(want)
    return chunks,off_back,U,tuple(frames),first,second,scalar


def exception_correction(b,x,r,key,borrow,inverse=False):
    if inverse:
        t=Tape();exception_correction(t,list(range(6,18)),list(range(6)),list(range(18,24)),list(range(24,32)))
        replay(b,t.ops,list(r)+list(x)+list(key)+list(borrow[:8]),True);return
    chunks,off_back,U,frames,first,second,scalar=compiled()
    wires=list(r)+list(x)+list(borrow[:8])
    for i,(kind,data)in enumerate(chunks):
        if i==second:continue
        conjugate=i>second and kind in('mul','norm')
        if conjugate:ar.linear_inplace(b,x,frames[i][1])
        if kind=='mul':controlled_mul(b,data,wires,key,borrow)
        elif kind=='norm':
            args,_=data;xx=[wires[j]for j in args[:3]];yy=[wires[j]for j in args[3:6]]
            if i==first:
                args2=chunks[second][1][0];xx2=[wires[j]for j in args2[:3]]
                controlled_norm_pair(b,[xx,xx2],yy,key,borrow,bool(args[6]),scalar)
            else:controlled_norm3(b,xx,yy,key,borrow,bool(args[6]))
        else:
            name,args=data;mapped=[wires[j]for j in args]
            if name=='ccx'and any(6<=j<18 for j in args):
                # The current source has no other target nonlinear gates.
                raise AssertionError((name,args))
            getattr(b,name)(*mapped)
        if conjugate:ar.linear_inplace(b,x,frames[i][0])
    ar.linear_inplace(b,x,off_back)
    controlled_involution(b,x,U,key,borrow)


@contextmanager
def source(b,y,borrow,inverse=False):
    assert len(y)==12 and len(borrow)>=8
    to,back,_=ar.tower(12);ar.linear_inplace(b,y,to)
    r,key=y[:6],y[6:];logarithm(b,key);key_scale6(b,r,key,True)
    def apply(targets):
        for x in targets:
            if inverse:exception_correction(b,x,r,key,borrow,True)
            regular_matrix12(b,x,r,inverse)
            ar.linear_inplace(b,x,to)
            key_scale6(b,x[:6],key,inverse);key_scale6(b,x[6:],key,inverse)
            ar.linear_inplace(b,x,back)
            if not inverse:exception_correction(b,x,r,key,borrow)
    yield apply
    key_scale6(b,r,key);logarithm(b,key,True);ar.linear_inplace(b,y,back)
