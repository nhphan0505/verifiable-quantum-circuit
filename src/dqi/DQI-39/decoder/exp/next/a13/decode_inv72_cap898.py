"""Whole candidate: one completed flag-free GF12 source at Q898 target.

Not measured until the unchanged checker prints whole resources.
The expensive completed source is selected only at static live count897.
"""
from pathlib import Path
from types import FunctionType
import ast,sys
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(ROOT),str(H),str(ROOT/'exp/next/a01'),
             str(ROOT/'exp/next/a04'),str(ROOT/'exp/next/a05'),
             str(ROOT/'exp/next/a07'),str(ROOT/'exp/new/a01'),
             str(ROOT/'exp/new/root'),str(ROOT/'exp/new/a18')]
import dispatch
decode,DISPATCH_LOG=dispatch.install(16,892)
from retained_first_inverse import install
NORMALIZER_LOG=install(decode,pairs=('first','second'),ceiling=892)
import log_source_cap898 as arithmetic
import no_clean_source12_inv72 as borrowed_source
import walk_bound as walk

def definition(path,name,scope):
    node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope)
    return scope[name]

def wrappers(old_normalize,old_finish):
    low_scope=dict(old_normalize.__globals__,lowclean=arithmetic)
    fallback=FunctionType(old_normalize.__code__,low_scope,old_normalize.__name__,old_normalize.__defaults__,old_normalize.__closure__)
    fallback.__kwdefaults__=old_normalize.__kwdefaults__
    high=definition(H/'normalize_borrowed.py','normalize_first_half',dict(low_scope,borrowed_source=borrowed_source))
    finish=definition(ROOT/'exp/next/a01/finish_defer_ratio.py','finish_partial_chart',dict(old_finish.__globals__))
    def normalize_first_half(b,N,D,L,R):
        if b.num_allocated_qubits>=891:return high(b,N,D,L,R)
        return fallback(b,N,D,L,R)
    def finish_partial_chart(b,D,F,forward,unused,N,L,R,head,ct):
        target=finish if unused=='a13_defer' else old_finish
        return target(b,D,F,forward,unused,N,L,R,head,ct)
    return normalize_first_half,finish_partial_chart

INSTALLED=[];seen=set()
for fn in walk.functions(decode):
    scope=fn.__globals__
    if fn.__name__!='external_node_chain' or 'finish_fused' not in fn.__code__.co_names or id(scope) in seen:continue
    seen.add(id(scope))
    scope['normalize_three'],scope['finish_fused']=wrappers(scope['normalize_three'],scope['finish_fused'])
    INSTALLED.append((fn.__code__.co_filename,fn.__code__.co_firstlineno))
assert INSTALLED
from install_consume_ceiling import install as install_ceiling
CEILING_LOG=install_ceiling(decode,892)
del fn,scope,seen
