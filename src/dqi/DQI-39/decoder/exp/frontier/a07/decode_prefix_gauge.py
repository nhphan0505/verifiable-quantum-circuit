"""Absorb the terminal continuant product into the prefix's linear head gauge.

The old prefix accumulator, plus its final r*border product, equals the new
accumulator identically.  No additional qubit or measurement is introduced.
"""
from pathlib import Path
import sys
import inspect

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'exp/r-main/narrow240'))
import decode_combo as combo


def install(entry):
    original = entry.__globals__['synthesize']
    source = inspect.getsource(original)
    edits = (
        ('b.cx(border,r);b.cx(border,d);b.cx(r,border);b.x(border[0])',
         'b.cx(border,r);b.cx(r,border);b.x(border[0])'),
        ('folds.add_tail(b,heads[i],qi,d,bool(i%2))',
         'folds.add_tail(b,heads[i],qi,d,not bool(i%2))'),
        ('ar.mul_xor0(b,r,border,d);tt=tail_inplace',
         'tt=tail_inplace'),
        ('tail_inplace(b,r,border,d,u,v,pole,True,tt);ar.mul_xor0(b,r,border,d)',
         'tail_inplace(b,r,border,d,u,v,pole,True,tt)'),
        ('b.cx(r,d);b.x(border[0]);b.cx(r,border);b.cx(border,r);b.free(r)',
         'b.x(border[0]);b.cx(r,border);b.cx(border,r);b.free(r)'),
    )
    for before, after in edits:
        expected = 2 if before.startswith('folds.add_tail') else 1
        assert source.count(before) == expected, (before, source.count(before))
        source = source.replace(before, after)
    env = dict(original.__globals__)
    exec(compile(source, __file__, 'exec'), env)
    out = combo.xsub.clone(entry, dict(entry.__globals__, synthesize=env['synthesize']))
    assert out.__globals__['convert_safe'] is entry.__globals__['convert_safe']
    assert out.__globals__['baseline'] is entry.__globals__['baseline']
    return out


decode = install(combo.decode)
