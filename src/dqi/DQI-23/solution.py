"""Compile DQI-23's reversible continued-fraction decoder to Kickmix.

The quantum input is the GF(2^degree) Laurent prefix of a rational function.
A valuation-d Schur step inverts its unit series and replaces the first 2d
words with the quotient block. Nonzero leading coefficients mark its end,
and a short cursor tracks the boundary between quotient and syndrome words.
The reciprocal factors the normalized series into units (1+p_i*z^i), then
multiplies their inverses. Both sweeps use triangular XOR updates. There is
no coefficient approximation or cutoff on d within the Reed–Solomon promise.

The converter walks the blocks backwards, using a leading-first interleaved
monic denominator and numerator. Padding by a shared power of x keeps the
layout independent of the decoded weight. After the Chien/Forney phase sweep
the converter and extraction run backwards. Kickmix's inverse, product and
AND cleanup primitives account for their own measurement phase corrections.
The verifier's runtime masks are classical and the syndrome remains quantum.

Run with --config src/dqi/DQI-23/configs/schur.json. The artifact is intended
for the notebook verifier. Build statistics count emitted gates, rather than
a verifier score.
"""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re

import kickmix as km


class SchurDecoder:
    """Emit the packed block extraction, converter and phase sweep."""

    def __init__(self, builder, field, syndromes):
        self.b = builder
        self.gf = field
        self.words = syndromes
        self.capacity = len(syndromes) // 2
        self.inverse_tables = self.subfield_tables() if field.degree == 12 else None

    def subfield_tables(self):
        """Express the norm and multiplication in a binary GF(64) basis."""
        gf = self.gf
        elements = [0]
        basis = []
        for a in range(1, 1 << gf.degree):
            if gf.pow(a, 64) == a and a not in elements:
                basis.append(a)
                elements += [x ^ a for x in elements]
        coords = {x: i for i, x in enumerate(elements)}
        conjugates = [gf.pow(1 << i, 64) for i in range(gf.degree)]
        linear = [coords[gf.mul(1 << i, a)] for i, a in enumerate(conjugates)]
        quadratic = [
            (i, j, coords[gf.mul(1 << i, conjugates[j]) ^ gf.mul(1 << j, conjugates[i])])
            for i in range(gf.degree) for j in range(i)
        ]
        inverse = [0] + [coords[gf.invert(x)] for x in elements[1:]]
        product = [[gf.mul(a, u) for u in basis] for a in conjugates]
        return linear, quadratic, inverse, product

    def quadratic_add(self, left, right, mask, target, work):
        if mask:
            self.b.init_and(left, right, work)
            self.b.gf2_iadd(mask, target=target, control=work)
            self.b.del_and(left, right, work)

    def inverse_add(self, word, target, *, undo=False):
        """XOR the inverse using conjugate/norm, including inverse(0)=0."""
        b, gf = self.b, self.gf
        if self.inverse_tables is None:
            if undo:
                b.del_gf2_inverse(word, target=target, field=gf)
            else:
                b.init_gf2_inverse(word, target=target, field=gf)
            return
        linear, quadratic, inverse, product = self.inverse_tables
        norm = b.alloc_qubits(6)
        inverse_norm = b.alloc_qubits(6)
        work = b.alloc_qubits(1)[0]

        def norm_add():
            for bit, mask in zip(word, linear):
                b.gf2_iadd(mask, target=norm, control=bit)
            for i, j, mask in quadratic:
                self.quadratic_add(word[i], word[j], mask, norm, work)

        def lookup():
            for i, mask in enumerate(inverse):
                if mask:
                    with self.equal(norm, i) as selected:
                        b.gf2_iadd(mask, target=inverse_norm, control=selected)

        norm_add()
        lookup()
        for bit, row in zip(word, product):
            for coeff, mask in zip(inverse_norm, row):
                self.quadratic_add(bit, coeff, mask, target, work)
        lookup()
        norm_add()
        b.free(norm + inverse_norm + km.array([work]))

    @contextmanager
    def flag(self, toggle):
        bit = self.b.alloc_qubits(1)[0]
        toggle(bit)
        yield bit
        toggle(bit)
        self.b.free(bit)

    def equal(self, word, value):
        return self.flag(lambda bit: self.b.flip_if_equal(word, value, target=bit))

    def between(self, jump, lo, hi):
        """Compute a flag for lo <= jump <= hi using two disjoint thresholds."""
        def toggle(bit):
            self.b.flip_if_less_than(jump, lo, target=bit)
            if hi + 1 < (1 << len(jump)):
                self.b.flip_if_less_than(jump, hi + 1, target=bit)
            else:
                self.b.x(bit)
        return self.flag(toggle)

    def swap_order(self, words, order, control, reverse=False):
        """Implement a fixed positional permutation with conditional swaps."""
        labels = list(range(len(order)))
        positions = labels[:]
        swaps = []
        for i, label in enumerate(order):
            j = positions[label]
            if i != j:
                swaps.append((i, j))
                positions[labels[i]], positions[label] = j, i
                labels[i], labels[j] = labels[j], labels[i]
        for i, j in reversed(swaps) if reverse else swaps:
            self.b.cswap(control, words[i], words[j])

    def rotate(self, words, jump, max_jump, reverse=False):
        for d in range(2, max_jump + 1):
            with self.equal(jump, d) as selected:
                order = list(range(d - 1, len(words))) + list(range(d - 1))
                self.swap_order(words, order, selected, reverse)

    def encode_jump(self, words, active, jump):
        """XOR the one-based index of the first nonzero word into jump."""
        prefix = self.b.alloc_qubits(len(words))
        live = active
        for i, next_live in enumerate(prefix):
            self.b.flip_if_equal(words[i], 0, target=next_live, control=live)
            self.b.gf2_iadd(i + 1, target=jump, control=live)
            self.b.gf2_iadd(i + 1, target=jump, control=next_live)
            live = next_live
        for i in reversed(range(len(prefix))):
            live = active if i == 0 else prefix[i - 1]
            self.b.flip_if_equal(words[i], 0, target=prefix[i], control=live)
        self.b.free(prefix)

    def toggle_start(self, start, target, control=True):
        """Toggle when the previous numerator slot marks a block end."""
        self.b.cx(control, target)
        if start:
            self.b.flip_if_equal(self.words[2*start-1], 0, target=target, control=control)

    def toggle_extracted_start(self, cursor, start, target):
        with self.between(cursor, start, self.capacity) as packed:
            self.toggle_start(start, target, packed)

    def move_cursor(self, cursor, start, jump, cap):
        for d in range(1, cap + 1):
            with self.equal(jump, d) as selected:
                self.b.gf2_iadd(start ^ (start + d), target=cursor, control=selected)

    def scale(self, word, factor, inverse, temp, control):
        """Controlled in-place multiplication with clean product workspace."""
        self.b.ixor_gf2_mul(word, factor, target=temp, field=self.gf, control=control)
        self.b.cswap(control, word, temp)
        self.b.ixor_gf2_mul(word, inverse, target=temp, field=self.gf, control=control)

    def square_add(self, word, target, control):
        masked = self.b.alloc_qubits(1)[0]
        for i, bit in enumerate(word):
            self.b.init_and(control, bit, masked)
            self.b.gf2_iadd(self.gf.square(1 << i), target=target, control=masked)
            self.b.del_and(control, bit, masked)
        self.b.free(masked)

    def reciprocal(self, words, jump):
        """Replace a truncated series by its reciprocal, preserving padding."""
        b, gf = self.b, self.gf
        degree = gf.degree
        length = len(words)
        max_jump = length // 2
        inv = b.alloc_qubits(degree)
        self.inverse_add(words[0], inv)
        temp = b.alloc_qubits(degree)
        for k in range(1, length):
            with self.between(jump, 1, length - k) as valid:
                self.scale(words[k], inv, words[0], temp, valid)
        b.free(temp)

        # Factor the unit series, keeping factor p_i in word i. In the active
        # series the coefficient at i becomes zero, hence the 2*i+1 bound.
        for i in range(1, length // 2):
            for k in range(2 * i + 1, length):
                with self.between(jump, 1, length - k) as valid:
                    b.ixor_gf2_mul(words[i], words[k-i], target=words[k],
                                   field=gf, control=valid)
        # Form the inverse unit series from the factors, largest i first.
        # b[2*i] gets p_i^2 and no variable product is needed there.
        for i in reversed(range(1, (length + 1) // 2)):
            with self.between(jump, 1, length - 2*i) as valid:
                self.square_add(words[i], words[2*i], valid)
            for k in range(2 * i + 1, length):
                with self.between(jump, 1, length - k) as valid:
                    b.ixor_gf2_mul(words[i], words[k-i], target=words[k],
                                   field=gf, control=valid)

        temp = b.alloc_qubits(degree)
        for k in range(1, length):
            with self.between(jump, 1, length - k) as valid:
                self.scale(words[k], inv, words[0], temp, valid)
        b.free(temp)
        with self.between(jump, 1, max_jump) as active:
            b.cswap(active, words[0], inv)
        self.inverse_add(words[0], inv, undo=True)
        b.free(inv)

    def route_quotient(self, words, jump, reverse):
        length = len(words)
        for d in range(1, length // 2 + 1):
            # After the reciprocal, place b_1..b_d in the denominator
            # slots and b_0 in the last numerator slot of this block.
            order = []
            for j in range(1, d + 1):
                order.extend((j, 0 if j == d else length - d + j))
            order.extend(range(d + 1, length - d + 1))
            with self.equal(jump, d) as selected:
                self.swap_order(words, order, selected, reverse)

    def extraction(self, cursor, reverse=False):
        indices = range(self.capacity)
        for start in reversed(indices) if reverse else indices:
            words = self.words[2*start:]
            cap = len(words) // 2
            jump = self.b.alloc_qubits(cap.bit_length())
            active = self.b.alloc_qubits(1)[0]
            if reverse:
                self.toggle_extracted_start(cursor, start, active)
                self.encode_jump(words[1::2], active, jump)
                self.move_cursor(cursor, start, jump, cap)
                self.route_quotient(words, jump, True)
                self.reciprocal(words, jump)
                self.rotate(words, jump, cap, True)
                self.encode_jump(words[:cap], active, jump)
                self.b.flip_if_equal(cursor, start, target=active)
            else:
                self.b.flip_if_equal(cursor, start, target=active)
                self.encode_jump(words[:cap], active, jump)
                self.rotate(words, jump, cap)
                self.reciprocal(words, jump)
                self.route_quotient(words, jump, False)
                self.move_cursor(cursor, start, jump, cap)
                self.encode_jump(words[1::2], active, jump)
                self.toggle_extracted_start(cursor, start, active)
            self.b.free(jump + km.array([active]))

    def at_jump_slot(self, a, jump, action):
        for d, word in enumerate(a, 1):
            with self.equal(jump, d) as selected:
                action(word, selected)

    def swap_tail(self, a, den, jump):
        for k in range(2, len(a) + 1):
            with self.between(jump, 1, k-1) as selected:
                self.b.cswap(selected, a[k-1], den[k-1])

    def scale_row(self, row, jump, factor, inverse):
        temp = self.b.alloc_qubits(self.gf.degree)
        with self.between(jump, 1, len(row)) as active:
            for word in row:
                self.scale(word, factor, inverse, temp, active)
        self.b.free(temp)

    def convolve(self, a, den, jump, reverse):
        """Add normalized q*B into the new denominator, omitting p_k*B_0."""
        b, gf = self.b, self.gf
        cap = len(a)
        terms = range(1, cap + 1)
        for k in terms if reverse else reversed(terms):
            if k < cap:
                with self.between(jump, 1, cap) as active:
                    b.gf2_iadd(a[k], target=den[k-1], control=active)
            for j in range(1, k):
                with self.between(jump, j, cap) as valid:
                    b.ixor_gf2_mul(den[j-1], a[k-j], target=den[k-1],
                                   field=gf, control=valid)

    def convert_block(self, den, a, jump, reverse):
        b, gf = self.b, self.gf
        cap = len(a)
        if reverse:
            inv = b.alloc_qubits(gf.degree)
            self.at_jump_slot(a, jump, lambda word, flag: b.gf2_iadd(word, target=inv, control=flag))
            lead = b.alloc_qubits(gf.degree)
            self.inverse_add(inv, lead)
            self.rotate(a, jump, cap)
            self.scale_row(a, jump, lead, inv)
            self.convolve(a, den, jump, True)
            self.scale_row(den, jump, lead, inv)
            self.rotate(a, jump, cap, True)
            self.swap_tail(a, den, jump)
            self.inverse_add(lead, inv, undo=True)
            self.at_jump_slot(a, jump, lambda word, flag: b.cx(flag, word[0]))
            self.at_jump_slot(a, jump, lambda word, flag: b.cswap(flag, word, lead))
        else:
            lead = b.alloc_qubits(gf.degree)
            self.at_jump_slot(a, jump, lambda word, flag: b.cswap(flag, word, lead))
            self.at_jump_slot(a, jump, lambda word, flag: b.cx(flag, word[0]))
            inv = b.alloc_qubits(gf.degree)
            self.inverse_add(lead, inv)
            self.swap_tail(a, den, jump)
            self.rotate(a, jump, cap)
            self.scale_row(den, jump, inv, lead)
            self.convolve(a, den, jump, False)
            self.scale_row(a, jump, inv, lead)
            self.rotate(a, jump, cap, True)
            self.inverse_add(inv, lead, undo=True)
            self.at_jump_slot(a, jump, lambda word, flag: b.gf2_iadd(word, target=inv, control=flag))
        b.free(inv + lead)

    def conversion(self, reverse=False):
        indices = range(self.capacity)
        for start in indices if reverse else reversed(indices):
            den = self.words[2*start::2]
            num = self.words[2*start+1::2]
            jump = self.b.alloc_qubits(len(den).bit_length())
            with self.flag(lambda bit: self.toggle_start(start, bit)) as active:
                self.encode_jump(num, active, jump)
                self.convert_block(den, num, jump, reverse)
                self.encode_jump(num, active, jump)
            self.b.free(jump)

    def phase(self, masks):
        """Chien sweep with three coefficient words used as accumulators."""
        b, gf = self.b, self.gf
        den, num = self.words[::2], self.words[1::2]
        odd = den[0]
        omega = num[0]
        sigma = den[1] if len(den) > 1 else odd
        pairs = [(word, omega) for word in num[1:]]
        pairs += [(word, odd) for word in den[2::2]]
        if len(den) > 1:
            pairs += [(word, sigma) for word in den[3::2]]
            pairs.append((odd, sigma))
        left = km.array([bit for src, _ in pairs for bit in src])
        right = km.array([bit for _, dst in pairs for bit in dst])
        back_left = km.array([bit for src, _ in reversed(pairs) for bit in src])
        back_right = km.array([bit for _, dst in reversed(pairs) for bit in dst])
        step = [gf.pow(gf.primitive_element, -(i+1) % ((1 << gf.degree)-1))
                for i in range(len(den))]
        inverse = b.alloc_qubits(gf.degree)
        located = b.alloc_qubits(gf.degree)
        root = b.alloc_qubits(1)[0]
        mask_live = b.alloc_bits(1)
        for j, mask in enumerate(masks):
            b.bit_store(mask_live[0], True, control=mask)
            b.push_condition(mask_live[0])
            if pairs:
                b.cx(left, right)
            b.flip_if_equal(sigma, 1, target=root)
            self.inverse_add(odd, inverse)
            b.init_and(root, omega, located)
            b.gf2_phase_by_product(located, inverse, mask=mask, field=gf)
            b.del_and(root, omega, located)
            self.inverse_add(odd, inverse, undo=True)
            b.flip_if_equal(sigma, 1, target=root)
            if pairs:
                b.cx(back_left, back_right)
            b.pop_condition()
            b.bit_store(mask_live, False)
            if j + 1 < len(masks):
                for factor, s, w in zip(step, den, num):
                    b.gf2_imul(factor, target=s, field=gf)
                    b.gf2_imul(factor, target=w, field=gf)
        for factor, s, w in zip(step, den, num):
            undo = gf.pow(factor, len(masks)-1)
            b.gf2_idiv(undo, target=s, field=gf)
            b.gf2_idiv(undo, target=w, field=gf)
        b.free(mask_live)
        b.free(inverse + located + km.array([root]))

    def build(self, masks):
        b = self.b
        cursor = b.alloc_qubits(self.capacity.bit_length())
        with b.mark("forward_schur"):
            self.extraction(cursor)
            self.conversion()
        with b.mark("chien_forney"):
            self.phase(masks)
        with b.mark("reverse_schur"):
            self.conversion(reverse=True)
            self.extraction(cursor, reverse=True)
        b.free(cursor)


def build_circuit(m, n, degree):
    if not (degree >= 2 and 2 <= n <= m < 1 << degree and n % 2 == 0):
        raise ValueError("Require an even syndrome count with 2 <= n <= m < 2**degree")
    b = km.CircuitBuilder()
    syndromes = [b.create_quantum_register(degree, name=f"S{i}") for i in range(n)]
    masks = [b.create_classical_register(degree, name=f"E{j}") for j in range(m)]
    SchurDecoder(b, km.GF2Field(degree), syndromes).build(masks)
    return b.finish_circuit()


def main():
    experiment = Path(__file__).resolve().parent
    config_dir = (experiment / "configs").resolve()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=config_dir / "schur.json")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    config = args.config.resolve()
    if (config.parent != config_dir or config.suffix != ".json"
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", config.stem)):
        raise ValueError("Use a named JSON config directly inside this experiment's configs directory")
    params = json.loads(config.read_text(encoding="utf-8"))
    if set(params) != {"m", "n", "degree"} or any(type(v) is not int for v in params.values()):
        raise ValueError("Config must specify integer m, n and degree")
    root = experiment.parents[2]
    output = root / "artifacts" / experiment.parent.name / experiment.name / (config.stem + ".kmb")
    if output.exists() and not args.overwrite:
        raise FileExistsError(f"{output} already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    circuit = build_circuit(**params)
    print(f"Compiled Q={circuit.num_qubits}, emitted T={circuit.operation_statistics().num_toffoli_like:,}",
          flush=True)
    temporary = output.with_suffix(".kmb.part")
    try:
        circuit.to_file(str(temporary), format="kmb")
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
