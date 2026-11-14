"""Exact companion subset / arithmetic width-selector experiment.

Only fixed node indices and resource ceilings are changed at import time.
The unchanged captured original return handles all unselected nodes.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'exp/new/a01')]
import decode_best as base
import walk_bound as walk


def install(max_gi,ceiling):
    entries=[];owners=set();codes={};edits=[]
    for fn in walk.functions(base.decode):
        code=fn.__code__;scope=fn.__globals__
        if fn.__name__=='external_node_chain' and {'normalize_three','forward_original'}<=set(code.co_names):
            if id(scope) not in owners:
                owners.add(id(scope));scope['SELECT']=frozenset(range(8,max_gi+1))
                entries.append((code.co_filename,code.co_firstlineno))
        if 'num_allocated_qubits' not in code.co_names:continue
        if any(type(c)is int and c in (889,900) for c in code.co_consts):
            if code not in codes:
                codes[code]=code.replace(co_consts=tuple(ceiling if type(c)is int and c in (889,900) else c for c in code.co_consts))
            fn.__code__=codes[code];edits.append((code.co_filename,code.co_firstlineno,'constant'))
        for name,cell in zip(code.co_freevars,fn.__closure__ or ()):
            if name=='ceiling' and cell.cell_contents in (889,900):
                cell.cell_contents=ceiling;edits.append((code.co_filename,code.co_firstlineno,'closure'))
        if fn.__defaults__ and 'ceiling' in code.co_varnames[:code.co_argcount]:
            fn.__defaults__=tuple(ceiling if type(c)is int and c in (889,900) else c for c in fn.__defaults__)
    assert entries
    return base.decode,dict(owners=entries,ceiling=ceiling,selector_edits=edits)
