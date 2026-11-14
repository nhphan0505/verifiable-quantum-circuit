"""Replace the entire reverse chart normalizer with one shared norm bank.

Three payloads and the reciprocal gauge are returned together. This first
complete schedule keeps all source and erasure costs and deliberately
exposes the width cost before attempting early numerator retirement.
"""
from types import FunctionType
from direct_owned_companion import clone,forward_owner
from direct_deferred_companion import normalize_with_token,node_context
from narrow_gauge import divide_pair_and_invert
from walk_bound import functions


def normalize_factory(reference):
    def normalize(b,N,D,L,R):
        reference.external_square24(b,L,True)
        with b.mark('shared_reverse_norm'):
            divide_pair_and_invert(b,[N,L,R],D)
        reference.external_square24(b,L)
        return 'a18_shared_norm',None
    return normalize


def finish_factory(reference,scope):
    cx=scope['cx'];combine=scope['combine']
    def finish(b,D,F,forward,reverse,N,L,R,head,ct):
        assert reverse=='a18_shared_norm' and F is None
        b.cz(D,forward['gauge']);b.free(forward['gauge'])
        a,h=head;cx(b,h,a,ct);b.cx(combine(head),N);cx(b,h,a,ct)
        b.cx(h,L[:12])
        original=b.alloc_bits(24);b.hmr(N,original)
        b.swap(N,R);b.free(R)
        return original
    return finish


def install(entry):
    seen=set();log=[]
    for fn in functions(entry):
        g=fn.__globals__
        if fn.__name__!='external_node_chain'or'finish_fused'not in fn.__code__.co_names:continue
        if id(g)in seen:continue
        seen.add(id(g));assert not fn.__closure__
        original=clone(fn,g);old_forward=g['forward_original'];selection=frozenset(g.get('SELECT',range(8,17)))
        new_forward=forward_owner(old_forward);reference=g['ref']
        def router(b,words,gi,reverse=False,token=None,normalizer=None,
                   _original=old_forward,_forward=new_forward,_select=selection):
            if not reverse and gi in _select:return _forward(b,words,gi,False,token,normalizer)
            return _original(b,words,gi,reverse,token,normalizer)
        context=dict(stack=[])
        g['forward_original']=router;g['finish_fused']=finish_factory(reference,g)
        g['normalize_three']=normalize_with_token(normalize_factory(reference),context)
        g.update(_a18_deferred_select=selection,_a18_deferred_context=context,_a18_deferred_original=original)
        fn.__code__=node_context.__code__
        log.append(dict(file=original.__code__.co_filename,select=sorted(selection)))
    assert log
    return log
