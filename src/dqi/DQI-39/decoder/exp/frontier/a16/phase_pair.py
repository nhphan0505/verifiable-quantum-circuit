"""Two exact GF(64) inverse characters sharing five nonlinear intermediates."""
from pathlib import Path
import json, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'exp/r-main/narrow240'))
import exact_subs as xs

RECORD=json.loads((HERE/'best_pair.json').read_text())
MASKS=tuple(RECORD['masks'])
FORMS=tuple(xs.FORMS)+((RECORD['left'],RECORD['right']),)


def decompose(terms):
    rows=[0]*11;linear=0;constant=0
    for term in terms:
        if term[0]=='constant':constant^=1
        elif term[0]=='linear':linear^=1<<term[1]
        else:
            i,j=term[1:];rows[i]^=1<<j;rows[j]^=1<<i
    pairs=[]
    while any(rows):
        i=next(i for i,r in enumerate(rows) if r)
        j=next(xs.bits(rows[i]))
        left,right=rows[i],rows[j]
        pairs.append((left,right));linear^=left&right
        for k in range(11):
            if left>>k&1:rows[k]^=right
            if right>>k&1:rows[k]^=left
    return constant,linear,tuple(pairs)


EXPRESSIONS=tuple(decompose(t) for t in RECORD['terms'])
assert [len(t[2]) for t in EXPRESSIONS]==[2,2]


def phase_pair(b,x,coefficients):
    """Pay sum_i coefficients[i] * dot(MASKS[i],inv0(x)); preserve inputs."""
    raw=b.alloc_qubits(5)
    source=list(x)+list(raw)
    for i,(left,right) in enumerate(FORMS):
        with xs.expose_pair(b,source[:6+i],left,right) as (a,c):
            b.init_and(a,c,raw[i])
    for coefficient,(constant,linear,pairs) in zip(coefficients,EXPRESSIONS):
        if constant:b.z(coefficient)
        for i in xs.bits(linear):b.cz(source[i],coefficient)
        for left,right in pairs:
            with xs.expose_pair(b,source,left<<1,right<<1) as (a,c):
                b.ccz(a,c,coefficient)
    for i in reversed(range(5)):
        with xs.expose_pair(b,source[:6+i],*FORMS[i]) as (a,c):
            b.del_and(a,c,raw[i])
    b.free(raw)
