"""Same exact bank-rotating map, using the supplied narrow forward division.

The reverse is A22's explicitly closed projective multiplication.  The
asymmetric implementation has the same all-input value permutation.
"""
from types import FunctionType
import inspect
import pivot_rotate as projective
from exp.mul99 import schedules as bridge
from exp.noscratch import schedules as stream
from exp.jet24.pro_jet import inverse6_joint18_12extra
from exp.mul99.phase36 import phase_inverse36_pivot_original


def inverse6_init18(b, x):
    """The existing initialized leaf, copied without a whole-decoder import."""
    t, F = inverse6_joint18_12extra(b, x)
    m = b.alloc_bits(1)
    b.hmr(F, m[0]); b.free(F)
    b.z(m[0])
    mask = b.alloc_bits(6); b.bit_store(mask, False)
    b.cx(m[0], mask[0])
    projective.ar.phase_product(b, x, t, mask)
    b.free(mask); b.free(m)
    return t


# Privately rebind the supplied recursive stream so its leaf is explicit
# here.  Its lazy import of exact_subs would otherwise load a whole decoder
# graph during a local diagnostic.  No supplied module global is patched.
_source = inspect.getsource(stream.inverse_stream_noscratch)
assert _source.count('from exact_subs import inverse6_init18') == 1
_source = _source.replace('from exact_subs import inverse6_init18', 'pass')
_scope = dict(stream.inverse_stream_noscratch.__globals__, inverse6_init18=inverse6_init18)
exec(compile(_source, __file__, 'exec'), _scope)
_stream = _scope['inverse_stream_noscratch']
_divide = FunctionType(bridge._divide_lowwidth.__code__,
    dict(bridge._divide_lowwidth.__globals__, inverse_stream_noscratch=_stream),
    '_divide_lowwidth', bridge._divide_lowwidth.__defaults__)
_low = FunctionType(bridge.divide_lowwidth369.__code__,
    dict(bridge.divide_lowwidth369.__globals__, _divide_lowwidth=_divide,
         phase_inverse36_pivot=phase_inverse36_pivot_original),
    'divide_lowwidth369', bridge.divide_lowwidth369.__defaults__)
divide_zero_bridge414 = FunctionType(bridge.divide_zero_bridge414.__code__,
    dict(bridge.divide_zero_bridge414.__globals__, divide_lowwidth369=_low),
    'divide_zero_bridge414', bridge.divide_zero_bridge414.__defaults__)


def divide_pair(b, source, target, reverse=False):
    if reverse:
        return projective.divide_pair(b, source, target, True)
    return divide_zero_bridge414(b, target, source, 2048)


rotated_affine_conjugate = FunctionType(
    projective.rotated_affine_conjugate.__code__,
    dict(projective.rotated_affine_conjugate.__globals__, divide_pair=divide_pair),
    'rotated_affine_conjugate', projective.rotated_affine_conjugate.__defaults__)

completed_outside_rotated_pivot = FunctionType(
    projective.completed_outside_rotated_pivot.__code__,
    dict(projective.completed_outside_rotated_pivot.__globals__,
         rotated_affine_conjugate=rotated_affine_conjugate),
    'completed_outside_rotated_pivot', projective.completed_outside_rotated_pivot.__defaults__)
