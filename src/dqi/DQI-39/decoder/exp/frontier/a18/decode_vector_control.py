"""Whole-decoder control for seven-source vector inverse characters."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE.parent/'root'),str(HERE.parent/'a04')]
import decode_combo_v14 as current
import decode_quantum_inverse_phase as prior
from nonzero_consume16 import functions
from exp.inverse_search import inverse20 as ref
xs=prior.xs
PLAN=json.loads((HERE/'control_plan.json').read_text())


def phase_inverse6_vector(b,x,coefficient,annihilates_zero=False):
    """Pay coefficient dot inverse0(x), preserving both quantum words."""
    raw=b.alloc_qubits(7)
    source=list(x)+list(raw)
    for i,(left,right) in enumerate(PLAN['source_forms']):
        with xs.expose_pair(b,source[:6+i],left,right)as(a,c):
            b.init_and(a,c,raw[i])
    for j,form in enumerate(PLAN['linear']):
        if form&1:b.z(coefficient[j])
        for i in xs.bits(form>>1):b.cz(source[i],coefficient[j])
    for gate in PLAN['products']:
        positions=list(xs.bits(gate['vector']))
        pivot=positions[0]
        for j in positions[1:]:b.cx(coefficient[j],coefficient[pivot])
        with xs.expose_pair(b,source,gate['left']<<1,gate['right']<<1)as(a,c):
            b.ccz(a,c,coefficient[pivot])
        for j in reversed(positions[1:]):b.cx(coefficient[j],coefficient[pivot])
    for i in reversed(range(7)):
        with xs.expose_pair(b,source[:6+i],*PLAN['source_forms'][i])as(a,c):
            b.del_and(a,c,raw[i])
    b.free(raw)


def install(entry,plan=PLAN):
    replacement=xs.clone(phase_inverse6_vector,dict(phase_inverse6_vector.__globals__,PLAN=plan))
    targets={id(fn):replacement for fn in functions(entry)
             if fn.__code__ is prior.phase_inverse6_quantum.__code__}
    assert targets
    scope=dict(entry.__globals__)
    for name in ('extraction','synthesize'):
        scope[name]=xs.private_rebind(scope[name],targets)
    result=xs.clone(entry,scope)
    for name in ('convert_safe','baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result


decode=install(current.decode)
