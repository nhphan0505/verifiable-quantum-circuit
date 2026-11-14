"""Same raw CF permutation with polynomial carry fused into its products.

A linear-by-linear q-adic product has three outputs: two residue words
and one carry. Computing these jointly uses three GF4096 products (126 T)
instead of the99-T GF24 product plus a42-T carry product.
"""
from raw_pair import closed_scale24,K,ar,combine,cx,frames_for,qframe,leader_step


def product_with_carry(b,U,V,lo,hi,carry,k=K):
    u,h=U[:12],U[12:];v,s=V[:12],V[12:]
    # p=u*v is sent to lo and hi.
    b.cx(lo,hi);ar.mul_xor0(b,u,v,lo);b.cx(lo,hi)
    # r=h*s is sent to carry and k*r to lo.
    cx(b,carry,lo,k);ar.mul_xor0(b,h,s,carry);cx(b,carry,lo,k)
    # hi += (u+h)*(v+s). Together with p this is u*s+h*v+h*s.
    b.cx(h,u);b.cx(s,v);ar.mul_xor0(b,u,v,hi);b.cx(s,v);b.cx(h,u)


def pivot(b,A,B,leaders,reverse=False,k=K):
    n=len(A);m=(n-1)//2
    assert n==len(B) and n>=3 and n%2
    U=combine(A[:2]);W=combine(B[:2]);a1,a2,beta=leaders
    u,h=A[:2];w,s=B[:2];z=B[-1]
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
    def head(divide):
        source=combine(A[2:4])if m>1 else combine([A[-1],a1])
        closed_scale24(b,W,source,divide,k)
    if not reverse:
        closed_scale24(b,U,W,True,k);first();head(True);second()
    else:
        second();head(False);first();closed_scale24(b,U,W,False,k)
    return U,W,list(A[2:]),list(B[2:])


def sweep(b,A,B,reverse=False):
    frames,C,D=frames_for(A,B)
    leaders=[b.alloc_qubits(12)for _ in range(3)];b.x(leaders[2][0]);z=B[-1]
    if not reverse:
        qframe(b,A,B,leaders,frames[0][2])
        for j,(a,d,k)in enumerate(frames):
            pivot(b,a,d,leaders,k=k)
            if j+1<len(frames):
                qframe(b,a[2:],d[2:],leaders,k,True)
                qframe(b,a[2:],d[2:],leaders,frames[j+1][2])
        for a,d,k in reversed(frames):leader_step(b,combine(a[:2]),combine(d[:2]),z,leaders,True)
    else:
        for a,d,k in frames:leader_step(b,combine(a[:2]),combine(d[:2]),z,leaders)
        for j in reversed(range(len(frames))):
            a,d,k=frames[j];pivot(b,a,d,leaders,True,k)
            if j:
                qframe(b,a,d,leaders,k,True);qframe(b,a,d,leaders,frames[j-1][2])
        qframe(b,A,B,leaders,frames[0][2],True)
    b.x(leaders[2][0])
    for x in leaders:b.free(x)
    return [(a[:2],d[:2])for a,d,k in frames],C,D
