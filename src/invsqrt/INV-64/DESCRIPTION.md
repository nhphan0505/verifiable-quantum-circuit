# [INV-64] Bỏ một bit pha thấp và cân lại hệ số bảng bậc hai INV-41, giữ nguyên 128 đoạn và số học

Loại: Tinh chỉnh một phương án.

## File gốc

Kế thừa [solution.py](../INV-41/solution.py), [base.json](../INV-41/configs/base.json) và [DESCRIPTION.md](../INV-41/DESCRIPTION.md) của INV-41 tại commit `a6ec810060d35d1fb53cc86c1cc0e8f0db631241`. Đối chứng là [run full PASS của INV-41](../../../results/invsqrt/INV-41/base/full/20261113T184751Z-local-full-2b9b2f/verifier.json): score 405278.3711389368, Q=164. Nguồn thuật toán và giấy phép kế thừa giữ nguyên theo INV-41.

## Phần tinh chỉnh và lý do

INV-41 áp pha trong `_phase()` từ các bit của `y1`, sau khi bỏ `phase_drop_bits=1` bit thấp. Verifier tính chi phí của các phép quay generic từ biên sai số tuyệt đối nhỏ nhất trên toàn miền. Chỉ tăng `phase_drop_bits` lên 2 khiến biên mô hình giảm từ khoảng 3.008e-12 xuống 1.023e-12 vòng; lợi ích bỏ một phép quay có thể bị chi phí tổng hợp các phép quay còn lại triệt tiêu. Giả thuyết là cân lại hệ số nguyên của một hàng bảng đang giới hạn biên sẽ vừa bỏ được một phép quay vừa giữ biên toàn miền đủ lớn để giảm score.

## Cách thực hiện và đánh đổi

Giữ nguyên 128 đoạn tra bảng, thuật toán `y = c0 - T(t (c1 - T(t c2)))`, các độ rộng `wy=29, wc1=28, wc2=25, d0=15, d1=13`, chuẩn hóa, dịch kết quả và uncompute của INV-41. Trong `coefficient_table()`, tạo bảng bằng nội suy Chebyshev và cân `c0` theo từng đoạn như nguồn gốc. Sau bước cân, áp offset nguyên từ JSON lên hàng `index=0`: `c0 -= 3`, `c1 += 2`, `c2 += 1`. Các offset ở đơn vị integer của word tương ứng, nghĩa là các bước `2^-29`, `2^-28`, `2^-25` trước khi nhân/cắt cụt. Không đổi scale, địa chỉ, số bit hoặc phép tính bảng ở các hàng còn lại. `init_lookup()` sử dụng bảng sau offset cho cả chiều compute và uncompute, do đó không thêm thanh ghi và cần xác minh scratch trả về 0.

Đặt `phase_drop_bits=2` trong JSON; `_phase()` chỉ phát `Z_POW` cho `j>=2`, bỏ phép quay ở `j=1` cùng với bit 0 đã bỏ từ trước. Mô hình trong `_evaluate()` phải dùng đúng `y1_masked = (y1 >> 2) << 2`. Mỗi phép nhân `T` giữ quy tắc bỏ các partial-product row dưới LSB của thanh ghi đích; không thay đổi làm tròn/cắt cụt. Vì offset có thể dịch `r1` và `y`, phải kiểm tra không âm và không tràn theo mọi `x=1..3,133,452`; kiểm tra cả đầu/cuối mỗi đoạn bảng, các giá trị gần biên và miền `x=1`. Tiêu chí pha là `abs(y1_masked / 2^(wy+n_p) - 1/sqrt(x)) < 2^-24 / sqrt(x)`.

Quét mô hình fixed-point của INV-41 trên toàn miền với ứng viên này cho sai số tương đối lớn nhất khoảng 0.898786 lần dung sai, biên tuyệt đối nhỏ nhất khoảng 4.110e-12 vòng, và các độ rộng word không tăng. Theo công thức điểm verifier với 34 thay vì 35 phép quay, Q=164 và 2220 Toffoli giữ nguyên, score ước tính 403718.36. Đây là kết quả mô hình, chưa phải mạch đã build hay verifier PASS. Config đầu tiên là [phase2_row0.json](configs/phase2_row0.json) với đúng offset và số bit trên để kiểm định giả thuyết, chưa khẳng định tối ưu. Offset có thể làm thay đổi pha ở điểm biên và đường HMR cần kiểm bằng mạch thật.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: [source](../INV-41/solution.py), [config](../INV-41/configs/base.json) INV-41 ở commit trên và [run full PASS](../../../results/invsqrt/INV-41/base/full/20261113T184751Z-local-full-2b9b2f/verifier.json) nêu trên; score 405278.3711389368. Môi trường, hash verifier và profile của run lịch sử cần nêu khi so kết quả mới.
- Dự đoán: Q và số Toffoli giữ nguyên, generic rotations giảm từ 35 xuống 34; biên sai số toàn miền tăng so với config chỉ bỏ thêm bit. Score full thấp hơn đối chứng nếu mạch khớp mô hình.
- Ủng hộ / bác bỏ: mô hình toàn miền không tràn và sai số dưới dung sai; mạch smoke rồi full PASS, phục hồi `x`, scratch sạch, score full dưới 405278.3711389368. Bác bỏ nếu sai pha/cleanup, biên không dương hoặc score không giảm. Chỉ có artifact BUILT thì chưa đủ bằng chứng.
- Điều kiện dừng: tối đa hai config trong cùng phạm vi offset bảng và bit pha thấp. Nếu không có lợi ích, giữ kết quả âm; không đổi thuật toán số học hay hướng phát sinh mạch.
- Kiểm tra ứng viên cuối: kiểm tra độc lập điểm biên của 128 đoạn và nhiều seed HMR; dùng full của verifier gốc. Smoke/BUILT không thay thế full.

## Kết luận và phiên bản tái lập

Chưa build hoặc chấm. Sẽ ghi config, SHA nguồn, provenance và run sau khi có kết quả.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa có | Chưa có | Chưa chấm |
| Full | Chưa có | Chưa có | Chưa chấm |

Mã triển khai: [solution.py](solution.py). Cấu hình: [phase2_row0.json](configs/phase2_row0.json).
