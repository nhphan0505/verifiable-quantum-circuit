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

Config schur đã dựng đủ 4095 vị trí với 900 qubit. Mạch phát ra 24.424.740 cổng Toffoli-like và artifact có dung lượng 2,19 GB. Đây là số đếm cổng tĩnh của build. Kết quả chấm notebook chưa có. Source dựng tại f7640b3. [Provenance](../../../results/dqi/DQI-23/schur/build_only/20261108T153618Z-local-build/provenance.json) · [Build metrics](../../../results/dqi/DQI-23/schur/build_only/20261108T153618Z-local-build/build_metrics.json)

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
