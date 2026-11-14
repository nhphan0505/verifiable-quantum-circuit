"""Single gauge character with the actual existing companion return.

The captured finish_fused already restores D to the selected forward gauge.
Run its exact reverse cleanup with absent old chart characters represented
by explicit zero classical masks, then pay the one new gauge character.
The companion and its scalar return remain present and fully charged.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/new/a01')]
from direct_normalization import forward_node
from walk_bound import functions


def finish_with_gauge(original):
    def finish(b,D,F,forward,reverse,N,L,R,head,ct):
        if 'gauge' not in forward:return original(b,D,F,forward,reverse,N,L,R,head,ct)
        zero={}
        for key,n in [('g',12),('i',12),('h',12),('t',12),('r',12),('f',1)]:
            m=b.alloc_bits(n);b.bit_store(m,False);zero[key]=m
        result=original(b,D,F,zero,reverse,N,L,R,head,ct)
        b.cz(D,forward['gauge']);b.free(forward['gauge'])
        return result
    return finish


def install(entry):
    seen=set();log=[]
    for fn in functions(entry):
        g=fn.__globals__
        if fn.__name__!='external_node_chain' or 'finish_fused' not in fn.__code__.co_names:continue
        if id(g)in seen:continue
        seen.add(id(g))
        old_forward=g['forward_original'];reference=g['ref']
        selection=frozenset(g.get('SELECT',range(8,17)))
        def router(b,words,gi,reverse=False,token=None,normalizer=None,
                   _original=old_forward,_reference=reference,_select=selection):
            if not reverse and gi in _select:return forward_node(b,words,gi,_reference)
            return _original(b,words,gi,reverse,token,normalizer)
        old_finish=g['finish_fused']
        g['forward_original']=router;g['finish_fused']=finish_with_gauge(old_finish)
        log.append(dict(file=fn.__code__.co_filename,line=fn.__code__.co_firstlineno,select=sorted(selection),
                        finish_file=old_finish.__code__.co_filename,finish_line=old_finish.__code__.co_firstlineno))
    assert log
    return log
