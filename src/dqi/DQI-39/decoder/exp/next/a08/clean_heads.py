"""Close every final scalar-head forward using its actual involutive return.

The node map and its matched return are unchanged.  This installer changes
only the forward scalar inversion call and supplies its exact zero token.
"""
from pathlib import Path
from types import FunctionType
import ast
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'exp/new/a01'))


def zero_mask(b):
    out=b.alloc_bits(24)
    b.bit_store(out,False)
    return out


def make_closed(reverse_early,reverse_late=None):
    def closed(b,x,gi,K=None):
        inverse=reverse_late if reverse_late is not None and gi>=15 else reverse_early
        inverse(b,x,zero_mask(b),K)
        return zero_mask(b)
    return closed


def _prototype(late):
    path=ROOT/'playbook/kit/decoder/final_decoder/decode.py'
    source=path.read_text()
    tree=ast.parse(source)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='external_extraction')
    fragment=ast.get_source_segment(source,node)
    old='local=inverse24_forward190(b,v,K)'
    assert fragment.count(old)==1
    fragment=fragment.replace(old,'local=_closed_head_inverse(b,v,gi,K)')
    if late:
        old='inverse24_reverse209(b,v,local,K)'
        assert fragment.count(old)==1
        fragment=fragment.replace(old,'(inverse24_reverse19 if gi>=15 else inverse24_reverse209)(b,v,local,K)')
    scope={}
    exec(compile(fragment,__file__,'exec'),scope)
    return scope['external_extraction'].__code__


def install(entry):
    from walk_bound import functions
    log=[]
    for fn in functions(entry):
        if fn.__name__!='external_extraction':
            continue
        if '_closed_head_inverse' in fn.__code__.co_names:
            assert '_closed_head_inverse' in fn.__globals__
            log.append(dict(file=fn.__code__.co_filename,line=fn.__code__.co_firstlineno,
                            already_installed=True))
            continue
        if 'inverse24_forward190' not in fn.__code__.co_names:
            continue
        scope=fn.__globals__
        assert fn.__closure__ is None
        assert 'inverse24_reverse209' in scope
        early=scope['inverse24_reverse209']
        late=scope.get('inverse24_reverse19') if 'inverse24_reverse19' in fn.__code__.co_names else None
        scope['_closed_head_inverse']=make_closed(early,late)
        log.append(dict(file=fn.__code__.co_filename,line=fn.__code__.co_firstlineno,
                        early=early.__code__.co_filename,
                        late=late.__code__.co_filename if late else None))
        fn.__code__=_prototype(late is not None)
    assert log
    return log
