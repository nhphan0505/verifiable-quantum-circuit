"""Consume a GF64 input with the isotopy20 circuit and fourteen wires."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from inverse19_consume16 import (ar,ref,combo,schedules,replacement_ids,
                               change_basis,retire,inverse6_consume17,inverse6_consume19)
from decode_unitary3 import inverse3_inplace
from exp.inverse_search import inverse20_iso as iso
PLAN=json.loads((HERE/'generic20_plan.json').read_text())
assert PLAN['domain']=='all' and PLAN['max_live']==14


def inverse6_consume20(b,x):
    """Exact inverse0; consume the source and return its linear character."""
    to,back,K=ar.tower(6);ar.linear_inplace(b,x,to)
    raw=b.alloc_qubits(6)
    for j,(left,right) in enumerate(iso.raw_forms()):
        with ref.expose_pair(b,x,left,right) as (a,c):b.init_and(a,c,raw[j])
    rows=iso.NORM_ROWS+iso.EXTRA_ROWS
    columns=[sum(((row>>j)&1)<<i for i,row in enumerate(rows)) for j in range(6)]
    ar.linear_inplace(b,raw,columns)
    for j,form in enumerate(ref.norm_forms(K)):
        ref.form_xor(b,x,form&127,raw[j])
    inverse3_inplace(b,raw[:3])
    pool=list(b.alloc_qubits(2))
    all_wires=list(x)+list(raw)+pool[:]
    live=list(x)+list(raw)
    transcript=b.alloc_bits(6);b.bit_store(transcript,False)
    retire(b,live,pool,transcript,PLAN['begin'])
    for step in PLAN['steps']:
        if step['kind']=='new':
            target=pool.pop()
            with ref.expose_pair(b,live,step['left'],step['right']) as (a,c):
                b.init_and(a,c,target)
            live.append(target)
        else:
            change_basis(b,live,step['pre_rows'])
            with ref.expose_pair(b,live,step['left'],step['right']) as (a,c):
                b.ccx(a,c,live[step['target']])
        retire(b,live,pool,transcript,step)
    retire(b,live,pool,transcript,PLAN['final'])
    assert len(live)==6
    for i,target in enumerate(x):
        source=live[i]
        if str(source)==str(target):continue
        other=next((j for j,q in enumerate(live) if str(q)==str(target)),None)
        b.swap(source,target);live[i]=target
        if other is not None:live[other]=source
    retained=set(map(str,x))
    b.free([q for q in all_wires if str(q) not in retained])
    return transcript


def stream(b,x):
    if len(x)==6:
        live=b.num_allocated_qubits
        if live+12>889 and live+11<=889:return inverse6_consume17(b,x)
        if live+11>889 and live+10<=889:return inverse6_consume19(b,x)
        if live+10>889 and live+8<=889:return inverse6_consume20(b,x)
    return recursive(b,x)


recursive=combo.xsub.clone(schedules.inverse_stream_noscratch,
                         dict(schedules.inverse_stream_noscratch.__globals__,inverse_stream_noscratch=stream))


def install(entry):
    replacements=replacement_ids(entry,schedules.inverse_stream_noscratch,stream)
    scope=dict(entry.__globals__)
    for name in ('extraction','synthesize'):
        scope[name]=combo.xsub.private_rebind(scope[name],replacements)
    return combo.xsub.clone(entry,scope)


decode=install(combo.decode)
