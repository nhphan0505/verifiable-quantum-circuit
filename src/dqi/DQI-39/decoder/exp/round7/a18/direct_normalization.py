"""Change the forward transcript to one measured actual gauge.

The actual forward chain and normalized values are preserved. Both payloads
are divided by the selected nonzero gauge with a fully closed shared norm
schedule; the gauge itself is X-erased and paid when the new return restores
it. No six-chart-character reconstruction is needed for this transcript.
"""
from pathlib import Path
from types import FunctionType,SimpleNamespace
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/round7/a09'),str(ROOT/'exp/round7/a02')]
from column_double_tail import *
from narrow_gauge import divide_pair,divide_pair_and_invert as old_divide
from exp.arithmetic.division import zero_flag
import consumer_top_block
from projective_top_block import ProjectiveTopOverlap


def forward_node(b,words,gi,reference=old):
    spec=reference.groups[gi]
    N=combine(words[spec['word']:spec['word']+2]);L=combine(words[spec['word']+2:spec['word']+4])
    heads=[words[2*i:2*i+2]for i in range(2*gi)]
    D=b.alloc_qubits(24);b.x(D[0]);corr=0
    for i,head in enumerate(heads):
        q=reference.ks[i]^spec['kap']
        reference.external_chain_step(b,head,N,D,L,q,spec['c'],corr,first=i==0)
        corr^=inv(q)
    assert corr==0
    pole=zero_flag(b,D);b.cswap(pole,N,D)
    reference.external_square24(b,L,True)
    with b.mark('direct_forward_normalization'):divide_pair(b,[N,L],D)
    reference.external_square24(b,L)
    mask=b.alloc_bits(24);b.hmr(D,mask);b.free(D)
    return dict(pole=pole,norm=dict(gauge=mask))


def divide_new_token(b,targets,source,token=None):
    if token is None or 'gauge' not in token:
        return old_divide(b,targets,source,token)
    old_divide(b,targets,source,None)
    b.cz(source,token['gauge']);b.free(token['gauge'])


def make_projective_return():
    fn=consumer_top_block.make_return
    scope=dict(fn.__globals__,divide_pair_and_invert=divide_new_token)
    maker=FunctionType(fn.__code__,scope,fn.__name__,fn.__defaults__,fn.__closure__)
    return maker(source_type=ProjectiveTopOverlap)


def make_column_return():
    import column_double_tail as module
    fn=module.return_node
    scope=dict(fn.__globals__,divide_pair_and_invert=divide_new_token)
    result=FunctionType(fn.__code__,scope,fn.__name__,fn.__defaults__,fn.__closure__)
    return result,SimpleNamespace(state=None)


def install(entry,return_node):
    from install_column import install as install_return,functions
    log=install_return(entry,narrow='tokenfused');seen=set()
    for fn in functions(entry):
        scope=fn.__globals__
        if '_a02_return' not in scope or id(scope)in seen:continue
        seen.add(id(scope));scope['_a02_return']=return_node
        original=scope['_a02_original'];reference=scope['ref'];selection=scope['_a02_select']
        def router(b,words,gi,reverse=False,token=None,normalizer=None,
                   _original=original,_reference=reference,_select=selection):
            if not reverse and gi in _select:return forward_node(b,words,gi,_reference)
            return _original(b,words,gi,reverse,token,normalizer)
        scope['_a02_original']=router
    return log
