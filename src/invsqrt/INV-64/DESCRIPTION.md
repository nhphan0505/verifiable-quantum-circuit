# [INV-64] Bỏ một bit pha thấp và cân lại hệ số bảng bậc hai INV-41, giữ nguyên 128 đoạn và số học

Loại: Tinh chỉnh một phương án.

## File gốc

Kế thừa [solution.py](../INV-41/solution.py), [base.json](../INV-41/configs/base.json) và [DESCRIPTION.md](../INV-41/DESCRIPTION.md) của INV-41 tại commit `a6ec810060d35d1fb53cc86c1cc0e8f0db631241`. Đối chứng là [run full PASS của INV-41](../../../results/invsqrt/INV-41/base/full/20261113T184751Z-local-full-2b9b2f/verifier.json): score 405278.3711389368, Q=164. Nguồn thuật toán và giấy phép kế thừa giữ nguyên theo INV-41.

## Phần tinh chỉnh và lý do

INV-41 áp pha trong `_phase()` từ các bit của `y1`, sau khi bỏ `phase_drop_bits=1` bit thấp. Verifier tính chi phí của các phép quay generic từ biên sai số tuyệt đối nhỏ nhất trên toàn miền. Chỉ tăng `phase_drop_bits` lên 2 khiến biên mô hình giảm từ khoảng 3.008e-12 xuống 1.023e-12 vòng; lợi ích bỏ một phép quay có thể bị chi phí tổng hợp các phép quay còn lại triệt tiêu. Giả thuyết là cân lại hệ số nguyên của một hàng bảng đang giới hạn biên sẽ vừa bỏ được một phép quay vừa giữ biên toàn miền đủ lớn để giảm score.

## Cách thực hiện và đánh đổi

Giữ nguyên 128 đoạn tra bảng, thuật toán `y = c0 - T(t (c1 - T(t c2)))`, các độ rộng `wy=29, wc1=28, wc2=25, d0=15, d1=13`, chuẩn hóa, dịch kết quả và uncompute của INV-41. Trong `coefficient_table()`, tạo bảng bằng nội suy Chebyshev và cân `c0` theo từng đoạn như nguồn gốc. Sau bước cân, áp offset nguyên từ JSON lên hàng `index=0`: `c0 -= 3`, `c1 += 2`, `c2 += 1`. Các offset ở đơn vị integer của word tương ứng, nghĩa là các bước `2^-29`, `2^-28`, `2^-25` trước khi nhân/cắt cụt. Không đổi scale, địa chỉ, số bit hoặc phép tính bảng ở các hàng còn lại. `init_lookup()` sử dụng bảng sau offset cho cả chiều compute và uncompute, do đó không thêm thanh ghi và cần xác minh scratch trả về 0.

Đặt `phase_drop_bits=2` trong JSON; `_phase()` chỉ phát `Z_POW` cho `j>=2`, bỏ phép quay ở `j=1` cùng với bit 0 đã bỏ từ trước. Mô hình trong `_evaluate()` phải dùng đúng `y1_masked = (y1 >> 2) << 2`. Mỗi phép nhân `T` giữ quy tắc bỏ các partial-product row dưới LSB của thanh ghi đích; không thay đổi làm tròn/cắt cụt. Vì offset có thể dịch `r1` và `y`, phải kiểm tra không âm và không tràn theo mọi `x=1..3,133,452`; kiểm tra cả đầu/cuối mỗi đoạn bảng, các giá trị gần biên và miền `x=1`. Tiêu chí pha là `abs(y1_masked / 2^(wy+n_p) - 1/sqrt(x)) < 2^-24 / sqrt(x)`.

Trước khi build/chấm, quét mô hình fixed-point của INV-41 trên toàn miền với ứng viên này cho sai số tương đối lớn nhất khoảng 0.898786 lần dung sai, biên tuyệt đối nhỏ nhất khoảng 4.110e-12 vòng, và các độ rộng word không tăng. Theo công thức điểm verifier với 34 thay vì 35 phép quay, Q=164 và 2220 Toffoli giữ nguyên, score ước tính 403718.36. Đây là dự đoán mô hình, không phải số đo tại thời điểm đặt hypothesis. Config đầu tiên là [phase2_row0.json](configs/phase2_row0.json) với đúng offset và số bit trên để kiểm định giả thuyết. Offset có thể làm thay đổi pha ở điểm biên và đường HMR cần kiểm bằng mạch thật.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: [source](../INV-41/solution.py), [config](../INV-41/configs/base.json) INV-41 ở commit trên và [run full PASS](../../../results/invsqrt/INV-41/base/full/20261113T184751Z-local-full-2b9b2f/verifier.json) nêu trên; score 405278.3711389368. Môi trường, hash verifier và profile của run lịch sử cần nêu khi so kết quả mới.
- Dự đoán: Q và số Toffoli giữ nguyên, generic rotations giảm từ 35 xuống 34; biên sai số toàn miền tăng so với config chỉ bỏ thêm bit. Score full thấp hơn đối chứng nếu mạch khớp mô hình.
- Ủng hộ / bác bỏ: mô hình toàn miền không tràn và sai số dưới dung sai; mạch smoke rồi full PASS, phục hồi `x`, scratch sạch, score full dưới 405278.3711389368. Bác bỏ nếu sai pha/cleanup, biên không dương hoặc score không giảm. Chỉ có artifact BUILT thì chưa đủ bằng chứng.
- Điều kiện dừng: tối đa hai config trong cùng phạm vi offset bảng và bit pha thấp. Nếu không có lợi ích, giữ kết quả âm; không đổi thuật toán số học hay hướng phát sinh mạch.
- Kiểm tra ứng viên cuối: kiểm tra độc lập điểm biên của 128 đoạn và nhiều seed HMR; dùng full của verifier gốc. Smoke/BUILT không thay thế full.

## Kết luận và phiên bản tái lập

Run [full INV-64](../../../results/invsqrt/INV-64/phase2_row0/full/20261114T144833Z-local-full-5929af/verifier.json) PASS với 200.540.928 shots, score `403718.3593824384`, 164 qubit, 2.220 Toffoli và 34 phép quay generic. Sai số lớn nhất bằng `0.8987860953092711` lần dung sai tại `x=2154475`; `rotation_eps=3.797698733857673e-13`. Hash mạch `aa89f2ff3a32b9ad6bbac476852e76c16227af2854f942e0ca0d90ee5a6339ed` khớp metadata, [provenance của run](../../../results/invsqrt/INV-64/phase2_row0/full/20261114T144833Z-local-full-5929af/provenance.json) và [build_only](../../../results/invsqrt/INV-64/phase2_row0/build_only/20261114T141430Z-local-build/provenance.json). Source/config của build là commit `22c4472510f6337a197c8a4019cbb0f31a82574e`; không suy ra từ HEAD hiện tại.

So với [full INV-41](../../../results/invsqrt/INV-41/base/full/20261113T184751Z-local-full-2b9b2f/verifier.json), score giảm `1560.0117564984` (`0.3849235%`), đúng chiều dự đoán và gần score mô hình. Q và Toffoli không đổi; rotations giảm 35 xuống 34, `rotation_eps` tăng từ `2.7002820506109133e-13` lên `3.797698733857673e-13`. Sai số tương đối xấu nhất giảm từ `0.9308138085034672` xuống `0.8987860953092711`. Kết quả ủng hộ hypothesis cải thiện score của INV-41; mức cải thiện nhỏ và vẫn cao hơn score full `80162.73214111096` của INV-51, nên dừng quét config của hướng này sau ứng viên đầu tiên.

Hai run full cùng dùng kickmix-engine 0.6.0, verifier invsqrt cùng SHA-256 `ddef520dec6b68d1cf0a6f328ddd36d79eb84570b9192cf3f7acaf073f06733a`, Python 3.13.18 và 200.540.928 shots, nhưng đối chứng chạy WSL2 Linux/AVX2 còn INV-64 chạy macOS/NEON. Không có run smoke/dev cho INV-64; full PASS đã kiểm miền chính thức, nhưng chưa làm kiểm tra độc lập nhiều seed HMR hoặc đối chiếu riêng các điểm biên bảng. Đây là giới hạn trước review cuối, không làm thay đổi điểm full đã ghi.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa có | Chưa có | Chưa chấm |
| Full | [phase2_row0.json](configs/phase2_row0.json) | `22c4472510f6337a197c8a4019cbb0f31a82574e` | [verifier](../../../results/invsqrt/INV-64/phase2_row0/full/20261114T144833Z-local-full-5929af/verifier.json), [provenance](../../../results/invsqrt/INV-64/phase2_row0/full/20261114T144833Z-local-full-5929af/provenance.json) |

Mã triển khai: [solution.py](solution.py). Cấu hình: [phase2_row0.json](configs/phase2_row0.json).
