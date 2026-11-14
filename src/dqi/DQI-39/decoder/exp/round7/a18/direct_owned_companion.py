"""Replace only the private owner's forward normalization binding.

Preserves its complete forward chain, zero-flag implementation, and all
private arithmetic dispatch, while using the reciprocal-norm transcript.
"""
from types import FunctionType
from direct_deferred_companion import normalize_deferred,normalize_with_token,node_context
from direct_companion import finish_with_gauge
from walk_bound import functions


def clone(fn,scope):
    out=FunctionType(fn.__code__,scope,fn.__name__,fn.__defaults__,fn.__closure__)
    out.__kwdefaults__=fn.__kwdefaults__;return out


def forward_owner(fn):
    """Clone the existing forward-only route down to its normalize call."""
    scope=dict(fn.__globals__)
    if 'normalize' in fn.__code__.co_names:
        reference=scope['ref']
        def normalize(b,N,D,L):
            with b.mark('owned_deferred_forward_normalization'):
                return normalize_deferred(b,N,D,L,reference)
        scope['normalize']=normalize
        return clone(fn,scope)
    for key in ('forward_chain','forward_original'):
        if key in fn.__code__.co_names and key in scope:
            scope[key]=forward_owner(scope[key]);return clone(fn,scope)
    raise AssertionError(('forward normalization owner not found',fn.__code__.co_filename,fn.__code__.co_names))


def install(entry):
    seen=set();log=[]
    for fn in functions(entry):
        g=fn.__globals__
        if fn.__name__!='external_node_chain'or'finish_fused'not in fn.__code__.co_names:continue
        if id(g)in seen:continue
        seen.add(id(g));assert not fn.__closure__
        original=clone(fn,g);old_forward=g['forward_original'];selection=frozenset(g.get('SELECT',range(8,17)))
        new_forward=forward_owner(old_forward)
        def router(b,words,gi,reverse=False,token=None,normalizer=None,
                   _original=old_forward,_forward=new_forward,_select=selection):
            if not reverse and gi in _select:return _forward(b,words,gi,False,token,normalizer)
            return _original(b,words,gi,reverse,token,normalizer)
        context=dict(stack=[])
        g['forward_original']=router;g['finish_fused']=finish_with_gauge(g['finish_fused'])
        g['normalize_three']=normalize_with_token(g['normalize_three'],context)
        g.update(_a18_deferred_select=selection,_a18_deferred_context=context,_a18_deferred_original=original)
        fn.__code__=node_context.__code__
        log.append(dict(file=original.__code__.co_filename,select=sorted(selection),forward=old_forward.__code__.co_filename))
    assert log
    return log
