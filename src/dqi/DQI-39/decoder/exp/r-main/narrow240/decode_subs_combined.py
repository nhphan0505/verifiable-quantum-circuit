"""Exact substitutions plus retained zero-cost early replay erasure and entry CNOTs."""
from pathlib import Path
import sys, inspect
sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_subs import *

def edited(fn, old, new, extra=None):
    source=inspect.getsource(fn)
    assert source.count(old)==1, (fn.__name__, source.count(old))
    env=dict(fn.__globals__)
    if extra: env.update(extra)
    exec(compile(source.replace(old,new),fn.__code__.co_filename,'exec'),env)
    return env[fn.__name__]

terminal=edited(xsub.terminal_two_phase,
    "        external_scalar_step(b, heads[i], N, D, params[i][0], ct, True, first=i == 0)",
    "        if i == 1: scalar_erase_second24(b, heads[i], N, D, params[i][0], ct, params[0][0])\n        else: external_scalar_step(b, heads[i], N, D, params[i][0], ct, True, first=i == 0)",
    dict(scalar_erase_second24=base.replay_erase.scalar_erase_second24))
original_node=xsub.clone(xsub.external_node_chain,
    dict(xsub.external_node_chain.__globals__,terminal_two_phase=terminal))
chart_node=edited(base.chart_chain,
    'D=b.alloc_qubits(24);b.x(D[0]);b.cswap(pole,N,D)',
    'D=b.alloc_qubits(24);b.x(D[0]);b.cx(pole,N[0]);b.cx(pole,D[0])')
replacements=dict(replacements)
replacements.update({
    id(base.replay_erase.external_node_chain):xsub.private_rebind(original_node,replacements),
    id(base.chart_chain):xsub.private_rebind(chart_node,replacements),
})
decode=xsub.private_rebind(base.decode,replacements)
trailing=edited(decode.__globals__['extraction'],
    'D=b.alloc_qubits(12);b.x(D[0]);b.cswap(pole,N,D)',
    'D=b.alloc_qubits(12);b.x(D[0]);b.cx(pole,N[0]);b.cx(pole,D[0])')
decode=xsub.clone(decode,dict(decode.__globals__,extraction=trailing))
