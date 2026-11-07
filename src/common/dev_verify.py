"""Development comparison profile; never an official full verification.

Solution: reuse unchanged organizer verification functions. Invsqrt selects a
fixed, circuit-independent set across the full input domain, including neighbors
of normalization/polynomial boundaries, and repeats measurement branches. A local
ProblemSpec subclass and temporary sample_shots replacement restrict simulation
to these inputs; original phase, register, cleanup and cost checks remain intact.
DQI retains its full problem size/distribution with fewer shots and an explicit
shared seed. DFTHC retains all addresses and Hamiltonian metrics but uses fewer
measurement repetitions. All outputs carry development-only labels and sample
configuration. Sampled scores can differ from full, especially invsqrt's worst
phase margin and DQI's sample-dependent confidence penalty.

Usage: python src/common/dev_verify.py --track invsqrt --submission artifacts/invsqrt/INV-BASELINE/baseline.kmb
Five minutes is a tuning target, not a bound; the notebook enforces a wall timeout
without treating an interrupted run as PASS. No candidate-specific fixed-point
model is assumed. Code/model equivalence must be tested by each experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'verifiers'))


def invsqrt_inputs(max_x: int, count: int, seed: int) -> np.ndarray:
    """Exactly count unique inputs, including both sides of scaling boundaries."""
    if not 2048 <= count <= max_x:
        raise ValueError('invsqrt sample count must lie in [2048, max_x]')
    edges = {1, max_x}
    for exponent in range(0, 23, 2):
        for numerator, denominator in [(1, 1), (3, 2), (2, 1), (3, 1)]:
            boundary = numerator * (1 << exponent) // denominator
            edges.update(x for x in range(boundary - 2, boundary + 3) if 1 <= x <= max_x)
    edges.update(range(1, 257))
    edges.update(range(max_x - 255, max_x + 1))
    edges.update(np.linspace(1, max_x, 512, dtype=np.int64).tolist())
    edges.update(np.geomspace(1, max_x, 256).astype(np.int64).tolist())
    rng = np.random.default_rng(seed)
    while len(edges) < count:
        # Stop at the exact count; sorted output has deterministic hashing.
        for x in rng.integers(1, max_x + 1, size=count - len(edges)):
            edges.add(int(x))
    if len(edges) > count:
        raise ValueError('sample count is smaller than mandatory boundary set')
    return np.array(sorted(edges), dtype=np.uint64)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--track', choices=['invsqrt', 'dqi', 'dfthcsos'], required=True)
    parser.add_argument('--submission', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=20261106)
    parser.add_argument('--invsqrt-samples', type=int, default=4096)
    parser.add_argument('--invsqrt-repeats', type=int, default=2)
    parser.add_argument('--dqi-shots', type=int, default=4096)
    parser.add_argument('--dfthc-repeats', type=int, default=4)
    args = parser.parse_args()
    started = time.monotonic()
    profile = vars(args).copy()
    profile['submission'] = str(args.submission)
    report = {'verification_level': 'dev_5min', 'official_score': False,
              'profile_version': 1, 'profile': profile}
    try:
        import kickmix as km
        if args.track == 'invsqrt':
            from invsqrt import verify_submission_invsqrt as verifier
            xs = invsqrt_inputs(3133452, args.invsqrt_samples, args.seed)
            if args.invsqrt_repeats < 1 or len(xs) * args.invsqrt_repeats % 256:
                raise ValueError('positive repeats and sample_count * repeats divisible by 256 required')

            class SampledSpec(verifier.ProblemSpecInvSqrt):
                @property
                def num_shots(self):
                    return len(xs) * self.shots_per_x

            spec = SampledSpec(width=22, max_x=3133452, beta=verifier.Fraction(1),
                               precision_bits=24, shots_per_x=args.invsqrt_repeats,
                               system_qubits=6540)
            original_sampler = verifier.sample_shots
            verifier.sample_shots = lambda spec, start, stop: xs[np.arange(start, stop) % len(xs)]
            try:
                result = verifier.verify(km.Circuit.from_file(str(args.submission), format='kmb'),
                                         spec, seed=args.seed, batch_size=256, max_workers=1)
            finally:
                verifier.sample_shots = original_sampler
            report.update(input_count=len(xs), input_min=int(xs.min()), input_max=int(xs.max()),
                          input_sha256=hashlib.sha256(xs.astype('<u8').tobytes()).hexdigest())
        elif args.track == 'dqi':
            from dqi import verify_submission_dqi as verifier
            if args.dqi_shots < 2048 or args.dqi_shots % 256:
                raise ValueError('DQI shots must be >=2048 and divisible by 256')
            spec = verifier.ProblemSpecDQI.benchmark_instance(num_shots=args.dqi_shots)
            result = verifier.verify(km.Circuit.from_file(str(args.submission), format='kmb'),
                                     spec, seed=args.seed, max_workers=1)
            report['resource_proxy_q2t'] = result['num_qubits'] ** 2 * result['toffoli_count']
        else:
            from dfthcsos.verify import verify
            if args.dfthc_repeats < 1:
                raise ValueError('DFTHC repeats must be positive')
            result = verify(str(args.submission), shots_per_address=args.dfthc_repeats,
                            seed=args.seed)
        report.update(result)
    except Exception as exc:
        report.update(status='FAIL', error=f'{type(exc).__name__}: {exc}')
    report['elapsed_seconds'] = time.monotonic() - started
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
