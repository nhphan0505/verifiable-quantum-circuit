"""Retire both words of the first U head while its virtual leaders hold it.

After the first half-pivot h0=a2 and u0=a1+h0*z+h0 on every input. The two
HMR signs are linear/bilinear. Both words stay free through all remaining
pivots and are recreated for42 T before reversing the first half-pivot.
"""
from raw_pair_fused import pivot
from raw_pair_narrow import bodies,erase_first_head
from raw_pair import closed_scale24,combine,frames_for,qframe,leader_first,leader_last,leader_step,ar
from paired_coefficient import qadic
from exp.decoder.common import reclaim


def erase_head(b,u,h,z,leaders):
    a1,a2,beta=leaders
    erase_first_head(b,u,h,z,a1)
    mask=b.alloc_bits(12);b.hmr(h,mask);b.free(h);b.cz(a2,mask);b.free(mask)


def restore_head(b,u,h,z,leaders):
    a1,a2,beta=leaders;reclaim(b,[u,h])
    b.cx(a2,h);b.cx(a1,u);b.cx(h,u);ar.mul_xor0(b,h,z,u)


def sweep(b,A,B,reverse=False):
    assert len(A)==len(B)==35
    frames,C,E=frames_for(A,B);u0,h0=A[:2];z=B[-1]
    a0,d0,k0=frames[0];U0=combine(a0[:2]);W0=combine(d0[:2])
    if not reverse:
        qadic(b,A,B,k=k0);closed_scale24(b,U0,W0,True,k0)
        leaders=[b.alloc_qubits(12)for _ in range(3)];b.x(leaders[2][0])
        a1,a2,beta=leaders;first,second,head=bodies(b,a0,d0,leaders,k0)
        first();erase_head(b,u0,h0,z,leaders);head(True);second()
        for j in range(1,len(frames)):
            a,d,k=frames[j]
            qframe(b,a,d,leaders,frames[j-1][2],True);qframe(b,a,d,leaders,k)
            pivot(b,a,d,leaders,k=k)
        for a,d,k in reversed(frames[1:]):
            leader_step(b,combine(a[:2]),combine(d[:2]),z,leaders,True)
        leader_last(b,W0,z,leaders,True);restore_head(b,u0,h0,z,leaders)
        leader_first(b,U0,z,leaders,True)
        b.x(beta[0])
        for x in leaders:b.free(x)
    else:
        leaders=[b.alloc_qubits(12)for _ in range(3)];b.x(leaders[2][0])
        a1,a2,beta=leaders
        leader_first(b,U0,z,leaders);erase_head(b,u0,h0,z,leaders);leader_last(b,W0,z,leaders)
        for a,d,k in frames[1:]:
            leader_step(b,combine(a[:2]),combine(d[:2]),z,leaders)
        for j in reversed(range(1,len(frames))):
            a,d,k=frames[j];pivot(b,a,d,leaders,True,k)
            qframe(b,a,d,leaders,k,True);qframe(b,a,d,leaders,frames[j-1][2])
        first,second,head=bodies(b,a0,d0,leaders,k0)
        second();head(False);restore_head(b,u0,h0,z,leaders);first()
        b.x(beta[0])
        for x in leaders:b.free(x)
        closed_scale24(b,U0,W0,False,k0);qadic(b,A,B,True,k0)
    return [(a[:2],d[:2])for a,d,k in frames],C,E
