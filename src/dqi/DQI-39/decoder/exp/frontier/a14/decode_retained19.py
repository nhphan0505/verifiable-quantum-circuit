"""Strictly nonzero 19-product scalar producer retaining two source coordinates."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'root')]
from decode_inverse20_12 import (ar,ref,combo,change_basis,retire,retained_prefix,functions)
PLAN=json.loads((HERE/'new19_retained2_b14_plan.json').read_text())
assert PLAN['found'] and PLAN['retained']==2 and PLAN['domain']=='nonzero'


def inverse6_retained19(b, x):
    plan = PLAN
    """Return an original-input phase mask and k linear source coordinates."""
    assert plan['domain'] == 'nonzero'
    raw = retained_prefix(b, x, plan['raw_rows'])
    pool = list(b.alloc_qubits(plan['max_live']-12))
    all_wires = list(x) + list(raw) + pool[:]
    live = list(x) + list(raw)
    transcript = b.alloc_bits(6)
    b.bit_store(transcript, False)
    retire(b, live, pool, transcript, plan['begin'])
    for step in plan['steps']:
        if step['kind'] == 'new':
            target = pool.pop()
            with ref.expose_pair(b, live, step['left'], step['right']) as (a, c):
                b.init_and(a, c, target)
            live.append(target)
        else:
            change_basis(b, live, step['pre_rows'])
            with ref.expose_pair(b, live, step['left'], step['right']) as (a, c):
                b.ccx(a, c, live[step['target']])
        retire(b, live, pool, transcript, step)
    retire(b, live, pool, transcript, plan['final'])
    assert len(live) == 6 + plan['retained']
    for i, target in enumerate(x):
        source = live[i]
        if str(source) == str(target):
            continue
        other = next((j for j, q in enumerate(live) if str(q) == str(target)), None)
        b.swap(source, target)
        live[i] = target
        if other is not None:
            live[other] = source
    cache = live[6:]
    held = set(map(str, list(x)+cache))
    b.free([q for q in all_wires if str(q) not in held])
    return transcript, cache


def install(entry):
    # This exact closure exists only in root's clipped, nonzero fold divider.
    targets=[fn for fn in functions(entry)
             if fn.__name__=='produce_retained'
             and Path(fn.__code__.co_filename).name=='decode_inverse_retained.py']
    assert targets
    replacements={id(fn):inverse6_retained19 for fn in targets}
    scope=dict(entry.__globals__)
    scope['synthesize']=combo.xsub.private_rebind(scope['synthesize'],replacements)
    result=combo.xsub.clone(entry,scope)
    for name in ('extraction','convert_safe','baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result


import decode_root_v11_six
decode=install(decode_root_v11_six.decode)
