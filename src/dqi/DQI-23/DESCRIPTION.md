# [DQI-23] Thay EEA đồng bộ 222 bước bằng Schur phân số liên tục tại chỗ với bước nhảy block-Wronskian trên vùng syndrome

Loại: Ý tưởng mới.

## Thuật toán và công thức

Giữ hợp đồng của [DQI-BASELINE](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/src/dqi/DQI-BASELINE/solution.py) và [verifier](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/verifiers/dqi/verify_submission_dqi.py). Với `m=4095`, `n=70`, `degree=12`, đầu vào là 70 word syndrome 12 bit và mask cổ điển runtime `E0..E4094`. Đầu ra là pha parity của tích bit giữa mask và lỗi giải mã, với toàn bộ syndrome được khôi phục và ancilla sạch. Thay `_initial_shift_loop` và `_synchronized_eea`; hai mảng EEA dài 73 word chứa tổng 1.752 dây, trong đó 840 dây là đầu vào đã được alias vào `reg_a`.

1. Làm việc trên GF(2^12) đúng basis và primitive element của baseline. Ký hiệu `F(x)=sum_{i=1..70} S_i x^(-i)`. Nếu có `w<=35` lỗi, `F` là khai triển của `A/B`, với `B=x^w sigma(1/x)` monic và `A=x^(w-1) omega(1/x)`. Cặp đa thức thỏa `sigma S = omega mod z^70`, `sigma(0)=1`, `deg omega < w`. Syndrome toàn zero đi thẳng qua với pha +1.
2. Mô hình đối chứng cổ điển cho extraction: với series hiện tại có valuation `d>0` theo biến `z=1/x`, viết `F=z^d a(z)` với `a_0!=0`. Dùng `b_0=1/a_0`, `b_k=b_0 sum_{i=1..k} a_i b_{k-i}` để tính reciprocal. Tách `1/F=q(x)+F_next`, với `q` lấy từ `b_0..b_d`. Từ prefix `L` hệ số của `F`, thu được `L-2d` hệ số hữu dụng của `F_next`. Các quotient chiếm tổng `sum(d+1)<=2w` word. Dựng lại rational từ cuối bằng `(A,B) <- (B,qB+A)` bắt đầu tại `(0,1)`, rồi scale đồng thời A và B để B monic. Khi chuyển A sang omega, đệm A đủ w hệ số trước khi đảo thứ tự. Đây là đối chứng đại số, chưa phải lịch gate tại chỗ.
3. Thử nhảy block qua prefix có pivot đơn bằng zero. Dùng leading minors của Hankel `H[r,c]=S_(r+c+1)` để kiểm định pivot. Sau một prefix khả nghịch, block tiếp là đoạn ngắn nhất làm prefix mở rộng khả nghịch, tương đương block chính đầu khả nghịch của Schur complement. So sánh trạng thái sau mỗi block với tích các ma trận convergent `[[0,1],[1,q]]` từ mô hình scalar. Thiết kế kernel block-Wronskian cho đúng chuyển đổi đó, dùng alias trên 70 word và tái dùng slot chỉ sau khi chứng minh đã sạch. Lưu đủ thông tin để chọn lại cùng block, kể cả khi pivot zero hoặc nhảy nhiều bậc, rồi kiểm tra inverse trên mọi nhánh của mô hình. Hankel trực tiếp chỉ dùng làm đối chứng để kiểm các điểm nhảy, vì chi phí bản tại chỗ đã thử trong tài liệu vượt ngân sách.
4. Giao tiếp bằng locator và numerator hệ số tăng dần với `sigma_0=1` ngầm định. Nếu lựa chọn lịch còn giữ syndrome cạnh locator, cập nhật tam giác `W_i <- S_(i+1) + sum_{j=1..i} sigma_j S_(i-j+1)` theo i giảm dần, với hệ số locator ngoài bậc bằng zero. Chỉ tái dùng `W_35..W_69` sau khi invariant chứng minh chúng sạch. Đảo bước này theo i tăng dần. Nếu extraction đã ghi đè syndrome bằng quotient, phải dựng `sigma,omega` bằng converter thuận nghịch từ các quotient và kiểm tra liveness riêng trước khi áp dụng công thức tam giác.
5. Tại `beta_j=gamma^(-j)`, chỉ kick pha khi `sigma(beta_j)=0`. Với convention `S_i=sum e_j gamma^(ij)`, dùng `e_j=omega(beta_j)/sigma'(beta_j)` trực tiếp trên hệ số chuẩn hóa. Kiểm parity theo basis nhị phân của verifier với `E_j` runtime. Giữ phép đánh giá Chien/Forney và nghịch đảo từng vị trí làm đối chứng cho H3; adapter cho layout mới phải được đối chiếu với một lỗi ở j=0 và j=4094. [DQI-21](https://github.com/nhphan0505/verifiable-quantum-circuit/issues/21) nghiên cứu reciprocal pha riêng, với EEA chính giữ nguyên. Sau pha, đảo converter, routing, block extraction và kiểm mọi dây đầu vào/ancilla.

Các note ready trên main dùng cho thiết kế gồm [phép ghi đè tam giác và routing](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/dqi/papers/arxiv-2610.22367/note.md), [in-place continued-fraction và mốc round12](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-mrmeows-open-circuits-v3/note.md), [ví dụ Schur và chi phí reverse](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-752897-verifier-in-the-loop/note.md), và [dòng C1, block-Wronskian, kết quả âm Hankel](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-vqcc-own-circuit-portfolio/note.md). Các note báo 881 qubit, khoảng 964.394 Toffoli cho round12 và chênh khoảng +31 Toffoli/cặp nút ở một thiết kế reverse. Đó là kết quả được báo cho các thiết kế tham chiếu, chưa có số đo cho H3.

## Điều kiện đúng và sai số

Không làm tròn GF. Locator phải có nghiệm đơn ở các vị trí lỗi phân biệt. Theo dõi valuation, pivot zero, thiếu số hệ số đáng tin cậy và kết thúc tại trọng số 0, 1, 35. Chỉ dùng conditional routing dạng `R_b^-1 K R_b` khi các nhánh có cùng kernel dưới phép đổi vị trí và có đủ thông tin phục hồi điều khiển. Nếu dọn bằng phép đo X, kiểm pha sửa trên từng nhánh đo. Các phần cần chứng minh trước compile là chuyển đổi block tại chỗ, lịch converter và cách tái tạo lịch sử block. Đối chiếu với decoder cổ điển và kiểm round-trip trước khi cấp phát lại word.

## Tài nguyên dự kiến

Input cố định 840 qubit nên mục tiêu `Q<900` chỉ chừa tối đa 59 qubit đồng thời ngoài vùng đầu vào. Tính cả inverse scaffold, root flag, dữ liệu định tuyến, lịch sử và converter. Đo `T_forward`, `T_reverse`, `T_phase` và peak `Q` riêng. Verifier chấm `R(eps_plus) Q^2 T`, với `T` là Toffoli-like trung bình mỗi shot. Kỳ vọng bỏ workspace của EEA và giảm số lượt xử lý; nghịch đảo, pivot động và tái tạo lịch sử có thể bù mất lợi ích.

## Kế hoạch kiểm chứng hypothesis

- Đối chứng từ [source](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/src/dqi/DQI-BASELINE/solution.py) và [config](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/src/dqi/DQI-BASELINE/configs/baseline.json) pin trên main, cùng [run dev](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5/verifier.json) và [provenance](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5/provenance.json). Provenance baseline lịch sử là pre-Git.
- Dự đoán ban đầu `Q<900` và `Q^2 T <= 0.5` lần baseline trên dev_5min 4096 shots, seed 20261106, cùng harness và môi trường. Mốc 0,5 định lượng yêu cầu giảm mạnh trong hypothesis.
- Ủng hộ khi không có lỗi syndrome, ancilla hay pha trên tập kiểm tra, đạt cả hai mục tiêu tài nguyên và score dev thấp hơn baseline tương thích. Bác bỏ ứng viên nếu mất dữ liệu, sai pha, vượt ngân sách qubit hoặc không đạt mức giảm đã đặt trước.
- Giới hạn một cấu hình đầu tiên. Nếu thiếu lịch block thuận nghịch và converter đạt ngân sách, dừng ở kiểm tra khả thi. Khi có build đúng hợp đồng, bàn giao smoke rồi dev_5min cho owner.
- Kiểm độc lập với trọng số 0/1/35, vị trí biên, ca pivot zero/degree gap và các mask phân biệt lỗi pha. Ứng viên cuối chạy full hoặc seed độc lập có đối chứng cùng profile.

## Kết luận và phiên bản tái lập

Chưa có mạch ứng viên hoặc kết quả chấm H3.

### Kiểm tra khả thi trước build

- Mô hình cổ điển GF(2^12) khôi phục đúng syndrome, locator, numerator và biên độ lỗi trên 432 ca với trọng số 0–35, seed 20261108, gồm lỗi đơn tại vị trí 0 và 4094. Kiểm 630 leading minor; các prefix khả nghịch khớp tổng bậc quotient tích lũy trong những ca kiểm. Khi đổi A sang omega phải đệm A đủ w hệ số trước khi đảo thứ tự. Bỏ đệm làm sai omega khi syndrome đầu bằng zero.
- Kiểm thêm 35 ca cưỡng bức bước nhảy đầu dài 1–35. Chọn w điểm khác nhau a_i và biên độ lỗi bằng nghịch đảo của `a_i * product_{j!=i}(a_i+a_j)`, tạo `S_1..S_(w-1)=0` và `S_w=1`. Mô hình khôi phục đúng syndrome và biên độ; leading minor đầu tiên khả nghịch có kích thước w. Vì vậy nhánh pivot đơn và nhảy tối đa 2 chưa đủ cho toàn bộ miền cam kết.
- Probe một điểm Forney với 840 dây đang sống và cách cấp phát baseline cho `Q=913`. Scaffold nghịch đảo chiếm 48 qubit, inverse và located mỗi thanh ghi 12 qubit, root flag 1 qubit. Mốc này đo riêng kernel, chưa tính metadata decoder. Layout giữ cả 70 word sống không thể dùng nguyên lịch này và đạt Q<900.
- Dừng trước build ứng viên. Mô hình reciprocal dùng bộ nhớ cổ điển ngoài dãy hệ số và mô hình Hankel chỉ kiểm điểm nhảy. Cần lịch gate block-Wronskian và converter đảo được cho các ca nhảy dài, kèm chứng minh wire nào đã sạch ở pha Forney để tính đỉnh Q. Các probe chưa đo chi phí forward/reverse của ứng viên hay điểm dev.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa có | Chưa có | Chưa chấm |
| Full | Chưa có | Chưa có | Chưa chấm |

Điểm và các run đối chứng nằm trong [SCORES.md](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/src/dqi/SCORES.md).
