"""Tra bảng đa thức bậc hai cho phép áp pha 1/sqrt(x), không dùng Newton–Raphson.

Experiment: INV-41 (Issue #41); Owner: Reece1512.
Nguồn tham khảo: verifiers/invsqrt/nr_reference_circuit.py (Apache-2.0, xem src/LICENSE.txt)
cho hợp đồng phase-by-bits; phần số học là thiết kế mới của hướng này.

Mục tiêu
-------
Baseline tốn phần lớn Toffoli ở ba phép nhân rộng 28–30 bit của bước Newton. Hàm điểm là
Q × (Toffoli + T/4). Giả thuyết: một bảng 128 đoạn đủ dày để đa thức bậc hai đạt sai số
tương đối 2^-24, nên có thể bỏ hẳn Newton và chỉ còn hai phép nhân hẹp hơn.

Solution chi tiết
-----------------
1. Chuẩn hóa: năm tầng dịch nhị phân (16, 8, 4, 2, 1 bit). Tầng k đặt cờ S_k nếu 2^k bit
   cao của x bằng 0 rồi dịch trái 2^k bit. Kết quả x_norm = x << S có bit 21 bằng 1, tức
   M = x_norm / 2^21 thuộc [1, 2) và x = M 2^E với E = 21 - S.
2. Tra bảng: địa chỉ gồm a bit ngay dưới bit dẫn đầu cùng S_0 (quyết định E chẵn hay lẻ).
   Bảng trả (c0, c1, c2) của đa thức y = c0 - c1 t + c2 t^2 trên t thuộc [0, 1), với
   y xấp xỉ M^-1/2 khi E chẵn và M^-1/2 2^-1/2 khi E lẻ.
3. Tính giá trị: t là D = 21 - a bit thấp của x_norm.
   r1 = c1 - T(t c2), P = T(t r1), y = c0 - P. T(.) cắt từng hàng partial product dưới
   LSB của thanh ghi đích, được mô hình hóa đúng từng bit trong fixed_point_model.
4. Dịch kết quả: y1 = y << (S >> 1), bốn tầng cswap, nên y1 / 2^(wy + 10) xấp xỉ 1/sqrt(x).
5. Áp pha: một Z_POW mỗi bit của y1 (trừ bit trọng số 1 vòng), rồi uncompute đối xứng.

Khác biệt với baseline
---------------------
Bỏ _square, _multiply_m, _correct, _multiply_y0; chuẩn hóa nhị phân thay unary; bảng qua
init_lookup thay mạng Clifford bốn hệ số. Giữ cách áp pha theo bit.

Điều kiện đúng và sai số
----------------------
Miền x thuộc [1, 3.133.452]; x phục hồi; scratch về 0. Mọi trung gian được fixed_point_model
kiểm tra không tràn. Hệ số c0 từng đoạn được dịch một số nguyên để cân sai số về 0 trên chính
các x thuộc đoạn đó; đây là hằng trong bảng nên không tốn Toffoli. Sai số tuyệt đối
|y1 / 2^(wy+10) - 1/sqrt(x)| phải nhỏ hơn 2^-24 / sqrt(x), và phần dư được verifier dùng để
định giá tổng hợp phép quay.

Đánh đổi tài nguyên
------------------
Bảng dày hơn tốn thêm AND nhưng giảm độ rộng các phép nhân. Biên sai số hẹp làm phép quay đắt
hơn: mỗi phép quay tốn 0.56 log2(1/eps) + 5.3 T.

Cách chạy và kiểm tra
--------------------
python src/invsqrt/INV-41/solution.py --config src/invsqrt/INV-41/configs/base.json
python src/invsqrt/INV-41/validate_model.py --config src/invsqrt/INV-41/configs/base.json
python verifiers/invsqrt/verify_submission_invsqrt.py artifacts/invsqrt/INV-41/base.kmb

Theo dõi
--------
DESCRIPTION.md, ../EXPERIMENTS.md, ../SCORES.md và results/invsqrt/INV-41/.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
import re
from fractions import Fraction
from pathlib import Path

import kickmix as km
import numpy as np

WIDTH = 22
TOP = WIDTH - 1


@dataclasses.dataclass(frozen=True)
class Config:
    n_p: int
    address_bits: int  # a: bits of mantissa used to address the table.
    wy: int  # Fractional bits of c0 and y.
    wc1: int  # Fractional bits of c1 and r1.
    wc2: int  # Fractional bits of c2.
    d0: int  # Top bits of t used by t * r1.
    d1: int  # Top bits of t used by t * c2.
    phase_drop_bits: int = 0  # Lowest bits of y1 that receive no Z_POW.

    @property
    def t_bits(self) -> int:
        return TOP - self.address_bits

    @property
    def phase_bits(self) -> int:
        return self.wy + self.n_p


def _quadratic_through(nodes: list[float], values: list[float]) -> tuple[float, float, float]:
    """`(a0, a1, a2)` with `a0 + a1 t + a2 t^2` through three points, by divided differences."""
    (n0, n1, n2), (v0, v1, v2) = nodes, values
    d01 = (v1 - v0) / (n1 - n0)
    d12 = (v2 - v1) / (n2 - n1)
    a2 = (d12 - d01) / (n2 - n0)
    a1 = d01 - a2 * (n0 + n1)
    a0 = v0 - n0 * (a1 + a2 * n0)
    return a0, a1, a2


def base_table(cfg: Config) -> np.ndarray:
    """Rounded `(c0, c1, c2)` per entry, before the per-entry centring of `c0`."""
    a = cfg.address_bits
    nodes = [(1 - math.cos((2 * i + 1) * math.pi / 6)) / 2 for i in range(3)]
    rows = []
    for k in range(2 << a):
        odd_shift, m = k >> a, k & ((1 << a) - 1)
        factor = 1.0 if odd_shift else 2.0**-0.5  # S odd means E even.
        lo, w = 1 + m * 2.0**-a, 2.0**-a
        a0, a1, a2 = _quadratic_through(nodes, [factor / math.sqrt(lo + w * n) for n in nodes])
        rows.append((round(a0 * 2**cfg.wy), round(-a1 * 2**cfg.wc1), round(a2 * 2**cfg.wc2)))
    return np.array(rows, dtype=np.int64)


def _normalize_model(xs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    exponent = np.floor(np.log2(xs)).astype(np.int64)
    shift = TOP - exponent
    return shift, xs << shift


def _rows(t: np.ndarray, t_bits: int, count: int, value: np.ndarray, value_frac: int,
          out_frac: int) -> np.ndarray:
    """`T(t value)`, dropping each partial-product row below the output LSB."""
    total = np.zeros_like(value)
    for j in range(1, count + 1):
        bit = (t >> (t_bits - j)) & 1
        s = out_frac - value_frac - j
        total += bit * (value << s if s >= 0 else value >> -s)
    return total


def _evaluate(cfg: Config, table: np.ndarray, xs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """`(y1 masked to the phased bits, table index)` for each `x`."""
    a, d = cfg.address_bits, cfg.t_bits
    shift, x_norm = _normalize_model(xs)
    index = ((shift & 1) << a) | ((x_norm >> d) & ((1 << a) - 1))
    t = x_norm & ((1 << d) - 1)
    c0, c1, c2 = table[index, 0], table[index, 1], table[index, 2]
    r1 = c1 - _rows(t, d, cfg.d1, c2, cfg.wc2, cfg.wc1)
    if (r1 < 0).any():
        raise OverflowError('r1 went negative.')
    product = _rows(t, d, cfg.d0, r1, cfg.wc1, cfg.wy)
    y = c0 - product
    if (y < 0).any() or (y >= 1 << (cfg.wy + 1)).any():
        raise OverflowError('y does not fit its register.')
    y1 = y << (shift >> 1)
    drop = cfg.phase_drop_bits
    return (y1 >> drop) << drop, index


def coefficient_table(cfg: Config) -> list[tuple[int, int, int]]:
    """The final table: `c0` of each entry is shifted to centre the error over its inputs."""
    max_x = 3 * (2**cfg.n_p - 2)**2
    xs = np.arange(1, max_x + 1, dtype=np.int64)
    table = base_table(cfg)
    y1, index = _evaluate(cfg, table, xs)
    exact = 1 / np.sqrt(xs.astype(np.float64))
    error = (y1 / 2.0**cfg.phase_bits - exact) / exact
    n = len(table)
    low, high = np.full(n, np.inf), np.full(n, -np.inf)
    np.minimum.at(low, index, error)
    np.maximum.at(high, index, error)
    seen = np.isfinite(low)
    centre = np.where(seen, (low + high) / 2, 0.0)
    a = cfg.address_bits
    typical = np.array([(1.0 if k >> a else 2.0**-0.5) / math.sqrt(1 + (k & ((1 << a) - 1)) * 2.0**-a)
                        for k in range(n)])
    table[:, 0] -= np.round(centre * typical * 2.0**cfg.wy).astype(np.int64)
    return [tuple(int(v) for v in row) for row in table]


def fixed_point_model(cfg: Config, table: list[tuple[int, int, int]], xs: np.ndarray) -> np.ndarray:
    """The integer whose bits receive `Z_POW`, in units of `2^-phase_bits` turns."""
    return _evaluate(cfg, np.array(table, dtype=np.int64), np.asarray(xs, dtype=np.int64))[0]


def error_ratio(cfg: Config, table: list[tuple[int, int, int]], xs: np.ndarray) -> np.ndarray:
    """`|phase error| / tolerance`, with tolerance `2^-24 / sqrt(x)`."""
    exact = 1 / np.sqrt(xs.astype(np.float64))
    approx = fixed_point_model(cfg, table, xs) / 2.0**cfg.phase_bits
    return np.abs(approx - exact) / (exact * 2.0**-24)


# Circuit construction. Each stage takes `inverse` and emits its own uncomputation.


def _flag_zero_top(builder: km.CircuitBuilder, x: km.array, count: int, flag: km.q) -> None:
    """`flag ^= top count bits of x are all zero`."""
    top = x[len(x) - count:]
    builder.x(top)
    builder.multi_controlled_x(top, flag)
    builder.x(top)


def _shift_left(builder: km.CircuitBuilder, inverse: bool, control: km.q, register: km.array,
                amount: int, live: int) -> None:
    """`if control: register <<= amount`, moving only the `live` lowest bits."""
    order = range(live) if inverse else reversed(range(live))
    for i in order:
        builder.cswap(control, register[i], register[i + amount])


def _normalize(builder: km.CircuitBuilder, inverse: bool, x: km.array, flags: km.array) -> None:
    stages = [4, 3, 2, 1, 0]
    for k in (reversed(stages) if inverse else stages):
        amount = 1 << k
        if inverse:
            _shift_left(builder, True, flags[k], x, amount, WIDTH - amount)
            _flag_zero_top(builder, x, amount, flags[k])
        else:
            _flag_zero_top(builder, x, amount, flags[k])
            _shift_left(builder, False, flags[k], x, amount, WIDTH - amount)


def _pack(entry: tuple[int, int, int], widths: tuple[int, int, int]) -> int:
    return entry[0] | (entry[1] << widths[0]) | (entry[2] << (widths[0] + widths[1]))


def _add_row(builder: km.CircuitBuilder, inverse: bool, control: km.q, terms: list[tuple[km.q, int]],
             target: km.array, scratch: km.array, subtract: bool, top: int | None = None) -> None:
    """`target += control * sum(2^index source)`, optionally touching only bits below `top`."""
    if not terms:
        return
    top = len(target) if top is None else top
    sources = km.array([q for q, _ in terms])
    products = km.array([scratch[i] for _, i in terms])
    low = min(i for _, i in terms)
    builder.init_and(control, sources, products)
    if subtract != inverse:
        builder.isub(scratch[low:top], target=target[low:top])
    else:
        builder.iadd(scratch[low:top], target=target[low:top])
    builder.del_and(control, sources, products)


def _reduce_c1(builder: km.CircuitBuilder, inverse: bool, cfg: Config, x: km.array, c2: km.array,
               c1: km.array, scratch: km.array) -> None:
    """`c1 -= T(t c2)`."""
    d = cfg.t_bits
    rows = list(range(1, cfg.d1 + 1))
    for j in (reversed(rows) if inverse else rows):
        s = cfg.wc1 - cfg.wc2 - j
        terms = [(c2[i], i + s) for i in range(max(0, -s), len(c2)) if i + s < len(c1)]
        _add_row(builder, inverse, x[d - j], terms, c1, scratch, subtract=True)


def _multiply(builder: km.CircuitBuilder, inverse: bool, cfg: Config, x: km.array, r1: km.array,
              product: km.array, scratch: km.array) -> None:
    """`product := T(t r1)`. Low rows go first so that each row carries through fewer bits."""
    d = cfg.t_bits
    rows = list(range(cfg.d0, 0, -1))
    for j in (reversed(rows) if inverse else rows):
        s = cfg.wy - cfg.wc1 - j
        terms = [(r1[i], i + s) for i in range(max(0, -s), len(r1)) if i + s < len(product)]
        top = min(len(product), len(r1) + s + 1)
        _add_row(builder, inverse, x[d - j], terms, product, scratch, subtract=False, top=top)


def _denormalize(builder: km.CircuitBuilder, inverse: bool, flags: km.array, y1: km.array,
                 y_width: int) -> None:
    """`y1 <<= S >> 1`. S <= 21 makes the two largest stages mutually exclusive."""
    live = {0: y_width, 1: y_width + 1, 2: y_width + 3, 3: y_width + 2}
    stages = [0, 1, 2, 3]
    for k in (reversed(stages) if inverse else stages):
        _shift_left(builder, inverse, flags[k + 1], y1, 1 << k, live[k])


def _phase(builder: km.CircuitBuilder, cfg: Config, y1: km.array) -> None:
    f = cfg.phase_bits
    with builder.mark('phase_by_bits'):
        for j in range(cfg.phase_drop_bits, f):
            builder.z_pow(y1[j], Fraction(2) ** (j - f + 1))


def build_circuit(cfg: Config, table: list[tuple[int, int, int]]) -> km.Circuit:
    a = cfg.address_bits
    widths = (cfg.wy + 1,
              max(int(row[1]).bit_length() for row in table),
              max(int(row[2]).bit_length() for row in table))
    packed = [_pack(row, widths) for row in table]
    product_width = widths[1] + max(cfg.wy - cfg.wc1, 0) + 1
    scratch_width = max(widths[1], product_width)
    pad = widths[0] - product_width

    builder = km.CircuitBuilder()
    x = builder.create_quantum_register(WIDTH, name='x')
    flags = builder.alloc_qubits(5)
    y, c1, c2 = (builder.alloc_qubits(w) for w in widths)
    target = km.array([*y, *c1, *c2])
    address = km.array([*x[TOP - a:TOP], flags[0]])

    with builder.mark('normalize'):
        _normalize(builder, False, x, flags)
    with builder.mark('lookup'):
        builder.init_lookup(table=packed, address=address, target=target)
    scratch = builder.alloc_qubits(scratch_width)
    with builder.mark('reduce_c1'):
        _reduce_c1(builder, False, cfg, x, c2, c1, scratch)
    product = builder.alloc_qubits(product_width)
    with builder.mark('multiply'):
        _multiply(builder, False, cfg, x, c1, product, scratch)
    with builder.mark('subtract'):
        builder.isub(km.array([*product, *scratch[:pad]]), target=y)
    builder.free(scratch)
    high = builder.alloc_qubits(cfg.n_p)
    y1 = km.array([*y, *high])
    with builder.mark('denormalize'):
        _denormalize(builder, False, flags, y1, widths[0])

    _phase(builder, cfg, y1)

    with builder.mark('denormalize'):
        _denormalize(builder, True, flags, y1, widths[0])
    builder.free(high)
    scratch = builder.alloc_qubits(scratch_width)
    with builder.mark('subtract'):
        builder.iadd(km.array([*product, *scratch[:pad]]), target=y)
    with builder.mark('multiply'):
        _multiply(builder, True, cfg, x, c1, product, scratch)
    builder.free(product)
    with builder.mark('reduce_c1'):
        _reduce_c1(builder, True, cfg, x, c2, c1, scratch)
    builder.free(scratch)
    with builder.mark('lookup'):
        builder.del_lookup(table=packed, address=address, target=target)
    with builder.mark('normalize'):
        _normalize(builder, True, x, flags)
    for register in (y, c1, c2, flags):
        builder.free(register)
    return builder.finish_circuit()


def load_config(path: Path) -> Config:
    experiment_dir = Path(__file__).resolve().parent
    resolved = path.resolve()
    if resolved.parent != (experiment_dir / 'configs').resolve() or resolved.suffix != '.json':
        raise ValueError('Config must be a JSON file directly inside this experiment configs/ directory')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', resolved.stem):
        raise ValueError('Config name must contain only letters, digits, hyphens or underscores')
    return Config(**json.loads(resolved.read_text(encoding='utf-8')))


def main() -> None:
    experiment_dir = Path(__file__).resolve().parent
    track, experiment_id, root = experiment_dir.parent.name, experiment_dir.name, experiment_dir.parents[2]
    if experiment_dir.parent.parent.name != 'src' or track not in {'invsqrt', 'dqi', 'dfthcsos'}:
        raise ValueError('solution.py must be located at src/<TRACK>/<ID>/solution.py')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=experiment_dir / 'configs/base.json')
    parser.add_argument('--output', type=Path, help='Optional output path; filename must match config stem')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing generated artifact')
    args = parser.parse_args()
    cfg = load_config(args.config)
    output = args.output or root / 'artifacts' / track / experiment_id / f'{args.config.stem}.kmb'
    if output.name != args.config.stem + '.kmb':
        raise ValueError('Output filename must be <config-name>.kmb')
    if output.exists() and not args.overwrite:
        raise FileExistsError(f'{output} exists; pass --overwrite to rebuild')
    output.parent.mkdir(parents=True, exist_ok=True)
    max_x = 3 * (2**cfg.n_p - 2)**2
    xs = np.arange(1, max_x + 1, dtype=np.int64)
    table = coefficient_table(cfg)
    ratio = error_ratio(cfg, table, xs)
    print(f'Model: max error/tolerance {ratio.max():.6f} at x={int(ratio.argmax()) + 1}')
    circuit = build_circuit(cfg, table)
    circuit.to_file(str(output), format='kmb')
    print(f'Wrote {output}: {circuit.operation_statistics().num_toffoli_like:,} Toffolis, '
          f'{circuit.num_qubits} qubits.')


if __name__ == '__main__':
    main()
