"""Whole raw-return join, including original synthesis measurement debt.

The polynomial source zero characters are paid at the corresponding raw
quotient source. Original head characters are paid when the heads return.
The original five-word tail transcript is consumed by tail_join.consume.
Common-q/gap agreement remains a documented, tested completion obligation.
"""
from pathlib import Path
from types import FunctionType
import sys
import tail_join as tail
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(ROOT/'exp/next/a14'),str(ROOT/'exp/round7/a01')]
import raw_pair_head24_erased as raw
from exp.arithmetic.division import phase_zero
from exp.decoder.common import combine,reclaim
from outer_quadratic import apply as outer_quadratic


def clone(fn,**changes):
    out=FunctionType(fn.__code__,dict(fn.__globals__,**changes),fn.__name__,fn.__defaults__,fn.__closure__)
    out.__kwdefaults__=fn.__kwdefaults__
    return out


def closure(fn):
    return dict(zip(fn.__code__.co_freevars,(c.cell_contents for c in fn.__closure__ or ())))


def source_paid_sweep(b,A,B,fold_tokens):
    heads=tail.heads_from_banks(A,B)
    indices={tuple(combine(head)):i for i,head in enumerate(heads)}
    original=raw.closed_scale24
    seen=[]
    def scale(b,x,y,divide=False,k=raw.pivot.__globals__['K']):
        if divide:
            i=indices[tuple(x)];seen.append(i)
            if i in fold_tokens:
                fm=fold_tokens[i][1]
                phase_zero(b,y,fm[0]);b.free(fm)
        return original(b,x,y,divide,k)
    pivot=clone(raw.pivot,closed_scale24=scale)
    bodies=clone(raw.bodies,closed_scale24=scale)
    sweep=clone(raw.sweep,closed_scale24=scale,pivot=pivot,bodies=bodies)
    sweep(b,A,B)
    assert seen==list(range(34)),seen


def consume_synthesis(b,A,B,pole,old_undo):
    cells=closure(old_undo)
    assert {'hist','tt'}<=cells.keys(),cells.keys()
    folds={row[0]:row[-1]for row in cells['hist']}
    assert set(folds)==set(range(1,34)),set(folds)
    with b.mark('outer_quadratic'):
        outer_quadratic(b,A,B,True)
    with b.mark('raw_paired_sweep'):
        source_paid_sweep(b,A,B,folds)
    with b.mark('raw_tail_join'):
        heads,real=tail.consume(b,A,B,pole,cells['tt'],old_undo.__globals__['tail_inplace'])
    with b.mark('old_head_characters'):
        for i,(hm,_)in sorted(folds.items()):
            b.cz(combine(heads[i]),hm);b.free(hm)
    return heads,real


def route_words(b,source_words,target_words):
    """Fixed construction-time handle permutation, without inspecting values."""
    source=[q for w in source_words for q in w];target=[q for w in target_words for q in w]
    source_set=set(source);target_set=set(target)
    missing=[q for q in target if q not in source_set]
    extras=[q for q in source if q not in target_set]
    assert len(missing)==len(extras)
    if missing:reclaim(b,[missing])
    labels={q:q for q in source+missing};places={q:q for q in source+missing}
    for dest,wanted in zip(target,source):
        where=places[wanted]
        if where!=dest:
            old=labels[dest];b.swap(dest,where)
            labels[dest],labels[where]=wanted,old
            places[wanted],places[old]=dest,where
    if extras:b.free(extras)
