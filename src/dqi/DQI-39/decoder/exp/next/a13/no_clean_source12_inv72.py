"""Third exact completion: controlled bilinearity and a six-wire correction.

Eight arbitrary dirty qubits suffice. Each multiply-add is an involution;
two controls from a dirty flag cancel that flag's initial value exactly.
"""
from contextlib import contextmanager
from functools import lru_cache
import no_clean_source12 as prior
import virtual_norm as vn
from no_clean_source12 import (ar,Tape as BaseTape,replay,inverse6_dirty,one_plus_zeta,
    mcx_dirty,controlled_linear_predicate,key_scale6,logarithm,regular_matrix12)

from dirty_inverse6 import inverse6_dirty

class Tape(BaseTape):
    def mul_boundary(self,*args):self.ops.append(('mul_boundary',tuple(args)))

@lru_cache(None)
def correction_program():
    original=vn.mul_xor_noscratch;original2=prior.mul_xor_noscratch;old_tape=prior.Tape
    def marked(b,*args):
        wires=sum((list(x) for x in args),[])
        b.mul_boundary(*wires);original(b,*args);b.mul_boundary(*wires)
    vn.mul_xor_noscratch=prior.mul_xor_noscratch=marked;prior.Tape=Tape
    try:
        t=Tape();r=list(range(6));x=list(range(6,18));dirty=list(range(18,26))
        inverse6_dirty(t,r,dirty);one_plus_zeta(t,x,r,True);inverse6_dirty(t,r,dirty)
    finally:vn.mul_xor_noscratch=original;prior.mul_xor_noscratch=original2;prior.Tape=old_tape
    chunks=[];block=None
    for name,args in t.ops:
        if name=='mul_boundary':
            if block is None:block=[];block_args=args
            else:
                assert args==block_args
                chunks.append(('mul',(args,tuple(block))));block=None
        elif block is None:chunks.append(('op',(name,args)))
        else:block.append((name,args))
    assert block is None
    rows={j:1<<(j-6) for j in x}
    for kind,data in chunks:
        if kind=='mul':continue # A disabled multiply-add is the identity.
        name,args=data;touched=[j in rows for j in args]
        if name=='ccx':
            if any(touched):assert touched[-1] and sum(touched)>=2
            continue
        if any(touched):
            assert all(touched)
            if name=='cx':rows[args[1]]^=rows[args[0]]
            elif name=='swap':rows[args[0]],rows[args[1]]=rows[args[1]],rows[args[0]]
            else:raise AssertionError((name,args))
    columns=tuple(sum(((rows[6+i]>>j)&1)<<i for i in range(12)) for j in range(12))
    return tuple(chunks),columns,tuple(ar.inverse_columns(columns))

def controlled_mul(b,data,wires,key,borrow):
    args,ops=data;n=len(args)//3;assert n in (3,6)
    a,x,z=([wires[j] for j in args[k*n:(k+1)*n]] for k in range(3))
    h=borrow[0];scratch=borrow[1:];dirty=scratch[:n]
    def controlled():
        b.ccx(h,a,dirty);vn.mul_xor_noscratch(b,dirty,x,z)
        b.ccx(h,a,dirty);vn.mul_xor_noscratch(b,dirty,x,z)
    mcx_dirty(b,key,h,scratch);controlled()
    mcx_dirty(b,key,h,scratch);controlled()

def exception_correction(b,x,r,key,borrow,inverse=False):
    if inverse:
        t=Tape();exception_correction(t,list(range(6,18)),list(range(6)),list(range(18,24)),list(range(24,32)))
        replay(b,t.ops,list(r)+list(x)+list(key)+list(borrow[:8]),True);return
    chunks,off,off_back=correction_program();wires=list(r)+list(x)+list(borrow[:8])
    for kind,data in chunks:
        if kind=='mul':controlled_mul(b,data,wires,key,borrow)
        else:
            name,args=data;mapped=[wires[j] for j in args]
            if name=='ccx' and any(6<=j<18 for j in args):
                mcx_dirty(b,list(key)+mapped[:2],mapped[2],borrow)
            else:getattr(b,name)(*mapped)
    ar.linear_inplace(b,x,off_back)
    to,back,_=ar.tower(12)
    tower_off=tuple(ar.apply(to,ar.apply(off,ar.apply(back,1<<j))) for j in range(12))
    assert tower_off[:6]==tuple(1<<j for j in range(6)) and all(v&63==0 for v in tower_off[6:])
    ar.linear_inplace(b,x,to)
    controlled_linear_predicate(b,x[6:],tuple(v>>6 for v in tower_off[6:]),key,borrow)
    ar.linear_inplace(b,x,back)

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
