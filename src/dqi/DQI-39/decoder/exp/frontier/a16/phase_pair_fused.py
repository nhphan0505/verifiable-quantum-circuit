"""Pair of quantum inverse characters plus any classical inverse character."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'exp/r-main/narrow240'))
import exact_subs as xs
RECORD=json.loads((HERE/'fused_pair.json').read_text())
FORMS=tuple(xs.FORMS)+tuple(tuple(t) for t in RECORD['forms_extra'])


def phase_pair_fused(b,x,coefficients,mask):
    """Pay L0·inv(x)[1] + L1·inv(x)[56] + dot(mask,inv(x)), including x=0."""
    raw=b.alloc_qubits(7);source=list(x)+list(raw)
    for i,(left,right) in enumerate(FORMS):
        with xs.expose_pair(b,source[:6+i],left,right) as (a,c):
            b.init_and(a,c,raw[i])
    for coefficient,expression in zip(coefficients,RECORD['quantum']):
        if expression['constant']:b.z(coefficient)
        for i in xs.bits(expression['linear']):b.cz(source[i],coefficient)
        with xs.expose_pair(b,source,*expression['pair']) as (a,c):
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
