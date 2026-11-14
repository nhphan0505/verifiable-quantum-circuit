"""All-input consuming GF64 inverse with twelve total live wires."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE.parent/'a08'),str(HERE.parent/'a04')]
from inverse19_consume16 import ar,ref,basic,combo,schedules,change_basis,retire
from decode_unitary3 import inverse3_inplace
from nonzero_consume16 import functions
PLAN=json.loads((HERE/'new_consuming12_plan.json').read_text())


def solve_columns(value,columns):
    basis={}
    for i,column in enumerate(columns):
        coefficient=1<<i
        while column:
            pivot=column.bit_length()-1
            if pivot not in basis:
                basis[pivot]=(column,coefficient)
                break
            old,tag=basis[pivot]
            column^=old
            coefficient^=tag
    answer=0
    while value:
        pivot=value.bit_length()-1
        if pivot not in basis:return None
        old,tag=basis[pivot]
        value^=old
        answer^=tag
    return answer


def retained_prefix(b,x,rows):
    """Consume the norm, retaining a possibly intersecting raw subspace."""
    to,back,K=ar.tower(6)
    ar.linear_inplace(b,x,to)
    raw=b.alloc_qubits(6)
    forms=basic.raw_forms19()
    for j,(left,right) in enumerate(forms):
        with ref.expose_pair(b,x,left,right) as(a,c):b.init_and(a,c,raw[j])
    norm_forms=ref.norm_forms(K)
    norm_rows=[(value>>7)&63 for value in norm_forms]
    active=norm_rows[:]
    for row in rows:
        if solve_columns(row,active) is None:active.append(row)
    full=active[:]
    for i in range(6):
        if solve_columns(1<<i,full) is None:full.append(1<<i)
    columns=[sum(((row>>j)&1)<<i for i,row in enumerate(full)) for j in range(6)]
    ar.linear_inplace(b,raw,columns)
    for j,form in enumerate(norm_forms):ref.form_xor(b,x,form&127,raw[j])
    for q,row in zip(raw[len(active):],full[len(active):]):
        mask=b.alloc_bits(1)[0]
        b.hmr(q,mask)
        for j in ar.bits(row):
            with ref.expose_pair(b,x,*forms[j]) as(a,c):b.ccz(a,c,mask)
        b.free(mask)
    transformed=[1,2,4]
    zero_positions=list(range(len(active),6))
    coefficients=[]
    for row in rows:
        coefficient=solve_columns(row,active)
        coefficients.append(coefficient)
        physical=coefficient
        if solve_columns(physical,transformed) is not None:
            physical^=1<<zero_positions.pop()
        transformed.append(physical)
    columns=[sum(((row>>j)&1)<<i for i,row in enumerate(transformed)) for j in range(6)]
    ar.linear_inplace(b,raw,columns)
    for q,coefficient in zip(raw[3:],coefficients):
        affine=0
        for j in ar.bits(coefficient&7):affine^=norm_forms[j]&127
        ref.form_xor(b,x,affine,q)
    inverse3_inplace(b,raw[:3])
    return raw


def inverse6_consume20_12(b,x):
    raw=retained_prefix(b,x,PLAN['raw_rows'])
    pool=list(b.alloc_qubits(PLAN['max_live']-12))
    all_wires=list(x)+list(raw)+pool[:]
    live=list(x)+list(raw)
    transcript=b.alloc_bits(6)
    b.bit_store(transcript,False)
    retire(b,live,pool,transcript,PLAN['begin'])
    for step in PLAN['steps']:
        if step['kind']=='new':
            target=pool.pop()
            with ref.expose_pair(b,live,step['left'],step['right']) as(a,c):
                b.init_and(a,c,target)
            live.append(target)
        else:
            change_basis(b,live,step['pre_rows'])
            with ref.expose_pair(b,live,step['left'],step['right']) as(a,c):
                b.ccx(a,c,live[step['target']])
        retire(b,live,pool,transcript,step)
    retire(b,live,pool,transcript,PLAN['final'])
    assert len(live)==6
    for i,target in enumerate(x):
        source=live[i]
        if str(source)==str(target):continue
        other=next((j for j,q in enumerate(live) if str(q)==str(target)),None)
        b.swap(source,target)
        live[i]=target
        if other is not None:live[other]=source
    kept=set(map(str,x))
    b.free([q for q in all_wires if str(q)not in kept])
    return transcript


def install(entry,ceiling=889):
    def wrap(original):
        def chosen(b,x):
            if len(x)==6 and ceiling-b.num_allocated_qubits in (6,7):
                return inverse6_consume20_12(b,x)
            return original(b,x)
        return chosen
    replacements={id(fn):wrap(fn)for fn in functions(entry)
                  if fn.__code__ is schedules.inverse_stream_noscratch.__code__}
    assert replacements
    scope=dict(entry.__globals__)
    for name in('extraction','synthesize'):
        scope[name]=combo.xsub.private_rebind(scope[name],replacements)
    result=combo.xsub.clone(entry,scope)
    for name in('convert_safe','baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result


decode=install(combo.decode)
