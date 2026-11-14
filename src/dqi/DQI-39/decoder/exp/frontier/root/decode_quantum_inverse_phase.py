"""Exact W14 inverse characters with a quantum coefficient.

The specialized caller has L=0 whenever u=0, since u=Norm(t) and L is
linear in t.  That identity removes the zero-output product without
assuming that an independently supplied field element is nonzero.
"""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/'exp/r-main/narrow240'), str(HERE.parent/'a03')]
import decode_combo as combo
import exact_subs as xs
from jet_norm6 import replacement_ids
from exp.jet24 import pro_jet as jet
from exp.inverse12_escape import joint


def phase_inverse6_quantum(b, x, coefficient, annihilates_zero=False):
    """Pay coefficient dot inv0(x); optionally use coefficient(0)=0."""
    dag = jet.W14_JOINT18
    xs.linear_inplace(b, x, jet.TO6)
    raw = b.alloc_qubits(6)
    for j, (left, right) in enumerate(dag['raw_gates']):
        with xs.expose_pair(b, x, left, right) as (a, c):
            b.init_and(a, c, raw[j])
    prefix = list(x) + list(raw)
    forms = xs.ref.norm_forms(1)
    inner = xs.ref.inverse3_virtual(b, prefix, forms)
    source = prefix + list(inner)
    transpose = [sum(((jet.FROM6[i] >> j) & 1) << i for i in range(6))
                 for j in range(6)]
    xs.linear_inplace(b, coefficient, transpose)
    for j, expression in enumerate(dag['outputs'][:6]):
        linear = expression & 65535
        if annihilates_zero and (expression >> 16) & 1:
            linear ^= 1555
        if linear & 1:
            b.z(coefficient[j])
        for i in xs.bits(linear >> 1):
            b.cz(source[i], coefficient[j])
    start = 1 if annihilates_zero else 0
    for i in range(start, len(dag['gates'])):
        vector = sum(((expression >> (16+i)) & 1) << j
                     for j, expression in enumerate(dag['outputs'][:6]))
        indices = list(xs.bits(vector))
        if not indices:
            continue
        pivot = indices[0]
        for j in indices[1:]:
            b.cx(coefficient[j], coefficient[pivot])
        with xs.expose_pair(b, source, *dag['gates'][i]) as (a, c):
            b.ccz(a, c, coefficient[pivot])
        for j in reversed(indices[1:]):
            b.cx(coefficient[j], coefficient[pivot])
    mask = b.alloc_bits(3)
    b.hmr(inner, mask)
    b.free(inner)
    xs.ref.phase_inverse3_virtual(b, prefix, forms, mask)
    b.free(mask)
    for j, (left, right) in reversed(list(enumerate(dag['raw_gates']))):
        with xs.expose_pair(b, x, left, right) as (a, c):
            b.del_and(a, c, raw[j])
    b.free(raw)
    xs.linear_inplace(b, coefficient, xs.inverse_columns(transpose))
    xs.linear_inplace(b, x, jet.FROM6)


def phase_inverse6_quantum17(b, x, coefficient):
    return phase_inverse6_quantum(b, x, coefficient, True)


def install(entry):
    old = joint.erase_norm_via_inverse_cache19
    specialized = xs.clone(old, dict(old.__globals__,
                                     phase_inverse6_quantum19=phase_inverse6_quantum17))
    specialized = xs.private_rebind(specialized, combo.synth.replacements)
    replacements = replacement_ids(entry, old, specialized)
    assert replacements
    scope = dict(entry.__globals__)
    for name in ('extraction', 'synthesize'):
        scope[name] = xs.private_rebind(scope[name], replacements)
    return xs.clone(entry, scope)


decode = install(combo.decode)
