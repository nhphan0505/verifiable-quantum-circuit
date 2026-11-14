"""Actual192T chain-pair successor: share twoGF16 Frobenius blocks.

The second99T multiplier uses the Frobenius-conjugate polynomial basis.
Its denominator evaluations then align with all first-multiplier blocks.
Fixed field gauges select two common numerator blocks on23 actual charts.
"""
from pathlib import Path
from functools import lru_cache
import json
from defect_tensor import ar,emul,einv,esqrt,epow,K,transpose,regroup,tensor99_extension
from eval_blocks import blocks,PAIR4
from chain_fused import tensor_accumulate

DATA=json.loads(Path(__file__).with_name('search_conjugate_pair4.json').read_text())
FRAMES={int(c):v for c,v in DATA['frames'].items()}
ROUTES={int(c):v for c,v in DATA['routes'].items()}

@lru_cache(None)
def frame_tensor(c):
    f=FRAMES[c];lam=f['lam'];sigma=f['sigma'];shared=set(f['blocks'])
    il=einv(lam);isz=einv(sigma);f4=ar.field(4)
    lc=tuple(emul(lam,1<<i) for i in range(24))
    pc=tuple(esqrt(emul(sigma,emul(c,1<<i)^((1<<i)>>12))) for i in range(24))
    terms=[];m99=tensor99_extension(K)
    for index,(ev,out) in enumerate(blocks()):
        if index not in shared:
            for mask,value in m99[9*index:9*index+9]:
                terms.append((transpose(mask,lc),mask,emul(il,value)))
                terms.append((transpose(mask,pc),mask,emul(isz,emul(value,value))<<24))
            continue
        xc=tuple(ar.apply(ev,z) for z in lc)
        second=tuple(f4.square(ar.apply(ev,z)) for z in pc)
        pivot=next(i for i,x in enumerate(xc) if x)
        scale=f4.mul(second[pivot],f4.invert(xc[pivot]))
        assert scale and all(y==f4.mul(scale,x) for x,y in zip(xc,second)),(c,index)
        out1=tuple(emul(il,z) for z in out)
        out2=[]
        for j in range(4):
            z=ar.apply(out,f4.pow(1<<j,8))
            out2.append(emul(isz,emul(z,z)))
        for u,v,w in PAIR4:
            left=ar.apply(out1,w&15)
            right=ar.apply(out2,f4.mul(scale,w>>4))
            terms.append((transpose(u,xc),transpose(v,ev),left|(right<<24)))
    tensor=regroup(terms)
    assert len(tensor)<=198-6*len(shared)
    return tensor

@lru_cache(None)
def preferred_tensor(c):
    if c not in ROUTES:return None
    route=ROUTES[c];k=route['k'];terms=frame_tensor(route['c'])
    if not k:return terms
    to=tuple(epow(1<<j,1<<k) for j in range(24))
    back=tuple(epow(1<<j,1<<(24-k)) for j in range(24))
    result=[]
    for a,b,v in terms:
        w=ar.apply(back,v&((1<<24)-1)) | (ar.apply(back,v>>24)<<24)
        result.append((transpose(a,to),transpose(b,to),w))
    return tuple(result)

def products(b,H,D,N,L,c,old_tensor):
    terms=preferred_tensor(c)
    tensor_accumulate(b,H,D,list(N)+list(L),old_tensor(c) if terms is None else terms)

def install(entry):
    import walk_bound
    edits=[];seen=set()
    for fn in walk_bound.functions(entry):
        names=set(fn.__code__.co_names)
        if not {'joint_tensor','accumulator'}<=names:continue
        scope=fn.__globals__
        if id(scope) in seen:continue
        seen.add(id(scope));old=scope['joint_tensor']
        assert len(old(0))==182 and len(old(2023))==192
        def factory(original):
            @lru_cache(None)
            def choose(c):
                new=preferred_tensor(c)
                return original(c) if new is None else new
            return choose
        scope['joint_tensor']=factory(old)
        edits.append(dict(file=fn.__code__.co_filename,line=fn.__code__.co_firstlineno,
                          name=fn.__name__,base_zero_terms=182,base_nonzero_terms=192))
    assert edits,'Actual joint_tensor/accumulator chain owner not found'
    return edits
