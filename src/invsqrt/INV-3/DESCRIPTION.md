# [INV-3] Cấp phát thanh ghi theo giai đoạn và uncompute sớm hệ số Horner cùng bình phương trung gian, giữ nguyên độ rộng bit số học baseline

Loại: Tinh chỉnh một phương án.

## File gốc

- File Python gốc kế thừa: [INV-BASELINE/solution.py](../INV-BASELINE/solution.py) (tại commit nhánh chính `13ec200455ab4aea1afc8df0bcab493cd269075e`, Git blob SHA-256: `a5a5fb399614c873625d37efb2e7a04ca070d943`).
- Mô tả baseline gốc: [INV-BASELINE/DESCRIPTION.md](../INV-BASELINE/DESCRIPTION.md).
- Cấu hình baseline đối chiếu: [INV-BASELINE/configs/baseline.json](../INV-BASELINE/configs/baseline.json) (Git blob SHA-256: `d2be4a71a86092762b1d0d64b86dcb47e2ed31c3`).
- Nguồn tham khảo của ban tổ chức: [verifiers/invsqrt/nr_reference_circuit.py](../../../verifiers/invsqrt/nr_reference_circuit.py) (SHA-256 trong [data_manifest.json](../../../data_manifest.json): `bb90330dcf774f7b502de471293facba67f27952cc8808fe4a9970a9b1322e23`, giấy phép Apache-2.0 tại [src/LICENSE.txt](../../LICENSE.txt)).
- Verifier chấm điểm: [verifiers/invsqrt/verify_submission_invsqrt.py](../../../verifiers/invsqrt/verify_submission_invsqrt.py) (SHA-256 trong [data_manifest.json](../../../data_manifest.json): `ddef520dec6b68d1cf0a6f328ddd36d79eb84570b9192cf3f7acaf073f06733a`).
- Ghi chú tài liệu liên quan đã merge trên nhánh chính: [research/invsqrt/papers/arxiv-2308.12352/note.md](../../../research/invsqrt/papers/arxiv-2308.12352/note.md).

## Phần tinh chỉnh và lý do

### 1. Các hàm và khối xử lý sẽ sửa trong `INV-BASELINE/solution.py`

Chỉ can thiệp vào lịch trình cấp phát/giải phóng thanh ghi (`builder.alloc_qubits` / `builder.free`) và lịch trình gọi uncompute trung gian trong các hàm xây dựng mạch của [INV-BASELINE/solution.py](../INV-BASELINE/solution.py):

1. `build_nr_circuit` (dòng 386–412) và `_compute_y1` (dòng 332–376): thay việc cấp phát tĩnh toàn bộ 10 thanh ghi ngay đầu mạch bằng cấp phát theo giai đoạn (staged allocation) và giải phóng sớm các thanh ghi đã đưa về $|0\rangle$.
2. `_load_coefficients` (dòng 244–256) và `_horner` (dòng 258–272): hỗ trợ nạp/xóa riêng từng hệ số hoặc xóa sớm thanh ghi hệ số bậc ba `c3` (`coefs[3]`, độ rộng `wc = coef_bits = 17` qubit) ngay sau bước nhân đầu tiên của Horner bằng mạng cổng Clifford `gf2_iadd` ($\Delta\text{Toffoli} = 0$).
3. Khối chuyển tiếp giữa `_multiply_m` (dòng 292–299), `_correct` (dòng 301–310), `_multiply_y0` (dòng 312–319) và `_denormalize` (dòng 321–330):
   - Trì hoãn cấp phát thanh ghi tích Newton `p` (`wp + 1 = result_bits + 1 = 30` qubit) tới ngay trước `_multiply_y0` thay vì cấp phát cả `y1` (`out_bits = wp + n_p + 1 = 40` qubit) từ đầu mạch.
   - Giải phóng thanh ghi `scratch` ($\max(\text{wsq}, \text{wz}+2, \text{wp}+1) = 30$ qubit) ngay sau khi `_multiply_y0` hoàn tất, rồi mới cấp phát thêm `n_p = 10` qubit cao của `y1` để ghép thành thanh ghi `y1` (40 qubit) cho `_denormalize`.
   - Tùy chọn cấu hình uncompute sớm (pebbling) thanh ghi `square` (`wsq = square_bits = 28` qubit) và/hoặc các hệ số trung gian trước khi cấp phát `p` cho `_multiply_y0` để kiểm chứng đánh đổi giữa giảm thêm $Q$ và chi phí Toffoli tăng thêm.

Toàn bộ mô hình cổ điển `Precision`, `fixed_point_model`, `relative_error` (dòng 77–170), bảng hệ số `POLY_A`, `POLY_B` (dòng 73–74), toán tử số học `_add_row`, `_flag_zero_pair`, `_normalize`, `_select_interval`, `_square`, `_multiply_m`, `_correct`, `_multiply_y0`, `_denormalize`, `_phase_by_bits` giữ nguyên công thức số học và quy tắc cắt cụt từng bit của baseline.

### 2. Hành vi trước và sau khi sửa

- **Hành vi trước khi sửa (`INV-BASELINE`):**
  Trong `build_nr_circuit` (dòng 400–405), mạch cấp phát đồng loạt tất cả thanh ghi trước khi gọi `_compute_y1`:
  - `x`: $2 n_p + 2 = 22$ qubit (thanh ghi đầu vào, giữ nguyên).
  - `y1`: $\text{result\_bits} + n_p + 1 = 29 + 10 + 1 = 40$ qubit.
  - `flags`: $n_p = 10$ qubit.
  - `selectors`: $3$ qubit.
  - `coefs`: $4 \times \text{coef\_bits} = 4 \times 17 = 68$ qubit (`c0, c1, c2, c3`).
  - `square`: $\text{square\_bits} = 28$ qubit.
  - `z`: $\text{product\_bits} + 2 = 30$ qubit.
  - `scratch`: $\max(28, 30, 30) = 30$ qubit.
  Tổng số qubit cấp phát tường minh là $22 + 40 + 10 + 3 + 68 + 28 + 30 + 30 = 231$ qubit. Khi bước `_multiply_y0` thực thi `builder.isub` / `builder.iadd` trên lát cắt dài tới $30$ bit (`p` có độ rộng $30$ bit), bộ cộng ripple-carry nội bộ của Kickmix cấp phát tạm thời thêm $29$ qubit ancilla nội bộ, đẩy đỉnh số qubit của mạch lên $Q = 231 + 29 = 260$ qubit. Tất cả các thanh ghi chỉ được `builder.free(...)` ở cuối mạch sau khi hoàn tất cả nhánh `uncompute_y1` (dòng 410–411).

- **Hành vi sau khi sửa (`INV-3`):**
  Vòng đời của từng thanh ghi được thu hẹp về đúng khoảng thời gian thanh ghi đó mang thông tin khác $|0\rangle$:
  1. **Xóa và giải phóng sớm `c3` (17 qubit) bằng Clifford:** Trong `_horner`, `c3` chỉ đóng vai trò số nhân ở bước 1 (`c2 -= T(c3 * delta)`). Sau bước 1, `c3` không bị ghi đè và vẫn chứa đúng giá trị bảng hệ số đã nạp từ `_load_coefficients`. Vì `_load_coefficients` chỉ gồm các cổng Clifford `gf2_iadd` điều khiển bởi `(True, top, t_a, t_b)` — vốn đang giữ nguyên giá trị suốt giai đoạn này — việc gọi lại phép nạp Clifford riêng cho `c3` sẽ uncompute `c3` về $|0\rangle$ chính xác tuyệt đối với $0$ cổng Toffoli, cho phép `builder.free(c3)` ngay lập tức trước bước 2 của `_horner`.
  2. **Trì hoãn cấp phát `p` và tách vòng đời `scratch` khỏi 10 qubit cao của `y1`:**
     - Trước `_multiply_y0`, thanh ghi `y1` hoàn toàn chưa được dùng. Ta không cấp phát `y1` (40 qubit) từ đầu mạch.
     - Ngay trước `_multiply_y0`, mới cấp phát thanh ghi `p` ($30$ qubit) để nhận tích $p = T(y_0 \cdot z)$.
     - Trong `_multiply_y0`, `scratch` (30 qubit) và ancilla nội bộ của `iadd`/`isub` (29 qubit) cùng hoạt động, nhưng lúc này `c3` (17 qubit) đã được giải phóng và $10$ qubit cao của `y1` chưa được cấp phát (giảm ngay $17 + 10 = 27$ qubit tại thời điểm đạt đỉnh của `_multiply_y0`).
     - Ngay sau khi `_multiply_y0` kết thúc, toàn bộ `scratch` (30 qubit) đã trở về $|0\rangle$ (do `_add_row` luôn gọi `del_and` ở cuối mỗi hàng). Ta gọi `builder.free(scratch)` để trả 30 qubit về pool trước khi cấp phát `y1_hi` ($n_p = 10$ qubit) và ghép `y1 = km.array(list(p) + list(y1_hi))` (40 qubit) cho `_denormalize`.
     - Trong `_denormalize`, mỗi phép `left_rotate(lane, 1, control=flags[k])` xoay `lane` dài $w_p + 2 = 31$ qubit chỉ cần 1–2 ancilla tạm thời (nhỏ hơn nhiều so với $30$ qubit `scratch` vừa giải phóng + $29$ ancilla của bộ cộng).
  3. **Tùy chọn pebbling `square` (28 qubit) trước `_multiply_y0`:**
     - Thanh ghi `square` ($28$ qubit) chỉ dùng để tính `z = T(M * square)` trong `_multiply_m`. Trong suốt `_multiply_y0`, `_denormalize` và `_phase_by_bits`, `square` không được đọc hay ghi, trong khi cả `y0` (`c0`) và `x` đều vẫn còn nguyên.
     - Nếu bật tùy chọn uncompute sớm `square` (`early_uncompute_square = true`): ngay sau `_multiply_m` (hoặc sau `_correct`), mạch gọi `_square(builder, True, y0, square, scratch)` để đưa `square` về $|0\rangle$ và `builder.free(square)` trước khi cấp phát `p` cho `_multiply_y0`. Nhờ đó đỉnh qubit tại `_multiply_y0` giảm thêm $28$ qubit nữa (tổng mức giảm dự kiến $27 + 28 = 55$ qubit, đưa $Q$ từ $260$ xuống $205$). Đánh đổi là ở nhánh `uncompute_y1`, trước khi uncompute `_multiply_m`, mạch phải tính lại `_square` rồi sau đó uncompute `_square` một lần nữa (tăng thêm 1 lần compute + 1 lần uncompute của `_square`, tức khoảng $2 \times 442 = 884$ Toffoli).

### 3. Lý do dự kiến có lợi

- Theo [research/invsqrt/papers/arxiv-2308.12352/note.md](../../../research/invsqrt/papers/arxiv-2308.12352/note.md) (mục II.D, dòng 121–125 và bảng dòng 228), bài báo gốc thảo luận việc giữ lại khoảng 2000 qubit trung gian để giảm chi phí uncompute. Tuy nhiên, trong hợp đồng chấm điểm của benchmark tại [verifiers/invsqrt/verify_submission_invsqrt.py](../../../verifiers/invsqrt/verify_submission_invsqrt.py) (dòng 39–41 và 327):
  $$\text{score} = Q \times C = \text{circuit.num\_qubits} \times \left(\text{toffoli\_count} + \frac{T}{4}\right)$$
  Hàm điểm nhân trực tiếp với `circuit.num_qubits` của mạch độc lập (không cộng `system_qubits = 6540` vào thừa số $Q$).
- Với phương án không pebbling (`early_uncompute_c3 = true`, `staged_y1_scratch = true`, `early_uncompute_square = false`), số cổng Toffoli, số cổng $T$, số phép quay `Z_POW` và giá trị pha đầu ra trên mọi $x$ giữ nguyên tuyệt đối so với baseline ($\Delta C = 0$, $\Delta\text{error} = 0$), trong khi đỉnh qubit $Q$ giảm từ $260$ xuống $233$ ($\Delta Q = -27$ qubit, tương đương giảm $\approx 10.38\%$ chi phí $Q \times C$, hay hệ số cải thiện $\approx 1.116\times$).
- Với phương án có thêm pebbling `square` (`early_uncompute_square = true`), đỉnh qubit dự kiến giảm xuống $205$ ($\Delta Q = -55$ qubit, giảm $21.15\%$ số qubit), trong khi $C$ tăng từ $\approx 7986.32$ lên $\approx 8870.32$ ($+11.07\%$), tích $Q \times C$ dự kiến đạt $205 \times 8870.32 \approx 1.818 \times 10^6$ (so với $233 \times 7986.32 \approx 1.861 \times 10^6$ và baseline $2.076 \times 10^6$). Cả hai phương án đều nằm trong cùng khuôn khổ quản lý vòng đời thanh ghi và sẽ được kiểm chứng trực tiếp bằng config JSON ở giai đoạn 03.

## Cách thực hiện và đánh đổi

### 1. Thiết kế chi tiết lịch trình cấp phát, uncompute và giải phóng thanh ghi

Giữ nguyên định nghĩa lớp `Precision` của baseline với các độ rộng bit:
- `width` $= 2 n_p + 2$ ($22$ bit khi $n_p = 10$).
- $d = \text{delta\_bits}$ ($14$), $w_c = \text{coef\_bits}$ ($17$), $w_{\text{sq}} = \text{square\_bits}$ ($28$), $w_z = \text{product\_bits}$ ($28$, thanh ghi `z` có $w_z + 2 = 30$ bit), $w_p = \text{result\_bits}$ ($29$, lát cắt `p` có $w_p + 1 = 30$ bit, thanh ghi `y1` có $\text{out\_bits} = w_p + n_p + 1 = 40$ bit).
- Độ rộng `scratch_len` $= \max(w_{\text{sq}}, w_z + 2, w_p + 1)$ ($30$ bit).

#### A. Hàm nạp/xóa hệ số `_load_coef_j` và `_load_coefficients`

Tách thao tác XOR bảng hệ số trong `_load_coefficients` để có thể gọi cho một chỉ số hệ số $j \in \{0, 1, 2, 3\}$ bất kỳ:

```python
def _xor_coefficient(builder: km.CircuitBuilder, prec: Precision, x: km.array,
                     selectors: km.array, j: int, reg: km.array) -> None:
    """XOR hệ số bậc j của khoảng được chọn bởi (top, t_a, t_b) vào thanh ghi reg (tự nghịch đảo)."""
    top, t_a, t_b = x[len(x) - 1], selectors[0], selectors[1]
    table = prec.coefficient_table()
    for control, value in ((True, table[0][j]), (top, table[0][j] ^ table[2][j]),
                           (t_a, table[0][j] ^ table[1][j]), (t_b, table[2][j] ^ table[3][j])):
        builder.gf2_iadd(value, target=reg, control=control)
```

Do `gf2_iadd` chỉ dùng cổng $X$ và $\text{CNOT}$ (Clifford, đối hợp $U^2 = I$), nếu thanh ghi `reg` đang ở trạng thái $|c_j\rangle$ và `x`, `selectors` không đổi, gọi lại `_xor_coefficient(..., j, reg)` sẽ đưa `reg` về đúng $|0^{\otimes w_c}\rangle$ mà không tiêu tốn cổng Toffoli hay phép đo nào.

#### B. Luồng thực thi chi tiết (Compute → Phase → Uncompute)

Khi `compute_only=False` (chế độ tạo mạch nộp bài), trình tự quản lý bộ nhớ lượng tử diễn ra đối xứng gương giữa hai chiều compute và uncompute:

**Chiều Compute (`compute_y1`):**
1. Khởi tạo thanh ghi đầu vào `x = builder.create_quantum_register(width, name='x')` ($22$ qubit).
2. Cấp phát `flags = builder.alloc_qubits(n_p)` ($10$ qubit) và chạy `_normalize(builder, False, x, flags)`.
3. Cấp phát `selectors = builder.alloc_qubits(3)` ($3$ qubit) và chạy `_select_interval(builder, False, x, selectors)`.
4. Cấp phát `c0, c1, c2, c3` ($4 \times w_c = 68$ qubit) và `scratch = builder.alloc_qubits(scratch_len)` ($30$ qubit). Nạp hệ số vào `c0, c1, c2, c3` bằng `_xor_coefficient`.
5. Thực hiện bước 1 của `_horner`: `c2 -= T(c3 * delta)` dùng `scratch`.
6. **Uncompute và giải phóng sớm `c3`:** Nếu `early_uncompute_c3=True`, gọi `_xor_coefficient(builder, prec, x, selectors, 3, c3)` để đưa `c3` về $|0^{\otimes w_c}\rangle$, sau đó gọi `builder.free(c3)` (giải phóng $17$ qubit).
7. Thực hiện bước 2 và bước 3 của `_horner`: `c1 -= T(c2 * delta)` và `c0 -= T(c1 * delta)`, thu được $y_0$ trong `c0`.
8. Cấp phát `square = builder.alloc_qubits(wsq)` ($28$ qubit) và tính `_square(builder, False, y0, square, scratch)`.
9. Cấp phát `z = builder.alloc_qubits(wz + 2)` ($30$ qubit) và tính `_multiply_m(builder, False, x, square, z, scratch)`.
10. **Tùy chọn uncompute và giải phóng sớm `square`:** Nếu `early_uncompute_square=True`, gọi `_square(builder, True, y0, square, scratch)` để đưa `square` về $|0^{\otimes w_{\text{sq}}}\rangle$, rồi gọi `builder.free(square)` (giải phóng $28$ qubit).
11. Thực hiện `_correct(builder, False, z)` (`z := 3 - z`).
12. Cấp phát `p = builder.alloc_qubits(wp + 1)` ($30$ qubit) và tính `_multiply_y0(builder, False, y0, z, p, scratch)`. (Tại đây bộ cộng nội bộ của Kickmix mượn tối đa $w_p = 29$ ancilla rồi trả lại ngay sau mỗi `iadd`/`isub`).
13. **Giải phóng `scratch` trước khi mở rộng `y1`:** Nếu `staged_y1_scratch=True`, vì `_add_row` đã `del_and` toàn bộ tích riêng nên `scratch` đang ở trạng thái $|0^{\otimes 30}\rangle$; gọi `builder.free(scratch)` (giải phóng $30$ qubit).
14. Cấp phát phần bit cao `y1_hi = builder.alloc_qubits(n_p)` ($10$ qubit), ghép thành mảng thanh ghi `y1 = km.array([*p, *y1_hi])` ($40$ qubit), và chạy `_denormalize(builder, False, flags, y1)`.

**Bước Áp pha (`phase_by_bits`):**
15. Gọi `_phase_by_bits(builder, y1)` áp $40$ cổng `Z_POW` lên `y1`.

**Chiều Uncompute (`uncompute_y1` — đối xứng gương từng bước):**
16. Chạy `_denormalize(builder, True, flags, y1)`. Sau bước này, $n_p = 10$ qubit cao `y1_hi = y1[wp + 1:]` trở về trạng thái $|0^{\otimes n_p}\rangle$, còn `p = y1[:wp + 1]` chứa lại tích $T(y_0 \cdot z)$.
17. Giải phóng `builder.free(y1_hi)` ($10$ qubit) và cấp phát lại `scratch = builder.alloc_qubits(scratch_len)` ($30$ qubit) (khi `staged_y1_scratch=True`).
18. Chạy `_multiply_y0(builder, True, y0, z, p, scratch)` để đưa `p` về $|0^{\otimes (w_p + 1)}\rangle$, rồi gọi `builder.free(p)` ($30$ qubit).
19. Chạy `_correct(builder, True, z)` để khôi phục `z` về $T(M \cdot \text{square})$.
20. Nếu `early_uncompute_square=True`: cấp phát lại `square = builder.alloc_qubits(wsq)` ($28$ qubit) và gọi `_square(builder, False, y0, square, scratch)` để tái tạo `square`.
21. Chạy `_multiply_m(builder, True, x, square, z, scratch)` để đưa `z` về $|0^{\otimes (w_z + 2)}\rangle$, rồi gọi `builder.free(z)` ($30$ qubit).
22. Chạy `_square(builder, True, y0, square, scratch)` để đưa `square` về $|0^{\otimes w_{\text{sq}}}\rangle$, rồi gọi `builder.free(square)` ($28$ qubit).
23. Đảo bước 3 và bước 2 của `_horner`: khôi phục `c0` về hệ số ban đầu và `c1` về hệ số ban đầu.
24. Nếu `early_uncompute_c3=True`: cấp phát lại `c3 = builder.alloc_qubits(wc)` ($17$ qubit) và gọi `_xor_coefficient(builder, prec, x, selectors, 3, c3)` để tái tạo `c3`.
25. Đảo bước 1 của `_horner`: khôi phục `c2` về hệ số ban đầu.
26. Gọi `_xor_coefficient` cho $j \in \{0, 1, 2, 3\}$ để đưa `c0, c1, c2, c3` về $|0^{\otimes w_c}\rangle$, rồi `builder.free` toàn bộ `c0, c1, c2, c3` và `scratch`.
27. Chạy `_select_interval(builder, True, x, selectors)` và `builder.free(selectors)`.
28. Chạy `_normalize(builder, True, x, flags)` và `builder.free(flags)`.

Khi `compute_only=True` (dùng cho kiểm thử đơn vị so khớp đầu ra `y1` với `fixed_point_model`), hàm vẫn tạo thanh ghi có tên `y1` và giữ nguyên ngữ nghĩa đầu ra để tương thích kiểm thử.

### 2. Bảng đối chiếu ngân sách qubit theo từng giai đoạn

Với cấu hình độ rộng chuẩn (`n_p = 10, delta_bits = 14, coef_bits = 17, square_bits = 28, product_bits = 28, result_bits = 29`), số qubit đang sống (active qubits, tính cả đỉnh ancilla nội bộ của cổng `iadd`/`isub`/`left_rotate`) tại từng giai đoạn như sau:

| Giai đoạn trong mạch | Thanh ghi đang cấp phát (chế độ `staged_no_pebble`: xóa sớm `c3` + tách `y1`/`scratch`) | Qubit thanh ghi | Ancilla nội bộ cực đại của cổng | Tổng qubit tức thời (chế độ `staged_no_pebble`) | Tổng qubit tức thời (chế độ `staged_pebble_square`: thêm xóa sớm `square`) | Baseline (`INV-BASELINE`) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1. `_normalize` | `x` (22), `flags` (10) | 32 | ~2 | 34 | 34 | 233 |
| 2. `_select_interval` | `x` (22), `flags` (10), `selectors` (3) | 35 | 0 | 35 | 35 | 231 |
| 3. `_horner` bước 1 (`c2 -= c3*delta`) | `x` (22), `flags` (10), `selectors` (3), `c0..c3` (68), `scratch` (30) | 133 | 16 (`isub` 17-bit) | 149 | 149 | 247 |
| 4. `_horner` bước 2 & 3 (sau `free(c3)`) | `x` (22), `flags` (10), `selectors` (3), `c0..c2` (51), `scratch` (30) | 116 | 16 (`isub` 17-bit) | 132 | 132 | 247 |
| 5. `_square` | + `square` (28) | 144 | 27 (`iadd` 28-bit) | 171 | 171 | 258 |
| 6. `_multiply_m` | + `z` (30) | 174 | 29 (`iadd` 30-bit) | 203 | 203 | 260 |
| 7. Uncompute sớm `square` (nếu bật) | `free(square)` (-28) sau uncompute | 174 → 146 | 27 (`isub` 28-bit) | 174 (không bật) | 201 → 146 | 231 |
| 8. `_multiply_y0` (**Đỉnh qubit**) | + `p` (30) | 204 (hoặc 176) | 29 (`iadd` 30-bit) | **233** | **205** | **260** |
| 9. `_denormalize` (sau `free(scratch)`, +`y1_hi`) | `free(scratch)` (-30), + `y1_hi` (10) → giữ `y1` (40) | 184 (hoặc 156) | ~2 (`left_rotate`) | 186 | 158 | 233 |

### 3. Điều kiện đúng, bất biến (invariants) và phân tích sai số

- **Bất biến giải phóng thanh ghi (`builder.free`):** Mọi qubit truyền vào `builder.free(reg)` bắt buộc phải ở trạng thái $|0\rangle$ độc lập với nhánh kết quả đo của các cổng `del_and` (`HMR`).
  - Với `c3`: `c3` chỉ được đọc làm điều khiển/toán hạng nguồn trong `_add_row` của bước 1 `_horner`. Trong `_add_row`, `c3` là đầu vào điều khiển của `init_and` và `del_and`. Sau khi `del_and` đo theo cơ sở $X$ và sửa pha `CZ` lên `control` và `sources` (`c3`), trạng thái trong cơ sở tính toán của `c3` vẫn hoàn toàn không đổi (vì $Z$ tác động lên trạng thái cơ sở tính toán $|b\rangle$ chỉ nhân pha $(-1)^b$, và thực tế trong `_load_coefficients` các bit của `c3` là hàm tất định của các bit cơ sở tính toán `top, second, third` của `x_norm` trên từng thành phần chồng chập). Do đó, áp dụng lại mạng CNOT/$X$ của `_xor_coefficient` cho `c3` khôi phục `c3` về $|0^{\otimes w_c}\rangle$ chính xác trên mọi nhánh đo.
  - Với `scratch`: Trong mọi lệnh gọi `_add_row`, các qubit `products = scratch[...]` được khởi tạo bằng `init_and` từ trạng thái $|0\rangle$ và được xóa bằng `del_and` (đo $X$ và reset về $|0\rangle$) ngay cuối `_add_row`. Các qubit khác của `scratch` không thuộc `products` không bị tác động và luôn ở $|0\rangle$. Do đó, sau khi kết thúc `_multiply_y0`, toàn bộ $30$ qubit của `scratch` chắc chắn ở trạng thái $|0\rangle$ và an toàn để `free(scratch)`.
  - Với `y1_hi` ($10$ qubit cao của `y1`): Trước `_denormalize`, `y1_hi` vừa được cấp phát ở $|0^{\otimes 10}\rangle$. Trong `_denormalize` chiều compute, các bit của `p` được dịch trái sang `y1_hi` tối đa $s \le n_p = 10$ vị trí. Trong `_denormalize` chiều uncompute, các phép `right_rotate` ngược lại dịch toàn bộ các bit đó trả về `p` ($30$ qubit đầu), đưa `y1_hi` trở lại $|0^{\otimes 10}\rangle$ trước khi `free(y1_hi)`.
  - Với `square` (khi bật `early_uncompute_square`): `_square(builder, True, y0, square, scratch)` là nghịch đảo chính xác của `_square(builder, False, y0, square, scratch)` với `y0` và `scratch` sạch, nên đưa `square` về $|0^{\otimes 28}\rangle$ trước khi `free(square)`.
- **Ảnh hưởng sai số và trường hợp biên:**
  - Vì toàn bộ phép toán số học trên `x`, `flags`, `selectors`, `c0..c3`, `square`, `z`, `p`, `y1` và bước áp pha `_phase_by_bits(builder, y1)` thực hiện đúng cùng tập biểu thức đại số trên cùng độ rộng bit như baseline, giá trị nguyên $y_1(x)$ sinh ra tại bước áp pha trùng khớp từng bit với `fixed_point_model(n_p, prec, xs)` trên toàn bộ miền $x \in [1, 3\,133\,452]$, kể cả các biên khoảng chuẩn hóa $M \in \{1, 1.5, 2, 3\}$ và mọi giá trị dịch $s \in \{0, \dots, 10\}$.
  - Sai số tương đối cực đại theo mô hình giữ nguyên ở $2^{-25.07}$ (tại $x = 2\,588\,411$), và tỉ số `worst_error_over_tolerance` trên bộ `dev_5min` dự kiến giữ nguyên bằng `0.37839383360236045` (tại $x = 3\,010\,856$).
- **Vai trò và ràng buộc tham số cấu hình (`configs/<name>.json`):**
  - Ngoài hai khóa chuẩn `n_p` và `precision` (`delta_bits`, `coef_bits`, `square_bits`, `product_bits`, `result_bits`), cấu hình JSON trong hướng này có thể hỗ trợ tùy chọn lịch trình bộ nhớ (hoặc mặc định bật `early_uncompute_c3` và `staged_y1_scratch`, còn `early_uncompute_square` điều khiển bằng cờ boolean trong config). Việc chọn và cố định các file JSON config cụ thể sẽ được thực hiện ở giai đoạn 03 trước khi compile.
- **Giả định cần kiểm chứng ở giai đoạn 03:**
  - Giả định rằng `km.CircuitBuilder.free(reg)` trả các chỉ số qubit của `reg` vào danh sách rãnh (free pool) và được `km.CircuitBuilder.alloc_qubits(...)` cũng như các ancilla nội bộ của `builder.iadd` / `builder.isub` / `builder.left_rotate` tái sử dụng ngay lập tức. Cách kiểm tra: ở giai đoạn 03, compile mạch và kiểm tra trực tiếp `circuit.num_qubits` giảm từ $260$ xuống $\le 235$ (với config không pebbling) và $\le 210$ (với config pebbling `square`).

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng:
  - Source và config baseline: [INV-BASELINE/solution.py](../INV-BASELINE/solution.py) và [INV-BASELINE/configs/baseline.json](../INV-BASELINE/configs/baseline.json) tại commit `13ec200455ab4aea1afc8df0bcab493cd269075e`.
  - Run `dev_5min` đối chứng: [20261106T111429Z-local-dev5min](../../../results/invsqrt/INV-BASELINE/baseline/dev_5min/20261106T111429Z-local-dev5min/verifier.json) (`status = PASS`, `score = 2076443.1049173493`, `num_qubits = 260`, `toffoli_equivalent = 7986.319634297497`, `toffoli_count = 7735.0`, `t_count = 1.0`, `rotation_count = 37.0`, `worst_error_over_tolerance = 0.37839383360236045`, `worst_x = 3010856`, `seed = 20261106`, `invsqrt_samples = 4096`, `invsqrt_repeats = 2`).
  - Run `full` đối chứng: [20261106T103144Z-colab-full-ef9a7a](../../../results/invsqrt/INV-BASELINE/baseline/full/20261106T103144Z-colab-full-ef9a7a/verifier.json) (`status = PASS`, `score = 2076774.233715282`, `num_qubits = 260`, `toffoli_equivalent = 7987.593206597238`, `worst_error_over_tolerance = 0.4769116097939472`, `worst_x = 2588411`).
- Dự đoán:
  - Cấu hình 1 (dự kiến đặt tên `staged_alloc` ở giai đoạn 03 — bật xóa sớm `c3` bằng Clifford và tách vòng đời `p`/`y1_hi`/`scratch`, không pebbling `square`): dự đoán `num_qubits` giảm từ $260$ xuống $233$ ($\Delta Q = -27$), `toffoli_count` giữ nguyên $7735.0$ ($\Delta\text{Toffoli} = 0$), `worst_error_over_tolerance` trên `dev_5min` giữ nguyên `0.37839383360236045`, và điểm `dev_5min` giảm xuống $\approx 233 \times 7986.3196 \approx 1\,860\,812.47$ (cải thiện $\approx 1.116\times$).
  - Cấu hình 2 (dự kiến đặt tên `pebble_square` ở giai đoạn 03 — bật thêm uncompute sớm `square` trước `_multiply_y0`): dự đoán `num_qubits` giảm xuống $205$ ($\Delta Q = -55$), `toffoli_count` tăng thêm $2 \times 442 = 884$ lên $8619.0$, `toffoli_equivalent` $\approx 8870.32$, và điểm `dev_5min` đạt $\approx 205 \times 8870.32 \approx 1\,818\,415.52$ (cải thiện $\approx 1.142\times$).
- Ủng hộ / bác bỏ:
  - **Ủng hộ hypothesis:** Chạy `dev_5min` đạt `status = PASS` (khôi phục `x` và mọi qubit `scratch` về $|0\rangle$ trên toàn bộ 8192 shots), `worst_error_over_tolerance` khớp với baseline (`0.37839383360236045`), `num_qubits` giảm xuống $\le 235$, và `score` thấp hơn `2076443.1049173493`. Giữa hai cấu hình có/không pebbling `square`, cấu hình nào cho tích $Q \times C$ thực tế thấp hơn sẽ được chọn làm ứng viên chính.
  - **Bác bỏ hypothesis:** Nếu bộ quản lý qubit của `km.CircuitBuilder` không tái sử dụng các qubit đã `free()` khiến `num_qubits` giảm dưới $5$ qubit, hoặc nếu việc giải phóng/tái cấp phát làm bẩn scratch (`Scratch qubit ... did not return to |0>`) không thể khắc phục mà không tăng $Q \times C$ vượt baseline. Riêng nhánh pebbling `square` sẽ bị loại nếu phần tăng Toffoli làm `score` cao hơn cấu hình không pebbling.
  - **Trường hợp chưa đủ bằng chứng:** Mới chỉ có kết quả compile (`build_only`) hoặc `smoke` mà chưa chạy `dev_5min` cùng profile với baseline.
- Điều kiện dừng:
  - Dừng thử thêm config trong hướng này sau tối đa 2–3 cấu hình lịch trình bộ nhớ (`staged_alloc`, `pebble_square`, và nhiều nhất 1 biến thể pebbling trung gian Horner nếu cần so sánh) khi đã xác định rõ cấu hình tối ưu hóa $Q \times C$ ở độ rộng bit chuẩn.
  - Không thay đổi độ rộng bit (`delta_bits`, `coef_bits`, `square_bits`, `product_bits`, `result_bits`) trong hướng này; việc kết hợp lịch trình bộ nhớ của `INV-3` với tinh chỉnh độ rộng bit sẽ được thực hiện ở một hướng kết hợp riêng sau khi `INV-3` hoàn tất.
- Kiểm tra ứng viên cuối:
  - Vì thay đổi của `INV-3` bảo toàn từng bit giá trị số học $y_1(x)$ trên mọi $x \in [1, 3\,133\,452]$, rủi ro quá khớp (overfitting) vào bộ mẫu `dev_5min` bằng 0 đối với sai số số học; tuy nhiên các nhánh đo ngẫu nhiên của `HMR` (`del_and`) phụ thuộc vào seed mạch. Do đó, ứng viên tốt nhất trên `dev_5min` sẽ được kiểm tra xác nhận trên chế độ `full` (hoặc kiểm tra bổ sung với seed/mẫu độc lập nếu chưa chạy `full`) để xác nhận toàn bộ nhánh đo uncompute đều trả scratch về $|0\rangle$.

## Kết luận và phiên bản tái lập

Chưa có kết quả chạy thực nghiệm (đang ở giai đoạn 02 — đăng ký Issue, tạo branch và mô tả thiết kế; sẽ triển khai `solution.py`, tạo config JSON và compile ở giai đoạn 03).

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa có (sẽ tạo ở giai đoạn 03) | Chưa có | Chưa chấm |
| Full | Chưa có (sẽ tạo ở giai đoạn 03) | Chưa có | Chưa chấm |

Mã triển khai: [solution.py](solution.py). Cấu hình: [configs](configs/).
Điểm và các run: [SCORES.md](../SCORES.md).
