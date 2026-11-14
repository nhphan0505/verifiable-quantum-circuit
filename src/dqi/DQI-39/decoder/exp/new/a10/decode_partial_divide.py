"""Early half retirement using direct source-preserving division."""
from pathlib import Path
import inspect
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import decode_partial as prior
import lowclean_bidirectional as lowclean
from companion import xs
import walk_bound as walk


def normalize_first_half(b,N,D,L,R):
    r,g=D[:12],D[12:]
    F=b.alloc_qubits(1)[0];lowclean.zero_toggle(b,g,F,r);b.cswap(F,r,g)
    with lowclean.source(b,g,True) as apply:
        apply([r])
        correct_subfield(b,N,F);ar.mul_xor0(b,r,N[12:],N[:12])
        apply([N[12:]])
    return None,F


entry=prior.body
original=entry.__globals__['extraction']
nodes=[fn for fn in walk.functions(original)
       if fn.__name__=='external_node_chain' and 'finish_fused' in fn.__code__.co_names
       and 'forward_original' in fn.__globals__]
assert nodes
scope=dict(nodes[0].__globals__)
scope['normalize_three']=xs.clone(normalize_first_half,dict(scope['normalize_three'].__globals__,lowclean=lowclean))
src=inspect.getsource(prior.finish_partial)
old='''    # g is still inverse(g_raw). Its phase-clean inversion can wait until
    # these twelve companion wires are available for ordinary arithmetic.
    closed_inverse(b,g)
'''
assert src.count(old)==1
fg=dict(scope['finish_fused'].__globals__,lowclean=lowclean)
exec(compile(src.replace(old,''),__file__,'exec'),fg)
scope['finish_fused']=fg['finish_partial']
node=xs.clone(nodes[0],scope)
body=xs.clone(entry,dict(entry.__globals__,extraction=xs.private_rebind(original,
    {id(fn):node for fn in nodes})))

def decode(b,S,E):
    return body(b,S,E)
