"""Coherent product tensors after singular, classically known source maps.

The rank reduction is an exact binary matrix factorization in groups with
one common first-input linear form. No simulator or input-specific branch.
"""
from functools import lru_cache
from profile_fusion import ar,emul,mul,inv,K,transpose,tensor99_extension

MASK=(1<<24)-1
def epow(x,n):
    z=1
    while n:
        if n&1:z=emul(z,x)
        x=emul(x,x);n>>=1
    return z
def einv(x):return epow(x,(1<<24)-2) if x else 0
def esqrt(x):return epow(x,1<<23)
def ebar(x):return x^(x>>12)
def etrace(x):return x>>12
def phi(x,c):return esqrt(emul(c,x)^etrace(x))
def k_inv(x,c):
    ci=inv(c)
    return emul(ci,x)^mul(mul(ci,ci),etrace(x))

@lru_cache(None)
def trace_gram():
    def trace(x):
        z=x;y=x
        for _ in range(23):y=emul(y,y);z^=y
        assert z in (0,1)
        return z
    cols=tuple(sum(trace(emul(1<<i,1<<j))<<j for j in range(24)) for i in range(24))
    return cols,tuple(ar.inverse_columns(cols))

def dual(mask):return ar.apply(trace_gram()[1],mask)

def regroup(terms):
    groups={}
    for a,b,v in terms:
        if not a or not b or not v:continue
        matrix=groups.setdefault(a,[0]*24)
        for j in ar.bits(b):matrix[j]^=v
    out=[]
    for a,columns in groups.items():
        basis={};coordinates=[];vectors=[]
        for v in columns:
            x=v;coordinate=0
            while x:
                p=x.bit_length()-1
                if p in basis:
                    value,tag=basis[p];x^=value;coordinate^=tag
                else:
                    tag=1<<len(vectors);basis[p]=(x,tag);vectors.append(x)
                    coordinate^=tag;break
            coordinates.append(coordinate)
        for k,v in enumerate(vectors):
            b=sum(((j>>k)&1)<<i for i,j in enumerate(coordinates))
            assert b
            out.append((a,b,v))
    return tuple(out)

@lru_cache(None)
def projected(c,lam,rho=1):
    # Product (H + lam*phi(H,c))*D. Opposite scalar source gauges
    # preserve the product and can change the available rank reduction.
    ri=einv(rho)
    acols=tuple(emul(rho,(1<<i)^emul(lam,phi(1<<i,c))) for i in range(24))
    bcols=tuple(emul(ri,1<<i) for i in range(24))
    raw=[(transpose(m,acols),transpose(m,bcols),v) for m,v in tensor99_extension(K)]
    return regroup(raw)

def candidates(c,rho=1):
    result={}
    for m,v in tensor99_extension(K):
        t=emul(dual(m),rho)
        if c:
            lam=emul(esqrt(k_inv(t,c)),einv(t))
        else:
            if etrace(t):continue
            # phi*(z)=Tr(z)^2. Choose Tr(z)=sqrt(t).
            z=esqrt(t)<<12
            lam=emul(z,einv(t))
        result[lam]=min(result.get(lam,99),len(projected(c,lam,rho)))
    return sorted((rank,lam) for lam,rank in result.items())

def verify(c,lam,rho=1):
    t=projected(c,lam,rho)
    for i in range(24):
        a=(1<<i)^emul(lam,phi(1<<i,c))
        for j in range(24):
            v=0
            for x,y,z in t:
                if ((x>>i)&1) and ((y>>j)&1):v^=z
            assert v==emul(a,1<<j),(c,lam,rho,i,j,v,emul(a,1<<j))
    return True

if __name__=='__main__':
    import json
    from pathlib import Path
    records=[]
    for c in [0,1,inv(6),inv(20),inv(30),inv(72)]:
        rhos=[1] if c else [1,einv(dual(tensor99_extension(K)[0][0]))]
        for rho in rhos:
            choices=candidates(c,rho)
            print('choices',c,rho,choices[:10],flush=True)
            for rank,lam in choices[:2]:verify(c,lam,rho)
            records.append(dict(c=c,rho=rho,best=choices[:2],all=choices))
    (Path(__file__).parent/'defect_candidates.json').write_text(json.dumps(records,indent=2)+'\n')
