# [INV-49] Giảm đỉnh qubit của mạch tra bảng bậc hai INV-41 bằng nạp c0 sau phép nhân và giới hạn qubit cho bộ cộng, giữ nguyên đa thức và độ rộng bit

Loại: Tinh chỉnh một phương án.

## File gốc

Kế thừa [INV-41/solution.py](../INV-41/solution.py), [INV-41/configs/base.json](../INV-41/configs/base.json) và [mô tả INV-41](../INV-41/DESCRIPTION.md) tại commit `56e39e9fc4bec3f7ac3b8c47ee3f1ba5cbfc3932` (merge PR #42 vào main; source INV-41 dựng mạch ở `78674187c2daa4dbc34b6052f91b733d6760a0f7`). Phần hợp đồng phase-by-bits lấy từ verifier tham chiếu theo Apache-2.0, xem [src/LICENSE.txt](../../LICENSE.txt). Verifier gốc giữ nguyên.

## Phần tinh chỉnh và lý do

**Đỉnh qubit của INV-41.** Mạch INV-41 dùng 164 qubit, đỉnh nằm ở phép nhân `P = T(t·r1)`. Lúc đó cùng sống: `x` 22, cờ chuẩn hóa 5, `y` (đang giữ `c0`) 30, `c1`/`r1` 21, `c2` 12, scratch AND 23, `P` 23, tổng 136 qubit cố định, cộng carry tạm của bộ cộng. Đo trực tiếp trên kickmix 1.0.0: `iadd` trên n bit mượn khoảng n − 2 qubit tạm làm carry (30 bit: 29 Toffoli, 88 qubit tính cả 60 dây dữ liệu).

**Hai quan sát dẫn tới tinh chỉnh.**

1. `c0` chỉ được dùng ở phép trừ cuối `y = c0 − P`, nhưng INV-41 nạp `c0` cùng `c1`, `c2` ngay sau chuẩn hóa. Như vậy 30 qubit nằm không suốt bước giảm `c1` và phép nhân.
2. `CircuitBuilder.set_max_qubits` của kickmix làm `iadd` tự chọn biến thể ít carry tạm hơn khi số qubit tự do bị giới hạn. Đo trên phép cộng 30 bit: giới hạn 88 → 29 Toffoli; 75 → 42; 64 → 53; 60 (không còn qubit tự do) → 57. Lookup và `multi_controlled_x` không đổi theo giới hạn. Áp riêng giới hạn 149 lên INV-41 đã cho Q = 149, 2.306 Toffoli, score ước tính 381.024 thay vì 405.278.

**Thay đổi.** (a) Tách bảng: `(c1, c2)` nạp sau chuẩn hóa như cũ; `c0` chỉ nạp vào `y` sau khi đã có `P` và đã giải phóng scratch, và được xóa bằng `del_lookup` ngay sau khi `y` trở lại `c0`, trước khi cấp lại scratch để uncompute `P`. (b) Thêm tham số `max_qubits` gọi `set_max_qubits` để bộ cộng dùng ít carry tạm ở các đoạn bị giới hạn.

**Phần giữ nguyên.** Bảng hệ số (kể cả bước cân `c0` từng đoạn), độ rộng, `fixed_point_model`, chuẩn hóa, giảm `c1`, nhân theo hàng, barrel shifter, áp pha và thứ tự uncompute đối xứng. Giá trị `y` và `y1` giống INV-41 từng bit với mọi x, nên sai số và chi phí phép quay không đổi.

## Cách thực hiện và đánh đổi

Thứ tự xuôi, ngược lại đối xứng:

1. Chuẩn hóa như INV-41.
2. `init_lookup` bảng `(c1, c2)` vào hai thanh ghi `c1`, `c2`.
3. Cấp scratch, `c1 −= T(t·c2)` → `r1`, như INV-41.
4. Cấp `P`, `P := T(t·r1)` theo hàng, như INV-41; giải phóng scratch.
5. `init_lookup` bảng `c0` vào `y` (30 qubit tại đúng chỗ scratch vừa trả), rồi `y −= P`. `P` có 23 bit; `isub` của kickmix mở rộng offset ngắn bằng số 0 (đã kiểm bằng mô phỏng), nên không cần đệm qubit như INV-41.
6. Dịch kết quả, áp pha, dịch ngược như INV-41.
7. `y += P`, `del_lookup` bảng `c0`, giải phóng `y`.
8. Cấp lại scratch, uncompute `P`, uncompute `r1` → `c1`, `del_lookup` bảng `(c1, c2)`, chuẩn hóa ngược.

Qubit cố định theo từng đoạn, chưa tính carry tạm: giảm `c1` 81; nhân 106; trừ 113; dịch kết quả và áp pha 123 (`x` 22, cờ 5, `y1` 40, `P` 23, `r1` 21, `c2` 12). Đoạn dịch kết quả trở thành sàn, nên giới hạn nhỏ hơn 123 không dựng được mạch; ở các đoạn trừ và nhân, giới hạn chỉ làm bộ cộng dùng ít carry tạm hơn.

Đánh đổi Toffoli so với INV-41 (2.220): thêm một lần tra bảng `c0` (126 + 18), phép trừ không đệm đắt hơn khoảng 4 mỗi chiều, và bộ cộng bị giới hạn đắt hơn khoảng 52. Không thêm phép quay.

Các biến thể đã dựng thử trước khi tạo Issue, mỗi biến thể lấy giới hạn qubit tốt nhất. Score là ước tính `Q × (Toffoli + T/4)` với biên sai số toàn miền của mô hình, cùng công thức của verifier:

| Biến thể | Q | Toffoli | Score ước tính |
| --- | ---: | ---: | ---: |
| INV-41 nguyên trạng | 164 | 2.220 | 405.278 |
| Chỉ thêm giới hạn qubit | 149 | 2.306 | 381.024 |
| Nạp `c0` sau `P` + giới hạn 123 (hướng này) | 123 | 2.424 | 329.051 |
| Như trên + tra `c2` riêng, xóa sau giảm `c1`, nạp lại khi uncompute | 111 | 2.712 | 328.916 |
| Nạp `c0` sau giảm `c1` nhưng trước phép nhân | 148 | 2.468 | 402.443 |
| Trừ thẳng từng hàng vào `y`, bỏ thanh ghi `P` | 148 | 2.612 | 423.755 |
| Cộng có điều khiển thay cho AND + scratch | 111–123 | 3.174–3.462 | ≥ 412.166 |

Bỏ `P` hoặc scratch đều không lợi vì bộ cộng của kickmix rẻ nhất khi offset dài bằng đoạn đích: trừ thẳng vào `y` 30 bit phải mang borrow lên tới bit cao nhất, còn `iadd` có điều khiển 21 bit tốn 45 Toffoli so với 41 của AND + cộng. Tra và xóa `c2` riêng giảm 12 qubit nhưng tốn thêm 288 Toffoli, gần như hòa, nên không dùng để giữ mạch đơn giản.

Mạch nháp với config đề xuất đã qua `validate_model.py`: pha khớp mô hình trên 3.104 đầu vào biên và ngẫu nhiên với 3 seed đo, x được phục hồi, scratch sạch. Một lần chạy thử dev harness trên artifact nháp cho PASS, 123 qubit, 2.424 Toffoli trung bình mỗi shot bằng đúng số tĩnh. Các số này chưa phải run của ID này; bước 03 dựng lại và ghi provenance.

**Config đầu tiên.** [base.json](configs/base.json): giữ nguyên độ rộng của INV-41 (a = 6, wy = 29, wc1 = 28, wc2 = 25, d0 = 15, d1 = 13, phase_drop_bits = 1) và thêm `max_qubits` = 123. Lý do: 123 là sàn của cấu trúc mới (thấp hơn thì không dựng được), và khi quét giới hạn từ 123 tới 143 trên mạch dựng thật, Q × C nhỏ nhất ở đúng 123. Tìm kiếm tọa độ trên các độ rộng, với mỗi điểm tự chọn giới hạn tốt nhất, không tìm được bộ nào tốt hơn bộ của INV-41. Chỉ cần một config vì đã có run đối chứng INV-41 cùng môi trường; việc tách riêng tác dụng của giới hạn qubit đã có ở bảng trên.

**Giả định cần giữ.** Hành vi của `set_max_qubits` và chi phí bộ cộng thuộc kickmix 1.0.0 đã pin trong `requirements.txt`. Nếu giới hạn thấp hơn sàn thì việc dựng mạch báo lỗi, không sinh mạch sai.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: [INV-41 config base](../INV-41/configs/base.json) tại `78674187c2daa4dbc34b6052f91b733d6760a0f7`, run dev [20261110T033017Z-local-dev_5min-856cb8](../../../results/invsqrt/INV-41/base/dev_5min/20261110T033017Z-local-dev_5min-856cb8/verifier.json): PASS, Q = 164, 2.220 Toffoli, score 404.024,71. Cùng máy, Python 3.13.9, cùng hash dev harness và verifier, nên so trực tiếp được với run dev của hướng này.
- Dự đoán: Q giảm từ 164 xuống 123, Toffoli tăng từ 2.220 lên khoảng 2.424, phép quay và sai số không đổi. Score dev khoảng 328.000, giảm khoảng 19%.
- Ủng hộ / bác bỏ: ủng hộ nếu dev_5min PASS và score dev không quá 383.823 (thấp hơn mốc INV-41 ít nhất 5%). Bác bỏ nếu mô hình hoặc mô phỏng không khớp INV-41 từng bit, nếu FAIL, hoặc nếu score cao hơn ngưỡng đó. Chỉ có BUILT thì chưa đủ bằng chứng.
- Điều kiện dừng: tối đa 3 vòng chỉnh giới hạn qubit hoặc độ rộng. Muốn hạ thêm sàn 123 phải đổi những gì sống trong đoạn dịch kết quả (`P`, `r1`, `c2`), thuộc hypothesis khác.
- Kiểm tra ứng viên cuối: chạy mode full (64 shot mỗi x trên toàn miền) cho config cuối. Dev chỉ thấy sai số xấu nhất 0,784 thay vì 0,9308 của toàn miền, nên score full dự kiến cao hơn dev khoảng 0,3%.

## Kết luận và phiên bản tái lập

Chưa có results. Điền sau khi chấm local ở bước 04.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa có | Chưa có | Chưa chấm |
| Full | Chưa có | Chưa có | Chưa chấm |

Mã triển khai: [solution.py](solution.py). Cấu hình: [configs](configs/).
Điểm và các run: [SCORES.md](../SCORES.md).
