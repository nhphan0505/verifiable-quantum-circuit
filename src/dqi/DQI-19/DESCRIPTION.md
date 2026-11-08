# [DQI-19] Thay bộ nhân GF(2^12) bằng bilinear rank 42 và xóa tích tạm bằng đo X, giữ decoder EEA baseline

Loại: Tinh chỉnh một phương án.

## File gốc

Kế thừa decoder, giao diện và số vòng EEA từ [baseline](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/e3827988aee8bd7731bbdcf6c5376cd2d5413aa5/src/dqi/DQI-BASELINE/solution.py), commit `e3827988aee8bd7731bbdcf6c5376cd2d5413aa5`; Apache-2.0, src/LICENSE.txt. Giữ verifier gốc, không sửa hạ tầng.

## Phần tinh chỉnh và lý do

Thay hai call site `ixor_gf2_mul` trong `_multiply_and_add_or_sub` bằng bộ nhân bilinear rank 42 tự dựng, với product tạm xóa bằng đo X và sửa pha CZ. Giữ các primitive inverse/division/scaffold và phase-by-product bên trong Kickmix; không tuyên bố thay toàn bộ phép nhân nội bộ thư viện. Giữ EEA 222 vòng, Chien/Forney, field basis và giao diện syndrome/mask của baseline.

Căn cứ MBU: [note Optimized DQI](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/e3827988aee8bd7731bbdcf6c5376cd2d5413aa5/research/dqi/papers/arxiv-2510.10967/note.md), II.C/C.3: pha Hadamard là tích vô hướng bit, không phải Hamming distance. [Note discussion](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/e3827988aee8bd7731bbdcf6c5376cd2d5413aa5/research/shared/discussions/kaggle-752897-verifier-in-the-loop/note.md) chỉ báo mốc rank 42 chưa xác minh. Phân rã dưới đây được tự suy luận; kết quả kiểm tra decoder nằm trong phần kết luận. Note arxiv-2610.22367 có cảnh báo nội dung review chưa nhất quán nên không dùng làm tiền đề triển khai.

## Cách thực hiện và đánh đổi

Dùng GF(8)=GF(2)[u]/(u^3+u+1). Trong GF(4096) đúng modulus Kickmix, tìm root beta của u^3+u+1 và chọn t sao cho 12 vector beta^i*t^j (0<=i<3,0<=j<4) độc lập trên GF(2). Đổi cơ sở nhị phân sang bốn hệ số GF(8). Đánh giá hai đa thức bậc <=3 tại bảy điểm 0..6 của GF(8), nhân từng cặp, rồi nội suy Vandermonde 7x7 để lấy tích bậc <=6. Ánh xạ hệ số về GF(4096) bằng beta^i*t^j, bao gồm reduction modulo field polynomial.

Mỗi nhân GF(8) dùng sáu AND nhị phân: d_i=a_i*b_i (i=0,1,2), s_ij=(a_i+a_j)*(b_i+b_j) (i<j). Cross term a_i*b_j+a_j*b_i=s_ij+d_i+d_j; reduction theo u^3=u+1. Gộp mọi map tuyến tính thu được 42 bộ mask (l_k,r_k,p_k) với xy=XOR_k p_k*(parity(l_k&x) AND parity(r_k&y)). Kiểm chứng tensor trên đủ 144 cặp basis; do bilinear đây là chứng minh trên mọi x,y. Không cần tin mốc rank của discussion.

Tính parity đầu vào bằng CX vào hai scratch qubit; init_and vào scratch thứ ba, XOR qua mask p_k vào product 12 qubit, del_and rồi đảo parity. Compute product dùng 42 Toffoli-like. Accumulate vào target không giả thiết target=0: CX nếu không control, CCX từng bit nếu control lượng tử (thêm 12 Toffoli). Đo X/reset 12 bit product, được c; với mỗi k bù CZ giữa hai parity đầu vào khi parity(c&p_k)=1. Pha cần bù là (-1)^(c dot xy); mọi scratch/input được khôi phục. Phép del_and cũng tự bù pha riêng. Không có rounding, truncation hoặc sai số chủ động.

Đánh đổi: thêm product/scratch qubit, CNOT và CZ; giảm Toffoli của multiply-add có điều khiển từ số đo primitive local 75 xuống dự kiến 54, nhưng Q^2 và thời gian simulator có thể tăng. Đếm này chỉ cho primitive, chưa phải chi phí toàn decoder. Config đầu tiên [rank42.json](configs/rank42.json) giữ m=4095,n=70,degree=12 để tách tác động bộ nhân; không quét tham số. `solution.py` tự suy ra TRACK/ID và kiểm tra config nằm trực tiếp trong configs/ sau resolve. Để dựng: `python src/dqi/DQI-19/solution.py --config src/dqi/DQI-19/configs/rank42.json`. Dùng Python 3.13 trong .venv và dependency đã pin.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: source baseline commit nêu trên, configs/baseline.json (4095,70,12); run dev `results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5`. Chỉ tính gain nếu profile/seed/shots, môi trường và hash verifier/harness tương thích; nếu thiếu thì chấm đối chứng mới hoặc để trống gain.
- Dự đoán: kernel nhân có điều khiển giảm T; Q và Clifford tăng. Chưa biết score tổng R(epsilon_plus)*Q^2*T.
- Ủng hộ: tensor chính xác, test primitive giữ value/phase/workspace và dev_5min 4096 shots PASS với phase_errors=0, T trung bình giảm so đối chứng tương thích; score giảm mới ủng hộ lợi ích end-to-end. Bác bỏ nếu tensor sai, xuất hiện phase/value/workspace errors, hoặc T không giảm. Timeout chỉ cho biết giới hạn runtime, không chứng minh sai mạch.
- Điều kiện dừng: một config ứng viên ban đầu; không quét hàng loạt. Dừng build nếu tensor sai, API không hỗ trợ MBU đúng hoặc tài nguyên vượt khả năng local; không đổi hypothesis ngầm.
- Kiểm tra ứng viên cuối: syndrome 0, trọng số 1/35, seed chưa dùng chọn config hoặc full; đối chứng cùng profile. Thành viên tự chấm notebook local; agent dừng sau artifact BUILT và provenance.

## Kết luận và phiên bản tái lập

Config `rank42` đã đạt **dev_5min PASS**, profile v1, seed 20261106, 4096 shots; không phát hiện lỗi giá trị hoặc pha. T trung bình/shot là 5044549.798095703, Q=1893, epsilon_plus=0.021427937912299865, hệ số lặp=2.9847755992784792. Kết quả dev này xác nhận phần đúng trên mẫu dev của hypothesis; full bổ sung được ghi bên dưới. [Run gốc](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/verifier.json), [provenance](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/provenance.json), [đối chiếu bằng chứng](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/review.json). Score chính xác nằm tại run gốc và bảng SCORES.

Run khớp duy nhất với build qua SHA-256 `ae5d79c2ade1f04ce5937581fae10bbb14f5cd992224c6c202c0b976f6d28627`, source commit `9918ac4f0cc2ae695180bc93ef1d1bf99613d168`. [Build provenance](../../../results/dqi/DQI-19/rank42/build_only/20261108T110144Z-local-build/provenance.json) ghi môi trường/hash; artifact 1143210844 bytes, 5044893 Toffoli-like đếm tĩnh. Đếm tĩnh khác T trung bình thực thi/shot. Giữ nguyên source/config và mọi JSON/log run gốc.

Primitive rank-42 có điều khiển dùng 54 Toffoli-like và 52 qubit, so với native 75 và 49 ở cùng môi trường kiểm tra kernel. Tensor khớp đủ 144 cặp basis; mạch kernel được kiểm tra exhaustive đủ 2^24 cặp toán hạng với cả hai control (33554432 trường hợp, seed HMR 1901), sampled bổ sung seed 1901/1902/1903; không phát hiện lỗi giá trị/pha/workspace. [Kernel validation](../../../results/dqi/DQI-19/rank42/build_only/20261108T110144Z-local-build/kernel_validation.json). Parity scratch cập nhật theo XOR hiệu hai mask, rồi đảo mạng tuyến tính để dọn scratch.

Run **full PASS** dùng verifier chính thức/default với 102400 shots, không lỗi giá trị/pha; T trung bình/shot 5044541.83546875, Q=1893, epsilon_plus=0.0008660587301657926, hệ số lặp=1.1912604648115832. [Full run](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/verifier.json), [provenance](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/provenance.json), [đối chiếu](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/review.json). Hash artifact/source/config khớp cùng build với dev. Đây là kiểm chứng thống kê chính thức bổ sung, không phải chứng minh trên mọi syndrome.

Giới hạn so sánh: đối chứng lịch sử dùng Python 3.13.14, ứng viên dùng 3.13.7; riêng dev, hash harness cũng khác (`cafdade408fda55072d7f305b0e9ad755636b59c5c3430b901e59e47e38ff242` so với `33402313455f76532bf856a6814702e89e5a9b30982cf49ff56321b1086d6d1c`). Chưa có đối chứng cùng môi trường để xác nhận cải thiện T/score toàn decoder. Cột hệ số cải thiện đã kiểm chứng giữ `—`; vẫn hiển thị tỷ số số học lịch sử trong ô dẫn run theo yêu cầu người dùng: dev `61234661450380.1 / 53955451017897.38 = 1.134911492632471...`, full `24439463583672.93 / 21534246734876.543 = 1.134911468442086...`; cả hai làm tròn **1.1349×**. Hai tỷ số này không được trình bày như cải thiện đã kiểm chứng trong môi trường tương thích. Không sửa metadata, run cũ hoặc checker để hợp thức hóa so sánh.

Đánh đổi quan sát được: Q cực đại 1893, bằng con số Q lịch sử; mạng CNOT/HMR/classical feedback và artifact lớn hơn vẫn là chi phí cần cân nhắc. Đề xuất giữ nguyên config, chấm lại baseline bằng cùng .venv/harness/verifier/profile rồi mới điền cột cải thiện chính thức. Chưa triển khai hoặc tự chấm vòng mới, chưa merge. Full đã bổ sung bằng chứng đúng nhưng chưa giải quyết giới hạn đối chứng hiệu năng.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | [rank42](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/9918ac4f0cc2ae695180bc93ef1d1bf99613d168/src/dqi/DQI-19/configs/rank42.json) | `9918ac4f0cc2ae695180bc93ef1d1bf99613d168` | [run](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/verifier.json), [provenance](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/provenance.json) |
| Full | [rank42](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/9918ac4f0cc2ae695180bc93ef1d1bf99613d168/src/dqi/DQI-19/configs/rank42.json) | `9918ac4f0cc2ae695180bc93ef1d1bf99613d168` | [run](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/verifier.json), [provenance](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/provenance.json) |

Tái lập source/config bằng `git show 9918ac4f0cc2ae695180bc93ef1d1bf99613d168:src/dqi/DQI-19/solution.py` và config tại commit cùng SHA. Mã triển khai: [solution.py](solution.py). Điểm: [SCORES.md](../SCORES.md).
