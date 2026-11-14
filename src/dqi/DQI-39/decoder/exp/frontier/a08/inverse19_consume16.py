"""All-input consuming GF64 inverse using sixteen total live wires."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'exp/r-main/narrow240'),str(HERE.parent/'a03')]
import decode_combo as combo
from jet_norm6 import replacement_ids
from inverse_consume17 import inverse6_consume17
from exp.inverse_width_subspaces import kernel19 as basic
from exp.inverse_search import inverse20 as ref
from exp.noscratch import schedules
from exp.arithmetic import field as ar
PLAN=json.loads((HERE/'generic19_plan16.json').read_text())
assert PLAN['domain']=='all' and PLAN['max_live']==16


def change_basis(b,live,rows):
    columns=[sum(((r>>(j+1))&1)<<i for i,r in enumerate(rows)) for j in range(len(live))]
    ar.linear_inplace(b,live,columns)
    for q,row in zip(live,rows):
        if row&1:b.x(q)


def retire(b,live,pool,transcript,record):
    change_basis(b,live,record['rows'])
    for action in record['retire']:
        p=action['index']
        for j in action['mix']:b.cx(live[j],live[p])
        q=live.pop(p);m=b.alloc_bits(1)[0];b.hmr(q,m)
        for term in action['phase']:
            if term[0]=='constant':b.z(m)
            elif term[0]=='linear':b.cz(live[term[1]],m)
            elif term[0]=='pair':b.ccz(live[term[1]],live[term[2]],m)
            else:b.cx(m,transcript[term[1]])
        b.free(m);pool.append(q)


def inverse6_consume19(b,x):
    """Consume x, return inv0(x) and the original-input linear HMR mask."""
    to,back,K=ar.tower(6);ar.linear_inplace(b,x,to)
    raw=b.alloc_qubits(6)
    for j,(left,right) in enumerate(basic.raw_forms19()):
        with ref.expose_pair(b,x,left,right) as (a,c):b.init_and(a,c,raw[j])
    inner=ref.inverse3_virtual(b,list(x)+list(raw),ref.norm_forms(K))
    pool=list(b.alloc_qubits(1))
    all_wires=list(x)+list(raw)+list(inner)+pool[:]
    live=list(x)+list(raw)+list(inner)
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
    return recursive(b,x)


recursive=combo.xsub.clone(schedules.inverse_stream_noscratch,
                         dict(schedules.inverse_stream_noscratch.__globals__,inverse_stream_noscratch=stream))


def install(entry):
    replacements=replacement_ids(entry,schedules.inverse_stream_noscratch,stream)
    assert replacements
    scope=dict(entry.__globals__)
    for name in ('extraction','synthesize'):
        scope[name]=combo.xsub.private_rebind(scope[name],replacements)
    return combo.xsub.clone(entry,scope)


decode=install(combo.decode)
assert decode.__globals__['convert_safe'] is combo.decode.__globals__['convert_safe']
assert decode.__globals__['baseline'] is combo.decode.__globals__['baseline']
