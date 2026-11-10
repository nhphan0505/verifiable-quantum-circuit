# [DQI-45] Ghép Bézout tại chỗ và quét pha 11 Toffoli vào decoder Schur Narrow Return, kiểm chứng vùng syndrome mượn

Loại: Kết hợp nhiều phương án.

## Các file gốc và thành phần kế thừa

- [DQI-27](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/96a39559419067f98dc7cde47ed03ee615de075e/src/dqi/DQI-27/solution.py), source `96a39559419067f98dc7cde47ed03ee615de075e`: Schur in-place, cursor Narrow Return, converter và history streaming. Mốc narrow_return đã dev/full PASS, Q=890, T tĩnh=11647130. Không sửa branch/PR DQI-43 đang chờ review.
- [DQI-19](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c0cf9dfb45b62ba7eeb8588c87b0066409880046/src/dqi/DQI-19/solution.py), source `c0cf9dfb45b62ba7eeb8588c87b0066409880046`: tensor Rank-42 và input masking. Không phụ thuộc source DQI-43 chưa merge; ghép trực tiếp primitive đã có trên main.
- [DQI-21](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/2bfda079587dfdc4b85b1245417b7acca52362ff/src/dqi/DQI-21/solution.py): mô hình reciprocal, field basis và zero-test/MBUC 11 T; không mượn các bank phụ lớn của layout reference.
- [DQI-32](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/10173eea73cf850e4290989c15e31de384f51af0/src/dqi/DQI-32/solution.py): đối chiếu structured Bézoutian model, packed polynomial division và giới hạn coherent schedule. Issue/PR #32/#33 đã đóng, PR chưa merge, evaluator overwrite reference từng có dev PASS nhưng Q=3841 và score kém baseline. Không nhận lại Issue của owner cũ hoặc gọi packed replay model là circuit đã kiểm chứng.
- Note ready đã merge trên main: [arxiv-2610.22367 SI I.1](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/6a4a4b0/research/dqi/papers/arxiv-2610.22367/note.md), [mrmeows](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/6a4a4b0/research/shared/discussions/kaggle-mrmeows-open-circuits-v3/note.md), [Kirill audit](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/6a4a4b0/research/dqi/discussions/kaggle-kirilltym-conditional-uncompute-audit/note.md). Chỉ đọc note, không PDF/notebook nguồn. Số 73k/Bézout và 500-600k toàn mạch trong ý tưởng là mục tiêu tham khảo, chưa là số đo thiết kế này. Giữ Apache-2.0 và attribution của các nguồn code.

## Cách kết hợp và hợp đồng

GF(2^12) đúng modulus/basis Kickmix, 70 syndrome quantum 12 bit, 4095 mask cổ điển runtime E0..E4094, tối đa 35 lỗi. Oracle chỉ tạo pha parity(mask AND error); phải khôi phục syndrome, locator/evaluator, lịch sử và ancilla. Không bỏ 71 vị trí theo mask offline, không cutoff độ bậc, không làm tròn.

1. Dùng extraction và converter của Schur Narrow Return để nhận dạng chính xác layout tại boundary trước phase. Cần kiểm trên circuit thật chứ không suy bank sạch từ paper. Audit weight 0..35, syndrome đầu zero, lỗi đơn ở 0/4094 và forced valuation jumps 1..35. Ghi giá trị từng word đầu/cuối boundary, xác minh locator/omega theo lỗi độc lập và kiểm khôi phục dữ liệu/pha khi đảo. Dây sạch phải về |0> trên toàn miền reachable, không chỉ bằng zero ở một mẫu.
2. Xác định f(z) và w(z) theo phase Schur: den/num interleaved, den chứa các hệ số không hằng của locator có hằng số chuẩn hóa 1; implicit coefficient và prefactor cần tự đối chiếu. Native phase dùng beta=alpha^(-j), các word i tiến bằng beta^(i+1), nên cả numerator và odd-derivative cùng mang một beta; không chép nguyên prefactor z^-1 của packed EEA DQI-21.
3. Với f square-free, tách f=E²+z O², deg E/O<=17. Tìm A E+B O=1, Psi=B²+z A², suy ra Psi*f'=1+A²*f. Mục tiêu tại chỗ là phép đổi evaluator R=w*Psi mod f, inverse w=R*f' mod f. Khi f có bậc 0 thì identity, phase không-error là +1; f zero/non-square-free ngoài promise cần chặn rõ. Với degree d biến thiên, giữ đủ quotient/remainder hoặc chứng minh deg w<d; không bỏ word cao theo giả thiết typical.
4. Model structured Bézoutian dùng B(f,f')=M_f' B(f,1). Giải B(f,f') u=w rồi R=B(f,1)u qua các phép swap, scale khác zero và shear. DQI-32 cung cấp identity/factorization làm đối chiếu; circuit mới chỉ được dùng lịch có quantum coefficients, degree/pivot quantum control và inverse replay đúng. Các coefficient/pivot của một fixture không được cắm thành hằng cho circuit nhận locator quantum tùy ý.
5. Triển khai tiền xử lý trực tiếp trong 70 word: nếu có bank sạch đã chứng minh, mượn theo liveness; nếu không, cần factorization overwrite giữ đủ dữ liệu để phục hồi. Record quotient/degree/flags và inverse scaffold đều tính vào Q_peak. Narrow Return chỉ trả metadata đã giải mã được, không xóa thông tin hoặc tự cấp thêm bank không đếm. Chỉ dùng HMR khi chỉ rõ hàm phase correction từ dữ liệu còn sống. Mô hình đại số khả nghịch chưa thay oracle cleanup/gate schedule.
6. Khi R có sẵn và f đã phục hồi, sweep mọi beta: evaluate f và R bằng CNOT/nhân hằng, zero-test 12 bit với 11 temporary AND và del_and cleanup; runtime masks chỉ điều khiển pha Clifford trên giá trị R(beta). Đúng convention error=w(beta)/f'(beta), nên R(beta) trực tiếp là error, không thêm beta^-1 nếu mapping Schur xác nhận như trên. Sau sweep phục hồi hệ số, inverse R->w, undo preprocessing/conversion/extraction. Đếm thuận/đảo/sweep riêng; hướng tới 45045 T cho sweep, không gọi đó là chi phí toàn decoder.

## Không tương thích và gate bắt buộc

Paper có 35 syndrome word zero sau bước tích syndrome tam giác với locator lưu riêng. Schur packed có locator và evaluator cùng chiếm 70 word; ở weight35 có thể không còn bank zero. Đây là giả thiết cần kiểm đầu tiên. Không áp liveness paper trực tiếp vào layout Schur. Mượn word zero ở weight nhỏ phải có quantum routing và xử lý weight35; không dùng nhánh host dựa trên input quantum.

Mục tiêu Q<=892, T toàn mạch khoảng 500000-600000 và gain40-45× chỉ là target. Schur repo hiện có nhiều triệu T ở extraction/conversion; thay phase đơn thuần chưa chứng minh giảm toàn mạch đến target. Không dựng một reference Q hàng nghìn rồi gắn nhãn đạt in-place. DQI-39 đã có Q892/T~395k, là đối chứng incumbent riêng; target500-600k cùng Q chưa mặc nhiên thắng mốc đó.

## Kế hoạch kiểm chứng hypothesis

- Đối chứng: DQI-27 narrow_return source/config/run đã có trên main; DQI-43 đang chờ review chỉ là đối chứng tham khảo cho Rank-42 trên Schur. DQI-39 dùng để đánh giá tính thực dụng sau cùng, không tự ghép gate stream V5 thành implementation H6.
- Dự đoán: trả cursor và overwrite evaluator có thể giới hạn ancilla nếu tìm được reversible factorization có lịch sạch. Chưa có chứng minh đạt Q892 hoặc T600k. Chọn một config screening/structured đầu tiên ở bước03, không quét hàng loạt.
- Kiểm chứng: model độc lập f, w, Psi, R và inverse trên weight0..35; root parity trên 4095 điểm với runtime masks. Circuit boundary audit trên GF(2^12) đầy đủ70 word, gồm all degree jumps và weight35; primitive/sweep kiểm value/phase/workspace qua nhiều HMR seed. Không gọi component hoặc model PASS là verifier PASS.
- Gate trước build submission: chứng minh mapping và mọi bank mượn sạch; có coherent variable-degree schedule và phase cleanup cả hai chiều; Q_peak<=892; đếm tổng extraction/preprocessing/sweep/reverse và khả năng đạt ngân sách. Nếu không qua gate, ghi screening thất bại với counterexample/cost thật và dừng trước full build, không tạo artifact giả hoặc chạy grader trên circuit thiếu khối tiền xử lý. Chỉ mở reference vượt ngân sách khi người dùng giao rõ thay đổi điều kiện dừng.
- Nếu qua gate: commit source/config trước compile, dựng artifact/provenance theo schema và bàn giao thành viên chấm dev_5min profilev1/seed20261106/4096 shots. Ủng hộ lợi ích khi score thấp hơn đối chứng tương thích, value/phase/workspace đúng. Bác bỏ nếu mapping/liveness sai hoặc Q²T/R không giảm. Timeout chưa chứng minh sai mạch.
- Ứng viên cuối cần full102400 shots hoặc holdout có đối chứng, cùng ca biên 0/1/35 và tụt bậc. Không tự chấm hoặc merge; các kết quả nguồn và ảnh là tham khảo.

## Kết luận và phiên bản tái lập

Đã triển khai và chạy screening bằng source/config commit `842c243db8b953c5abafed976f31b7bf4e51a537`. Trước đó commit `51da796cf712214c0922b552730d4526b14ca5c5` đã chạy lượt đầu với kernel dùng 3 parity/product scratch; giữ nguyên báo cáo lượt đầu, không ghi đè. **Trạng thái SCREENED_NOT_BUILT:** mô hình và các component đã được kiểm; chưa có coherent preprocessing hoặc submission H6. Chưa có dev/full score, không thêm dòng SCORES và không tạo provenance giả cho artifact không tồn tại.

## Cấu hình, implementation và kết quả screening bước 03

Config duy nhất [inplace_probe.json](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/842c243db8b953c5abafed976f31b7bf4e51a537/src/dqi/DQI-45/configs/inplace_probe.json): m4095/n70/degree12, mode=screening_only, seed20261110, hai random fixture cho mỗi weight0..35, measurement seeds4501/4502/4503, Q target892 và total T target600000. Không có setting submission. [solution.py](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/842c243db8b953c5abafed976f31b7bf4e51a537/src/dqi/DQI-45/solution.py) từ chối compile nếu không có `--screen`, vì chưa có circuit tiền xử lý coherent để đưa cho grader.

Model structured Bézoutian kế thừa phép factorization từ DQI-32 nhưng không dùng coefficient của fixture như hằng số trong circuit có locator quantum. Mô hình tính R và inverse trên **109 ca**, bao phủ mọi weight0..35, lỗi đơn0/4094 và 35 ca cưỡng bức jump1..35. R khớp phép nghịch đảo đa thức độc lập, inverse khôi phục w, và **1892** root values khớp biên độ lỗi gốc. Đây là model số học, chưa là schedule quantum xử lý degree/pivot và uncompute.

Kernel Rank-42 mới conjugate từng CCX bằng map parity trên chính hai input word và map fanout trên target. Với output mask p và pivot k trong p, map tuyến tính L thỏa L(e_k)=p, nên L*CCX*L cộng đúng p*(parity(lhs)&parity(rhs)) vào target bất kỳ. Hoàn nguyên toàn bộ basis mỗi hạng. Không có scratch cho 42 tích và không đo target; nhánh có control vẫn dùng 12 masked-input AND, del_and chỉ sau khi các input basis đã trả về ban đầu. Đây là phép sửa triển khai sau kết quả Q893 của lượt đầu, giữ nguyên hypothesis/config và chi phí 42/54 T.

| Component | Kết quả đo | Giới hạn |
| --- | --- | --- |
| Rank-42 không control | 196608 ca, 42 T, 36 tổng qubit | arbitrary target, zero/equal/random operands, 3 seed |
| Rank-42 có control | 393216 ca, 54 T, 49 tổng qubit | control0/1, phase và masked-input cleanup đúng |
| Schur boundary đầy đủ | 109 ca/seed ×3, Q peak890 | GF(2^12), đủ70 word, model locator/evaluator khớp, forward/reverse khôi phục syndrome và ancilla |
| Sweep với R cho sẵn | 45045 T, 875 qubit, đủ4095 vị trí | 5 ca weights0/1/7/17/35 ×3 seed, runtime masks; không tính R coherent |

Tất cả component trên có 0 lỗi value/phase/workspace trong các ca kiểm. Không gọi đây là decoder dev/full PASS. Convention Schur đã được kiểm: locator f(z)=1+sum den_i*z^(i+1), omega(z)=sum num_i*z^i, beta=alpha^-j. Native sweep có cùng factor beta ở numerator và z*f', nên với R=omega/f' mod f, kernel mới dùng **R(beta)** trực tiếp; không nhân thêm beta^-1 của convention EEA DQI-21.

### Phản ví dụ bank sạch

Lượt seed4501 có fixture weight35 mà **toàn bộ70 coefficient word ở boundary đều khác zero**. Không có slot luôn zero trong tập109 fixtures. Witness tạo lại từ config seed20261110, positions bắt đầu `2733,3496,673,452,2620`, values bắt đầu `554,1195,3964,1896,946`; báo cáo JSON chứa đủ35 positions,35 values và70 packed words. Điều này bác bỏ cách mượn một bank35 word zero đã tồn tại tại boundary hiện tại; không bác bỏ mọi phép biến đổi ghi đè tại chỗ.

Còn có cận thông tin cho yêu cầu giữ sạch35 word cùng lúc: riêng lỗi weight35 có `C(4095,35)*4095^35` input khác nhau và syndrome70 phân biệt chúng vì Vandermonde trên hiệu support<=70 khả nghịch. Log2 số input khoảng706.8407, cần ít nhất707 qubit để giữ thông tin trong một encoding reversible. Với tổng892 qubit mà420 qubit sạch, chỉ còn472 qubit mang thông tin, không đủ. Cận này giả thiết không offload dữ liệu input vào classical output hoặc workspace ngoài ngân sách. Nó không cấm H6 dùng phép overwrite thay biểu diễn; nó loại suy luận rằng có thể giữ nguyên toàn bộ thông tin và đồng thời dành sẵn35 word sạch trong ngân sách này.

### Cận chi phí khi giữ lõi Schur hiện tại

| Stage giữ lại | Toffoli-like tĩnh |
| --- | ---: |
| Forward extraction | 2986703 |
| Forward conversion | 1063622 |
| Reverse conversion | 1063622 |
| Reverse extraction | 2986703 |
| Tổng lõi | **8100650** |
| Sweep11/điểm | 45045 |
| Tổng lạc quan, chưa tính Bézout | **8145695** |

Q của lõi sau đổi basis kernel là890 (lượt đầu893). Gate Q đạt cho **lõi**, chưa phải Q của một H6 đầy đủ; gate T600000 thất bại hơn13 lần ngay khi cho preprocessing chi phí0. Đây là cận của phép ghép giữ nguyên extraction/conversion trên repo, không phải định lý về mọi decoder Schur. Đạt target500-600k cần thay lịch extraction/conversion hoặc tái dựng một kiến trúc khác; giảm riêng khối phase không đủ.

## Bằng chứng, tái lập và quyết định dừng

Chạy từ worktree của DQI-45 bằng Python3.13.14/kickmix1.0.0/numpy2.5.4/scipy1.18.1:

```powershell
D:/GQA/.venv/Scripts/python.exe src/dqi/DQI-45/solution.py --config src/dqi/DQI-45/configs/inplace_probe.json --screen
```

Code xuất diagnostic JSON dưới `artifacts/dqi/DQI-45/` với timestamp mới, không ghi đè report cũ. Báo cáo cuối `inplace_probe.20261110T095058556025Z.screening.json` có SHA-256 `b173eff9d12092a2f2d2666a7decca7f4eac488b426d23e12331241468714bb0`; elapsed151.1477 giây là thời gian screening, không là runtime grader. Report chứa source/config hashes, command và helper hashes. Các report diagnostic ở artifacts ignored; kết luận kỹ thuật, counterexample tái lập và code được lưu trong Git. Không lưu chúng như build_only/provenance của một KMB giả.

**Dừng trước build submission theo gate đã đặt ở bước02:** giả thiết bank sạch không đúng cho layout giữ nguyên, T lõi vượt budget, và coherent variable-degree evaluator overwrite/cleanup vẫn chưa có. Giữ draft PR để lưu code/probe và kết quả âm; chưa nghiệm thu bước03 ở mức artifact BUILT, chưa bàn giao chấm local và chưa mở vòng config khác. Muốn tiếp tục cần một schedule cụ thể cho overwrite Bézout và thay phần lõi gây chi phí8.1triệu T; không tự đổi mục tiêu thành một reference nhiều qubit hoặc coi model số học là circuit.
