"""Exact two-copy Hankel schedule with a frozen public partition.

Standalone installer: imports only A01's port and immutable kit arithmetic.
It retains the top dot and changes only the forward Hankel map. Every
selected public bilinear tensor is verified during construction.
"""
from pathlib import Path
from functools import lru_cache
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'research/agents/a01'))
import ported as p
ar,kernels=p.ar,p.k


def product(a,b,f):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]^=f.mul(x,y)
    return out

def remainder(a,mod,f):
    out=list(a)
    for i in range(len(out)-len(mod),-1,-1):
        c=out[i+len(mod)-1]
        for j,v in enumerate(mod):out[i+j]^=f.mul(c,v)
    return (out+[0]*(len(mod)-1))[:len(mod)-1]

def evaluate(a,x,f):
    out=0
    for c in reversed(a):out=f.mul(out,x)^c
    return out

def pack(a):return sum(c<<(6*i) for i,c in enumerate(a))

def unpack(x,n):return [(x>>(6*i))&63 for i in range(n)]

@lru_cache(None)
def thickening(k):
    f,sub=ar.field(12),ar.field(6)
    generator=f.pow(f.primitive_element,65)
    def binary_eval(poly,x):
        out=0
        for i in reversed(range(7)):out=f.mul(out,x)^((poly>>i)&1)
        return out
    root=next(f.pow(generator,i) for i in range(1,64)
              if binary_eval(sub.modulus,f.pow(generator,i))==0)
    embed=[f.pow(root,i) for i in range(6)]
    alpha=f.primitive_element
    to=ar.inverse_columns(embed+[f.mul(v,alpha) for v in embed])
    minimal=unpack(ar.apply(to,f.square(alpha)),2)+[1]
    mod=[1]
    for _ in range(k):mod=product(mod,minimal,sub)
    theta=[0,1]
    for _ in range(12):theta=remainder(product(theta,theta,sub),mod,sub)
    epsilon=list(theta);epsilon[1]^=1
    epowers=[[1]]
    for _ in range(k):epowers.append(remainder(product(epowers[-1],epsilon,sub),mod,sub))
    assert not any(epowers[k])
    unit=[0]*(k+1);other=[0]*(k+1)
    for j in range(k+1):
        if (j&k)==j:other[j],unit[j]=unpack(ar.apply(to,f.pow(alpha,k-j)),2)
    assert any(remainder(unit,minimal,sub))
    assert remainder(product(theta,unit,sub),mod,sub)==remainder(other,mod,sub)
    columns=[]
    for degree in range(k):
        for bit in range(12):
            c0,c1=unpack(to[bit],2)
            value=[sub.mul(c1,a) for a in theta];value[0]^=c0
            columns.append(pack(remainder(product(value,epowers[degree],sub),mod,sub)))
    weighted=[pack(remainder(product(unpack(v,2*k),unit,sub),mod,sub)) for v in columns]
    double=[pack(remainder(product(unpack(v,2*k),unit,sub),mod,sub)) for v in weighted]
    return mod,tuple(weighted),tuple(ar.inverse_columns(double))

@lru_cache(None)
def two_sided(k,nx,ny):
    assert 1<=nx<=k and 1<=ny<=k
    sub=ar.field(6)
    mod,weighted,decode=thickening(k)
    left=weighted[:12*nx];right=weighted[:12*ny]
    ld=max((v.bit_length()-1)//6 for v in left if v)
    rd=max((v.bit_length()-1)//6 for v in right if v)
    points=range(ld+rd+1)
    assert len(points)<=64
    terms=[]
    for point in points:
        lag,den=[1],1
        for other in points:
            if other==point:continue
            lag=product(lag,[other,1],sub);den=sub.mul(den,point^other)
        lag=[sub.mul(a,sub.invert(den)) for a in lag]
        lv=[evaluate(unpack(v,2*k),point,sub) for v in left]
        rv=[evaluate(unpack(v,2*k),point,sub) for v in right]
        for mask,vector in ar.tensor(6):
            a=sum(((v&mask).bit_count()&1)<<i for i,v in enumerate(lv))
            b=sum(((v&mask).bit_count()&1)<<i for i,v in enumerate(rv))
            out=ar.apply(decode,pack(remainder([sub.mul(v,vector) for v in lag],mod,sub)))
            if a and b and out:terms.append((a,b,out))
    merged={}
    for a,b,out in terms:merged[a,b]=merged.get((a,b),0)^out
    result=tuple((a,b,out) for (a,b),out in merged.items() if out)
    return result

@lru_cache(None)
def trace_pairing():
    f=ar.field(12)
    def trace(x):
        y=x;out=0
        for _ in range(12):out^=y;y=f.square(y)
        assert out in (0,1)
        return out
    columns=tuple(sum(trace(f.mul(1<<i,1<<j))<<i for i in range(12)) for j in range(12))
    return columns,tuple(ar.inverse_columns(columns))

def reverse_transform(value,words,columns):
    return sum(ar.apply(columns,(value>>(12*i))&4095)<<(12*(words-1-i)) for i in range(words))

def verify_middle(terms,k,sources,prefix):
    f=ar.field(12)
    for i in range(12*sources):
        result=[0]*(12*k)
        for a,b,out in terms:
            if not ((a>>i)&1):continue
            for j in ar.bits(b):result[j]^=out
        for j,value in enumerate(result):
            degree=i//12+j//12
            expected=(f.mul(1<<(i%12),1<<(j%12))<<(12*(degree-prefix+1))
                      if prefix-1<=degree<k else 0)
            assert value==expected,(k,sources,prefix,i,j,value,expected)
    return True

@lru_cache(None)
def middle_tensor(k,sources,overlap=2):
    prefix=sources-overlap
    outputs=k-prefix+1
    assert prefix>=1 and 1<=outputs<=k
    paired,unpaired=trace_pairing()
    terms=[]
    for a,b,out in two_sided(k,sources,outputs):
        terms.append((a,reverse_transform(out,k,paired),reverse_transform(b,outputs,unpaired)))
    merged={}
    for a,b,out in terms:merged[a,b]=merged.get((a,b),0)^out
    result=tuple((a,b,out) for (a,b),out in merged.items() if a and b and out)
    verify_middle(result,k,sources,prefix)
    return result

class NativeMiddle:
    def __init__(self,k,sources,overlap):
        self.k,self.sources=k,sources
        self.prefix=sources-overlap
        self.outputs=k-self.prefix+1
        N=sources+self.outputs-1
        V,W=kernels.vandermonde(N)
        self.terms=tuple((tuple(V[t][:sources]),
                         tuple(W[k-1-j][t] for j in range(k)),
                         tuple(V[t][self.outputs-1-j] for j in range(self.outputs)))
                        for t in range(N))
        self.terms=tuple((a,b,c) for a,b,c in self.terms if any(a) and any(b) and any(c))
        self.verify()

    def verify(self):
        f=ar.field(12)
        for i in range(self.sources):
            for j in range(self.k):
                out=[0]*self.outputs
                for a,b,c in self.terms:
                    ab=f.mul(a[i],b[j])
                    for l,v in enumerate(c):out[l]^=f.mul(ab,v)
                expected=[int(i+j==self.prefix-1+l) for l in range(self.outputs)]
                assert out==expected,(self.k,self.sources,i,j,out,expected)
        return True

    def __len__(self):
        return 42*len(self.terms)

@lru_cache(None)
def hybrid_tensor(k,sources,overlap=2):
    if k<=17:
        return middle_tensor(k,sources,overlap)
    return NativeMiddle(k,sources,overlap)

def accumulate_binary(b,x,q,out,terms):
    assert len(set(map(str,x+q+out)))==len(x)+len(q)+len(out)
    for am,bm,vector in terms:
        ix,iy,iz=[list(ar.bits(v)) for v in (am,bm,vector)]
        a,c,t=ix[0],iy[0],iz[0]
        for i in ix[1:]: b.cx(x[i],x[a])
        for i in iy[1:]: b.cx(q[i],q[c])
        for i in iz[1:]: b.cx(out[t],out[i])
        b.ccx(x[a],q[c],out[t])
        for i in reversed(iz[1:]): b.cx(out[t],out[i])
        for i in reversed(iy[1:]): b.cx(q[i],q[c])
        for i in reversed(ix[1:]): b.cx(x[i],x[a])

def accumulate(b,x,q,out,terms):
    if not isinstance(terms,NativeMiddle):
        return accumulate_binary(b,x,q,out,terms)
    assert len(set(map(str,x+q+out)))==len(x)+len(q)+len(out)
    words=lambda bits:[bits[i:i+12] for i in range(0,len(bits),12)]
    aw,bw,tw=map(words,(x,q,out))
    for ac,bc,tc in terms.terms:
        p.dk.rank_update(b,aw,ac,bw,bc,tw,tc)

def retire_descending(b,q,x,old_sources,copies,prefix):
    for index in reversed(range(prefix,len(old_sources))):
        copied=copies[index-prefix]
        mask=b.alloc_bits(12)
        b.hmr(copied,mask);b.free(copied)
        b.cz(x[index],mask)
        for j in range(index):
            ar.phase_product(b,q[index-j-1],old_sources[j],mask)
        b.free(mask)

flat=lambda words:[bit for word in words for bit in word]
PLANS={1:('empty',),2:('small',),4:('small',),6:('leaf',4),
       10:('leaf',6),14:('leaf',8),18:('leaf',8),34:('leaf',16)}


def install(cv):
    cells=dict(zip(cv.__code__.co_freevars,cv.__closure__))
    scope=cells['core'].cell_contents.__globals__
    maximum,max_sources,overlap,force_sources=34,18,2,None

    @lru_cache(None)
    def partition(n):
        assert maximum==34 and max_sources==18 and overlap==2 and force_sources is None
        return 0,PLANS[n]

    def tri(b,q,x,reverse=False):
        assert not reverse
        _,plan=partition(len(x))
        if plan[0]=='empty':return
        if plan[0]=='small':
            if len(x)==2:return ar.mul_xor0(b,q[0],x[0],x[1])
            return p.hankel_direct(b,q,x)
        assert plan[0]=='leaf'
        sources=plan[1];prefix=sources-overlap
        tri(b,q[:len(x)-sources-1],x[sources:])
        copies=[b.alloc_qubits(12) for _ in range(overlap)]
        for source,target in zip(x[prefix:sources],copies):b.cx(source,target)
        old_sources=x[:prefix]+copies
        accumulate(b,flat(old_sources),flat(q[:len(x)-1]),flat(x[prefix:]),
                   hybrid_tensor(len(x)-1,sources,overlap))
        retire_descending(b,q,x,old_sources,copies,prefix)
        tri(b,q[:prefix-1],x[:prefix])

    def hankel(b,B,A,reverse=False):
        if reverse:return p.hankel(b,B,A,True)
        return p.clone(kernels.hankel,dict(vars(kernels),tri=tri))(b,B,A)
    scope['old'].hankel=hankel
    return cv
