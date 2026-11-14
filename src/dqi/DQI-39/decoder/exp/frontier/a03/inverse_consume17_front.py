"""Install the consuming inverse only in extraction and synthesis closures."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from inverse_consume17 import inverse6_consume17,inverse_stream_narrow,fallback
from jet_norm6 import base,xs,replacement_ids
from exp.noscratch import schedules


def install(entry):
    updates={}
    for name in ('extraction','synthesize'):
        original=entry.__globals__[name]
        replacements=replacement_ids(original,schedules.inverse_stream_noscratch,inverse_stream_narrow)
        updates[name]=xs.private_rebind(original,replacements)
    return xs.clone(entry,dict(entry.__globals__,**updates))


decode=install(base.decode)
assert decode.__globals__['convert_safe'] is base.decode.__globals__['convert_safe']
assert decode.__globals__['baseline'] is base.decode.__globals__['baseline']
