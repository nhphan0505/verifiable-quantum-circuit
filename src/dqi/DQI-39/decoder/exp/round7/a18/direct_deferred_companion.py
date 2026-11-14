"""Also defer the inverse-norm character to the held reciprocal gauge.

At entry to the existing companion normalizer D=1/C. Thus Norm(D) is the
same1/Norm(C) that the new forward measured, and its character is quadratic.
"""
from pathlib import Path
from types import FunctionType
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/new/a01')]
from direct_normalization import *
from direct_companion import finish_with_gauge
from walk_bound import functions
from exp.noscratch.schedules import norm_xor_noscratch,inverse_stream_noscratch
from exp.mul99.schedules import multiply_forward99
from exp.arithmetic.division import phase_product24
from exp.decoder.common import ar


def normalize_deferred(b,N,D,L,reference=old):
    reference.external_square24(b,L,True)
    b.cx(D[12:],D[:12]);masks=[multiply_forward99(b,x,D,K)for x in(N,L)];b.cx(D[12:],D[:12])
    reciprocal=b.alloc_qubits(12);norm_xor_noscratch(b,D,reciprocal,K)
    nm=inverse_stream_noscratch(b,reciprocal);ar._phase_norm(b,D,nm,K);b.free(nm)
    halves=[]
    for x in(N,L):
        for off in(0,12):
            v=x[off:off+12];out=b.alloc_qubits(12);ar.mul_xor0(b,v,reciprocal,out)
            m=b.alloc_bits(12);b.hmr(v,m);b.swap(v,out);b.free(out);halves.append((v,m))
    im=b.alloc_bits(12);b.hmr(reciprocal,im);b.free(reciprocal)
    norm=b.alloc_qubits(12);norm_xor_noscratch(b,D,norm,K)
    for v,m in halves:ar.phase_product(b,v,norm,m);b.free(m)
    ar._erase_norm(b,D,norm,K);b.free(norm)
    for x,m in zip((N,L),masks):phase_product24(b,x,D,m,K);b.free(m)
    reference.external_square24(b,L)
    gauge=b.alloc_bits(24);b.hmr(D,gauge);b.free(D)
    return dict(gauge=gauge,inv_norm=im)


def forward_deferred(b,words,gi,reference=old):
    spec=reference.groups[gi]
    N=combine(words[spec['word']:spec['word']+2]);L=combine(words[spec['word']+2:spec['word']+4])
    heads=[words[2*i:2*i+2]for i in range(2*gi)]
    D=b.alloc_qubits(24);b.x(D[0]);corr=0
    for i,head in enumerate(heads):
        q=reference.ks[i]^spec['kap']
        reference.external_chain_step(b,head,N,D,L,q,spec['c'],corr,first=i==0);corr^=inv(q)
    assert corr==0
    pole=zero_flag(b,D);b.cswap(pole,N,D)
    with b.mark('deferred_forward_normalization'):token=normalize_deferred(b,N,D,L,reference)
    return dict(pole=pole,norm=token)


def normalize_with_token(original,context):
    def normalize(b,N,D,L,R):
        token=context['stack'][-1]['norm']
        mask=token.pop('inv_norm')
        ar._phase_norm(b,D,mask,K);b.free(mask)
        return original(b,N,D,L,R)
    return normalize


def node_context(b,words,gi,reverse=False,token=None,normalizer=None):
    active=reverse and gi in _a18_deferred_select
    if active:_a18_deferred_context['stack'].append(token)
    try:return _a18_deferred_original(b,words,gi,reverse,token,normalizer)
    finally:
        if active:assert _a18_deferred_context['stack'].pop()is token


def install(entry):
    seen=set();log=[]
    for fn in functions(entry):
        g=fn.__globals__
        if fn.__name__!='external_node_chain'or'finish_fused'not in fn.__code__.co_names:continue
        if id(g)in seen:continue
        seen.add(id(g));assert not fn.__closure__
        original=FunctionType(fn.__code__,g,fn.__name__,fn.__defaults__,fn.__closure__)
        original.__kwdefaults__=fn.__kwdefaults__
        old_forward=g['forward_original'];reference=g['ref'];selection=frozenset(g.get('SELECT',range(8,17)))
        def router(b,words,gi,reverse=False,token=None,normalizer=None,
                   _original=old_forward,_reference=reference,_select=selection):
            if not reverse and gi in _select:return forward_deferred(b,words,gi,_reference)
            return _original(b,words,gi,reverse,token,normalizer)
        context=dict(stack=[])
        g['forward_original']=router;g['finish_fused']=finish_with_gauge(g['finish_fused'])
        g['normalize_three']=normalize_with_token(g['normalize_three'],context)
        g.update(_a18_deferred_select=selection,_a18_deferred_context=context,_a18_deferred_original=original)
        fn.__code__=node_context.__code__
        log.append(dict(file=original.__code__.co_filename,select=sorted(selection)))
    assert log
    return log
