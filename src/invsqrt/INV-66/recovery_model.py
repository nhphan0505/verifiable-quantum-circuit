"""Recovered INV-66 classical arithmetic; analysis, not the circuit builder.

Tables are independently recovered coefficient values, not encoded gates.
The six row-specific rounding rules are part of the observed algorithm.
This module does not read a KMB/KMX or establish quantum phase correctness.
"""
from math import isqrt
INTERCEPT = (8065, 7821, 7587, 7364, 7151, 6946, 6751, 6564, 6384, 6212, 6046, 5887, 5734, 5587, 5445, 5309, 5178, 5051, 4929, 4812, 4699, 4590, 4484, 4382, 4284, 4188, 4096, 4007, 3921, 3837, 3757, 3679, 3603, 3529, 3458, 3389, 3321, 3256, 3194, 3132, 3073, 3015, 2958, 2903, 2850, 2798, 2748, 2699, 2651, 2605, 2559, 2515, 2472, 2430, 2389, 2350, 2311, 2273, 2236, 2200, 2165, 2130, 2097, 2064)
SLOPE = (125, 120, 114, 109, 104, 99, 97, 91, 88, 85, 81, 78, 75, 72, 70, 67, 64, 62, 59, 57, 56, 54, 51, 49, 48, 46, 45, 44, 41, 41, 40, 38, 38, 35, 35, 34, 33, 32, 31, 30, 29, 28, 28, 27, 26, 25, 25, 24, 23, 23, 22, 22, 21, 21, 20, 20, 19, 19, 18, 18, 17, 17, 16, 16)
COEFFICIENT_PORTS = (34, 36, 30, 32, 28, 35, 33, 31, 29, 26, 27, 37, 38)
SEED_PORTS = (45, 42, 41, 40, 43, 39)
PRODUCT_PORTS = SEED_PORTS + tuple(range(9))
RETURNED_PRODUCT_PORTS = SEED_PORTS + tuple(range(7)) + (30, 36)

def normalize_root(x):
    """Return pair-shift count, normalized n, fractional root v, residual h.

    n=x*4**k, R=floor(sqrt(16*n))=4096+v. Residual h is a ten-bit
    word, not an unrestricted signed integer. The implicit leading root bit
    and the bias -1 matter at exact squares and bin boundaries.
    """
    if not 1 <= x <= 3133452:
        raise ValueError('x outside the competition input domain')
    k = (22 - x.bit_length()) // 2
    n = x << 2 * k
    r = isqrt(16 * n)
    return (k, n, r - 4096, n - r * (r + 1) // 16 - 1 & 1023)

def coefficient(v):
    """13-bit interpolation C, with a=v>>6 and local coordinate t=v&63.

    Each low-root bit selects addition/subtraction of one truncated slope
    row. Positive/negative rows use different adjacent rounding bits; a
    single rounded linear interpolation does not reproduce this function.
    """
    a, t = divmod(v, 64)
    c, s = (INTERCEPT[a], SLOPE[a])
    for i in range(6):
        k = 5 - i
        upper = s >> k + 1
        if t >> i & 1:
            c -= upper + (s >> k - 1 & 1 if k else 0)
        else:
            c += upper + (s >> k & 1)
    return c & 8191

def seed_word(v, c):
    """Six-bit seed from three signed rows of the current coefficient.

    Carries are rounded at cuts 11,10,9. The transformed root coordinates
    are temporary; the circuit restores the original low-root owners.
    Bit operations also support NumPy integer arrays for analysis.
    """
    p0 = (v >> 0 ^ v >> 2) & 1
    p1 = (v >> 1 ^ v >> 2) & 1
    p3 = (v >> 3 ^ v >> 2 ^ p0 & p1) & 1
    p0 ^= p1
    z = 7
    for i, p in enumerate((p0, p1, p3)):
        cut = 11 - i
        row = (c >> cut) + (c >> cut - 1 & 1)
        z = z + (2 * p - 1) * row & (1 << 3 + i) - 1
        z |= (1 ^ p) << 3 + i
    return z

def signed_product(h, c, seed):
    """Return the 15-bit product word entering the balanced divider.

    Ten signed rows update a six-bit seed followed by the residual word.
    Rounding uses the shared coefficient parity, including the aliased
    carry on the final row. This returns a modular word, not a real number.
    """
    word = (seed | h << 6) ^ 1 << 15
    doubled = c << 1
    parity = doubled >> 8 & 1
    for i in range(10):
        q = word >> 6 + i & 1
        shift = 8 - i
        if shift > 0:
            upper = doubled >> shift & 1
            lower = doubled >> shift - 1 & 1
            carry = upper ^ (upper ^ lower) & (q ^ parity ^ 1)
        elif shift == 0:
            carry = 0
        else:
            carry = q ^ parity ^ 1
        row = (doubled >> max(9 - i, 0)) + carry
        mask = (1 << 6 + i) - 1
        low = (word & mask) + (1 - 2 * q) * row & mask
        word = word & (65535 ^ mask) | low
    return (word ^ 1 << 15) & 32767

def divider_forward(v, p):
    """Return the 14-bit remainder register and saved signs 12..24.

    R=4096+v is the fixed-point square root. Initialization absorbs the
    three high signed-product bits. Thirteen feed rows consume P12..P0;
    eleven remaining rows rotate and progressively truncate the remainder.
    """
    v0 = v & 1
    u = 4094 - 3 * v + (p >> 12 & 1) + (p >> 13 & 1) - 2 * (p >> 14 & 1) & 16383
    history = {}
    for j in range(12, 36):
        if j <= 24:
            prev = p >> 24 - j & 1
            cur = p >> 23 - j & 1 if j < 24 else 0
            sign = u >> 13 & 1
            carry = v0 ^ prev ^ v0 & prev ^ v0 & cur ^ prev & cur ^ prev & sign ^ cur & sign
            target = (u & 8191) + (2 * sign - 1) * ((v >> 1) + carry + 2048) & 8191
            low = prev ^ v0 ^ sign ^ cur
            u = low | target << 1
            history[j] = sign
        else:
            k = j - 26 if j >= 28 else 0
            rotated = u << 1 & 16383 | u >> 13
            sign = rotated & 1
            target = (rotated >> k + 1) + (2 * sign - 1) * ((v >> k + 1) + (v >> k & 1) + (1 << 11 - k))
            target &= (1 << 13 - k) - 1
            low = rotated & (1 << k + 1) - 1 ^ v0
            u = low | target << k + 1
    return (u, history)

def divider_inverse(v, u, history):
    """Invert all 24 rows and recover the signed 15-bit product word."""
    v0 = v & 1
    p = 0
    for j in reversed(range(12, 36)):
        if j >= 25:
            k = j - 26 if j >= 28 else 0
            sign = u & 1 ^ v0
            target = (u >> k + 1) - (2 * sign - 1) * ((v >> k + 1) + (v >> k & 1) + (1 << 11 - k))
            target &= (1 << 13 - k) - 1
            rotated = u & (1 << k + 1) - 1 ^ v0 | target << k + 1
            u = rotated >> 1 | (rotated & 1) << 13
        else:
            sign = history[j]
            cur = p >> 23 - j & 1 if j < 24 else 0
            prev = u & 1 ^ v0 ^ sign ^ cur
            p |= prev << 24 - j
            carry = v0 ^ prev ^ v0 & prev ^ v0 & cur ^ prev & cur ^ prev & sign ^ cur & sign
            target = (u >> 1) - (2 * sign - 1) * ((v >> 1) + carry + 2048) & 8191
            u = target | sign << 13
    high = u + 3 * v - 4094 - (p >> 12 & 1) & 16383
    return p | (high & 1) << 13 | (high >> 1 & 1) << 14

def phase_features(v, u, history, k, slots):
    bit = lambda n, i: n >> i & 1
    v0, v1, v10 = (bit(v, 0), bit(v, 1), bit(v, 10))
    ubits = [bit(u, i) for i in range(14)]
    ubits[10] ^= v10 ^ v0 ^ v1 ^ (ubits[9] ^ ubits[8]) & (v0 ^ v1)
    for i in range(9):
        ubits[i] ^= v0
    ubits[9] ^= v1
    signs = dict(history)
    signs.update({25: ubits[10], 26: ubits[9], 36: ubits[13]})
    signs.update({j: ubits[35 - j] for j in range(27, 36)})
    word = [1 ^ signs[36 - i] for i in range(25)] + [1]
    flags = [bit(k, i) for i in range(4)]
    controls = [1 ^ flags[2], flags[3], 1 ^ flags[1] ^ flags[2] ^ flags[3], 1 ^ flags[0] ^ flags[1], 1 ^ flags[0]]
    for centre, control in zip((2, 6, 24, 0, 25), controls):
        for i in range(26):
            j = (centre - i) % 26
            if i < j:
                delta = (word[i] ^ word[j]) & control
                word[i] ^= delta
                word[j] ^= delta
    base = [word[i] for i in slots]
    overflow = [base[j] & (k >= j + 1) for j in range(9)]
    return (base, overflow)

def phase_half_turns(x, parameters):
    """Evaluate the recovered phase model modulo two half-turns.

    The original refit search is not repeated: 33 tracked dyadic coefficients
    are the fixed parameters. The overflow-8 term remains present even though
    the finishing pass relocates its implementation to normalization.
    """
    from fractions import Fraction
    k, n, v, h = normalize_root(x)
    c = coefficient(v)
    p = signed_product(h, c, seed_word(v, c))
    u, history = divider_forward(v, p)
    base, overflow = phase_features(v, u, history, k, parameters['slots'])
    angles = parameters['base_half_turns'] + parameters['overflow_half_turns']
    phase = sum((Fraction(a) * b for a, b in zip(angles, base + overflow[:7])), Fraction())
    phase += Fraction(overflow[7], 4) + Fraction(overflow[8], 2) + (k >> 1 & 1 & (k >> 3 & 1))
    return phase % 2
