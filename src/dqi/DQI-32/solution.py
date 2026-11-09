"""DQI-32 stage 3 screening for an in-place Bézout phase block.

Run with --config structured_probe.json --validate-phase-block. The classical
factorization changes only the evaluator and returns its inverse schedule.
The circuit probes use quantum polynomial coefficients for packed division
and a runtime classical mask for the sweep. The division degrees are fixed
for each probe. A coherent variable-degree schedule must pass the resource
gate in DESCRIPTION.md before this module can emit a submission artifact.

The baseline EEA layout, GF(2^12) basis, DQI-21 field arithmetic and phase
conventions are retained. All arithmetic is exact under the stated promises.
"""

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import random

import kickmix as km
import numpy as np

DQI21_SHA256 = "32ff5f4ffeade7b98c4470a179e3b57111eb13184125a5d37b693818ffe4aa02"


def load_dqi21():
    """Load the pinned arithmetic, sweep and packed fixtures."""
    path = Path(__file__).resolve().parents[1] / "DQI-21" / "solution.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != DQI21_SHA256:
        raise ValueError("DQI-21 source differs from the pinned dependency")
    spec = importlib.util.spec_from_file_location("dqi32_dqi21", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def division_ops(divisor, size, field):
    """P^-1: store the remainder low and the quotient high, in the same words."""
    degree = len(divisor) - 1
    inverse_lead = field.invert(divisor[-1])
    for high in range(size - 1, degree - 1, -1):
        yield ("scale", high, high, inverse_lead)
        for j, coefficient in enumerate(divisor[:-1]):
            yield ("shear", high - degree + j, high, coefficient)


def solve_b1_ops(polynomial, start, field):
    """Invert the anti-triangular B(polynomial,1) in place."""
    size = len(polynomial) - 1
    inverse_lead = field.invert(polynomial[-1])
    for i in range(size // 2):
        yield ("swap", start + i, start + size - i - 1, 0)
    for i in range(size):
        for j in range(i):
            yield ("shear", start + i, start + j, polynomial[size - i + j])
        yield ("scale", start + i, start + i, inverse_lead)


def multiply_b1_ops(polynomial):
    """Apply B(polynomial,1) in place."""
    size = len(polynomial) - 1
    for i in range(size // 2):
        yield ("swap", i, size - i - 1, 0)
    for i in range(size):
        yield ("scale", i, i, polynomial[-1])
        for j in range(i + 1, size):
            yield ("shear", i, j, polynomial[size + i - j])


def bezout_solve_ops(factors, field):
    """Apply B(s,D)^-1 using B(f,g)=P diag(B(g,r), B(q,1)) P^T."""
    divisions = []
    for size, divisor, quotient in factors:
        divide = list(division_ops(divisor, size, field))
        divisions.append(divide)
        yield from divide
        yield from solve_b1_ops(quotient, len(divisor) - 1, field)
    for divide in reversed(divisions):
        for kind, dst, src, coefficient in reversed(divide):
            yield (kind, src, dst, coefficient)


def derivative_factors(locator, previous):
    """Generate Euclid factors with packed E/O words and degree-only replay."""
    field = previous.FIELD
    even = previous.trim(field.pow(x, 1 << 11) for x in locator[::2])
    odd = previous.trim(field.pow(x, 1 << 11) for x in locator[1::2])
    banks = [even + [0] * (18 - len(even)), odd + [0] * (18 - len(odd))]
    lengths = [len(even), len(odd)]
    factors, history = [], []
    target = 0
    while lengths[1 - target]:
        divisor = banks[1 - target][:lengths[1 - target]]
        size = lengths[target]
        split = len(divisor) - 1
        words = banks[target]
        ops = list(division_ops(divisor, size, field))
        apply_ops(words, ops, field)
        remainder = previous.trim(words[:min(size, split)])
        quotient = words[split:size]
        if not history:
            first_quotient = previous.add(previous.square(quotient), [0, 1])
            derivative = previous.square(divisor)
            assert previous.add(previous.mul(first_quotient, derivative),
                                previous.square(remainder)) == locator
            factors.append((len(locator) - 1, derivative, first_quotient))
        else:
            factors.append((2 * (size - 1), previous.square(divisor),
                            previous.square(quotient)))
        history.append((target, size, len(divisor)))
        lengths[target] = len(remainder)
        target = 1 - target
    if lengths[target] != 1:
        raise ValueError("Expected a square-free locator")
    for target, size, divisor_size in reversed(history):
        divisor = banks[1 - target][:divisor_size]
        apply_ops(banks[target], list(division_ops(divisor, size, field)), field, inverse=True)
    assert previous.trim(banks[0]) == even and previous.trim(banks[1]) == odd
    return factors


def evaluator_ops(locator, previous):
    """Create the structured exact schedule on the active remainder slots."""
    if len(locator) == 1:
        return [], []
    factors = derivative_factors(locator, previous)
    ops = list(bezout_solve_ops(factors, previous.FIELD))
    ops.extend(multiply_b1_ops(locator))
    return ops, [len(quotient) - 1 for _, _, quotient in factors]


def apply_ops(words, ops, field, *, inverse=False):
    """Apply a linear operation schedule on a coefficient vector."""
    for kind, dst, src, coefficient in reversed(ops) if inverse else ops:
        if kind == "swap":
            words[dst], words[src] = words[src], words[dst]
        elif kind == "scale":
            factor = field.invert(coefficient) if inverse else coefficient
            words[dst] = field.mul(words[dst], factor)
        else:
            words[dst] ^= field.mul(coefficient, words[src])


def validate_model(previous, config):
    """Compare the structured evaluator with independent polynomial EEA."""
    rng = random.Random(config["seed"])
    field = previous.FIELD
    fixtures = [(case["sigma"], case["omega"]) for case in previous.PACKED_CASES]
    points = [field.pow(field.primitive_element, j) for j in range(config["m"])]
    for degree in range(config["n"] // 2 + 1):
        for _ in range(config["cases_per_locator_degree"]):
            locator = [rng.randrange(1, 4096)]
            for point in rng.sample(points, degree):
                locator = previous.mul(locator, [point, 1])
            omega = [rng.randrange(4096) for _ in range(degree)] + [0] * (35 - degree)
            fixtures.append((locator, omega))
    # z^35 + 1 splits over GF(4096) because 35 divides 4095.
    # Its derivative Euclid chain exercises a jump from degree 34 to zero.
    fixtures.append(([1] + [0] * 34 + [1], [1] + [0] * 34))
    peak_ops = Counter()
    deepest_drop = 0
    for locator, omega in fixtures:
        locator = previous.trim(locator)
        ops, drops = evaluator_ops(locator, previous)
        assert not any(omega[len(locator) - 1:])
        transformed = omega.copy()
        apply_ops(transformed, ops, field)
        if len(locator) > 1:
            psi, _ = previous.reciprocal_reference(locator)
            _, expected = previous.divide(previous.mul(omega, psi), locator)
            assert previous.trim(transformed) == expected
        apply_ops(transformed, ops, field, inverse=True)
        assert transformed == omega
        peak_ops |= Counter(kind for kind, _, _, _ in ops)
        deepest_drop = max([deepest_drop, *drops])
    return {"cases": len(fixtures), "degrees": [0, 35],
            "max_quotient_degree": deepest_drop,
            "max_operations_by_kind": dict(peak_ops)}


def packed_division(builder, words, divisor, previous, *, inverse=False):
    """Emit P^-1 or P for quantum coefficients with a fixed divisor degree.

    High words store the quotients, and the low prefix stores the remainder.
    The divisor stays live and must have a nonzero leading coefficient.
    """
    lead = divisor[-1]
    field = previous.FIELD
    reciprocal, scaffold = builder.init_gf2_inverse_with_scaffold(lead, field=field)
    degree = len(divisor) - 1
    order = range(degree, len(words)) if inverse else range(len(words) - 1, degree - 1, -1)
    for high in order:
        word = words[high]
        if not inverse:
            previous._scale_inplace(builder, [word], reciprocal, lead)
        for j, coefficient in enumerate(divisor[:-1]):
            previous._mul_accumulate(builder, word, coefficient, words[high - degree + j])
        if inverse:
            previous._scale_inplace(builder, [word], lead, reciprocal)
    builder.del_gf2_inverse_with_scaffold(lead, target=reciprocal, scaffold=scaffold, field=field)
    builder.free(reciprocal + scaffold)


def validate_division(previous, config):
    """Test both directions separately against polynomial division on basis inputs."""
    rng = random.Random(config["seed"])
    reports = []
    for degree in (0, 8, 17):
        size = 18
        divisors = [[rng.randrange(4096) for _ in range(degree)] + [rng.randrange(1, 4096)]
                    for _ in range(128)]
        inputs = [[rng.randrange(4096) for _ in range(size)] for _ in divisors]
        packed = []
        for words, divisor in zip(inputs, divisors):
            quotient, remainder = previous.divide(words, divisor)
            packed.append(remainder + [0] * (degree - len(remainder))
                          + quotient + [0] * (size - degree - len(quotient)))
        for inverse in (False, True):
            builder = km.CircuitBuilder()
            words = [builder.create_quantum_register(12, f"word{i}") for i in range(size)]
            divisor = [builder.create_quantum_register(12, f"div{i}") for i in range(degree + 1)]
            packed_division(builder, words, divisor, previous, inverse=inverse)
            circuit = builder.finish_circuit()
            initial, expected = (packed, inputs) if inverse else (inputs, packed)
            for seed in config["measurement_seeds"]:
                simulator = km.Simulator(len(inputs), debug_print=False, seed=seed)
                simulator.use_same_registers_as(circuit)
                previous._write_words(simulator, words, initial)
                previous._write_words(simulator, divisor, divisors)
                simulator.do(circuit)
                assert np.array_equal(previous._read_words(simulator, words), np.asarray(expected).T)
                assert np.array_equal(previous._read_words(simulator, divisor), np.asarray(divisors).T)
                previous._assert_clean_except(simulator, circuit, words + divisor)
                assert not np.any(simulator.read_phase_flipped_across_shots())
            reports.append({"divisor_degree": degree, "inverse": inverse, "cases_per_seed": len(inputs),
                            "static_toffoli_like": circuit.operation_statistics().num_toffoli_like,
                            "scratch_qubits": circuit.num_qubits - 12 * (size + degree + 1)})
    return reports


def validate_sweep(previous, config):
    """Emit all 4095 phase points and compare against known RS errors."""
    cases = previous.PACKED_CASES
    field = previous.FIELD
    evaluators = []
    for case in cases:
        evaluator = case["omega"].copy()
        ops, _ = evaluator_ops(previous.trim(case["sigma"]), previous)
        apply_ops(evaluator, ops, field)
        evaluators.append(evaluator)
    builder = km.CircuitBuilder()
    sigma = [builder.create_quantum_register(12, f"sigma{i}") for i in range(36)]
    evaluator = [builder.create_quantum_register(12, f"r{i}") for i in range(35)]
    masks = [builder.create_classical_register(12, f"E{i}") for i in range(config["m"])]
    previous._scan_error_polynomial(builder, sigma, evaluator, masks)
    circuit = builder.finish_circuit()
    toffoli = circuit.operation_statistics().num_toffoli_like
    assert toffoli == 11 * config["m"]
    shifts = np.arange(12, dtype=np.uint32)[:, None]
    for seed in config["measurement_seeds"]:
        simulator = km.Simulator(len(cases), debug_print=False, seed=seed)
        simulator.use_same_registers_as(circuit)
        previous._write_words(simulator, sigma, [case["sigma"] for case in cases])
        previous._write_words(simulator, evaluator, evaluators)
        rng = np.random.default_rng(seed)
        expected = np.zeros(len(cases), dtype=bool)
        for j, mask in enumerate(masks):
            values = rng.integers(0, 4096, len(cases), dtype=np.uint32)
            if j % 5 == 0:
                values[0] = 0
            simulator.write_across_shots(mask, ((values[None, :] >> shifts) & 1).astype(bool))
            for i, case in enumerate(cases):
                error = case["expected_errors"].get(str(j), 0)
                expected[i] ^= (int(values[i]) & error).bit_count() % 2 != 0
        simulator.do(circuit)
        assert np.array_equal(previous._read_words(simulator, sigma),
                              np.asarray([case["sigma"] for case in cases]).T)
        assert np.array_equal(previous._read_words(simulator, evaluator), np.asarray(evaluators).T)
        previous._assert_clean_except(simulator, circuit, sigma + evaluator)
        assert np.array_equal(simulator.read_phase_flipped_across_shots(), expected)
    return {"packed_cases_per_seed": len(cases), "points": config["m"],
            "static_toffoli_like": toffoli, "qubits_including_inputs": circuit.num_qubits}


def resource_screen(sweep_t):
    """Compute optimistic costs for the separate-transcript schedule."""
    baseline_q, baseline_t = 1893, 5725461
    retained_eea_t, eea_live_q = 4280724, 1803
    compact_history_q = 36 * (5 + 1 + 12) + 10
    q_floor = eea_live_q + compact_history_q
    optimistic_t = retained_eea_t + sweep_t
    return {"separate_transcript_q_floor": q_floor,
            "q_with_two_separate_cofactors_before_scratch": q_floor + 2 * 18 * 12,
            "optimistic_q2t_ratio_vs_baseline": (q_floor / baseline_q) ** 2 * optimistic_t / baseline_t,
            "gate": "stop_before_full_build",
            "reason": "Separate history exceeds peak; coherent variable-degree packed replay is unverified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-phase-block", action="store_true")
    args = parser.parse_args()
    if not args.validate_phase_block:
        parser.error("This screening config requires --validate-phase-block")
    path = args.config.resolve()
    if path.parent != Path(__file__).resolve().parent / "configs" or path.suffix != ".json":
        parser.error("Select a JSON config from this experiment's configs directory")
    config = json.loads(path.read_text())
    if (config["m"], config["n"], config["degree"]) != (4095, 70, 12):
        parser.error("This probe requires the DQI benchmark dimensions")
    previous = load_dqi21()
    report = {"verification_level": "classical factorization and isolated circuit probes",
              "measurement_seeds": config["measurement_seeds"],
              "model": validate_model(previous, config),
              "packed_division": validate_division(previous, config)}
    report["sweep"] = validate_sweep(previous, config)
    report["screen"] = resource_screen(report["sweep"]["static_toffoli_like"])
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
