"""DQI-19: rank-42 controlled multiply-add with X-measurement cleanup.

Owner: trng-hminh; Issue: https://github.com/nhphan0505/verifiable-quantum-circuit/issues/19.
Baseline decoder copied from DQI-BASELINE at e3827988aee8bd7731bbdcf6c5376cd2d5413aa5;
Apache-2.0, see src/LICENSE.txt. Only the two explicit ixor_gf2_mul call sites
in EEA's _multiply_and_add_or_sub are replaced. Native inverse/division/scaffold
and Chien/Forney phase primitives remain inherited, with 222 EEA iterations.

Solution: represent GF(4096) as a degree-four extension of GF(8), evaluate at
seven GF(8) points and reconstruct by Vandermonde interpolation. Each GF(8)
product has six binary bilinear products, giving 42 init_and operations.
Basis maps are derived from Kickmix's actual field modulus and checked on all
144 binary basis pairs before generating gates. CX parity networks compute
x*y in 12 temporary qubits. Controlled CCX copies this product into arbitrary
target (12 extra Toffoli-like gates). HMR clears the product and generates
phase (-1)^(c dot (x*y)). For each scalar bilinear term, a CZ controlled by
parity(c & output_mask) cancels this phase. Inputs and quantum scratch are
restored, independently of the accumulation control; no quantum-controlled
measurement is used. Per-term temporary ANDs use Kickmix del_and with its
own measurement/phase fixup. Arithmetic is exact, with no truncation or
intentional error. The tensor identity proves the value map; simulator tests
also check phase and workspace for all operand pairs and both controls.

Tradeoff: fewer EEA multiplication Toffolis versus more CX/CZ operations,
measurement feedback and up to 15 kernel workspace qubits. Neither the
primitive reduction nor BUILT implies a better R(epsilon_plus)*Q^2*T score.

Run from repository root with Python 3.13 and pinned dependencies:
python src/dqi/DQI-19/solution.py --config src/dqi/DQI-19/configs/rank42.json
Use --overwrite only for an intentional rebuild. Config must resolve directly
inside this experiment's configs directory; output defaults to the matching
artifact stem. See DESCRIPTION.md for derivation, validation and stop criteria.
The member runs dev_5min in the local notebook; this program only compiles.
"""

from __future__ import annotations

import argparse
from typing import Sequence

import kickmix as km

from functools import lru_cache


def _gf8_mul(a: int, b: int) -> int:
    """Multiply in GF(2)[u]/(u^3+u+1), little-endian polynomial basis."""
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & 8:
            a ^= 0b1011
    return out


def _gf8_inverse(a: int) -> int:
    if not a:
        raise ValueError('Cannot invert zero')
    return next(b for b in range(1, 8) if _gf8_mul(a, b) == 1)


@lru_cache(maxsize=1)
def rank42_tensor() -> tuple[tuple[int, int, int], ...]:
    """Derive exact (left parity, right parity, output) masks; prove on basis pairs.

    A four-dimensional tower over GF(8) reduces multiplication to seven
    evaluation products. Each GF(8) multiplication uses six binary ANDs.
    All basis conversions are derived from the actual Kickmix modulus.
    """
    field = km.GF2Field(12)
    beta = next(b for b in range(2, 4096)
                if field.mul(field.square(b), b) ^ b ^ 1 == 0)
    embedded = [0] * 8
    for a in range(8):
        for i in range(3):
            if a >> i & 1:
                embedded[a] ^= field.pow(beta, i)

    def binary_basis(t):
        pivots = {}
        for j in range(4):
            for i in range(3):
                value = field.mul(field.pow(t, j), field.pow(beta, i))
                coordinate = 1 << (3 * j + i)
                while value:
                    p = value.bit_length() - 1
                    if p not in pivots:
                        pivots[p] = (value, coordinate)
                        break
                    v, c = pivots[p]
                    value ^= v
                    coordinate ^= c
        return pivots

    t = field.primitive_element
    pivots = binary_basis(t)
    if len(pivots) != 12:
        raise ValueError('Primitive element does not give a degree-four GF(8) tower')

    def coordinates(value):
        out = 0
        while value:
            v, c = pivots[value.bit_length() - 1]
            value ^= v
            out ^= c
        return [(out >> (3 * j)) & 7 for j in range(4)]

    # Invert the 7x7 Vandermonde matrix over GF(8).
    matrix = []
    for a in range(7):
        row = [1]
        for _ in range(6):
            row.append(_gf8_mul(row[-1], a))
        matrix.append(row + [int(a == j) for j in range(7)])
    for col in range(7):
        pivot = next(j for j in range(col, 7) if matrix[j][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        inv = _gf8_inverse(matrix[col][col])
        matrix[col] = [_gf8_mul(x, inv) for x in matrix[col]]
        for row in range(7):
            if row == col:
                continue
            factor = matrix[row][col]
            matrix[row] = [x ^ _gf8_mul(factor, y)
                           for x, y in zip(matrix[row], matrix[col])]
    interpolation = [row[7:] for row in matrix]

    # Six scalar products reconstruct the unreduced quadratic convolution.
    scalar_products = []
    for i in range(3):
        weight = _gf8_mul(1 << i, 1 << i)
        for j in range(3):
            if i != j:
                weight ^= _gf8_mul(1 << i, 1 << j)
        scalar_products.append((1 << i, weight))
    for i in range(3):
        for j in range(i + 1, 3):
            scalar_products.append(((1 << i) | (1 << j),
                                    _gf8_mul(1 << i, 1 << j)))

    tensor = []
    for a in range(7):
        eval_rows = [0, 0, 0]
        for bit in range(12):
            value = 0
            for coefficient in reversed(coordinates(1 << bit)):
                value = _gf8_mul(value, a) ^ coefficient
            for i in range(3):
                if value >> i & 1:
                    eval_rows[i] |= 1 << bit
        for scalar_mask, weight in scalar_products:
            left = 0
            for i in range(3):
                if scalar_mask >> i & 1:
                    left ^= eval_rows[i]
            output = 0
            for power in range(7):
                coefficient = _gf8_mul(interpolation[power][a], weight)
                output ^= field.mul(embedded[coefficient], field.pow(t, power))
            tensor.append((left, left, output))
    if len(tensor) != 42 or any(not (l and r and p) for l, r, p in tensor):
        raise AssertionError('Invalid rank-42 factorization')
    for i in range(12):
        for j in range(12):
            output = 0
            for left, right, p in tensor:
                if left >> i & 1 and right >> j & 1:
                    output ^= p
            if output != field.mul(1 << i, 1 << j):
                raise AssertionError(f'Tensor disagrees on basis pair {i}, {j}')
    return tuple(tensor)


def _xor_mask(builder, register, mask, target):
    """XOR a selected parity into a quantum or classical scratch bit."""
    controls = [register[i] for i in range(len(register)) if mask >> i & 1]
    if controls:
        builder.cx(km.array(controls), target)


def rank42_ixor(builder, lhs, rhs, *, target, field, control=True):
    """Exact controlled target ^= lhs*rhs; 42 compute + 12 controlled-copy T.

    Inputs and arbitrary initial target are restored/preserved as required.
    Product HMR is corrected by the transpose output map and bilinear CZs.
    Both parity scratches and each temporary AND return to zero, including
    on shots with control=0. Never quantum-control an HMR instruction.
    """
    if field.degree != 12 or field.modulus != km.GF2Field(12).modulus:
        raise ValueError('Rank-42 kernel requires the default Kickmix GF(2^12)')
    if not all(len(reg) == 12 for reg in (lhs, rhs, target)):
        raise ValueError('All multiplication registers must have 12 bits')
    tensor = rank42_tensor()
    product = builder.alloc_qubits(12)
    scratch = builder.alloc_qubits(3)
    a, b, temporary = scratch
    previous_l = previous_r = 0
    for left, right, output in tensor:
        _xor_mask(builder, lhs, left ^ previous_l, a)
        _xor_mask(builder, rhs, right ^ previous_r, b)
        builder.init_and(a, b, temporary)
        builder.cx(temporary, km.array([product[i] for i in range(12)
                                        if output >> i & 1]))
        builder.del_and(a, b, temporary)
        previous_l, previous_r = left, right
    _xor_mask(builder, lhs, previous_l, a)
    _xor_mask(builder, rhs, previous_r, b)
    builder.ccx(control, product, target)

    measured = builder.alloc_bits(12)
    parity = builder.alloc_bits(1)[0]
    builder.hmr(product, measured)
    builder.bit_store(parity, False)
    previous_l = previous_r = previous_p = 0
    for left, right, output in tensor:
        _xor_mask(builder, lhs, left ^ previous_l, a)
        _xor_mask(builder, rhs, right ^ previous_r, b)
        _xor_mask(builder, measured, output ^ previous_p, parity)
        builder.push_condition(parity)
        builder.cz(a, b)
        builder.pop_condition()
        previous_l, previous_r, previous_p = left, right, output
    _xor_mask(builder, lhs, previous_l, a)
    _xor_mask(builder, rhs, previous_r, b)
    builder.free(measured)
    builder.free(parity)
    builder.free(product + scratch)


# Out-of-range address value used to park unary iteration cursors with match_qubit = |0>.
_UNREACHABLE = 1 << 63


def _active(cursor: km.UnaryIterationCursor, address_value: int, limit: int):
    """Moves `cursor` to `address_value` and returns `control and (x == address_value)`.

    When `address_value > limit` (outside the caller's upper bound `x <= limit`),
    parks `cursor` out of range and returns `False` so controlled operations
    become no-ops.
    """
    if address_value > limit:
        cursor.move_to(_UNREACHABLE)
        return False
    cursor.move_to(address_value)
    return cursor.match_qubit


def _xor_threshold(builder: km.CircuitBuilder, cursor: km.UnaryIterationCursor,
                   limit: int, target, control, value: int, *,
                   at_least: bool, lowest: int = 0) -> None:
    """Initializes or clears `target ^= control and (x >= value)` (or `x < value`)."""
    if value > limit:
        if not at_least:
            builder.cx(control, target)
        return
    if at_least:
        builder.cx(control, target)
    for u in range(lowest, value):
        builder.cx(_active(cursor, u, limit), target)


class ProosAndZalkaDecoder:
    """Builds the reversible Reed-Solomon MBUC decoder circuit (arXiv:2510.10967)."""

    def __init__(self, n_syndromes: int, field: km.GF2Field):
        if n_syndromes < 2:
            raise ValueError(f'n_syndromes must be at least 2, got {n_syndromes}.')
        self.n_syndromes = n_syndromes
        self.field = field

    def build_syndrome_decoding_mbuc(self, builder: km.CircuitBuilder, *,
                                     syndromes: Sequence[km.array],
                                     error_mbuc: Sequence[km.array],
                                     n_iters: int) -> None:
        """Appends the syndrome-decoding MBUC phase circuit to `builder`.

        Args:
            builder: Circuit builder receiving the instructions.
            syndromes: `n_syndromes` quantum registers of width `field.degree`.
                Restored to their initial state on completion.
            error_mbuc: Classical bit registers of width `field.degree`, one per
                codeword position, holding X-basis measurement outcomes.
            n_iters: Number of synchronized EEA iterations (`default_n_iters(n)`).
        """
        gf = self.field
        n = self.n_syndromes
        degree = gf.degree
        if len(syndromes) != n:
            raise ValueError(f'Expected {n} syndrome registers, got {len(syndromes)}.')
        if not (n <= len(error_mbuc) <= (1 << degree) - 1):
            raise ValueError(
                f'Expected between {n} and {(1 << degree) - 1} error_mbuc registers, '
                f'got {len(error_mbuc)}.'
            )
        if any(len(s) != degree for s in syndromes):
            raise ValueError(f'Every syndrome register must have length {degree}.')
        if any(len(e) != degree for e in error_mbuc):
            raise ValueError(f'Every error_mbuc register must have length {degree}.')
        m = n + 3

        reg_a = [builder.alloc_qubits(degree) if i < 3 else syndromes[i - 3] for i in range(m)]
        reg_b = [builder.alloc_qubits(degree) for _ in range(m)]

        logm = m.bit_length() + 1
        n_A = builder.alloc_qubits(logm)
        n_B = builder.alloc_qubits(logm)
        n_a = builder.alloc_qubits(logm)
        n_b = builder.alloc_qubits(logm)
        n_q = builder.alloc_qubits(logm)
        flag = builder.alloc_qubits(1)[0]
        counter = builder.alloc_qubits(2)
        halting_counter = builder.alloc_qubits(n_iters.bit_length())
        eea = (reg_a, reg_b, n_A, n_B, n_a, n_b, n_q, flag, counter, halting_counter)

        init_ones = km.array([reg_a[0][0], reg_b[m - 1][0], n_a[0], flag])
        builder.x(init_ones)
        builder.gf2_iadd(n, target=n_A)
        builder.gf2_iadd(n + 1, target=n_B)

        with builder.mark('initial_shift'):
            self._initial_shift_loop(builder, reg_a, n_A, is_adjoint=False)
        with builder.mark('forward_eea'):
            self._synchronized_eea(builder, *eea, n_iters=n_iters, is_adjoint=False)
        with builder.mark('chien_forney_mbuc'):
            self._chien_search_and_forney_mbuc(builder, reg_b, error_mbuc, n_b, n_B)
        with builder.mark('reverse_eea'):
            self._synchronized_eea(builder, *eea, n_iters=n_iters, is_adjoint=True)
        with builder.mark('uncompute_initial_shift'):
            self._initial_shift_loop(builder, reg_a, n_A, is_adjoint=True)

        builder.gf2_iadd(n + 1, target=n_B)
        builder.gf2_iadd(n, target=n_A)
        builder.x(init_ones)

        for reg in (halting_counter, counter, flag, n_q, n_b, n_a, n_B, n_A, *reg_a[:3], *reg_b):
            builder.free(reg)

    def _initial_shift_loop(self, builder: km.CircuitBuilder,
                            reg_a: Sequence[km.array], n_A: km.array, *,
                            is_adjoint: bool) -> None:
        """Left-aligns the syndrome polynomial in `reg_a` and updates `n_A`."""
        n = self.n_syndromes
        m = len(reg_a)
        shift_step = builder.mark('shift_step')
        for step in (range(n - 2, -1, -1) if is_adjoint else range(n - 1)):
            with shift_step:
                ctrl = builder.alloc_qubits(1)[0]
                if is_adjoint:
                    builder.flip_if_less_than(n_A, n - step, target=ctrl)
                    builder.iadd(1, target=n_A, control=ctrl)
                    for b in range(self.field.degree):
                        lane = km.array([r[b] for r in reg_a[3 + step:m]])
                        builder.right_rotate(lane, 1, control=ctrl)
                    builder.flip_if_equal(reg_a[m - 1], 0, target=ctrl)
                else:
                    builder.flip_if_equal(reg_a[m - 1], 0, target=ctrl)
                    for b in range(self.field.degree):
                        lane = km.array([r[b] for r in reg_a[3 + step:m]])
                        builder.left_rotate(lane, 1, control=ctrl)
                    builder.isub(1, target=n_A, control=ctrl)
                    builder.flip_if_less_than(n_A, n - step, target=ctrl)
                builder.free(ctrl)

    def _synchronized_eea(self, builder: km.CircuitBuilder,
                          reg_a: Sequence[km.array], reg_b: Sequence[km.array],
                          n_A: km.array, n_B: km.array, n_a: km.array,
                          n_b: km.array, n_q: km.array, flag,
                          counter: km.array, halting_counter: km.array, *,
                          n_iters: int, is_adjoint: bool) -> None:
        """Runs `n_iters` steps of the reversible synchronized EEA."""
        eea_step = builder.mark('eea_step')
        for it in (range(n_iters - 1, -1, -1) if is_adjoint else range(n_iters)):
            with eea_step:
                if is_adjoint:
                    self._update_counter(builder, counter, flag, is_adjoint=True)

                is_c3 = builder.alloc_qubits(1)[0]
                builder.init_and(counter[0], counter[1], is_c3)
                if is_adjoint:
                    self._update_halting_counter(builder, n_A, n_B, n_b, halting_counter,
                                                 flag, is_c3, is_adjoint=True)

                is_hc_zero = builder.alloc_qubits(1)[0]
                builder.flip_if_equal(halting_counter, 0, target=is_hc_zero)
                ctrl = self._counter_controls(builder, counter, is_c3, is_hc_zero)

                steps = [
                    lambda: self._update_flag(builder, reg_b, n_A, n_B, n_a, n_b, n_q,
                                              flag, ctrl),
                    lambda: self._multiply_and_add_or_sub(builder, reg_a, reg_b, n_A, n_a,
                                                          n_q, ctrl, it,
                                                          is_adjoint=is_adjoint),
                    lambda: self._shift_b_array_right(builder, reg_b, n_B, n_b, flag, ctrl,
                                                      it, is_adjoint=is_adjoint),
                    lambda: self._update_metadata(builder, n_B, n_b, n_q, flag, ctrl,
                                                  is_adjoint=is_adjoint),
                    lambda: self._swap_a_and_b(builder, reg_a, reg_b, n_A, n_B, n_a, n_b,
                                               flag, ctrl),
                ]
                for step in (reversed(steps) if is_adjoint else steps):
                    step()

                self._del_counter_controls(builder, counter, is_c3, is_hc_zero, ctrl)
                builder.flip_if_equal(halting_counter, 0, target=is_hc_zero)
                builder.free(is_hc_zero)

                if not is_adjoint:
                    self._update_halting_counter(builder, n_A, n_B, n_b, halting_counter,
                                                 flag, is_c3, is_adjoint=False)
                builder.del_and(counter[0], counter[1], is_c3)
                builder.free(is_c3)
                if not is_adjoint:
                    self._update_counter(builder, counter, flag, is_adjoint=False)

    @staticmethod
    def _counter_controls(builder: km.CircuitBuilder, counter: km.array, is_c3,
                          is_hc_zero) -> km.array:
        """One-hot decodes `counter == 0..3` gated by `is_hc_zero` using 3 Toffolis."""
        ctrl = builder.alloc_qubits(4)
        c0, c1, c2, c3 = ctrl
        builder.init_and(is_hc_zero, km.array([counter[0], is_c3]), km.array([c1, c3]))
        builder.cx(km.array([is_hc_zero, c1]), c0)
        builder.init_and(c0, counter[1], c2)
        builder.cx(km.array([c2, c3]), km.array([c0, c1]))
        return ctrl

    @staticmethod
    def _del_counter_controls(builder: km.CircuitBuilder, counter: km.array, is_c3,
                              is_hc_zero, ctrl: km.array) -> None:
        c0, c1, c2, c3 = ctrl
        builder.cx(km.array([c2, c3]), km.array([c0, c1]))
        builder.del_and(c0, counter[1], c2)
        builder.cx(km.array([is_hc_zero, c1]), c0)
        builder.del_and(is_hc_zero, km.array([counter[0], is_c3]), km.array([c1, c3]))
        builder.free(ctrl)

    @staticmethod
    def _update_counter(builder: km.CircuitBuilder, counter: km.array, flag, *,
                        is_adjoint: bool) -> None:
        """Increments the 2-bit `counter` mod 4 when `flag` is set."""
        if is_adjoint:
            builder.cx(flag, counter[0])
            builder.ccx(flag, counter[0], counter[1])
        else:
            builder.ccx(flag, counter[0], counter[1])
            builder.cx(flag, counter[0])

    def _update_flag(self, builder: km.CircuitBuilder, reg_b: Sequence[km.array],
                     n_A: km.array, n_B: km.array, n_a: km.array, n_b: km.array,
                     n_q: km.array, flag, ctrl) -> None:
        """Toggles `flag` when the active EEA sub-step reaches its termination condition."""
        with builder.mark('update_flag'):
            c0, c1, c2, c3 = ctrl
            m = len(reg_b)
            aux = builder.alloc_qubits(1)[0]

            # Sub-step 0 finishes when deg(A) < deg(B) (if n_q == 0) or deg(A) == deg(B).
            builder.flip_if_less_than(n_A, n_B, target=aux, control=c0)
            builder.flip_if_equal(n_q, 0, target=flag, control=aux)
            builder.flip_if_less_than(n_A, n_B, target=aux, control=c0)
            builder.flip_if_equal(n_A, n_B, target=flag, control=c0)

            # Sub-step 1 finishes once B's leading coefficient is aligned.
            builder.flip_if_equal(n_A, n_B, target=flag, control=c1)
            builder.cx(c1, flag)
            builder.flip_if_equal(n_B, 1, target=aux, control=c1)
            builder.cx(c1, aux)
            builder.flip_if_equal(reg_b[m - 2], 0, target=flag, control=aux)
            builder.cx(c1, aux)
            builder.flip_if_equal(n_B, 1, target=aux, control=c1)

            # Sub-step 2 finishes once the auxiliary polynomial is aligned.
            builder.cx(c2, flag)
            builder.flip_if_equal(n_b, 0, target=aux, control=c2)
            builder.cx(c2, aux)
            builder.flip_if_equal(reg_b[0], 0, target=flag, control=aux)
            builder.cx(c2, aux)
            builder.flip_if_equal(n_b, 0, target=aux, control=c2)
            builder.iadd(1, target=n_b)
            builder.flip_if_equal(n_a, n_b, target=flag, control=c2)
            builder.isub(1, target=n_b)

            # Sub-step 3 finishes once all quotient terms are applied.
            builder.flip_if_equal(n_a, n_b, target=flag, control=c3)
            builder.flip_if_equal(n_q, 1, target=flag, control=c3)

            builder.free(aux)

    def _multiply_and_add_or_sub(self, builder: km.CircuitBuilder,
                                 reg_a: Sequence[km.array], reg_b: Sequence[km.array],
                                 n_A: km.array, n_a: km.array, n_q: km.array,
                                 ctrl, it: int, *, is_adjoint: bool) -> None:
        """Computes the leading-coefficient ratio `q_i` and updates `reg_b ^= q_i * reg_a`."""
        c0_hc, _, _, c3_hc = ctrl
        gf = self.field
        m = len(reg_b)

        def accumulate_quotient(index: int, control) -> None:
            with builder.mark('quotient_div'):
                ratio, scaffold = builder.init_gf2_div_with_scaffold(
                    reg_b[index], reg_a[index], field=gf)
                builder.gf2_iadd(ratio, target=q_i, field=gf, control=control)
                builder.del_gf2_div_with_scaffold(
                    reg_b[index], reg_a[index], target=ratio, scaffold=scaffold, field=gf)
                builder.free(scaffold + ratio)

        def sweep_positions() -> None:
            with builder.mark('sweep_positions'):
                lim_q = min(m - 1, 1 + it)
                lim_q1 = min(m, 1 + it)
                lim_a = min(m - 2, it // 2 + 1)
                lim_A = m - 2
                order = range(m) if is_adjoint else range(m - 1, -1, -1)

                with (
                    builder.unary_iteration(n_q, control=c0_hc) as eq_i,
                    builder.unary_iteration(n_q, control=c3_hc) as eq_ip1,
                    builder.unary_iteration(n_a, control=c3_hc) as cur_a,
                    builder.unary_iteration(n_A, control=c0_hc) as cur_A,
                ):
                    mul = builder.alloc_qubits(1)[0]

                    def endpoint(i: int) -> None:
                        _xor_threshold(builder, cur_a, lim_a, mul, c3_hc, i + 1,
                                       at_least=True, lowest=1)
                        _xor_threshold(builder, cur_A, lim_A, mul, c0_hc, m - i,
                                       at_least=True, lowest=1)

                    prev = None
                    for i in order:
                        if prev is None:
                            endpoint(i)
                        else:
                            builder.cx(
                                km.array([
                                    _active(cur_a, min(prev, i) + 1, lim_a),
                                    _active(cur_A, m - max(prev, i), lim_A),
                                ]),
                                mul,
                            )
                        prev = i

                        swaps = [a for a in (_active(eq_i, i, lim_q),
                                             _active(eq_ip1, i + 1, lim_q1))
                                 if a is not False]
                        multiplies = i < lim_a or i >= 2

                        if is_adjoint and multiplies:
                            rank42_ixor(builder, q_i, reg_a[i], target=reg_b[i], field=gf,
                                                 control=mul)
                        if len(swaps) == 1:
                            builder.cswap(swaps[0], q_i, reg_a[i])
                        elif swaps:
                            both = builder.alloc_qubits(1)[0]
                            builder.cx(km.array(swaps), both)
                            builder.cswap(both, q_i, reg_a[i])
                            builder.cx(km.array(swaps), both)
                            builder.free(both)
                        if not is_adjoint and multiplies:
                            rank42_ixor(builder, q_i, reg_a[i], target=reg_b[i], field=gf,
                                                 control=mul)

                    endpoint(prev)
                    builder.free(mul)

        with builder.mark('multiply_and_add_or_sub'):
            q_i = builder.alloc_qubits(gf.degree)
            leading, trailing = (0, m - 1) if is_adjoint else (m - 1, 0)
            accumulate_quotient(leading, c3_hc if is_adjoint else c0_hc)
            builder.iadd(n_a, target=n_q)
            sweep_positions()
            builder.isub(n_a, target=n_q)
            accumulate_quotient(trailing, c0_hc if is_adjoint else c3_hc)
            builder.free(q_i)

    def _shift_b_array_right(self, builder: km.CircuitBuilder,
                             reg_b: Sequence[km.array], n_B: km.array, n_b: km.array,
                             flag, ctrl, it: int, *, is_adjoint: bool) -> None:
        """Shifts the active slice of `reg_b` by one slot."""
        with builder.mark('shift_b_array_right'):
            c0_hc, c1_hc, c2_hc, c3_hc = ctrl
            m = len(reg_b)
            lim_B = m - 2
            lim_b = min(m - 2, it // 2 + 1)

            builder.x(flag)
            nf = builder.alloc_qubits(2)
            builder.init_and(km.array([c0_hc, c3_hc]), flag, nf)
            builder.x(flag)
            c0_nf, c3_nf = nf

            ctrl_nB = builder.alloc_qubits(1)[0]
            builder.cx(km.array([c0_nf, c1_hc]), ctrl_nB)

            order = range(1, m) if is_adjoint else range(m - 1, 0, -1)
            with (
                builder.unary_iteration(n_B, control=ctrl_nB) as cur_B_ge,
                builder.unary_iteration(n_b, control=c2_hc) as cur_b_ge,
                builder.unary_iteration(n_B, control=c3_nf) as cur_B_lt,
            ):
                do_shift = builder.alloc_qubits(1)[0]

                def endpoint(i: int) -> None:
                    _xor_threshold(builder, cur_B_ge, lim_B, do_shift, ctrl_nB, m - i + 1,
                                   at_least=True)
                    _xor_threshold(builder, cur_b_ge, lim_b, do_shift, c2_hc, i,
                                   at_least=True)
                    _xor_threshold(builder, cur_B_lt, lim_B, do_shift, c3_nf, m - i,
                                   at_least=False)

                prev = None
                for i in order:
                    if prev is None:
                        endpoint(i)
                    else:
                        builder.cx(
                            km.array([
                                _active(cur_B_ge, m - max(prev, i) + 1, lim_B),
                                _active(cur_b_ge, min(prev, i), lim_b),
                                _active(cur_B_lt, m - max(prev, i), lim_B),
                            ]),
                            do_shift,
                        )
                    prev = i
                    builder.cswap(do_shift, reg_b[i - 1], reg_b[i])

                endpoint(prev)
                builder.free(do_shift)

            builder.cx(km.array([c0_nf, c1_hc]), ctrl_nB)
            builder.free(ctrl_nB)
            builder.x(flag)
            builder.del_and(km.array([c0_hc, c3_hc]), flag, nf)
            builder.x(flag)
            builder.free(nf)

    @staticmethod
    def _update_metadata(builder: km.CircuitBuilder, n_B: km.array, n_b: km.array,
                         n_q: km.array, flag, ctrl, *, is_adjoint: bool) -> None:
        """Updates the polynomial degree registers `(n_B, n_b, n_q)`."""
        with builder.mark('update_metadata'):
            c0_hc, c1_hc, c2_hc, c3_hc = ctrl
            builder.x(flag)
            nf = builder.alloc_qubits(2)
            builder.init_and(km.array([c0_hc, c3_hc]), flag, nf)
            builder.x(flag)
            c0_nf, c3_nf = nf

            sign = -1 if is_adjoint else 1
            updates = [
                [(n_q, 1, c0_hc), (n_B, -1, c0_nf)],
                [(n_B, -1, c1_hc)],
                [(n_b, 1, c2_hc)],
                [(n_b, 1, c3_nf), (n_q, -1, c3_hc)],
            ]
            for step in (reversed(updates) if is_adjoint else updates):
                for target, offset, control in (reversed(step) if is_adjoint else step):
                    builder.iadd(sign * offset, target=target, control=control)

            builder.x(flag)
            builder.del_and(km.array([c0_hc, c3_hc]), flag, nf)
            builder.x(flag)
            builder.free(nf)

    @staticmethod
    def _swap_a_and_b(builder: km.CircuitBuilder, reg_a: Sequence[km.array],
                      reg_b: Sequence[km.array], n_A: km.array, n_B: km.array,
                      n_a: km.array, n_b: km.array, flag, ctrl) -> None:
        """Swaps `(reg_a, n_A, n_a)` and `(reg_b, n_B, n_b)` at the end of a division round."""
        with builder.mark('swap_a_and_b'):
            c3_hc = ctrl[3]
            swap_ctrl = builder.alloc_qubits(1)[0]
            builder.init_and(c3_hc, flag, swap_ctrl)
            lhs = km.array([q for r in (n_A, n_a, *reg_a) for q in r])
            rhs = km.array([q for r in (n_B, n_b, *reg_b) for q in r])
            builder.cswap(swap_ctrl, lhs, rhs)
            builder.del_and(c3_hc, flag, swap_ctrl)
            builder.free(swap_ctrl)

    @staticmethod
    def _update_halting_counter(builder: km.CircuitBuilder, n_A: km.array,
                                n_B: km.array, n_b: km.array,
                                halting_counter: km.array, flag, is_c3, *,
                                is_adjoint: bool) -> None:
        """Increments `halting_counter` once the EEA stopping criterion holds."""
        with builder.mark('update_halting_counter'):
            work = builder.alloc_qubits(3)
            ctrl, busy, running = work
            builder.init_and(is_c3, flag, ctrl)
            builder.flip_if_less_than(n_b, n_B, target=busy, control=ctrl)
            builder.cx(busy, running)
            builder.flip_if_equal(n_A, 0, target=running, control=busy)

            builder.cx(running, ctrl)
            if is_adjoint:
                builder.isub(1, target=halting_counter, control=ctrl)
            else:
                builder.iadd(1, target=halting_counter, control=ctrl)
            builder.cx(running, ctrl)

            builder.flip_if_equal(n_A, 0, target=running, control=busy)
            builder.cx(busy, running)
            builder.flip_if_less_than(n_b, n_B, target=busy, control=ctrl)
            builder.del_and(is_c3, flag, ctrl)
            builder.free(work)

    def _pre_align_reg_b(self, builder: km.CircuitBuilder, reg_b: Sequence[km.array],
                         n_b: km.array, n_B: km.array, *, is_adjoint: bool) -> None:
        """Rotates the evaluator slice of `reg_b` by `n_B - n_b` into fixed indices."""
        omega = reg_b[len(reg_b) // 2 + 1:]
        for b in range(self.field.degree):
            lane = km.array([r[b] for r in omega])
            if is_adjoint:
                builder.right_rotate(lane, n_B)
                builder.left_rotate(lane, n_b)
            else:
                builder.right_rotate(lane, n_b)
                builder.left_rotate(lane, n_B)

    def _chien_search_and_forney_mbuc(self, builder: km.CircuitBuilder,
                                      reg_b: Sequence[km.array],
                                      error_mbuc: Sequence[km.array],
                                      n_b: km.array, n_B: km.array) -> None:
        """Evaluates `sigma` and `omega` via Chien search and kicks back the Forney MBUC phase."""
        gf = self.field
        degree = gf.degree
        m = len(reg_b)
        t = self.n_syndromes // 2
        block_length = (1 << degree) - 1
        primitive = gf.primitive_element

        with builder.mark('pre_align_reg_b'):
            self._pre_align_reg_b(builder, reg_b, n_b, n_B, is_adjoint=False)

        sigma = reg_b[0]
        sigma_prime = reg_b[1]
        omega = reg_b[m // 2 + t]
        sigma_prime_inv = builder.alloc_qubits(degree)
        located = builder.alloc_qubits(degree)
        is_sigma_zero = builder.alloc_qubits(1)[0]
        is_error = builder.alloc_bits(1)

        # Fold the Forney prefactor `c_j ** -(m - 2)` (`c_j = primitive ** -j`) into
        # `omega`'s per-step multipliers so each position's polynomial evaluation is
        # a plain XOR sum followed by in-place constant multiplications.
        omega_indices = range(m // 2 + 1, m // 2 + t + 1)
        step_multipliers = [
            (k, gf.pow(primitive, k))
            for k in range(1, t + 1)
        ] + [
            (k, gf.pow(primitive, (m - 2 - k) % block_length))
            for k in omega_indices
            if (m - 2 - k) % block_length != 0
        ]

        sum_pairs = (
            [(reg_b[k], omega) for k in range(m // 2 + 1, m // 2 + t)]
            + [(reg_b[k], sigma_prime) for k in range(3, t + 1, 2)]
            + [(reg_b[k], sigma) for k in range(2, t + 1, 2)]
            + [(sigma_prime, sigma)]
        )
        fwd_src = km.array([q for src, _ in sum_pairs for q in src])
        fwd_dst = km.array([q for _, dst in sum_pairs for q in dst])
        rev_src = km.array([q for src, _ in reversed(sum_pairs) for q in src])
        rev_dst = km.array([q for _, dst in reversed(sum_pairs) for q in dst])

        num_positions = min(block_length, len(error_mbuc))
        forney_step = builder.mark('forney_step')
        for j in range(num_positions):
            with forney_step:
                builder.bit_store(is_error[0], True, control=error_mbuc[j])
                builder.push_condition(is_error[0])

                builder.cx(fwd_src, fwd_dst)
                builder.flip_if_equal(sigma, 0, target=is_sigma_zero)

                _, inverse_chain = builder.init_gf2_inverse_with_scaffold(
                    sigma_prime, target=sigma_prime_inv, field=gf)

                builder.init_and(is_sigma_zero, omega, located)
                builder.gf2_phase_by_product(located, sigma_prime_inv,
                                             mask=error_mbuc[j], field=gf)
                builder.del_and(is_sigma_zero, omega, located)

                builder.del_gf2_inverse_with_scaffold(
                    sigma_prime, target=sigma_prime_inv, scaffold=inverse_chain, field=gf)
                builder.free(inverse_chain)

                builder.flip_if_equal(sigma, 0, target=is_sigma_zero)
                builder.cx(rev_src, rev_dst)

                builder.pop_condition()
                builder.bit_store(is_error, False)

                if j + 1 < num_positions:
                    for k, step in step_multipliers:
                        builder.gf2_imul(step, target=reg_b[k], field=gf)

        if num_positions > 1:
            for k, step in step_multipliers:
                builder.gf2_idiv(
                    gf.pow(step, num_positions - 1), target=reg_b[k], field=gf)

        builder.free(is_error)
        builder.free(located + sigma_prime_inv + km.array([is_sigma_zero]))

        with builder.mark('unalign_reg_b'):
            self._pre_align_reg_b(builder, reg_b, n_b, n_B, is_adjoint=True)


def default_n_iters(n_syndromes: int) -> int:
    """Returns the EEA iteration count `3 * (n_syndromes + 1) + 9`."""
    return 3 * (n_syndromes + 1) + 9


def build_reference_circuit(m: int, n: int, degree: int) -> km.Circuit:
    """Builds the standalone reference Reed-Solomon MBUC decoder circuit."""
    builder = km.CircuitBuilder()
    syndromes = [builder.create_quantum_register(degree, name=f'S{i}') for i in range(n)]
    error_mbuc = [builder.create_classical_register(degree, name=f'E{j}') for j in range(m)]
    ProosAndZalkaDecoder(n, km.GF2Field(degree)).build_syndrome_decoding_mbuc(
        builder, syndromes=syndromes, error_mbuc=error_mbuc, n_iters=default_n_iters(n))
    return builder.finish_circuit()


def validate_kernel(*, exhaustive=False):
    """Test emitted value/phase/workspace, independently of the decoder verifier.

    Exhaustive covers every ordered operand pair with each control value and
    arbitrary deterministic target. Non-exhaustive covers basis/edge/random
    operands with three independent HMR seeds. Reference multiplication uses
    NumPy polynomial arithmetic rather than the bilinear factorization.
    """
    import numpy as np
    field = km.GF2Field(12)
    builder = km.CircuitBuilder()
    x = builder.create_quantum_register(12, 'x')
    y = builder.create_quantum_register(12, 'y')
    z = builder.create_quantum_register(12, 'z')
    c = builder.create_quantum_register(1, 'c')[0]
    rank42_ixor(builder, x, y, target=z, field=field, control=c)
    circuit = builder.finish_circuit()
    native = km.CircuitBuilder()
    nx = native.create_quantum_register(12, 'x')
    ny = native.create_quantum_register(12, 'y')
    nz = native.create_quantum_register(12, 'z')
    nc = native.create_quantum_register(1, 'c')[0]
    native.ixor_gf2_mul(nx, ny, target=nz, field=field, control=nc)
    native_circuit = native.finish_circuit()
    if circuit.operation_statistics().num_toffoli_like != 54:
        raise AssertionError('Controlled rank-42 kernel must have 54 Toffoli-like gates')
    mask_bits = np.arange(12, dtype=np.uint32)[:, None]
    def bits(values):
        return ((values[None, :] >> mask_bits) & 1).astype(bool)
    def multiply(a, b):
        out = np.zeros_like(a)
        a = a.copy()
        for i in range(12):
            out ^= np.where((b >> i) & 1, a, 0).astype(np.uint32)
            a <<= 1
            a ^= np.where(a & 4096, field.modulus, 0).astype(np.uint32)
        return out
    if exhaustive:
        count, batch, seeds = 1 << 24, 65536, (1901,)
    else:
        count, batch, seeds = 65536, 65536, (1901, 1902, 1903)
    shots_checked = 0
    import time
    started = time.monotonic()
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for start in range(0, count, batch):
            indexes = np.arange(start, min(start + batch, count), dtype=np.uint32)
            if exhaustive:
                xv, yv = indexes & 4095, indexes >> 12
            else:
                xv = rng.integers(0, 4096, len(indexes), dtype=np.uint32)
                yv = rng.integers(0, 4096, len(indexes), dtype=np.uint32)
                edges = [0, 1, 4095] + [1 << i for i in range(12)]
                for i, a in enumerate(edges):
                    for j, b in enumerate(edges):
                        xv[i * len(edges) + j] = a
                        yv[i * len(edges) + j] = b
            zv = ((xv * 197) ^ (yv * 313) ^ indexes) & 4095
            product = multiply(xv, yv)
            for control in (False, True):
                sim = km.Simulator(len(indexes), seed=seed + start + int(control),
                                   debug_print=False)
                sim.use_same_registers_as(circuit)
                sim.write_across_shots(x, bits(xv))
                sim.write_across_shots(y, bits(yv))
                sim.write_across_shots(z, bits(zv))
                sim.write_across_shots(c, np.full(len(indexes), control, dtype=bool))
                sim.do(circuit)
                expected = zv ^ product if control else zv
                for register, values in ((x, xv), (y, yv), (z, expected)):
                    if not np.array_equal(sim.read_across_shots(register), bits(values)):
                        raise AssertionError('Kernel changed an input or produced wrong output')
                if not np.all(sim.read_across_shots(c) == control):
                    raise AssertionError('Kernel changed its quantum control')
                # Registers are allocated first and scratch is the suffix 37..51.
                ancillas = km.array([km.q(i) for i in range(37, circuit.num_qubits)])
                if sim.read_across_shots(ancillas).any():
                    raise AssertionError('Kernel left nonzero quantum workspace')
                if sim.read_phase_flipped_across_shots().any():
                    raise AssertionError('Kernel left an unwanted phase')
                shots_checked += len(indexes)
            if exhaustive and (start // batch + 1) % 32 == 0:
                print(f'Kernel validation: {shots_checked:,} cases checked', flush=True)
    return {'tensor_basis_pairs': 144, 'rank': len(rank42_tensor()),
            'exhaustive_operand_pairs': exhaustive, 'control_values': [0, 1],
            'shots_checked': shots_checked, 'measurement_seeds': list(seeds),
            'value_errors': 0, 'phase_errors': 0, 'workspace_errors': 0,
            'kernel_toffoli_like': circuit.operation_statistics().num_toffoli_like,
            'native_toffoli_like': native_circuit.operation_statistics().num_toffoli_like,
            'kernel_qubits': circuit.num_qubits,
            'native_qubits': native_circuit.num_qubits,
            'elapsed_seconds': time.monotonic() - started,
            'verification_level': 'isolated multiplication kernel, not decoder grading'}


def main() -> None:
    import json
    from pathlib import Path
    experiment_dir = Path(__file__).resolve().parent
    track = experiment_dir.parent.name
    experiment_id = experiment_dir.name
    root = experiment_dir.parents[2]
    if experiment_dir.parent.parent.name != 'src' or track not in {'invsqrt', 'dqi', 'dfthcsos'}:
        raise ValueError('solution.py must be located at src/<TRACK>/<ID>/solution.py')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-kernel', choices=('sampled', 'exhaustive'), help='Only test the isolated multiplication kernel; no decoder grading')
    parser.add_argument('--config', type=Path, default=Path(__file__).parent/'configs/rank42.json')
    parser.add_argument('--output', type=Path, help='Optional output path; filename must match config stem')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing generated artifact')
    args = parser.parse_args()
    if args.validate_kernel:
        print(json.dumps(validate_kernel(exhaustive=args.validate_kernel == 'exhaustive'), indent=2))
        return
    args.config = args.config.resolve()
    config_dir = (experiment_dir/'configs').resolve()
    if args.config.parent != config_dir or args.config.suffix != '.json':
        raise ValueError('Config must be a JSON file directly inside this experiment configs/ directory')
    import re
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.config.stem):
        raise ValueError('Config name must contain only letters, digits, hyphens or underscores and start with a letter/digit')
    config = json.loads(args.config.read_text(encoding='utf-8'))
    if config != {'m': 4095, 'n': 70, 'degree': 12}: 
        raise ValueError('This experiment requires m=4095, n=70, degree=12')
    output = args.output or root/'artifacts'/track/experiment_id/f'{args.config.stem}.kmb'
    if output.name != args.config.stem+'.kmb':
        raise ValueError('Output filename must be <config-name>.kmb')
    if output.exists() and not args.overwrite:
        raise FileExistsError(f'{output} exists; pass --overwrite to rebuild')
    output.parent.mkdir(parents=True, exist_ok=True)
    circuit = build_reference_circuit(config['m'], config['n'], config['degree'])
    circuit.to_file(str(output), format='kmb')
    print(f'Wrote {output}: {circuit.operation_statistics().num_toffoli_like:,} Toffolis, {circuit.num_qubits} qubits.')


if __name__ == '__main__':
    main()
