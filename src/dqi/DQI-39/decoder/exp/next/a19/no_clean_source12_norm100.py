"""A13's complete nonzero source with whole-multiplier dirty controls.

Three norm scales cost100 rather than120 Toffolis apiece. The outer
source and all zero/pure-subfield corrections retain their exact maps.
"""
from contextlib import contextmanager
from functools import lru_cache
from dirty_norm_control import controlled_norm3
import no_clean_source12_inv72 as old
import no_clean_source12 as prior
import virtual_norm as vn
from no_clean_source12_inv72 import (ar,replay,inverse6_dirty,one_plus_zeta,
    mcx_dirty,controlled_linear_predicate,key_scale6,logarithm,
    regular_matrix12,controlled_mul)


class Tape(prior.Tape):
    def mul_boundary(self,*args):self.ops.append(('mul_boundary',tuple(args)))
    def norm_boundary(self,*args):self.ops.append(('norm_boundary',tuple(args)))


@lru_cache(None)
def correction_program():
    original=vn.mul_xor_noscratch;original2=prior.mul_xor_noscratch
    original_norm=vn.norm_scale3;old_tape=prior.Tape
    def marked_mul(b,*args):
        wires=sum((list(x) for x in args),[])
        b.mul_boundary(*wires);original(b,*args);b.mul_boundary(*wires)
    def marked_norm(b,x,y,inverse=False):
        target=any(6<=j<18 for j in x)
        args=list(x)+list(y)+[int(inverse)]
        if target:b.norm_boundary(*args)
        original_norm(b,x,y,inverse)
        if target:b.norm_boundary(*args)
    vn.mul_xor_noscratch=prior.mul_xor_noscratch=marked_mul
    vn.norm_scale3=marked_norm;prior.Tape=Tape
    try:
        t=Tape();r=list(range(6));x=list(range(6,18));dirty=list(range(18,26))
        inverse6_dirty(t,r,dirty);one_plus_zeta(t,x,r,True);inverse6_dirty(t,r,dirty)
    finally:
        vn.mul_xor_noscratch=original;prior.mul_xor_noscratch=original2
        vn.norm_scale3=original_norm;prior.Tape=old_tape
    chunks=[];block=None
    for name,args in t.ops:
        if name.endswith('_boundary'):
            if block is None:block=[];block_args=args;block_kind=name[:-9]
            else:
                assert args==block_args and name==block_kind+'_boundary'
                if block_kind=='norm':
                    # one_plus_zeta's inverse replays a whole recorded tape
                    # backwards, including boundary markers. Recover the
                    # actual block orientation from its literal gates.
                    reference=Tape();original_norm(reference,list(args[:3]),list(args[3:6]),bool(args[6]))
                    if tuple(block)==tuple(reversed(reference.ops)):
                        args=tuple(args[:6])+(int(not args[6]),)
                    else:assert tuple(block)==tuple(reference.ops)
                chunks.append((block_kind,(args,tuple(block))));block=None
        elif block is None:chunks.append(('op',(name,args)))
        else:block.append((name,args))
    assert block is None
    rows={j:1<<(j-6) for j in x}
    for kind,data in chunks:
        if kind in ('mul','norm'):continue
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


def exception_correction(b,x,r,key,borrow,inverse=False):
    if inverse:
        t=Tape();exception_correction(t,list(range(6,18)),list(range(6)),list(range(18,24)),list(range(24,32)))
        replay(b,t.ops,list(r)+list(x)+list(key)+list(borrow[:8]),True);return
    chunks,off,off_back=correction_program();wires=list(r)+list(x)+list(borrow[:8])
    for kind,data in chunks:
        if kind=='mul':controlled_mul(b,data,wires,key,borrow)
        elif kind=='norm':
            args,_=data
            xx=[wires[j] for j in args[:3]];yy=[wires[j] for j in args[3:6]]
            controlled_norm3(b,xx,yy,key,borrow,bool(args[6]))
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
