# [DQI-21] Thay nghịch đảo Forney từng vị trí bằng Bézout/reciprocal và quét pha, kiểm chứng mục tiêu 11 Toffoli mỗi điểm

Loại: Ý tưởng mới cho giai đoạn đánh giá lỗi và áp pha MBUC.

## Thuật toán và công thức

Kế thừa decoder EEA/giao diện từ [baseline](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/src/dqi/DQI-BASELINE/solution.py), Apache-2.0, src/LICENSE.txt; chỉ thay `_chien_search_and_forney_mbuc` và helper riêng của hướng. Giữ 222 vòng EEA chính, m=4095,n=70,degree=12, field basis/modulus và toàn bộ verifier. Chưa ghép tối ưu DQI-19 vào EEA chính để tách tác động H2.

Nguồn tham khảo chỉ là note ready đã merge ở commit `bb3a6311113217a69c64e88e9c3bb0513237a1f9`: [arxiv-2610.22367, SI I.1](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/dqi/papers/arxiv-2610.22367/note.md), [mrmeows v3, DQI/đặc số 2](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-mrmeows-open-circuits-v3/note.md), [verifier-in-loop, DQI](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-752897-verifier-in-the-loop/note.md). Metadata ready của note paper có đoạn coverage/review cũ chưa nhất quán; chỉ dùng các đồng nhất thức được tự đối chiếu, không suy ra tác giả đã cung cấp gate schedule. Không đọc PDF/notebook nguồn hoặc dùng các số 73000/45000 như kết quả project.

### Giao diện và bước ghép

Input là trạng thái EEA trước Chien/Forney, với `reg_b`, `n_b`, `n_B` và 4095 classical mask `E0..E4094` của verifier. Mask là dữ liệu cổ điển runtime, không cố định offline. Output chỉ là dấu pha; reg_b, EEA metadata, syndrome và quantum workspace phải phục hồi. Dùng `_pre_align_reg_b` thuận/ngược như baseline.

Sau alignment, đặt s(z)=sum_{k=0}^{35} reg_b[k] z^k và w(z)=sum_{k=37}^{71} reg_b[k] z^(71-k). Đọc lại range từ source tại commit nêu trên khi triển khai. Baseline tại vị trí j đánh giá z=alpha^j, sigma=s(z), sigma_prime=z*s'(z) (vì tổng hệ số bậc lẻ đã mang z^k), omega=w(z). Pha mục tiêu tại s(z)=0 là parity(mask_j & (w(z)/(z*s'(z)))). Không áp thẳng công thức paper vào các slice packed hoặc bỏ prefactor z. Xác minh mapping này trên mô hình/ca EEA thực trước compile ứng viên.

Nếu packed s có thừa nhân tử z^v do padding/đảo hệ số, deflate s=z^v*f bằng phép dịch có điều khiển và giữ v/tape để đảo; tại z!=0, s=0 iff f=0 và z*s'=z^(v+1)*f' ở nghiệm f. Kiểm tra trường hợp f hằng và s=0 trên no-error state thay vì chia zero hoặc giả định luôn bậc 35.

### Reciprocal bằng phân tách chẵn/lẻ và Bézout

Với f square-free, biểu diễn f=E(z)^2+z*O(z)^2, E_i=sqrt(f_2i), O_i=sqrt(f_(2i+1)), deg E,deg O<=17. Frobenius/square root trong field là map tuyến tính. E/O coprime trên locator hợp lệ; EEA phụ tìm A*E+B*O=g với g khác zero hằng. Chuẩn hóa A,B bằng g^-1 để A*E+B*O=1. Khi đó Psi=B^2+z*A^2 thỏa Psi*f'=1+A^2*f; Psi là reciprocal đúng tại nghiệm, không cần biểu diễn remainder chuẩn.

EEA phụ dự kiến là fixed-loop leading-term cancellation có tape để đảo, không nhánh Python theo dữ liệu lượng tử. Mỗi bước tính degree+1 (zero polynomial ->0), swap khi deg r0<deg r1, rồi r0 ^= q*z^shift*r1 và cập nhật hai cặp cofactor cùng phép biến đổi; q=leading(r0)/leading(r1), shift=degree difference. Tối đa 35 cancellation với hai input bậc <=17 vì tổng degree+1 giảm sau mỗi cancellation hoạt động. Nhánh đã dừng giữ nguyên và lưu running/swap/degree/quotient để undo; không cắt degree jumps hoặc pivot. Cofactor buffers phải có bound chứng minh hoặc mở rộng, không cắt dữ liệu ngầm. Nếu không chứng minh được layout/tape/biên, dừng trước compile decoder và báo phần thiếu.

### Vì sao mục tiêu 11/điểm cần thêm tiền xử lý

Quét trực tiếp w(z)*Psi(z) với control nghiệm vẫn cần một tích phi tuyến ngoài zero-test; note paper nêu 12+11=23/vị trí cho mô hình đó. Runtime mask có thể điều khiển Clifford, nhưng bản thân điều này không chứng minh tổng chỉ còn 11. Để nhắm 11, tính trước H(z)=w(z)*Psi(z) bằng convolution các hệ số quantum; chưa reduction modulo f thì bậc tối đa 69. Với deflation v, tiền xử lý thêm dịch hệ số Htilde=z^(35-v)*H; tại nghiệm không zero, lỗi là z^-36*Htilde(z). Bậc Htilde tối đa 104; đây là suy luận triển khai mới cần kiểm chứng và tính cả workspace/cost. Nếu xác minh packed locator không có nhân tử padding, dùng v=0 và có thể rút gọn prefactor về z^-1 với bound bậc nhỏ hơn.

Trong sweep 4095 vị trí, đánh giá f (hoặc s) và Htilde bằng XOR/Frobenius/nhân hằng CNOT; mask runtime chọn các CZ. Zero-test 12 bit dùng chain 11 `init_and` trên các bit đã complement; CZ giữa kết quả chain và bit đánh giá được condition bởi mask. Dọn chain bằng `del_and` ngược, phục hồi input complement; compute zero-test 11 Toffoli-like, cleanup Clifford/HMR. Không dùng hai `flip_if_equal` có thể tính lại chi phí 11 lần nữa. Prefactor z^-36 là hằng theo vị trí nên gộp vào step multipliers. Không bỏ 71 vị trí, không dùng mask của verifier để fit offline.

Sau scan, undo mọi step multiplier/evaluation, Htilde/H convolution, normalization/reciprocal, EEA phụ và deflation, rồi unalign reg_b. Các record/tape chỉ free sau khi về zero. Không đo giá trị locator/Bézout hoặc thay coherent control bằng classical branch. Chỉ HMR trong các primitive MBU có phase fixup đúng được dùng.

## Điều kiện đúng và sai số

- Promise verifier: lỗi trọng số <=35 trên GF(2^12); giữ little-endian field basis và convention syndrome/position của verifier. Đầu ra pha là parity bitmask, tương đương trace trong dual basis đúng; không dùng mask word trực tiếp như trace coefficient chưa đổi basis.
- Kiểm từng đồng nhất thức packed mapping, Bézout, reciprocal và prefactor. No-error/locator hằng có output phase 0 và workspace sạch; trọng số 1/35, tụt bậc lớn, E=0 hoặc O hằng phải có nhánh xác định.
- Không intentional approximation, cutoff hoặc overflow. Square-free/coprime phải suy từ locator hợp lệ sau deflation, không chỉ từ tên thuật toán. Không lấy giá trị gcd zero rồi normalize.
- Classical model chỉ chứng minh identity số học; kernel simulator kiểm phase/workspace; dev/full verifier mới là bằng chứng decoder. Không coi compile/kernel test là PASS toàn mạch.

## Tài nguyên dự kiến

Mục tiêu scan 11 Toffoli-like/điểm (45045 cho 4095 điểm) chỉ sau khi đã tạo Htilde; đây chưa phải số đo. Tổng cần tính đủ reciprocal/Bézout/cofactor, convolution, degree handling, forward+reverse và các nhánh biên. Số 73000 thuận hoặc 45000 sweep trong note thuộc cấu phần khác, không phải bảo đảm cho thiết kế này. Template tape/coef có thể tăng Q đáng kể; đánh giá cả R(epsilon_plus)*Q²*T, không chỉ scan T. Ghi chi phí thuận/đảo/sweep riêng trước kết luận; không che overhead chuẩn bị hoặc uncompute.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: baseline source/config tại commit bb3a631 nêu trên; full lịch sử `results/dqi/DQI-BASELINE/baseline/full/20261107T094931Z-local-full-5ed1c6`, dev lịch sử `results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5`. Python patch/harness khác local 3.13.7 nên không tính gain từ các run này. Các run baseline chạy lại ở worktree DQI-19 khớp môi trường nhưng thiếu build provenance; chưa đăng ký làm đối chứng chính thức.
- Dự đoán: bỏ inverse tại từng vị trí, scan chỉ 11 Toffoli-like sau tiền xử lý; tiền xử lý và Q có thể triệt tiêu lợi ích. Mục tiêu là tổng T và score giảm dưới cùng profile, không khẳng định 11 hoặc 73000 đã đạt.
- Ủng hộ/bác bỏ: bác bỏ implementation nếu sai phase/value/workspace, Bézout sai, không xử lý degree/no-error hoặc bỏ runtime masks. Bác bỏ lợi ích giảm T nếu tổng forward+reverse preprocessing+4095 sweep không thấp hơn khối gốc; nếu T thấp nhưng Q²T tăng, ghi kết quả âm về score. Đếm thực kernel/khối trước compile toàn decoder khi có thể.
- Điều kiện dừng: một config exact đầu tiên m=4095,n=70,degree=12, giữ EEA chính; không quét setting/cutoff. Dừng trước compile nếu mapping/corner case chưa chứng minh được, hoặc resource estimate không đáp ứng phạm vi đã nhận; không tự đổi hypothesis.
- Kiểm tra ứng viên cuối: dev_5min profile v1/seed 20261106/4096 shots; full hoặc seed độc lập và ca biên 0/1/35, degree drops. Thành viên tự chấm notebook; agent bàn giao artifact/hash/provenance sau BUILT, không tự chấm.

## Kết luận và phiên bản tái lập

Đã triển khai **probe tính khả thi**, không phải compiler submission đầy đủ, tại source commit `6b3318a36bbedf0abc62cf763efdb4fedc2ff786`. Probe không chạy verifier, không xuất artifact decoder hoặc ghi điểm. Kế hoạch materialize H riêng bị loại ở resource screening; H2 tổng quát chưa bị bác bỏ.

### Bằng chứng đã kiểm tra

- `--validate-packed`: tái tạo fixture từ EEA baseline đúng hash source `3bba2c941021749393d322c1b779e02dd7ec987c61c7b253a54fd2173968cdb4`, commit bb3a631. Sáu ca trọng số 0/1/1/1/7/35, gồm vị trí biên 0/4094 và các coset GF(8) tạo khoảng trống hệ số lớn. Sigma/omega khớp snapshot, syndrome được phục hồi. Không xuất submission từ mạch extraction.
- `--validate-model`: trên sáu fixture, kiểm identity A*E+B*O=1 và Psi*f'=1+A²*f; quét đủ 4095 điểm mỗi ca, ba mask runtime/điểm (zero/full/mask thay đổi), không mismatch giá trị hoặc parity so với native w/(z*s'). Cả sáu locator packed quan sát có valuation=0, degree bằng trọng số; no-error là locator hằng. Đây là kiểm tra ca, chưa phải chứng minh mapping cho mọi trạng thái EEA.
- `--validate-kernel`: kiểm đủ mọi cặp sigma/value 12 bit với mask thay đổi, cộng đủ mọi value/mask khi sigma=0, tổng 33554432 trường hợp. Không lỗi value/phase/workspace; point kernel dùng đúng 11 Toffoli-like, 35 qubit bao gồm 24 input. Con số này giả thiết error_value đã có, chưa tính tiền xử lý H/reciprocal.
- `--audit-resources`: build các block baseline trong bộ nhớ để đếm tĩnh, không chạy grader hoặc viết artifact. Baseline có Q=1893, T tĩnh=5725461; riêng khối Chien/Forney cũ=1444737. Giữ EEA chính cần 1803 quantum wire sống qua sweep (hai mảng 73x12 bit và metadata).

### Quyết định và điều kiện chặn bước 03

Với layout giữ riêng 70 hệ số H (840 qubit), Q ít nhất 2643 chỉ tính state EEA còn sống và H. Coi **mọi** chi phí/workspace tiền xử lý, evaluation và cleanup bổ sung là zero, thay toàn block Forney bằng 4095x11=45045 Toffoli thì T tĩnh lạc quan vẫn là 4325769. Proxy Q²T của layout này bằng 1.4728074136 lần baseline, tức cao hơn 47.2807%. Ngay cả giả thiết reduction H mod f xuống 35 hệ số (420 qubit), Q=2223 cho tỷ số lạc quan 1.0419108503, cao hơn 4.1911%.

Đây là **screening cấu trúc tĩnh** cho cách lưu riêng hệ số trong khi giữ nguyên state EEA, không phải score verifier hoặc định lý bác bỏ mọi H2; classical mask skips/cận lỗi/chi phí thực thi cần grader thật nếu có decoder. Tuy vậy ngay mô hình lạc quan đã không có lợi, nên không compile decoder theo layout này hoặc bàn giao baseline giả làm ứng viên. Tăng workspace Bézout/tape/convolution chỉ làm thiết kế lưu riêng tệ hơn mô hình này.

Bước 02 đã có Issue/branch/draft PR và thiết kế. Bước 03 hiện **chưa nghiệm thu artifact BUILT**: còn cần biến đổi Bézout/Hankel tại chỗ (ví dụ thay đổi evaluator trong register sống rồi đảo được), với lịch gate đầy đủ, invariant cofactor/degree-drop/no-error, workspace bound và phase cleanup. Note cung cấp identity và số liệu tham khảo nhưng chưa cung cấp lịch này; classical xgcd trong probe không được coi là quantum preprocessing. Không tự đổi hypothesis, giảm EEA chính hoặc mở rộng sang BM trong Issue này.

Không có JSON verifier, dev/full PASS, score hoặc build_only provenance cho decoder chưa tồn tại. Giữ Issue mở và PR draft để hoàn thiện biến đổi tại chỗ; nếu tiếp tục cần thay thế phần preprocessing rồi kiểm lại tổng Q²T, không chỉ 11/vị trí.

### Tái lập probe

Dùng Python 3.13.7, kickmix 1.0.0, numpy 2.5.4 tại source commit `6b3318a36bbedf0abc62cf763efdb4fedc2ff786`, baseline helper tại bb3a631/hash nêu trên. Chạy từ root với `--config src/dqi/DQI-21/configs/exact_probe.json` và một trong các option `--validate-packed`, `--validate-model`, `--validate-kernel`, `--audit-resources`. Output là JSON probe qua stdout, không phải verifier result; config này không có artifact để chấm notebook. Code/config đã commit; các số trong phần này được đo lại bằng đúng snapshot đó.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa có | Chưa có | Chưa chấm |
| Full | Chưa có | Chưa có | Chưa chấm |

Probe model/kernel/resource: [solution.py](solution.py). Config chỉ cho probe: [exact_probe.json](configs/exact_probe.json). Điểm: [SCORES.md](../SCORES.md).
