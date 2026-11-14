"""Per-owner retained chart plus exact arithmetic selectors at the same Q900 cap.

Only width-choice guards in existing, exact arithmetic are relaxed. Field
constants, decoder input handling, builder operations and all zero-chart
completions remain unchanged. The whole checker decides the actual peak.
"""
from pathlib import Path
from types import CodeType
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import decode_owner as prior
import walk_bound as walk
body=prior.body
CAP_EDIT_LOG={}
_CODE_REPLACEMENTS={}
for fn in walk.functions(body):
    code=fn.__code__
    if 'num_allocated_qubits' not in code.co_names:
        continue
    edits=[]
    if 889 in code.co_consts:
        if code not in _CODE_REPLACEMENTS:
            _CODE_REPLACEMENTS[code]=code.replace(co_consts=tuple(900 if type(c)is int and c==889 else c for c in code.co_consts))
        fn.__code__=_CODE_REPLACEMENTS[code]
        edits.append('guard constant')
    for name,cell in zip(code.co_freevars,fn.__closure__ or ()):
        if name=='ceiling' and cell.cell_contents==889:
            cell.cell_contents=900
            edits.append('ceiling closure')
    if fn.__defaults__ and 889 in fn.__defaults__ and 'ceiling' in code.co_varnames[:code.co_argcount]:
        fn.__defaults__=tuple(900 if type(c)is int and c==889 else c for c in fn.__defaults__)
        edits.append('ceiling default')
    if edits:
        key=(code.co_filename,code.co_firstlineno,fn.__name__,tuple(edits))
        CAP_EDIT_LOG[key]=CAP_EDIT_LOG.get(key,0)+1
assert CAP_EDIT_LOG
CODE_REPLACEMENT_COUNT=len(_CODE_REPLACEMENTS)
del _CODE_REPLACEMENTS,fn,code,edits
for _temporary in ('name','cell','key'):
    globals().pop(_temporary,None)
del _temporary


def decode(b,S,E):return body(b,S,E)
