"""Use the seven-fresh19 inverse only inside proved-nonzero streams."""
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/'a14'),str(HERE.parent/'a04')]
import decode_inverse20_12 as generic
import nonzero_consume16 as nonzero

PLAN=json.loads((HERE/'nonzero19_stream_plan.json').read_text())
assert PLAN['domain']=='nonzero' and PLAN['max_live']==13
inverse6_nonzero19=generic.combo.xsub.clone(generic.inverse6_consume20_12,
    dict(generic.inverse6_consume20_12.__globals__,PLAN=PLAN))


def install(entry,ceiling=889,minimum_space=7):
    def wrap(original):
        def chosen(b,x):
            space=ceiling-b.num_allocated_qubits
            if len(x)==6 and minimum_space<=space<10:
                return inverse6_nonzero19(b,x)
            return original(b,x)
        return chosen
    replacements={id(fn):wrap(fn) for fn in nonzero.functions(entry)
                  if fn.__code__ is nonzero.stream_nonzero.__code__}
    assert replacements
    scope=dict(entry.__globals__)
    scope['extraction']=generic.combo.xsub.private_rebind(scope['extraction'],replacements)
    result=generic.combo.xsub.clone(entry,scope)
    for name in ('synthesize','convert_safe','baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result


decode=install(nonzero.install(generic.combo.decode))
