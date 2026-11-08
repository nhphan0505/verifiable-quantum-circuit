"""DQI-27: narrow-return Schur cursor and stream jump history.

Derived from DQI-23 c5b70b1a7618057000cc9af35794c8e733e5eb1c,
SHA-256 18f7e197dc832236b95cef3b87013cce15373d7327554efb1fdb2bd2f618f492.
Apache-2.0, src/LICENSE.txt. Original arithmetic and phase sweep retained.
New metadata schedule: stream first-nonzero detection using unique jump codes
as reversible history, then return the six cursor qubits between extraction
and conversion. Cursor equals the last nonzero odd quotient slot index on
valid extracted states. No polynomial input is discarded or measured.
Optional extra converter flag retains a predicate whose source word lies
outside the modified slice; its benefit must include actual full peak Q.
No long-lived quantum branch tape or uncorrected X measurement is added.
Component validation and resource audit are not submission grader PASS.

Compile this experiment's config after committing source/config.

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

Run with --config src/dqi/DQI-27/configs/narrow_return.json. The artifact is intended
for the notebook verifier. Build statistics count emitted gates, rather than
a verifier score.

Optional masked_cleanup="hmr" replaces compute/uncompute CCX on a clean
masked lhs by init_and/del_and. The quantum control and lhs are unchanged
inside multiply_add; target disjointness is checked. Kickmix del_and measures
in X and corrects the induced phase with CZ, with no quantum-controlled HMR.
The mask is still clean after cleanup. This saves degree Toffoli-like gates
per controlled multiply_add, with the same reserved quantum workspace.
The default hmr cleanup retains the graded DQI-23 schur_hmr arithmetic.
Only metadata scheduling/lifetimes change in this experiment.
--validate-components checks isolated products and reduced decoders, not the
submission grader. Commit source/config before building a new artifact;
member runs dev/full in the local notebook. Source/helper attribution and
historical source/run mapping are in DESCRIPTION.md.
"""

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re

import kickmix as km


class SchurDecoder:
    """Emit the packed block extraction, converter and phase sweep."""

    def __init__(self, builder, field, syndromes, *, masked_cleanup="hmr", use_extra_converter_qubit=False):
        if masked_cleanup not in {"ccx", "hmr"}:
            raise ValueError("masked_cleanup must be ccx or hmr")
        self.use_extra_converter_qubit = use_extra_converter_qubit
        self.masked_cleanup = masked_cleanup
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
            self.constant_add(mask, target, work)
            self.b.del_and(left, right, work)

    def constant_add(self, mask, target, control):
        if mask:
            selected = km.array([bit for i, bit in enumerate(target) if mask >> i & 1])
            self.b.cx(control, selected)

    def inverse_add(self, word, target, *, undo=False):
        """XOR the inverse using conjugate/norm, including inverse(0)=0."""
        b, gf = self.b, self.gf
        if self.inverse_tables is None:
            if undo:
                b.del_gf2_inverse(word, target=target, field=gf)
            else:
                b.init_gf2_inverse(word, target=target, field=gf)
            return
        with self.inverse_norm(word) as (inverse_norm, work):
            self.conjugate_product_add(word, inverse_norm, target, work)

    @contextmanager
    def inverse_norm(self, word):
        b = self.b
        linear, quadratic, inverse, _ = self.inverse_tables
        norm = b.alloc_qubits(6)
        inverse_norm = b.alloc_qubits(6)
        work = b.alloc_qubits(1)[0]

        def norm_add():
            for bit, mask in zip(word, linear):
                self.constant_add(mask, norm, bit)
            for i, j, mask in quadratic:
                self.quadratic_add(word[i], word[j], mask, norm, work)

        def lookup():
            # Reuse the address prefix between adjacent GF(64) table entries.
            with b.unary_iteration(norm, range(1, len(inverse))) as cursor:
                for address, selected in cursor:
                    self.constant_add(inverse[address], inverse_norm, selected)

        norm_add()
        lookup()
        yield inverse_norm, work
        lookup()
        norm_add()
        b.free(norm + inverse_norm + km.array([work]))

    def conjugate_product_add(self, word, inverse_norm, target, work):
        for bit, row in zip(word, self.inverse_tables[3]):
            for coeff, mask in zip(inverse_norm, row):
                self.quadratic_add(bit, coeff, mask, target, work)

    @contextmanager
    def computed_inverse(self, word, target):
        if self.inverse_tables is None:
            self.inverse_add(word, target)
            yield
            self.inverse_add(word, target, undo=True)
        else:
            with self.inverse_norm(word) as (inverse_norm, work):
                self.conjugate_product_add(word, inverse_norm, target, work)
                yield
                self.conjugate_product_add(word, inverse_norm, target, work)

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

    def encode_jump(self, words, active, jump, *, reverse=False, codes=None):
        """Compute first-nonzero code into zero jump, or erase its valid code.

        A hit writes a unique nonzero tag into jump. That tag recovers the
        hit flag after live has changed. This requires zero jump on compute
        and the corresponding tag on erase, unlike arbitrary-target XOR.
        Both preconditions hold at the explicitly oriented call sites.
        """
        b=self.b
        codes=list(range(1,len(words)+1)) if codes is None else list(codes)
        if len(codes)!=len(words) or len(set(codes))!=len(codes) or any(
                not 0<c<(1<<len(jump)) for c in codes):
            raise ValueError("Jump tags must be distinct, nonzero and fit width")
        work=b.alloc_qubits(3); live,zero,hit=work
        if reverse:
            b.flip_if_equal(jump,0,target=live,control=active)
        else:
            b.cx(active,live)
        pairs=list(zip(words,codes))
        for word,code in reversed(pairs) if reverse else pairs:
            b.flip_if_equal(word,0,target=zero)
            b.x(zero)
            if reverse:
                b.flip_if_equal(jump,code,target=hit,control=active)
                b.cx(hit,live)
                b.gf2_iadd(code,target=jump,control=hit)
                b.ccx(live,zero,hit)
            else:
                b.ccx(live,zero,hit)
                b.gf2_iadd(code,target=jump,control=hit)
                b.cx(hit,live)
                b.flip_if_equal(jump,code,target=hit,control=active)
            b.x(zero)
            b.flip_if_equal(word,0,target=zero)
        if reverse:
            b.cx(active,live)
        else:
            b.flip_if_equal(jump,0,target=live,control=active)
        b.free(work)

    def cursor_from_quotients(self,cursor,*,reverse):
        """Last nonzero odd quotient slot is the accumulated degree w.

        Quotient leading coefficients mark block ends, the last at w-1.
        Slots beyond w are zero on completed valid extraction, including
        the all-zero/no-error case. Reverse=True erases a valid cursor.
        """
        words=list(reversed(self.words[1::2]))
        codes=range(self.capacity,0,-1)
        self.encode_jump(words,True,cursor,reverse=reverse,codes=codes)

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
        self.multiply_add(word, factor, temp, control)
        self.b.cswap(control, word, temp)
        self.multiply_add(word, inverse, temp, control)

    def multiply_add(self, lhs, rhs, target, control):
        b = self.b
        if control is True:
            b.ixor_gf2_mul(lhs, rhs, target=target, field=self.gf)
            return
        masked = b.alloc_qubits(self.gf.degree)
        # target must be disjoint from the factors needed by del_and.
        if self.masked_cleanup == "hmr":
            if set(target) & (set(lhs) | {control}):
                raise ValueError("HMR cleanup requires unchanged control/lhs")
            b.init_and(control, lhs, masked)
            b.ixor_gf2_mul(masked, rhs, target=target, field=self.gf)
            b.del_and(control, lhs, masked)
        else:
            b.ccx(control, lhs, masked)
            b.ixor_gf2_mul(masked, rhs, target=target, field=self.gf)
            b.ccx(control, lhs, masked)
        b.free(masked)

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
                    self.multiply_add(words[i], words[k-i], words[k], valid)
        # Form the inverse unit series from the factors, largest i first.
        # b[2*i] gets p_i^2 and no variable product is needed there.
        for i in reversed(range(1, (length + 1) // 2)):
            with self.between(jump, 1, length - 2*i) as valid:
                self.square_add(words[i], words[2*i], valid)
            for k in range(2 * i + 1, length):
                with self.between(jump, 1, length - k) as valid:
                    self.multiply_add(words[i], words[k-i], words[k], valid)

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
                self.encode_jump(words[:cap], active, jump, reverse=True)
                self.b.flip_if_equal(cursor, start, target=active)
            else:
                self.b.flip_if_equal(cursor, start, target=active)
                self.encode_jump(words[:cap], active, jump)
                self.rotate(words, jump, cap)
                self.reciprocal(words, jump)
                self.route_quotient(words, jump, False)
                self.move_cursor(cursor, start, jump, cap)
                self.encode_jump(words[1::2], active, jump, reverse=True)
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

    def scale_row(self, row, factor, inverse):
        temp = self.b.alloc_qubits(self.gf.degree)
        for word in row:
            self.scale(word, factor, inverse, temp, True)
        self.b.free(temp)

    def convolve(self, a, den, jump, reverse):
        """Add normalized q*B into the new denominator, omitting p_k*B_0."""
        b = self.b
        cap = len(a)
        terms = range(1, cap + 1)
        for k in terms if reverse else reversed(terms):
            if k < cap:
                with self.between(jump, 1, cap) as active:
                    b.gf2_iadd(a[k], target=den[k-1], control=active)
            for j in range(1, k):
                with self.between(jump, j, cap) as valid:
                    self.multiply_add(den[j-1], a[k-j], den[k-1], valid)

    def convert_block(self, den, a, jump, reverse):
        b, gf = self.b, self.gf
        cap = len(a)
        # Use the unit scale on inactive blocks so row scaling needs no flag.
        if reverse:
            inv = b.alloc_qubits(gf.degree)
            self.at_jump_slot(a, jump, lambda word, flag: b.gf2_iadd(word, target=inv, control=flag))
            b.flip_if_equal(jump, 0, target=inv[0])
            lead = b.alloc_qubits(gf.degree)
            self.inverse_add(inv, lead)
            self.rotate(a, jump, cap)
            self.scale_row(a, lead, inv)
            self.convolve(a, den, jump, True)
            self.scale_row(den, lead, inv)
            self.rotate(a, jump, cap, True)
            self.swap_tail(a, den, jump)
            self.inverse_add(lead, inv, undo=True)
            self.at_jump_slot(a, jump, lambda word, flag: b.cx(flag, word[0]))
            self.at_jump_slot(a, jump, lambda word, flag: b.cswap(flag, word, lead))
            b.flip_if_equal(jump, 0, target=lead[0])
        else:
            lead = b.alloc_qubits(gf.degree)
            self.at_jump_slot(a, jump, lambda word, flag: b.cswap(flag, word, lead))
            b.flip_if_equal(jump, 0, target=lead[0])
            self.at_jump_slot(a, jump, lambda word, flag: b.cx(flag, word[0]))
            inv = b.alloc_qubits(gf.degree)
            self.inverse_add(lead, inv)
            self.swap_tail(a, den, jump)
            self.rotate(a, jump, cap)
            self.scale_row(den, inv, lead)
            self.convolve(a, den, jump, False)
            self.scale_row(a, inv, lead)
            self.rotate(a, jump, cap, True)
            self.inverse_add(inv, lead, undo=True)
            self.at_jump_slot(a, jump, lambda word, flag: b.gf2_iadd(word, target=inv, control=flag))
            b.flip_if_equal(jump, 0, target=inv[0])
        b.free(inv + lead)

    def conversion(self, reverse=False):
        indices=range(self.capacity)
        for start in indices if reverse else reversed(indices):
            den=self.words[2*start::2];num=self.words[2*start+1::2]
            jump=self.b.alloc_qubits(len(den).bit_length())
            if self.use_extra_converter_qubit:
                # Predicate reads only the preceding odd slot, outside both slices.
                with self.flag(lambda bit:self.toggle_start(start,bit)) as active:
                    self.encode_jump(num,active,jump)
                    self.convert_block(den,num,jump,reverse)
                    self.encode_jump(num,active,jump,reverse=True)
            else:
                with self.flag(lambda bit:self.toggle_start(start,bit)) as active:
                    self.encode_jump(num,active,jump)
                self.convert_block(den,num,jump,reverse)
                with self.flag(lambda bit:self.toggle_start(start,bit)) as active:
                    self.encode_jump(num,active,jump,reverse=True)
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
            with self.computed_inverse(odd, inverse):
                b.init_and(root, omega, located)
                b.gf2_phase_by_product(located, inverse, mask=mask, field=gf)
                b.del_and(root, omega, located)
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
        b=self.b
        cursor=b.alloc_qubits(self.capacity.bit_length())
        with b.mark("forward_extraction"):
            self.extraction(cursor)
            self.cursor_from_quotients(cursor,reverse=True)
        b.free(cursor)
        with b.mark("forward_conversion"):
            self.conversion()
        with b.mark("chien_forney"):
            self.phase(masks)
        with b.mark("reverse_conversion"):
            self.conversion(reverse=True)
        cursor=b.alloc_qubits(self.capacity.bit_length())
        with b.mark("reverse_extraction"):
            self.cursor_from_quotients(cursor,reverse=False)
            self.extraction(cursor,reverse=True)
        b.free(cursor)


def build_circuit(m, n, degree, *, masked_cleanup="hmr", use_extra_converter_qubit=False):
    if not (degree >= 2 and 2 <= n <= m < 1 << degree and n % 2 == 0):
        raise ValueError("Require an even syndrome count with 2 <= n <= m < 2**degree")
    b = km.CircuitBuilder()
    syndromes = [b.create_quantum_register(degree, name=f"S{i}") for i in range(n)]
    masks = [b.create_classical_register(degree, name=f"E{j}") for j in range(m)]
    SchurDecoder(b, km.GF2Field(degree), syndromes, masked_cleanup=masked_cleanup, use_extra_converter_qubit=use_extra_converter_qubit).build(masks)
    return b.finish_circuit()

def _reference_module():
    """Read the pinned historical implementation for diagnostic comparisons only."""
    import subprocess,hashlib,types
    blob=subprocess.check_output(['git','show','c5b70b1a7618057000cc9af35794c8e733e5eb1c:src/dqi/DQI-23/solution.py'])
    if hashlib.sha256(blob).hexdigest()!='18f7e197dc832236b95cef3b87013cce15373d7327554efb1fdb2bd2f618f492':
        raise ValueError('Pinned DQI-23 diagnostic source hash mismatch')
    module=types.ModuleType('dqi27_reference')
    exec(compile(blob,'pinned-DQI23','exec'),module.__dict__)
    return module


def audit_resources():
    """Isolated peak components plus exact metadata T composition, no full build."""
    ref=_reference_module()
    def fixture(case,candidate,extra=False):
        b=km.CircuitBuilder();words=[b.create_quantum_register(12,f'S{i}') for i in range(70)]
        cls=SchurDecoder if candidate else ref.SchurDecoder
        d=cls(b,km.GF2Field(12),words,masked_cleanup='hmr',**({'use_extra_converter_qubit':extra} if candidate else {}))
        if not candidate or case in ('encode','reciprocal'):b.alloc_qubits(6)
        if case=='encode':
            jump=b.alloc_qubits(6);active=b.alloc_qubits(1)[0];d.encode_jump(words[:35],active,jump)
        elif case.startswith('convert'):
            jump=b.alloc_qubits(6)
            if extra:b.alloc_qubits(1)
            d.convert_block(words[::2],words[1::2],jump,case.endswith('reverse'))
        elif case=='reciprocal':
            jump=b.alloc_qubits(6);b.alloc_qubits(1);d.reciprocal(words,jump)
        elif case=='phase':d.phase([b.create_classical_register(12,'E0')])
        c=b.finish_circuit();return {'q':c.num_qubits,'t':c.operation_statistics().num_toffoli_like}
    cases=('encode','convert_forward','convert_reverse','reciprocal','phase')
    peaks={case:{'reference':fixture(case,False),'narrow':fixture(case,True),'extra':fixture(case,True,True)} for case in cases}
    def encode_t(length,candidate,constant_active=False):
        b=km.CircuitBuilder();words=[b.create_quantum_register(12,f'x{i}') for i in range(length)]
        jump=b.create_quantum_register(length.bit_length(),'j')
        active=True if constant_active else b.create_quantum_register(1,'a')[0]
        (SchurDecoder if candidate else ref.SchurDecoder)(b,km.GF2Field(12),words,masked_cleanup='hmr').encode_jump(words,active,jump)
        return b.finish_circuit().operation_statistics().num_toffoli_like
    counts=[{'length':k,'old_t':encode_t(k,False),'new_t':encode_t(k,True)} for k in range(1,36)]
    scan=encode_t(35,True,True)
    b=km.CircuitBuilder();word=b.create_quantum_register(12,'w');q=b.alloc_qubits(1)[0]
    b.flip_if_equal(word,0,target=q);predicate=b.finish_circuit().operation_statistics().num_toffoli_like
    low=11620060+8*sum(x['new_t']-x['old_t'] for x in counts)+2*scan
    return {'scope':'isolated components and metadata composition, not full decoder grading',
            'component_peaks':peaks,'encode_counts':counts,'cursor_scan_t':scan,'word_predicate_t':predicate,
            'predicted_static_t_low':low,'predicted_static_t_extra':low-4*34*predicate,
            'baseline_q':900,'baseline_t':11620060,'predicted_q':890,
            'limitation':'Isolated allocator peaks predict whole-circuit Q; actual full build is authoritative.'}


def _bits(values,degree):
    import numpy as np
    return np.array([(values>>i)&1 for i in range(degree)],dtype=bool)


def _error_cases(degree,n,m,count,seed):
    """Independent syndrome/phase data, including forced valuation jumps."""
    import numpy as np
    gf=km.GF2Field(degree);rng=np.random.default_rng(seed)
    synd=np.zeros((n,count),dtype=np.uint32)
    masks=rng.integers(0,1<<degree,(m,count),dtype=np.uint32)
    phases=np.zeros(count,dtype=bool);weights=np.zeros(count,dtype=np.uint32)
    forced=[]
    for case in range(count):
        weight=case%(n//2+1)
        pos=list(map(int,rng.choice(m,weight,replace=False)))
        vals=list(map(int,rng.integers(1,1<<degree,weight)))
        if case==0:pos=[];vals=[]
        elif case==1:pos=[0];vals=[1]
        elif case==2:pos=[m-1];vals=[(1<<degree)-1]
        elif 3<=case<3+n//2:
            weight=case-2;pos=list(range(weight));vals=[]
            roots=[gf.pow(gf.primitive_element,j) for j in pos]
            for i,a in enumerate(roots):
                den=a
                for j,other in enumerate(roots):
                    if i!=j:den=gf.mul(den,a ^ other)
                vals.append(gf.invert(den))
            forced.append(weight)
        weights[case]=len(pos)
        for j,e in zip(pos,vals):
            for i in range(n):synd[i,case]^=gf.mul(e,gf.pow(gf.primitive_element,(i+1)*j))
            phases[case]^=bool((e&int(masks[j,case])).bit_count()&1)
    for d in forced:
        case=d+2
        assert not synd[:d-1,case].any() and synd[d-1,case]==1
    return synd,masks,phases,weights


def validate_jump():
    import numpy as np
    checked=0;report=[]
    for length in (1,2,8,35):
        count=2*(1<<length) if length<=8 else 1024
        rng=np.random.default_rng(2701+length)
        values=rng.integers(1,4096,(length,count),dtype=np.uint32)
        idx=np.arange(count);active=(idx&1).astype(bool)
        if length<=8:
            nonzero=np.array([((idx>>1)>>i)&1 for i in range(length)],dtype=bool)
        else:
            nonzero=rng.integers(0,2,(length,count)).astype(bool)
            for first in range(length+1):
                nonzero[:,2*first:2*first+2]=True
                nonzero[:first,2*first:2*first+2]=False
        values*=nonzero
        for descending in (False,True):
            b=km.CircuitBuilder();words=[b.create_quantum_register(12,f'x{i}') for i in range(length)]
            a=b.create_quantum_register(1,'a')[0];jump=b.create_quantum_register(length.bit_length(),'jump')
            observed=b.create_quantum_register(len(jump),'observed')
            boundary=length*12+1+2*len(jump)
            codes=list(range(length,0,-1)) if descending else list(range(1,length+1))
            d=SchurDecoder(b,km.GF2Field(12),words)
            d.encode_jump(words,a,jump,codes=codes);b.cx(jump,observed)
            d.encode_jump(words,a,jump,codes=codes,reverse=True)
            c=b.finish_circuit();expected=np.zeros(count,dtype=np.uint32)
            for case in range(count):
                positions=np.flatnonzero(values[:,case])
                if active[case] and len(positions):expected[case]=codes[int(positions[0])]
            for seed in (2701,2702,2703):
                sim=km.Simulator(count,seed=seed,debug_print=False);sim.use_same_registers_as(c)
                for i,word in enumerate(words):sim.write_across_shots(word,_bits(values[i],12))
                sim.write_across_shots(a,active);sim.do(c)
                for i,word in enumerate(words):assert np.array_equal(sim.read_across_shots(word),_bits(values[i],12))
                assert np.array_equal(sim.read_across_shots(observed),_bits(expected,len(jump)))
                assert not sim.read_across_shots(jump).any()
                assert np.array_equal(sim.read_across_shots(a),active)
                anc=km.array([km.q(i) for i in range(boundary,c.num_qubits)])
                assert not sim.read_across_shots(anc).any() and not sim.read_phase_flipped_across_shots().any()
                checked+=count
        report.append({'length':length,'zero_patterns_exhaustive':length<=8,'active_values':[0,1]})
    return {'cases':checked,'domains':report,'seeds':[2701,2702,2703],'value_errors':0,'phase_errors':0,'workspace_errors':0}


def validate_cursor():
    """Full 70-word metadata-only test; excludes phase/official decoder grading."""
    import numpy as np
    b=km.CircuitBuilder();words=[b.create_quantum_register(12,f'S{i}') for i in range(70)]
    cursor=b.alloc_qubits(6)
    observed=[b.create_quantum_register(6,name) for name in ('before','cleared','restored')]
    boundary=840+6+18
    d=SchurDecoder(b,km.GF2Field(12),words)
    d.extraction(cursor);b.cx(cursor,observed[0])
    d.cursor_from_quotients(cursor,reverse=True);b.cx(cursor,observed[1])
    d.cursor_from_quotients(cursor,reverse=False);b.cx(cursor,observed[2])
    d.extraction(cursor,reverse=True)
    c=b.finish_circuit();checked=0
    for seed in (2701,2702,2703):
        count=128;synd,_,_,weights=_error_cases(12,70,4095,count,seed)
        sim=km.Simulator(count,seed=seed,debug_print=False);sim.use_same_registers_as(c)
        for i,word in enumerate(words):sim.write_across_shots(word,_bits(synd[i],12))
        sim.do(c)
        for i,word in enumerate(words):assert np.array_equal(sim.read_across_shots(word),_bits(synd[i],12))
        for reg in (observed[0],observed[2]):assert np.array_equal(sim.read_across_shots(reg),_bits(weights,6))
        assert not sim.read_across_shots(observed[1]).any() and not sim.read_across_shots(cursor).any()
        anc=km.array([km.q(i) for i in range(boundary,c.num_qubits)])
        assert not sim.read_across_shots(anc).any() and not sim.read_phase_flipped_across_shots().any()
        checked+=count
    return {'scope':'full-width extraction/cursor/reverse component only, not submission grading',
            'cases':checked,'weights':list(range(36)),'forced_initial_jumps':list(range(1,36)),
            'measurement_seeds':[2701,2702,2703],'value_errors':0,'phase_errors':0,'workspace_errors':0}


def validate_reduced():
    import numpy as np
    report=[];checked=0
    for degree,n,m in ((3,6,7),(4,8,15),(12,8,31)):
        circuits=[build_circuit(m,n,degree,use_extra_converter_qubit=extra) for extra in (False,True)]
        for seed in (2701,2702,2703):
            count=128;synd,masks,phase,_=_error_cases(degree,n,m,count,seed)
            for c in circuits:
                sim=km.Simulator(count,seed=seed,debug_print=False);sim.use_same_registers_as(c)
                for i in range(n):sim.write_across_shots(c.register_data[f'S{i}'],_bits(synd[i],degree))
                for j in range(m):sim.write_across_shots(c.register_data[f'E{j}'],_bits(masks[j],degree))
                sim.do(c)
                for i in range(n):assert np.array_equal(sim.read_across_shots(c.register_data[f'S{i}']),_bits(synd[i],degree))
                anc=km.array([km.q(i) for i in range(n*degree,c.num_qubits)])
                assert not sim.read_across_shots(anc).any()
                assert np.array_equal(sim.read_phase_flipped_across_shots(),phase)
            checked+=count
        report.append({'degree':degree,'n':n,'m':m,'low_q':circuits[0].num_qubits,'extra_q':circuits[1].num_qubits,
                       'low_t':circuits[0].operation_statistics().num_toffoli_like,'extra_t':circuits[1].operation_statistics().num_toffoli_like})
    return {'cases_per_variant':checked,'decoder_shapes':report,'value_errors':0,'phase_errors':0,'workspace_errors':0}


def validate_metadata():
    return {'verification_level':'local metadata/reduced component validation, not official grading',
            'jump':validate_jump(),'cursor':validate_cursor(),'reduced_decoders':validate_reduced(),
            'limitation':'Sampled coherent cases supplement reachable-state identities; not universal syndrome or measurement enumeration.'}


def main():
    experiment=Path(__file__).resolve().parent;root=experiment.parents[2]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=experiment/'configs/narrow_return.json')
    parser.add_argument('--validate-components',action='store_true')
    parser.add_argument('--audit-resources',action='store_true')
    parser.add_argument('--overwrite',action='store_true')
    args=parser.parse_args()
    if args.validate_components:
        print(json.dumps(validate_metadata(),indent=2));return
    if args.audit_resources:
        print(json.dumps(audit_resources(),indent=2));return
    config=args.config.resolve()
    if config.parent!=(experiment/'configs') or config.suffix!='.json' or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',config.stem):
        raise ValueError('Config must be a named JSON directly in this experiment configs/')
    params=json.loads(config.read_text())
    if (set(params)!={'m','n','degree','use_extra_converter_qubit'}
            or any(type(params[k]) is not int for k in ('m','n','degree'))
            or type(params['use_extra_converter_qubit']) is not bool
            or {k:params[k] for k in ('m','n','degree')}!={'m':4095,'n':70,'degree':12}):
        raise ValueError('Require official m/n/degree and Boolean use_extra_converter_qubit')
    output=root/'artifacts'/experiment.parent.name/experiment.name/(config.stem+'.kmb')
    if output.exists() and not args.overwrite:raise FileExistsError(output)
    circuit=build_circuit(**params);stats=circuit.operation_statistics()
    expected=11647130 if params['use_extra_converter_qubit'] else 11648762
    if stats.num_toffoli_like!=expected:raise AssertionError('Metadata gate count differs from component composition')
    if circuit.num_qubits>=900 or circuit.num_qubits**2*stats.num_toffoli_like>=900**2*11620060:
        raise AssertionError('Narrow-return candidate fails the Q2T resource gate')
    output.parent.mkdir(parents=True,exist_ok=True);temporary=output.with_suffix('.kmb.part')
    try:
        circuit.to_file(str(temporary),format='kmb');temporary.replace(output)
    finally:temporary.unlink(missing_ok=True)
    print(json.dumps({'status':'BUILT','artifact_path':str(output.relative_to(root)),
                      'num_qubits':circuit.num_qubits,'static_toffoli_like':stats.num_toffoli_like,
                      'num_instructions':stats.num_instructions,'reference_q':900,'reference_static_t':11620060},indent=2))


if __name__=='__main__':
    main()
