# [DQI-21] Thay nghịch đảo Forney từng vị trí bằng Bézout/reciprocal và quét pha, kiểm chứng mục tiêu 11 Toffoli mỗi điểm

Loại: Ý tưởng mới cho giai đoạn đánh giá lỗi và áp pha MBUC.

## Thuật toán và công thức

Kế thừa decoder EEA/giao diện từ [baseline](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/src/dqi/DQI-BASELINE/solution.py), Apache-2.0, src/LICENSE.txt; chỉ thay `_chien_search_and_forney_mbuc` và helper riêng của hướng. Giữ 222 vòng EEA chính, m=4095,n=70,degree=12, field basis/modulus và toàn bộ verifier. Chưa ghép tối ưu DQI-19 vào EEA chính để tách tác động H2.

Nguồn tham khảo chỉ là note ready đã merge ở commit `bb3a6311113217a69c64e88e9c3bb0513237a1f9`: [arxiv-2610.22367, SI I.1](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/dqi/papers/arxiv-2610.22367/note.md), [mrmeows v3, DQI/đặc số 2](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-mrmeows-open-circuits-v3/note.md), [verifier-in-loop, DQI](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-752897-verifier-in-the-loop/note.md). Metadata ready của note paper có đoạn coverage/review cũ chưa nhất quán; chỉ dùng các đồng nhất thức được tự đối chiếu, không suy ra tác giả đã cung cấp gate schedule. Không đọc PDF/notebook nguồn hoặc dùng các số 73000/45000 như kết quả project.

### Giao diện và bước ghép

Input là trạng thái EEA trước Chien/Forney, với `reg_b`, `n_b`, `n_B` và 4095 classical mask `E0..E4094` của verifier. Mask là dữ liệu cổ điển runtime, không cố định offline. Output chỉ là dấu pha; reg_b, EEA metadata, syndrome và quantum workspace phải phục hồi. Dùng `_pre_align_reg_b` thuận/ngược như baseline.

Sau alignment, đặt s(z)=sum_{k=0}^{35} reg_b[k] z^k và w(z)=sum_{k=37}^{71} reg_b[k] z^(71-k). Đọc lại range từ source tại commit nêu trên khi triển khai. Baseline tại vị trí j đánh giá z=alpha^j, sigma=s(z), sigma_prime=z*s'(z) (vì tổng hệ số bậc lẻ đã mang z^k), omega=w(z). Pha mục tiêu tại s(z)=0 là parity(mask_j & (w(z)/(z*s'(z)))). Không áp thẳng công thức paper vào các slice packed hoặc bỏ prefactor z. Xác minh mapping này trên mô hình/ca EEA thực trước compile ứng viên.

Trên miền RS hợp lệ của EEA kế thừa, packed s là scalar khác zero nhân tích các (z+alpha^j) cho vị trí lỗi, nên s(0)!=0; no-error là s hằng khác zero. Bản reference dùng trực tiếp f=s, không cần deflation. Mapping packed đã kiểm từ EEA thật và mô hình; không giả định luôn bậc 35. Locator zero hoặc không square-free nằm ngoài promise này; không dùng như trường hợp no-error hợp lệ.

### Reciprocal bằng phân tách chẵn/lẻ và Bézout

Với f square-free, biểu diễn f=E(z)^2+z*O(z)^2, E_i=sqrt(f_2i), O_i=sqrt(f_(2i+1)), deg E,deg O<=17. Frobenius/square root trong field là map tuyến tính. E/O coprime trên locator hợp lệ; EEA phụ tìm A*E+B*O=g với g khác zero hằng. Chuẩn hóa A,B bằng g^-1 để A*E+B*O=1. Khi đó Psi=B^2+z*A^2 thỏa Psi*f'=1+A^2*f; Psi là reciprocal đúng tại nghiệm, không cần biểu diễn remainder chuẩn.

EEA phụ dự kiến là fixed-loop leading-term cancellation có tape để đảo, không nhánh Python theo dữ liệu lượng tử. Mỗi bước tính degree+1 (zero polynomial ->0), swap khi deg r0<deg r1, rồi r0 ^= q*z^shift*r1 và cập nhật hai cặp cofactor cùng phép biến đổi; q=leading(r0)/leading(r1), shift=degree difference. Tối đa 35 cancellation với hai input bậc <=17 vì tổng degree+1 giảm sau mỗi cancellation hoạt động. Circuit dùng 36 vòng cố định để bao gồm swap định hướng cuối khi r0 vừa thành zero, r1 là gcd. Nhánh đã dừng giữ nguyên và lưu running/swap/degree/quotient để undo; không cắt degree jumps hoặc pivot. Mỗi remainder/cofactor có 18 word. Trong một phép chia Euclid, deg(source)+shift của remainder không vượt degree remainder đích; với hai cofactor, bound của extended EEA không vượt bậc input đối diện, tối đa 17, kể cả row cho remainder zero cuối. Do đó cyclic word shift 18 vị trí không wrap hệ số khác zero khi q!=0; nếu q=0, mọi cập nhật bằng zero. Degree+1/shift dùng 5 bit, quotient 12 bit, swap 1 bit; giữ transcript đến khi đảo. Kiểm tra invariant riêng bao phủ mọi trọng số 0..35 và ca tụt bậc.

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

### Quyết định tiếp tục sau screening

Probe tại commit `6b3318a36bbedf0abc62cf763efdb4fedc2ff786` xác nhận identity reciprocal/mapping packed và kernel 11 Toffoli/điểm, nhưng layout giữ riêng 70 hệ số H có proxy tĩnh Q²T lạc quan cao hơn baseline 47.2807%; 35 hệ số riêng vẫn cao hơn 4.1911%. Đây là kết quả âm về layout lưu riêng, không bị rút lại hoặc coi như score verifier.

Sau đó người dùng giao tiếp tục bước 03 rồi 04 để tự chấm local. Vì vậy thay đổi **điều kiện dừng trước build**: dựng một implementation reference coherent/exact để đo correctness và chi phí thực, dù dự đoán score kém. Tiêu chí lợi ích Q²T ban đầu vẫn giữ: nếu score xấu hơn thì ghi kết quả âm; không đổi tiêu chí để gọi implementation này là tối ưu. Chỉ một config build đầu tiên [bezout_reference.json](configs/bezout_reference.json), m=4095,n=70,degree=12, aux_steps=36, layout=materialized_exact. [exact_probe.json](configs/exact_probe.json) giữ nguyên, chỉ chạy probe và không có artifact grader.

### Hiện thực coherent reference

Code [solution.py](solution.py) đã bổ sung compiler đầy đủ cho decoder: lớp con baseline chỉ thay Chien/Forney, EEA chính vẫn 222 vòng. E/O lấy bằng Frobenius inverse tuyến tính; auxiliary EEA giữ hai remainder và bốn cofactor, mỗi polynomial 18 word; 36 step transcript chứa degree+1, swap, shift, quotient. Leading coefficient được chọn bằng unary iteration, ratio dùng GF division native (divisor zero sau khi dừng cho quotient zero). Không nhánh Python theo dữ liệu quantum, không cutoff.

Chuẩn hóa a0/b0 tại chỗ bằng gcd g: compute word*g^-1 vào một temp, HMR/CZ xóa word cũ bằng quan hệ old=new*g, rồi swap. Khi đảo, scale lại bằng g trước khi replay transcript ngược. Cách này tiết kiệm 432 qubit so với copy hai cofactor chuẩn hóa riêng; g và scaffold inverse giữ đến khi cleanup, g!=0 do E/O coprime trên locator hợp lệ.

H=w*(B²+z*A²) có 70 field word. Mỗi tích hệ số dùng 42 temporary AND từ tensor DQI-19 đã merge; chỉ mượn tensor, không đổi arithmetic EEA chính. Square mỗi cofactor vào một temp field để tránh giữ 36 word Psi riêng. Erase H bằng HMR từng bit và gf2_phase_by_product cho từng cặp convolution để sửa pha, zero Toffoli ở lượt erase H. Undo normalization, quotient/degree/swap transcript, E/O initialization rồi unalign. Sweep đánh giá H(z)/z bằng step alpha^(k-1), sigma bằng alpha^k; mask runtime chỉ điều khiển Clifford. Point chain compute 11 AND, CZ pha, del_and ngược, inputs phục hồi.

Nguồn compile phụ thuộc hai helper read-only được pin hash: baseline tại bb3a631 (SHA-256 `3bba2c941021749393d322c1b779e02dd7ec987c61c7b253a54fd2173968cdb4`) và DQI-19 tại c0cf9df (SHA-256 `3798b608825c8ca741aaf4cf1d7913d87b650f2be55242a35dc769b8cd47c298`). Provenance build phải ghi dependency closure này ngoài hash solution/config của ID.

### Kiểm tra trước compile submission

- Probe cũ: sáu packed fixture 0/1/1/1/7/35 từ EEA native; identity Bézout/reciprocal và 4095 điểm/fixture; kernel 33554432 trường hợp, không lỗi value/phase/workspace. Con số 11 chỉ là sweep sau preprocessing, không ẩn chi phí tạo H.
- `--validate-aux-model`: 114 locator hợp lệ, bao phủ tất cả trọng số 0..35 và các ca sparse; tối đa 35 cancellation, cofactor degree tối đa 17, không wrap hoặc lỗi Bézout. Đây là mô hình invariant, không verifier.
- `--validate-aux-circuit`: auxiliary circuit coherent trên 18 ca, gồm no-error, edge roots, degree gaps và random locator; normalized A*E+B*O=1, gcd nonzero constant, r1=0; input phục hồi, không phase/workspace error sau đảo. Output snapshot chỉ có trong mạch unit test.
- `--validate-phase-block`: toàn bộ replacement phase block trên 10 ca sparse/dense (gồm trọng số 0/1/7/35 và random 2/17/34/35), mỗi ca quét 4095 điểm với mask runtime khác nhau. Không lỗi giá trị, pha hoặc workspace. Component test không chạy verifier submission và không tạo dev/full PASS.

Component aligned có 721404 Toffoli-like tĩnh, so với 1444737 của block Chien/Forney baseline gồm alignment; cần cộng alignment và EEA chính khi build toàn mạch. Chi phí thuận, reverse, convolution và sweep được tách trong báo cáo component. Workspace tăng lớn; chưa có bằng chứng score giảm và dự đoán score cao hơn baseline do Q². Wall time từ unit test không phải benchmark grader.

### Build và bàn giao

Commit source/config trước compile; dùng `.venv` Python 3.13.7, kickmix 1.0.0, numpy 2.5.4, scipy 1.18.1. Từ root chạy `./.venv/bin/python src/dqi/DQI-21/solution.py --config src/dqi/DQI-21/configs/bezout_reference.json`. TRACK/ID/output suy từ vị trí solution, config phải resolve trực tiếp trong configs/, output stem trùng config. Artifact mặc định `artifacts/dqi/DQI-21/bezout_reference.kmb`; chỉ ghi đè khi có --overwrite chủ động. Đã **BUILT** từ source commit `433dd403bc03a2b346c36314967a4d9665cefbbb`; [provenance](../../../results/dqi/DQI-21/bezout_reference/build_only/20261108T141940Z-local-build/provenance.json), [build record](../../../results/dqi/DQI-21/bezout_reference/build_only/20261108T141940Z-local-build/build.json), [component validation](../../../results/dqi/DQI-21/bezout_reference/build_only/20261108T141940Z-local-build/phase_block_validation.json). Artifact có SHA-256 `381b187b980a3ddfa0337e0c3ded9fe8b72cc897788184320e1f44d83a0b0669`, 838593417 bytes, Q=5042, T tĩnh=5009520, 82641733 instruction. So baseline tĩnh: T giảm 12.5045%, nhưng proxy Q²T tăng lên 6.207120 lần do workspace. Không coi proxy này là score verifier hoặc kết luận full PASS.

Các phần aligned phase đo tĩnh riêng: Bézout thuận 313011, H convolution 52920, sweep 4095 điểm 45045, H erase 0, Bézout reverse 310428 Toffoli-like, tổng 721404. Alignment gốc thêm 7392, tổng replacement 728796 so với Chien/Forney gốc 1444737. Giữ cả chi phí thuận/đảo/preprocessing, không chỉ công bố 11/điểm. Các báo cáo unit và 21 tests repo nằm cùng record build; source/config được đối chiếu snapshot trước/sau compile.

Sau build, thành viên mở notebook trong worktree **GQA-DQI-21**, kernel `.venv` Python 3.13.7, chọn TRACK=dqi, MODE=dev_5min, EXPERIMENT_ID=DQI-21, CONFIG_NAME=bezout_reference, OWNER=trng-hminh. Giữ profile v1/seed 20261106/4096 shots. Results tự lưu `results/dqi/DQI-21/bezout_reference/dev_5min/<run-id>/`. Agent dừng sau bàn giao; bước 04 chỉ thực hiện khi có results thật. Không tự chạy grader, không sửa verifier/harness/notebook/SCORES hoặc tạo score trong bước 03.

Chưa có run dev/full của decoder DQI-21. Baseline local cùng môi trường từ DQI-19 vẫn thiếu provenance build và chưa đăng ký chính thức; không suy đoán SHA hoặc tính hệ số formal từ baseline khác patch/harness. Khi phân tích phải giữ cả giới hạn đối chứng và kết quả âm nếu có.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa có | Chưa chấm | Chưa chấm |
| Full | Chưa có | Chưa chấm | Chưa chấm |

Mã: [solution.py](solution.py). Config build: [bezout_reference.json](configs/bezout_reference.json). Probe: [exact_probe.json](configs/exact_probe.json). Điểm: [SCORES.md](../SCORES.md).
