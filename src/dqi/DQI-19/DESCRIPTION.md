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

### Phân tích bước 04 với baseline chạy lại

Hai run baseline mới của thành viên (dev `20261108T113442Z-local-dev_5min-1aa90c`, full `20261108T113523Z-local-full-ecd8e5`) đều PASS, không lỗi giá trị/pha. Python 3.13.7, packages, toàn bộ hash verifier và hash dev harness khớp ứng viên; dev cùng profile v1/seed 20261106/4096 shots, full 102400 shots. Tỷ số score mới là dev 1.1349114926324711×, full 1.134911658020827×; T ứng viên giảm khoảng 11.8874% trên các run này, Q giữ 1893. Đây là bằng chứng thực nghiệm ủng hộ giảm chi phí Toffoli toàn decoder theo tiêu chí ban đầu. [Đối chiếu dev](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/comparison_v4.json), [đối chiếu full](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/comparison_v2.json) kèm bản sao nguyên bytes metadata/verifier/config/stdout baseline trong cùng thư mục ứng viên.

Giới hạn provenance đối chứng: hai run baseline mới không có record build_only khớp hash `5dfb9991335e41f709a2b2cd0c1e8b28f5ad50e9672b11539d77480b39e9f98f`; không gán SHA nguồn từ HEAD. Chưa đăng ký các run đó vào dòng baseline toàn repo, nên cột cải thiện chính thức vẫn để trống. Mọi run và sidecar cũ được giữ nguyên; không sửa dữ liệu baseline ngoài phạm vi nhánh.

Đánh đổi quan sát được: dev ứng viên mất khoảng 53.85 giây so với 28.97 giây của baseline chạy lại. Vì vậy giảm T chưa đồng nghĩa simulator nhanh hơn. Mạng CNOT/CZ, feedback và artifact là mục tiêu của vòng tiếp, giữ nguyên thuật toán rank 42 và m/n/degree.

### Kế hoạch vòng 05 đã được giao

Mở rộng điều kiện dừng ban đầu một config vì bước 05 đã được giao và results cho thấy bottleneck Clifford/runtime. Chỉ thêm một setting `rank42_control_input`: thay vì tính product 12 bit, copy có điều khiển rồi đo/xóa product, compute `masked_x = control AND x` bằng 12 init_and, dùng 42 tích bilinear giữa masked_x và y để XOR trực tiếp vào target bất kỳ; từng tích tạm được del_and ngay sau fanout. Dọn parity scratch, rồi del_and 12 bit masked_x. Mỗi phép có điều khiển vẫn 54 Toffoli-like, giữ chính xác value/phase/cleanup và workspace tối đa 15 qubit; bỏ lượt quét sửa pha của product nên dự kiến giảm Clifford/feedback/size và thời gian simulator. Không đổi inverse/division/EEA/Chien/Forney. Config `rank42` và mapping source/run cũ vẫn nguyên.

Trước build kiểm tra tensor và primitive exhaustive trên cả hai control như vòng trước; dùng reference polynomial độc lập. Kiểm tra operation statistics để xác nhận 54 Toffoli và giảm số instruction. Sau source commit → compile → provenance, bàn giao cùng dev profile/seed 4096 shots. Bác bỏ setting mới nếu phát sinh value/phase/workspace errors, T tăng, hoặc không giảm overhead như dự đoán. Kiểm tra sampled trên ba seed HMR cho primitive mới chưa phát hiện lỗi; primitive vẫn 54 Toffoli-like, 52 qubit, nhưng 1022 instruction so với 1926 của strategy product. Đây là kiểm tra kernel, chưa phải số đo decoder. Chưa có dev/full của setting mới; bước 06 chờ chấm và phân tích trước khi chọn ứng viên cuối. Không tự chấm.

Đánh đổi quan sát được: Q cực đại 1893, bằng con số Q lịch sử; mạng CNOT/HMR/classical feedback và artifact lớn hơn vẫn là chi phí cần cân nhắc. Giữ mốc rank42 đã PASS; vòng 05 được triển khai theo kế hoạch bổ sung phía trên. Chưa tự chấm hoặc merge. Full đã bổ sung bằng chứng đúng nhưng chưa giải quyết giới hạn đối chứng hiệu năng.

### Bàn giao vòng 05 và trạng thái bước 06

Setting [rank42_control_input](configs/rank42_control_input.json) đã **BUILT** tại commit `c0cf9dfb45b62ba7eeb8588c87b0066409880046`. [Build provenance](../../../results/dqi/DQI-19/rank42_control_input/build_only/20261108T121007Z-local-build/provenance.json), [build record](../../../results/dqi/DQI-19/rank42_control_input/build_only/20261108T121007Z-local-build/build.json), [kiểm tra kernel](../../../results/dqi/DQI-19/rank42_control_input/build_only/20261108T121007Z-local-build/kernel_validation.json), [regression strategy cũ](../../../results/dqi/DQI-19/rank42_control_input/build_only/20261108T121007Z-local-build/product_regression.json). Cả hai kernel đã kiểm tra exhaustive 33554432 trường hợp, không lỗi value/phase/workspace. Source/config local khớp bytes snapshot commit trước build.

Artifact `artifacts/dqi/DQI-19/rank42_control_input.kmb` có SHA-256 `8a7a9de680e4918ffdf949c529643e6cded8f7b06e023b0ebc7db994b42e7b7d`, 896002620 bytes; nhỏ hơn artifact rank42 21.6240%, Q=1893, T đếm tĩnh=5044893. Giảm kích thước/instruction chưa chứng minh dev nhanh hơn hoặc pha toàn decoder đúng; chưa có điểm verifier cho setting mới. Mốc tốt dev/full vẫn là `rank42` tại source commit `9918ac4f0cc2ae695180bc93ef1d1bf99613d168` bên dưới.

Thành viên mở notebook trong worktree GQA-DQI-19, chọn TRACK=dqi, MODE=dev_5min, EXPERIMENT_ID=DQI-19, OWNER=trng-hminh, CONFIG_NAME=rank42_control_input; giữ profile v1/seed 20261106/4096 shots. Kết quả tự lưu `results/dqi/DQI-19/rank42_control_input/dev_5min/<run-id>/`. Không tự chấm hoặc theo dõi runtime. Bước 06 đã đồng bộ main (không có thay đổi mới), kiểm tra phần commit trên checkout sạch và cập nhật draft PR; chưa đưa PR sẵn sàng review vì vòng 05 chờ kết quả và phân tích. Hai run baseline chưa đăng ký vẫn được giữ nguyên ở worktree của thành viên; không đưa thay đổi ngoài phạm vi DQI-19 vào PR.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | [rank42](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/9918ac4f0cc2ae695180bc93ef1d1bf99613d168/src/dqi/DQI-19/configs/rank42.json) | `9918ac4f0cc2ae695180bc93ef1d1bf99613d168` | [run](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/verifier.json), [provenance](../../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/provenance.json) |
| Full | [rank42](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/9918ac4f0cc2ae695180bc93ef1d1bf99613d168/src/dqi/DQI-19/configs/rank42.json) | `9918ac4f0cc2ae695180bc93ef1d1bf99613d168` | [run](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/verifier.json), [provenance](../../../results/dqi/DQI-19/rank42/full/20261108T110834Z-local-full-612d9f/provenance.json) |

Tái lập source/config bằng `git show 9918ac4f0cc2ae695180bc93ef1d1bf99613d168:src/dqi/DQI-19/solution.py` và config tại commit cùng SHA. Mã triển khai: [solution.py](solution.py). Điểm: [SCORES.md](../SCORES.md).
