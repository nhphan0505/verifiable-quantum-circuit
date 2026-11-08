# [DQI-23] Thay EEA đồng bộ 222 bước bằng Schur phân số liên tục tại chỗ với bước nhảy block-Wronskian trên vùng syndrome

Loại: Ý tưởng mới.

## Thuật toán và công thức

Giữ hợp đồng của [DQI-BASELINE](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/src/dqi/DQI-BASELINE/solution.py) và [verifier](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/verifiers/dqi/verify_submission_dqi.py). Với `m=4095`, `n=70`, `degree=12`, đầu vào là 70 word syndrome 12 bit và mask cổ điển runtime `E0..E4094`. Đầu ra là pha parity của tích bit giữa mask và lỗi giải mã, với toàn bộ syndrome được khôi phục và ancilla sạch. Thay `_initial_shift_loop` và `_synchronized_eea`; hai mảng EEA dài 73 word chứa tổng 1.752 dây, trong đó 840 dây là đầu vào đã được alias vào `reg_a`.

1. Làm việc trên GF(2^12) đúng basis và primitive element của baseline. Ký hiệu `F(x)=sum_{i=1..70} S_i x^(-i)`. Nếu có `w<=35` lỗi, `F` là khai triển của `A/B`, với `B=x^w sigma(1/x)` monic và `A=x^(w-1) omega(1/x)`. Cặp đa thức thỏa `sigma S = omega mod z^70`, `sigma(0)=1`, `deg omega < w`. Syndrome toàn zero đi thẳng qua với pha +1.
2. Mô hình đối chứng cổ điển cho extraction: với series hiện tại có valuation `d>0` theo biến `z=1/x`, viết `F=z^d a(z)` với `a_0!=0`. Dùng `b_0=1/a_0`, `b_k=b_0 sum_{i=1..k} a_i b_{k-i}` để tính reciprocal. Tách `1/F=q(x)+F_next`, với `q` lấy từ `b_0..b_d`. Từ prefix `L` hệ số của `F`, thu được `L-2d` hệ số hữu dụng của `F_next`. Các quotient chiếm tổng `sum(d+1)<=2w` word. Dựng lại rational từ cuối bằng `(A,B) <- (B,qB+A)` bắt đầu tại `(0,1)`, rồi scale đồng thời A và B để B monic. Khi chuyển A sang omega, đệm A đủ w hệ số trước khi đảo thứ tự. Đây là đối chứng đại số. Bản schur triển khai reciprocal tại chỗ bằng cách tách series đơn vị thành các nhân tử (1+p_i z^i) rồi ghép các nghịch đảo theo thứ tự ngược. Các cập nhật tam giác dùng XOR và tái sử dụng ngay dãy hệ số.
3. Bản dựng chọn trực tiếp valuation d, tức bước nhảy đến biên block kế tiếp của phân số liên tục. Leading minor Hankel là đối chứng cho các biên này. Kernel dùng reciprocal và hoán vị hệ số theo d, chưa có phép cập nhật determinant block-Wronskian riêng. Trong cặp slot của mỗi block, hệ số đầu thương khác zero đánh dấu biên cuối, còn các slot tử trước biên bằng zero. Con trỏ 6 bit chỉ điểm bắt đầu phần syndrome chưa xử lý. Các dấu biên cho phép tái tạo điều khiển ở chiều đảo.
4. Converter đi từ cuối dãy thương về đầu. Với L là hệ số đầu q và B monic, dùng A'=B/L và B'=(qB+A)/L. Cặp A,B được đệm bằng cùng lũy thừa x để giữ layout cố định. Hoán đổi slot ở đuôi và cộng tích qB theo thứ tự bậc giảm để các hệ số thương còn dùng nằm nguyên tại chỗ. Sau bước quét pha, converter đảo bằng cách đọc valuation của tử để tìm lại d. Việc trích thương và dựng cặp đa thức cùng dùng 70 word syndrome.
5. Tại `beta_j=gamma^(-j)`, chỉ kick pha khi `sigma(beta_j)=0`. Với convention `S_i=sum e_j gamma^(ij)`, dùng `e_j=omega(beta_j)/sigma'(beta_j)` trực tiếp trên hệ số chuẩn hóa. Kiểm parity theo basis nhị phân của verifier với `E_j` runtime. Giữ phép đánh giá Chien/Forney và nghịch đảo từng vị trí làm đối chứng cho H3; adapter cho layout mới phải được đối chiếu với một lỗi ở j=0 và j=4094. [DQI-21](https://github.com/nhphan0505/verifiable-quantum-circuit/issues/21) nghiên cứu reciprocal pha riêng, với EEA chính giữ nguyên. Sau pha, đảo converter, routing, block extraction và kiểm mọi dây đầu vào/ancilla.

Các note ready trên main dùng cho thiết kế gồm [phép ghi đè tam giác và routing](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/dqi/papers/arxiv-2610.22367/note.md), [in-place continued-fraction và mốc round12](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-mrmeows-open-circuits-v3/note.md), [ví dụ Schur và chi phí reverse](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-752897-verifier-in-the-loop/note.md), và [dòng C1, block-Wronskian, kết quả âm Hankel](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-vqcc-own-circuit-portfolio/note.md). Các note báo 881 qubit, khoảng 964.394 Toffoli cho round12 và chênh khoảng +31 Toffoli/cặp nút ở một thiết kế reverse. Đó là kết quả được báo cho các thiết kế tham chiếu, chưa có số đo cho H3.

## Điều kiện đúng và sai số

Không làm tròn GF. Locator phải có nghiệm đơn ở các vị trí lỗi phân biệt. Theo dõi valuation, pivot zero, thiếu số hệ số đáng tin cậy và kết thúc tại trọng số 0, 1, 35. Chỉ dùng conditional routing dạng `R_b^-1 K R_b` khi các nhánh có cùng kernel dưới phép đổi vị trí và có đủ thông tin phục hồi điều khiển. Nếu dọn bằng phép đo X, kiểm pha sửa trên từng nhánh đo. Các kiểm tra kỹ thuật của bản dựng bao gồm pha, khôi phục syndrome và dọn ancilla trong mô phỏng thu nhỏ.

## Tài nguyên dự kiến

Input cố định 840 qubit. Điều kiện bàn giao Q ≤ 900 cho phép tối đa 60 qubit ngoài vùng đầu vào. Phép nghịch đảo GF(2^12) dùng norm xuống GF(64), lookup 6 bit và tích với liên hợp. Tính cả inverse scaffold, root flag, dữ liệu định tuyến, lịch sử và converter. Đo `T_forward`, `T_reverse`, `T_phase` và peak `Q` riêng. Verifier chấm `R(eps_plus) Q^2 T`, với `T` là Toffoli-like trung bình mỗi shot. Kỳ vọng bỏ workspace của EEA và giảm số lượt xử lý; nghịch đảo, pivot động và tái tạo lịch sử có thể bù mất lợi ích.

## Cấu hình dựng

Config schur giữ 4095 vị trí, 70 syndrome và word 12 bit. Dùng đủ kích thước của notebook để có thể nạp artifact trực tiếp. Mốc 900 áp dụng cho qubit của toàn mạch.

## Kết luận và phiên bản tái lập

Config schur dựng đủ 4095 vị trí với 900 qubit. Bản từ f7640b3 có kích thước 2,19 GB. Run dev_5min 20261108T154827Z-local-dev_5min-0b76a9 báo ValueError: string too long khi verifier ghi KMB vào bộ nhớ để tính SHA-256, trước mô phỏng shot. [Provenance bản đầu](../../../results/dqi/DQI-23/schur/build_only/20261108T153618Z-local-build/provenance.json)

Bản từ b87d51d dùng unary iteration cho lookup nghịch đảo norm GF(64) để tái sử dụng tiền tố địa chỉ. Artifact còn 1,60 GB và vẫn dùng 900 qubit. Số đếm tĩnh là 12.668.380 cổng Toffoli-like. Hàm băm của verifier hoàn thành và cho SHA-256 trùng file. Chờ lượt chấm notebook cho bản mới. [Provenance](../../../results/dqi/DQI-23/schur/build_only/20261108T155439Z-local-build/provenance.json) · [Build metrics](../../../results/dqi/DQI-23/schur/build_only/20261108T155439Z-local-build/build_metrics.json)

Bản 1,60 GB báo MemoryError: bad allocation trong lượt dev_5min 20261108T155643Z-local-dev_5min-6b6368. Bản từ 1fed986 giảm số lệnh từ 151.558.097 xuống 113.341.248 bằng cách tạo tích có điều khiển qua một toán hạng được mask và tái dùng nghịch đảo norm qua pha Forney. KMB còn 1,10 GB với 900 qubit. Probe cùng tiến trình đã nạp, băm, mô phỏng 256 shot đúng pha và trạng thái, rồi tính reaction depth 471.805. Chờ chạy lại dev_5min. [Provenance](../../../results/dqi/DQI-23/schur/build_only/20261108T160851Z-local-build/provenance.json) · [Build metrics](../../../results/dqi/DQI-23/schur/build_only/20261108T160851Z-local-build/build_metrics.json)

### Kiểm tra khả thi trước build

- Mô hình cổ điển GF(2^12) khôi phục đúng syndrome, locator, numerator và biên độ lỗi trên 432 ca với trọng số 0–35, seed 20261108, gồm lỗi đơn tại vị trí 0 và 4094. Kiểm 630 leading minor; các prefix khả nghịch khớp tổng bậc quotient tích lũy trong những ca kiểm. Khi đổi A sang omega phải đệm A đủ w hệ số trước khi đảo thứ tự. Bỏ đệm làm sai omega khi syndrome đầu bằng zero.
- Kiểm thêm 35 ca cưỡng bức bước nhảy đầu dài 1–35. Chọn w điểm khác nhau a_i và biên độ lỗi bằng nghịch đảo của `a_i * product_{j!=i}(a_i+a_j)`, tạo `S_1..S_(w-1)=0` và `S_w=1`. Mô hình khôi phục đúng syndrome và biên độ; leading minor đầu tiên khả nghịch có kích thước w. Vì vậy nhánh pivot đơn và nhảy tối đa 2 chưa đủ cho toàn bộ miền cam kết.
- Probe một điểm Forney với 840 dây đang sống và cách cấp phát baseline cho `Q=913`. Scaffold nghịch đảo chiếm 48 qubit, inverse và located mỗi thanh ghi 12 qubit, root flag 1 qubit. Mốc này đo riêng kernel, chưa tính metadata decoder. Layout giữ cả 70 word sống không thể dùng nguyên lịch này và đạt Q<900.
- Mạch thu nhỏ khôi phục syndrome, dọn ancilla và cho đúng pha trên 320 ca qua bốn kích thước. Kiểm toàn bộ 4.096 đầu vào của kernel nghịch đảo GF(2^12), gồm zero.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa có | Chưa có | Chưa chấm |
| Full | Chưa có | Chưa có | Chưa chấm |

Điểm và các run đối chứng nằm trong [SCORES.md](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/src/dqi/SCORES.md).

## Tiếp nhận và kế hoạch bàn giao stage 03 trên macOS

Người dùng giao tiếp tục stage 03 của branch hiện có; không tạo lại Issue/branch/config. Mốc nguồn thuật toán là `1fed986e9e736a15195fc654c48cf85dc53620c7`, source SHA-256 `d2461e322a413a6463cba13741f1434e83c96577a70d6e3b5a0240ae44e1637f`; config [schur.json](configs/schur.json) SHA-256 `74055cda362a06faece1aa628efa072d1b6ecce8898934143c2b0fb40985466d`. Giữ nguyên implementation và config đã build ở máy trước; chỉ dựng lại artifact còn thiếu trên máy tiếp nhận, không lấy bằng chứng Windows làm provenance build macOS.

Kế hoạch trước rebuild/chấm:

- Mốc đối chứng thực dụng: DQI-19 control_input tại `c0cf9dfb45b62ba7eeb8588c87b0066409880046`, [config](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c0cf9dfb45b62ba7eeb8588c87b0066409880046/src/dqi/DQI-19/configs/rank42_control_input.json), [dev run](../../../results/dqi/DQI-19/rank42_control_input/dev_5min/20261108T122637Z-local-dev_5min-3fdc53/verifier.json). Dev dùng profile v1, seed 20261106, 4096 shots, Python 3.13.7 và packages pin. Trước so điểm phải đối chiếu hash verifier/harness và môi trường; formal baseline toàn repo có Python patch khác nên chưa mặc định có hệ số hợp lệ.
- Dự đoán tái lập: build đủ m/n/degree=4095/70/12, Q=900, T tĩnh=12565900 và artifact hash giống bản `1fed986` nếu serialization xác định trên hai hệ điều hành. Khác hash cần ghi thực tế và điều tra trước gắn record cũ; không sửa provenance Windows. T cao hơn DQI-19, nhưng Q² thấp hơn có thể bù. Đây là dự đoán từ build lịch sử, chưa là score đo hoặc decoder PASS.
- Ủng hộ hypothesis tài nguyên khi Q<=900 và score dev PASS thấp hơn đối chứng tương thích, không lỗi value/phase; kiểm cả khôi phục input và workspace theo hợp đồng verifier. Nếu phát hiện lỗi hoặc score không tốt hơn thì bác bỏ implementation/đánh đổi hiện tại, không suy mọi kiến trúc Schur đều thất bại. TIMEOUT hoặc MemoryError chỉ là chưa chấm xong, không chứng minh mạch sai.
- Giới hạn vòng tiếp nhận: một rebuild config schur mới nhất và bàn giao dev. Không mở thêm config hay tăng giới hạn tài nguyên tự động; nếu build/nạp lỗi thì xử lý trong phạm vi stage 03, ghi bằng chứng thật và giữ run cũ. Chưa có decoder dev/full PASS trong records đã tiếp nhận; probe 256 shots ở máy trước không thay dev/full chính thức.
- Kiểm tra ứng viên cuối: sau dev, thành viên chạy full chính thức hoặc bộ seed giữ lại độc lập trước khi khẳng định chất lượng; lưu cả ca biên trọng số 0/1/35 và valuation jumps đã nêu. Agent không tự chạy notebook/grader. Đổi bytes artifact có thể đổi seed full mặc định, nên không gọi so sánh full paired nếu chưa có seed chung thực tế.

Build local dùng `.venv` Python 3.13.7, kickmix 1.0.0, numpy 2.5.4, scipy 1.18.1. Source/config đã commit, bytes phải khớp snapshot trước và sau compile; build record/provenance macOS mới được lưu riêng. GitHub vẫn giữ attribution/owner gốc; việc tiếp nhận do người dùng giao không sửa danh tính hay log cũ. Không push tùy chọn ở stage 03.

### Bàn giao rebuild macOS

Artifact local đã BUILT từ snapshot `fabb0298c7976b6a7f8d0db0ef5a1cd6c8b55f5b` (implementation không đổi từ `1fed986e9e736a15195fc654c48cf85dc53620c7`). Source/config bytes khớp snapshot trước/sau compile. [Provenance macOS](../../../results/dqi/DQI-23/schur/build_only/20261108T163330Z-local-macos-build/provenance.json), [build metrics](../../../results/dqi/DQI-23/schur/build_only/20261108T163330Z-local-macos-build/build_metrics.json). Artifact `artifacts/dqi/DQI-23/schur.kmb` có 1096210127 bytes, SHA-256 `876e9b376ed5964aaac7989eae7dc4cf885345c6dc705a713656dd4a109035b8`, trùng chính xác bản Windows mới nhất. Compiler báo Q=900, T tĩnh=12565900. Không chạy lại grader hoặc gọi đây là dev/full PASS.

Checker thường và checker scope với common ancestor `bb3a6311113217a69c64e88e9c3bb0513237a1f9` đạt; 21 tests đạt. Check với origin/main mới báo thiếu 68 result files DQI-21 vì branch được tạo trước lần merge đó, không phải thao tác xóa run ở DQI-23; chưa coi là đạt điều kiện PR. Đồng bộ main/check lại thuộc bước 06, chưa tự merge vào branch ở bước 03. Các probe 256 shots và kiểm model/component được báo ở phần trước thuộc công việc trên máy Windows, không tuyên bố đã chạy lại tại đây; hash khớp xác nhận tái lập artifact bytes.

Thành viên mở notebook trong worktree **GQA-DQI-23**, kernel `.venv` Python 3.13.7, chọn TRACK=dqi, MODE=dev_5min, EXPERIMENT_ID=DQI-23, CONFIG_NAME=schur, OWNER=trng-hminh (người chạy local hiện tại; attribution/assignee GitHub gốc giữ nguyên). Giữ profile v1/seed20261106/4096 shots. Results tự lưu `results/dqi/DQI-23/schur/dev_5min/<run-id>/`. Khi có hai build cùng hash, notebook sẽ giữ review báo nhiều matching builds và chưa tự chọn provenance; agent dùng record macOS nêu trên để thêm provenance đúng ở bước 04, giữ raw review cũ nguyên bytes.

Source/plan commit là mốc bắt buộc trước build; build records và annotation bàn giao giữ local để gộp cùng mốc kết quả bước 04. Không push tùy chọn, không sửa source/config/verifier/notebook/SCORES hay record Windows, không tự chuyển bước hoặc chấm thay thành viên.


## Kết quả macOS và phân tích bước 04

Dev và full thật do thành viên chạy đều PASS, artifact hash `876e9b376ed5964aaac7989eae7dc4cf885345c6dc705a713656dd4a109035b8` khớp rebuild macOS tại source `fabb0298c7976b6a7f8d0db0ef5a1cd6c8b55f5b` (implementation `1fed986`). Notebook không tự chọn provenance vì hai build Windows/macOS cùng hash; agent thêm provenance nối đúng lần build đã thực hiện trên máy này. Raw review.json báo ambiguity được giữ nguyên; nhận xét mới ở review_v2.json. Không suy source từ HEAD, không sửa raw stdout/JSON/config/metadata.

| Mode | Run / provenance / review | Score ↓ | Mean Toffoli | Q | Shots | Value/phase errors |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| dev_5min | [run](../../../results/dqi/DQI-23/schur/dev_5min/20261108T163610Z-local-dev_5min-88b8e2/verifier.json), [provenance](../../../results/dqi/DQI-23/schur/dev_5min/20261108T163610Z-local-dev_5min-88b8e2/provenance.json), [review_v2](../../../results/dqi/DQI-23/schur/dev_5min/20261108T163610Z-local-dev_5min-88b8e2/review_v2.json) | 30379145822809.52 | 12565473.3671875 | 900 | 4096 | 0/0 |
| full | [run](../../../results/dqi/DQI-23/schur/full/20261108T163718Z-local-full-272d25/verifier.json), [provenance](../../../results/dqi/DQI-23/schur/full/20261108T163718Z-local-full-272d25/provenance.json), [review_v2](../../../results/dqi/DQI-23/schur/full/20261108T163718Z-local-full-272d25/review_v2.json) | 12124679698528.295 | 12565463.902070312 | 900 | 102400 | 0/0 |

Dev giữ profile v1/seed20261106/4096 shots; full dùng defaults chính thức m/n/degree/r=4095/70/12/2016, 102400 shots, log2_delta=-128, chỉ thêm max-workers=1. Agent đối chiếu stdout bằng verifier JSON, exit code 0, hashes verifier/harness, config/mode/shots và source/config snapshot. Không chạy grader lại.

So DQI-19 control_input dev cùng môi trường/giao thức, Q giảm 1893→900; Q² còn khoảng 0.2260 lần, T tăng khoảng 2.491 lần, R giữ nguyên. Tổng score còn khoảng 0.5630 lần: giảm khoảng 43.70%, cải thiện khoảng 1.7761×. Full có xu hướng tương tự so incumbent DQI-19 rank42/product, nhưng source/config đối chứng khác và default seeds phụ thuộc artifact, không gọi paired common-seed ablation. Full PASS bổ sung bằng chứng ngoài dev cố định, không chứng minh mọi syndrome.

Kết quả ủng hộ đánh đổi dùng ít qubit của implementation hiện tại theo tiêu chí Q<=900 và score thấp hơn đối chứng. Không chứng minh riêng một determinant block-Wronskian kernel: source hiện dùng valuation routing, reciprocal unit-series và converter đã mô tả. Formal gain so baseline toàn repo vẫn `—` vì baseline chính thức khác Python patch/harness; không đổi tỷ số vs DQI-19 thành tỷ số vs baseline. Các lỗi string-too-long/MemoryError lịch sử có mô tả và build records, nhưng raw grading logs cũ không có trong branch đã nhận; giữ giới hạn này, không tạo lại log.

### Mốc tốt nhất đã chấm và vòng tiếp theo

Cả dev và full tốt nhất hiện là config [schur.json](configs/schur.json), source snapshot `fabb0298c7976b6a7f8d0db0ef5a1cd6c8b55f5b`, source hash `d2461e322a413a6463cba13741f1434e83c96577a70d6e3b5a0240ae44e1637f`, config hash `74055cda362a06faece1aa628efa072d1b6ecce8898934143c2b0fb40985466d`. Run/provenance ở bảng trên. Lấy source/config tại đúng SHA và dùng build_command trong provenance; JSON cùng tên chạy với implementation tương lai không mặc nhiên tái lập mốc này.

Người dùng chọn rõ thử một config mới ở bước 05 trước khi tổng kết bước 06. Vì vậy giữ PR draft và giữ nguyên mốc schur đã PASS; không tự gọi bước 06 hoàn tất khi config mới chưa có grading thật. Các dòng “chưa chấm/chờ bước 04” phía trên là lịch sử bàn giao đã được kết quả này thay thế.

## Kế hoạch bước 05 — schur_hmr

Người dùng chọn rõ thử một config mới thay vì kết thúc ở schur. Chỉ thêm [schur_hmr.json](configs/schur_hmr.json): m/n/degree=4095/70/12, masked_cleanup=hmr. Config schur cũ mặc định masked_cleanup=ccx; không đổi JSON, artifact hay source/run mapping đã chấm. Chưa tuyên bố config mới tốt nhất; score tiếp tục trỏ mốc schur PASS cho tới khi có kết quả thật.

### Thay đổi và chứng chỉ cleanup

`multiply_add(lhs,rhs,target,control)` bản trước alloc masked sạch, CCX tính masked_i=control*lhs_i, nhân field XOR vào target, rồi CCX đảo masked. Biến thể dùng init_and(control,lhs,masked), cùng phép nhân field, rồi del_and(control,lhs,masked). Control/lhs không bị ghi trong phép nhân; target phải disjoint với control/lhs, được assert tại call site trong mode hmr. Phép nhân không thay masked/rhs. del_and dùng HMR và hiệu chỉnh CZ với chính factor ban đầu nên xóa masked về zero, bảo toàn pha với mọi nhánh đo. Không đặt HMR dưới quantum control; khi control=False, phép nhân với masked=0 vẫn xử lý đúng và cleanup độc lập kết quả đo.

Các call ở reciprocal/convolution dùng target bậc cao khác các factor; scale gọi multiply_add trước/sau cswap, nên factor chỉ cần không đổi trong từng lời gọi. Trường hợp control=True literal giữ đường nhân field gốc, không thêm masked/HMR. Không thay inverse norm, lookup, routing, converter, polynomial layout hoặc khối Forney. Thêm keyword masked_cleanup cho SchurDecoder/build_circuit; mặc định ccx duy trì gate schedule cũ. Mọi helper nằm trong solution.py của ID này; không import hướng mới hoặc sửa hạ tầng.

### Dự đoán, đối chứng và tiêu chí trước build

- Đối chứng chính: schur đã PASS, source fabb029, dev/full và provenance ở phần bước 04. Cùng environment Python 3.13.7/packages pin/verifier/harness; dev giữ profile v1/seed20261106/4096 shots.
- Mỗi controlled multiply_add 12 bit giảm 12 Toffoli-like, từ 87 xuống 75; kernel Q=49 ở cả hai mode. Q peak toàn decoder dự kiến giữ 900. T toàn mạch dự kiến giảm theo số lời gọi có control lượng tử, nhưng chưa đặt số tiết kiệm toàn mạch khi chưa build. Không nhập 13.79% giảm của kernel thành mức giảm score toàn decoder.
- Build chỉ bàn giao nếu Q<=900 và T tĩnh thấp hơn 12565900 của schur. Member dev PASS không lỗi value/phase và score thấp hơn schur tương thích ủng hộ biến thể. Nếu lỗi thì loại implementation; nếu không giảm score thì kiểm tra Q/T/R và giới hạn đo trước kết luận.
- Đúng một config mới; không mở sweep mask/lookup khác. Sau build dừng chờ member grading. Bước 06 đã được giao nhưng chưa đủ điều kiện hoàn tất trước khi config mới được chấm và phân tích; không tự chạy grader để vượt điểm dừng.
- Ứng viên cuối cần full chính thức hoặc seed giữ lại độc lập do thành viên chạy, với giới hạn statistical/default artifact seed như đã ghi. Không sửa tiêu chí sau khi có score.

### Kiểm tra trước compile submission

`--validate-components` kiểm độc lập GF polynomial multiply trên 393216 ca/kernel cho cả ccx và hmr, gồm zero/equal/random operands, arbitrary target, control false/true và ba seed HMR. Không lỗi input/value/phase/workspace; giảm đúng 12 T tại Q không đổi. Năm decoder thu nhỏ (degree/n=2/2,3/2,3/4,3/6,4/8), mỗi biến thể 1920 ca tổng qua ba seed, đối chiếu syndrome/pha trực tiếp từ error/mask; có trọng số 0, single errors ở đầu/cuối, max weight và ca cưỡng bức valuation jumps 1..n/2. Không lỗi khôi phục syndrome/pha/ancilla. Seeded HMR không phải exhaustive outcome enumeration; chứng minh cleanup dựa trên factor bất biến. Đây là component checks, không phải official full-size dev/full PASS. Dùng source/config commit mới trước build, giữ mốc source cũ để tái lập schur.

### Bàn giao BUILT schur_hmr

Config mới BUILT từ source `c5b70b1a7618057000cc9af35794c8e733e5eb1c`; [provenance](../../../results/dqi/DQI-23/schur_hmr/build_only/20261108T165644Z-local-build/provenance.json), [build metrics](../../../results/dqi/DQI-23/schur_hmr/build_only/20261108T165644Z-local-build/build_metrics.json), [component checks](../../../results/dqi/DQI-23/schur_hmr/build_only/20261108T165644Z-local-build/component_validation.json). Source/config bytes khớp snapshot trước/sau compile. Artifact `artifacts/dqi/DQI-23/schur_hmr.kmb`, 1109451887 bytes, SHA-256 `77d44574ee606aee7eae312e5dfd5b9f4353a0db2b63be53a2addf42b16e1458`.

Toàn mạch Q=900, T tĩnh=11620060, giảm 945840 T (7.5270%) so schur tĩnh=12565900, proxy Q²T còn 0.9247296 lần ở Q không đổi. Đạt điều kiện bàn giao Q<=900/T giảm đã đặt trước build. File lớn hơn nhẹ do phép đo/hiệu chỉnh cần thêm instructions; không suy tốc độ hay score grader từ dung lượng file. Chưa có mean T/R/score của config mới. Hash artifact schur cũ vẫn `876e9b376ed5964aaac7989eae7dc4cf885345c6dc705a713656dd4a109035b8`, không ghi đè.

Checker thường/scope theo common ancestor đạt; 21 tests repo đạt. Notebook do người dùng vừa chạy giữ nguyên bytes, không stage/commit. Source/config/plan đã commit trước build; records mới và annotation bàn giao giữ local để gộp với kết quả ở mốc bước 04 tiếp theo. Không push tùy chọn hoặc đưa PR ready khi config mới chưa được chấm.

Thành viên mở notebook trong **GQA-DQI-23**, kernel `.venv` Python 3.13.7, chọn TRACK=dqi, MODE=dev_5min, EXPERIMENT_ID=DQI-23, CONFIG_NAME=schur_hmr, OWNER=trng-hminh; giữ profile v1/seed20261106/4096 shots. Results tự lưu `results/dqi/DQI-23/schur_hmr/dev_5min/<run-id>/`. Nếu dev PASS, nên chạy full config schur_hmr để kiểm bổ sung ứng viên cuối trước bước 06. Mốc schur đã PASS vẫn giữ nguyên trong SCORES/source mapping; không ghi score cho setting chưa chấm. Agent dừng chờ grading thật rồi phân tích bước 04 và tiếp tục bước 06 đã giao khi đủ nghiệm thu; không tự chấm, approve/merge hoặc đóng Issue.


## Kết quả schur_hmr và tổng kết bước 06

Sau lựa chọn dev-only ban đầu, người dùng đã chạy thêm full và giao tổng kết. Cả dev/full schur_hmr đều PASS, không lỗi value/phase, hash khớp build `77d44574ee606aee7eae312e5dfd5b9f4353a0db2b63be53a2addf42b16e1458`, source `c5b70b1a7618057000cc9af35794c8e733e5eb1c`. Đối chiếu source/config snapshot, artifact, provenance/build_run, metadata/command/shots/mode, verifier/harness và raw stdout JSON. Raw records giữ nguyên, review mới lưu riêng; không chạy grader lại.

| Mode | Run / provenance / review | Score ↓ | Mean Toffoli | Q | Shots | Value/phase errors |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| dev_5min | [run](../../../results/dqi/DQI-23/schur_hmr/dev_5min/20261108T165822Z-local-dev_5min-41cf1d/verifier.json), [provenance](../../../results/dqi/DQI-23/schur_hmr/dev_5min/20261108T165822Z-local-dev_5min-41cf1d/provenance.json), [review](../../../results/dqi/DQI-23/schur_hmr/dev_5min/20261108T165822Z-local-dev_5min-41cf1d/review.json) | 28092418499024.06 | 11619633.3671875 | 900 | 4096 | 0/0 |
| full | [run](../../../results/dqi/DQI-23/schur_hmr/full/20261108T170045Z-local-full-f8c7d3/verifier.json), [provenance](../../../results/dqi/DQI-23/schur_hmr/full/20261108T170045Z-local-full-f8c7d3/provenance.json), [review](../../../results/dqi/DQI-23/schur_hmr/full/20261108T170045Z-local-full-f8c7d3/review.json) | 11212018283368.457 | 11619623.323007813 | 900 | 102400 | 0/0 |

Dev giữ profile v1/seed20261106/4096 shots cùng schur; mean T giảm đúng 945840, score giảm khoảng 7.5273%, Q=900 và R không đổi. Full 102400 shots xác nhận xu hướng tương tự trên verifier chính thức defaults, chỉ thêm max-workers=1; full là kiểm tra thống kê bổ sung cho config mới. Default seeds full phụ thuộc artifact, không gọi paired common-seed test hoặc chứng minh mọi syndrome.

So DQI-19 cùng mode/môi trường, score cải thiện khoảng 1.9206× (giảm khoảng 47.93%). Full DQI-19 vẫn là rank42/product, dev là control_input; phép so có giới hạn source/config và seed như review ghi. Formal gain so baseline toàn repo giữ `—` vì baseline chính thức khác Python patch/harness. Không sửa baseline/provenance cũ hoặc coi tỷ số vs DQI-19 là gain chính thức vs baseline.

Tiêu chí vòng 05 đạt trên các ca đã kiểm: Q không tăng, T/score giảm, dev/full PASS không lỗi; HMR cleanup giữ nguyên contract của factor trong mỗi multiply_add. Chốt đúng một config mới schur_hmr, không mở thêm vòng. Lợi ích tài nguyên của Schur in-place và giảm thêm bằng cleanup được hỗ trợ bằng số đo, không chứng minh một determinant block-Wronskian kernel đã được triển khai; source dùng valuation/block routing như phần thiết kế đã nêu. Các probe/model lịch sử thuộc máy Windows và raw logs lỗi trước đây không được đưa vào branch vẫn là giới hạn bằng chứng; không tạo lại log.

### Mốc tốt nhất và tái lập cuối

Cả dev và full tốt nhất DQI-23 hiện dùng [schur_hmr.json](configs/schur_hmr.json), source `c5b70b1a7618057000cc9af35794c8e733e5eb1c`, source SHA-256 `18f7e197dc832236b95cef3b87013cce15373d7327554efb1fdb2bd2f618f492`, config SHA-256 `e684813da2f18212eca5ea21edb7cdfaee998578f8cbdf8a1fb396f523f372f1`; run/provenance nằm ở bảng trên. Checkout đúng source đó, Python 3.13.7/kickmix1.0.0/numpy2.5.4/scipy1.18.1 rồi chạy:

```sh
./.venv/bin/python src/dqi/DQI-23/solution.py --config src/dqi/DQI-23/configs/schur_hmr.json
```

Mốc schur cũ vẫn dùng source fabb029 (implementation 1fed986) và hai run/provenance riêng ở phần bước 04; không thay SHA cũ bằng HEAD mới. Artifact lớn ignore, raw results/build records/provenance được commit. Notebook do người dùng chấm giữ local, không commit/push hoặc sửa thay người dùng.

Main đã được fetch và merge trước tổng kết theo yêu cầu người dùng, merge commit `b9e60d7`; chỉ conflict hai bảng EXPERIMENTS/SCORES và đã giữ đủ các dòng hướng khác. Giữ các SHA nguồn bằng merge, không amend/rebase. Bước 06 hoàn thiện checks và push branch/PR để review độc lập; chưa approve/merge PR hoặc đóng Issue. Những dòng “chưa chấm/chưa push/chờ stage 04/06” trong phần lịch sử được kết quả/tổng kết này thay thế ở thời điểm công bố; không sửa record lịch sử.


### Quy ước hiển thị hệ số sau tổng kết

Theo yêu cầu cập nhật toàn bảng DQI, hai cột hệ số trong SCORES đều dùng score DQI-BASELINE cùng mode chia score ứng viên, làm tròn 4 chữ số thập phân. DQI-23 hiển thị full 2.1798× và dev 2.1798×, kèm chú thích đây là tỷ số số học so baseline lịch sử khác môi trường; chưa gọi là phép so sánh cùng môi trường được checker xác nhận. Các tỷ số so DQI-19 ở phần phân tích vẫn là 1.9206396378089878× full và 1.920640911358237× dev, có đối chứng khác với hai cột bảng điểm.

Thay đổi hiển thị này được người dùng giao rõ cho toàn bộ bảng DQI, gồm các dòng của hướng khác; không sửa score gốc, JSON/log/provenance hoặc verifier/checker. Các mốc trước ghi hệ số để trống là lịch sử trước quyết định hiển thị số học. Checker hiện vẫn yêu cầu môi trường tương thích và phạm vi exp branch chỉ thay dòng của ID, nên thay đổi toàn bảng này không được coi là đạt schema/scope hiện tại; không tuyên bố CI xanh hoặc PR đủ điều kiện merge khi các check đó còn lỗi.
