"""Kiểm tra độc lập INV-49: mô hình toàn miền và mạch khớp mô hình; không phải bộ chấm.

Mục tiêu: xác nhận fixed_point_model không tràn và có sai số dưới ngưỡng trên toàn bộ
x = 1..3.133.452, rồi xác nhận mạch thật cho đúng pha của mô hình, phục hồi x và làm sạch
scratch trên các đầu vào biên và ngẫu nhiên với nhiều seed đo.

Solution chi tiết: chạy mô hình theo từng khối x; so với chính cấu hình đó khi bỏ bước cân
c0 từng đoạn để thấy tác dụng của bước cân. Simulation dùng mọi mép trong 128 đoạn trên mọi
số mũ, các lũy thừa của hai, biên miền và mẫu ngẫu nhiên có seed cố định.

Điều kiện đúng và sai số: dừng với lỗi nếu sai số xấu nhất từ 0,95 lần dung sai trở lên,
hoặc nếu pha, x, scratch không khớp. Script không tạo trạng thái PASS hay điểm verifier.

Cách chạy từ thư mục gốc:
python src/invsqrt/INV-49/validate_model.py --config src/invsqrt/INV-49/configs/base.json --output artifacts/invsqrt/INV-49/base_model_validation.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import kickmix as km
import numpy as np

MAX_X = 3_133_452
LIMIT = 0.95
SEEDS = (17, 982451653, 20261108)


def load_solution(path: Path):
    spec = importlib.util.spec_from_file_location('inv49_validation_solution', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def bits(xs: np.ndarray, width: int) -> np.ndarray:
    return (xs[None, :] >> np.arange(width, dtype=np.uint64)[:, None]) & 1 == 1


def values(bs: np.ndarray) -> np.ndarray:
    return (bs.astype(np.uint64) << np.arange(len(bs), dtype=np.uint64)[:, None]).sum(axis=0)


def summarize(y1: np.ndarray, xs: np.ndarray, phase_bits: int) -> dict:
    exact = 1 / np.sqrt(xs.astype(np.float64))
    signed = (y1 / 2.0**phase_bits - exact) / (exact * 2.0**-24)
    worst = int(np.abs(signed).argmax())
    return {'min_signed_ratio': float(signed.min()), 'max_signed_ratio': float(signed.max()),
            'worst_ratio': float(abs(signed[worst])), 'worst_x': int(xs[worst]), 'overflow': False}


def boundary_inputs(address_bits: int, rng: np.random.Generator) -> np.ndarray:
    points = {1, 2, 3, MAX_X - 1, MAX_X}
    for exponent in range(22):
        for segment in range(1 << address_bits):
            edge = math.ceil(2**exponent * (1 + segment / (1 << address_bits)))
            points.update(v for v in (edge - 1, edge, edge + 1) if 1 <= v <= MAX_X)
    points.update(int(v) for v in rng.integers(1, MAX_X + 1, 256))
    return np.array(sorted(points), dtype=np.uint64)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sample-seed', type=int, default=20261109)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    solution = load_solution(here / 'solution.py')
    cfg = solution.load_config(args.config)
    table = solution.coefficient_table(cfg)

    xs = np.arange(1, MAX_X + 1, dtype=np.int64)
    report = {'kind': 'local_model_and_simulation_checks', 'not_verifier_result': True,
              'config_name': args.config.stem, 'exhaustive_domain': [1, MAX_X], 'model': {}}
    report['model'][args.config.stem] = summarize(
        solution.fixed_point_model(cfg, table, xs), xs, cfg.phase_bits)
    uncentred = [tuple(int(v) for v in row) for row in solution.base_table(cfg)]
    report['model']['no_c0_centring'] = summarize(
        solution.fixed_point_model(cfg, uncentred, xs), xs, cfg.phase_bits)
    print(json.dumps(report['model'], indent=2), flush=True)
    if report['model'][args.config.stem]['worst_ratio'] >= LIMIT:
        raise SystemExit(f'worst error ratio is not below {LIMIT}')

    inputs = boundary_inputs(cfg.address_bits, np.random.default_rng(args.sample_seed))
    expected = solution.fixed_point_model(cfg, table, inputs.astype(np.int64))
    circuit = solution.build_circuit(cfg, table)
    x = km.array(circuit.register_data['x'])
    used = set(x)
    scratch = km.array([km.q(i) for i in range(circuit.num_qubits) if km.q(i) not in used])
    for seed in SEEDS:
        sim = km.Simulator(batch_size=len(inputs), seed=seed)
        sim.write_across_shots(x, bits(inputs, 22))
        sim.do(circuit)
        if not np.array_equal(values(sim.read_across_shots(x)), inputs):
            raise SystemExit(f'x was not restored (seed {seed})')
        if sim.read_across_shots(scratch).any():
            raise SystemExit(f'scratch is not clean (seed {seed})')
        for i, y in enumerate(expected):
            turns = sim.read_shot_phase(i) / 2 - km_fraction(int(y), cfg.phase_bits)
            if turns % 1 != 0:
                raise SystemExit(f'phase differs from model at x={int(inputs[i])} (seed {seed})')
    report['simulation'] = {
        'inputs': int(len(inputs)), 'rng_seed': args.sample_seed, 'measurement_seeds': list(SEEDS),
        'phase_matches_model': True, 'x_restored': True, 'scratch_zero': True,
        'num_qubits': circuit.num_qubits,
        'static_toffoli': int(circuit.operation_statistics().num_toffoli_like)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report['simulation']), flush=True)


def km_fraction(numerator: int, bits_count: int):
    from fractions import Fraction
    return Fraction(numerator, 2**bits_count)


if __name__ == '__main__':
    main()
