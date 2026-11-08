# [DQI-19] Thay bộ nhân GF(2^12) bằng bilinear rank 42 và xóa tích tạm bằng đo X, giữ decoder EEA baseline

Loại: Tinh chỉnh một phương án.

## File gốc

Kế thừa decoder, giao diện và số vòng EEA từ [baseline](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/e3827988aee8bd7731bbdcf6c5376cd2d5413aa5/src/dqi/DQI-BASELINE/solution.py), commit `e3827988aee8bd7731bbdcf6c5376cd2d5413aa5`; Apache-2.0, src/LICENSE.txt. Giữ verifier gốc, không sửa hạ tầng.

## Phần tinh chỉnh và lý do

Thay hai call site `ixor_gf2_mul` trong `_multiply_and_add_or_sub` bằng bộ nhân bilinear rank 42 tự dựng, với product tạm xóa bằng đo X và sửa pha CZ. Giữ các primitive inverse/division/scaffold và phase-by-product bên trong Kickmix; không tuyên bố thay toàn bộ phép nhân nội bộ thư viện. Giữ EEA 222 vòng, Chien/Forney, field basis và giao diện syndrome/mask của baseline.

Căn cứ MBU: [note Optimized DQI](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/e3827988aee8bd7731bbdcf6c5376cd2d5413aa5/research/dqi/papers/arxiv-2510.10967/note.md), II.C/C.3: pha Hadamard là tích vô hướng bit, không phải Hamming distance. [Note discussion](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/e3827988aee8bd7731bbdcf6c5376cd2d5413aa5/research/shared/discussions/kaggle-752897-verifier-in-the-loop/note.md) chỉ báo mốc rank 42 chưa xác minh. Phân rã dưới đây được tự suy luận; chưa có số đo decoder ứng viên. Note arxiv-2610.22367 có cảnh báo nội dung review chưa nhất quán nên không dùng làm tiền đề triển khai.

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

Đã triển khai tensor và hai call site EEA trong [solution.py](solution.py), giữ nguyên thuật toán decoder còn lại. Parity scratch được cập nhật bằng XOR hiệu hai mask kế tiếp để giảm CNOT; mạng tuyến tính cuối được đảo để dọn scratch. Kết quả kiểm tra primitive sampled trên ba seed HMR độc lập và exhaustive đủ 2^24 cặp toán hạng với cả hai control không phát hiện lỗi giá trị, pha hoặc workspace. Exhaustive bao phủ 33.554.432 trường hợp với HMR seed 1901; sampled bổ sung dùng 1901/1902/1903. Đếm primitive có điều khiển là 54 Toffoli-like và 52 qubit (bao gồm 37 qubit input/target/control), so với 75 và 49 của native Kickmix. Đây là kiểm tra kernel, không phải điểm hoặc PASS của decoder. Kiểm tra exhaustive được tái lập bằng `python src/dqi/DQI-19/solution.py --validate-kernel exhaustive`: đủ 2^24 cặp toán hạng với cả hai giá trị control, target ban đầu khác zero theo công thức cố định; reference dùng nhân polynomial nhị phân độc lập, không dùng tensor để tính expected.

Chưa có dev/full ứng viên, chưa có config tối ưu hoặc kết luận cải thiện. Source/config được commit trước build. Đã BUILT tại source commit `9918ac4f0cc2ae695180bc93ef1d1bf99613d168`; [provenance](../../../results/dqi/DQI-19/rank42/build_only/20261108T110144Z-local-build/provenance.json) và [kiểm tra kernel](../../../results/dqi/DQI-19/rank42/build_only/20261108T110144Z-local-build/kernel_validation.json) ghi môi trường/hash thật. Decoder có 1893 qubit và 5044893 Toffoli-like đếm tĩnh; đếm tĩnh không phải T trung bình/shot. Artifact `artifacts/dqi/DQI-19/rank42.kmb` có SHA-256 `ae5d79c2ade1f04ce5937581fae10bbb14f5cd992224c6c202c0b976f6d28627`, 1143210844 bytes. Python local 3.13.7 khác patch 3.13.14 của đối chứng lịch sử, nên không dùng run đó để tính gain; cần đối chứng tương thích nếu so điểm. Chưa chấm decoder; agent dừng sau BUILT để thành viên chấm notebook local. Dự kiến mode dev_5min, 4096 shots theo harness của repo; OWNER trng-hminh, TRACK dqi, EXPERIMENT_ID DQI-19, CONFIG_NAME rank42.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa xác định | Chưa chấm | Chưa chấm |
| Full | Chưa xác định | Chưa chấm | Chưa chấm |

Mã triển khai: [solution.py](solution.py). Điểm: [SCORES.md](../SCORES.md).
