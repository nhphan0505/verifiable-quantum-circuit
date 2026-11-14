"""Control the entire exceptional GF4096 multiplier by Frobenius.

For every nonzero field multiplier a, F M_a F^-1 M_a^-1=M_a,
where F:x->x^2. This removes the per-gate exceptional controls.
"""
from contextlib import contextmanager
from types import FunctionType
import no_clean_source12_factored as prior
from no_clean_source12 import one_plus_zeta
from dirty_inverse_fast import inverse6_dirty
from field_frobenius_control import controlled_frobenius
ar=prior.ar


def exception_correction(b,x,r,key,borrow,inverse=False):
    # The correction on the zero-high source row is multiplication by
    # r/(r+zeta)=(1+inv0(r)*zeta)^-1. Its nonzero-source promise gives
    # r!=0 there. Off that row the four factors cancel for every r.
    inverse6_dirty(b,r,borrow)
    wanted_inverse=not inverse
    one_plus_zeta(b,x,r,not wanted_inverse)
    controlled_frobenius(b,x,key,borrow,True)
    one_plus_zeta(b,x,r,wanted_inverse)
    controlled_frobenius(b,x,key,borrow,False)
    inverse6_dirty(b,r,borrow)


raw=prior.source.__wrapped__
scope=dict(raw.__globals__,exception_correction=exception_correction)
source=contextmanager(FunctionType(raw.__code__,scope,raw.__name__,raw.__defaults__,raw.__closure__))
