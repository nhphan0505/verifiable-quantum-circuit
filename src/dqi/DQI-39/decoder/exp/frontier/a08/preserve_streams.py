"""Add narrow generic leaves without replacing any existing recursive body."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'a04')]
from inverse20_consume14 import inverse6_consume20,inverse6_consume19,combo,schedules
from nonzero_consume16 import functions


def wrap(original,ceiling):
    def chosen(b,x):
        if len(x)==6:
            space=ceiling-b.num_allocated_qubits
            if space==10:return inverse6_consume19(b,x)
            if 8<=space<10:return inverse6_consume20(b,x)
        return original(b,x)
    return chosen


def install(entry,ceiling=889):
    scope=dict(entry.__globals__)
    for name in ('extraction','synthesize'):
        original=scope[name]
        replacements={id(fn):wrap(fn,ceiling) for fn in functions(original)
                      if fn.__code__ is schedules.inverse_stream_noscratch.__code__}
        scope[name]=combo.xsub.private_rebind(original,replacements)
    result=combo.xsub.clone(entry,scope)
    for name in ('convert_safe','baseline'):
        assert result.__globals__[name] is entry.__globals__[name]
    return result


decode=install(combo.decode)
