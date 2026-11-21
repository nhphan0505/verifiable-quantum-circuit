"""Merged two-slot J-fraction extraction: one unit-series reciprocal per two slots.

The J chart stores, per slot j, the pair (c_j, a_j) with f_j = c_j / (1 + a_j x + x^2 f_{j+1}).
Two ordinary levels compose into one Mobius step that needs a single reciprocal:

    a  = f_1 / c
    v  = c + (1 + a x) f                 (v_0 = v_1 = 0, v_2 = c c')
    w  = (v[2:] / v_2)^(-1)
    z  = (w + c' x^2) / (1 + a x)        (c' = v_2 / c)
    a' = z_1,   f_{j+2} = z[2:]

The two-slot 3+1 gap repair of jfraction_gap_decoder gives five pair patterns; each
needs one reciprocal of a window that starts at position 3 once the pivot is at 2:
    A  ordinary, ordinary         as above
    B  gap in slot j              A on the series shifted by one (rotated left first)
    C  ordinary, gap in slot j+1  pivot v_3 (rotated left after the premultiply)
    D  previous gap, ordinary     pivot w_3; then c'' = w_3 / w_2, a'' = u_1 + c''
    E  previous gap, gap in j+1   pivot w_4 (rotated left); then c''' = w_4 / w_2
In B, C and E the rotated-in word is protected exactly like the original 'shortened'
word, so the original scale_active / reciprocal_active are reused unchanged.  The
final layout and the flags equal those of jfraction_gap_decoder.extract_gap, so the
conversion, the Forney scan and the reverse conversion are unchanged.
"""
from __future__ import annotations

from contextlib import contextmanager

from jfraction_gap_decoder import (GF, add_scaled, reciprocal_active, rotate,
                                   toggle_gap)
from jfraction_decoder import scale_words


def _not(b, q):
    b.x(q)


def scale_active(b, pivot, words, shortened, *, divide):
    """jfraction_gap_decoder.scale_active with the HMR-cleared word reused as the AND mask.

    Same gates as SomeJoint's version; only the 12-qubit mask allocation is
    shared with the temporary that HMR has just reset (idea credited to
    anazemcev's compact DQI notebook), which lowers the peak by one word.
    """
    zero = b.alloc_qubits(1)[0]
    b.flip_if_equal(pivot, 0, target=zero)
    b.cx(zero, pivot[0])
    inverse, scaffold = b.init_gf2_inverse_with_scaffold(pivot, field=GF)
    temporary = b.alloc_qubits(12)
    factor, undo_factor = (inverse, pivot) if divide else (pivot, inverse)
    for word in words[:-1]:
        b.ixor_gf2_mul(word, factor, target=temporary, field=GF)
        b.swap(word, temporary)
        b.del_gf2_mul(word, undo_factor, target=temporary, field=GF)
    word = words[-1]
    b.ixor_gf2_mul(word, factor, target=temporary, field=GF)
    b.x(shortened)
    b.cswap(shortened, word, temporary)
    mask = b.alloc_bits(12)
    b.hmr(temporary, mask)
    b.gf2_phase_by_product(word, factor, mask=mask, field=GF)
    b.init_and(shortened, word, temporary)
    b.cx(undo_factor, factor)
    b.gf2_phase_by_product(temporary, factor, mask=mask, field=GF)
    b.cx(undo_factor, factor)
    b.del_and(shortened, word, temporary)
    b.free(mask)
    b.x(shortened)
    b.free(temporary)
    b.del_gf2_inverse_with_scaffold(pivot, target=inverse, scaffold=scaffold, field=GF)
    b.free(inverse + scaffold)
    b.cx(zero, pivot[0])
    b.flip_if_equal(pivot, 0, target=zero)
    b.free(zero)


def _scale_by(b, fac, word, *, divide):
    scale_words(b, fac, [word], divide=divide)


def _discard_scaffold(b, pivot, control, scaffold):
    """MBU-erase the norm/reciprocal scaffold of init_controlled_inverse, keeping its output.

    Mirrors the inner part of quotient.del_controlled_inverse (scaffold
    discarding idea credited to anazemcev's compact DQI notebook).
    """
    basis, nb = b.bases[12], b.native
    norm, reciprocal, chain = scaffold[:6], scaffold[6:12], scaffold[12:]
    basis.change_basis(nb, pivot, to_tower=True)
    a, c = pivot[:6], pivot[6:]
    b.del_controlled_inverse(norm, control, target=reciprocal, scaffold=chain)
    nb.free(reciprocal + chain)
    basis.add_linear(nb, c, norm, basis.delta_square_columns)
    basis.add_linear(nb, a, norm, basis.square_columns)
    nb.del_gf2_mul(a, c, target=norm, field=basis.inner)
    nb.free(norm)
    basis.change_basis(nb, pivot, to_tower=False)


def _rebuild_scaffold(b, pivot, control):
    """Recompute the scaffold that _discard_scaffold erased (about 36 Toffolis)."""
    basis, nb = b.bases[12], b.native
    basis.change_basis(nb, pivot, to_tower=True)
    a, c = pivot[:6], pivot[6:]
    norm = b.init_gf2_mul(a, c, field=basis.inner)
    basis.add_linear(nb, a, norm, basis.square_columns)
    basis.add_linear(nb, c, norm, basis.delta_square_columns)
    reciprocal, chain = b.init_controlled_inverse(norm, control)
    basis.change_basis(nb, pivot, to_tower=False)
    return norm + reciprocal + chain


def _phase_word(b, word, mask):
    """(-1)^(mask . word): Z on each bit of word whose mask bit is set."""
    for q, m in zip(word, mask):
        b.push_condition(m)
        b.z(q)
        b.pop_condition()


def _pair(b, act, prev, gj, gj1, *, reverse):
    m = len(act)
    assert m >= 6 and m % 2 == 0
    # pre = 1 - prev (modes A, B, C). The previous flag's own qubit is negated in
    # place for the pair's duration; only the first pair (no previous slot) allocates.
    own_pre = prev is False
    pre = b.alloc_qubits(1)[0] if own_pre else prev

    def flip_pre():
        b.x(pre)

    # ---- premultiply on the (B-shifted) frame: a = f1 / c, v = c + (1 + a x) f ----
    def scale_a(divide):
        """act[1] /= c (divide) or *= c (undo) when pre; unchanged otherwise.

        Neither the factor u = pre ? c : 1 nor its inverse f = pre ? 1/c : 1 gets
        a word of its own: f lives in the controlled-inverse register, u is
        applied as 1 + pre*(c + 1) through the HMR-cleared temporary.
        """
        word, pivot = act[1], act[0]
        zero = b.alloc_qubits(1)[0]
        b.flip_if_equal(pivot, 0, target=zero)
        b.cx(zero, pivot[0])
        mask = b.alloc_bits(12)

        def open_inverse():
            inv, scaf = b.init_controlled_inverse(pivot, pre, target='alloc')
            _not(b, pre)
            b.cx(pre, inv[0])                      # f = pre ? 1/c : 1
            _not(b, pre)
            return inv, scaf

        def close_inverse(inv, scaf):
            _not(b, pre)
            b.cx(pre, inv[0])
            _not(b, pre)
            b.del_controlled_inverse(pivot, pre, target=inv, scaffold=scaf)
            b.free(inv + scaf)

        if divide:
            inverse, scaffold = open_inverse()
            _discard_scaffold(b, pivot, pre, scaffold)
            temporary = b.alloc_qubits(12)
            b.ixor_gf2_mul(word, inverse, target=temporary, field=GF)
            b.swap(word, temporary)
            # Erase old = new * u = new + pre*new*(c + 1).
            b.hmr(temporary, mask)
            _phase_word(b, word, mask)
            b.init_and(pre, word, temporary)
            b.x(pivot[0])
            b.gf2_phase_by_product(temporary, pivot, mask=mask, field=GF)
            b.x(pivot[0])
            b.del_and(pre, word, temporary)
            b.free(temporary)
            close_inverse(inverse, _rebuild_scaffold(b, pivot, pre))
        else:
            # f is computed first and its scaffold erased by measurement, so the
            # inverse's internal peak never overlaps the two words used below.
            inverse, scaffold = open_inverse()
            _discard_scaffold(b, pivot, pre, scaffold)
            temporary = b.alloc_qubits(12)
            # temporary = old * u = old + pre*old*(c + 1).
            b.cx(word, temporary)
            masked = b.alloc_qubits(12)
            b.init_and(pre, word, masked)
            b.x(pivot[0])
            b.ixor_gf2_mul(masked, pivot, target=temporary, field=GF)
            b.x(pivot[0])
            b.del_and(pre, word, masked)
            b.free(masked)
            b.swap(word, temporary)
            # Erase old = new * f = new + pre*new*(f + 1).
            b.hmr(temporary, mask)
            _phase_word(b, word, mask)
            b.init_and(pre, word, temporary)
            b.x(inverse[0])
            b.gf2_phase_by_product(temporary, inverse, mask=mask, field=GF)
            b.x(inverse[0])
            b.del_and(pre, word, temporary)
            b.free(temporary)
            scaffold = _rebuild_scaffold(b, pivot, pre)
            close_inverse(inverse, scaffold)
        b.free(mask)
        b.cx(zero, pivot[0])
        b.flip_if_equal(pivot, 0, target=zero)
        b.free(zero)

    def premultiply(forward):
        aeff = b.alloc_qubits(12)
        b.init_and(pre, act[1], aeff)

        def last_step():
            # The last word is the protected zero in B: multiply by aeff * not gj.
            alast = b.alloc_qubits(12)
            _not(b, gj)
            b.init_and(gj, aeff, alast)
            _not(b, gj)
            b.ixor_gf2_mul(alast, act[m - 2], target=act[m - 1], field=GF)
            _not(b, gj)
            b.del_and(gj, aeff, alast)
            _not(b, gj)
            b.free(alast)

        def k_step(k):
            b.ixor_gf2_mul(aeff, act[k - 1], target=act[k], field=GF)

        def square_step():
            # v2 += pre * a^2 * c; aeff already carries the pre factor.
            square = b.alloc_qubits(12)
            add_scaled(b, aeff, square, frobenius=2)
            b.ixor_gf2_mul(square, act[0], target=act[2], field=GF)
            add_scaled(b, aeff, square, frobenius=2)
            b.free(square)

        if forward:
            last_step()
            for k in range(m - 2, 2, -1):
                k_step(k)
            square_step()
        else:
            square_step()
            for k in range(3, m - 1):
                k_step(k)
            last_step()
        b.del_and(pre, act[1], aeff)
        b.free(aeff)

    # ---- shared window: pivot at 2, window from 3, last word protected by gj ^ gj1 ----
    def window(forward):
        rotate(b, act, gj1, left=True)
        b.cx(gj, gj1)                   # gj1 holds the protection gj ^ gj1 meanwhile
        if forward:
            scale_active(b, act[2], act[3:], gj1, divide=True)
            reciprocal_active(b, [1] + act[3:], gj1)
        else:
            reciprocal_active(b, [1] + act[3:], gj1, reverse=True)
            scale_active(b, act[2], act[3:], gj1, divide=False)
        b.cx(gj, gj1)
        rotate(b, act, gj1, left=False)

    # ---- post-processing (A and B share it; B still shifted) ----
    modes = []

    def set_modes():
        modes[:] = [b.alloc_qubits(1)[0] for _ in range(7)]
        ab, mc, md, me, nonzero, ab2, post = modes
        _not(b, gj1)
        b.init_and(pre, gj1, ab)
        _not(b, pre)
        b.init_and(pre, gj1, md)
        _not(b, gj1)
        b.init_and(pre, gj1, me)
        _not(b, pre)
        b.init_and(pre, gj1, mc)
        b.flip_if_equal(act[2], 0, target=nonzero)
        _not(b, nonzero)
        b.init_and(ab, nonzero, ab2)
        b.cx(ab2, post)
        b.cx(mc, post)

    def clear_modes():
        ab, mc, md, me, nonzero, ab2, post = modes
        b.cx(mc, post)
        b.cx(ab2, post)
        b.del_and(ab, nonzero, ab2)
        _not(b, nonzero)
        b.flip_if_equal(act[2], 0, target=nonzero)
        b.del_and(pre, gj1, mc)
        _not(b, pre)
        b.del_and(pre, gj1, me)
        _not(b, gj1)
        b.del_and(pre, gj1, md)
        _not(b, pre)
        b.del_and(pre, gj1, ab)
        _not(b, gj1)
        for q in modes:
            b.free(q)
        modes.clear()

    def scale_pivot(divide):
        """Pivot (2 for A/B/D, 3 for C/E) /= c (A/B/C) or w_2 (D/E).

        The divisor is brought into act[0] by a controlled swap instead of
        being copied into a separate factor word.
        """
        b.cswap(gj1, act[2], act[3])
        _not(b, pre)
        b.cswap(pre, act[0], act[1])
        _not(b, pre)
        _scale_by(b, act[0], act[2], divide=divide)
        _not(b, pre)
        b.cswap(pre, act[0], act[1])
        _not(b, pre)
        b.cswap(gj1, act[2], act[3])

    def additions():
        ab, mc, md, me = modes[:4]
        b.gf2_iadd(act[2], target=act[4], control=ab, field=GF)
        if m > 6:
            b.gf2_iadd(act[3], target=act[6], control=mc, field=GF)
        b.gf2_iadd(act[2], target=act[3], control=md, field=GF)
        b.gf2_iadd(act[3], target=act[5], control=me, field=GF)

    def divide_low(forward):
        mc, ab2 = modes[1], modes[5]

        def shift():
            b.gf2_iadd(act[1], target=act[3], control=ab2, field=GF)
            b.gf2_iadd(act[1], target=act[4], control=mc, field=GF)

        def carry():
            a_a = b.alloc_qubits(12)
            b.init_and(ab2, act[1], a_a)
            b.ixor_gf2_mul(a_a, act[3], target=act[4], field=GF)
            b.del_and(ab2, act[1], a_a)
            b.free(a_a)

        if forward:
            shift()
            carry()
        else:
            carry()
            shift()

    def divide_high(order):
        post = modes[6]
        a_p = b.alloc_qubits(12)
        b.init_and(post, act[1], a_p)
        a_last = b.alloc_qubits(12)
        _not(b, gj)
        b.init_and(gj, a_p, a_last)
        _not(b, gj)
        for k in order:
            b.ixor_gf2_mul(a_last if k == m - 1 else a_p, act[k - 1], target=act[k], field=GF)
        _not(b, gj)
        b.del_and(gj, a_p, a_last)
        _not(b, gj)
        b.free(a_last)
        b.del_and(post, act[1], a_p)
        b.free(a_p)

    def postprocess(forward):
        # Scaling never changes whether act[2] is zero (zero factors act as 1),
        # so the pivot scaling can run outside the mode-qubit lifetime.
        if forward:
            scale_pivot(divide=True)
            set_modes()
            additions()
            divide_low(forward=True)
            divide_high(range(5, m))
            clear_modes()
        else:
            set_modes()
            divide_high(range(m - 1, 4, -1))
            divide_low(forward=False)
            additions()
            clear_modes()
            scale_pivot(divide=False)

    if not reverse:
        toggle_gap(b, act, prev, gj)
        flip_pre()
        rotate(b, act, gj, left=True)
        scale_a(divide=True)
        premultiply(forward=True)
        toggle_gap(b, act[2:], gj, gj1)
        window(forward=True)
        postprocess(forward=True)
        rotate(b, act, gj, left=False)
        flip_pre()
    else:
        flip_pre()
        rotate(b, act, gj, left=True)
        postprocess(forward=False)
        window(forward=False)
        toggle_gap(b, act[2:], gj, gj1)
        premultiply(forward=False)
        scale_a(divide=False)
        rotate(b, act, gj, left=False)
        flip_pre()
        toggle_gap(b, act, prev, gj)
    if own_pre:
        b.free(pre)


def _codec(b, bits, *, inverse=False):
    """Bijection between the 8 no-adjacent-one 4-bit flag words and 3 bits (bit 3 -> 0)."""
    gates = (("cx", 3, 0), ("ccx", 0, 1, 3), ("cx", 3, 1), ("cx", 3, 2), ("ccx", 1, 2, 3))
    for gate in reversed(gates) if inverse else gates:
        getattr(b, gate[0])(*(bits[i] for i in gate[1:]))


class FlagBank:
    """Gap flags allocated in chronological order; closed 4-flag blocks kept in 3 qubits.

    Two adjacent gap flags are never both set (a gap's successor is its repair
    slot), so a block of four has only 8 patterns.  The 4-to-3 codec idea is
    credited to anazemcev's public compact DQI notebook.
    """

    def __init__(self, b, count):
        self.b, self.count = b, count
        self.live = {}       # flag index -> qubit, for unpacked flags
        self.packed = {}     # block -> its 3 code qubits

    def add(self, j):
        assert j not in self.live and j // 4 not in self.packed
        self.live[j] = self.b.alloc_qubits(1)[0]

    def remove(self, j):
        self.b.free(self.live.pop(j))

    def pack(self, block):
        bits = [self.live.pop(4 * block + i) for i in range(4)]
        _codec(self.b, bits)
        self.b.free(bits[3])
        self.packed[block] = bits[:3]

    def unpack(self, block):
        bits = self.packed.pop(block) + [self.b.alloc_qubits(1)[0]]
        _codec(self.b, bits, inverse=True)
        for i, q in enumerate(bits):
            self.live[4 * block + i] = q

    @contextmanager
    def access(self, indices):
        opened = sorted({i // 4 for i in indices if i >= 0 and i // 4 in self.packed})
        for block in opened:
            self.unpack(block)
        try:
            yield {i: self.live[i] for i in indices if i >= 0}
        finally:
            for block in reversed(opened):
                self.pack(block)

    def empty(self):
        return not self.live and not self.packed

    @contextmanager
    def step(self, j, width, *, reverse):
        """Flags of slots j-1 .. j+width-1 for one extraction step (new ones start at 0)."""
        closes = width == 2 and j >= 1 and (j - 1) % 4 == 3
        if not reverse:
            for s in range(j, j + width):
                self.add(s)
        elif closes:
            self.unpack((j - 1) // 4)
        with self.access(list(range(j - 1, j + width))) as f:
            yield f
        if not reverse:
            if closes:
                self.pack((j - 1) // 4)
        else:
            for s in reversed(range(j, j + width)):
                self.remove(s)

    def read(self, indices):
        return self.access(indices)


class GapPointers:
    """Gap flags kept as two 1-based 6-bit slot pointers (0 = no gap).

    The two-slot repair never has adjacent gaps and three or more first-order
    gaps occur with probability about 6e-8, so two pointers suffice (pointer
    idea credited to DePie's public retraining-study notebook).  Flags are
    decoded into single qubits only while a step uses them.
    """

    def __init__(self, b, count):
        self.b, self.count = b, count
        self.p = [b.alloc_qubits(6), b.alloc_qubits(6)]

    def _eq(self, reg, value):
        b = self.b
        flips = [reg[i] for i in range(6) if not (value >> i) & 1]
        for q in flips:
            b.x(q)
        chain = b.alloc_qubits(4)
        b.init_and(reg[0], reg[1], chain[0])
        for i in range(1, 4):
            b.init_and(chain[i - 1], reg[i + 1], chain[i])
        flag = b.alloc_qubits(1)[0]
        b.init_and(chain[3], reg[5], flag)
        for q in flips:
            b.x(q)
        return flag, chain, flips

    def _uneq(self, reg, flag, chain, flips):
        b = self.b
        for q in flips:
            b.x(q)
        b.del_and(chain[3], reg[5], flag)
        for i in reversed(range(1, 4)):
            b.del_and(chain[i - 1], reg[i + 1], chain[i])
        b.del_and(reg[0], reg[1], chain[0])
        for q in flips:
            b.x(q)
        b.free(flag)
        b.free(chain)

    def decode(self, s):
        b = self.b
        f = b.alloc_qubits(1)[0]
        for reg in self.p:
            e = self._eq(reg, s + 1)
            b.cx(e[0], f)
            self._uneq(reg, *e)
        return f

    def erase(self, s, f):
        """Measure away a qubit holding flag s; repair its phase only on outcome 1."""
        b = self.b
        m = b.alloc_bits(1)
        b.hmr(f, m)
        b.push_condition(m[0])
        for reg in self.p:
            e = self._eq(reg, s + 1)
            b.z(e[0])
            self._uneq(reg, *e)
        b.pop_condition()
        b.free(m)
        b.free(f)

    def _move(self, s, g, *, commit):
        """commit: write s+1 into p1 if empty else p2; uncommit: remove the last recorded gap s."""
        b = self.b
        p1, p2 = self.p
        probe = p1 if commit else p2
        z = self._eq(probe, 0)
        if not commit:
            b.x(z[0])                       # z = [p2 != 0]: the gap is in p2
        first = b.alloc_qubits(1)[0]        # commit: g and p1 empty; uncommit: g and gap in p2
        b.init_and(g, z[0], first)
        other = b.alloc_qubits(1)[0]
        b.cx(g, other)
        b.cx(first, other)
        if not commit:
            b.x(z[0])
        self._uneq(probe, *z)
        a, c = (p1, p2) if commit else (p2, p1)
        for i in range(6):
            if (s + 1) >> i & 1:
                b.cx(first, a[i])
                b.cx(other, c[i])
        b.cx(first, other)
        b.cx(g, other)
        b.free(other)
        # first = g and [p1 == s+1] after a commit, g and [p1 != 0] after an uncommit.
        e = self._eq(p1, s + 1 if commit else 0)
        if not commit:
            b.x(e[0])
        b.del_and(g, e[0], first)
        if not commit:
            b.x(e[0])
        self._uneq(p1, *e)
        b.free(first)

    @contextmanager
    def step(self, j, width, *, reverse):
        prev = self.decode(j - 1) if j >= 1 else None
        if not reverse:
            new = [self.b.alloc_qubits(1)[0] for _ in range(width)]
        else:
            new = [self.decode(s) for s in range(j, j + width)]
            for s in reversed(range(j, j + width)):
                self._move(s, new[s - j], commit=False)
        flags = {j + i: q for i, q in enumerate(new)}
        if prev is not None:
            flags[j - 1] = prev
        yield flags
        if not reverse:
            for s in range(j, j + width):
                self._move(s, new[s - j], commit=True)
            for s in range(j, j + width):
                self.erase(s, new[s - j])
        else:
            for q in new:
                self.b.free(q)
        if prev is not None:
            self.erase(j - 1, prev)

    @contextmanager
    def read(self, indices):
        decoded = {i: self.decode(i) for i in indices if i >= 0}
        yield decoded
        for i, q in decoded.items():
            self.erase(i, q)

    def empty(self):
        return True

    def release(self):
        self.b.free(self.p[0] + self.p[1])


def _single_slot(b, words, previous, gap, j, *, reverse):
    """The original gap-repair slot (used for the trailing odd slot)."""
    active = words[2 * j:]
    if not reverse:
        toggle_gap(b, active, previous, gap)
    shortened = b.alloc_qubits(1)[0]
    b.cx(gap, shortened)
    if j:
        b.cx(previous, shortened)
    rotate(b, active, shortened, left=True)
    if reverse:
        reciprocal_active(b, [1] + active[1:], shortened, reverse=True)
        scale_active(b, active[0], active[1:], shortened, divide=False)
    else:
        scale_active(b, active[0], active[1:], shortened, divide=True)
        reciprocal_active(b, [1] + active[1:], shortened)
    rotate(b, active, shortened, left=False)
    if j:
        b.cx(previous, shortened)
    b.cx(gap, shortened)
    b.free(shortened)
    if reverse:
        toggle_gap(b, active, previous, gap)


def extract_merged(b, words, flags, *, reverse=False):
    """Merged extraction; `flags` is a list of 35 flag qubits or a FlagBank."""
    if isinstance(flags, (FlagBank, GapPointers)):
        return _extract_banked(b, words, flags, reverse=reverse)
    slots = len(words) // 2
    assert len(flags) == slots
    pairs = slots // 2
    steps = [('pair', k) for k in range(pairs)]
    if slots % 2:
        steps.append(('slot', slots - 1))
    for kind, k in reversed(steps) if reverse else steps:
        if kind == 'pair':
            j = 2 * k
            prev = flags[j - 1] if j else False
            _pair(b, words[4 * k:], prev, flags[j], flags[j + 1], reverse=reverse)
        else:
            _single_slot(b, words, flags[k - 1] if k else False, flags[k], k, reverse=reverse)


def _extract_banked(b, words, bank, *, reverse):
    """Merged extraction with the flags supplied step by step by a FlagBank or GapPointers."""
    slots = len(words) // 2
    assert bank.count == slots
    pairs = slots // 2

    def pair(k):
        j = 2 * k
        with bank.step(j, 2, reverse=reverse) as f:
            _pair(b, words[4 * k:], f.get(j - 1, False), f[j], f[j + 1], reverse=reverse)

    def slot(j):
        with bank.step(j, 1, reverse=reverse) as f:
            _single_slot(b, words, f.get(j - 1, False), f[j], j, reverse=reverse)

    order = [('pair', k) for k in range(pairs)] + ([('slot', slots - 1)] if slots % 2 else [])
    for kind, k in reversed(order) if reverse else order:
        pair(k) if kind == 'pair' else slot(k)


def convert_banked(b, words, bank, *, reverse=False):
    """jfraction_gap_decoder.convert_gap with the flags read through a FlagBank."""
    from jfraction_decoder import conversion_layout
    from jfraction_gap_decoder import conversion_core, toggle_header
    p, q, stages = conversion_layout(words)
    stages = [(bank.count - 1 - i, *stage) for i, stage in enumerate(stages)]
    for j, x, y, old_p, old_q in reversed(stages) if reverse else stages:
        with bank.read([j - 1, j]) as f:
            pending, gap = f.get(j - 1, False), f[j]
            new_p = [x] + old_q[1:]
            rotations = [x, y] + old_q[1:]
            if reverse:
                rotate(b, new_p, gap, left=True)
                scale_words(b, x, old_q[1:], divide=True)
                toggle_header(b, y, old_q, pending)
            else:
                if j:
                    b.cswap(pending, x, y)
                rotate(b, rotations, gap, left=True)
            conversion_core(b, y, old_p, old_q, pending)
            if reverse:
                rotate(b, rotations, gap, left=False)
                if j:
                    b.cswap(pending, x, y)
            else:
                toggle_header(b, y, old_q, pending)
                scale_words(b, x, old_q[1:], divide=False)
                rotate(b, new_p, gap, left=False)
    return p, q
