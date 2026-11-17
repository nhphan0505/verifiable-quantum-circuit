"""Compose the recovered forward arithmetic, preserving typed inverse debts.

The live builder carries coefficient/seed/product/divider/phase words and
typed measurement debts into their inverse. Every stage preserves allocator
ownership and the fixed Q44 schedule.
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


def component(name,key):
    shared=sys.modules['_inv74_shared_arithmetic']
    spec=shared._Spec(name,shared._VROOT/key)
    module=shared._new_module(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def context():
    if '_inv74_shared_arithmetic' not in sys.modules:arithmetic_modules()
    shared=sys.modules['_inv74_shared_arithmetic']
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
