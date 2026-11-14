"""All-input initialized GF64 inverse with ten fresh qubits."""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent/'a08'), str(HERE.parent/'a04')]
from inverse19_consume16 import ar, ref, basic, combo, change_basis, retire
from nonzero_consume16 import functions
from exp.inverse_search import inverse20_iso as iso

PLAN = json.loads((HERE/'source_preserving19_b16_result.json').read_text())
assert PLAN['found'] and PLAN['domain'] == 'all' and PLAN['max_live'] == 16


def inverse6_initialized19(b, x):
    """Preserve x, return inverse0(x), and pay every internal HMR phase."""
    to, back, K = ar.tower(6)
    ar.linear_inplace(b, x, to)
    raw = b.alloc_qubits(6)
    for j, (left, right) in enumerate(basic.raw_forms19()):
        with ref.expose_pair(b, x, left, right) as (a, c):
            b.init_and(a, c, raw[j])
    inner = ref.inverse3_virtual(b, list(x)+list(raw), ref.norm_forms(K))
    pool = list(b.alloc_qubits(1))
    all_wires = list(x)+list(raw)+list(inner)+pool[:]
    live = list(x)+list(raw)+list(inner)
    transcript = b.alloc_bits(6)
    b.bit_store(transcript, False)
    retire(b, live, pool, transcript, PLAN['begin'])
    for step in PLAN['steps']:
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
    retire(b, live, pool, transcript, PLAN['final'])
    assert len(live) == 12
    # The final basis is (canonical reciprocal, canonical original source).
    for i, target in enumerate(x, 6):
        source = live[i]
        if str(source) == str(target):
            continue
        other = next((j for j, q in enumerate(live) if str(q) == str(target)), None)
        b.swap(source, target)
        live[i] = target
        if other is not None:
            live[other] = source
    out = live[:6]
    kept = set(map(str, list(x)+out))
    b.free([q for q in all_wires if str(q) not in kept])
    b.cz(x, transcript)
    b.free(transcript)
    return out


def install(entry, ceiling=889):
    def wrap(original):
        def chosen(b, x, z=None, keep_norm=False):
            if z is None and not keep_norm and b.num_allocated_qubits+10 <= ceiling:
                return inverse6_initialized19(b, x)
            return original(b, x, z, keep_norm)
        return chosen
    replacements = {id(fn):wrap(fn) for fn in functions(entry)
                    if fn.__code__ is iso.inverse6_xor20.__code__}
    assert replacements
    scope = dict(entry.__globals__)
    for name in ('extraction', 'synthesize'):
        scope[name] = combo.xsub.private_rebind(scope[name], replacements)
    result = combo.xsub.clone(entry, scope)
    for name in ('convert_safe', 'baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result


decode = install(combo.decode)
