"""Whole unsynthesis replacement with coherent x-padding completion.

At a zero quotient source the old clipped synthesis removes the two lower
terms contributed by its implicit top coefficient.  Undo that completion
before routing the quotient: P += [source=0]*lead*(k+x)*x^(d-2).
The predicate is coherent and the rank is never inspected.
"""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(ROOT/'exp/round7/a05')]
import raw_live_return as live
import raw_return as rr
from raw_pair import frames_for,qframe,K,mul,combine
from paired_coefficient import qadic
from raw_pair_head24_erased import erase_head
from raw_pair_narrow import bodies
from exp.arithmetic.division import zero_flag,phase_zero
from exp.partial_gauge.tail import controlled_linear_xor


def constant_qadic(k,degree,n):
    """Constant q-adic coefficients of (k+x)*x^(degree-2)."""
    p=[0]*(degree-2)+[k,1];out=[]
    while len(out)<n:
        q=[0]*max(0,len(p)-2)
        for i in range(len(p)-1,1,-1):
            a=p[i];q[i-2]=a
            p[i]^=a;p[i-1]^=a;p[i-2]^=mul(k,a)
        out.extend((p+[0,0])[:2]);p=q
    assert not any(p)
    return out[:n]


def complete_zero(b,target,lead,source,degree,k,old_mask=None):
    F=zero_flag(b,source)
    if old_mask is not None:
        b.cz(F,old_mask[0]);b.free(old_mask)
    co=constant_qadic(k,degree,len(target))
    assert co[-1]==0
    controlled_linear_xor(b,F,lead,target,co)
    mask=b.alloc_bits(1);b.hmr(F,mask[0]);b.free(F)
    phase_zero(b,source,mask[0]);b.free(mask)


def sweep(b,A,B,folds):
    heads=rr.tail.heads_from_banks(A,B)
    frames,_,_=frames_for(A,B);a0,d0,k0=frames[0]
    U0=combine(a0[:2]);W0=combine(d0[:2]);z=B[-1]
    # The first top numerator coefficient is the implicit constant zero.
    qadic(b,A,B,k=k0);rr.raw.closed_scale24(b,U0,W0,True,k0)
    leaders=[b.alloc_qubits(12)for _ in range(3)];b.x(leaders[2][0])
    for j,(a,d,k) in enumerate(frames):
        n=len(a);a1,a2,beta=leaders
        U=combine(a[:2]);W=combine(d[:2])
        if j:
            qframe(b,a,d,leaders,frames[j-1][2],True)
            qframe(b,a,d,leaders,k)
            complete_zero(b,a+[a1,a2],a2,W,n+1,k,folds[2*j][1])
            rr.raw.closed_scale24(b,U,W,True,k)
        first,second,_=bodies(b,a,d,leaders,k)
        first()
        if not j:erase_head(b,*heads[0],z,leaders)
        source=combine(a[2:4])if n>3 else combine([a[-1],a1])
        complete_zero(b,d+[beta],beta,source,n,k,folds[2*j+1][1])
        rr.raw.closed_scale24(b,W,source,True,k)
        second()
    return heads,leaders


def consume_synthesis(b,A,B,pole,old_undo):
    cells=rr.closure(old_undo)
    folds={row[0]:row[-1]for row in cells['hist']}
    assert set(folds)==set(range(1,34))
    with b.mark('outer_quadratic'):
        rr.outer_quadratic(b,A,B,True)
    with b.mark('completed_paired_sweep'):
        heads,leaders=sweep(b,A,B,folds)
    with b.mark('live_tail_join'):
        heads,real=live.consume_live_tail(b,A,B,heads,leaders,pole,cells['tt'],old_undo.__globals__['tail_inplace'])
    with b.mark('old_head_characters'):
        for i,(hm,_)in sorted(folds.items()):
            b.cz(combine(heads[i]),hm);b.free(hm)
    return heads,real

route_words=rr.route_words
