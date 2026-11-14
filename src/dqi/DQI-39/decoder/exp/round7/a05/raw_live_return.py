"""Join the raw sweep directly to its tail with virtual leaders still live.

The old raw kernel deflates three leaders after its last pivot.  Its tail
adapter then immediately inflates them again.  This schedule omits both
traversals and keeps the first U head erased until the scalar-prefix
return reconstructs it.  Rank completion is the same open obligation as
raw_return.py; no correctness claim is made on mismatching raw charts.
"""
import raw_return as rr
import tail_join as tail
from raw_pair import frames_for,qframe,K,mul,cx,combine
from paired_coefficient import qadic
from raw_pair_head24_erased import erase_head
from exp.arithmetic.division import phase_zero
from exp.decoder.common import reclaim


def live_sweep(b,A,B,folds):
    assert len(A)==len(B)==35
    heads=tail.heads_from_banks(A,B)
    indices={tuple(combine(head)):i for i,head in enumerate(heads)}
    seen=[]
    def scale(b,x,y,divide=False,k=K):
        if divide:
            i=indices[tuple(x)];seen.append(i)
            if i in folds:
                fm=folds[i][1];phase_zero(b,y,fm[0]);b.free(fm)
        return rr.raw.closed_scale24(b,x,y,divide,k)
    pivot=rr.clone(rr.raw.pivot,closed_scale24=scale)
    bodies=rr.clone(rr.raw.bodies,closed_scale24=scale)
    frames,_,_=frames_for(A,B);a0,d0,k0=frames[0]
    U0=combine(a0[:2]);W0=combine(d0[:2]);z=B[-1]
    qadic(b,A,B,k=k0);scale(b,U0,W0,True,k0)
    leaders=[b.alloc_qubits(12)for _ in range(3)];b.x(leaders[2][0])
    first,second,head=bodies(b,a0,d0,leaders,k0)
    first();erase_head(b,*heads[0],z,leaders);head(True);second()
    for j in range(1,len(frames)):
        a,d,k=frames[j]
        qframe(b,a,d,leaders,frames[j-1][2],True);qframe(b,a,d,leaders,k)
        pivot(b,a,d,leaders,k=k)
    assert seen==list(range(34)),seen
    return heads,leaders


def consume_live_tail(b,A,B,heads,leaders,pole,token,inverse):
    a1,r,q=leaders;u0,h0=heads[0];z=B[-1];u=A[-1]
    c=32;k=K^mul(c,c)^c
    cx(b,r,u,k);b.cx(r,a1)
    with b.mark('old_tail_inverse'):
        inverse(b,r,q,z,u,a1,pole,True,token)
    with b.mark('prefix_return'):
        tail.prefix(b,heads,r,q,z,True)
    with b.mark('head_and_tail_routing'):
        reclaim(b,[u0,h0]);b.cx(z,u0);b.cx(r,h0)
        b.cx(u0,z);b.cx(h0,r);b.x(q[0]);b.swap(z,a1)
        for reg in(a1,r,q):b.free(reg)
    return heads,[A[-1],B[-1]]


def consume_synthesis(b,A,B,pole,old_undo):
    cells=rr.closure(old_undo)
    assert {'hist','tt'}<=cells.keys()
    folds={row[0]:row[-1]for row in cells['hist']}
    assert set(folds)==set(range(1,34))
    with b.mark('outer_quadratic'):
        rr.outer_quadratic(b,A,B,True)
    with b.mark('raw_paired_sweep_live'):
        heads,leaders=live_sweep(b,A,B,folds)
    with b.mark('raw_tail_join_live'):
        heads,real=consume_live_tail(b,A,B,heads,leaders,pole,cells['tt'],old_undo.__globals__['tail_inplace'])
    with b.mark('old_head_characters'):
        for i,(hm,_)in sorted(folds.items()):
            b.cz(combine(heads[i]),hm);b.free(hm)
    return heads,real
