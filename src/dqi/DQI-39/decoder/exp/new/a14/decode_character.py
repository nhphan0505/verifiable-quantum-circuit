"""Per-owner A10/A03 companion with one reciprocal-character closure.

Keeps the denominator chart's t=1/(g*q) through old-numerator retirement.
The first old-product and old-denominator masks are paid by one exact
inverse character, replacing the t -> 1/t -> t replay. Other changes and
arithmetic selectors are inherited from decode_owner_cap900.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import decode_owner_cap900 as prior
import decode_owner as owner
import walk_bound as walk
body=prior.body
CHANGED={}
seen=set()
for fn in walk.functions(body.__globals__['extraction']):
    if fn.__name__!='external_node_chain' or 'finish_fused' not in fn.__code__.co_names:
        continue
    scope=fn.__globals__
    if id(scope) in seen:continue
    seen.add(id(scope))
    old=scope['finish_fused']
    scope['finish_fused']=owner.definition(HERE/'finish_character.py','finish_partial_chart',dict(old.__globals__))
    key=(fn.__code__.co_filename,fn.__code__.co_firstlineno)
    CHANGED[key]=CHANGED.get(key,0)+1
assert CHANGED
del fn,scope,old,seen,key


def decode(b,S,E):return body(b,S,E)
