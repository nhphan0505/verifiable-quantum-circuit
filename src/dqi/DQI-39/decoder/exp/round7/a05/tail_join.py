"""Raw fraction-free tail -> original extracted real jet.

The original tail inverse consumes its real forward transcript.  The first
U head is temporarily redundant in the leader frame and is measured in X;
both resulting signs are repaid immediately.  Its coordinates are restored
by the original scalar-prefix return, so no virtual leader survives.

This completes the tail interface on matching raw/extracted-head charts.
It does not assert agreement of the preceding raw sweep on common-q gaps.
"""
from pathlib import Path
import sys
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(ROOT/'exp/next/a14'),str(ROOT/'playbook/kit'),
             str(ROOT/'playbook/kit/decoder')]
from raw_pair import ar,combine,cx,K,mul,leader_first,leader_last,leader_step
from raw_pair_head24_erased import erase_head
from exp.decoder.common import reclaim


def heads_from_banks(A,B):
    heads=[]
    for j in range(17):heads.extend((list(A[2*j:2*j+2]),list(B[2*j:2*j+2])))
    return heads


def add_tail(b,head,source,target,odd):
    """Exact modified-prefix accumulator term, 42 T, no retained debt."""
    a,h=head
    if odd:b.cx(h,a)
    sq=tuple(ar.square_columns(12));back=tuple(ar.inverse_columns(sq))
    ar.linear_inplace(b,source,sq)
    ar.mul_xor0(b,a,source,target)
    ar.linear_inplace(b,source,back)
    if odd:b.cx(h,a)


def prefix(b,heads,r,q,d,reverse=False):
    indices=reversed(range(1,34)) if reverse else range(1,34)
    for i in indices:
        source,target=(r,q) if i%2 else(q,r)
        if reverse:add_tail(b,heads[i],source,d,bool(i%2))
        ar.mul_xor0(b,heads[i][1],source,target)
        if not reverse:add_tail(b,heads[i],source,d,bool(i%2))


def consume(b,A,B,pole,tail_token,tail_inverse):
    """Consume original tail token and overwrite raw tail by its old real jet.

    Returned heads use A[2j:2j+2], B[2j:2j+2]; the real jet uses A[-1],B[-1].
    The caller still owns old fold and external-extraction transcripts.
    """
    assert len(A)==len(B)==35
    heads=heads_from_banks(A,B);u0,h0=heads[0]
    a1,r,q=[b.alloc_qubits(12)for _ in range(3)];b.x(q[0])
    leaders=[a1,r,q];z=B[-1];u=A[-1]
    with b.mark('leader_inflation'):
        leader_first(b,combine(heads[0]),z,leaders)
        erase_head(b,u0,h0,z,leaders)
        leader_last(b,combine(heads[1]),z,leaders)
        for j in range(1,17):
            leader_step(b,combine(heads[2*j]),combine(heads[2*j+1]),z,leaders)
    c=32;k=K^mul(c,c)^c
    cx(b,r,u,k);b.cx(r,a1)
    with b.mark('old_tail_inverse'):
        tail_inverse(b,r,q,z,u,a1,pole,True,tail_token)
    with b.mark('prefix_return'):
        prefix(b,heads,r,q,z,True)
    with b.mark('head_and_tail_routing'):
        reclaim(b,[u0,h0]);b.cx(z,u0);b.cx(r,h0)
        b.cx(u0,z);b.cx(h0,r);b.x(q[0])
        b.swap(z,a1)
        for reg in(a1,r,q):b.free(reg)
    return heads,[A[-1],B[-1]]


def prepare_fixture(b,A,B,pole,tail_forward):
    """Audit-only exact opposite boundary with a genuine original transcript.

    This uses a wider fixture schedule; it is not the proposed whole entry.
    """
    heads=heads_from_banks(A,B);u,v=A[-1],B[-1]
    r,q,z=[b.alloc_qubits(12)for _ in range(3)]
    b.cx(heads[0][1],r);b.x(q[0]);b.cx(heads[0][0],z)
    prefix(b,heads,r,q,z)
    token=tail_forward(b,r,q,z,u,v,pole)
    c=32;k=K^mul(c,c)^c
    cx(b,r,u,k);b.cx(r,v)
    leaders=[v,r,q]
    for j in reversed(range(17)):
        leader_step(b,combine(heads[2*j]),combine(heads[2*j+1]),z,leaders,True)
    b.x(q[0]);b.swap(v,z)
    for reg in(r,q,z):b.free(reg)
    return token
