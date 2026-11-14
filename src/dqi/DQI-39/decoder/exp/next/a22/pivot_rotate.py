"""A paired pivot that moves the surviving denominator into the d bank.

The value boundary is (a,z,d), with a in GF(4096), z,d in GF(2^24).
It maps (z,d) to ((d+a*bar(z))/safe(z), z), where safe(0)=1.
Thus every nonzero-z fiber gives the actual quotient, and no fiber
coordinate is erased: the old z occupies the old d bank.  The quotient
source a is preserved.  This is not the fixed-d permutation in
nonlinear_pair.py; it explicitly changes both existing target banks.
"""
from nonlinear_pair import inverse_apply, scale, zero_toggle, ar, matrix_bar


def add_trace_term(b, a, z, d):
    """d += a*bar(z), preserving quantum a,z, no fresh word."""
    b.cx(z[12:], z[:12])
    ar.mul_xor0(b, a, z[:12], d[:12])
    ar.mul_xor0(b, a, z[12:], d[12:])
    b.cx(z[12:], z[:12])


def divide_pair(b, source, target, reverse=False):
    """Multiply target by inverse(safe(source)), or its inverse operation.

    The source is exposed and restored in its existing 24 wires.  Only
    GF(4096) inverse/product temporaries are needed; there is no fresh
    GF(2^24) denominator or output companion.
    """
    r, g = source[:12], source[12:]
    I = b.alloc_qubits(1)[0]
    zero_toggle(b, g, I)
    b.cswap(I, r, g)
    b.x(I)

    def prepare(gi):
        scale(b, r, g, gi, True)
        if not reverse:
            scale(b, target[:12], g, gi, True)
            scale(b, target[12:], g, gi, True)
    # g is unchanged across the middle matrix operation.  Its first
    # inverse/zero measurement character can be paid from the second
    # already-required inverse, without keeping any quantum inverse bank.
    token = inverse_apply(b, g, prepare, defer=True)

    # Conjugation changes multiplication/division by bar(v) to v.
    b.cx(target[12:], target[:12])
    matrix_bar(b, target, r, I, not reverse)
    b.cx(target[12:], target[:12])

    def restore(gi):
        if reverse:
            scale(b, target[:12], g, gi, False)
            scale(b, target[12:], g, gi, False)
        scale(b, r, g, gi, False)
    inverse_apply(b, g, restore, incoming=token)

    b.x(I)
    b.cswap(I, r, g)
    zero_toggle(b, g, I)
    b.free(I)


def rotated_affine_conjugate(b, a, z, d, reverse=False):
    """(z,d) <-> (quotient,old-z); the quotient uses safe(0)=1."""
    if not reverse:
        add_trace_term(b, a, z, d)
        divide_pair(b, z, d)
        b.swap(z, d)
    else:
        b.swap(z, d)
        divide_pair(b, z, d, True)
        add_trace_term(b, a, z, d)


def completed_outside_rotated_pivot(b, ui, uj, uk, zi, zj, zk,
                                    tj=2, tk=4, reverse=False):
    """A17 actual outside-row entry followed by a bank-rotating pivot.

    When the outside row has rank two and zi!=0, the output in zi is the
    actual derivative, with all lower-H/fiber coordinates retained in
    remaining B storage.  At lower outside rank the A17 first coordinate
    is its rank completion, not raw d; no physical derivative claim is
    made there.  The full composition has an exact inverse in all cases.
    """
    from cached_row import completed_full_outside_row
    if not reverse:
        completed_full_outside_row(b, ui, uj, uk, zj, zk, tj, tk, fast=True)
        rotated_affine_conjugate(b, ui[12:], zi, zj)
    else:
        rotated_affine_conjugate(b, ui[12:], zi, zj, True)
        completed_full_outside_row(b, ui, uj, uk, zj, zk, tj, tk,
                                   True, fast=True)
