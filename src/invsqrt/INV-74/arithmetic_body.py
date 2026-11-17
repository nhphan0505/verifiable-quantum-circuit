"""Compose the recovered forward arithmetic, preserving typed inverse debts.

This is the continuous coefficient/seed/product/divider/phase body. During
staged recovery its adapter supplies the existing lookup's physical owners;
the individual modules expose word-level APIs for the complete generator.
No KMB/KMX, external bundle, cache or reference file is a runtime input.
"""
import sys
import kickmix as km
import coefficient
import seed_product
import divider
import phase
from arithmetic_prefix import arithmetic_modules
from phase_parameters import BASE_HALF_TURNS, OVERFLOW_HALF_TURNS


def context():
    arithmetic_modules()
    shared=sys.modules['_inv74_shared_arithmetic']
    def component(name,key):
        spec=shared._Spec(name,shared._VROOT/key)
        module=shared._new_module(spec)
        sys.modules[name]=module
        spec.loader.exec_module(module)
        return module
    base='work/c10/narrow/checkpoint002/cleanroom/baseline_stage97/engine/'
    return (component('_inv74_paired',base+'paired_arithmetic.py'),
            component('_inv74_polynomial',base+'quadratic_terms.py'),
            component('_inv74_cyclic',base+'cyclic_phase.py'))


def forward(cb,v,D,H,bridge,flags,h):
    """Return divider/seed/product/coefficient tokens for subsequent inversion."""
    ar,poly,cyclic=context()
    D,ctoken=coefficient.forward(cb,ar,v[:6],D,H,bridge)
    v,P,ptoken=seed_product.forward(cb,ar,v,D,flags,h,
        hold_outcome=km.b(363),top_outcome=km.b(364))
    token=divider.forward(cb,ar,v,P,flags,D)
    phase.apply(cb,poly,cyclic,token,{'base_half_turns':list(BASE_HALF_TURNS),
        'overflow_half_turns':list(OVERFLOW_HALF_TURNS)},finishing_outcome=km.b(365))
    return token,ptoken,ctoken


def build_forward_body():
    """Compile arithmetic against the still-unlifted lookup's owner interface."""
    cb=coefficient._SegmentBuilder()
    q=km.q
    D=[q(i) for i in (21,34,36,0,30,32,28,35,33,31,20,26,27)]
    forward(cb,[q(i) for i in range(10,20)],D,[q(i) for i in range(37,42)],
        q(29),[q(i) for i in range(22,26)],[q(i) for i in range(1,10)])
    return str(cb.finish_circuit()).splitlines()
