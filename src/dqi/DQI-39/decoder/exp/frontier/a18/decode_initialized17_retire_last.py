"""Exact initialized seventeen-product inverse with twelve fresh qubits."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'root')]
import decode_combo_v16 as parent
from decode_vector_control import xs,functions
from exp.inverse_search import inverse20 as ref
PLAN=json.loads((HERE/'retire_last_plan.json').read_text())


def inverse6_initialized17_retire_last(b,x):
    """Retire the last raw AND before allocating the sixth output coordinate."""
    raw=list(b.alloc_qubits(7))
    source=list(x)+raw
    for i,(left,right)in enumerate(PLAN['source_forms']):
        with xs.expose_pair(b,source[:6+i],left,right)as(a,c):
            b.init_and(a,c,raw[i])
    out=list(b.alloc_qubits(5))
    for j,form in enumerate(PLAN['linear'][:5]):
        if form&1:b.x(out[j])
        for i in xs.bits(form>>1):b.cx(source[i],out[j])
    for gate in PLAN['products']:
        if not((gate['left']|gate['right'])>>12&1):continue
        with xs.expose_pair(b,source,gate['left']<<1,gate['right']<<1)as(a,c):
            ref.rankone_xor(b,a,c,out,gate['vector'])
    with xs.expose_pair(b,source[:12],*PLAN['source_forms'][6])as(a,c):
        b.del_and(a,c,raw[-1])
    b.free(raw[-1]);raw.pop();source=list(x)+raw
    out+=list(b.alloc_qubits(1))
    form=PLAN['linear'][5]
    if form&1:b.x(out[5])
    for i in xs.bits(form>>1):b.cx(source[i],out[5])
    for gate in PLAN['products']:
        if(gate['left']|gate['right'])>>12&1:continue
        with xs.expose_pair(b,source,gate['left']<<1,gate['right']<<1)as(a,c):
            ref.rankone_xor(b,a,c,out,gate['vector'])
    for i in reversed(range(6)):
        with xs.expose_pair(b,source[:6+i],*PLAN['source_forms'][i])as(a,c):
            b.del_and(a,c,raw[i])
    b.free(raw)
    xs.linear_inplace(b,out,xs.inverse_columns(PLAN['output_columns']))
    return out


def install(entry):
    replacements={id(fn):inverse6_initialized17_retire_last for fn in functions(entry)
                  if fn.__code__ is xs.inverse6_init18.__code__}
    assert replacements
    scope=dict(entry.__globals__)
    for name in('extraction','synthesize'):
        scope[name]=xs.private_rebind(scope[name],replacements)
    result=xs.clone(entry,scope)
    for name in('convert_safe','baseline'):
        assert result.__globals__[name]is entry.__globals__[name]
    return result


decode=install(parent.decode)
