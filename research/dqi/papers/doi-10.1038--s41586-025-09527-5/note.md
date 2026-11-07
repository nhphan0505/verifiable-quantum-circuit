# Optimization by decoded quantum interferometry — thuật toán DQI, luật bán nguyệt và quy về giải mã Reed–Solomon

Status: draft
Track: dqi
Source: doi:10.1038/s41586-025-09527-5 (https://doi.org/10.1038/s41586-025-09527-5); metadata và SHA-256 trong source.json
Version: Nature Vol. 646, pp. 831–836 (2025-10-23; published online 2025-10-22); bản PDF local 7 trang, đọc ngày 2026-11-07

- Paper: *Optimization by decoded quantum interferometry*, Stephen P. Jordan, Noah Shutty, Mary Wootters, Adam Zalcman, Alexander Schmidhuber, Robbie King, Sergei V. Isakov, Tanuj Khattar & Ryan Babbush, *Nature* Vol. 646, pp. 831–836 (2025), DOI: `10.1038/s41586-025-09527-5` (không ghi mã arXiv của chính bài báo trong PDF; phần docstring verifier dẫn bản preprint liên quan `arXiv:2408.08292`).
- Track: `dqi`.
- Từ khóa: Decoded Quantum Interferometry (DQI), max-XORSAT, max-LINSAT, Optimal Polynomial Intersection (OPI), Dicke state, syndrome decoding, uncomputation, semicircle law, Reed–Solomon codes, Berlekamp–Massey, LFSR, LDPC, belief propagation.
- Bản đã đọc: [PDF local](paper.pdf) (`f492957ba9897ef735decb7a4a7a75fc7cdd6515a3e2b94b9571726ab060420f`), [DOI gốc](https://doi.org/10.1038/s41586-025-09527-5), [metadata/hash](source.json).
- Phạm vi đã đọc và giới hạn:
  - **Đã đọc toàn bộ 7 trang của file PDF đính kèm** (trang PDF 1–7, tương ứng trang tạp chí 831–836) và đối chiếu trực quan bằng ảnh chụp từng trang cho mọi phương trình Eq. (1)–(6), Definition 1–2, Fig. 1–3, Table 1, mục *Discussion*, danh mục tham khảo [1]–[59] và mục *Data/Code availability*.
  - **Phần chưa đọc / ngoài PDF:** Tài liệu bổ sung (*Supplementary Information* — SI Sections 1–13, bao gồm Supplementary Theorem 1.1, Supplementary Theorem 7.1, chi tiết ma trận đường chéo 3 dải ở SI Section 6, chứng minh quy OPI về Reed–Solomon ở SI Section 2, và chi tiết ước lượng tài nguyên ở SI Section 13) không nằm trong file PDF 7 trang và chưa được mở/đọc trực tiếp. Các bài báo được trích dẫn hoặc dẫn trong code project (như `arXiv:2408.08292`, `arXiv:2510.10967`, [22], [23], [37]) cũng chưa được đọc bản gốc trong phạm vi note này.
  - Quy ước trích dẫn trang: ghi rõ `trang PDF <số> (trang <số tạp chí>)`.

## Vấn đề và kết quả của paper

**Kết quả nguồn (lý thuyết + thực nghiệm máy tính cổ điển + ước lượng tài nguyên lượng tử):**

1. **Nguyên lý DQI và quy bài toán tối ưu về bài toán giải mã:**
   - Paper đề xuất thuật toán lượng tử **Decoded Quantum Interferometry (DQI)** sử dụng biến đổi Fourier lượng tử (Hadamard trên $\mathbb{F}_2$ hoặc QFT trên trường hữu hạn $\mathbb{F}_p$) để biến bài toán tối ưu tổ hợp thành bài toán giải mã hội chứng (*syndrome decoding*) trên mã tuyến tính đối ngẫu $C^\perp = \{\mathbf{d} \in \mathbb{F}_p^m : B^T \mathbf{d} = \mathbf{0}\}$ (Abstract, trang PDF 1 / trang 831; trang PDF 2 / trang 832).
   - Thay vì khai thác cấu trúc cục bộ của cảnh quan năng lượng như các phương pháp dựa trên Hamiltonian (adiabatic, QAOA), DQI khai thác **tính thưa (*sparsity*) và cấu trúc đại số** trong phổ Fourier của hàm mục tiêu để giao thoa tăng cường biên độ tại các chuỗi nghiệm có giá trị mục tiêu lớn (trang PDF 1 / trang 831).
2. **Định lý tỷ lệ ràng buộc thỏa mãn kỳ vọng — Luật bán nguyệt (*Semicircle law*):**
   - Với bài toán tổng quát **max-LINSAT** trên $\mathbb{F}_p$ gồm $m$ ràng buộc, mỗi tập chấp nhận $F_i \subset \mathbb{F}_p$ có cùng kích thước $|F_i| = r$ (Definition 1, trang PDF 2 / trang 832): nếu có bộ giải mã cổ điển thời gian đa thức sửa được tới $\ell$ lỗi trên mã $C^\perp$ với $\ell / m \le 1 - r / p$, thì chọn tối ưu các trọng số $w_0, \dots, w_\ell$ cho phép DQI đạt tỷ lệ ràng buộc thỏa mãn kỳ vọng $\langle s \rangle / m$ theo Eq. (6) (trang PDF 2–3 / trang 832–833). Khi $\ell / m > 1 - r / p$ (tức $r / p > 1 - \ell / m$), $\langle s \rangle / m = 1$ (trang PDF 3 / trang 833).
   - Paper dẫn chiếu chứng minh chính xác cho trường hợp giải mã hoàn hảo tại **Supplementary Theorem 1.1** và trường hợp có lỗi giải mã tại **Supplementary Theorem 7.1** (trang PDF 3 / trang 833; các định lý này nằm trong SI ngoài PDF).
3. **Tăng tốc siêu đa thức (*superpolynomial speed-up*) trên bài toán OPI:**
   - Bài toán **Optimal Polynomial Intersection (OPI)** trên trường nguyên tố $\mathbb{F}_p$ (Definition 2, trang PDF 3 / trang 833) là trường hợp riêng của max-LINSAT với $m = p - 1$ ràng buộc, ma trận $B$ là ma trận Vandermonde và $C^\perp$ là **mã Reed–Solomon** (trang PDF 3 / trang 833, dẫn SI Section 2).
   - Giải mã hội chứng cho mã Reed–Solomon giải được trong thời gian đa thức tới nửa khoảng cách mã, tức $\ell = \lfloor (n + 1)/2 \rfloor$, ví dụ bằng thuật toán **Berlekamp–Massey** [26] (trang PDF 3 / trang 833).
   - Ở chế độ tiệm cận $p \to \infty$ với $r/p$ và $n/p$ cố định (thay $\ell / m = n / (2p)$ vào Eq. (6)), với $r/p = 1/2$ và mọi $0 < n/p < 1$ cố định, DQI + Berlekamp–Massey đạt tỷ lệ thỏa mãn vượt thuật toán đa thức cổ điển tốt nhất mà nhóm tác giả biết là thuật toán Prange ($1/2 + n/(2p)$) (Fig. 3, trang PDF 3 / trang 833).
   - Cụ thể: tại $n/p = 1/10, r/p = 1/2$, Prange đạt $0.55$ còn DQI đạt $\langle s \rangle / p = 1/2 + \sqrt{19}/20 \approx 0.7179$; tại $n/p = 1/2, r/p = 1/2$, Prange đạt $0.75$ còn DQI đạt $\langle s \rangle / p = 1/2 + \sqrt{3}/4 \approx 0.9330$ (Fig. 3 caption, trang PDF 3 / trang 833; trang PDF 4 / trang 834).
   - Tác giả nêu rõ giới hạn: hiện chưa có định lý độ khó phức tạp tính toán hay giả thuyết mật mã nào chứng minh trực tiếp OPI ở đúng miền tham số của DQI là bất khả trị cổ điển, dù các trường hợp giới hạn liên quan đến giải mã hợp lý cực đại (NP-hard [33, 34]) hoặc bài toán logarit rời rạc [35, 36] (trang PDF 4 / trang 834).
4. **Ước lượng tài nguyên lượng tử cho OPI tại $p = 521$:**
   - Với $n/p \approx r/p \approx 1/2$ tại $p = 521$, chi phí chủ đạo của DQI + Berlekamp–Massey là cài đặt thuận nghịch (*reversible implementation*) cho chương trình con tìm thanh ghi dịch hồi tiếp tuyến tính ngắn nhất (*shortest linear-feedback shift register* — LFSR). Dùng thư viện **Qualtran** [37], các tác giả ước lượng bước tìm LFSR tại $p = 521$ cần khoảng $1 \times 10^8$ cổng Toffoli logic và $9 \times 10^3$ qubit logic (trang PDF 4 / trang 834, dẫn SI Section 13).
5. **Thực nghiệm đối sánh trên sparse max-XORSAT với giải mã LDPC:**
   - Khi $B$ thưa trên $\mathbb{F}_2$, DQI quy max-XORSAT về giải mã mã kiểm tra chẵn lẻ mật độ thấp (**LDPC**) bằng **belief propagation (BP)** (trang PDF 4 / trang 834).
   - Trên một thực thể mẫu có $31,216$ biến và $50,000$ ràng buộc với phân bố bậc bất quy tắc được tinh chỉnh (Table 1, trang PDF 4 / trang 834): `DQI + BP` đạt $\ge 0.831$ (thời gian chạy BP cổ điển khoảng $8\text{ s} \times 1\text{ core}$), vượt `Short anneal` ($0.764$ trong $8\text{ s} \times 1\text{ core}$), `Prange's algorithm` ($0.812$), `Greedy` ($0.666$) và `AdvRand` ($0.554$), trong khi `Long anneal` cần $73\text{ h} \times 5\text{ cores}$ để đạt $0.832$. Tuy nhiên, các tác giả thiết kế được một thuật toán cổ điển chuyên biệt (`Tailored heuristic`, biến thể simulated annealing gắn trọng số phụ thuộc nhiệt độ theo số biến của mệnh đề) đạt $0.880$ trong $7\text{ min} \times 1\text{ core}$, nên không coi ví dụ max-XORSAT này là lợi thế lượng tử siêu đa thức (trang PDF 4 / trang 834).

## Thuật toán và công thức cần dùng

### 1. Biểu diễn max-XORSAT và trạng thái đa thức của DQI (trên $\mathbb{F}_2$)

- **Định nghĩa hàm mục tiêu max-XORSAT (trang PDF 1–2 / trang 831–832):**
  Cho ma trận $B \in \mathbb{F}_2^{m \times n}$ ($m > n$) và vector $\mathbf{v} \in \mathbb{F}_2^m$, cần tìm $\mathbf{x} \in \mathbb{F}_2^n$ thỏa mãn nhiều phương trình nhất trong hệ $B\mathbf{x} = \mathbf{v} \pmod 2$. Gọi $\mathbf{b}_i$ là hàng thứ $i$ của $B$ và $v_i$ là phần tử thứ $i$ của $\mathbf{v}$. Hàm mục tiêu đếm số phương trình thỏa mãn trừ số phương trình không thỏa mãn là Eq. (1) (trang PDF 1 / trang 831):
  $$f(\mathbf{x}) = \sum_{i=1}^{m} (-1)^{v_i + \mathbf{b}_i \cdot \mathbf{x}}$$
- **Biến đổi Hadamard và trạng thái mục tiêu $|P(f)\rangle$ (trang PDF 2 / trang 832):**
  Biến đổi Hadamard của $f$ có đúng $m$ biên độ khác không nằm trên các chuỗi $\mathbf{b}_1, \dots, \mathbf{b}_m$. Để tăng cường xác suất đo được $\mathbf{x}$ có $f(\mathbf{x})$ lớn, DQI chuẩn bị trạng thái ứng với đa thức bậc $\ell$ chuẩn hóa thích hợp $P$ theo Eq. (2):
  $$|P(f)\rangle = \sum_{\mathbf{x} \in \mathbb{F}_2^n} P(f(\mathbf{x})) |\mathbf{x}\rangle$$
  Biến đổi Hadamard của $|P(f)\rangle$ luôn có dạng Eq. (3):
  $$\sum_{k=0}^{\ell} \frac{w_k}{\sqrt{\binom{m}{k}}} \sum_{\substack{\mathbf{y} \in \mathbb{F}_2^m \\ |\mathbf{y}| = k}} (-1)^{\mathbf{v} \cdot \mathbf{y}} |B^T \mathbf{y}\rangle$$
  trong đó $w_0, \dots, w_\ell$ là các hệ số trọng số và $|\mathbf{y}|$ là trọng số Hamming của chuỗi bit $\mathbf{y} \in \mathbb{F}_2^m$.

### 2. Năm bước chuẩn bị trạng thái $|P(f)\rangle$ (trang PDF 2 / trang 832, Fig. 1)

1. **Bước 1 — Chuẩn bị chồng chập các trạng thái Dicke:**
   Chuẩn bị trạng thái $\sum_{k=0}^{\ell} w_k |D_{m,k}\rangle$ trên thanh ghi thứ nhất ($m$ qubit), trong đó trạng thái Dicke trọng số $k$ được định nghĩa ở Eq. (4):
   $$|D_{m,k}\rangle = \frac{1}{\sqrt{\binom{m}{k}}} \sum_{\substack{\mathbf{y} \in \mathbb{F}_2^m \\ |\mathbf{y}| = k}} |\mathbf{y}\rangle$$
   Theo paper, bước này thực hiện được với $\mathcal{O}(m^2)$ cổng lượng tử dùng kỹ thuật của [22, 23].
2. **Bước 2 — Áp pha theo vector vế phải $\mathbf{v}$:**
   Áp toán tử $Z_1^{v_1} \otimes \dots \otimes Z_m^{v_m}$ (với $Z_m$ là cổng Pauli-$Z$ trên qubit thứ $m$) để nhân pha $(-1)^{\mathbf{v} \cdot \mathbf{y}}$.
3. **Bước 3 — Tính hội chứng (*syndrome*) $B^T \mathbf{y}$ thuận nghịch:**
   Dùng mạch nhân ma trận thuận nghịch tính $B^T \mathbf{y}$ vào một thanh ghi phụ (*ancilla register*, kích thước $n$), thu được trạng thái Eq. (5):
   $$\sum_{k=0}^{\ell} \frac{w_k}{\sqrt{\binom{m}{k}}} \sum_{\substack{\mathbf{y} \in \mathbb{F}_2^m \\ |\mathbf{y}| = k}} (-1)^{\mathbf{v} \cdot \mathbf{y}} |\mathbf{y}\rangle |B^T \mathbf{y}\rangle$$
4. **Bước 4 — Uncompute $|\mathbf{y}\rangle$ bằng giải mã hội chứng:**
   Từ giá trị hội chứng $B^T \mathbf{y}$ trong thanh ghi thứ hai và ràng buộc trọng số Hamming $|\mathbf{y}| \le \ell$, suy ra $\mathbf{y}$ và trừ (XOR) khỏi thanh ghi thứ nhất để đưa thanh ghi thứ nhất về $|0\rangle^{\otimes m}$ rồi loại bỏ. Đây chính là bài toán giải mã hội chứng (*syndrome decoding*) với tối đa $\ell$ lỗi cho mã tuyến tính cổ điển:
   $$C^\perp = \{\mathbf{d} \in \mathbb{F}_2^m : B^T \mathbf{d} = \mathbf{0}\}$$
5. **Bước 5 — Biến đổi Hadamard cuối:**
   Áp $H^{\otimes n}$ lên thanh ghi còn lại (đang giữ $|B^T \mathbf{y}\rangle$) để thu được $|P(f)\rangle$, sau đó đo trong cơ sở tính toán.

### 3. Bài toán max-LINSAT, OPI và công thức Luật bán nguyệt

- **Definition 1 — max-LINSAT (trang PDF 2 / trang 832):**
  Cho trường hữu hạn $\mathbb{F}_p$, ma trận $B \in \mathbb{F}_p^{m \times n}$, và với mỗi $i = 1, \dots, m$ một tập con $F_i \subset \mathbb{F}_p$ (kích thước $|F_i| = r$). Tìm $\mathbf{x} \in \mathbb{F}_p^n$ thỏa mãn nhiều nhất trong số $m$ ràng buộc $\sum_{j=1}^{n} B_{ij} x_j \in F_i$. (max-XORSAT là trường hợp $p = 2, |F_i| = 1$).
- **Luật bán nguyệt — Eq. (6) (trang PDF 2–3 / trang 832–833):**
  Giả sử có bộ giải mã thời gian đa thức sửa được tới $\ell$ lỗi trên mã $C^\perp = \{\mathbf{d} \in \mathbb{F}_p^m : B^T \mathbf{d} = \mathbf{0}\}$. Khi đó với lựa chọn tối ưu của $w_0, \dots, w_\ell$ (tính trước cổ điển trong thời gian đa thức theo SI Section 6), kỳ vọng số ràng buộc thỏa mãn $\langle s \rangle$ khi đo $|P(f)\rangle$ thỏa mãn:
  $$\frac{\langle s \rangle}{m} = \left( \sqrt{\frac{\ell}{m}\left(1 - \frac{r}{p}\right)} + \sqrt{\frac{r}{p}\left(1 - \frac{\ell}{m}\right)} \right)^2 \quad \text{nếu } \frac{r}{p} \le 1 - \frac{\ell}{m}$$
  và $\langle s \rangle / m = 1$ nếu $r/p > 1 - \ell/m$. Khi $r/p = 1/2$, công thức rút gọn thành $\frac{\langle s \rangle}{m} = \frac{1}{2} + \sqrt{\frac{\ell}{m}\left(1 - \frac{\ell}{m}\right)}$, là phương trình nửa đường tròn.
- **Definition 2 — Optimal Polynomial Intersection (OPI) (trang PDF 3 / trang 833):**
  Cho các số nguyên $n < p - 1$ với $p$ nguyên tố và các tập con $F_1, \dots, F_{p-1} \subset \mathbb{F}_p$. Tìm đa thức $Q \in \mathbb{F}_p[y]$ có bậc tối đa $n - 1$ cực đại hóa $f_{\text{OPI}}(Q) = |\{y \in \{1, \dots, p - 1\} : Q(y) \in F_y\}|$. Trong biểu diễn max-LINSAT, $m = p - 1$, $B$ là ma trận Vandermonde, $C^\perp$ là mã Reed–Solomon và bộ giải mã Berlekamp–Massey sửa được $\ell = \lfloor (n + 1)/2 \rfloor$ lỗi.

## Điều kiện đúng, sai số và tài nguyên

### 1. Điều kiện đúng và mô hình chi phí trong paper

- **Điều kiện khử rối (*uncomputation*) ở Bước 4:**
  Để biến đổi Fourier cuối ở Bước 5 tạo ra sự giao thoa đúng của $|P(f)\rangle$, thanh ghi lỗi $|\mathbf{y}\rangle$ phải được uncompute về $|0\rangle^{\otimes m}$ từ hội chứng $|B^T \mathbf{y}\rangle$. Nếu bộ giải mã là hoàn hảo cho mọi trọng số lỗi $|\mathbf{y}| \le \ell$, thanh ghi $|\mathbf{y}\rangle$ được xóa hoàn toàn (trang PDF 2–3 / trang 832–833). Khi bộ giải mã có xác suất lỗi (ví dụ BP trên mã LDPC hoặc giải mã gần đúng), paper dẫn chiếu **Supplementary Theorem 7.1** (trong SI, ngoài PDF) cho biểu thức suy giảm tương ứng.
- **Chi phí cổng tổng quát (trang PDF 2 / trang 832):**
  Nếu mạch giải mã thuận nghịch cần $T$ cổng lượng tử, tổng số cổng để chuẩn bị $|P(f)\rangle$ là $\mathcal{O}(T + m^2)$ (trong đó $\mathcal{O}(m^2)$ đến từ chuẩn bị chồng chập trạng thái Dicke theo [22, 23]).
- **Ước lượng tài nguyên OPI cụ thể trong paper (trang PDF 4 / trang 834):**
  Tại $p = 521$ ($n/p \approx r/p \approx 1/2$, trường nguyên tố $\mathbb{F}_{521}$), cài đặt thuận nghịch phần tìm LFSR ngắn nhất của thuật toán Berlekamp–Massey bằng Qualtran [37] cần xấp xỉ $1 \times 10^8$ cổng Toffoli logic và $9 \times 10^3$ qubit logic.

### 2. Đối chiếu khác biệt giữa mô hình paper và hợp đồng benchmark `dqi` của cuộc thi

Theo [verify_submission_dqi.py](../../../../verifiers/dqi/verify_submission_dqi.py) và [solution.py](../../../../src/dqi/DQI-BASELINE/solution.py) (đối chiếu tại commit `74c543d217ad394457054f14a6ea9e66fd3c2552`):

| Tiêu chí | Bài báo Nature (Jordan et al., 2025) | Benchmark II (`dqi`) trong repository |
| --- | --- | --- |
| **Bài toán & Trường hữu hạn** | Minh họa chính trên $\mathbb{F}_2$ (max-XORSAT) và trường nguyên tố $\mathbb{F}_p$ (OPI, ví dụ $p = 521$, $m = p - 1 = 520$, $n \approx 260$). | Mã Reed–Solomon trên trường nhị phân mở rộng $\text{GF}(2^b)$ với $b = 12$ ($q = 2^{12} = 4096$), chiều dài mã $m = 4095$, số hội chứng $n = 70$, sửa tối đa $\ell = n/2 = 35$ lỗi ký hiệu, $r = 2016$ (hỗ trợ hàm bent $(2^{12} - 2^6)/2$). |
| **Phạm vi mạch lượng tử** | Toàn bộ 5 bước chuẩn bị trạng thái $\|P(f)\rangle$ (chuẩn bị Dicke state, áp pha, nhân $B^T \mathbf{y}$, giải mã uncompute $\|\mathbf{y}\rangle$, QFT/Hadamard). | Chỉ tách riêng **bước giải mã hội chứng Reed–Solomon kết hợp Measurement-Based Uncomputation (MBUC)** theo thiết kế tiếp nối `arXiv:2510.10967` (được dẫn trong docstring verifier/baseline). |
| **Đầu vào / Đầu ra của mạch** | Nhánh giải mã nhận $\|B^T \mathbf{y}\rangle$ và uncompute $\|\mathbf{y}\rangle \to \|0\rangle^{\otimes m}$ bằng cổng thuận nghịch trực tiếp. | Thanh ghi $|\mathbf{y}\rangle$ đã được đo trong cơ sở $X$ (MBUC), tạo ra $m$ thanh ghi cổ điển `E0..E{m-1}` giữ kết quả đo $M_0, \dots, M_{m-1} \in \text{GF}(2^{12})$. Mạch chỉ nhận $n$ thanh ghi hội chứng lượng tử `S0..S{n-1}` ($S_i = \sum_j e_j \alpha^{(i+1)j}$), phải nhân pha toàn cục $(-1)^{\sum_j \text{popcount}(e_j \,\&\, M_j)}$, khôi phục nguyên vẹn `S0..S{n-1}` và trả mọi ancilla lượng tử về $\|0\rangle$. Cấm dùng cổng `Z_POW`. |
| **Phân bố trọng số lỗi thử nghiệm** | Trọng số $k \in \{0, \dots, \ell\}$ có biên độ $w_k$ chọn tối ưu để cực đại hóa $\langle s \rangle / m$ (SI Section 6). | Verifier (`optimal_dqi_weights`, dòng 174–185) lấy vector riêng chính đơn vị $w_0, \dots, w_\ell$ của ma trận 3 đường chéo đối xứng $A$ kích thước $(\ell + 1) \times (\ell + 1)$ với $A_{k,k} = k(q - 2r)/\sqrt{r(q - r)}$ và $A_{k-1,k} = \sqrt{k(m - k + 1)}$ (dẫn Lemma 9.2 của `arXiv:2408.08292`), rồi lấy mẫu trọng số lỗi $k$ theo xác suất $w_k^2$ (kỳ vọng trọng số lỗi $\approx 31.047$ trên cấu hình chuẩn). |
| **Thuật toán giải mã** | Đề cập Berlekamp–Massey (LFSR) cho OPI trên $\mathbb{F}_p$. | Baseline dùng `ProosAndZalkaDecoder` theo `arXiv:2510.10967`: EEA đồng bộ thuận ($222$ bước cho $n=70$) tính đa thức định vị lỗi $\sigma$ và đánh giá lỗi $\omega$ $\to$ Chien search + công thức Forney áp pha MBUC (có điều kiện cổ điển khi $M_j \ne 0$) $\to$ EEA đồng bộ ngược để uncompute. |
| **Xử lý lỗi giải mã & Hàm điểm** | Đánh giá tỷ lệ thỏa mãn kỳ vọng $\langle s \rangle / m$ và tổng số cổng Toffoli / qubit logic. | Với $k = \text{value\_errors} + \text{phase\_errors}$ lỗi trên $N$ shots, tính cận trên Clopper–Pearson một phía $\varepsilon_+$ ở độ tin cậy $1 - 2^{\text{log2\_delta}}$ ($\delta = 2^{-128}$), yêu cầu $\varepsilon_+ < 1/16$, nhân hệ số phạt lặp $R(\varepsilon_+) = \frac{\ln 2}{-\ln(1/2 + 2\sqrt{\varepsilon_+})}$, và chấm điểm $\text{score} = R(\varepsilon_+) \cdot Q^2 \cdot T$ (càng thấp càng tốt). |

## Khả năng áp dụng vào project

Các file trong repository được đối chiếu tại commit `74c543d217ad394457054f14a6ea9e66fd3c2552` (hash **Git blob** lưu trong [source.json](source.json)):

- [verifiers/dqi/verify_submission_dqi.py](../../../../verifiers/dqi/verify_submission_dqi.py): định nghĩa `ProblemSpecDQI`, `optimal_dqi_weights`, `sample_shots`, `clopper_pearson_upper_bound`, `repetition_overhead`, và hợp đồng kiểm tra thanh ghi / pha / ancilla.
- [src/dqi/DQI-BASELINE/solution.py](../../../../src/dqi/DQI-BASELINE/solution.py) (bản sao từ [verifiers/dqi/dqi_reference_circuit.py](../../../../verifiers/dqi/dqi_reference_circuit.py), giấy phép Apache-2.0): lớp `ProosAndZalkaDecoder` với `_initial_shift_loop`, `_synchronized_eea`, `_chien_search_and_forney_mbuc`, và `default_n_iters(n) = 3 * (n + 1) + 9`.
- [src/dqi/DQI-BASELINE/configs/baseline.json](../../../../src/dqi/DQI-BASELINE/configs/baseline.json) và [src/dqi/DQI-BASELINE/DESCRIPTION.md](../../../../src/dqi/DQI-BASELINE/DESCRIPTION.md).

**Ý nghĩa trực tiếp của paper đối với việc thiết kế mạch trong track `dqi`:**

1. **Giải thích nguồn gốc phân bố test của verifier:**
   Trong paper, trạng thái trước giải mã là chồng chập có trọng số $w_k$ trên các vector lỗi $\mathbf{y}$ có trọng số Hamming $k \le \ell$ (Eq. (3), Eq. (5)). Khi chuyển sang MBUC trong benchmark, verifier kiểm tra mạch giải mã hội chứng bằng cách lấy mẫu lỗi có trọng số $k$ theo đúng phân bố $w_k^2$ (`optimal_dqi_weights`). Vì $w_k^2$ tập trung mạnh ở vùng $k$ gần $\ell = 35$ (trọng số lỗi trung bình $\approx 31.05$ trên cả run `dev_5min` và `full`), bất kỳ cải tiến nào cắt giảm số bước giải mã phải đặc biệt kiểm soát tỷ lệ lỗi ở các trọng số $k$ gần $35$, không chỉ ở $k$ nhỏ.
2. **Vai trò sống còn của uncomputation và độ sạch ancilla:**
   Bước 4 của DQI (trang PDF 2 / trang 832) đòi hỏi xóa sạch thông tin lỗi khỏi nhánh phụ để Bước 5 giao thoa đúng. Trong hợp đồng verifier, bất kỳ sai lệch nào trên `S0..S{n-1}` hoặc ancilla khác $|0\rangle$ sau khi chạy mạch đều bị tính là `value_error`, làm tăng $\varepsilon_+$ và tăng hệ số phạt $R(\varepsilon_+)$.
3. **Nút thắt tài nguyên nằm ở bước tìm đa thức định vị lỗi (Berlekamp–Massey / EEA):**
   Paper chỉ rõ tại trang PDF 4 (trang 834) rằng chi phí chủ đạo của DQI + giải mã đại số là cài đặt thuận nghịch của vòng lặp tìm LFSR / đa thức định vị lỗi. Điều này hoàn toàn nhất quán với cấu trúc của `ProosAndZalkaDecoder` trong baseline, nơi hai lượt chạy `_synchronized_eea` (thuận và nghịch, mỗi lượt $222$ bước lặp đồng bộ với chia trường hữu hạn, unary iteration và hoán đổi thanh ghi) chiếm phần lớn số cổng Toffoli và số qubit.
4. **Giới hạn của bài báo gốc khi áp vào code baseline:**
   Bài báo Nature trình bày khung thuật toán DQI tổng quát và ước lượng Berlekamp–Massey trên $\mathbb{F}_{521}$, nhưng **không** trình bày chi tiết mạch MBUC trên $\text{GF}(2^{12})$ hay cấu trúc EEA đồng bộ của `ProosAndZalkaDecoder` (vốn thuộc bài báo tiếp theo `arXiv:2510.10967` được dẫn trong docstring của `solution.py`). Do đó, để tối ưu chi tiết các bước con bên trong `ProosAndZalkaDecoder`, agent nghiên cứu cần kết hợp kiến thức nền từ note này với việc phân tích trực tiếp code `solution.py` (và đọc thêm `arXiv:2510.10967` nếu nguồn đó được đăng ký vào kho).

## Hypothesis gợi ý và cách kiểm chứng

Các gợi ý dưới đây là **suy luận kỹ thuật từ việc đối chiếu paper với cấu trúc baseline và hàm điểm cuộc thi**, chỉ dùng để tham khảo khi sinh hypothesis trong luồng experiment (chưa tạo Issue, chưa thử nghiệm):

| Hướng suy luận có thể cân nhắc | Cơ sở từ paper + code baseline | Cách kiểm chứng và điều kiện bác bỏ |
| --- | --- | --- |
| **Đánh đổi số bước lặp tìm đa thức định vị lỗi (`n_iters` trong EEA) với hệ số phạt $R(\varepsilon_+)$** | Paper chỉ ra bước giải mã hội chứng (LFSR/EEA) là chi phí cổng chủ đạo và cho phép giải mã không hoàn hảo (SI Theorem 7.1); verifier cho phép $\varepsilon_+ < 1/16$ qua hệ số phạt $R(\varepsilon_+)$. Tuy nhiên, phân bố trọng số lỗi $w_k^2$ dồn về $k \approx 31\text{–}35$. | Quét giảm nhẹ `n_iters` dưới mức bảo thủ $3(n+1)+9 = 222$ trên profile `dev_5min`. Bác bỏ ngay nếu tỷ lệ lỗi trên các mẫu $k \approx 31\text{–}35$ làm $R(\varepsilon_+) \cdot T$ tăng lên hoặc làm $\varepsilon_+ \ge 1/16$. |
| **Giảm số lượng thanh ghi qubit $Q$ trong bước giải mã đại số (hoặc thay đổi cấu trúc lưu trữ giữa EEA và Berlekamp–Massey)** | Paper nhấn mạnh bài toán giải mã chỉ cần tìm đa thức định vị lỗi bậc $\le \ell = n/2 = 35$, trong khi hàm điểm của cuộc thi phạt bậc hai theo số qubit ($Q^2 \cdot T$). Trong baseline, `reg_a` và `reg_b` mỗi mảng giữ $m_{\text{eea}} = n + 3 = 73$ thanh ghi 12-bit ($1752$ trên tổng $1893$ qubit). | Phân tích bất biến bậc đa thức của EEA (hoặc thuật toán Berlekamp–Massey như paper đề cập ở trang PDF 3–4) để xem có thể cắt giảm các ô thanh ghi không bao giờ chứa hệ số khác 0 hoặc thu gọn độ rộng lưu trữ mà vẫn đảm bảo tính thuận nghịch không. Bác bỏ nếu chi phí cổng điều khiển phát sinh làm tăng tích $Q^2 \cdot T$ hoặc làm hỏng uncompute. |
| **Tối ưu phần đánh giá đa thức và áp pha MBUC (`_chien_search_and_forney_mbuc`)** | Trong MBUC, kết quả đo cơ sở $X$ trên $m = 4095$ vị trí là cổ điển (`error_mbuc`), và chỉ cần áp pha $(-1)^{\sum_j \text{popcount}(e_j \,\&\, M_j)}$. Baseline đã dùng `push_condition` để bỏ qua nghịch đảo Forney khi $M_j = 0$, nhưng vẫn thực hiện nhân hằng số dịch bước cho mọi $j$. | Kiểm tra xem có thể giảm số qubit phụ (`sigma_prime_inv`, `located`, ` inverse_chain`) hoặc giảm số cổng trong chuỗi nghịch đảo Itoh–Tsujii / tổng XOR mà không vi phạm điều kiện không dùng `Z_POW` và giữ nguyên pha. |

## Bằng chứng trong project và câu hỏi còn mở

- **Bằng chứng hiện có của baseline (không phải thử nghiệm mới từ note này):**
  Theo [src/dqi/SCORES.md](../../../../src/dqi/SCORES.md) và [src/dqi/DQI-BASELINE/DESCRIPTION.md](../../../../src/dqi/DQI-BASELINE/DESCRIPTION.md):
  - Run `full` ([verifier.json](../../../../results/dqi/DQI-BASELINE/baseline/full/20261107T094931Z-local-full-5ed1c6/verifier.json)): `PASS` trên $102,400$ shots ($m = 4095, n = 70, \text{degree} = 12, r = 2016$), `value_errors = 0`, `phase_errors = 0`, `effective_error_rate` $\varepsilon_+ \approx 8.6606 \times 10^{-4}$, `repetition_factor` $R(\varepsilon_+) \approx 1.1913$, `num_qubits` $Q = 1893$, `toffoli_count` $T \approx 5,725,108.38$, `score` $\approx 2.4439 \times 10^{13}$.
  - Run `dev_5min` ([verifier.json](../../../../results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5/verifier.json)): `PASS` trên $4,096$ shots, `value_errors = 0`, `phase_errors = 0`, $\varepsilon_+ \approx 0.02143$, $R(\varepsilon_+) \approx 2.9848$, $Q = 1893$, $T \approx 5,725,117.54$, `score` $\approx 6.1235 \times 10^{13}$.
  - Cả hai run đều cho thấy ngay cả khi mạch giải mã có $0$ lỗi thực nghiệm ($k = 0$), hệ số phạt thống kê Clopper–Pearson $R(\varepsilon_+)$ vẫn phụ thuộc mạnh vào số mẫu $N$ ($2.9848$ ở $4,096$ shots so với $1.1913$ ở $102,400$ shots).
- **Câu hỏi còn mở và giới hạn chưa kiểm chứng:**
  - Chưa có hướng thử nghiệm (`DQI-*` ngoài `DQI-BASELINE`) nào được mở hoặc chạy trong repository tính đến thời điểm viết note này.
  - Các chi tiết chứng minh trong *Supplementary Information* của paper (đặc biệt là SI Section 6 về ma trận 3 đường chéo xác định $w_k$, SI Theorem 7.1 về ảnh hưởng của lỗi giải mã, và SI Section 13 về mạch Berlekamp–Massey trong Qualtran) không có trong bản PDF 7 trang nên chưa được đối chiếu trực tiếp từ nguồn SI.
  - Chi tiết thiết kế mạch MBUC và EEA đồng bộ của baseline nằm trong bài báo tiếp theo `arXiv:2510.10967` (được dẫn trong docstring [solution.py](../../../../src/dqi/DQI-BASELINE/solution.py)), chưa nằm trong tài liệu PDF của note này.

## Tài liệu liên quan

Các tài liệu được trích dẫn trong bài báo (trang PDF 5–7 / trang 835–836) hoặc trong docstring verifier/baseline có liên hệ trực tiếp với track `dqi`:

- **Từ danh mục tham khảo của paper:**
  - [22] Bartschi, A. & Eidenbenz, S., *Short-depth circuits for Dicke state preparation*, Proc. IEEE QCE (2022) — chuẩn bị trạng thái Dicke ở Bước 1.
  - [23] Wang, H., Tan, B., Cong, J. & De Micheli, G., *Quantum state preparation using an exact CNOT synthesis formulation*, Proc. DATE, 1–6 (2024) — chuẩn bị chồng chập trạng thái Dicke ở Bước 1.
  - [26] Berlekamp, E. R., *Algebraic Coding Theory* (revised edition, World Scientific, 2015) — thuật toán giải mã Berlekamp–Massey cho mã Reed–Solomon.
  - [37] Harrigan, M. P. et al., *Expressing and analyzing quantum algorithms with Qualtran*, preprint `arXiv:2409.04643` (2024) — công cụ ước lượng tài nguyên cho bộ giải mã tại $p = 521$.
  - [59] Shutty, N., Jordan, S. & Khattar, T., *Supporting material for: optimization by decoded quantum interferometry*, Zenodo `https://doi.org/10.5281/zenodo.13327870` (2025) — dữ liệu và code thực nghiệm/ước lượng tài nguyên của bài báo.
- **Từ docstring của verifier/baseline trong repository (chưa đọc bản gốc trong note này):**
  - `arXiv:2408.08292` — bản preprint đầy đủ của bài báo DQI (được `verify_submission_dqi.py` dẫn cho Lemma 9.2 về ma trận trọng số $w_k$).
  - `arXiv:2510.10967` — tài liệu mô tả mạch giải mã Reed–Solomon MBUC và thuật toán EEA đồng bộ thuận nghịch được cài đặt trong `ProosAndZalkaDecoder` ([solution.py](../../../../src/dqi/DQI-BASELINE/solution.py), giấy phép Apache-2.0 theo `src/LICENSE.txt`).
