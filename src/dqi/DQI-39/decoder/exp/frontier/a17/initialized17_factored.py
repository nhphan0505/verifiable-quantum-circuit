"""Initialized A18 inverse with explicit conditional cubic phase repairs."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'a08'),str(HERE.parent/'a04'),str(HERE.parent/'root')]
from inverse19_consume16 import ar,ref,combo,change_basis
from nonzero_consume16 import functions
import decode_initialized19 as old
DAG=json.loads((HERE/'a18_dag17_frozen.json').read_text())
PLAN=json.loads((HERE/'a18_17_initialized_b16_cubic_plan.json').read_text())
assert PLAN['found'] and PLAN['preserve'] and PLAN['max_live']==16


def retire_cubic(b,live,pool,transcript,debts,record):
    change_basis(b,live,record['rows'])
    for action in record['retire']:
        p=action['index']
        for j in action['mix']:b.cx(live[j],live[p])
        q=live.pop(p);m=b.alloc_bits(1)[0];b.hmr(q,m)
        for term in action['phase']:
            kind=term[0]
            if kind=='constant':b.z(m)
            elif kind=='linear':b.cz(live[term[1]],m)
            elif kind=='pair':b.ccz(live[term[1]],live[term[2]],m)
            elif kind=='original':b.cx(m,transcript[term[1]])
            elif kind=='triple':
                b.push_condition(m)
                b.ccz(*[live[i] for i in term[1:]])
                b.pop_condition()
            else:b.cx(m,debts[tuple(term)])
        b.free(m);pool.append(q)


def pay_final_cubics_factored(b,live,debts):
    """Exact factorization of the two late HMR characters in this plan."""
    expected={("final_triple",0,1,k) for k in (2,3,4,5,8,9,10)}
    expected.update(("final_triple",0,2,k) for k in (3,4,5))
    assert set(debts)==expected
    late=debts[("final_triple",0,1,2)]
    earlier=debts[("final_triple",0,1,5)]
    b.cx(late,earlier)
    b.push_condition(late)
    for j in (3,4,5,8,9,10):b.cx(live[j],live[2])
    b.ccz(live[0],live[1],live[2])
    for j in reversed((3,4,5,8,9,10)):b.cx(live[j],live[2])
    for j in (4,5):b.cx(live[j],live[3])
    b.ccz(live[0],live[2],live[3])
    for j in (5,4):b.cx(live[j],live[3])
    b.pop_condition()
    b.push_condition(earlier)
    b.ccz(live[0],live[1],live[5])
    b.pop_condition()


def inverse6_initialized17_factored(b,x):
    raw=b.alloc_qubits(7)
    source=list(x)+list(raw)
    for i,(left,right) in enumerate(DAG['source_forms']):
        with ref.expose_pair(b,source[:6+i],left,right) as(a,c):
            b.init_and(a,c,raw[i])
    pool=list(b.alloc_qubits(3));all_wires=source+pool[:];live=source[:]
    transcript=b.alloc_bits(6);b.bit_store(transcript,False)
    phase_bits=b.alloc_bits(len(PLAN['final_phases']));b.bit_store(phase_bits,False)
    debts={tuple(term):bit for term,bit in zip(PLAN['final_phases'],phase_bits)}
    retire_cubic(b,live,pool,transcript,debts,PLAN['begin'])
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
        retire_cubic(b,live,pool,transcript,debts,step)
    retire_cubic(b,live,pool,transcript,debts,PLAN['final'])
    assert len(live)==12
    pay_final_cubics_factored(b,live,debts)
    b.free(phase_bits)
    for i,target in enumerate(x,6):
        source=live[i]
        if str(source)==str(target):continue
        other=next((j for j,q in enumerate(live) if str(q)==str(target)),None)
        b.swap(source,target);live[i]=target
        if other is not None:live[other]=source
    out=live[:6];kept=set(map(str,list(x)+out))
    b.free([q for q in all_wires if str(q) not in kept])
    b.cz(x,transcript);b.free(transcript)
    return out


def install(entry):
    replacements={id(fn):inverse6_initialized17_factored for fn in functions(entry)
                  if fn.__code__ is old.inverse6_initialized19.__code__}
    assert replacements
    scope=dict(entry.__globals__)
    for name in ('extraction','synthesize'):
        scope[name]=combo.xsub.private_rebind(scope[name],replacements)
    result=combo.xsub.clone(entry,scope)
    for name in ('convert_safe','baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result
