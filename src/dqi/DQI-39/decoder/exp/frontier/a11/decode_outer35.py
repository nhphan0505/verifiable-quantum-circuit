"""Recover the last full product's known highest coefficient linearly.

At this boundary r_before=1+h*Q. Interpolation at35 points gives the full
product modulo their monic polynomial. Its missing coefficient is h*Q,
which is already present as r_before+1. The redundant leader is measured
and its exact bilinear phase is paid before the head is consumed.
"""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import decode_virtual_leader as virtual
from decode_low_crt import combo

@lru_cache(None)
def points_polynomial():
    from exp.decoder.common import pmul
    p=[1]
    for t in range(35):p=pmul(p,[t,1])
    assert len(p)==36 and p[-1]==1
    return tuple(p)


def install(entry):
    synth=entry.__globals__['synthesize'];folds=synth.__globals__['folds'];sg=dict(folds.sg)
    fn=sg['absorb_even'];original=fn.__globals__['full_product'];scope=fn.__globals__
    base,old,ar,cx=scope['base'],scope['old'],scope['ar'],scope['cx']
    def full_product(b,head,A,Q,target):
        if len(target)!=36:return original(b,head,A,Q,target)
        out=target[:-1];r=target[-1];V,W=base.vandermonde(35)
        for t in range(35):
            old.rank_affine(b,head,[1,t],A+[Q],V[t][:len(A)+1],out,[W[j][t]for j in range(35)])
        for word,co in zip(out,points_polynomial()[:-1]):
            if not co:continue
            cx(b,r,word,co)
            for j in ar.bits(co):b.x(word[j])
        mask=b.alloc_bits(12);b.hmr(r,mask)
        b.z(mask[0]);ar.phase_product(b,head[1],Q,mask);b.free(mask)
        b.x(r[0])
    sg['absorb_even']=combo.xsub.clone(fn,dict(scope,full_product=full_product))
    fs=SimpleNamespace(**dict(vars(folds),sg=sg))
    sy=combo.xsub.clone(synth,dict(synth.__globals__,folds=fs))
    result=combo.xsub.clone(entry,dict(entry.__globals__,synthesize=sy))
    assert result.__globals__['convert_safe'] is entry.__globals__['convert_safe']
    assert result.__globals__['baseline'] is entry.__globals__['baseline']
    return result


decode=install(virtual.decode)
