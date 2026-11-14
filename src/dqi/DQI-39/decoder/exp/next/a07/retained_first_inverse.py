"""Retain the first reciprocal across normalization's three target scales.

The old second consuming-inverse mask denotes inv0(g).  Measuring the
initialized reciprocal gives exactly the same token character, while g
remains in its original value throughout.  The selected g is nonzero.
"""
from pathlib import Path
import ast
from types import FunctionType


def initialized_inverse12(b, g):
    from exp.jet24.pro_jet import cached_inverse, PLAN12
    gi, F = cached_inverse(b, g, PLAN12, True)
    # The homogeneous pair is nonzero and its selected subfield component
    # is nonzero.  F is therefore identically zero on this interface.
    b.free(F)
    return gi


def rewrite(original, pairs=('first',), ceiling=None):
    """Rebuild just the matching function, retaining its private helpers."""
    path=Path(original.__code__.co_filename)
    text=path.read_text()
    tree=ast.parse(text)
    node=next((x for x in tree.body if isinstance(x,ast.FunctionDef)
               and x.name==original.__name__),None)
    if node is None:
        # normalize_early is generated from this literal definition.
        if original.__name__ not in ('normalize_early','normalize_retained'):
            return None
        frozen=path.with_name('frozen_chart.py').read_text()
        tree=ast.parse(frozen)
        node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='normalize')
        text=frozen
        source=ast.get_source_segment(text,node)
        source=source.replace('def normalize(', 'def '+original.__name__+'(')
        start=source.index(' rm=b.alloc_bits(12);gg=')
        source=source[:start]+" return dict(g=gm,i=im,h=hm,t=tm),F\n"
        if original.__name__=='normalize_early':
            lo=source.index(' tm=inverse_stream_noscratch')
            hi=source.index(' b.x(r[0]);b.cx(F,r[0])',lo)
            source=source[:lo]+source[hi:]
            source=source.replace('return dict(g=gm,i=im,h=hm,t=tm),F',
                                  'return dict(g=gm,i=im,h=hm,half=half_masks),F')
    else:
        source=ast.get_source_segment(text,node)
    if 'oldg=inverse_stream_noscratch(b,g)' not in source:
        return None
    if 'first' in pairs:
        assert source.count('oldg=inverse_stream_noscratch(b,g)')==1
        source=source.replace('oldg=inverse_stream_noscratch(b,g)',
                              'gi=initialized_inverse12(b,g)')
        source=source.replace('olda=scale_defer(b,r,g)', 'olda=scale_defer(b,r,gi)')
        source=source.replace('half_masks=[scale_defer(b,x[12:],g)for x in (N,L)]',
                              'half_masks=[scale_defer(b,x[12:],gi)for x in (N,L)]',1)
        old='im=inverse_stream_noscratch(b,g) # g restored\n b.cz(g,oldg);b.free(oldg)'
        new='im=b.alloc_bits(12);b.hmr(gi,im);b.free(gi)'
        assert source.count(old)==1,original.__name__
        source=source.replace(old,new)
    if 'second' in pairs and 'tm=inverse_stream_noscratch(b,g)' in source:
        old='hm=inverse_stream_noscratch(b,g) # t=1/(g*q)'
        new='gi2=initialized_inverse12(b,g);hm=b.alloc_bits(12);b.bit_store(hm,False)'
        assert source.count(old)==1,original.__name__
        source=source.replace(old,new)
        source=source.replace('half_masks=[scale_defer(b,x[:12],g)for x in (N,L)]',
                              'half_masks=[scale_defer(b,x[:12],gi2)for x in (N,L)]')
        source=source.replace('tm=inverse_stream_noscratch(b,g) # g*q restored',
                              'tm=b.alloc_bits(12);b.hmr(gi2,tm);b.free(gi2)')
    scope=dict(original.__globals__,initialized_inverse12=initialized_inverse12)
    if ceiling is not None:
        # This limits the retained schedule's extra width.  The caller must
        # also ensure its existing fallback fits the desired global cap.
        # Entry + outer chart flag + reciprocal + scale output = entry+25.
        fallback_name='_a07_unretained_'+original.__name__
        fallback=FunctionType(original.__code__,dict(original.__globals__),
                              original.__name__,original.__defaults__,original.__closure__)
        fallback.__kwdefaults__=original.__kwdefaults__
        scope[fallback_name]=fallback
        split=source.index('\n')+1
        source=source[:split]+(
            ' if b.num_allocated_qubits + 25 > '+str(int(ceiling))+':\n'
            '  return '+fallback_name+'(b,N,D,L)\n')+source[split:]
    exec(compile(source,__file__,'exec'),scope)
    return scope[original.__name__]


def install(entry, pairs=('first',), ceiling=None):
    from walk_bound import functions
    changed=[]
    for fn in functions(entry):
        if fn.__name__ not in ('normalize','normalize_early','normalize_retained'):
            continue
        if 'oldg' not in fn.__code__.co_varnames:
            continue
        replacement=rewrite(fn,pairs,ceiling)
        if replacement is None:continue
        # The replacement introduces one helper; preserve the function's
        # private scope and exact ownership of every other arithmetic call.
        fn.__globals__['initialized_inverse12']=initialized_inverse12
        if ceiling is not None:
            key='_a07_unretained_'+fn.__name__
            fn.__globals__[key]=replacement.__globals__[key]
        fn.__code__=replacement.__code__
        changed.append((fn.__name__,fn.__code__.co_filename,fn.__code__.co_firstlineno))
    assert changed
    return changed
