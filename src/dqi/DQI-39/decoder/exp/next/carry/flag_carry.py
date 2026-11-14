"""Carry of the pole flags along the homogeneous return.

The forward measures the flags of groups 5 to 15 in the X basis and keeps the
bits. The return holds one flag: at the end of a group's node it computes the
flag of the group before as this flag AND zero(N of that group), and a CZ with
the kept bit repays the measurement. So the flags hold no wires through the
middle stages, and groups 5 to 7 take the homogeneous route too.
The relation P(g-1) = P(g) AND zero(N(g-1)) fails only on rare inputs.

The one-carry history is yoyobar's; Ali Haydar Ozdag fitted it to the q18 return,
with groups 6 and 7 on the homogeneous route. Written for q22's return by Claude.
"""
import ast
from pathlib import Path
import walk_bound as walk

ROOT = Path(__file__).resolve().parents[3]
FIRST, LAST = 5, 16
banks = {}


def carry_forward(b, token, gi):
    bank = banks.setdefault(id(b), dict(masks={}, flag=None))
    pole = token.pop('pole')
    if gi == LAST:
        bank['flag'] = pole
        return
    mask = b.alloc_bits(1)
    b.hmr(pole, mask[0])
    b.free(pole)
    bank['masks'][gi] = mask


def carry_pole(b, gi):
    bank = banks[id(b)]
    if gi < LAST:
        mask = bank['masks'].pop(gi)
        b.cz(bank['flag'], mask[0])
        b.free(mask)
    return bank['flag']


def carry_next(b, pole, marker, gi, zero_flag):
    bank = banks[id(b)]
    if gi == FIRST:
        assert not bank['masks']
        bank['flag'] = None
        return
    b.x(pole)
    bank['flag'] = zero_flag(b, list(marker) + [pole])
    b.x(pole)


def source_text():
    path = ROOT / 'exp/new/a01/companion.py'
    text = path.read_text()
    node = next(x for x in ast.parse(text).body if isinstance(x, ast.FunctionDef) and x.name == 'external_node_chain')
    source = ast.get_source_segment(text, node)
    begin = source.index("    with b.mark('companion_normalize'):")
    end = source.index('    b.cswap(pole, N, D)', begin)
    source = source[:begin] + '''    with b.mark('companion_normalize'):
        norm, F = normalize_three(b,N,D,L,R)
    with b.mark('companion_fused_chart'):
        original = finish_fused(b,D,F,token['norm'],norm,N,L,R,heads[0],gn['c'])
''' + source[end:]
    for before, after in (
        ("        return forward_original(b, words, gi, reverse, token, normalizer)",
         "        result = forward_original(b, words, gi, reverse, token, normalizer)\n"
         "        if not reverse:\n"
         "            carry_forward(b, result, gi)\n"
         "        return result"),
        ("    pole = token['pole']", "    pole = carry_pole(b, gi)"),
        ("    b.cswap(pole, N, D)\n    fm = b.alloc_bits(1)",
         "    b.cswap(pole, N, D)\n"
         "    previous = ref.groups[gi - 1]['word']\n"
         "    carry_next(b, pole, combine(words[previous:previous + 2]), gi, ref.zero_flag)\n"
         "    fm = b.alloc_bits(1)"),
    ):
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    return source


def install(entry):
    namespace = {}
    exec(compile(source_text(), __file__, 'exec'), namespace)
    code = namespace['external_node_chain'].__code__
    functions = walk.functions(entry)
    log = dict(nodes=0, scopes=0)
    for fn in functions:
        if fn.__name__ == 'external_node_chain' and {'finish_fused', 'SELECT', 'forward_original'} <= set(fn.__code__.co_names):
            fn.__globals__.update(carry_forward=carry_forward, carry_pole=carry_pole, carry_next=carry_next)
            fn.__code__ = code
            log['nodes'] += 1
    for scope in {id(fn.__globals__): fn.__globals__ for fn in functions}.values():
        for key in ('EXTERNAL_HOMOGENEOUS', 'SELECT'):
            if scope.get(key) == frozenset(range(8, LAST + 1)):
                scope[key] = frozenset(range(FIRST, LAST + 1))
                log['scopes'] += 1
    assert log['nodes'] and log['scopes']
    return log
