"""A10 companion installed separately in each actual base node owner.

This installer edits only private Python function objects in its isolated
imported decoder graph. It preserves every owner's original forward and
arithmetic scope, and avoids copying the entire historical graph again.
A03 exact convolution tensors are composed in the converter only.
"""
from pathlib import Path
from types import FunctionType
from functools import lru_cache
import ast
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'exp/new/root'),str(ROOT/'exp/new/a01'),str(ROOT/'exp/new/a10'),str(ROOT/'exp/new/a03')]
import fast_base
import exact_subs as xs
import frozen_chart as frozen
from replay_erase import scalar_erase_second24
import walk_bound as walk
import lowclean_shared as lowclean
from install_thickening import install as install_thickening


@lru_cache(None)
def compiled_definition(path,name):
    tree=ast.parse(Path(path).read_text())
    node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
    return compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec')


def definition(path,name,scope):
    exec(compiled_definition(str(path),name),scope)
    return scope[name]


source_path=ROOT/'exp/new/a01/companion.py'
tree=ast.parse(source_path.read_text())
node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='external_node_chain')
source=ast.get_source_segment(source_path.read_text(),node)
start=source.index("    with b.mark('companion_normalize'):")
stop=source.index('    b.cswap(pole, N, D)',start)
source=source[:start]+'''    with b.mark('companion_normalize'):
        norm, F = normalize_three(b,N,D,L,R)
    with b.mark('companion_fused_chart'):
        original = finish_fused(b,D,F,token['norm'],norm,N,L,R,heads[0],gn['c'])
'''+source[stop:]
prototype_scope={}
exec(compile(source,__file__,'exec'),prototype_scope)
prototype=prototype_scope['external_node_chain']
entry=fast_base.decode
original=entry.__globals__['extraction']
functions=walk.functions(original)
groups={}
for fn in functions:
    if fn.__name__=='external_node_chain' and 'normalize_early' in fn.__code__.co_names:
        groups.setdefault(id(fn.__globals__),[]).append(fn)
OWNER_LOG=[]
for members in groups.values():
    first=members[0]
    assert all(fn.__closure__ is None and fn.__code__ is first.__code__ for fn in members)
    scope=first.__globals__
    original_scope=dict(scope)
    forward=xs.clone(first,original_scope)
    ng=dict(scope['normalize_early'].__globals__,lowclean=lowclean)
    fg=dict(scope['direct_chart'].__globals__,lowclean=lowclean,frozen=frozen,
            correct_subfield=ng['correct_subfield'])
    scope.update(forward_original=forward,SELECT=frozenset(range(8,17)),
        normalize_three=definition(ROOT/'exp/new/a10/decode_partial_divide.py','normalize_first_half',ng),
        finish_fused=definition(ROOT/'exp/new/a10/decode_partial_chart.py','finish_partial_chart',fg),
        scalar_erase_second24=scalar_erase_second24)
    OWNER_LOG.append((first.__code__.co_filename,first.__code__.co_firstlineno,
        scope['normalize_early'].__code__.co_filename,
        scope['direct_chart'].__code__.co_filename,len(members)))
    for fn in members:fn.__code__=prototype.__code__
assert OWNER_LOG
# Stop the walk result retaining unrelated historical objects while the
# converter installer creates its own exact private graph.
del functions,groups,members,first,forward,original_scope,scope,ng,fg
scope=dict(entry.__globals__,convert_safe=install_thickening(entry.__globals__['convert_safe']))
body=xs.clone(entry,scope)
# These construction-only roots can retain historical module graphs.
del entry,original,fn,scope,source_path,tree,node,source,prototype_scope,prototype


def decode(b,S,E):return body(b,S,E)
