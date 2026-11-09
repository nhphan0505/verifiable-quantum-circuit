# Measurement-based uncomputation of quantum circuits for modular arithmetic

Status: draft
Track: shared
Source: arXiv:2407.20167
Version: v1 (truy cập 2026-11-09)

- Alessandro Luongo, Antonio Michele Miti, Varun Narasimhachar và Adithya Sireesh (2024).
- Từ khóa — đo cơ sở X, phase kickback, cờ so sánh, cộng modulo, Toffoli kỳ vọng.
- Bản đã đọc — [PDF v1](paper.pdf), [metadata và SHA-256](source.json). Số trang dưới đây tính từ trang đầu PDF.

## Vấn đề và kết quả của paper

Bài báo phân tích mạch cộng, trừ và so sánh thuận nghịch, rồi dùng phép đo giữa mạch để xóa cờ một qubit khi cờ đã hết vai trò điều khiển. Lemma 4.1 cho phép thay một lần gọi mạch xóa tất định bằng một lần gọi có xác suất 1/2. Sau sửa pha, cả hai nhánh đo thực hiện cùng ánh xạ trên dữ liệu và trả cờ về trạng thái sạch. Phần ngẫu nhiên nằm ở chi phí thực thi. Các kết quả là phân tích mạch logic (mục 1.1 và 4, tr. 3, 34–41).

## Thuật toán và công thức cần dùng

**Xóa một bit (Lemma 4.1, Hình 24, tr. 34–35).** Cho `g(x) ∈ {0,1}`. Trước phép đo, trạng thái có dạng `Σ_x α_x |x⟩|g(x)⟩`. Oracle sửa pha phải có tác dụng `U_g|x⟩|b⟩ = |x⟩|b XOR g(x)⟩` cho cả hai giá trị `b`, với mọi scratch trả sạch và pha đúng. Áp dụng H lên cờ rồi đo Z, tương đương đo X, được bit cổ điển `h`. Biên độ chưa chuẩn hóa của dữ liệu là `α_x (-1)^(h g(x))/√2`. Vì các `|x⟩` trực giao, mỗi kết quả có xác suất 1/2.

- `h=0` — dữ liệu giữ nguyên pha và cờ đã ở `|0⟩`.
- `h=1` — cờ đang ở `|1⟩`. Áp dụng H để tạo `|−⟩`, gọi `U_g` để nhân thêm `(-1)^g(x)`, rồi H và X để trả cờ về `|0⟩`. Hai thừa số pha triệt tiêu trên từng thành phần `x`.

Nếu đã có oracle pha `D_g|x⟩ = (-1)^g(x)|x⟩`, có thể suy ra cách dùng đo X kèm reset và áp dụng `D_g` chỉ khi `h=1`. Ví dụ, với `g(x)=u·v` và hai toán hạng còn sống, `D_g` là CZ. Với predicate phức tạp, cần tính chi phí mạch pha riêng.

**Cộng modulo kiểu VBE (Prop. 3.2, tr. 24–25, Thm. 4.2 và Hình 25, tr. 35–36).** Với `x,y` là số không dấu `n` bit, modulus cổ điển `0<p<2^n` và `0≤x,y<p`, tạo tổng `s=x+y` trên `n+1` bit. Tạo cờ `d=1[s≥p]`, rồi trừ `d·p` để được `z=s-d·p`. Khi `d=0`, `z≥x`. Khi `d=1`, `z=x+y-p<x` vì `y<p`. Vậy `d=1[z<x]`, và comparator trên **đầu ra hiện tại** `(x,z)` thực hiện được `U_g` dùng để xóa cờ. Tổng bằng đúng `p` phải đi vào nhánh trừ.

- Với quantum control `c`, đặt `z=(y+c·x) mod p` và `g=c·1[z<x]`. Khi `c=0`, `y<p` đảm bảo cờ bằng 0. Thm. 4.7 (tr. 37–38) dùng `c` trong bộ cộng đầu và oracle sửa pha cuối. Việc đo cờ diễn ra trên cả hai nhánh của `c`.
- Với hằng số `a∈[0,p)`, dùng `g=1[z<a]` hoặc `g=c·1[z<a]` cho biến thể có control. Trong kiến trúc Takahashi, trừ `p-a` trước rồi cộng lại `p` khi có borrow. Cờ lúc này có cực tính ngược, `1[x+a<p]=1[z≥a]` với `z=(x+a) mod p` (Prop. 3.15, tr. 31–32, Thm. 4.10–4.12, tr. 39–40).
- Với kiểm tra khoảng mở, tạo `q=1[y<x]`, dùng `q` điều khiển XOR predicate `1[x<z]` vào đích rồi xóa `q` từ `(y,x)`. Trường hợp bằng một trong hai biên cho 0 (Thm. 4.13, tr. 40–41).

## Điều kiện đúng, sai số và tài nguyên

Với cờ cần xóa tại thời điểm mà thanh ghi dữ liệu đã thay đổi, phải chứng minh cờ bằng đúng `g` của dữ liệu **tại điểm đo** trên toàn miền reachable. Oracle có relative phase chưa sửa hoặc còn scratch phụ không thỏa ánh xạ của Lemma 4.1. Suy ra từ công thức biên độ, một kiểm tra chỉ so bit đầu ra sẽ bỏ sót lỗi pha giữa các trạng thái có `g` khác nhau. Lemma dùng phép đo và cổng lý tưởng, không đưa mô hình nhiễu hoặc sai số tổng hợp phép quay. Nhiều bit garbage cần phân tích riêng từng phép đo và quan hệ phụ thuộc.

Gọi `B` là Toffoli của phần luôn chạy và `C` là Toffoli của oracle xóa cuối. Nếu các chi phí cố định trong từng nhánh, Toffoli là `B` hoặc `B+C`, kỳ vọng `B+C/2`, cực đại `B+C`. Lemma còn dùng một H và một đo Z cho mọi nhánh, thêm hai H và một X ở nhánh `h=1`. Độ trễ đo, phản hồi và reset phải được xét riêng nếu nằm trong hàm chi phí. Với VBE ở Thm. 4.2, `B=r_ADD+r_COMP+r_C-SUB`, `C=r'_COMP` và scratch là hai dây phụ cộng với số scratch lớn nhất của bốn khối theo quy ước định lý.

| Phép cộng modulo thường | Toffoli xóa tất định | Toffoli kỳ vọng với MBU |
| --- | ---: | ---: |
| VBE 5 adder | `20n+10` | `16n+8` |
| VBE 4 adder | `16n+4` | `14n+4` |
| CDKPM | `8n` | `7n` |
| Gidney | `4n` | `3.5n` |
| CDKPM + Gidney | `6n` | `5.5n` |

Các số Toffoli trên lấy từ Bảng 1, tr. 4. CDKPM ở Thm. 4.3 tiết kiệm `n` Toffoli kỳ vọng (12,5%) so với chính biến thể xóa tất định. Khi đọc số qubit, Bảng 1 và các Thm. 4.3–4.5 có chênh một dây nếu cộng trực tiếp `2n` dây dữ liệu với ancilla nêu trong định lý. Chưa đối chiếu được quy ước hoặc lịch cấp phát cho dây chênh, nên cần đếm lại trước khi dùng số qubit để so sánh. Tương tự, số khối QFT ở Bảng 1 và Thm. 4.6 khác cách trình bày, và chưa quy đổi được sang Toffoli tương đương. Với kiểm tra khoảng, công thức ở Thm. 4.13 giảm từ `2r+r_c` xuống `1.5r+r_c` với `r` là chi phí comparator và `r_c` là chi phí comparator có control. Tỷ lệ giảm là `0.5r/(2r+r_c)`. Để đếm scratch từ sơ đồ, cần đủ cho cả comparator có control nếu khối đó dùng nhiều scratch hơn comparator thường.

## Khả năng áp dụng vào project

Đối chiếu mã tại main `84bdf39776f20902ff1abb454bb37c70ff75f4bb`. Điểm chung là mạch xóa scratch bằng đo, còn phép cộng modulo `p` của paper khác hợp đồng số học và hàm điểm của các bài.

- **DQI.** [DQI-27](../../../../src/dqi/DQI-27/DESCRIPTION.md) nêu điều kiện còn sống của hai toán hạng trong masked product. [Code](../../../../src/dqi/DQI-27/solution.py) có đường `masked_cleanup="hmr"` với `init_and/del_and`. Đây là trường hợp `g=u·v`. Một cờ valuation hoặc điều kiện rộng cần chứng minh predicate từ dữ liệu còn sống trước khi xóa. [Verifier DQI](../../../../verifiers/dqi/verify_submission_dqi.py) tính `R·Q²·T`, với `R` phụ thuộc cận lỗi giải mã, `Q` là số qubit và `T` là chi phí Toffoli.
- **Invsqrt.** [Mạch Newton tham chiếu](../../../../verifiers/invsqrt/nr_reference_circuit.py) dùng `del_and` trong phần đảo phép toán và dọn tích phụ. MBU có thể liên quan đến cờ carry của số học fixed-point nếu chứng minh được điều kiện sau cắt bit và giữ nguyên phép pha số học. [Verifier invsqrt](../../../../verifiers/invsqrt/verify_submission_invsqrt.py) tính `Q·T_equiv`, trong đó phép quay đóng góp theo dung sai tổng hợp suy từ biên sai số còn lại.
- **DFTHCSOS.** `node` của [DFT-BASELINE](../../../../src/dfthcsos/DFT-BASELINE/solution.py) dùng `del_and` để xóa cờ đường đi khi hai bit nguồn còn sống. [Verifier ANGLES](../../../../verifiers/dfthcsos/SCORING_README.md) kiểm tra word và pha bằng mô phỏng, rồi tính `λ_eff·T_total·Q_total` cho cả ANGLES và các thành phần ước tính. Số Toffoli tiết kiệm trong một nhánh xóa cờ không thể dùng trực tiếp làm phần trăm giảm score toàn bài.

## Hypothesis gợi ý và cách kiểm chứng

Suy luận áp dụng từ paper. Với một cờ so sánh đã hết lượt dùng trong DQI-27, nếu có thể tái tính predicate từ trạng thái tại điểm xóa và scratch dùng cho sửa pha không làm tăng peak, MBU có thể giảm Toffoli kỳ vọng so với xóa bằng comparator đảo. Đối chứng là cùng phép biến đổi Schur, layout và tham số decoder với comparator xóa tất định. Bác bỏ nếu thiếu predicate hợp lệ, có khác biệt pha hoặc scratch, hay chi phí cả mạch ở cùng profile không giảm.

Trước khi xem điểm, kiểm tra cờ ở biên bằng nhau, các nhánh control và hai kết quả đo. Với mạch rút gọn, đối chiếu biên độ và pha của chồng chập hai đầu vào có predicate khác nhau, cùng điều kiện ancilla sạch sau cả hai nhánh. Tính cả chi phí dựng oracle sửa pha và mức qubit đỉnh. Đây là đề xuất kiểm chứng cho công việc sau.

## Bằng chứng trong project và câu hỏi còn mở

[Issue DQI-27](https://github.com/nhphan0505/verifiable-quantum-circuit/issues/27) và [mô tả DQI-27](../../../../src/dqi/DQI-27/DESCRIPTION.md) là tiền lệ của xóa masked AND và phân tích liveness. Chưa xác định được cờ comparator rộng có đủ dữ liệu tại điểm đo, và chưa có kết quả chấm cho biến thể đề xuất ở note này. Phạm vi nguồn đã rà nằm trong [coverage](source.json). Mục 2, các dẫn xuất còn lại của mục 3, mã bổ trợ và tài liệu dẫn chưa được rà đầy đủ. Phần số qubit/QFT chênh giữa bảng và định lý cần đối chiếu nếu dùng để dự toán.

## Tài liệu liên quan

- [Bài báo arXiv được giao](https://arxiv.org/pdf/2407.20167).
- [Note về DQI và MBUC trên GF(2^b)](../../../dqi/papers/arxiv-2510.10967/note.md).
- [Note về biên dịch mạch và điều kiện verifier](../../discussions/verifiable-circuit-compilation/note.md).
