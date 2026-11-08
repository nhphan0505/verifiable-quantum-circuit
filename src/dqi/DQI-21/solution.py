"""DQI-21: exact Bezout-reciprocal reference decoder and validation probes.

Owner trng-hminh; https://github.com/nhphan0505/verifiable-quantum-circuit/issues/21.
Baseline interface/source: bb3a6311113217a69c64e88e9c3bb0513237a1f9,
DQI-BASELINE/solution.py, Apache-2.0 (src/LICENSE.txt). The merged baseline is
loaded only after checking its pinned SHA-256. The merged DQI-19 helper is
also hash-pinned and supplies only the proven 42-term field tensor; the main
EEA remains native baseline. See DESCRIPTION.md for references and scope.

Algorithm: after baseline alignment, s(z) is the packed locator (36 words),
w(z) the reversed 35-word evaluator. At z=alpha^j the native denominator is
z*s'(z). For valid RS decoder states s is a nonzero scalar times a product of
distinct nonzero-root linear factors, including the constant no-error locator.
Split s=E^2+z*O^2 with inverse Frobenius maps and deg E,deg O<=17. A coherent
fixed schedule of 36 auxiliary steps records degrees, swaps, shifts and field
quotients, performs at most 35 leading cancellations and a terminal orientation
swap, and yields constant nonzero gcd g. Two Bezout rows satisfy a0*E+b0*O=g.
Normalize them in place using g^-1, so A*E+B*O=1. A temporary-word multiply and
measurement-based deletion of the old value implement invertible scaling.
The 18-word buffers do not wrap on valid EEA states: shifted remainder degree
and cofactor degrees never exceed 17. Zero divisors after termination map to
quotient zero; data-dependent branches are always quantum control, never host
Python branches. No heuristic cutoff or intentional arithmetic error is used.

Compute H=w*(B^2+z*A^2) into 70 words using rank-42 temporary AND kernels.
Evaluate s(z) and H(z)/z with CNOT/constant-field multipliers at all 4095 points.
A 12-bit zero-predicate chain costs 11 Toffoli-like gates per point; runtime
mask bits condition CZs, and del_and erases the predicate chain. No offline
mask fitting or position cancellation is used. Restore step multipliers,
measure H in X and correct its convolution phase via gf2_phase_by_product,
undo normalization, reverse the auxiliary tape, erase E/O and initial units,
then let the unchanged main EEA restore syndrome and other workspace.

Stage 5 adds layout="streamed_exact" with compact_degree_history=true.
It keeps only two live degree registers and a per-step shift/swap/quotient
transcript (18 bits per step instead of 28), restoring each prior degree as
shift+divisor_degree before undoing its step. The current remainder supplies
the new degree, so no historical degree copies are retained. Both degrees are
erased against the restored E/O at the end; 350 qubits are saved in total.

The streamed sweep allocates no 70-word H: it evaluates A(z)^2+B(z)^2/z and
omega(z) separately, combines them through gf2_phase_by_product with a
root-masked numerator, and restores both normalized cofactor rows. Exact
Frobenius CNOT networks square/unsquare those rows in place. This costs 23
Toffoli-like gates per point (11 zero predicate +12 masked-numerator ANDs),
explicitly trading away the 11-point target to reduce total space. Original
materialized config and its graded source/run mapping remain unchanged.
This is an intermediate ablation, not a baseline-beating design: six separate
auxiliary polynomials still make Q too large. Future work must use in-place
Bezout/Hankel transforms and prove variable-degree, mask and cleanup invariants.

Tradeoff: this materialized reference layout has a poor predicted Q^2*T score
because it retains auxiliary state and 70 H words. The user requested a full
stage-3 build after that screening result, to obtain exact correctness/cost
evidence. It is not presented as the final space-optimized Bezout/Hankel design.
Model, auxiliary and phase-block unit tests are not decoder verifier PASS.
The member runs the unchanged local grader; this program never invokes it.

Run from repo root with Python 3.13 and pinned requirements:
  python src/dqi/DQI-21/solution.py --config src/dqi/DQI-21/configs/bezout_reference.json
Config resolves directly under this ID's configs/. TRACK/ID/default artifact
are inferred from this file's location; output stem must match config stem.
Use --overwrite only for deliberate rebuild. exact_probe.json remains probe
only. Optional unit probes: --validate-packed, --validate-model,
--validate-kernel, --audit-resources, --validate-aux-model,
--validate-aux-circuit, --validate-phase-block. These print diagnostic JSON,
not official results. Source/config commit must precede submission compilation.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import kickmix as km

FIELD = km.GF2Field(12)
BASELINE_COMMIT = 'bb3a6311113217a69c64e88e9c3bb0513237a1f9'
BASELINE_SHA256 = '3bba2c941021749393d322c1b779e02dd7ec987c61c7b253a54fd2173968cdb4'
PACKED_CASES = [{'weight': 0, 'degree': 0, 'valuation': 0, 'sigma': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'omega': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'expected_errors': {}, 'root_positions': [], 'value_mismatches': 0}, {'weight': 1, 'degree': 1, 'valuation': 0, 'sigma': [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'omega': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'expected_errors': {'0': 1}, 'root_positions': [0], 'value_mismatches': 0}, {'weight': 1, 'degree': 1, 'valuation': 0, 'sigma': [3567, 1856, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'omega': [2726, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'expected_errors': {'17': 5}, 'root_positions': [17], 'value_mismatches': 0}, {'weight': 1, 'degree': 1, 'valuation': 0, 'sigma': [3752, 3331, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'omega': [373, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'expected_errors': {'4094': 4095}, 'root_positions': [4094], 'value_mismatches': 0}, {'weight': 7, 'degree': 7, 'valuation': 0, 'sigma': [2083, 0, 0, 0, 0, 0, 0, 2083, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'omega': [0, 1625, 2749, 542, 1261, 1999, 1531, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'expected_errors': {'0': 1, '585': 2, '1170': 3, '1755': 4, '2340': 5, '2925': 6, '3510': 7}, 'root_positions': [0, 585, 1170, 1755, 2340, 2925, 3510], 'value_mismatches': 0}, {'weight': 35, 'degree': 35, 'valuation': 0, 'sigma': [2616, 0, 0, 0, 0, 0, 0, 3315, 0, 0, 0, 0, 0, 0, 464, 0, 0, 0, 0, 0, 0, 2891, 0, 0, 0, 0, 0, 0, 175, 0, 0, 0, 0, 0, 0, 3327], 'omega': [0, 3773, 737, 3374, 1666, 3187, 1623, 3806, 1014, 2855, 647, 2143, 3100, 1044, 3126, 3967, 1867, 385, 2126, 4011, 1840, 1020, 2106, 2732, 3867, 449, 3821, 2133, 276, 1513, 3344, 2702, 1913, 327, 2895], 'expected_errors': {'0': 1, '585': 2, '1170': 3, '1755': 4, '2340': 5, '2925': 6, '3510': 7, '1': 8, '586': 9, '1171': 10, '1756': 11, '2341': 12, '2926': 13, '3511': 14, '2': 15, '587': 16, '1172': 17, '1757': 18, '2342': 19, '2927': 20, '3512': 21, '3': 22, '588': 23, '1173': 24, '1758': 25, '2343': 26, '2928': 27, '3513': 28, '4': 29, '589': 30, '1174': 31, '1759': 32, '2344': 33, '2929': 34, '3514': 35}, 'root_positions': [0, 1, 2, 3, 4, 585, 586, 587, 588, 589, 1170, 1171, 1172, 1173, 1174, 1755, 1756, 1757, 1758, 1759, 2340, 2341, 2342, 2343, 2344, 2925, 2926, 2927, 2928, 2929, 3510, 3511, 3512, 3513, 3514], 'value_mismatches': 0}]


def trim(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def add(a, b):
    out = [0] * max(len(a), len(b))
    for i, v in enumerate(a): out[i] ^= v
    for i, v in enumerate(b): out[i] ^= v
    return trim(out)


def mul(a, b):
    if not a or not b: return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): out[i+j] ^= FIELD.mul(x, y)
    return trim(out)


def divide(a, b):
    a, b = trim(a), trim(b)
    if not b: raise ValueError('Polynomial division by zero')
    q = [0] * max(0, len(a) - len(b) + 1)
    while a and len(a) >= len(b):
        shift = len(a) - len(b)
        scalar = FIELD.div(a[-1], b[-1])
        q[shift] ^= scalar
        for j, x in enumerate(b): a[shift+j] ^= FIELD.mul(scalar, x)
        a = trim(a)
    return trim(q), a


def evaluate(p, x):
    value = 0
    for c in reversed(p): value = FIELD.mul(value, x) ^ c
    return value


def square(p):
    if not p: return []
    out = [0] * (2 * len(p) - 1)
    for i, x in enumerate(p): out[2*i] = FIELD.square(x)
    return trim(out)


def derivative(p):
    return trim([p[i+1] if i % 2 == 0 else 0 for i in range(max(0, len(p)-1))])


def reciprocal_reference(f):
    """Classical exact reference, including constant f; never a coherent EEA."""
    f = trim(f)
    if not f: raise ValueError('Zero locator needs an independently proven no-error branch')
    E = trim([FIELD.pow(x, 1 << 11) for x in f[0::2]])
    O = trim([FIELD.pow(x, 1 << 11) for x in f[1::2]])
    r0, r1 = E, O
    a0, a1, b0, b1 = [1], [], [], [1]
    steps, degree_drops = 0, []
    while r1:
        q, r = divide(r0, r1)
        degree_drops.append(len(r0) - len(r))
        r0, r1 = r1, r
        a0, a1 = a1, add(a0, mul(q, a1))
        b0, b1 = b1, add(b0, mul(q, b1))
        steps += 1
    if len(r0) != 1: raise ValueError('E/O not coprime: locator not square-free')
    inv = FIELD.invert(r0[0])
    A = trim([FIELD.mul(x, inv) for x in a0])
    B = trim([FIELD.mul(x, inv) for x in b0])
    assert add(mul(A, E), mul(B, O)) == [1]
    psi = add(square(B), [0] + square(A))
    assert add(mul(psi, derivative(f)), add([1], mul(square(A), f))) == []
    return psi, {'bezout_steps': steps, 'degree_drops': degree_drops}


def validate_model():
    """Check full field sweep against packed native Forney for boundary cases."""
    reports = []
    for case in PACKED_CASES:
        s, w = trim(case['sigma']), trim(case['omega'])
        valuation = next(i for i, c in enumerate(s) if c)
        f = s[valuation:]
        psi, report = reciprocal_reference(f)
        h = [0] * (35 - valuation) + mul(w, psi)
        errors = {int(j): v for j, v in case['expected_errors'].items()}
        roots = []
        for j in range(4095):
            z = FIELD.pow(FIELD.primitive_element, j)
            is_root = evaluate(s, z) == 0
            native = FIELD.div(evaluate(w, z), FIELD.mul(z, evaluate(derivative(s), z))) if is_root else 0
            candidate = FIELD.mul(FIELD.pow(z, 4095 - 36), evaluate(h, z)) if is_root else 0
            assert native == candidate == errors.get(j, 0), (case['weight'], j)
            if is_root: roots.append(j)
            # Runtime masks vary by position and case, including zero and full.
            for mask in (0, 4095, ((j * 197) ^ case['weight']) & 4095):
                assert ((native & mask).bit_count() & 1) == ((candidate & mask).bit_count() & 1)
        assert set(roots) == set(errors)
        report.update(weight=case['weight'], degree=len(s)-1, valuation=valuation,
                      root_count=len(roots), value_mismatches=0, phase_mismatches=0)
        reports.append(report)
    return {'verification_level': 'classical polynomial model, not decoder grading',
            'packed_fixture_source_commit': BASELINE_COMMIT, 'cases': reports,
            'field_points_per_case': 4095, 'runtime_masks_per_point': 3}


def phase_point(builder, sigma_value, error_value, mask):
    """Preserve inputs and apply (-1)^([sigma==0]*parity(mask & error))."""
    if len(sigma_value) != 12 or len(error_value) != 12 or len(mask) != 12:
        raise ValueError('Point kernel requires 12-bit registers')
    chain = builder.alloc_qubits(11)
    builder.x(sigma_value)
    builder.init_and(sigma_value[0], sigma_value[1], chain[0])
    for i in range(2, 12): builder.init_and(chain[i-2], sigma_value[i], chain[i-1])
    for i in range(12):
        builder.push_condition(mask[i])
        builder.cz(chain[-1], error_value[i])
        builder.pop_condition()
    for i in range(11, 1, -1): builder.del_and(chain[i-2], sigma_value[i], chain[i-1])
    builder.del_and(sigma_value[0], sigma_value[1], chain[0])
    builder.x(sigma_value)
    builder.free(chain)


def validate_kernel():
    """Exhaust every sigma/value pair, then every value/runtime-mask at a root."""
    import numpy as np
    import time
    b = km.CircuitBuilder()
    s = b.create_quantum_register(12, 'sigma')
    v = b.create_quantum_register(12, 'value')
    mask = b.create_classical_register(12, 'mask')
    phase_point(b, s, v, mask)
    c = b.finish_circuit()
    assert c.operation_statistics().num_toffoli_like == 11
    batch = 65536
    shifts = np.arange(12, dtype=np.uint32)[:, None]
    def bits(x): return ((x[None, :] >> shifts) & 1).astype(bool)
    started = time.monotonic()
    for mode in ('sigma_value', 'root_value_mask'):
        for start in range(0, 1 << 24, batch):
            index = np.arange(start, start + batch, dtype=np.uint32)
            if mode == 'sigma_value':
                sv, vv = index & 4095, index >> 12
                mv = ((index * 197) ^ (index >> 5) ^ 21) & 4095
            else:
                sv = np.zeros(batch, dtype=np.uint32)
                vv, mv = index & 4095, index >> 12
            parity = vv & mv
            parity ^= parity >> 8
            parity ^= parity >> 4
            parity ^= parity >> 2
            parity ^= parity >> 1
            expected = (sv == 0) & ((parity & 1) != 0)
            sim = km.Simulator(batch, debug_print=False, seed=start + (1 if mode == 'sigma_value' else 2))
            sim.use_same_registers_as(c)
            sim.write_across_shots(s, bits(sv)); sim.write_across_shots(v, bits(vv)); sim.write_across_shots(mask, bits(mv))
            sim.do(c)
            assert np.array_equal(sim.read_across_shots(s), bits(sv))
            assert np.array_equal(sim.read_across_shots(v), bits(vv))
            assert np.array_equal(sim.read_across_shots(mask), bits(mv))
            assert not sim.read_across_shots(km.array([km.q(i) for i in range(24, c.num_qubits)])).any()
            assert np.array_equal(sim.read_phase_flipped_across_shots(), expected)
    return {'verification_level': 'isolated phase kernel, not decoder grading',
            'cases_checked': 2 * (1 << 24), 'num_toffoli_like': 11,
            'num_qubits_including_24_inputs': c.num_qubits,
            'phase_errors': 0, 'value_errors': 0, 'workspace_errors': 0,
            'elapsed_seconds': time.monotonic() - started}


def baseline_module():
    """Load the exact merged baseline for resource-only probes."""
    path = Path(__file__).resolve().parents[1] / 'DQI-BASELINE' / 'solution.py'
    if hashlib.sha256(path.read_bytes()).hexdigest() != BASELINE_SHA256:
        raise ValueError('Baseline source differs from pinned snapshot')
    spec = importlib.util.spec_from_file_location('dqi21_pinned_baseline', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_packed_mapping():
    """Regenerate boundary fixtures from baseline EEA, without grading a decoder."""
    import numpy as np
    base = baseline_module()
    cases = [{int(j): v for j, v in c['expected_errors'].items()} for c in PACKED_CASES]
    class Capture(base.ProosAndZalkaDecoder):
        def _chien_search_and_forney_mbuc(self, builder, reg_b, masks, nb, nB):
            self._pre_align_reg_b(builder, reg_b, nb, nB, is_adjoint=False)
            for k, reg in enumerate(reg_b):
                builder.cx(reg, builder.create_quantum_register(12, 'snapshot'+str(k)))
            self._pre_align_reg_b(builder, reg_b, nb, nB, is_adjoint=True)
    b = km.CircuitBuilder()
    syndromes = [b.create_quantum_register(12, 'S'+str(i)) for i in range(70)]
    masks = [b.create_classical_register(12, 'E'+str(i)) for i in range(70)]
    Capture(70, FIELD).build_syndrome_decoding_mbuc(
        b, syndromes=syndromes, error_mbuc=masks, n_iters=base.default_n_iters(70))
    circuit = b.finish_circuit()
    sim = km.Simulator(len(cases), debug_print=False, seed=21)
    sim.use_same_registers_as(circuit)
    inputs = []
    for i, reg in enumerate(syndromes):
        values = []
        for errors in cases:
            value = 0
            for j, e in errors.items():
                value ^= FIELD.mul(e, FIELD.pow(FIELD.primitive_element, (i+1)*j))
            values.append(value)
        matrix = np.array([[(v >> bit) & 1 for v in values] for bit in range(12)], dtype=bool)
        inputs.append(matrix)
        sim.write_across_shots(reg, matrix)
    sim.do(circuit)
    for reg, matrix in zip(syndromes, inputs):
        assert np.array_equal(sim.read_across_shots(reg), matrix)
    snapshots = [sim.read_across_shots('snapshot'+str(k)) for k in range(73)]
    for index, case in enumerate(PACKED_CASES):
        values = [sum(int(bits[i, index]) << i for i in range(12)) for bits in snapshots]
        assert values[:36] == case['sigma']
        assert list(reversed(values[37:72])) == case['omega']
    return {'verification_level': 'baseline EEA boundary extraction, not decoder grading',
            'source_commit': BASELINE_COMMIT, 'source_sha256': BASELINE_SHA256,
            'weights': [len(e) for e in cases], 'fixture_mismatches': 0,
            'syndrome_restoration_errors': 0,
            'note': 'Snapshot outputs intentionally retain polynomial data; this is a test circuit, never a submission artifact.'}


def audit_resources():
    """Optimistic static costs for separate coefficient storage, not full score."""
    base = baseline_module()
    b = km.CircuitBuilder()
    regs = [b.create_quantum_register(12, 'B'+str(i)) for i in range(73)]
    masks = [b.create_classical_register(12, 'E'+str(i)) for i in range(4095)]
    nb, nB = b.create_quantum_register(8, 'nb'), b.create_quantum_register(8, 'nB')
    base.ProosAndZalkaDecoder(70, FIELD)._chien_search_and_forney_mbuc(b, regs, masks, nb, nB)
    c = b.finish_circuit()
    phase_t = c.operation_statistics().num_toffoli_like
    del c, b
    c = base.build_reference_circuit(4095, 70, 12)
    total_t, baseline_q = c.operation_statistics().num_toffoli_like, c.num_qubits
    persistent = 2 * 73 * 12 + 5 * 8 + 1 + 2 + 8
    optimistic_t = total_t - phase_t + 4095 * 11
    variants = []
    for words in (70, 35):
        q = persistent + 12 * words
        variants.append({'coefficient_words': words, 'extra_coefficient_qubits': 12*words,
                         'candidate_q_optimistic': q, 'static_q2t_ratio_optimistic':
                         q*q*optimistic_t/(baseline_q*baseline_q*total_t)})
    return {'verification_level': 'static structural feasibility audit, not verifier score',
            'baseline_source_commit': BASELINE_COMMIT, 'baseline_source_sha256': BASELINE_SHA256,
            'baseline_static_total_toffoli_like': total_t, 'baseline_static_phase_toffoli_like': phase_t,
            'baseline_qubits': baseline_q, 'persistent_main_eea_qubits': persistent,
            'scan_toffoli_like': 4095*11, 'candidate_static_t_optimistic': optimistic_t,
            'variants': variants,
            'preprocessing_and_workspace_assumption': 'zero cost and zero additional workspace, deliberately optimistic',
            'screening_decision': 'Separate storage is score-unfavorable; the later exact reference build intentionally measures correctness/cost despite this screening result',
            'limitation': 'Does not disprove H2 or in-place designs. Classical mask skips, statistical penalty and executed counts require real decoder grading.'}


AUX_WORDS = 18
AUX_STEPS = 36  # <=35 leading cancellations plus a terminal orientation swap.
RANK42_SHA256 = '3798b608825c8ca741aaf4cf1d7913d87b650f2be55242a35dc769b8cd47c298'
_RANK42 = None


def rank42_terms():
    global _RANK42
    if _RANK42 is None:
        path = Path(__file__).resolve().parents[1] / 'DQI-19' / 'solution.py'
        if hashlib.sha256(path.read_bytes()).hexdigest() != RANK42_SHA256:
            raise ValueError('Rank-42 helper differs from pinned merged DQI-19 snapshot')
        spec = importlib.util.spec_from_file_location('dqi21_rank42', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _RANK42 = module.rank42_tensor()
    return _RANK42


def _xor_parity(builder, register, mask, target):
    controls = [register[i] for i in range(len(register)) if mask >> i & 1]
    if controls: builder.cx(km.array(controls), target)


def _mul_accumulate(builder, lhs, rhs, target):
    """42 temporary ANDs; exact target ^= lhs*rhs, arbitrary initial target."""
    scratch = builder.alloc_qubits(3)
    a, b, term = scratch
    last_l = last_r = 0
    for left, right, output in rank42_terms():
        _xor_parity(builder, lhs, left ^ last_l, a)
        _xor_parity(builder, rhs, right ^ last_r, b)
        builder.init_and(a, b, term)
        builder.cx(term, km.array([target[i] for i in range(12) if output >> i & 1]))
        builder.del_and(a, b, term)
        last_l, last_r = left, right
    _xor_parity(builder, lhs, last_l, a)
    _xor_parity(builder, rhs, last_r, b)
    builder.free(scratch)


def _xor_frobenius(builder, source, target, power):
    """target ^= source^(2^power), a binary linear map."""
    for i in range(12):
        image = FIELD.pow(1 << i, 1 << power)
        builder.cx(source[i], km.array([target[j] for j in range(12) if image >> j & 1]))


def _flat(polys):
    return km.array([q for poly in polys for word in poly for q in word])


def _alloc_poly(builder, words):
    return [builder.alloc_qubits(12) for _ in range(words)]


def _nonzero_xor(builder, word, target):
    chain = builder.alloc_qubits(11)
    builder.x(word)
    builder.init_and(word[0], word[1], chain[0])
    for i in range(2, 12): builder.init_and(chain[i-2], word[i], chain[i-1])
    builder.cx(chain[-1], target)
    builder.x(target)
    for i in range(11, 1, -1): builder.del_and(chain[i-2], word[i], chain[i-1])
    builder.del_and(word[0], word[1], chain[0])
    builder.x(word)
    builder.free(chain)


def _degree_xor(builder, polynomial, target):
    """XOR degree+1 into target; zero polynomial maps to 0. Clean workspace."""
    n = len(polynomial)
    nz = builder.alloc_qubits(n)
    seen = builder.alloc_qubits(n+1)
    highest = builder.alloc_qubits(1)[0]
    for i in range(n): _nonzero_xor(builder, polynomial[i], nz[i])
    for i in range(n-1, -1, -1):
        builder.init_and(nz[i], seen[i+1], seen[i])
        builder.cx(nz[i], seen[i]); builder.cx(seen[i+1], seen[i])
        builder.x(seen[i+1])
        builder.init_and(nz[i], seen[i+1], highest)
        builder.cx(highest, km.array([target[j] for j in range(len(target)) if (i+1) >> j & 1]))
        builder.del_and(nz[i], seen[i+1], highest)
        builder.x(seen[i+1])
    for i in range(n):
        builder.cx(seen[i+1], seen[i]); builder.cx(nz[i], seen[i])
        builder.del_and(nz[i], seen[i+1], seen[i])
    for i in range(n): _nonzero_xor(builder, polynomial[i], nz[i])
    builder.free(nz + seen + km.array([highest]))


def _selected_leading_xor(builder, polynomial, degree_plus_one, target):
    with builder.unary_iteration(degree_plus_one) as cursor:
        for i, word in enumerate(polynomial):
            cursor.move_to(i+1)
            builder.ccx(cursor.match_qubit, word, target)


def _rotate_words(builder, polynomial, shift, *, inverse=False):
    for bit in range(12):
        lane = km.array([word[bit] for word in polynomial])
        if inverse: builder.right_rotate(lane, shift)
        else: builder.left_rotate(lane, shift)


def _row_update(builder, rows, quotient, shift):
    # On reachable EEA states, nonzero source coefficients shifted past degree
    # 17 do not exist (including both Bezout rows). Cyclic rotations are exact.
    for dst, src in rows:
        _rotate_words(builder, src, shift)
        for a, b in zip(dst, src): _mul_accumulate(builder, quotient, b, a)
        _rotate_words(builder, src, shift, inverse=True)


def _aux_step(builder, rows):
    r0, r1 = rows[0]
    d0, d1, shift = (builder.alloc_qubits(5) for _ in range(3))
    swapped = builder.alloc_qubits(1)[0]
    quotient = builder.alloc_qubits(12)
    _degree_xor(builder, r0, d0); _degree_xor(builder, r1, d1)
    builder.flip_if_less_than(d0, d1, target=swapped)
    for a, b in rows: builder.cswap(swapped, _flat([a]), _flat([b]))
    builder.cswap(swapped, d0, d1)
    builder.cx(d0, shift); builder.isub(d1, target=shift)
    l0, l1 = builder.alloc_qubits(12), builder.alloc_qubits(12)
    _selected_leading_xor(builder, r0, d0, l0)
    _selected_leading_xor(builder, r1, d1, l1)
    builder.init_gf2_div(l0, l1, target=quotient, field=FIELD)
    _selected_leading_xor(builder, r0, d0, l0)
    _selected_leading_xor(builder, r1, d1, l1)
    builder.free(l0+l1)
    _row_update(builder, rows, quotient, shift)
    return d0, d1, shift, swapped, quotient


def _aux_step_inverse(builder, rows, record):
    r0, r1 = rows[0]
    d0, d1, shift, swapped, quotient = record
    _row_update(builder, rows, quotient, shift)
    l0, l1 = builder.alloc_qubits(12), builder.alloc_qubits(12)
    _selected_leading_xor(builder, r0, d0, l0)
    _selected_leading_xor(builder, r1, d1, l1)
    builder.del_gf2_div(l0, l1, target=quotient, field=FIELD)
    _selected_leading_xor(builder, r0, d0, l0)
    _selected_leading_xor(builder, r1, d1, l1)
    builder.free(l0+l1)
    builder.iadd(d1, target=shift); builder.cx(d0, shift)
    builder.cswap(swapped, d0, d1)
    for a, b in rows: builder.cswap(swapped, _flat([a]), _flat([b]))
    builder.flip_if_less_than(d0, d1, target=swapped)
    _degree_xor(builder, r0, d0); _degree_xor(builder, r1, d1)
    builder.free(d0+d1+shift+km.array([swapped])+quotient)


def _scale_inplace(builder, polynomial, factor, inverse_factor):
    """Invertible field scaling with one temporary word and MBU of old word."""
    temp = builder.alloc_qubits(12)
    for word in polynomial:
        _mul_accumulate(builder, word, factor, temp)
        builder.del_gf2_mul(temp, inverse_factor, target=word, field=FIELD)
        builder.swap(temp, word)
    builder.free(temp)


def _aux_step_compact(builder, rows, degrees):
    """Keep two live degrees; store only shift/swap/quotient per step."""
    r0,r1=rows[0];d0,d1=degrees
    shift=builder.alloc_qubits(5);swapped=builder.alloc_qubits(1)[0]
    quotient=builder.alloc_qubits(12)
    builder.flip_if_less_than(d0,d1,target=swapped)
    for a,b in rows:builder.cswap(swapped,_flat([a]),_flat([b]))
    builder.cswap(swapped,d0,d1)
    l0,l1=builder.alloc_qubits(12),builder.alloc_qubits(12)
    _selected_leading_xor(builder,r0,d0,l0);_selected_leading_xor(builder,r1,d1,l1)
    builder.init_gf2_div(l0,l1,target=quotient,field=FIELD)
    _selected_leading_xor(builder,r0,d0,l0);_selected_leading_xor(builder,r1,d1,l1)
    builder.free(l0+l1)
    builder.cx(d0,shift);builder.isub(d1,target=shift)
    builder.isub(d1,target=d0);builder.cx(shift,d0)
    _row_update(builder,rows,quotient,shift)
    _degree_xor(builder,r0,d0)
    return shift,swapped,quotient


def _aux_step_compact_inverse(builder,rows,degrees,record):
    r0,r1=rows[0];d0,d1=degrees;shift,swapped,quotient=record
    _degree_xor(builder,r0,d0)
    _row_update(builder,rows,quotient,shift)
    builder.cx(shift,d0);builder.iadd(d1,target=d0)
    l0,l1=builder.alloc_qubits(12),builder.alloc_qubits(12)
    _selected_leading_xor(builder,r0,d0,l0);_selected_leading_xor(builder,r1,d1,l1)
    builder.del_gf2_div(l0,l1,target=quotient,field=FIELD)
    _selected_leading_xor(builder,r0,d0,l0);_selected_leading_xor(builder,r1,d1,l1)
    builder.free(l0+l1)
    builder.iadd(d1,target=shift);builder.cx(d0,shift)
    builder.cswap(swapped,d0,d1)
    for a,b in rows:builder.cswap(swapped,_flat([a]),_flat([b]))
    builder.flip_if_less_than(d0,d1,target=swapped)
    builder.free(shift+km.array([swapped])+quotient)


def _square_inplace(builder,word,*,inverse=False):
    """Binary Gaussian decomposition of the exact Frobenius automorphism."""
    rows=[sum(((FIELD.square(1<<j)>>i)&1)<<j for j in range(12)) for i in range(12)]
    operations=[]
    for col in range(12):
        pivot=next(i for i in range(col,12) if rows[i]>>col&1)
        if pivot!=col:
            rows[col],rows[pivot]=rows[pivot],rows[col]
            operations.append(('swap',col,pivot))
        for row in range(12):
            if row!=col and rows[row]>>col&1:
                rows[row]^=rows[col];operations.append(('xor',col,row))
    assert rows==[1<<i for i in range(12)]
    for kind,a,b in (operations if inverse else reversed(operations)):
        if kind=='swap':builder.swap(word[a],word[b])
        else:builder.cx(word[a],word[b])


def _phase_reciprocal_point(builder,sigma_value,omega_value,reciprocal_value,mask):
    """23 Toffoli-like gates: 11 zero-test + 12 root-masked numerator ANDs."""
    chain=builder.alloc_qubits(11);located=builder.alloc_qubits(12)
    builder.x(sigma_value)
    builder.init_and(sigma_value[0],sigma_value[1],chain[0])
    for i in range(2,12):builder.init_and(chain[i-2],sigma_value[i],chain[i-1])
    builder.init_and(chain[-1],omega_value,located)
    builder.gf2_phase_by_product(located,reciprocal_value,mask=mask,field=FIELD)
    builder.del_and(chain[-1],omega_value,located)
    for i in range(11,1,-1):builder.del_and(chain[i-2],sigma_value[i],chain[i-1])
    builder.del_and(sigma_value[0],sigma_value[1],chain[0])
    builder.x(sigma_value);builder.free(chain+located)


def validate_streamed_kernel():
    """Independent field-product phase test across predicates/masks and HMR seeds."""
    import numpy as np
    b=km.CircuitBuilder()
    sigma=b.create_quantum_register(12,'sigma');omega=b.create_quantum_register(12,'omega')
    reciprocal=b.create_quantum_register(12,'reciprocal');mask=b.create_classical_register(12,'mask')
    _phase_reciprocal_point(b,sigma,omega,reciprocal,mask)
    circuit=b.finish_circuit();assert circuit.operation_statistics().num_toffoli_like==23
    n=16384;shifts=np.arange(12,dtype=np.uint32)[:,None]
    bits=lambda v:((v[None,:]>>shifts)&1).astype(bool)
    for seed in (2105,2106,2107):
        rng=np.random.default_rng(seed)
        sv=np.arange(n,dtype=np.uint32)&4095;sv[:8192]=0
        ov=rng.integers(0,4096,n,dtype=np.uint32);pv=rng.integers(0,4096,n,dtype=np.uint32)
        mv=np.arange(n,dtype=np.uint32)&4095
        for i,a in enumerate((0,1,4095)):
            for j,c in enumerate((0,1,4095)):
                k=3*i+j;ov[k]=a;pv[k]=c;mv[k]=4095
        product=np.array([FIELD.mul(int(a),int(c)) for a,c in zip(ov,pv)],dtype=np.uint32)
        parity=product&mv
        parity ^= parity>>8;parity ^= parity>>4;parity ^= parity>>2;parity ^= parity>>1
        expected=(sv==0)&((parity&1)!=0)
        sim=km.Simulator(n,debug_print=False,seed=seed);sim.use_same_registers_as(circuit)
        for reg,values in ((sigma,sv),(omega,ov),(reciprocal,pv),(mask,mv)):sim.write_across_shots(reg,bits(values))
        sim.do(circuit)
        for reg,values in ((sigma,sv),(omega,ov),(reciprocal,pv),(mask,mv)):assert np.array_equal(sim.read_across_shots(reg),bits(values))
        _assert_clean_except(sim,circuit,[sigma,omega,reciprocal])
        assert np.array_equal(sim.read_phase_flipped_across_shots(),expected)
    return {'verification_level':'streamed point kernel unit test, not decoder grading',
            'cases_checked':n*3,'measurement_seeds':[2105,2106,2107],
            'all_predicate_words_covered':True,'all_runtime_mask_words_covered':True,
            'static_toffoli_like':23,'qubits_including_36_inputs':circuit.num_qubits,
            'value_errors':0,'phase_errors':0,'workspace_errors':0}


def _scan_streamed_reciprocal(builder,sigma,omega,state,masks):
    # Psi(z)/z = sum B_i^2*z^(2i-1) + sum A_i^2*z^(2i).
    # Squaring and constant-field updates are Clifford; the original cofactor
    # words are restored before auxiliary EEA uncomputation.
    A,B=state['A'],state['B']
    for word in A+B:_square_inplace(builder,word)
    sv,ov,pv=(builder.alloc_qubits(12) for _ in range(3))
    groups=[(sigma,sv),(omega,ov),(A+B,pv)]
    vectors=[(_flat([regs]),km.array([q for _ in regs for q in value])) for regs,value in groups]
    steps=[(word,FIELD.pow(FIELD.primitive_element,k)) for k,word in enumerate(sigma) if k]
    steps += [(word,FIELD.pow(FIELD.primitive_element,k)) for k,word in enumerate(omega) if k]
    steps += [(word,FIELD.pow(FIELD.primitive_element,2*k)) for k,word in enumerate(A) if k]
    steps += [(word,FIELD.pow(FIELD.primitive_element,(2*k-1)%4095)) for k,word in enumerate(B)]
    active=builder.alloc_bits(1)[0]
    for j,mask in enumerate(masks):
        with builder.mark('streamed_reciprocal_point'):
            builder.bit_store(active,False);builder.bit_store(active,True,control=mask)
            builder.push_condition(active)
            for source,target in vectors:builder.cx(source,target)
            _phase_reciprocal_point(builder,sv,ov,pv,mask)
            for source,target in reversed(vectors):builder.cx(source,target)
            builder.pop_condition();builder.bit_store(active,False)
        if j+1<len(masks):
            for word,factor in steps:builder.gf2_imul(factor,target=word,field=FIELD)
    if len(masks)>1:
        for word,factor in steps:builder.gf2_idiv(FIELD.pow(factor,len(masks)-1),target=word,field=FIELD)
    builder.free(sv+ov+pv);builder.free(active)
    for word in reversed(A+B):_square_inplace(builder,word,inverse=True)


def _aligned_streamed_phase(builder,sigma,omega,masks,metrics=None):
    def count():
        s=builder.finish_circuit().operation_statistics()
        return s.num_toffoli_like,s.num_instructions
    last=count() if metrics is not None else (0,0)
    def record(name):
        nonlocal last
        if metrics is not None:
            now=count();metrics[name]={'static_toffoli_like':now[0]-last[0],'instructions':now[1]-last[1]};last=now
    with builder.mark('compact_bezout_forward'):
        state=_prepare_bezout(builder,sigma,compact=True)
    record('compact_bezout_forward')
    with builder.mark('streamed_reciprocal_sweep'):
        _scan_streamed_reciprocal(builder,sigma,omega,state,masks)
    record('streamed_reciprocal_sweep')
    with builder.mark('compact_bezout_reverse'):
        _erase_bezout(builder,sigma,state)
    record('compact_bezout_reverse')


def _prepare_bezout(builder, sigma, *, compact=False):
    polys = [_alloc_poly(builder, AUX_WORDS) for _ in range(6)]
    r0, r1, a0, a1, b0, b1 = polys
    for i in range(AUX_WORDS):
        _xor_frobenius(builder, sigma[2*i], r0[i], 11)
        _xor_frobenius(builder, sigma[2*i+1], r1[i], 11)
    builder.x(km.array([a0[0][0], b1[0][0]]))
    rows = [(r0, r1), (a0, a1), (b0, b1)]
    degrees = None
    if compact:
        degrees=(builder.alloc_qubits(5),builder.alloc_qubits(5))
        _degree_xor(builder,r0,degrees[0]);_degree_xor(builder,r1,degrees[1])
        tape=[_aux_step_compact(builder,rows,degrees) for _ in range(AUX_STEPS)]
    else:
        tape = [_aux_step(builder, rows) for _ in range(AUX_STEPS)]
    inverse_g, scaffold = builder.init_gf2_inverse_with_scaffold(r0[0], field=FIELD)
    _scale_inplace(builder, a0, inverse_g, r0[0])
    _scale_inplace(builder, b0, inverse_g, r0[0])
    return {'polys': polys, 'rows': rows, 'tape': tape, 'inverse_g': inverse_g,
            'scaffold': scaffold, 'A': a0, 'B': b0, 'compact':compact, 'degrees':degrees}


def _erase_bezout(builder, sigma, state):
    r0, r1, a0, a1, b0, b1 = state['polys']
    inverse_g = state['inverse_g']
    _scale_inplace(builder, a0, r0[0], inverse_g)
    _scale_inplace(builder, b0, r0[0], inverse_g)
    builder.del_gf2_inverse_with_scaffold(r0[0], target=inverse_g,
                                         scaffold=state['scaffold'], field=FIELD)
    builder.free(inverse_g+state['scaffold'])
    if state['compact']:
        for record in reversed(state['tape']):_aux_step_compact_inverse(builder,state['rows'],state['degrees'],record)
        _degree_xor(builder,r0,state['degrees'][0]);_degree_xor(builder,r1,state['degrees'][1])
        builder.free(state['degrees'][0]+state['degrees'][1])
    else:
        for record in reversed(state['tape']): _aux_step_inverse(builder, state['rows'], record)
    builder.x(km.array([a0[0][0], b1[0][0]]))
    for i in range(AUX_WORDS):
        _xor_frobenius(builder, sigma[2*i], r0[i], 11)
        _xor_frobenius(builder, sigma[2*i+1], r1[i], 11)
    builder.free(_flat(state['polys']))


def _prepare_error_polynomial(builder, omega, state):
    h = _alloc_poly(builder, 70)
    temp = builder.alloc_qubits(12)
    for j in range(36):
        source = state['B'][j//2] if j % 2 == 0 else state['A'][j//2]
        _xor_frobenius(builder, source, temp, 1)
        for i, word in enumerate(omega): _mul_accumulate(builder, word, temp, h[i+j])
        _xor_frobenius(builder, source, temp, 1)
    builder.free(temp)
    return h


def _erase_error_polynomial(builder, omega, h, state):
    measured = builder.alloc_bits(70*12)
    builder.hmr(_flat([h]), measured)
    temp = builder.alloc_qubits(12)
    for j in range(36):
        source = state['B'][j//2] if j % 2 == 0 else state['A'][j//2]
        _xor_frobenius(builder, source, temp, 1)
        for i, word in enumerate(omega):
            builder.gf2_phase_by_product(word, temp, mask=measured[(i+j)*12:(i+j+1)*12], field=FIELD)
        _xor_frobenius(builder, source, temp, 1)
    builder.free(temp); builder.free(measured); builder.free(_flat([h]))


def _scan_error_polynomial(builder, sigma, h, masks):
    sigma_value, error_value = builder.alloc_qubits(12), builder.alloc_qubits(12)
    active = builder.alloc_bits(1)[0]
    sigma_sources = _flat([sigma])
    h_sources = _flat([h])
    sigma_targets = km.array([q for _ in sigma for q in sigma_value])
    h_targets = km.array([q for _ in h for q in error_value])
    steps = [(word, FIELD.pow(FIELD.primitive_element, k)) for k, word in enumerate(sigma) if k]
    steps += [(word, FIELD.pow(FIELD.primitive_element, (k-1) % 4095)) for k, word in enumerate(h) if k != 1]
    for j, mask in enumerate(masks):
        with builder.mark('reciprocal_scan_point'):
            builder.bit_store(active, False)
            builder.bit_store(active, True, control=mask)
            builder.push_condition(active)
            builder.cx(sigma_sources, sigma_targets); builder.cx(h_sources, h_targets)
            phase_point(builder, sigma_value, error_value, mask)
            builder.cx(h_sources, h_targets); builder.cx(sigma_sources, sigma_targets)
            builder.pop_condition(); builder.bit_store(active, False)
        if j+1 < len(masks):
            for word, factor in steps: builder.gf2_imul(factor, target=word, field=FIELD)
    if len(masks) > 1:
        for word, factor in steps:
            builder.gf2_idiv(FIELD.pow(factor, len(masks)-1), target=word, field=FIELD)
    builder.free(sigma_value+error_value); builder.free(active)


def _aligned_phase(builder, sigma, omega, masks, metrics=None):
    last_t = last_ops = 0
    if metrics is not None:
        initial = builder.finish_circuit().operation_statistics()
        last_t, last_ops = initial.num_toffoli_like, initial.num_instructions
    def record(name):
        nonlocal last_t, last_ops
        if metrics is not None:
            circuit = builder.finish_circuit()
            stats = circuit.operation_statistics()
            metrics[name] = {'static_toffoli_like':stats.num_toffoli_like-last_t,
                             'instructions':stats.num_instructions-last_ops}
            last_t, last_ops = stats.num_toffoli_like, stats.num_instructions
    with builder.mark('bezout_forward'):
        state = _prepare_bezout(builder, sigma)
    record('bezout_forward')
    with builder.mark('error_polynomial_forward'):
        h = _prepare_error_polynomial(builder, omega, state)
    record('error_polynomial_forward')
    with builder.mark('phase_only_sweep'):
        _scan_error_polynomial(builder, sigma, h, masks)
    record('phase_only_sweep')
    with builder.mark('error_polynomial_mbuc'):
        _erase_error_polynomial(builder, omega, h, state)
    record('error_polynomial_mbuc')
    with builder.mark('bezout_reverse'):
        _erase_bezout(builder, sigma, state)
    record('bezout_reverse')


def build_candidate(layout="materialized_exact"):
    base = baseline_module()
    class BezoutDecoder(base.ProosAndZalkaDecoder):
        def _chien_search_and_forney_mbuc(self, builder, reg_b, masks, nb, nB):
            self._pre_align_reg_b(builder, reg_b, nb, nB, is_adjoint=False)
            phase=_aligned_streamed_phase if layout=='streamed_exact' else _aligned_phase
            phase(builder, reg_b[:36], list(reversed(reg_b[37:72])), masks)
            self._pre_align_reg_b(builder, reg_b, nb, nB, is_adjoint=True)
    builder = km.CircuitBuilder()
    syndromes = [builder.create_quantum_register(12, 'S'+str(i)) for i in range(70)]
    masks = [builder.create_classical_register(12, 'E'+str(j)) for j in range(4095)]
    BezoutDecoder(70, FIELD).build_syndrome_decoding_mbuc(
        builder, syndromes=syndromes, error_mbuc=masks, n_iters=base.default_n_iters(70))
    return builder.finish_circuit()


def _sample_locators():
    import random
    rng = random.Random(2103)
    locators = [trim(c['sigma']) for c in PACKED_CASES]
    for weight in range(36):
        for _ in range(3):
            f = [rng.randrange(1, 4096)]
            for j in rng.sample(range(4095), weight):
                f = mul(f, [FIELD.pow(FIELD.primitive_element, j), 1])
            locators.append(f)
    return locators


def validate_aux_model():
    """Check 18-word no-wrap invariants and <=35 cancellations on legal inputs."""
    max_active = max_degree = 0
    for f in _sample_locators():
        E = [FIELD.pow(x, 1 << 11) for x in f[0::2]]
        O = [FIELD.pow(x, 1 << 11) for x in f[1::2]]
        pad = lambda p: list(p) + [0] * (18-len(p))
        r0, r1, a0, a1, b0, b1 = pad(E), pad(O), pad([1]), pad([]), pad([]), pad([1])
        active = 0
        for _ in range(AUX_STEPS):
            deg = lambda p: max((i+1 for i, x in enumerate(p) if x), default=0)
            d0, d1 = deg(r0), deg(r1)
            if d0 < d1:
                r0, r1, a0, a1, b0, b1 = r1, r0, a1, a0, b1, b0
                d0, d1 = d1, d0
            shift = d0-d1
            q = FIELD.div(r0[d0-1], r1[d1-1]) if d1 else 0
            if q:
                active += 1
                for dst, src in ((r0,r1),(a0,a1),(b0,b1)):
                    for j, value in enumerate(src):
                        if value:
                            assert j+shift < 18, ('cofactor wrap', len(f)-1, j, shift)
                            dst[j+shift] ^= FIELD.mul(q, value)
            max_degree = max(max_degree, *(deg(p)-1 for p in (a0,a1,b0,b1)))
        assert trim(r1) == [] and len(trim(r0)) == 1 and r0[0]
        assert add(mul(trim(a0), E), mul(trim(b0), O)) == [r0[0]]
        assert active <= 35
        max_active = max(max_active, active)
    return {'verification_level':'classical fixed-step invariant check, not decoder grading',
            'cases':len(_sample_locators()),'aux_steps':AUX_STEPS,
            'max_active_cancellations':max_active,'max_cofactor_degree':max_degree,
            'wrap_errors':0,'bezout_errors':0}


def _write_words(sim, registers, cases):
    import numpy as np
    for i, word in enumerate(registers):
        sim.write_across_shots(word, np.array([[(p[i] >> bit) & 1 for p in cases]
                                              for bit in range(12)], dtype=bool))


def _read_words(sim, registers):
    import numpy as np
    return [sum(sim.read_across_shots(word)[i].astype(np.uint16) << i for i in range(12))
            for word in registers]


def _assert_clean_except(sim, circuit, registers):
    allowed = {q for reg in registers for q in reg}
    junk = km.array([km.q(i) for i in range(circuit.num_qubits) if km.q(i) not in allowed])
    assert not sim.read_across_shots(junk).any(), 'nonzero quantum workspace'


def validate_aux_circuit(*, compact=False):
    """Check real coherent EEA/cofactor extraction and complete inverse cleanup."""
    import numpy as np
    cases = [list(c['sigma']) for c in PACKED_CASES]
    cases += [f+[0]*(36-len(f)) for f in _sample_locators()[6::9]]
    b = km.CircuitBuilder()
    sigma = [b.create_quantum_register(12, 'sigma'+str(i)) for i in range(36)]
    state = _prepare_bezout(b, sigma, compact=compact)
    copies = {}
    for name, polynomial in (('A',state['A']),('B',state['B']),('R0',state['polys'][0]),('R1',state['polys'][1])):
        copies[name] = [b.create_quantum_register(12, name+str(i)) for i in range(18)]
        b.cx(_flat([polynomial]), _flat([copies[name]]))
    _erase_bezout(b, sigma, state)
    circuit = b.finish_circuit()
    sim = km.Simulator(len(cases),debug_print=False,seed=2103)
    sim.use_same_registers_as(circuit); _write_words(sim,sigma,cases); sim.do(circuit)
    actual = {name:_read_words(sim,regs) for name,regs in copies.items()}
    for k,f in enumerate(cases):
        A = trim([int(x[k]) for x in actual['A']]); B = trim([int(x[k]) for x in actual['B']])
        R0 = trim([int(x[k]) for x in actual['R0']]); R1 = trim([int(x[k]) for x in actual['R1']])
        E = [FIELD.pow(x,1<<11) for x in f[0::2]]; O = [FIELD.pow(x,1<<11) for x in f[1::2]]
        assert add(mul(A,E),mul(B,O)) == [1], ('coherent Bezout',k)
        assert len(R0)==1 and R0[0] and R1==[]
    read_sigma = _read_words(sim,sigma)
    assert all(int(read_sigma[i][k])==f[i] for k,f in enumerate(cases) for i in range(36))
    _assert_clean_except(sim,circuit,sigma+[reg for regs in copies.values() for reg in regs])
    assert not sim.read_phase_flipped_across_shots().any(), 'unexpected auxiliary EEA phase'
    return {'verification_level':'coherent auxiliary EEA unit test, not decoder grading',
            'cases':len(cases),'value_errors':0,'phase_errors':0,'workspace_errors':0,
            'compact_degree_history':compact,
            'test_circuit_qubits_including_snapshots':circuit.num_qubits,
            'test_circuit_static_toffoli_like':circuit.operation_statistics().num_toffoli_like}


def validate_phase_block(*, layout="materialized_exact"):
    """Compare only the new phase component against packed boundary fixtures."""
    import numpy as np
    import time
    cases = list(PACKED_CASES)
    # Dense generic locators complement the native sparse degree-drop fixtures.
    locators = _sample_locators()
    for weight in (2,17,34,35):
        f = locators[6+3*weight]
        errors = {}
        w = []
        for j in range(4095):
            z = FIELD.pow(FIELD.primitive_element,j)
            if evaluate(f,z)==0:
                value = ((j*313)^0x123)&4095 or 1
                errors[str(j)] = value
                quotient,remainder = divide(f,[z,1])
                assert remainder==[]
                w = add(w,[FIELD.mul(x,FIELD.mul(value,z)) for x in quotient])
        assert len(errors)==weight
        cases.append({'sigma':f+[0]*(36-len(f)),'omega':w+[0]*(35-len(w)),
                      'expected_errors':errors})
    b = km.CircuitBuilder()
    sigma = [b.create_quantum_register(12,'sigma'+str(i)) for i in range(36)]
    omega = [b.create_quantum_register(12,'omega'+str(i)) for i in range(35)]
    masks = [b.create_classical_register(12,'M'+str(j)) for j in range(4095)]
    started = time.monotonic()
    metrics = {}
    phase=_aligned_streamed_phase if layout=='streamed_exact' else _aligned_phase
    phase(b,sigma,omega,masks,metrics=metrics)
    circuit = b.finish_circuit()
    sim = km.Simulator(len(cases),debug_print=False,seed=2104)
    sim.use_same_registers_as(circuit)
    _write_words(sim,sigma,[c['sigma'] for c in cases]); _write_words(sim,omega,[c['omega'] for c in cases])
    expected = np.zeros(len(cases),dtype=bool)
    for j,mask in enumerate(masks):
        words = [((j*197) ^ (k*313) ^ 0x924) & 4095 for k in range(len(cases))]
        sim.write_across_shots(mask,np.array([[(v>>i)&1 for v in words] for i in range(12)],dtype=bool))
        for k,c in enumerate(cases):
            error = c['expected_errors'].get(str(j),0)
            expected[k] ^= bool((error & words[k]).bit_count() & 1)
    sim.do(circuit)
    for regs,name in ((sigma,'sigma'),(omega,'omega')):
        values=_read_words(sim,regs)
        assert all(int(values[i][k])==c[name][i] for k,c in enumerate(cases) for i in range(len(regs))), name+' not restored'
    _assert_clean_except(sim,circuit,sigma+omega)
    assert np.array_equal(sim.read_phase_flipped_across_shots(),expected), 'phase block wrong sign'
    return {'verification_level':'phase block boundary unit test, not full decoder grading',
            'layout':layout,'cases':len(cases),'points_per_case':4095,'value_errors':0,'phase_errors':0,
            'workspace_errors':0,'component_qubits':circuit.num_qubits,
            'component_static_toffoli_like':circuit.operation_statistics().num_toffoli_like,
            'component_instructions':circuit.operation_statistics().num_instructions,
            'stages':metrics,
            'elapsed_seconds':time.monotonic()-started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path(__file__).parent/'configs/bezout_reference.json')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--overwrite', action='store_true')
    action = parser.add_mutually_exclusive_group()
    for flag in ('validate-packed','validate-model','validate-kernel','audit-resources',
                 'validate-aux-model','validate-aux-circuit','validate-phase-block'):
        action.add_argument('--'+flag,action='store_true')
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    path = args.config.resolve()
    if path.parent != (directory/'configs').resolve() or path.suffix != '.json':
        raise ValueError('Config must resolve directly inside this experiment configs/')
    import re
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',path.stem):
        raise ValueError('Invalid config filename')
    config=json.loads(path.read_text())
    probe={'m':4095,'n':70,'degree':12,'layout':'materialized_probe'}
    reference={'m':4095,'n':70,'degree':12,'layout':'materialized_exact','aux_steps':36}
    streamed={'m':4095,'n':70,'degree':12,'layout':'streamed_exact','aux_steps':36,'compact_degree_history':True}
    if config not in (probe,reference,streamed): raise ValueError('Unsupported exact config')
    actions={'validate_packed':validate_packed_mapping,'validate_model':validate_model,
             'validate_kernel':lambda:validate_streamed_kernel() if config==streamed else validate_kernel(),'audit_resources':audit_resources,
             'validate_aux_model':validate_aux_model,'validate_aux_circuit':lambda:validate_aux_circuit(compact=config==streamed),
             'validate_phase_block':lambda:validate_phase_block(layout=config['layout'])}
    for flag,func in actions.items():
        if getattr(args,flag):
            print(json.dumps(func(),indent=2)); return
    if config==probe: raise ValueError('Probe config is not a decoder build config')
    track=directory.parent.name; experiment_id=directory.name; root=directory.parents[2]
    if directory.parent.parent.name!='src' or track!='dqi':
        raise ValueError('Expected src/dqi/<ID>/solution.py')
    output=args.output or root/'artifacts'/track/experiment_id/(path.stem+'.kmb')
    if output.name!=path.stem+'.kmb': raise ValueError('Output must match config stem')
    if output.exists() and not args.overwrite: raise FileExistsError('Pass --overwrite for intentional rebuild')
    output.parent.mkdir(parents=True,exist_ok=True)
    circuit=build_candidate(layout=config["layout"])
    circuit.to_file(str(output),format='kmb')
    print(json.dumps({'status':'BUILT','artifact_path':str(output),'num_qubits':circuit.num_qubits,
                     'static_toffoli_like':circuit.operation_statistics().num_toffoli_like,
                     'num_instructions':circuit.operation_statistics().num_instructions},indent=2))


if __name__ == '__main__': main()
