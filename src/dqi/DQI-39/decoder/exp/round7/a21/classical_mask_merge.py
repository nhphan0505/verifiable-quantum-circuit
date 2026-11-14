"""Merge two product characters with only classical mask arithmetic.

No quantum input is read or used as a classical control.  The ratio is a
function of the two independently generated HMR masks.  Both payloads are
restored by the same conditional linear field addition.
"""
from functools import lru_cache
from exp.decoder.common import ar, emul, K
from exp.mul99.kernels import tensor99_extension, mul24_xor99


def classical_linear(b, source, columns):
    out = b.alloc_bits(len(columns))
    b.bit_store(out, False)
    for j, v in enumerate(columns):
        for k in ar.bits(v):
            b.cx(source[j], out[k])
    return out


def classical_product(b, x, y):
    """Rank99 field product into classical bits, with classical conditions."""
    out = b.alloc_bits(24)
    b.bit_store(out, False)
    p = b.alloc_bits(1)[0]
    q = b.alloc_bits(1)[0]
    for mask, v in tensor99_extension(K):
        b.bit_store(p, False)
        b.bit_store(q, False)
        for j in ar.bits(mask):
            b.cx(x[j], p)
            b.cx(y[j], q)
        b.push_condition(p)
        for k in ar.bits(v):
            b.cx(q, out[k])
        b.pop_condition()
    b.free(q)
    b.free(p)
    return out


@lru_cache(None)
def frobenius_columns(power):
    cols = []
    for j in range(24):
        v = 1 << j
        for _ in range(power):
            v = emul(v, v)
        cols.append(v)
    return tuple(cols)


def classical_inverse(b, a):
    """inv0(a), using the addition chain 1,2,4,8,16,20,22,23."""
    powers = {1: a}
    for left, right in ((1,1),(2,2),(4,4),(8,8),(16,4),(20,2),(22,1)):
        shifted = classical_linear(b, powers[left], frobenius_columns(right))
        powers[left+right] = classical_product(b, shifted, powers[right])
        b.free(shifted)
    result = classical_linear(b, powers[23], frobenius_columns(1))
    for key, value in powers.items():
        if key != 1:
            b.free(value)
    return result


def absolute_trace(v):
    out = 0
    for _ in range(24):
        out ^= v
        v = emul(v, v)
    assert out in (0, 1)
    return out


@lru_cache(None)
def dual_columns():
    """gamma(m) is the unique element with Tr(gamma(m)*x)=dot(m,x)."""
    gram = tuple(sum(absolute_trace(emul(1 << i, 1 << j)) << i
                     for i in range(24)) for j in range(24))
    columns = tuple(ar.inverse_columns(gram))
    for j, column in enumerate(columns):
        assert ar.apply(gram, column) == 1 << j
    return columns


def phase_pair(b, targets, C, u, masks, phase_three_factor):
    assert len(targets) == len(masks) == 2
    x, y = targets
    mx, my = masks
    a = classical_linear(b, mx, dual_columns())
    c = classical_linear(b, my, dual_columns())
    inverse = classical_inverse(b, a)
    ratio = classical_product(b, c, inverse)
    b.free(inverse)
    b.free(c)
    b.free(a)
    active = b.alloc_bits(1)[0]
    b.bit_store(active, False)
    for m in mx:
        b.bit_store(active, True, control=m)
    b.push_condition(active)
    mul24_xor99(b, y, ratio, x, K)
    phase_three_factor(b, x, C, u, mx)
    mul24_xor99(b, y, ratio, x, K)
    b.pop_condition()
    b.x(active)
    b.push_condition(active)
    phase_three_factor(b, y, C, u, my)
    b.pop_condition()
    b.free(active)
    b.free(ratio)
