"""Direct completed coefficient sweep sharing the original inverse norms.

The original owner's fused divider consumes the old source-zero character
and the new coherent zero predicate. Its callback applies the quotient
body while retaining the norms, and preserves the source exactly.
"""
import padded_entry_return as entry
import padded_rank_return as rank
import padded_return as prior
from raw_pair import frames_for,qframe,K,combine
from paired_coefficient import qadic
from exp.arithmetic.division import zero_flag
from exp.partial_gauge.tail import controlled_linear_xor

ROOT=prior.ROOT


def complete_flag(b,target,lead,source,degree,k):
    F=zero_flag(b,source)
    controlled_linear_xor(b,F,lead,target,prior.constant_qadic(k,degree,len(target)))
    return F


def sweep(b,C,B,folds,divide):
    qadic(b,C,B,k=K)
    beta=b.alloc_qubits(12);b.x(beta[0]);leaders=[C[-2],C[-1],beta]
    H=b.alloc_qubits(24);h0=[H[:12],H[12:]];b.free(H)
    A=h0+list(C[:-2]);heads=prior.rr.tail.heads_from_banks(A,B)
    frames,_,_=frames_for(A,B)
    for j,(a,d,k)in enumerate(frames):
        n=len(a);a1,a2,beta=leaders
        U=combine(a[:2]);W=combine(d[:2])
        first,second,_=rank.bodies(b,a,d,leaders,k)
        if j:
            qframe(b,a,d,leaders,frames[j-1][2],True)
            qframe(b,a,d,leaders,k)
            F=complete_flag(b,a+[a1,a2],a2,W,n+1,k)
            divide(b,U,W,F,folds[2*j][1],first,K=k)
        source=combine(a[2:4])if n>3 else combine([a[-1],a1])
        F=complete_flag(b,d+[beta],beta,source,n,k)
        divide(b,W,source,F,folds[2*j+1][1],second,K=k)
    return A,heads,leaders


def consume_synthesis(b,C,B,pole,old_undo):
    cells=prior.rr.closure(old_undo)
    folds={row[0]:row[-1]for row in cells['hist']}
    owner=old_undo.__globals__['folds']
    divide=owner.ug['absorb'].__globals__['divide_fused']
    with b.mark('direct_fused_sweep'):
        A,heads,leaders=sweep(b,C,B,folds,divide)
    with b.mark('live_tail_join'):
        heads,real=prior.live.consume_live_tail(b,A,B,heads,leaders,pole,cells['tt'],old_undo.__globals__['tail_inplace'])
    with b.mark('old_head_characters'):
        for i,(hm,_)in sorted(folds.items()):
            b.cz(combine(heads[i]),hm);b.free(hm)
    return heads,real

route_words=prior.route_words
