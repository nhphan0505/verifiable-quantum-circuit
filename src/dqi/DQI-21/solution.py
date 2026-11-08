"""DQI-21: feasibility/model probes for a Bezout reciprocal phase sweep.

Owner trng-hminh; https://github.com/nhphan0505/verifiable-quantum-circuit/issues/21.
Baseline interface/source: bb3a6311113217a69c64e88e9c3bb0513237a1f9,
DQI-BASELINE/solution.py, Apache-2.0 (src/LICENSE.txt). References and exact
input/output conventions are in DESCRIPTION.md. This file is a feasibility
harness, NOT a complete DQI submission compiler and never runs the grader.

Algorithm: split a square-free packed locator f=E^2+z*O^2, compute classical
reference Bezout coefficients A*E+B*O=1, then Psi=B^2+z*A^2. On a root,
Psi*f'=1. For packed s=z^v*f, precompute Htilde=z^(35-v)*w*Psi; the native
Forney value at z=alpha^j is z^-36*Htilde(z). The un-deflated native derivative
is z*s'(z), not s'(z). Runtime masks select binary parity in the Kickmix
polynomial basis; no offline-fixed mask or omitted positions are assumed.
The scalar reference xgcd below is NOT claimed to be reversible circuit code.

The emitted isolated point kernel computes a 12-bit zero predicate with 11
init_and operations, phases value bits through runtime-mask-controlled CZs,
then uses del_and to erase the complete predicate chain and restores inputs.
It has exactly 11 Toffoli-like gates; polynomial/Bézout preprocessing is absent
from this isolated kernel and must not be hidden in the claimed sweep cost.

Probes check Bezout/reciprocal identities, real packed EEA boundary fixtures,
root values/phase, and exhaustive point-kernel phase/value/workspace. Resource
probe compiles baseline blocks only, compares an optimistic static Q^2*T model
for separately materializing 70 coefficients, and assigns zero cost/workspace
to all other preprocessing. This rules out that allocation strategy when even
its optimistic ratio exceeds one; it does not disprove in-place Bezout/Hankel.
No approximation, cutoff, intentional overflow, old-artifact renaming, score,
or decoder PASS is produced. Complete reversible in-place preprocessing and
its degree-drop/no-error cleanup remain required before a submission build.

Run from repo root with Python 3.13 and pinned requirements:
  python src/dqi/DQI-21/solution.py --validate-packed
  python src/dqi/DQI-21/solution.py --validate-model
  python src/dqi/DQI-21/solution.py --validate-kernel
  python src/dqi/DQI-21/solution.py --audit-resources
Config resolves directly under this experiment's configs/. Outputs are probe
JSON, not verifier evidence; DESCRIPTION.md records the limits and stop reason.
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
            'decision': 'Reject separate materialized-polynomial layout; derive in-place Bezout/Hankel preprocessing before a decoder build',
            'limitation': 'Does not disprove H2 or in-place designs. Classical mask skips, statistical penalty and executed counts require real decoder grading.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path(__file__).parent/'configs/exact_probe.json')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--validate-packed', action='store_true')
    action.add_argument('--validate-model', action='store_true')
    action.add_argument('--validate-kernel', action='store_true')
    action.add_argument('--audit-resources', action='store_true')
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    path = args.config.resolve()
    if path.parent != (directory/'configs').resolve() or path.suffix != '.json':
        raise ValueError('Config must resolve directly inside this experiment configs/')
    if json.loads(path.read_text()) != {'m': 4095, 'n': 70, 'degree': 12, 'layout': 'materialized_probe'}:
        raise ValueError('Only the declared exact materialization feasibility probe is supported')
    result = validate_packed_mapping() if args.validate_packed else validate_model() if args.validate_model else validate_kernel() if args.validate_kernel else audit_resources()
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
