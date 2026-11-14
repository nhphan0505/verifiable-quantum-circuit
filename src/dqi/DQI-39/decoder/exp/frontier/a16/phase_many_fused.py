"""Several quantum inverse characters and arbitrary classical inverse character."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from phase_pair_fused import FORMS,RECORD,xs


def decompose(terms):
    rows=[0]*13;linear=0;constant=0
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
        for k in range(13):
            if left>>k&1:rows[k]^=right
            if right>>k&1:rows[k]^=left
    return constant,linear,tuple(pairs)


CHARACTERS={int(k):decompose(v['terms']) for k,v in json.loads((HERE/'fused_characters.json').read_text()).items()}


def phase_many_fused(b,x,coefficients,mask):
    """coefficients maps constant field masks to quantum coefficients; inv0 is total."""
    raw=b.alloc_qubits(7);source=list(x)+list(raw)
    for i,(left,right) in enumerate(FORMS):
        with xs.expose_pair(b,source[:6+i],left,right) as (a,c):
            b.init_and(a,c,raw[i])
    for char,coefficient in coefficients.items():
        constant,linear,pairs=CHARACTERS[char]
        if constant:b.z(coefficient)
        for i in xs.bits(linear):b.cz(source[i],coefficient)
        for left,right in pairs:
            with xs.expose_pair(b,source,left<<1,right<<1) as (a,c):
                b.ccz(a,c,coefficient)
    for coefficient,terms in zip(mask,RECORD['classical']):
        for term in terms:
            if term[0]=='constant':b.z(coefficient)
            elif term[0]=='linear':b.cz(source[term[1]],coefficient)
            else:b.ccz(source[term[1]],source[term[2]],coefficient)
    for i in reversed(range(7)):
        with xs.expose_pair(b,source[:6+i],*FORMS[i]) as (a,c):
            b.del_and(a,c,raw[i])
    b.free(raw)
