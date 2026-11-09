"""DQI-32 stage 3 screening for an in-place Bézout phase block.

Run with --config structured_probe.json --validate-phase-block. The classical
factorization changes only the evaluator and returns its inverse schedule.
The circuit probes use quantum polynomial coefficients for packed division
and a runtime classical mask for the sweep. The division degrees are fixed
for each packed probe. The modular_reference config builds a diagnostic
variable-degree decoder using a companion shift and a temporary bank.

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


def companion_parameters(builder, sigma, width, previous):
    """Keep the locator fixed while selecting its nonzero lead and prefix."""
    degree = builder.alloc_qubits(len(sigma).bit_length())
    lead = builder.alloc_qubits(12)
    prefix = builder.alloc_qubits(width - 1)
    previous._degree_xor(builder, sigma, degree)
    previous._selected_leading_xor(builder, sigma, degree, lead)
    for i, flag in enumerate(prefix, 1):
        builder.x(flag)
        builder.flip_if_less_than(degree, i + 2, target=flag)
    field = previous.FIELD
    inverse, scaffold = builder.init_gf2_inverse_with_scaffold(lead, field=field)
    scale = builder.init_gf2_mul(sigma[0], inverse, field=field)
    inverse_scale = builder.init_gf2_div(lead, sigma[0], field=field)
    return degree, lead, prefix, inverse, scaffold, scale, inverse_scale


def erase_companion_parameters(builder, sigma, state, previous):
    """Clear the state shared by every modular shift."""
    degree, lead, prefix, inverse, scaffold, scale, inverse_scale = state
    field = previous.FIELD
    builder.del_gf2_div(lead, sigma[0], target=inverse_scale, field=field)
    builder.del_gf2_mul(sigma[0], inverse, target=scale, field=field)
    builder.del_gf2_inverse_with_scaffold(lead, target=inverse, scaffold=scaffold, field=field)
    for i, flag in enumerate(prefix, 1):
        builder.flip_if_less_than(degree, i + 2, target=flag)
        builder.x(flag)
    previous._selected_leading_xor(builder, sigma, degree, lead)
    previous._degree_xor(builder, sigma, degree)
    builder.free(degree + lead + prefix + inverse + scaffold + scale + inverse_scale)


def companion_shift(builder, sigma, words, state, previous, *, inverse=False):
    """Multiply by z modulo s on the active prefix, or apply the inverse."""
    _, _, prefix, inverse_lead, _, scale, inverse_scale = state
    field = previous.FIELD
    if inverse:
        previous._scale_inplace(builder, words[:1], inverse_scale, scale)
    else:
        for i in range(len(words) - 1, 0, -1):
            builder.cswap(prefix[i - 1], words[i - 1], words[i])
    ratio = builder.init_gf2_mul(words[0], inverse_lead, field=field)
    masked = builder.alloc_qubits(12)
    for i, flag in enumerate(prefix, 1):
        builder.init_and(flag, sigma[i], masked)
        previous._mul_accumulate(builder, ratio, masked, words[i])
        builder.del_and(flag, sigma[i], masked)
    builder.free(masked)
    builder.del_gf2_mul(words[0], inverse_lead, target=ratio, field=field)
    builder.free(ratio)
    if inverse:
        for i, flag in enumerate(prefix, 1):
            builder.cswap(flag, words[i - 1], words[i])
    else:
        previous._scale_inplace(builder, words[:1], scale, inverse_scale)


def modular_product(builder, sigma, source, coefficients, state, previous, *,
                    square_coefficients, target=None, mask=None):
    """XOR the reduced product into target, or apply its parity against mask."""
    field = previous.FIELD
    square = builder.alloc_qubits(12) if square_coefficients else None
    last = 0
    for exponent, coefficient in coefficients:
        for _ in range(exponent - last):
            companion_shift(builder, sigma, source, state, previous)
        factor = coefficient
        if square_coefficients:
            previous._xor_frobenius(builder, coefficient, square, 1)
            factor = square
        for i, word in enumerate(source):
            if target is None:
                builder.gf2_phase_by_product(word, factor, mask=mask[12 * i:12 * (i + 1)], field=field)
            else:
                previous._mul_accumulate(builder, word, factor, target[i])
        if square_coefficients:
            previous._xor_frobenius(builder, coefficient, square, 1)
        last = exponent
    for _ in range(last):
        companion_shift(builder, sigma, source, state, previous, inverse=True)
    if square_coefficients:
        builder.free(square)


def transform_evaluator(builder, sigma, omega, previous, *, inverse=False):
    """Replace omega by its modular image, then erase the old value by phase."""
    bezout = previous._prepare_bezout(builder, sigma, compact=True)
    companion = companion_parameters(builder, sigma, len(omega), previous)
    psi = [(i, bezout["A" if i % 2 else "B"][i // 2]) for i in range(len(sigma))]
    derivative = [(2 * i, word) for i, word in enumerate(sigma[1::2])]
    forward, reverse = (derivative, psi) if inverse else (psi, derivative)
    transformed = previous._alloc_poly(builder, len(omega))
    modular_product(builder, sigma, omega, forward, companion, previous,
                    square_coefficients=not inverse, target=transformed)
    measured = builder.alloc_bits(12 * len(omega))
    builder.hmr(previous._flat([omega]), measured)
    modular_product(builder, sigma, transformed, reverse, companion, previous,
                    square_coefficients=inverse, mask=measured)
    builder.free(measured)
    builder.swap(previous._flat([omega]), previous._flat([transformed]))
    builder.free(previous._flat([transformed]))
    erase_companion_parameters(builder, sigma, companion, previous)
    previous._erase_bezout(builder, sigma, bezout)


def modular_phase_block(builder, sigma, omega, masks, previous):
    with builder.mark("modular_evaluator_forward"):
        transform_evaluator(builder, sigma, omega, previous)
    with builder.mark("phase_only_sweep"):
        previous._scan_error_polynomial(builder, sigma, omega, masks)
    with builder.mark("modular_evaluator_reverse"):
        transform_evaluator(builder, sigma, omega, previous, inverse=True)


def validate_modular_reference(previous):
    """Compare both coherent transforms and the end-to-end phase block."""
    rng = random.Random(32026)
    field = previous.FIELD
    cases = list(previous.PACKED_CASES)
    for degree in (2, 3, 4, 8, 17, 18, 34, 35):
        sigma = [rng.randrange(1, 4096)]
        for position in rng.sample(range(4095), degree):
            sigma = previous.mul(sigma, [field.pow(field.primitive_element, position), 1])
        cases.append({"sigma": sigma + [0] * (36 - len(sigma)),
                      "omega": [rng.randrange(4096) for _ in range(degree)] + [0] * (35 - degree)})
    locators = [case["sigma"] for case in cases]
    evaluators = [case["omega"] for case in cases]
    remainders = []
    for case in cases:
        value = case["omega"].copy()
        ops, _ = evaluator_ops(previous.trim(case["sigma"]), previous)
        apply_ops(value, ops, field)
        remainders.append(value)
    reports = []
    for mode in ("forward", "reverse", "phase"):
        builder = km.CircuitBuilder()
        sigma = [builder.create_quantum_register(12, f"sigma{i}") for i in range(36)]
        omega = [builder.create_quantum_register(12, f"omega{i}") for i in range(35)]
        masks = []
        if mode == "phase":
            masks = [builder.create_classical_register(12, f"E{i}") for i in range(4095)]
            modular_phase_block(builder, sigma, omega, masks, previous)
        else:
            transform_evaluator(builder, sigma, omega, previous, inverse=(mode == "reverse"))
        circuit = builder.finish_circuit()
        initial = remainders if mode == "reverse" else evaluators
        expected = remainders if mode == "forward" else evaluators
        shifts = np.arange(12, dtype=np.uint16)[:, None]
        phase_rng = np.random.default_rng(32)
        mask_values = phase_rng.integers(0, 4096, (len(masks), len(cases)), dtype=np.uint16)
        expected_phase = np.zeros(len(cases), dtype=bool)
        for j, values in enumerate(mask_values):
            point = field.pow(field.primitive_element, j)
            for k, locator in enumerate(locators):
                if previous.evaluate(locator, point) == 0:
                    denominator = field.mul(point, previous.evaluate(previous.derivative(locator), point))
                    error = field.div(previous.evaluate(evaluators[k], point), denominator)
                    expected_phase[k] ^= (error & int(values[k])).bit_count() % 2 != 0
        for seed in (32, 320, 3200):
            sim = km.Simulator(len(cases), debug_print=False, seed=seed)
            sim.use_same_registers_as(circuit)
            previous._write_words(sim, sigma, locators)
            previous._write_words(sim, omega, initial)
            for mask, values in zip(masks, mask_values):
                sim.write_across_shots(mask, ((values[None, :] >> shifts) & 1).astype(bool))
            sim.do(circuit)
            assert np.array_equal(previous._read_words(sim, sigma), np.asarray(locators).T), mode
            assert np.array_equal(previous._read_words(sim, omega), np.asarray(expected).T), mode
            previous._assert_clean_except(sim, circuit, sigma + omega)
            assert np.array_equal(sim.read_phase_flipped_across_shots(), expected_phase), mode
        reports.append({"mode": mode, "cases_per_seed": len(cases), "seeds": [32, 320, 3200],
                        "num_qubits": circuit.num_qubits,
                        "static_toffoli_like": circuit.operation_statistics().num_toffoli_like})
        del sim, circuit, builder
    return {"verification_level": "coherent phase-block component checks", "checks": reports}


def build_modular_reference(previous, config):
    """Keep the baseline decoder and replace its aligned Forney phase block."""
    base = previous.baseline_module()

    class ModularDecoder(base.ProosAndZalkaDecoder):
        def _chien_search_and_forney_mbuc(self, builder, reg_b, masks, nb, nB):
            self._pre_align_reg_b(builder, reg_b, nb, nB, is_adjoint=False)
            modular_phase_block(builder, reg_b[:36], list(reversed(reg_b[37:72])), masks, previous)
            self._pre_align_reg_b(builder, reg_b, nb, nB, is_adjoint=True)

    builder = km.CircuitBuilder()
    syndromes = [builder.create_quantum_register(12, f"S{i}") for i in range(config["n"])]
    masks = [builder.create_classical_register(12, f"E{i}") for i in range(config["m"])]
    ModularDecoder(config["n"], previous.FIELD).build_syndrome_decoding_mbuc(
        builder, syndromes=syndromes, error_mbuc=masks, n_iters=base.default_n_iters(config["n"]))
    return builder.finish_circuit()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--validate-phase-block", action="store_true")
    args = parser.parse_args()
    path = args.config.resolve()
    if path.parent != Path(__file__).resolve().parent / "configs" or path.suffix != ".json":
        parser.error("Select a JSON config from this experiment's configs directory")
    config = json.loads(path.read_text())
    if (config["m"], config["n"], config["degree"]) != (4095, 70, 12):
        parser.error("This probe requires the DQI benchmark dimensions")
    previous = load_dqi21()
    if config.get("layout") == "companion_modular_reference":
        if args.validate_phase_block:
            print(json.dumps(validate_modular_reference(previous), indent=2))
            return
        directory = Path(__file__).resolve().parent
        output = directory.parents[2] / "artifacts" / directory.parent.name / directory.name / (path.stem + ".kmb")
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            raise FileExistsError(output)
        temporary = output.with_suffix(".tmp.kmb")
        try:
            circuit = build_modular_reference(previous, config)
            stats = circuit.operation_statistics()
            circuit.to_file(str(temporary), format="kmb")
            temporary.rename(output)
        finally:
            temporary.unlink(missing_ok=True)
        print(json.dumps({"status": "BUILT", "artifact_path": str(output),
                          "num_qubits": circuit.num_qubits,
                          "static_toffoli_like": stats.num_toffoli_like,
                          "num_instructions": stats.num_instructions}, indent=2))
        return
    if config.get("layout") is not None or not args.validate_phase_block:
        parser.error("Select the reference build config or a screening config with --validate-phase-block")
    report = {"verification_level": "classical factorization and isolated circuit probes",
              "measurement_seeds": config["measurement_seeds"],
              "model": validate_model(previous, config),
              "packed_division": validate_division(previous, config)}
    report["sweep"] = validate_sweep(previous, config)
    report["screen"] = resource_screen(report["sweep"]["static_toffoli_like"])
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
