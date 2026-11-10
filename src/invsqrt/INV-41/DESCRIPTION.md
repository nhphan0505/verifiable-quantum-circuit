# [INV-41] Thay Horner bậc ba và bước Newton bằng tra bảng 128 đoạn đa thức bậc hai, chuẩn hóa và dịch kết quả bằng barrel shifter nhị phân

Loại: Ý tưởng mới.

## Thuật toán và công thức

**Bài toán.** Với mọi x từ 1 đến 3.133.452 trong thanh ghi `x` 22 qubit, áp pha exp(2πi/√x), phục hồi x, đưa scratch về 0, với sai số pha dưới 2⁻²⁴/√x vòng. Điểm là Q × (Toffoli + T/4).

**Lý do chọn hướng.** [Baseline](../INV-BASELINE/solution.py) tốn phần lớn Toffoli ở ba phép nhân rộng 28–30 bit của bước Newton (`_square`, `_multiply_m`, `_multiply_y0`). Nếu một bảng đủ dày giúp đa thức bậc hai đạt thẳng độ chính xác yêu cầu thì có thể bỏ cả ba, chỉ còn hai phép nhân hẹp hơn. Hướng này tự suy luận từ verifier và baseline; các note [mrmeows v3](../../../research/shared/discussions/kaggle-mrmeows-open-circuits-v3/note.md) và [portfolio v11](../../../research/shared/discussions/kaggle-vqcc-own-circuit-portfolio/note.md) cho biết kiến trúc bảng cộng Horner bậc hai từng được nhóm khác dùng, nhưng note không có đủ chi tiết để tái lập và hướng này không mở notebook gốc.

**Kế thừa từ các hướng trước của nhóm.** Từ [INV-6](../INV-6/DESCRIPTION.md): ý tưởng bù thiên lệch cắt cụt bằng số nguyên trong bảng hệ số, ở đây áp dụng riêng cho `c0` của từng đoạn. Từ [baseline](../INV-BASELINE/solution.py): cách cộng từng hàng qua scratch AND, cắt cụt từng hàng và áp pha theo bit. Từ INV-6: khuôn kiểm tra `validate_model.py`. Lịch cấp phát theo giai đoạn của [INV-3](../INV-3/DESCRIPTION.md) chưa áp dụng ở đây và để cho hướng rút ngắn vòng đời thanh ghi.

**Tham số.** `a = address_bits` (bit mantissa dùng làm địa chỉ), `wy`, `wc1`, `wc2` (số bit phân của `c0`/`y`, `c1`/`r1`, `c2`), `d0`, `d1` (số bit cao của `t` dùng trong hai phép nhân), `phase_drop_bits` (số bit thấp của `y1` không áp Z_POW). D = 21 − a là số bit của `t`.

**Các bước.** T(·) cắt từng hàng partial product dưới LSB của thanh ghi đích.

1. *Chuẩn hóa.* Năm tầng k = 4, 3, 2, 1, 0. Tầng k tính cờ S_k = "2^k bit cao của x đều bằng 0" bằng `multi_controlled_x` (2^k − 1 Toffoli, tầng k = 0 là Clifford), rồi nếu S_k bằng 1 thì dịch trái x đi 2^k bit bằng chuỗi `cswap` chỉ trên 22 − 2^k bit còn sống. Kết quả x_norm = x·2^S có bit 21 bằng 1, tức M = x_norm/2²¹ ∈ [1, 2), và x = M·2^E với E = 21 − S.
2. *Tra bảng.* Địa chỉ gồm a bit ngay dưới bit dẫn đầu (bit 20 đến 21 − a) và S_0. S_0 = 1 tương ứng E chẵn. `init_lookup` nạp một lần ba hệ số vào ba thanh ghi `y`, `c1`, `c2`. Hệ số của đoạn m được nội suy tại ba mốc Chebyshev trên t ∈ [0, 1) của hàm g(t) = f·(1 + (m + t)·2⁻ᵃ)^(−1/2), với f = 1 khi E chẵn và f = 2^(−1/2) khi E lẻ, viết dưới dạng c0 − c1·t + c2·t².
3. *Tính giá trị.* `t` = D bit thấp của x_norm. Tính tại chỗ `r1 = c1 − T(t[d1 bit cao]·c2)`, tính ra thanh ghi mới `P = T(t[d0 bit cao]·r1)`, các hàng thấp cộng trước để mỗi hàng chỉ phải truyền carry qua ít bit hơn, rồi `y = c0 − P`.
4. *Dịch kết quả.* y1 = y·2^(S>>1) trên 40 dây, bốn tầng `cswap` điều khiển bởi S_1..S_4 với lượng dịch 1, 2, 4, 8. Vì S ≤ 21, tầng 8 và tầng 4 loại trừ nhau, nên số bit sống của các tầng lần lượt là 30, 31, 33, 32.
5. *Áp pha.* Bit j của y1 nhận Z_POW 2^(j−39) vòng, bỏ `phase_drop_bits` bit thấp nhất và bit trọng số 1 vòng. Sau đó uncompute đối xứng toàn bộ, `del_lookup` để xóa bảng.

**Cân sai số từng đoạn.** Sau khi làm tròn hệ số, chạy `fixed_point_model` trên mọi x của từng đoạn, lấy trung điểm của sai số tương đối nhỏ nhất và lớn nhất, rồi dịch `c0` của đoạn đó một số nguyên để đưa trung điểm về 0. Vì `c0` là hằng trong bảng nên việc này không tốn Toffoli và bù được phần lệch do cắt cụt.

**Config đầu tiên.** [base.json](configs/base.json): a = 6, wy = 29, wc1 = 28, wc2 = 25, d0 = 15, d1 = 13, phase_drop_bits = 1. Cách chọn: xuất phát từ bộ độ rộng nhỏ nhất mà mô hình toàn miền cho sai số dưới 0,95 lần dung sai, rồi tìm kiếm tọa độ, mỗi lần đổi một tham số ±1 và dựng mạch thật để đo Q, Toffoli và biên sai số. Chỉ nhận bộ có sai số xấu nhất dưới 0,95 lần dung sai, và chọn bộ có Q × C dự kiến nhỏ nhất. Ngưỡng 0,95 là biên an toàn đặt trước; phần biên còn lại cũng là phần verifier dùng để định giá phép quay, nên biên quá sát 0 sẽ làm điểm xấu đi. Một config là đủ để kiểm hypothesis vì đã có run đối chứng baseline cùng profile; không thêm config đối chứng.

## Điều kiện đúng và sai số

- **Miền.** Mọi x từ 1 đến 3.133.452. x = 0 nằm ngoài hợp đồng. x_norm luôn có bit 21 bằng 1.
- **Sai số xấp xỉ.** Đa thức bậc hai trên 128 đoạn có sai số tương đối khoảng 0,612 lần 2⁻²⁴, phần còn lại dành cho làm tròn hệ số, cắt cụt từng hàng và bỏ bit pha.
- **Mô hình khớp từng bit.** `fixed_point_model` tái hiện đúng phép cắt cụt theo hàng và báo lỗi nếu `r1` âm hoặc `y` vượt độ rộng. [validate_model.py](validate_model.py) kiểm tra toàn miền với ngưỡng 0,95 lần dung sai, rồi so pha của mạch thật với mô hình trên các đầu vào biên và ngẫu nhiên.
- **Phục hồi và làm sạch.** Mọi bước được đảo đúng thứ tự. Cờ S_k được tính lại trên x đã dịch ngược. Các tích AND trong từng hàng xóa bằng `del_and`, bảng xóa bằng `del_lookup`, nên có phép đo; do đó phải thử nhiều seed đo.
- **Giả định `_denormalize`.** Việc giới hạn số bit sống dựa trên S ≤ 21 với x ≥ 1. Giả định này được kiểm bằng so khớp pha trên mạch.
- **Biên sai số và phép quay.** Verifier định giá phép quay từ biên tuyệt đối nhỏ nhất min_x(tol(x) − |error(x)|). Biên càng hẹp thì mỗi phép quay càng đắt.

## Tài nguyên dự kiến

Số đo của config `base` từ mô hình toàn miền và một mạch dựng thử trên máy trước khi tạo Issue. Đây chưa phải điểm chấm; bước 03 dựng lại và ghi provenance dưới ID này.

| Đại lượng | Baseline | Hướng này (dự kiến) |
| --- | ---: | ---: |
| Qubit | 260 | 164 |
| Toffoli | 7.735 | 2.220 |
| Phép quay bậc cao | 37 | 35 |
| Sai số xấu nhất / dung sai trên toàn miền | 0,477 | 0,931 |

Phân bổ Toffoli theo khối, xuôi và ngược: chuẩn hóa 105 + 105; tra bảng 126 + 18; giảm `c1` khoảng 358 + 358; nhân `t·r1` khoảng 420 + 420; trừ `y` 29 + 29; dịch kết quả 126 + 126.

Tác động lên điểm dự kiến: score khoảng 405.000, tức khoảng 5,1 lần so với baseline. Đây là dự đoán từ công thức của verifier, không phải kết quả đã chấm. Đỉnh 164 qubit gồm nhiều thanh ghi sống cùng lúc; rút ngắn vòng đời của chúng thuộc một hướng khác.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: [INV-BASELINE/solution.py](../INV-BASELINE/solution.py) và [baseline.json](../INV-BASELINE/configs/baseline.json) tại commit `c4d8b66974ee7bc958d9adf7a1505eac3e7b249e`; run dev [20261107T180810Z-local-dev_5min-eb9c85](../../../results/invsqrt/INV-BASELINE/baseline/dev_5min/20261107T180810Z-local-dev_5min-eb9c85/verifier.json), profile seed 20261106, 4096 mẫu × 2 lần. Mốc tốt nhất hiện có của nhóm là dev 1.809.545 của [INV-3](../INV-3/DESCRIPTION.md), config `pebble_square`.
- Dự đoán: Q giảm từ 260 xuống khoảng 164, Toffoli giảm từ 7.735 xuống khoảng 2.220. Đổi lại biên sai số hẹp hơn nên mỗi phép quay đắt hơn.
- Ủng hộ / bác bỏ: ủng hộ nếu dev_5min PASS và score thấp hơn 1.809.545. Bác bỏ nếu mô hình tràn hoặc sai số từ 0,95 lần dung sai trở lên, nếu FAIL, hoặc nếu score không thấp hơn mốc đó. Mới có BUILT hoặc smoke thì chưa đủ bằng chứng.
- Điều kiện dừng: tối đa 3 vòng chỉnh độ rộng trong hướng này. Đổi vòng đời thanh ghi hoặc cách uncompute thuộc hướng khác.
- Kiểm tra ứng viên cuối: chạy verifier gốc ở mode full, đủ 64 shot mỗi x trên toàn miền. Bộ dev_5min chỉ có 8.192 shot và có thể không gặp x có sai số xấu nhất, nên score dev có thể thấp hơn score full một chút.

## Kết luận và phiên bản tái lập

Chưa có results. Điền sau khi chấm local ở bước 04.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa có | Chưa có | Chưa chấm |
| Full | Chưa có | Chưa có | Chưa chấm |

Mã triển khai: [solution.py](solution.py). Cấu hình: [configs](configs/).
Điểm và các run: [SCORES.md](../SCORES.md).
