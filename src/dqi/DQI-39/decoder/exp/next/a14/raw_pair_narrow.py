"""Raw fused sweep with its first saved low head as a redundant cross product.

Keep d=a1*beta+a2*z in that first head while routing later heads. Its X-basis
erasure is repaid by two bilinear characters. Freeing this12-qubit word at
each scale hotspot reduces the live source width without a zero-beta branch.
The head and all three leaders are restored by the final accumulator return.
"""
from raw_pair_fused import product_with_carry
from raw_pair import closed_scale24,K,ar,combine,cx,frames_for,qframe,leader_first,leader_last,leader_step
from paired_coefficient import qadic
from exp.decoder.common import reclaim


def bodies(b,A,B,leaders,k=K):
    n=len(A);m=(n-1)//2;U=combine(A[:2]);W=combine(B[:2])
    a1,a2,beta=leaders;u,h=A[:2];w,s=B[:2];z=B[-1]
    def first():
        ar.mul_xor0(b,h,B[1],A[2])
        for i in range(1,m):
            product_with_carry(b,U,combine(B[2*i:2*i+2]),A[2*i],A[2*i+1],A[2*i+2],k)
        product_with_carry(b,U,combine([z,beta]),A[-1],a1,a2,k)
    def second():
        ar.mul_xor0(b,s,A[3]if m>1 else a1,B[2])
        for i in range(1,m):
            source=combine(A[2*i+2:2*i+4])if i<m-1 else combine([A[-1],a1])
            product_with_carry(b,W,source,B[2*i],B[2*i+1],B[2*i+2],k)
        ar.mul_xor0(b,w,a2,z);ar.mul_xor0(b,s,a2,beta)
    def second_head(divide):
        source=combine(A[2:4])if m>1 else combine([A[-1],a1])
        closed_scale24(b,W,source,divide,k)
    return first,second,second_head


def erase_cross(b,D,z,leaders):
    a1,a2,beta=leaders;mask=b.alloc_bits(12)
    b.hmr(D,mask);b.free(D)
    ar.phase_product(b,a1,beta,mask);ar.phase_product(b,a2,z,mask)
    b.free(mask)


def restore_cross(b,D,z,leaders):
    a1,a2,beta=leaders;reclaim(b,[D])
    ar.mul_xor0(b,a1,beta,D);ar.mul_xor0(b,a2,z,D)


def erase_first_head(b,D,h,z,a1):
    mask=b.alloc_bits(12);b.hmr(D,mask);b.free(D)
    b.cz(a1,mask);b.cz(h,mask);ar.phase_product(b,h,z,mask);b.free(mask)


def restore_first_head(b,D,h,z,a1):
    reclaim(b,[D]);b.cx(a1,D);b.cx(h,D);ar.mul_xor0(b,h,z,D)


def square_product(b,x,y,target):
    square=tuple(ar.square_columns(12));sqrt=tuple(ar.inverse_columns(square))
    ar.linear_inplace(b,y,square);ar.mul_xor0(b,x,y,target);ar.linear_inplace(b,y,sqrt)


def cross_first(b,U,beta,D):
    u,h=U[:12],U[12:];b.cx(h,u);square_product(b,u,beta,D);b.cx(h,u)


def cross_last(b,W,a2,D):square_product(b,W[:12],a2,D)


def sweep(b,A,B,reverse=False):
    assert len(A)==len(B)==35
    frames,C,E=frames_for(A,B);D=A[0];z=B[-1]
    a0,d0,k0=frames[0];U0=combine(a0[:2]);W0=combine(d0[:2]);h0=a0[1]
    if not reverse:
        # The first quotient needs no live virtual leader words.
        qadic(b,A,B,k=k0);closed_scale24(b,U0,W0,True,k0)
        leaders=[b.alloc_qubits(12)for _ in range(3)];b.x(leaders[2][0])
        a1,a2,beta=leaders
        first,second,head=bodies(b,a0,d0,leaders,k0)
        first()
        # At this boundary a1=u0+h0*z+h0 exactly, even at zero quotient sources.
        erase_first_head(b,D,h0,z,a1);head(True);second()
        restore_cross(b,D,z,leaders)
        for j in range(1,len(frames)):
            a,d,k=frames[j]
            qframe(b,a,d,leaders,frames[j-1][2],True);qframe(b,a,d,leaders,k)
            U=combine(a[:2]);W=combine(d[:2]);first,second,head=bodies(b,a,d,leaders,k)
            erase_cross(b,D,z,leaders);closed_scale24(b,U,W,True,k);restore_cross(b,D,z,leaders)
            first();cross_first(b,U,beta,D)
            erase_cross(b,D,z,leaders);head(True);restore_cross(b,D,z,leaders)
            second();cross_last(b,W,a2,D)
        for a,d,k in reversed(frames[1:]):
            U=combine(a[:2]);W=combine(d[:2])
            cross_last(b,W,a2,D);leader_last(b,W,z,leaders,True)
            cross_first(b,U,beta,D);leader_first(b,U,z,leaders,True)
        # d1=u0+h0+w0*h0². Restore the actual saved low head before using it.
        square_product(b,d0[0],h0,D);b.cx(h0,D)
        leader_step(b,U0,W0,z,leaders,True)
        b.x(beta[0])
        for x in leaders:b.free(x)
    else:
        leaders=[b.alloc_qubits(12)for _ in range(3)];b.x(leaders[2][0])
        a1,a2,beta=leaders
        leader_step(b,U0,W0,z,leaders)
        b.cx(h0,D);square_product(b,d0[0],h0,D)
        for a,d,k in frames[1:]:
            U=combine(a[:2]);W=combine(d[:2])
            leader_first(b,U,z,leaders);cross_first(b,U,beta,D)
            leader_last(b,W,z,leaders);cross_last(b,W,a2,D)
        for j in reversed(range(1,len(frames))):
            a,d,k=frames[j];U=combine(a[:2]);W=combine(d[:2]);first,second,head=bodies(b,a,d,leaders,k)
            second();cross_last(b,W,a2,D)
            erase_cross(b,D,z,leaders);head(False);restore_cross(b,D,z,leaders)
            first();cross_first(b,U,beta,D)
            erase_cross(b,D,z,leaders);closed_scale24(b,U,W,False,k);restore_cross(b,D,z,leaders)
            qframe(b,a,d,leaders,k,True);qframe(b,a,d,leaders,frames[j-1][2])
        first,second,head=bodies(b,a0,d0,leaders,k0)
        second();cross_last(b,W0,a2,D);b.cx(h0,D)
        erase_first_head(b,D,h0,z,a1);head(False);restore_first_head(b,D,h0,z,a1)
        first()
        b.x(beta[0])
        for x in leaders:b.free(x)
        closed_scale24(b,U0,W0,False,k0);qadic(b,A,B,True,k0)
    return [(a[:2],d[:2])for a,d,k in frames],C,E
