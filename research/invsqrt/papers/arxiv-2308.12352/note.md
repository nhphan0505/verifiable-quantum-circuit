# Quantum computation of stopping power — nội suy bậc ba và Newton–Raphson cho invsqrt

Status: draft
Track: invsqrt
Source: arXiv:2308.12352v1; metadata và SHA-256 trong source.json
Version: v1 ngày 2023-08-23; bản PDF local 37 trang, đọc ngày 2026-11-07

- Tác giả: Nicholas C. Rubin, Dominic W. Berry, Alina Kononov, Fionn D. Malone,
  Tanuj Khattar, Alec White, Joonho Lee, Hartmut Neven, Ryan Babbush, Andrew D. Baczewski.
- Nguồn: [PDF local](paper.pdf), [arXiv v1](https://arxiv.org/abs/2308.12352v1),
  [metadata/hash](source.json). Tài liệu BTC cung cấp cho task 1 theo thông tin chủ repo.
- Từ khóa: reciprocal square root, variable-spacing QROM, cubic interpolation,
  Horner, Newton–Raphson, chuẩn hóa, fixed-point, phase kickback, uncompute.
- Phạm vi: đọc sâu mục II.D, trang PDF 12–14, đến Eq. (50) và đoạn uncompute/hệ số b;
  đọc abstract trang 1, ngữ cảnh Table IV/trang 21–22 và mục tham khảo [102]–[104]/trang 26.
  Đã xem ảnh trang 12–14 để đối chiếu hệ số, dấu và số mũ. Các phần vật lý,
  block encoding/QSP, phép đo, ước lượng Trotter và phụ lục chưa được review sâu.
- Số trang bên dưới là số trang PDF (trùng số in trên các trang được dẫn).
  Đây là bản nháp của tác giả note, chưa có review độc lập hay quyết định nhóm.

## Vấn đề và kết quả của paper

**Kết quả nguồn:** paper đề xuất giao thức lượng tử tính stopping power: mức mất
động năng của hạt mang điện trong vật liệu, phục vụ mô phỏng điều kiện liên quan
đến inertial confinement fusion. Paper ước lượng tài nguyên fault-tolerant, không
báo cáo chạy mạch trên máy lượng tử thực nghiệm (abstract, trang 1; Discussion,
trang 21–22). Không dùng tổng chi phí mô phỏng vật lý làm điểm của task 1.

Phần liên quan trực tiếp là mô phỏng bằng product formula: tính thế năng trong
cơ sở vị trí và áp pha, tính động năng trong cơ sở động lượng và áp pha, dùng QFT
chuyển cơ sở. Tính tương tác Coulomb cho từng cặp cần nghịch đảo căn bậc hai của
bình phương khoảng cách; đây là nút thắt số học mà tác giả tập trung tối ưu
(mục II.D, trang 12).

Paper kết hợp QROM nội suy bậc ba với **một** bước Newton–Raphson, thay vì dựa
vào nhiều bước Newton với khởi tạo không kiểm soát. Tác giả lưu ý kết quả 32 bit
sau 5 bước của hướng [102] phụ thuộc giá trị khởi tạo; thử nghiệm số của họ chỉ
đạt mức đó trên miền có tỷ lệ biên dưới 5. Đây là nhận xét được paper báo cáo,
chưa phải kết luận được nhóm tự tái lập (trang 12).

## Thuật toán và công thức cần dùng

### 1. Chia miền theo tỷ lệ và chuẩn hóa

Paper dùng QROM có khoảng cách biến thiên; Eq. (36), trang 12, minh họa các ô
nguyên: 0, 1, 2, 3, [4,5], [6,7], [8,11], [12,15], ... . Hai khoảng nền là
[1,3/2] và [3/2,2], được nhân lên theo lũy thừa của 2. Ví dụ [16,23] tương ứng
với các đầu vào rời rạc thuộc 16 lần khoảng [1,3/2].

Với khoảng có đầu mút cơ sở c nhân 2^m, hệ số bậc j được scale thành
`a_j * 2^(-(j+1/2)*m)`, và độ lệch dùng `x - c*2^m` (trang 13, đoạn sau Eq. (42)).
Đây là cách giữ các đa thức cùng biểu diễn một hàm sau đổi thang.

Paper xử lý số nhỏ bằng bỏ **cặp bit 0 đầu** và dịch bù, giúp tránh tăng precision
quá nhiều trong các phép nhân (trang 13 cuối–14 đầu). x=0 không nằm trong phép
lấy nghịch đảo căn; không dùng ô QROM 0 để suy ra hàm được định nghĩa tại 0.

**Đối chiếu implementation của repo:** chuẩn hóa thành `M = x*2^(2s)/2^(2*n_p)`
trong [1,4), với `s` là số cặp bit 0 được dịch. Khi đó
`1/sqrt(x) = 2^(s-n_p)/sqrt(M)`. Bốn khoảng là [1,1.5), [1.5,2), [2,3), [3,4).
Hai khoảng cuối dùng M/2 và hệ số `a_j/(2^j*sqrt(2))`. Đây là quy ước cụ thể của
baseline, không phải nguyên văn thiết kế register của paper.

### 2. Hai đa thức nền

Đặt `d = x-c`, `P(x) = a0 - a1*d + a2*d^2 - a3*d^3`.
Các số thập phân dưới đây chép từ Eq. (38)–(41), (44)–(48), trang 13:

| Tham số | A: c=1, x thuộc [1,3/2] | B: c=3/2, x thuộc [3/2,2] |
| --- | --- | --- |
| a0 | 0.99994132489119882162 | 0.81648515205385221995 |
| a1 | 0.49609891915903542303 | 0.27136515484240234115 |
| a2 | 0.33261112772430493331 | 0.12756148214815175348 |
| a3 | 0.14876762006038398086 | 0.044753028579153842218 |
| delta_NR | 5.1642030908180720584e-9 | 3.6279794522852781448e-10 |

Đánh giá bằng Horner theo Eq. (49):

```text
r1 = a2 - a3*d
r2 = a1 - r1*d
p  = a0 - r2*d
```

Cần ba phép nhân thay vì tính riêng d^2, d^3. Dùng độ lệch thay cho x giảm độ rộng
một số toán hạng. Khẳng định phép trừ mốc có thể thực hiện bằng Clifford ở trang 13
phụ thuộc encoding và miền đã chọn; không suy ra mọi phép trừ hằng trong mạch đều miễn phí.

### 3. Một bước hiệu chỉnh

Eq. (42), trang 13:

```text
y0 = P(x)
y1 = (y0/2) * (3 + delta_NR - x*y0^2)
```

`delta_NR` là offset hiệu chỉnh Newton, khác với độ lệch đa thức `d`. Các hệ số và
offset được tác giả tối ưu số nhằm giảm maximum relative error. Paper báo cáo sau
hiệu chỉnh sai số tương đối khoảng không quá 2.5821e-9 ở khoảng A và 1.8140e-10 ở B
(trang 13). Đây là số của tác giả trên các khoảng/phép tính được mô tả, không phải
chứng minh mọi cách làm tròn và mọi mạch lượng tử đều đạt các mức đó.

**Suy luận đại số của note:** với Newton chuẩn không offset, đặt
`y0=(1+e)/sqrt(x)` thì `e1 = -3*e^2/2 - e^3/2`. Vì vậy sai số khởi tạo nhỏ được
cải thiện theo bậc hai. Với offset, thêm `delta_NR*(1+e)/2`. Phép cắt cụt fixed-point
còn thêm sai số khác; cần mô hình đúng từng phép nhân/thanh ghi.

### 4. Áp pha và uncompute

Sau tính giá trị nghịch đảo căn, áp pha cho từng cặp tương tác rồi uncompute
(trang 14, đoạn sau Eq. (50)). Paper bàn đến giữ khoảng 2000 qubit trung gian để
uncompute số học bằng Clifford. Đó là một đánh đổi tài nguyên, không phải khẳng định
mọi implementation có thể bỏ toàn bộ chi phí uncompute mà không trả thêm qubit.

Task 1 dùng một phép áp pha trên x có sẵn; không cần dựng tổng bình phương tọa độ,
mô phỏng electron hay QFT. Baseline áp Z_POW theo từng bit đầu ra rồi đảo các bước
số học; các ancilla và x phải được phục hồi theo hợp đồng verifier.

## Điều kiện đúng, sai số và tài nguyên

### Ước lượng của tác giả

Trang 13 cho ước lượng dùng nội suy precision 15 bit, rồi số học Newton nhắm khoảng
24 bit. Đây là estimate, không phải config để sao chép nguyên vào Kickmix:

- Ba phép nhân Horner: khoảng `3*15^2 = 675` Toffoli; ba phép trừ khoảng 45.
- Bình phương 15 bit, hai phép nhân 24 bit và phép trừ bổ sung đưa tổng số học
  lên khoảng 2136 Toffoli, chưa gồm tổng bình phương/QROM.
- Tổng bình phương ba tọa độ n bit: `3*n^2-n-1`; QROM: `4*n+2`.
- Thêm chuẩn hóa `n*(n+1)` và dịch bù khoảng `15*n`.
- Eq. (50), trang 14: `2137 + 4*n^2 + 19*n`, bằng 2395 tại n=6.

n trong estimate trên là bit tọa độ của mô hình paper. Task 1 có n_p=10 và verifier
chấm cả Q, cổng chạy thực, uncompute và tổng hợp phép quay. Không so 2395 trực tiếp
với Toffoli/score của baseline, cũng không dùng số này để tuyên bố đã tối ưu.
Table IV trang 21 là tài nguyên mô phỏng toàn hệ, khác hoàn toàn một lần invsqrt.

### Hợp đồng benchmark trong repo

Theo docstring verifier đang được đối chiếu:

```text
n_p = 10; beta = 1
x = 1..3*(2^10-2)^2 = 1..3,133,452; thanh ghi x có 22 qubit
|x>|0> -> exp(2*pi*i/sqrt(x)) |x>|0>
tol(x) = 2^-24/sqrt(x) turns
score = Q * (Toffoli_mean + T/4)
```

So pha modulo 1, phục hồi x và toàn bộ scratch. Full mặc định 64 shots mỗi x để
kiểm tra cả các nhánh measurement-based uncomputation. Dư địa sai số còn lại phải
đủ cho tổng hợp Z_POW; sai số số học sát ngưỡng có thể làm chi phí T tăng hoặc FAIL.
Paper không chứng minh mạch đáp ứng hợp đồng này; verifier gốc là căn cứ chấm.

### Hệ số b và giới hạn của note

Trang 14 đề xuất hấp thụ hệ số product-formula b bằng scale các hệ số nội suy và
thay 3 bằng `2+b^2` trong bước Newton. Note ghi nhận đề xuất này, nhưng **không dùng
làm bảo đảm precision cho b tùy ý**. Suy luận kiểm tra: nếu dùng đúng map
`F(y)=y*(2+b^2-x*y^2)/2` thì tại `y=b/sqrt(x)`, đạo hàm theo y là `1-b^2`, không
phải luôn bằng 0. Cần phân tích thêm sai số/điều kiện của phép tổng quát hóa trước
khi dùng ngoài beta=1; note chưa tra erratum hay các phiên bản sau v1. Điều này
không bác bỏ thuật toán beta=1 đang dùng trong benchmark.

## Khả năng áp dụng vào project

Các file được đọc tại commit df3d62b6dec8622ced06a4bd876dff69d6ebc01c, hash bytes trong source.json:

- [solution.py baseline](../../../../src/invsqrt/INV-BASELINE/solution.py):
  `Precision.coefficient_table`, `_normalize`, `_horner`, `_compute_y1`,
  `fixed_point_model`, `relative_error`, `_phase_by_bits`.
- [config baseline](../../../../src/invsqrt/INV-BASELINE/configs/baseline.json):
  n_p=10, delta_bits=14, coef_bits=17, square_bits=28, product_bits=28, result_bits=29.
- [verifier gốc](../../../../verifiers/invsqrt/verify_submission_invsqrt.py)
  và [DESCRIPTION](../../../../src/invsqrt/INV-BASELINE/DESCRIPTION.md).

Baseline đã có hai bộ hệ số paper, bốn khoảng, Horner và một bước Newton.
Không gọi việc áp dụng lại các ý đó là hypothesis mới. Baseline dùng `3 - M*y0^2`
không có delta_NR của paper, và bỏ hệ số 1/2 tại bước p rồi hấp thụ vào scale đầu ra.
`T(.)` của baseline bỏ các partial product dưới cột được giữ, khác với làm tròn
một tích thực chính xác ở cuối. Sai số hệ số, phép dịch và mọi phép nhân cần được
đánh giá trong đúng mô hình fixed-point đó.

Mọi phương án kế thừa phải tính cả pha/scratch và chi phí qubit, không chỉ sai số
của hàm số thực. Code baseline có attribution Apache-2.0 trong repo; giấy phép code
không tự trở thành giấy phép của paper. Note không thêm implementation mới.

## Hypothesis gợi ý và cách kiểm chứng

Đây là suy luận để agent nghiên cứu cân nhắc, **chưa nhận Issue, chưa thử và chưa
khẳng định hướng chưa ai làm**. Trước nhận hướng vẫn phải đối chiếu Issues/PR/results.

| Câu hỏi có thể nghiên cứu | Cơ sở và giới hạn | Đối chứng / điều có thể bác bỏ |
| --- | --- | --- |
| Có thể giảm precision khởi tạo và tái phân bổ bit cho Newton không? | Paper quan sát 15 bit có thể đủ trong thiết kế của họ; baseline có encoding và truncation khác | So baseline cùng profile; mô hình đúng partial-product, biên khoảng và miền rời rạc; bác bỏ nếu error margin/score thực không tốt hơn |
| Offset Newton tối ưu trong fixed-point có giúp giảm bit hoặc tăng margin không? | Paper có delta_NR, baseline không dùng; offset paper rất nhỏ có thể bị lượng tử hóa mất | Cần xác định representability trước; chỉ đổi offset/bit liên quan; bác bỏ nếu offset bị cắt mất, chi phí thêm vượt lợi ích hoặc lỗi tăng |
| Đánh đổi giữ workspace và uncompute có lợi cho Q*C không? | Paper bàn về giữ nhiều qubit để giảm Toffoli | Tính cả Q cực đại, compute/uncompute, nhánh đo và rotation; giảm Toffoli riêng lẻ chưa đủ để ủng hộ |

Không quét config hoặc dựng/chấm trong luồng đọc tài liệu. Các thử nghiệm thực sự
phải theo workflow experiment, commit nguồn trước build, chấm thủ công, lưu results.

## Bằng chứng trong project và câu hỏi còn mở

[Bảng điểm baseline](../../../../src/invsqrt/SCORES.md) đã có run full và dev;
đó là bằng chứng của baseline hiện hữu, không phải thử nghiệm mới sinh từ note.
Note không chạy lại mạch, không thay đổi bất cứ score/run nào và không suy ra
commit tạo artifact lịch sử từ HEAD dùng để đọc source.

Chưa có thử nghiệm được ghi nhận trong note về offset Newton, config 15 bit hay
thiết kế workspace khác. Chưa tái lập numerical minimax của tác giả, chưa chứng
minh bound fixed-point cho mọi x, chưa đọc sâu [102]/[103], chưa đối chiếu phiên
bản mới hơn hoặc errata. Reviewer cần kiểm lại công thức, hệ số, diễn giải bound,
map code–paper và giới hạn của nhận xét về b trước khi đổi Status sang ready.

## Tài liệu liên quan

Trong danh mục paper, trang 26:

- [102] Jones et al., *Faster quantum chemistry simulation on fault-tolerant quantum
  computers*, New Journal of Physics 14, 115023 (2012): hướng Newton tiền nhiệm.
- [103] Sanders et al., *Compilation of Fault-Tolerant Quantum Heuristics for
  Combinatorial Optimization*, PRX Quantum 1, 020312 (2020): QROM nội suy được dẫn.
- [104] Low et al., *On the complexity of implementing Trotter steps*,
  arXiv:2211.09133 (2022): ngữ cảnh Trotter, không phải bound riêng cho mạch task 1.

Các nguồn này mới được nhận diện từ danh mục tham khảo; chưa đọc bản gốc và không
được trình bày như nguồn đã được nhóm độc lập kiểm chứng.
