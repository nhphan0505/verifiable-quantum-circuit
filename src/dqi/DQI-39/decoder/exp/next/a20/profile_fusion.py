"""Exact rank-one factor overlap audit for the two chain updates.

This uses arithmetic modules only, never an imported whole decoder.
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'playbook/kit'),str(ROOT/'playbook/kit/decoder')]
from exp.decoder.common import ar,emul,mul,inv,K
from exp.mul99.kernels import tensor99_extension

def transpose(mask,cols):
    return sum(((mask&v).bit_count()&1)<<i for i,v in enumerate(cols))

def terms(c,first='99',second='99'):
    sq=tuple(emul(1<<i,1<<i) for i in range(24))
    change=tuple(emul(c,1<<i) ^ ((1<<i)>>12) for i in range(24))
    ts=tensor99_extension(K) if first=='99' else ar.tensor24_extension(K)
    out=[(m,m,v) for m,v in ts]
    if c:
        us=tensor99_extension(K) if second=='99' else ar.tensor24_extension(K)
        out += [(transpose(m,change),transpose(m,sq),v<<24) for m,v in us]
    else:
        for high in (False,True):
            for m,v in ar.tensor(12):
                out.append((m<<12,transpose(m<<(12 if high else 0),sq),v<<(36 if high else 24)))
    return out

def compress(ts):
    # Exact merge when both input forms coincide.
    d={}
    for a,b,c in ts:
        if not a or not b or not c:continue
        d[a,b]=d.get((a,b),0)^c
    return [(a,b,c) for (a,b),c in d.items() if c]

def summary(ts):
    from collections import Counter
    return dict(rank_terms=len(ts),after_identical_pair_merge=len(compress(ts)),
                repeated_factors=[sum(n*(n-1)//2 for n in Counter(t[i] for t in ts).values()) for i in range(3)])

if __name__=='__main__':
    records=[]
    for c in [0,1,inv(6),inv(20),inv(30),inv(72)]:
        for first in ['99','105']:
            for second in ['99','105'] if c else ['84']:
                t=terms(c,first,second)
                row=dict(c=c,first=first,second=second,**summary(t))
                records.append(row)
                print(row,flush=True)
                (Path(__file__).parent/f'terms_c{c}_{first}_{second}.json').write_text(json.dumps(t)+'\n')
    (Path(__file__).parent/'profile_fusion.json').write_text(json.dumps(records,indent=2)+'\n')
