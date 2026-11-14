"""Retain the trailing scalar ratio and remove its forward phase replay.

The denominator is inverted in place. All normalization masks are combined
into one inverse character before either original input word is retired.
"""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/'exp/r-main/narrow240')]
import decode_combo as combo
import retained_core_safe27 as retained
from exp.noscratch.schedules import inverse_stream_noscratch


def transpose_square_mask(b, mask):
    columns = [ar.field(12).square(1 << j) for j in range(12)]
    out = b.alloc_bits(12)
    b.bit_store(out, False)
    for j, column in enumerate(columns):
        for i in ar.bits(column):
            b.cx(mask[i], out[j])
    return out


def scale_defer(b, x, factor):
    out = b.alloc_qubits(12)
    ar.mul_xor0(b, x, factor, out)
    mask = b.alloc_bits(12)
    b.hmr(x, mask)
    b.swap(x, out)
    b.free(out)
    return mask


def extraction_companion(b, words, reverse=False, token=None):
    if not reverse:
        return forward_original(b, words, False, token)
    heads = [words[2*i:2*i+2] for i in range(34)]
    N, L = words[-2:]
    pole = token['pole']
    controlled_inverse(b, L, pole, True, token['chart_inverse'])
    ratio = b.alloc_qubits(12)
    b.cx(N, ratio)
    D = b.alloc_qubits(12)
    b.x(D[0])
    b.cx(pole, N[0])
    b.cx(pole, D[0])
    for head, kap, c in reversed(list(zip(heads, ks, corrections))[1:]):
        step(b, head, N, D, L, kap, c, True)
    scale(b, N, inv(ks[0]))
    b.swap(N, D)
    scale(b, L, inv(ks[0]))
    # D=1/C, N=(N0+a0)/C, L=(L0+h0)/C², ratio=selected Nf/C.
    im = inverse_stream_noscratch(b, D)
    nm = scale_defer(b, N, D)
    rm = scale_defer(b, ratio, D)
    square12(b, D)
    lm = scale_defer(b, L, D)
    square12(b, D, True)
    constant = token['normalization']
    b.cx(im, constant)
    b.free(im)
    square12(b, L, True)
    sm = transpose_square_mask(b, lm)
    linear_inverse_character(b, D, constant, [(N, nm), (ratio, rm), (L, sm)])
    square12(b, L)
    for mask in (constant, nm, rm, lm, sm):
        b.free(mask)
    b.cz(D, token['gauge_mask'])
    b.free(token['gauge_mask'])
    b.cx(heads[0][0], N)
    b.cx(heads[0][1], L)
    original_mask = b.alloc_bits(12)
    b.hmr(N, original_mask)
    b.swap(N, ratio)
    b.free(ratio)
    b.cswap(pole, N, D)
    # Deliberately retain the supplied trailing pole toggle, not the user's
    # excluded newer measured-pole improvement.
    guarded.zero_toggle(b, D, pole)
    for i in reversed(range(1, len(heads))):
        if i == 1:
            scalar_erase_second12(b, heads[i], N, D, ks[i], ks[0])
        else:
            scalar_step(b, heads[i], N, D, ks[i], True)
    scalar_step(b, heads[0], N, D, ks[0], True, first=True)
    b.x(D[0])
    b.free(D)
    b.free(pole)
    b.cz(N, original_mask)
    b.free(original_mask)
    external_extraction(b, words, True, token['external'])


def install(entry):
    original = entry.__globals__['extraction']
    scope = dict(original.__globals__)
    ref = scope['ref']
    for name in ('controlled_inverse', 'ks', 'corrections', 'step',
                 'scalar_step', 'guarded', 'square12'):
        scope[name] = getattr(ref, name)
    scope['scalar_erase_second12'] = retained.__dict__.get('scalar_erase_second12')
    from replay_erase import scalar_erase_second12
    scope['scalar_erase_second12'] = scalar_erase_second12
    scope.update(forward_original=original, inverse_stream_noscratch=inverse_stream_noscratch,
                 linear_inverse_character=retained.linear_inverse_character)
    scope['transpose_square_mask'] = combo.xsub.clone(transpose_square_mask, scope)
    scope['scale_defer'] = combo.xsub.clone(scale_defer, scope)
    candidate = combo.xsub.clone(extraction_companion, scope)
    candidate = combo.xsub.private_rebind(candidate, combo.synth.replacements)
    result = combo.xsub.clone(entry, dict(entry.__globals__, extraction=candidate))
    assert result.__globals__['convert_safe'] is entry.__globals__['convert_safe']
    assert result.__globals__['baseline'] is entry.__globals__['baseline']
    return result


decode = install(combo.decode)
