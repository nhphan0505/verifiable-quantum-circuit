"""Source-preserving completed degree-two Hermite denominator pivot.

u holds R(beta), B holds the degree-two monic denominator evaluated at beta.
For the nonsingular chart, replace B by R'(beta), preserving u.  For rank
one, the canonical common factor x+hc gives the same derivative; its other
padding coordinates map to the otherwise missing norm-one circle values.
For u=0 the completed map is inverse0(B), so the canonical B=q maps to zero.
Every basis input has an exact inverse.  This is a local component, not the
complete 35-node direct return.  No original decoder or engine is modified.
"""
from schur_scalar import inverse_apply,scale,zero_toggle,ar
from universal_rank_completion import closed_inverse

K=2048


def masked_product(b,F,a,x,z):
    temp=b.alloc_qubits(12)
    for i in range(12):b.init_and(F,a[i],temp[i])
    ar.mul_xor0(b,temp,x,z)
    m=b.alloc_bits(12);b.hmr(temp,m);b.free(temp)
    for i in range(12):b.ccz(F,a[i],m[i])
    b.free(m)


def norm_source(b,r,F):
    """N=1+F*(r²+r+K+1), nonzero on both coherent charts."""
    n=b.alloc_qubits(12);b.x(n[0]);tmp=b.alloc_qubits(1)[0]
    f=ar.field(12)
    for i in range(12):
        b.init_and(F,r[i],tmp)
        for j in ar.bits(f.square(1<<i)^(1<<i)):b.cx(tmp,n[j])
        b.del_and(F,r[i],tmp)
    for j in ar.bits(K^1):b.cx(F,n[j])
    b.free(tmp)
    return n


def retire_norm(b,r,F,n):
    m=b.alloc_bits(12);b.hmr(n,m);b.free(n);b.z(m[0])
    f=ar.field(12)
    for i in range(12):
        for j in ar.bits(f.square(1<<i)^(1<<i)):b.ccz(F,r[i],m[j])
    for j in ar.bits(K^1):b.cz(F,m[j])
    b.free(m)


def add_rplus(b,F,r,x,z,one=False,square=False):
    if square:ar.linear_inplace(b,r,ar.square_columns(12))
    c=(K if square else 0)^(1 if one else 0)
    for i in ar.bits(c):b.x(r[i])
    masked_product(b,F,r,x,z)
    for i in ar.bits(c):b.x(r[i])
    if square:ar.linear_inplace(b,r,ar.inverse_columns(ar.square_columns(12)))


def matrix_bar(b,y,r,F,reverse=False):
    """Multiply/divide by bar(v)=r+1+beta on F, identity otherwise."""
    x,z=y[:12],y[12:]
    def first():add_rplus(b,F,r,z,x)
    def last():add_rplus(b,F,r,x,z,one=True)
    def middle():
        n=norm_source(b,r,F)
        inverse_apply(b,n,lambda ni:scale(b,z,n,ni,reverse))
        retire_norm(b,r,F,n)
    if not reverse:first();middle();last();b.cswap(F,x,z)
    else:b.cswap(F,x,z);last();middle();first()


def ratio(b,y,r,F,reverse=False):
    """Multiply/divide by v/bar(v), identity on F=0, at no extra bank."""
    x,z=y[:12],y[12:]
    def first():add_rplus(b,F,r,z,x,one=True,square=True)
    def last():add_rplus(b,F,r,x,z,square=True)
    def middle():
        n=norm_source(b,r,F)
        def action(ni):
            scale(b,x,n,ni,not reverse)
            scale(b,z,n,ni,reverse)
        inverse_apply(b,n,action)
        retire_norm(b,r,F,n)
    if not reverse:first();middle();last();b.cswap(F,x,z)
    else:b.cswap(F,x,z);last();middle();first()


def point_swap(b,y,F,hc=0):
    pivot=y[12]
    for j in ar.bits(hc):b.cx(pivot,y[j])
    rest=list(y[:12])+list(y[13:]);Z=b.alloc_qubits(1)[0]
    zero_toggle(b,rest,Z);b.ccx(F,Z,pivot);zero_toggle(b,rest,Z);b.free(Z)
    for j in ar.bits(hc):b.cx(pivot,y[j])


def high_swap(b,t,F):
    Z=b.alloc_qubits(1)[0]
    zero_toggle(b,t[1:],Z);b.ccx(F,Z,t[0]);zero_toggle(b,t[1:],Z);b.free(Z)


def conditional_T(b,y,F):
    s,t=y[:12],y[12:]
    high_swap(b,t,F)
    closed_inverse(b,t)
    inverse_apply(b,t,lambda ti:scale(b,s,t,ti,False))
    b.cx(F,t[0])
    inverse_apply(b,t,lambda ti:scale(b,s,t,ti,True))
    closed_inverse(b,t)


def normalized_completion(b,y,F,reverse=False,hc=0):
    if not reverse:
        point_swap(b,y,F,hc);conditional_T(b,y,F);closed_inverse(b,y);b.cx(F,y[0])
    else:
        b.cx(F,y[0]);closed_inverse(b,y);conditional_T(b,y,F);point_swap(b,y,F,hc)


def completed_pair(b,u,B,reverse=False,hc=0):
    """Overwrite B with its completed derivative coordinate; preserve u."""
    assert len(u)==len(B)==24
    r,g=u[:12],u[12:]
    Z=b.alloc_qubits(1)[0];zero_toggle(b,g,Z);b.cswap(Z,r,g)
    inverse_apply(b,g,lambda gi:scale(b,r,g,gi,True))
    # F=1 exactly when the original imaginary component is nonzero.
    b.x(Z);F=Z
    def scalar():
        def action(gi):
            scale(b,B[:12],g,gi,reverse)
            scale(b,B[12:],g,gi,reverse)
        inverse_apply(b,g,action)
    if not reverse:
        matrix_bar(b,B,r,F,True)
        normalized_completion(b,B,F,hc=hc)
        ratio(b,B,r,F)
        scalar()
    else:
        scalar()
        ratio(b,B,r,F,True)
        normalized_completion(b,B,F,True,hc)
        matrix_bar(b,B,r,F)
    b.x(Z)
    inverse_apply(b,g,lambda gi:scale(b,r,g,gi,False))
    b.cswap(Z,r,g);zero_toggle(b,g,Z);b.free(Z)
