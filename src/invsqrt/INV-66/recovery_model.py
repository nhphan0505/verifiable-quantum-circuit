"""Recovered INV-66 classical arithmetic; analysis, not the circuit builder.

Tables are independently recovered coefficient values, not encoded gates.
The six row-specific rounding rules are part of the observed algorithm.
This module does not read a KMB/KMX or establish quantum phase correctness.
"""
from math import isqrt

INTERCEPT = (
    8065,7821,7587,7364,7151,6946,6751,6564,6384,6212,6046,5887,5734,5587,5445,5309,
    5178,5051,4929,4812,4699,4590,4484,4382,4284,4188,4096,4007,3921,3837,3757,3679,
    3603,3529,3458,3389,3321,3256,3194,3132,3073,3015,2958,2903,2850,2798,2748,2699,
    2651,2605,2559,2515,2472,2430,2389,2350,2311,2273,2236,2200,2165,2130,2097,2064,
)
SLOPE = (
    125,120,114,109,104,99,97,91,88,85,81,78,75,72,70,67,
    64,62,59,57,56,54,51,49,48,46,45,44,41,41,40,38,
    38,35,35,34,33,32,31,30,29,28,28,27,26,25,25,24,
    23,23,22,22,21,21,20,20,19,19,18,18,17,17,16,16,
)
COEFFICIENT_PORTS = (34,36,30,32,28,35,33,31,29,26,27,37,38)
SEED_PORTS = (45,42,41,40,43,39)
PRODUCT_PORTS = SEED_PORTS + tuple(range(9))
RETURNED_PRODUCT_PORTS = SEED_PORTS + tuple(range(7)) + (30,36)

def normalize_root(x):
    """Return pair-shift count, normalized n, fractional root v, residual h.

    n=x*4**k, R=floor(sqrt(16*n))=4096+v. Residual h is a ten-bit
    word, not an unrestricted signed integer. The implicit leading root bit
    and the bias -1 matter at exact squares and bin boundaries.
    """
    if not 1 <= x <= 3133452:
        raise ValueError('x outside the competition input domain')
    k = (22-x.bit_length())//2
    n = x << (2*k)
    r = isqrt(16*n)
    return k,n,r-4096,(n-(r*(r+1)//16)-1)&1023

def coefficient(v):
    """13-bit interpolation C, with a=v>>6 and local coordinate t=v&63.

    Each low-root bit selects addition/subtraction of one truncated slope
    row. Positive/negative rows use different adjacent rounding bits; a
    single rounded linear interpolation does not reproduce this function.
    """
    a,t = divmod(v,64)
    c,s = INTERCEPT[a],SLOPE[a]
    for i in range(6):
        k = 5-i
        upper = s>>(k+1)
        if (t>>i)&1:
            c -= upper + (((s>>(k-1))&1) if k else 0)
        else:
            c += upper + ((s>>k)&1)
    return c&8191

def seed_word(v,c):
    """Six-bit seed from three signed rows of the current coefficient.

    Carries are rounded at cuts 11,10,9. The transformed root coordinates
    are temporary; the circuit restores the original low-root owners.
    Bit operations also support NumPy integer arrays for analysis.
    """
    p0 = ((v>>0)^(v>>2))&1
    p1 = ((v>>1)^(v>>2))&1
    p3 = ((v>>3)^(v>>2)^(p0&p1))&1
    p0 ^= p1
    z = 7
    for i,p in enumerate((p0,p1,p3)):
        cut = 11-i
        row = (c>>cut)+((c>>(cut-1))&1)
        z = (z+(2*p-1)*row)&((1<<(3+i))-1)
        z |= (1^p)<<(3+i)
    return z

def signed_product(h,c,seed):
    """Return the 15-bit product word entering the balanced divider.

    Ten signed rows update a six-bit seed followed by the residual word.
    Rounding uses the shared coefficient parity, including the aliased
    carry on the final row. This returns a modular word, not a real number.
    """
    word = (seed|(h<<6))^(1<<15)
    doubled = c<<1
    parity = (doubled>>8)&1
    for i in range(10):
        q = (word>>(6+i))&1
        shift = 8-i
        if shift > 0:
            upper = (doubled>>shift)&1
            lower = (doubled>>(shift-1))&1
            carry = upper^((upper^lower)&(q^parity^1))
        elif shift == 0:
            carry = 0
        else:
            carry = q^parity^1
        row = (doubled>>max(9-i,0))+carry
        mask = (1<<(6+i))-1
        low = ((word&mask)+(1-2*q)*row)&mask
        word = (word&(65535^mask))|low
    return (word^(1<<15))&32767
