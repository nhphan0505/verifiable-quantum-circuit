"""GF64 thickening tensor planner, adapted unchanged from the supplied Hankel planner."""
from pathlib import Path
from functools import lru_cache
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'playbook/kit'), str(ROOT/'playbook/kit/decoder'), str(ROOT/'playbook/kit/decoder/exp/convert')]
from exp.arithmetic import field as ar
from exp.convert import kernels
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
