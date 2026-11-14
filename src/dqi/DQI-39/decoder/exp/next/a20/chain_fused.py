"""Exact coherent derivative/product pair in a rank-deficient output frame.

The ordinary99-term multiplication tensor is restricted to an explicitly
singular source map. This removes at least one rank-one gate per product,
without a source or output register allocation and without measurements.
"""
from functools import lru_cache
from defect_tensor import (ar,emul,einv,esqrt,phi,dual,transpose,
                           tensor99_extension,K,projected,candidates,regroup)

@lru_cache(None)
def square_columns(inverse=False):
    return tuple(esqrt(1<<i) if inverse else emul(1<<i,1<<i) for i in range(24))

@lru_cache(None)
def constant_columns(c):return tuple(emul(c,1<<i) for i in range(24))

def add_constant(b,source,target,c):
    if c:ar.linear_xor(b,source,target,constant_columns(c))

def scale_constant(b,source,c):
    assert c
    if c!=1:ar.linear_inplace(b,source,constant_columns(c))

def tensor_accumulate(b,H,D,target,terms):
    for a,d,v in terms:
        ix=list(ar.bits(a));iy=list(ar.bits(d));iz=list(ar.bits(v))
        x=ix[0];y=iy[0];z=iz[0]
        for i in ix[1:]:b.cx(H[i],H[x])
        for i in iy[1:]:b.cx(D[i],D[y])
        for i in iz[1:]:b.cx(target[z],target[i])
        b.ccx(H[x],D[y],target[z])
        for i in reversed(iz[1:]):b.cx(target[z],target[i])
        for i in reversed(iy[1:]):b.cx(D[i],D[y])
        for i in reversed(ix[1:]):b.cx(H[i],H[x])

@lru_cache(None)
def subfield_phi_terms():
    cols=tuple(phi(1<<i,0) for i in range(24))
    out=[]
    for shift in (0,12):
        for m,v in ar.tensor(12):out.append((transpose(m,cols),m<<shift,v<<shift))
    return regroup(out)

@lru_cache(None)
def schedule(c):
    if c==0:
        rho=einv(dual(tensor99_extension(K)[0][0]))
        rank,lam=candidates(0,rho)[0]
        u=projected(0,lam,rho);v=subfield_phi_terms()
        assert len(u)+len(v)<=182
        return lam,None,u,v
    (rank,lam),(rank2,mu)=candidates(c)[:2]
    assert lam!=mu
    u=projected(c,lam);v=projected(c,mu)
    assert len(u)+len(v)<=196
    return lam,mu,u,v

def products(b,H,D,N,L,c):
    """N^=H*D; L^=(c*H+Tr(H))*D². All targets may be dirty."""
    lam,mu,u,v=schedule(c)
    ar.linear_inplace(b,L,square_columns(True))
    add_constant(b,L,N,lam)
    if mu is not None:
        scale_constant(b,L,lam^mu);b.cx(N,L)
    tensor_accumulate(b,H,D,N,u)
    tensor_accumulate(b,H,D,L,v)
    if mu is not None:
        b.cx(N,L);scale_constant(b,L,einv(lam^mu))
    add_constant(b,L,N,lam)
    ar.linear_inplace(b,L,square_columns(False))

def external_chain_step(b,head,N,D,L,q,ct,c,reverse=False,first=False):
    if reverse:
        scalepair(b,N,inv(q));b.swap(N,D);scalepair(b,L,inv(q))
    if first and not reverse:
        b.cx(head[1],L[:12]);scalepair(b,L,q)
        a,h=head;cx(b,h,a,ct);b.cx(combine(head),N);cx(b,h,a,ct)
        b.swap(N,D);scalepair(b,N,q)
        return
    a,h=head;cx(b,h,a,ct)
    chain_products(b,combine(head),D,N,L,c)
    cx(b,h,a,ct)
    if not reverse:
        scalepair(b,L,q);b.swap(N,D);scalepair(b,N,q)

def install(entry):
    import walk_bound
    edits=[]
    for fn in walk_bound.functions(entry):
        if fn.__name__!='external_chain_step':continue
        if 'external_corrected_product' not in fn.__code__.co_names:continue
        assert fn.__closure__ is None
        fn.__globals__['chain_products']=products
        edits.append((fn.__code__.co_filename,fn.__code__.co_firstlineno))
        fn.__code__=external_chain_step.__code__
    assert edits,'Actual homogeneous chain owner not found'
    return edits
