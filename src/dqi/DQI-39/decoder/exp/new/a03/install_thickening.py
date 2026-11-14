"""Reusable exact converter tensor installer; no base import or circuit build.

The helpers are source-identical to the accepted a03_thickening whole decoder.
Use install(cv) on the actual completed converter, then check the whole decoder.
"""
from pathlib import Path
from types import FunctionType, CodeType, ModuleType, SimpleNamespace
from functools import lru_cache
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(Path(__file__).resolve().parent), str(ROOT/'research/agents/a01')]
import tensor64 as h
from rebind_graph import private_rebind
ar=h.ar
COUNTS={}

def names(code):
    result=set(code.co_names)
    for item in code.co_consts:
        if isinstance(item,CodeType): result.update(names(item))
    return result


def owned(path):
    try:return Path(path).resolve().is_relative_to(ROOT)
    except (TypeError,ValueError):return False


def functions(entry):
    seen=set(); found=[]
    def walk(value):
        if id(value) in seen:return
        seen.add(id(value))
        if isinstance(value,FunctionType) and owned(value.__code__.co_filename):
            found.append(value)
            for name in names(value.__code__):
                if name in value.__globals__:walk(value.__globals__[name])
            for cell in value.__closure__ or ():
                try:walk(cell.cell_contents)
                except ValueError:pass
        elif isinstance(value,SimpleNamespace) or (isinstance(value,ModuleType) and owned(getattr(value,'__file__',None))):
            for name,item in vars(value).items():
                if name!='__builtins__':walk(item)
        elif isinstance(value,dict):
            for item in value.values():walk(item)
        elif isinstance(value,(tuple,list)):
            for item in value:walk(item)
        elif isinstance(value,FunctionType) and getattr(value,'__wrapped__',None) is not None:
            walk(value.__wrapped__)
    walk(entry)
    return found


@lru_cache(None)
def plan(k,nx,ny):
    terms=h.two_sided(k,nx,ny)
    field=ar.field(12)
    for i in range(12*nx):
        result=[0]*(12*ny)
        for a,c,out in terms:
            if a>>i&1:
                for j in ar.bits(c):result[j]^=out
        for j,value in enumerate(result):
            d=i//12+j//12
            expected=(field.mul(1<<(i%12),1<<(j%12))<<(12*d)) if d<k else 0
            assert value==expected,(k,nx,ny,i,j,value,expected)
    return terms


def apply(b,a,c,out,terms,reverse=False):
    x=[bit for word in a for bit in word]
    y=[bit for word in c for bit in word]
    z=[bit for word in out for bit in word]
    assert len(set(map(str,x+y+z)))==len(x)+len(y)+len(z)
    for am,cm,zm in (reversed(terms) if reverse else terms):
        ix,iy,iz=map(lambda v:list(ar.bits(v)),(am,cm,zm))
        p,q,r=ix[0],iy[0],iz[0]
        for i in ix[1:]:b.cx(x[i],x[p])
        for j in iy[1:]:b.cx(y[j],y[q])
        for l in iz[1:]:b.cx(z[r],z[l])
        b.ccx(x[p],y[q],z[r])
        for l in reversed(iz[1:]):b.cx(z[r],z[l])
        for j in reversed(iy[1:]):b.cx(y[j],y[q])
        for i in reversed(ix[1:]):b.cx(x[i],x[p])


def choose(b,a,c,out,N,reverse,original,kind):
    k=len(out)
    if 2<=k<=17 and min(len(a),len(c))>=2:
        nx,ny=min(len(a),k),min(len(c),k)
        if nx*ny>1:
            terms=plan(k,nx,ny)
            if len(terms)<42*N:
                key=(kind,len(a),len(c),k,N,len(terms),bool(reverse))
                COUNTS[key]=COUNTS.get(key,0)+1
                return apply(b,a[:nx],c[:ny],out,terms,reverse)
    return original()


def conv_wrapper(original):
    def conv(b,g,q,out,N,reverse=False):
        return choose(b,g,q,out,N,reverse,lambda:original(b,g,q,out,N,reverse),'conv')
    return conv


def convolution_wrapper(original):
    def convolution_xor(b,a,c,out,reverse=False):
        return choose(b,a,c,out,len(a)+len(c)-1,reverse,
                      lambda:original(b,a,c,out,reverse),'convolution_xor')
    return convolution_xor


def install(cv):
    replacements={}
    for fn in functions(cv):
        filename=Path(fn.__code__.co_filename).name
        if filename=='direct_kernels.py' and fn.__name__=='conv':
            replacements[id(fn)]=conv_wrapper(fn)
        elif filename=='kernels.py' and fn.__name__=='convolution_xor':
            replacements[id(fn)]=convolution_wrapper(fn)
    assert replacements
    return private_rebind(cv,replacements,ROOT)
