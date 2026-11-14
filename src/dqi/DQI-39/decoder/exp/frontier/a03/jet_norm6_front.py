"""Install the complete retained inverse-norm jet only in extraction."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from jet_norm6 import base,xs,replacement_ids,jet,reverse_canonical_kept


def install(entry):
    original=entry.__globals__['extraction']
    replacements=replacement_ids(original,jet.reverse_canonical,reverse_canonical_kept)
    extraction=xs.private_rebind(original,replacements)
    return xs.clone(entry,dict(entry.__globals__,extraction=extraction))


decode=install(base.decode)
assert decode.__globals__['convert_safe'] is base.decode.__globals__['convert_safe']
assert decode.__globals__['baseline'] is base.decode.__globals__['baseline']
