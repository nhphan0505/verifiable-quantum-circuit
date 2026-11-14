"""Compose cyclic top-row sharing with an existing one-word Hankel handoff."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import inspect
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'research/agents/a09'), str(ROOT/'research/agents/a01')]
import hankel_compact as h
p, ar, k = h.p, h.ar, h.kernels


@lru_cache(None)
def root_terms(sources):
    f = ar.field(12)
    zeta = f.pow(f.primitive_element, 117)
    points = [f.pow(zeta, i) for i in range(35)]
    assert len(set(points)) == 35
    V = [[f.pow(point, j) for j in range(35)] for point in points]
    W = k.mi(V)
    outputs = 36-sources
    terms = tuple((tuple(V[t][:sources]),
                   tuple(W[32-j][t] for j in range(33)),
                   tuple(V[t][outputs-1-j] for j in range(outputs))+(V[t][34],))
                  for t in range(35))
    for i in range(sources):
        for j in range(33):
            out = [0]*(outputs+1)
            for a, b, c in terms:
                ab = f.mul(a[i], b[j])
                for index, coefficient in enumerate(c):
                    out[index] ^= f.mul(ab, coefficient)
            expected = [int(i+j == sources-3+index) for index in range(outputs)]
            expected.append(int(i > 0 and i+j == 33))
            assert out == expected, (sources, i, j, out, expected)
    return terms


def install(cv, root_sources=16):
    cells = dict(zip(cv.__code__.co_freevars, cv.__closure__))
    core = cells['core'].cell_contents
    scope = core.__globals__
    old_hankel = scope['old'].hankel
    hcells = dict(zip(old_hankel.__code__.co_freevars, old_hankel.__closure__))
    forward_name = 'forward_tri' if 'forward_tri' in hcells else 'forward'
    old_forward = hcells[forward_name].cell_contents
    saved = hcells['saved'].cell_contents
    current = {'delta': None}

    def accumulate(b, x, q, out, terms):
        assert current['delta'] is not None
        assert len(x) == 12*root_sources and len(q) == 12*33
        words = lambda flat: [flat[i:i+12] for i in range(0,len(flat),12)]
        aw, bw, tw = map(words, (x,q,out))
        tw.append(current['delta'])
        for ac, bc, tc in root_terms(root_sources):
            p.dk.rank_update(b, aw, ac, bw, bc, tw, tc)

    # Only the outer call uses these globals. Recursive calls retain the old
    # closure and its original helper, so the extra row is produced once.
    env = dict(old_forward.__globals__)
    env['h'] = SimpleNamespace(**dict(vars(env['h']), accumulate=accumulate))
    forward = p.clone(old_forward, env)

    def hankel(b, B, A, reverse=False, delta=None):
        if reverse:
            assert delta is None
            return old_hankel(b,B,A,True)
        assert delta is not None and not saved
        current['delta'] = delta
        try:
            forward(b,list(reversed(B[1:])),A)
        finally:
            current['delta'] = None
        for i in range(len(A)//2):
            b.swap(A[i],A[-1-i])
        assert len(saved) == 1

    scope['old'].hankel = hankel
    source = inspect.getsource(core)
    needle = 'for i in range(17):old.ar.mul_xor0(b,E[i+1],w[i],delta)'
    assert source.count(needle) == 1
    source = source.replace(needle,
        f'for i in range({root_sources//2},17):old.ar.mul_xor0(b,E[i+1],w[i],delta)')
    needle = "b.cx(delta,top);phase['_top_dot']=delta"
    assert source.count(needle) == 1
    source = source.replace(needle, "phase['_top_dot']=delta")
    needle = '        old.hankel(b,B[1:],A[:34])'
    assert source.count(needle) == 1
    source = source.replace(needle,
        f'        for j in range(2,{root_sources},2):old.ar.mul_xor0(b,B[j+1],A[j],delta)\n'
        '        old.hankel(b,B[1:],A[:34],delta=delta)\n'
        '        b.cx(delta,top)')
    exec(compile(source, __file__, 'exec'), scope)
    cells['core'].cell_contents = scope[core.__name__]
    return cv
