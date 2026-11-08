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

Setting thứ hai [rank42_control_input.json](configs/rank42_control_input.json) đưa control vào đầu vào: compute `masked_x = control AND x` bằng 12 init_and; stream 42 tích bilinear của masked_x và y vào target bất kỳ; del_and từng tích ngay sau fanout. Sau khi trả parity scratch về 0, del_and 12 bit masked_x bằng control/x gốc. Tổng vẫn 54 Toffoli-like cho mỗi phép có điều khiển, workspace kernel 15 qubit; bỏ lượt sửa pha của product dài 12 bit. Các input của del_and không được đổi trước cleanup; hai call site EEA có input/target/control rời nhau. Setting rank42 vẫn dùng strategy product mặc định và giữ nguyên lịch sử/source cũ.

Đánh đổi: thêm product/scratch qubit, CNOT và CZ; giảm Toffoli của multiply-add có điều khiển từ số đo primitive local 75 xuống dự kiến 54, nhưng Q^2 và thời gian simulator có thể tăng. Đếm này chỉ cho primitive, chưa phải chi phí toàn decoder. Cả [rank42.json](configs/rank42.json) và [rank42_control_input.json](configs/rank42_control_input.json) giữ m=4095,n=70,degree=12 để tách tác động bộ nhân và lịch MBU; không quét tham số. `solution.py` tự suy ra TRACK/ID và kiểm tra config nằm trực tiếp trong configs/ sau resolve. Để dựng: `python src/dqi/DQI-19/solution.py --config src/dqi/DQI-19/configs/rank42.json`. Dùng Python 3.13 trong .venv và dependency đã pin.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: source baseline commit nêu trên, configs/baseline.json (4095,70,12); run dev `results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5`. Chỉ tính gain nếu profile/seed/shots, môi trường và hash verifier/harness tương thích; nếu thiếu thì chấm đối chứng mới hoặc để trống gain.
- Dự đoán: kernel nhân có điều khiển giảm T; Q và Clifford tăng. Chưa biết score tổng R(epsilon_plus)*Q^2*T.
- Ủng hộ: tensor chính xác, test primitive giữ value/phase/workspace và dev_5min 4096 shots PASS với phase_errors=0, T trung bình giảm so đối chứng tương thích; score giảm mới ủng hộ lợi ích end-to-end. Bác bỏ nếu tensor sai, xuất hiện phase/value/workspace errors, hoặc T không giảm. Timeout chỉ cho biết giới hạn runtime, không chứng minh sai mạch.
- Điều kiện dừng: một config ứng viên ban đầu; không quét hàng loạt. Dừng build nếu tensor sai, API không hỗ trợ MBU đúng hoặc tài nguyên vượt khả năng local; không đổi hypothesis ngầm.
- Kiểm tra ứng viên cuối: syndrome 0, trọng số 1/35, seed chưa dùng chọn config hoặc full; đối chứng cùng profile. Thành viên tự chấm notebook local; agent dừng sau artifact BUILT và provenance.

## Kết luận và phiên bản tái lập

Hướng đã thử hai setting và dừng mở rộng ở đây. Cả `rank42` và `rank42_control_input` đạt dev_5min và full PASS, không phát hiện lỗi giá trị/pha. Chọn `rank42_control_input` làm phương án thực dụng cuối vì giữ chi phí Q/T gần như bằng nhau nhưng giảm overhead mạch, kích thước artifact và thời gian dev quan sát được. Bảng SCORES vẫn giữ đúng score nhỏ nhất từng mode: dev là control_input; full là rank42. Chênh score giữa hai setting chỉ khoảng 5–6e-8 tương đối và không được xem là cải thiện đáng kể.

### Kết quả và đối chiếu

| Setting / source commit | Mode / run | Score | Shots | Value/phase errors | Mean Toffoli-like | Q |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| rank42 / `9918ac4f0cc2ae695180bc93ef1d1bf99613d168` | [dev](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/verifier.json) | 53955451017897.38 | 4096 | 0/0 | 5044549.798095703 | 1893 |
| rank42 / `9918ac4f0cc2ae695180bc93ef1d1bf99613d168` | [full](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/verifier.json) | 21534246734876.543 | 102400 | 0/0 | 5044541.83546875 | 1893 |
| rank42_control_input / `c0cf9dfb45b62ba7eeb8588c87b0066409880046` | [dev](../../../results/dqi/DQI-19/rank42_control_input/dev_5min/20261108T122637Z-local-dev_5min-3fdc53/verifier.json) | 53955448268222.56 | 4096 | 0/0 | 5044549.541015625 | 1893 |
| rank42_control_input / `c0cf9dfb45b62ba7eeb8588c87b0066409880046` | [full](../../../results/dqi/DQI-19/rank42_control_input/full/20261108T122721Z-local-full-33aea9/verifier.json) | 21534248022526.41 | 102400 | 0/0 | 5044542.137109375 | 1893 |

Dev dùng profile v1, seed 20261106, 4096 shots. Full dùng verifier chính thức/default với 102400 shots, m/n/degree/r=4095/70/12/2016, log2_delta=-128; chỉ bổ sung max-workers=1. Full là kiểm tra thống kê bổ sung cho ứng viên cuối, không phải chứng minh đúng trên mọi syndrome. Epsilon_plus dev/full lần lượt 0.021427937912299865 và 0.0008660587301657926. [Review bằng chứng dev mới](../../../results/dqi/DQI-19/rank42_control_input/dev_5min/20261108T122637Z-local-dev_5min-3fdc53/review.json) và [review full mới](../../../results/dqi/DQI-19/rank42_control_input/full/20261108T122721Z-local-full-33aea9/review.json) kiểm tra raw stdout=verifier JSON, mode/command/shots, hash artifact/verifier/harness, snapshot source/config và liên kết build. Không sửa JSON/log hoặc sidecar cũ.

Vòng 05 được giao sau kết quả vòng đầu nên điều kiện dừng một config ban đầu được mở rộng thành đúng một setting bổ sung, với dự đoán trước build: giữ 54 Toffoli-like/15 scratch qubit và giảm Clifford/feedback bằng input masking. Kết quả ủng hộ dự đoán: primitive controlled vẫn 54 Toffoli-like/52 tổng qubit, instruction giảm 1926->1022; toàn decoder num_ops giảm 119884966->90588134 (24.4375%), reaction depth 196370->170757, artifact giảm 1143210844->896002620 bytes (21.6240%). Dev elapsed giảm 53.8529595->30.5831066 giây (43.2100%, khoảng 1.7609×). Đây là một timing mỗi setting, chưa phải benchmark runtime lặp độc lập; không gộp giảm thời gian simulator vào score chính thức R(epsilon_plus)*Q²*T.

### Baseline và giới hạn cải thiện

Baseline chạy lại của thành viên trên Python 3.13.7 (dev `20261108T113442Z-local-dev_5min-1aa90c`, full `20261108T113523Z-local-full-ecd8e5`) PASS, cùng packages/hash verifier; dev cùng hash harness/profile v1/seed/shots. Với control_input, tỷ số score baseline/candidate xấp xỉ **1.1349×**, tương ứng giảm T khoảng **11.8874%** và Q giữ 1893. Bản sao nguyên bytes metadata/verifier/config/stdout baseline nằm trong từng run ứng viên dưới tên `baseline_recheck_*`; các phép đối chiếu đã ghi trong review mới. [So sánh vòng đầu dev](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/comparison_v4.json) và [full](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/comparison_v2.json) cũng được giữ nguyên.

Hai run baseline mới thiếu record build_only khớp hash `5dfb9991335e41f709a2b2cd0c1e8b28f5ad50e9672b11539d77480b39e9f98f`; không suy đoán source commit từ HEAD. Chưa đăng ký chúng vào dòng baseline toàn repo ngoài phạm vi nhánh này. Dòng baseline chính thức vẫn trỏ run lịch sử Python 3.13.14 (dev harness khác), nên cột hệ số cải thiện chính thức giữ `—`; tỷ số với baseline chạy lại hiển thị ở chú thích cùng dòng DQI-19. Cần bổ sung/xác minh provenance baseline và đăng ký riêng trước khi điền hệ số chính thức; không sửa metadata/checker hoặc ghi đè bằng chứng để vượt điều kiện. Đây là giới hạn đối chứng, không thay đổi trạng thái PASS của ứng viên.

### Bằng chứng dựng và tái lập

Tensor tự dựng khớp đủ 144 cặp basis; do bilinear đây là identity trên mọi x,y. Cả hai strategy kernel được kiểm tra exhaustive 33554432 trường hợp (mọi cặp toán hạng với cả hai control), không lỗi value/phase/workspace; sampled bổ sung ba seed HMR. [Kernel mới](../../../results/dqi/DQI-19/rank42_control_input/build_only/20261108T121007Z-local-build/kernel_validation.json), [regression product](../../../results/dqi/DQI-19/rank42_control_input/build_only/20261108T121007Z-local-build/product_regression.json). Các kiểm tra kernel không thay thế verifier decoder; các lượt full phía trên đã bổ sung bằng chứng này.

- `rank42` dùng source `9918ac4f0cc2ae695180bc93ef1d1bf99613d168`, artifact SHA-256 `ae5d79c2ade1f04ce5937581fae10bbb14f5cd992224c6c202c0b976f6d28627`; [build provenance](../../../results/dqi/DQI-19/rank42/build_only/20261108T110144Z-local-build/provenance.json).
- `rank42_control_input` dùng source `c0cf9dfb45b62ba7eeb8588c87b0066409880046`, artifact SHA-256 `8a7a9de680e4918ffdf949c529643e6cded8f7b06e023b0ebc7db994b42e7b7d`; [build provenance](../../../results/dqi/DQI-19/rank42_control_input/build_only/20261108T121007Z-local-build/provenance.json).
- Source/config được commit trước build và đối chiếu bytes snapshot; giữ nguyên hai SHA và mapping run, không amend/rebase. Môi trường chấm Python 3.13.7, kickmix 1.0.0, numpy 2.5.4, scipy 1.18.1. Default artifact nằm dưới artifacts/dqi/DQI-19/, tên trùng config stem.

| Mốc tốt nhất | Config tại source commit | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | [rank42_control_input](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c0cf9dfb45b62ba7eeb8588c87b0066409880046/src/dqi/DQI-19/configs/rank42_control_input.json) | `c0cf9dfb45b62ba7eeb8588c87b0066409880046` | [run](../../../results/dqi/DQI-19/rank42_control_input/dev_5min/20261108T122637Z-local-dev_5min-3fdc53/verifier.json), [provenance](../../../results/dqi/DQI-19/rank42_control_input/dev_5min/20261108T122637Z-local-dev_5min-3fdc53/provenance.json) |
| Full | [rank42](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/9918ac4f0cc2ae695180bc93ef1d1bf99613d168/src/dqi/DQI-19/configs/rank42.json) | `9918ac4f0cc2ae695180bc93ef1d1bf99613d168` | [run](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/verifier.json), [provenance](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/provenance.json) |

Tái lập bằng source/config tại đúng SHA trong bảng, ví dụ `git show c0cf9dfb45b62ba7eeb8588c87b0066409880046:src/dqi/DQI-19/solution.py`; dựng với .venv Python 3.13 và requirements đã pin. Mã hiện tại: [solution.py](solution.py); config: [rank42](configs/rank42.json), [control_input](configs/rank42_control_input.json); điểm: [SCORES.md](../SCORES.md).

Bước 04/05 đã có phân tích/results/provenance cho hai setting; kết thúc vòng thử, không tạo thêm config. Bước 06 tổng kết PR để review độc lập, giữ giới hạn baseline nêu trên; chưa approve, merge hoặc đóng Issue.
