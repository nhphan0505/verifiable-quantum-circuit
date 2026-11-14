"""Absorb the odd prefix update into the full polynomial fold.

At an odd fold, p_after=p_before+h*Q.  The old projected product adds
h*Q to the two top stored coordinates, and its alias then adds p_after
there.  These cancel to p_before.  A full fold performs that update and
the p update in one polynomial product, retaining the same zero alias.
"""
from pathlib import Path
import inspect
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'exp/r-main/narrow240'))
import decode_combo as combo


def install(entry, prefix_gauge=False):
    original = entry.__globals__['synthesize']
    source = inspect.getsource(combo.decode.__globals__['synthesize'])
    old = '''        if i%2:
            ar.mul_xor0(b,heads[i][1],r,border);qi,p=r,border
            A,B,t=folds.sg['absorb'](b,heads[i],A,B,qi,p,None,0,cs[i],ks[i],wide=False)
        else:
            qi,p=border,r
            A,B,t=folds.sg['absorb_even'](b,heads[i],A,B,qi,r,cs[i],ks[i])'''
    new = '''        qi,p=(r,border) if i%2 else (border,r)
        A,B,t=folds.sg['absorb_even'](b,heads[i],A,B,qi,p,cs[i],ks[i])'''
    assert source.count(old) == 1
    source = source.replace(old, new)
    old = '''            if i%2:
                folds.ug['absorb'](b,heads[i],aa,bb,qi,p,None,0,cs[i],ks[i],True,t,False)
                ar.mul_xor0(b,heads[i][1],r,border)
            else:folds.ug['absorb_even'](b,heads[i],aa,bb,qi,r,cs[i],ks[i],True,t)'''
    new = '''            folds.ug['absorb_even'](b,heads[i],aa,bb,qi,p,cs[i],ks[i],True,t)'''
    assert source.count(old) == 1
    source = source.replace(old, new)
    if prefix_gauge:
        edits = (
            ('b.cx(border,r);b.cx(border,d);b.cx(r,border);b.x(border[0])',
             'b.cx(border,r);b.cx(r,border);b.x(border[0])'),
            ('folds.add_tail(b,heads[i],qi,d,bool(i%2))',
             'folds.add_tail(b,heads[i],qi,d,not bool(i%2))'),
            ('ar.mul_xor0(b,r,border,d);tt=tail_inplace', 'tt=tail_inplace'),
            ('tail_inplace(b,r,border,d,u,v,pole,True,tt);ar.mul_xor0(b,r,border,d)',
             'tail_inplace(b,r,border,d,u,v,pole,True,tt)'),
            ('b.cx(r,d);b.x(border[0]);b.cx(r,border);b.cx(border,r);b.free(r)',
             'b.x(border[0]);b.cx(r,border);b.cx(border,r);b.free(r)'),
        )
        for before, after in edits:
            assert before in source
            source = source.replace(before, after)
    environment = dict(original.__globals__)
    exec(compile(source, __file__, 'exec'), environment)
    return combo.xsub.clone(entry, dict(entry.__globals__, synthesize=environment['synthesize']))


decode = install(combo.decode)
