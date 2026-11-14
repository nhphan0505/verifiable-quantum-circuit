"""Use the same installed chart owner for all nine homogeneous nodes.

The supplied dispatcher used its replay_erase owner only at gi8 and its
chart_chain owner at gi9..16. Here gi8 uses that dispatcher's own installed
chart_chain as well. This preserves each dispatcher's arithmetic ownership;
it does not select an arbitrary function found first by a graph walk.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import decode_character as prior
import walk_bound as walk
body=prior.body


def use_chart_owner(b,words,gi,reverse=False,token=None,normalizer=None):
    return chart_chain(b,words,gi,reverse,token,normalizer)


DISPATCH_EDITS={}
for fn in walk.functions(body.__globals__['extraction']):
    if fn.__name__=='external_node_chain' and {'chart_chain','replay_erase'}<=set(fn.__code__.co_names):
        assert fn.__closure__ is None
        key=(fn.__code__.co_filename,fn.__code__.co_firstlineno,
             fn.__globals__['chart_chain'].__code__.co_filename)
        DISPATCH_EDITS[key]=DISPATCH_EDITS.get(key,0)+1
        fn.__code__=use_chart_owner.__code__
assert DISPATCH_EDITS
del fn,key


def decode(b,S,E):return body(b,S,E)
