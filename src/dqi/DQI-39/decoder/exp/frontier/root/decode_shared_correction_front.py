"""Install the shared tail factor only in the synthesis graph."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_shared_correction import term_correction_with_inverse, base


def install(entry):
    synth = entry.__globals__['synthesize']
    tail = synth.__globals__['tail_inplace']
    finish = tail.__globals__['tail_finish']
    old = finish.__globals__['term_correction_with_inverse']
    new = base.xsub.clone(term_correction_with_inverse, dict(old.__globals__))
    scope = dict(entry.__globals__)
    scope['synthesize'] = base.xsub.private_rebind(synth, {id(old): new})
    return base.xsub.clone(entry, scope)


decode = install(base.decode)
