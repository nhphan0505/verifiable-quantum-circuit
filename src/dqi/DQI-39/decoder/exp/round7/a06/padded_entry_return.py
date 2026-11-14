"""Direct entry at the actual omitted-first-fold synthesis boundary.

The original numerator is already the residual after the first half-pivot.
The q0 multiplication, quotient extraction, and quotient update therefore
cancel. Enter that residual directly, reserve no value for its redundant
first head, and reconstruct that head from the matched original tail.
"""
import padded_rank_return as rank
import padded_return as prior
from raw_pair import frames_for,qframe,K,combine
from paired_coefficient import qadic

ROOT=prior.ROOT


def sweep(b,C,B,folds):
    assert len(C)==len(B)==35
    qadic(b,C,B,k=K)
    beta=b.alloc_qubits(12);b.x(beta[0])
    leaders=[C[-2],C[-1],beta]
    # Distinct free physical handles, disjoint from the retained leaders.
    H=b.alloc_qubits(24);h0=[H[:12],H[12:]];b.free(H)
    A=h0+list(C[:-2])
    heads=prior.rr.tail.heads_from_banks(A,B)
    frames,_,_=frames_for(A,B)
    for j,(a,d,k)in enumerate(frames):
        n=len(a);a1,a2,beta=leaders
        U=combine(a[:2]);W=combine(d[:2])
        if j:
            qframe(b,a,d,leaders,frames[j-1][2],True)
            qframe(b,a,d,leaders,k)
            prior.complete_zero(b,a+[a1,a2],a2,W,n+1,k,folds[2*j][1])
            prior.rr.raw.closed_scale24(b,U,W,True,k)
        first,second,_=rank.bodies(b,a,d,leaders,k)
        if j:first()
        source=combine(a[2:4])if n>3 else combine([a[-1],a1])
        prior.complete_zero(b,d+[beta],beta,source,n,k,folds[2*j+1][1])
        prior.rr.raw.closed_scale24(b,W,source,True,k)
        second()
    return A,heads,leaders


def consume_synthesis(b,C,B,pole,old_undo):
    cells=prior.rr.closure(old_undo)
    folds={row[0]:row[-1]for row in cells['hist']}
    assert set(folds)==set(range(1,34))
    with b.mark('direct_completed_sweep'):
        A,heads,leaders=sweep(b,C,B,folds)
    with b.mark('live_tail_join'):
        heads,real=prior.live.consume_live_tail(b,A,B,heads,leaders,pole,cells['tt'],old_undo.__globals__['tail_inplace'])
    with b.mark('old_head_characters'):
        for i,(hm,_)in sorted(folds.items()):
            b.cz(combine(heads[i]),hm);b.free(hm)
    return heads,real

route_words=prior.route_words
