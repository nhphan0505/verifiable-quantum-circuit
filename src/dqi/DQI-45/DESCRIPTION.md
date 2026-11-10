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

Chưa triển khai hoặc đo H6 sửa lại. Chưa có artifact, source build SHA hay score; mốc dev/full để trống đến khi có bằng chứng thật. Bước03 phải hoàn thiện schedule và resource gate trước khi bàn giao chấm.
