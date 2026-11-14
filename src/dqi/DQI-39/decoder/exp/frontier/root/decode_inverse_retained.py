"""Joint consuming inversion and retained norm coordinates in fold division."""
from pathlib import Path
from types import SimpleNamespace
import inspect
import json
import sys
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent/'a08')]
from inverse20_consume14 import ar, ref, iso, change_basis, retire, inverse3_inplace, combo
from final_decoder import synthesis as original_folds
import norm_cache
import decode_combo_v9


def inverse6_retained(b, x, plan):
    """Return an original-input phase mask and k linear source coordinates."""
    assert plan['domain'] == 'all'
    to, back, K = ar.tower(6)
    ar.linear_inplace(b, x, to)
    raw = b.alloc_qubits(6)
    for j, (left, right) in enumerate(iso.raw_forms()):
        with ref.expose_pair(b, x, left, right) as (a, c):
            b.init_and(a, c, raw[j])
    rows = iso.NORM_ROWS + iso.EXTRA_ROWS
    columns = [sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(6)]
    ar.linear_inplace(b, raw, columns)
    for j, form in enumerate(ref.norm_forms(K)):
        ref.form_xor(b, x, form & 127, raw[j])
    inverse3_inplace(b, raw[:3])
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


def install(entry, keep=2):
    plan = json.loads((HERE/f'retained_inverse_k{keep}_b14_all.json').read_text())
    assert plan['found']
    synthesize = entry.__globals__['synthesize']
    folds = synthesize.__globals__['folds']
    old_divide = folds.ug['absorb_even'].__globals__['divide_fused']
    source = inspect.getsource(original_folds.divide_fused)
    before = '    t = inverse6_xor20(b, M)\n'
    after = '''    inverse_mask, kept_M = produce_retained(b, M)
    t = M
    part_masks = []
'''
    assert source.count(before) == 1
    source = source.replace(before, after)
    before = '            ar.erase_product(b, out, M, part)\n'
    after = '''            pm = b.alloc_bits(6)
            b.hmr(part, pm)
            part_masks.append(pm)
'''
    assert source.count(before) == 1
    source = source.replace(before, after)
    before = '    for off, m in zip((0, 12), masks):\n'
    after = '''    ar.linear_inplace(b, N, to)
    M = rebuild_retained(b, N, kept_M, k6)
    ar.linear_inplace(b, N, frm)
    b.cz(M, inverse_mask)
    b.free(inverse_mask)
    for off in (0, 12):
        half = x[off:off+12]
        ar.linear_inplace(b, half, to)
        for j in (0, 6):
            pm = part_masks.pop(0)
            ar.phase_product(b, half[j:j+6], M, pm)
            b.free(pm)
        ar.linear_inplace(b, half, frm)
    assert not part_masks
    for off, m in zip((0, 12), masks):
'''
    assert source.count(before) == 1
    source = source.replace(before, after)
    def produce_retained(b, x):
        return inverse6_retained(b, x, plan)
    environment = dict(old_divide.__globals__, produce_retained=produce_retained,
                       rebuild_retained=norm_cache.rebuild)
    exec(compile(source, __file__, 'exec'), environment)
    ug = dict(folds.ug)
    for name in ('absorb', 'absorb_even'):
        fn = ug[name]
        ug[name] = combo.xsub.clone(fn, dict(fn.__globals__, divide_fused=environment['divide_fused']))
    proxy = SimpleNamespace(**dict(vars(folds), ug=ug))
    replacement = combo.xsub.clone(synthesize, dict(synthesize.__globals__, folds=proxy))
    result = combo.xsub.clone(entry, dict(entry.__globals__, synthesize=replacement))
    for name in ('convert_safe', 'baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result


decode = install(combo.decode)
