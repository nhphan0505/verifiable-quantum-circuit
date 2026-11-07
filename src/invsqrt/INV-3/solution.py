"""Triển khai cấp phát thanh ghi theo giai đoạn và uncompute sớm cho invsqrt.

Experiment: INV-3; Issue: https://github.com/nhphan0505/verifiable-quantum-circuit/issues/3; Owner: nhphan0505.
Nguồn tham khảo / code kế thừa và giấy phép:
Kế thừa cấu trúc số học và bảng hệ số từ src/invsqrt/INV-BASELINE/solution.py
(commit 13ec200455ab4aea1afc8df0bcab493cd269075e, SHA-256 fddc7ecc89a67a4a897a5bf509c902805383b31c94964221f8ae70c2f695cfad),
dựa trên verifiers/invsqrt/nr_reference_circuit.py của ban tổ chức (arXiv:2308.12352).
Giấy phép Apache-2.0, xem src/LICENSE.txt.

Mục tiêu
-------
Nút thắt baseline: Baseline INV-BASELINE cấp phát tĩnh toàn bộ 10 thanh ghi (231 qubit)
ngay từ đầu mạch và giữ sống đến tận cuối mạch, khiến đỉnh qubit đạt Q = 260 qubit tại
bước _multiply_y0 do cộng thêm 29 qubit ancilla mượn tạm thời từ bộ cộng iadd/isub.
Hàm điểm của benchmark là score = Q * (Toffoli + T/4) cho một lần gọi mạch độc lập
(không tính system_qubits vào Q theo verifier). Do đó, giữ thanh ghi nhàn rỗi làm tăng Q
trực tiếp, gây bất lợi đáng kể cho hàm điểm.
Giả thuyết:
(a) Uncompute sớm thanh ghi hệ số bậc ba c3 (17 qubit) ngay sau bước 1 của _horner bằng
    mạng cổng Clifford gf2_iadd (0 Toffoli) và giải phóng c3 trước khi cấp phát các
    thanh ghi của giai đoạn Newton.
(b) Trì hoãn cấp phát p (30 qubit) đến ngay trước _multiply_y0, và giải phóng scratch
    (30 qubit) ngay sau _multiply_y0 trước khi cấp phát 10 qubit mở rộng y1_hi cho _denormalize.
Kết quả dự kiến: Giảm đỉnh qubit Q từ 260 xuống 232 qubit (-28 qubit, giảm 10.77%)
mà hoàn toàn không tăng thêm bất kỳ cổng Toffoli hay T nào (Delta C = 0), đồng thời bảo toàn
từng bit kết quả số học (Delta error = 0), giúp score giảm tỉ lệ thuận ~10.7%.

Solution chi tiết
-----------------
1. Chuẩn hóa: Đếm cặp bit 0 đầu của x vào unary register flags (10 qubit) và xoay trái x
   để M thuộc [1, 4).
2. Chọn khoảng: selectors (3 qubit) xác định một trong bốn khoảng đa thức bậc ba.
3. Nạp và đánh giá Horner:
   - Cấp phát c0, c1, c2, c3 (mỗi thanh ghi 17 qubit) và scratch (30 qubit).
   - Nạp hệ số vào c0..c3 bằng mạng Clifford gf2_iadd.
   - Bước 1 Horner: c2 -= T(c3 * delta). c3 chỉ đóng vai trò số nhân và không bị ghi đè.
   - Uncompute sớm c3: Gọi lại _xor_coefficient cho c3 bằng gf2_iadd đưa c3 về |0>,
     rồi gọi builder.free(c3) ngay lập tức (giải phóng 17 qubit với 0 Toffoli).
   - Bước 2 & 3 Horner: c1 -= T(c2 * delta) và c0 -= T(c1 * delta), thu được y0 trong c0.
4. Bình phương Newton: Cấp phát square (28 qubit), tính square := T(y0^2).
5. Nhân M: Cấp phát z (30 qubit), tính z := T(M * square).
   Tùy chọn pebbling: Có thể uncompute và free(square) sớm nếu bật early_uncompute_square.
6. Hiệu chỉnh: z := 3 - z.
7. Nhân y0: Cấp phát p (30 qubit), tính p := T(y0 * z) = T(y0 * (3 - M * y0^2)).
8. Tách vòng đời scratch và mở rộng y1:
   - Toàn bộ scratch (30 qubit) đã ở trạng thái |0> vì _add_row luôn kết thúc bằng del_and.
   - Gọi builder.free(scratch) giải phóng 30 qubit về pool.
   - Cấp phát y1_hi (10 qubit), ghép y1 = [p, y1_hi] (40 qubit).
   - Chạy _denormalize xoay trái y1 theo flags.
9. Áp pha: _phase_by_bits áp 40 cổng Z_POW lên y1.
10. Uncomputation: Đảo ngược đối xứng gương toàn bộ các bước, hoàn trả mọi ancilla về |0>
    và khôi phục x nguyên vẹn.

Khác biệt với baseline
---------------------
- Baseline: Cấp phát tất cả thanh ghi (x, y1, flags, selectors, c0..c3, square, z, scratch)
  từ đầu hàm build_nr_circuit và free ở cuối hàm.
- INV-3: Cấp phát theo giai đoạn (staged allocation), uncompute sớm c3 bằng Clifford,
  trì hoãn cấp phát p, và giải phóng scratch trước khi mở rộng y1.
- Toàn bộ tham số số học (delta_bits=14, coef_bits=17, square_bits=28, product_bits=28,
  result_bits=29), bảng hệ số và toán tử số học giữ nguyên 100% so với baseline.

Điều kiện đúng và sai số
----------------------
- Miền đầu vào: x nguyên từ 1 đến 3.133.452 (width = 22 qubit).
- Invariants: Mọi thanh ghi được truyền vào builder.free() bắt buộc phải ở trạng thái |0>
  trên mọi nhánh kết quả đo của cổng del_and (HMR).
  + c3 sau khi nạp và gọi lại _xor_coefficient trở về đúng |0^17>.
  + scratch sau mỗi bước _add_row đều trở về |0^30>.
  + y1_hi sau khi uncompute _denormalize trở về |0^10>.
  + x và scratch được phục hồi hoàn toàn về trạng thái ban đầu.
- Sai số số học: Vì các phép toán số học thực thi giống hệt baseline, fixed_point_model
  và relative_error cho kết quả trùng khớp từng bit với baseline trên toàn bộ miền x.
  worst_error_over_tolerance trên dev_5min giữ nguyên 0.3783938... (x = 3010856).

Đánh đổi tài nguyên
------------------
- Số qubit cực đại Q: Giảm từ 260 xuống 232 (-28 qubit, giảm 10.77%) ở staged_alloc và xuống 204 (-56 qubit, giảm 21.54%) ở pebble_square.
- Toffoli: Giữ nguyên 7735.0 (0 Toffoli phụ trội) ở staged_alloc; tăng lên 8619.0 (+884 Toffoli, +11.43%) ở pebble_square.
- Phép quay Z_POW và T: Giữ nguyên 37 phép quay và 1 cổng T.
- Tích Q * C trên dev_5min:
  + staged_alloc: đạt 1.852.826 (cải thiện 1.1207x, tức 1.12x).
  + pebble_square: đạt 1.809.545 (cải thiện 1.1475x, tức 1.15x).

Cách chạy và kiểm tra
--------------------
Từ thư mục gốc dự án:
python src/invsqrt/INV-3/solution.py --config src/invsqrt/INV-3/configs/staged_alloc.json
Kiểm tra verifier smoke:
python verifiers/invsqrt/verify_submission_invsqrt.py artifacts/invsqrt/INV-3/staged_alloc.kmb --max-x 256 --shots-per-x 1 --batch-size 256

Theo dõi
--------
Mô tả chi tiết: src/invsqrt/INV-3/DESCRIPTION.md;
Mục lục: src/invsqrt/EXPERIMENTS.md;
Bảng điểm: src/invsqrt/SCORES.md;
Kết quả: results/invsqrt/INV-3/.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
from fractions import Fraction
from pathlib import Path

import kickmix as km
import numpy as np

# Bảng hệ số đa thức bậc ba kế thừa từ baseline (arXiv:2308.12352).
POLY_A = (0.99994132489119882162, 0.49609891915903542303, 0.33261112772430493331, 0.14876762006038398086)
POLY_B = (0.81648515205385221995, 0.27136515484240234115, 0.12756148214815175348, 0.044753028579153842218)


@dataclasses.dataclass(frozen=True)
class Precision:
    """Độ rộng bit fixed-point của các thanh ghi trong pipeline."""
    delta_bits: int = 14
    coef_bits: int = 17
    square_bits: int = 28
    product_bits: int = 28
    result_bits: int = 29

    def coefficient_table(self) -> list[list[int]]:
        cases = [POLY_A, POLY_B,
                 [a / (2**j * math.sqrt(2)) for j, a in enumerate(POLY_A)],
                 [b / (2**j * math.sqrt(2)) for j, b in enumerate(POLY_B)]]
        return [[round(c * 2**self.coef_bits) for c in case] for case in cases]

    def output_bits(self, n_p: int) -> int:
        return self.result_bits + n_p + 1


@dataclasses.dataclass(frozen=True)
class ScheduleConfig:
    """Cấu hình lịch trình cấp phát và uncompute sớm thanh ghi."""
    early_uncompute_c3: bool = True
    staged_y1_scratch: bool = True
    early_uncompute_square: bool = False


# Mô hình số học cổ điển để đối chiếu sai số.


def fixed_point_model(n_p: int, prec: Precision, xs: np.ndarray) -> np.ndarray:
    """Tính y1 theo mô hình fixed-point số học cho mỗi x trong xs."""
    width, d, wc, wsq, wz, wp = 2 * n_p + 2, *dataclasses.astuple(prec)
    xs = np.asarray(xs, dtype=np.int64)
    if not ((1 <= xs) & (xs < 2**width)).all():
        raise ValueError('x must lie in [1, 2^(width - 1)).')

    def bit(v: np.ndarray, i: int) -> np.ndarray:
        return (v >> i) & 1

    def product(rows: list[tuple[np.ndarray, int]], operand: np.ndarray, out_bits: int,
                operand_bits: int, limit: int) -> np.ndarray:
        acc = np.zeros_like(xs)
        for ctl, weight in rows:
            e = out_bits - operand_bits + weight
            acc += ctl * (operand << e if e >= 0 else operand >> -e)
        if (acc >= 2**limit).any():
            raise OverflowError('Intermediate register overflow.')
        return acc

    s = (width - (np.floor(np.log2(xs)).astype(np.int64) + 1)) // 2
    x_norm = xs << (2 * s)
    top, second, third = bit(x_norm, width - 1), bit(x_norm, width - 2), bit(x_norm, width - 3)

    table = np.array(prec.coefficient_table(), dtype=np.int64)
    c0, c1, c2, c3 = (table[np.where(top == 0, third, 2 + second), j] for j in range(4))
    delta = [(top & third, -1)] + [(bit(x_norm, width - 2 - m), -m) for m in range(2, min(d, width - 2) + 1)]
    y0, mult = c0, c3
    for acc in (c2, c1, c0):
        y0 = mult = acc - product(delta, mult, wc, wc, wc)
        if ((y0 <= 0) | (y0 >= 2**wc)).any():
            raise OverflowError('Horner intermediate does not fit its register.')

    y = {k: bit(y0, wc - k) for k in range(1, wc + 1)}
    square = np.zeros_like(xs)
    for k in range(1, wc + 1):
        if 2 * k <= wsq:
            square += y[k] << (wsq - 2 * k)
        for l in range(k + 1, wc + 1):
            if k + l - 1 <= wsq:
                square += (y[k] & y[l]) << (wsq - (k + l - 1))
    m_rows = [(bit(x_norm, i), i - width + 2) for i in range(width)]
    z = product(m_rows, square, wz, wsq, wz + 2)
    correction = (3 << wz) - z
    p = product([(y[k], -k) for k in range(1, wc + 1)], correction, wp, wz, wp + 1)
    return p << s


def relative_error(n_p: int, prec: Precision, xs: np.ndarray) -> np.ndarray:
    """Sai số tương đối so với hàm lý thuyết 1 / sqrt(x)."""
    exact = 1 / np.sqrt(np.asarray(xs, dtype=np.float64))
    approx = fixed_point_model(n_p, prec, xs) / 2.0**prec.output_bits(n_p)
    return np.abs(approx - exact) / exact


# Các khối xây dựng mạch lượng tử.


def _and(builder: km.CircuitBuilder, inverse: bool, control1: km.q | km.array,
         control2: km.q | km.array, target: km.q | km.array) -> None:
    if inverse:
        builder.del_and(control1, control2, target)
    else:
        builder.init_and(control1, control2, target)


def _add_row(builder: km.CircuitBuilder, inverse: bool, control: km.q,
             terms: list[tuple[km.q, int]], target: km.array, scratch: km.array,
             subtract: bool = False) -> None:
    """target += control * sum(2^index source) cho (source, index) trong terms."""
    sources = km.array([q for q, _ in terms])
    products = km.array([scratch[i] for _, i in terms])
    low = min(i for _, i in terms)
    builder.init_and(control, sources, products)
    if subtract != inverse:
        builder.isub(scratch[low:len(target)], target=target[low:])
    else:
        builder.iadd(scratch[low:len(target)], target=target[low:])
    builder.del_and(control, sources, products)


def _flag_zero_pair(builder: km.CircuitBuilder, inverse: bool, x: km.array, flag: km.q) -> None:
    top_pair = x[-2:]
    builder.x(top_pair)
    _and(builder, inverse, top_pair[0], top_pair[1], flag)
    builder.x(top_pair)


def _normalize(builder: km.CircuitBuilder, inverse: bool, x: km.array, flags: km.array) -> None:
    for k in (reversed(range(len(flags))) if inverse else range(len(flags))):
        lanes = (x[2 * k::2], x[2 * k + 1::2])
        if inverse:
            for lane in lanes:
                builder.right_rotate(lane, 1, control=flags[k])
            _flag_zero_pair(builder, inverse, x, flags[k])
        else:
            _flag_zero_pair(builder, inverse, x, flags[k])
            for lane in lanes:
                builder.left_rotate(lane, 1, control=flags[k])


def _select_interval(builder: km.CircuitBuilder, inverse: bool, x: km.array, selectors: km.array) -> None:
    width = len(x)
    top, second, third = x[width - 1], x[width - 2], x[width - 3]
    builder.x(top)
    _and(builder, inverse, top, third, selectors[0])
    builder.x(top)
    _and(builder, inverse, top, km.array([second, third]), selectors[1:])


def _xor_coefficient(builder: km.CircuitBuilder, prec: Precision, x: km.array,
                     selectors: km.array, j: int, reg: km.array) -> None:
    """XOR hệ số bậc j vào thanh ghi reg bằng cổng Clifford (tự nghịch đảo, 0 Toffoli)."""
    top, t_a, t_b = x[len(x) - 1], selectors[0], selectors[1]
    table = prec.coefficient_table()
    for control, value in ((True, table[0][j]), (top, table[0][j] ^ table[2][j]),
                           (t_a, table[0][j] ^ table[1][j]), (t_b, table[2][j] ^ table[3][j])):
        builder.gf2_iadd(value, target=reg, control=control)


def _horner_step(builder: km.CircuitBuilder, inverse: bool, prec: Precision, x: km.array,
                 selectors: km.array, acc: km.array, mult: km.array, scratch: km.array) -> None:
    """Một bước đánh giá Horner: acc -= T(mult * delta)."""
    width, wc = len(x), len(acc)
    delta = [(selectors[2], 1)]
    delta += [(x[width - 2 - m], m) for m in range(2, min(prec.delta_bits, width - 2) + 1)]
    with builder.mark('horner_step'):
        for control, m in delta:
            _add_row(builder, inverse, control, [(mult[i], i - m) for i in range(m, wc)], acc,
                     scratch, subtract=True)


def _square(builder: km.CircuitBuilder, inverse: bool, y0: km.array, square: km.array,
            scratch: km.array) -> None:
    wc, wsq = len(y0), len(square)
    y = {k: y0[wc - k] for k in range(1, wc + 1)}
    diagonal = [k for k in range(1, wc + 1) if 2 * k <= wsq]
    controls = km.array([y[k] for k in diagonal])
    targets = km.array([square[wsq - 2 * k] for k in diagonal])
    if not inverse:
        builder.cx(controls, targets)
    for k in range(1, wc + 1):
        terms = [(y[l], wsq - (k + l - 1)) for l in range(k + 1, wc + 1) if k + l - 1 <= wsq]
        if terms:
            _add_row(builder, inverse, y[k], terms, square, scratch)
    if inverse:
        builder.cx(controls, targets)


def _multiply_m(builder: km.CircuitBuilder, inverse: bool, x: km.array, square: km.array,
                z: km.array, scratch: km.array) -> None:
    width, wsq, wz = len(x), len(square), len(z) - 2
    for i in range(width):
        e = wz - wsq + i - width + 2
        _add_row(builder, inverse, x[i], [(square[j], j + e) for j in range(max(0, -e), wsq)], z, scratch)


def _correct(builder: km.CircuitBuilder, inverse: bool, z: km.array) -> None:
    constant = (3 << (len(z) - 2)) + 1
    if inverse:
        builder.isub(constant, target=z)
        builder.x(z)
    else:
        builder.x(z)
        builder.iadd(constant, target=z)


def _multiply_y0(builder: km.CircuitBuilder, inverse: bool, y0: km.array, z: km.array,
                 p: km.array, scratch: km.array) -> None:
    wc, wz, wp = len(y0), len(z) - 2, len(p) - 1
    for k in range(1, wc + 1):
        e = wp - wz - k
        _add_row(builder, inverse, y0[wc - k], [(z[j], j + e) for j in range(max(0, -e), wz + 2)], p, scratch)


def _denormalize(builder: km.CircuitBuilder, inverse: bool, flags: km.array, y1: km.array) -> None:
    wp = len(y1) - len(flags) - 1
    for k in (reversed(range(len(flags))) if inverse else range(len(flags))):
        lane = y1[k:k + wp + 2]
        if inverse:
            builder.right_rotate(lane, 1, control=flags[k])
        else:
            builder.left_rotate(lane, 1, control=flags[k])


def _phase_by_bits(builder: km.CircuitBuilder, y: km.array) -> None:
    f = len(y)
    with builder.mark('phase_by_bits'):
        for j in range(f):
            builder.z_pow(y[j], Fraction(2) ** (j - f + 1))


def build_nr_circuit(n_p: int, *, prec: Precision = Precision(),
                     schedule: ScheduleConfig = ScheduleConfig(),
                     compute_only: bool = False) -> km.Circuit:
    """Xây dựng mạch lượng tử tính pha 1/sqrt(x) với quản lý thanh ghi theo giai đoạn."""
    if n_p < 1:
        raise ValueError(f'n_p must be positive, got {n_p}.')
    width = 2 * n_p + 2
    out_bits = prec.output_bits(n_p)
    scratch_len = max(prec.square_bits, prec.product_bits + 2, prec.result_bits + 1)
    builder = km.CircuitBuilder()

    if compute_only:
        # Chế độ compute_only dùng cho kiểm thử tương thích baseline
        x = builder.create_quantum_register(width, name='x')
        y1 = builder.create_quantum_register(out_bits, name='y1')
        flags = builder.create_quantum_register(n_p, name='flags')
        selectors = builder.create_quantum_register(3, name='selectors')
        coefs = [builder.create_quantum_register(prec.coef_bits, name=f'c{j}') for j in range(4)]
        square = builder.create_quantum_register(prec.square_bits, name='square')
        z = builder.create_quantum_register(prec.product_bits + 2, name='z')
        scratch = builder.create_quantum_register(scratch_len, name='scratch')

        _normalize(builder, False, x, flags)
        _select_interval(builder, False, x, selectors)
        for j, reg in enumerate(coefs):
            _xor_coefficient(builder, prec, x, selectors, j, reg)
        _horner_step(builder, False, prec, x, selectors, coefs[2], coefs[3], scratch)
        _horner_step(builder, False, prec, x, selectors, coefs[1], coefs[2], scratch)
        _horner_step(builder, False, prec, x, selectors, coefs[0], coefs[1], scratch)
        _square(builder, False, coefs[0], square, scratch)
        _multiply_m(builder, False, x, square, z, scratch)
        _correct(builder, False, z)
        p = y1[:len(y1) - len(flags)]
        _multiply_y0(builder, False, coefs[0], z, p, scratch)
        _denormalize(builder, False, flags, y1)
        return builder.finish_circuit()

    # --- CHẾ ĐỘ THỰC THI CHÍNH THỨC (CẤP PHÁT THEO GIAI ĐOẠN) ---
    x = builder.create_quantum_register(width, name='x')
    flags = builder.alloc_qubits(n_p)
    with builder.mark('normalize'):
        _normalize(builder, False, x, flags)

    selectors = builder.alloc_qubits(3)
    with builder.mark('select_interval'):
        _select_interval(builder, False, x, selectors)

    # Cấp phát scratch và 4 hệ số ban đầu
    scratch = builder.alloc_qubits(scratch_len)
    c0 = builder.alloc_qubits(prec.coef_bits)
    c1 = builder.alloc_qubits(prec.coef_bits)
    c2 = builder.alloc_qubits(prec.coef_bits)
    c3 = builder.alloc_qubits(prec.coef_bits)

    with builder.mark('load_coefficients'):
        for j, reg in enumerate((c0, c1, c2, c3)):
            _xor_coefficient(builder, prec, x, selectors, j, reg)

    # Bước 1 Horner: c2 -= T(c3 * delta)
    with builder.mark('horner'):
        _horner_step(builder, False, prec, x, selectors, c2, c3, scratch)

    # Uncompute sớm c3 bằng Clifford (0 Toffoli) và giải phóng c3
    if schedule.early_uncompute_c3:
        with builder.mark('early_uncompute_c3'):
            _xor_coefficient(builder, prec, x, selectors, 3, c3)
            builder.free(c3)
            c3 = None

    # Bước 2 & 3 Horner
    with builder.mark('horner'):
        _horner_step(builder, False, prec, x, selectors, c1, c2, scratch)
        _horner_step(builder, False, prec, x, selectors, c0, c1, scratch)

    y0 = c0

    # Bước bình phương: square := T(y0^2)
    square = builder.alloc_qubits(prec.square_bits)
    with builder.mark('square'):
        _square(builder, False, y0, square, scratch)

    # Bước nhân M: z := T(M * square)
    z = builder.alloc_qubits(prec.product_bits + 2)
    with builder.mark('multiply_m'):
        _multiply_m(builder, False, x, square, z, scratch)

    # Tùy chọn pebbling uncompute sớm square
    if schedule.early_uncompute_square:
        with builder.mark('early_uncompute_square'):
            _square(builder, True, y0, square, scratch)
            builder.free(square)
            square = None

    # Bước hiệu chỉnh: z := 3 - z
    with builder.mark('correct'):
        _correct(builder, False, z)

    # Bước nhân y0: p := T(y0 * z)
    p = builder.alloc_qubits(prec.result_bits + 1)
    with builder.mark('multiply_y0'):
        _multiply_y0(builder, False, y0, z, p, scratch)

    # Tách vòng đời scratch và cấp phát mở rộng y1
    if schedule.staged_y1_scratch:
        builder.free(scratch)
        scratch = None
        y1_hi = builder.alloc_qubits(n_p)
        y1 = km.array(list(p) + list(y1_hi))
    else:
        y1_hi = builder.alloc_qubits(n_p)
        y1 = km.array(list(p) + list(y1_hi))

    with builder.mark('denormalize'):
        _denormalize(builder, False, flags, y1)

    _phase_by_bits(builder, y1)

    # --- NHÁNH UNCOMPUTE (ĐỐI XỨNG GƯƠNG TỪNG BƯỚC) ---
    with builder.mark('uncompute_y1'):
        with builder.mark('denormalize'):
            _denormalize(builder, True, flags, y1)

        if schedule.staged_y1_scratch:
            builder.free(y1_hi)
            scratch = builder.alloc_qubits(scratch_len)
        else:
            builder.free(y1_hi)

        with builder.mark('multiply_y0'):
            _multiply_y0(builder, True, y0, z, p, scratch)
        builder.free(p)

        with builder.mark('correct'):
            _correct(builder, True, z)

        if schedule.early_uncompute_square:
            square = builder.alloc_qubits(prec.square_bits)
            with builder.mark('early_uncompute_square'):
                _square(builder, False, y0, square, scratch)

        with builder.mark('multiply_m'):
            _multiply_m(builder, True, x, square, z, scratch)
        builder.free(z)

        with builder.mark('square'):
            _square(builder, True, y0, square, scratch)
        builder.free(square)

        with builder.mark('horner'):
            _horner_step(builder, True, prec, x, selectors, c0, c1, scratch)
            _horner_step(builder, True, prec, x, selectors, c1, c2, scratch)

        if schedule.early_uncompute_c3:
            c3 = builder.alloc_qubits(prec.coef_bits)
            with builder.mark('early_uncompute_c3'):
                _xor_coefficient(builder, prec, x, selectors, 3, c3)

        with builder.mark('horner'):
            _horner_step(builder, True, prec, x, selectors, c2, c3, scratch)

        with builder.mark('load_coefficients'):
            for j, reg in enumerate((c0, c1, c2, c3)):
                _xor_coefficient(builder, prec, x, selectors, j, reg)
                builder.free(reg)

        builder.free(scratch)

        with builder.mark('select_interval'):
            _select_interval(builder, True, x, selectors)
        builder.free(selectors)

        with builder.mark('normalize'):
            _normalize(builder, True, x, flags)
        builder.free(flags)

    return builder.finish_circuit()


def main() -> None:
    experiment_dir = Path(__file__).resolve().parent
    track = experiment_dir.parent.name
    experiment_id = experiment_dir.name
    root = experiment_dir.parents[2]
    if experiment_dir.parent.parent.name != 'src' or track not in {'invsqrt', 'dqi', 'dfthcsos'}:
        raise ValueError('solution.py must be located at src/<TRACK>/<ID>/solution.py')

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=experiment_dir / 'configs/staged_alloc.json')
    parser.add_argument('--output', type=Path, help='Optional output path; filename must match config stem')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing generated artifact')
    args = parser.parse_args()

    args.config = args.config.resolve()
    config_dir = (experiment_dir / 'configs').resolve()
    if args.config.parent != config_dir or args.config.suffix != '.json':
        raise ValueError('Config must be a JSON file directly inside this experiment configs/ directory')

    import re
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.config.stem):
        raise ValueError('Config name must contain only letters, digits, hyphens or underscores and start with a letter/digit')

    config = json.loads(args.config.read_text(encoding='utf-8'))
    allowed_keys = {'n_p', 'precision', 'schedule'}
    if not set(config).issubset(allowed_keys) or not {'n_p', 'precision'}.issubset(set(config)):
        raise ValueError('Config requires n_p and precision (optional schedule)')

    prec = Precision(**config['precision'])
    n_p = config['n_p']
    schedule_data = config.get('schedule', {})
    schedule = ScheduleConfig(**schedule_data)

    output = args.output or root / 'artifacts' / track / experiment_id / f'{args.config.stem}.kmb'
    if output.name != args.config.stem + '.kmb':
        raise ValueError('Output filename must be <config-name>.kmb')
    if output.exists() and not args.overwrite:
        raise FileExistsError(f'{output} exists; pass --overwrite to rebuild')

    output.parent.mkdir(parents=True, exist_ok=True)
    max_x = 3 * (2**n_p - 2)**2
    error = relative_error(n_p, prec, np.arange(1, max_x + 1))
    print(f'Model: max relative error 2^{math.log2(error.max()):.2f} at x={error.argmax() + 1}')

    circuit = build_nr_circuit(n_p, prec=prec, schedule=schedule)
    circuit.to_file(str(output), format='kmb')
    print(f'Wrote {output}: {circuit.operation_statistics().num_toffoli_like:,} Toffolis, {circuit.num_qubits} qubits.')


if __name__ == '__main__':
    main()
