"""Full-fold reverse in remainder/low-Taylor coordinates.

This changes only coordinate transforms and bilinear coefficient updates.
All measurements are performed by the supplied exact fused divider.
"""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'exp/r-main/narrow240'),str(ROOT/'exp/frontier/root')]
import decode_combo as combo
import decode_fullfold

@lru_cache(None)
def crt_matrix(k,c,kap):
    """coeffs -> [remainder0,remainder1,low0,...,low(k-1),leader]."""
    from exp.decoder.common import divmodp
    n=k+3
    rows=[[0]*n for _ in range(n)]
    for j in range(n):
        poly=[0]*j+[1]
        _,rem=divmodp(poly,[kap,1,1])
        rem=rem+[0]*(2-len(rem))
        rows[0][j],rows[1][j]=rem[:2]
    for j in range(k):rows[2+j][j]=1
    rows[-1][-1]=1
    return tuple(tuple(row) for row in rows)


def absorb_even_low_crt(b,head,A,B,Q,r,c,kap,reverse=False,transcript=None):
    assert reverse
    k=len(B)
    out=head+B
    value=old.eval_implicit(b,A,Q,c)
    F=dv.zero_flag(b,value)
    old.eval_implicit(b,A,Q,c,True)
    linear_words(b,out+[r],crt_matrix(k,c,kap))
    v=epow(c,k+2)
    co=[(v&4095)^mul(c,v>>12),v>>12]
    old.controlled_linear_xor(b,F,r,head,co)
    value=old.eval_implicit(b,A,Q,c)
    cx(b,head[1],head[0],c)
    hm,fm=transcript
    def after():
        cx(b,head[1],head[0],c)
        old.eval_implicit(b,A,Q,c,True)
        b.cx(F,A[0][0])
        low_product(b,head,A,B)
        b.cx(F,A[0][0])
        q_times_low(b,B,kap,True)
        ar.mul_xor0(b,head[1],Q,r)
        old.eval_implicit(b,A,Q,c)
    divide_fused(b,combine(head),value,F,fm,after,K)
    b.cz(combine(head),hm)
    b.free(hm)
    old.eval_implicit(b,A,Q,c,True)
    return out,A,transcript


def install(entry,select=None):
    synth=entry.__globals__['synthesize']
    folds=synth.__globals__['folds']
    original=folds.ug['absorb_even']
    patched=combo.xsub.clone(absorb_even_low_crt,dict(original.__globals__,crt_matrix=crt_matrix,
        low_product=folds.ug['absorb'].__globals__['low_product']))
    if select is not None:
        def choose(b,head,A,B,Q,r,c,kap,reverse=False,transcript=None):
            fn=patched if len(B) in select else original
            return fn(b,head,A,B,Q,r,c,kap,reverse,transcript)
        replacement=choose
    else:replacement=patched
    ug=dict(folds.ug,absorb_even=replacement)
    proxy=SimpleNamespace(**dict(vars(folds),ug=ug))
    new_synth=combo.xsub.clone(synth,dict(synth.__globals__,folds=proxy))
    result=combo.xsub.clone(entry,dict(entry.__globals__,synthesize=new_synth))
    assert result.__globals__['convert_safe'] is entry.__globals__['convert_safe']
    assert result.__globals__['baseline'] is entry.__globals__['baseline']
    return result


decode=install(decode_fullfold.decode)
