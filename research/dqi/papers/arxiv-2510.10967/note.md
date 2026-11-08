# Verifiable Quantum Advantage via Optimized DQI Circuits — EEA và giải mã RS thuận nghịch

Status: draft
Track: dqi
Source: arXiv:2510.10967v1; paper.pdf; metadata và SHA-256 trong source.json
Version: v1 (arXiv 2025-10-13; trang đầu ghi 2025-10-09); truy cập 2026-11-08

- Tác giả: Tanuj Khattar, Noah Shutty, Craig Gidney, Adam Zalcman, Noureldin Yosri, Dmitri Maslov, Ryan Babbush, Stephen P. Jordan; Google Quantum AI.
- Bản đọc: [PDF người dùng cung cấp](paper.pdf), 52 trang, giữ nguyên bytes; không tải bản thay thế hoặc assets ngoài PDF.
- Phân loại: paper, track `dqi`, vì mô tả trực tiếp decoder EEA/MBUC mà baseline DQI dẫn.
- Phạm vi đọc kỹ: I–II (tr. 2–15), V.A–B (tr. 27–28), C (tr. 39–41), D (tr. 41–43), F (tr. 48–52). Đọc abstract/mục lục (tr. 1–2), phần B.3 trên tr. 39 để hiểu chỗ nối với C. Trực quan đối chiếu tr. 14, 15, 27, 40, 43 cho phương trình, bảng và giới hạn vòng lặp.
- Chưa đọc đầy đủ: III–IV về classical attacks/chứng minh tiệm cận (tr. 15–27), các layout vật lý tr. 29–31, kết luận/references tr. 32–34, A, B.1–2, E. Không xác nhận độc lập chứng minh hardness, tối ưu tiệm cận, mạch Qualtran/Zenodo, hoặc chạy code trong F. F đã đọc ở mức thuật toán và đối chiếu cấu trúc; chưa kiểm chứng từng dòng/cổng.
- Trạng thái: chờ review độc lập bước 04; chưa dùng làm note ready cho nghiên cứu.

## Vấn đề và kết quả của paper

DQI chuẩn bị trạng thái có biên độ tỷ lệ với đa thức tăng cường $P(f(x))$, với $f$ là số ràng buộc thỏa trừ số không thỏa. Bài max-LINSAT có ma trận $B$ kích thước $m\times n$ trên $\mathbb F_q$ và các tập chấp nhận $F_i$; dual code là $C^\perp=\{e:B^Te=0\}$. Khả năng sửa tối đa $\ell$ lỗi quyết định bậc đa thức tăng cường (I, tr. 3, Eq. 1–2).

OPI tìm đa thức $Q(y)$ bậc tối đa $n-1$ để tối đa số điểm $y\ne0$ có $Q(y)\in F_y$. Với $m=q-1$, ma trận Vandermonde dẫn tới giải mã Reed–Solomon (RS). Paper chuyển trọng tâm sang $q=2^b$: cộng là XOR; bình phương và nhân hằng là mạch tuyến tính CNOT; nhân hai toán hạng lượng tử cần tài nguyên phi-Clifford (II.C, tr. 13).

Ba đóng góp hữu ích cho track này (II, tr. 4–15):

1. Sparse Dicke state và tạo từng ký hiệu lỗi rồi MBU giảm nhu cầu giữ thanh ghi lỗi dày $mb$ qubit.
2. EEA đồng bộ với hệ số Bézout tường minh: chứa thương ngay trong vùng trống của thanh ghi dùng chung, hợp nhất chu kỳ số học.
3. EEA với biểu diễn Dialog: giữ lịch biến đổi thay vì vật chất hóa hệ số Bézout. EEA rẻ hơn nhưng việc đánh giá đa thức phía sau có thể đắt hơn.

Tác giả báo leading space $2nb$ cộng overhead điều khiển logarithmic; đây là hạng đầu theo mô hình của paper, không phải số qubit chính xác của circuit bất kỳ. Các bảng III–IV/V.A ghi $2nb+O(\log_2 n)$. Với $(m,n,b,r)=(4095,70,12,2016)$, Table VI, tr. 27 ghi $5.72\times10^6$ Toffoli, $1.52\times10^8$ Clifford, 1885 qubit; số trial Prange và Extended Prange (XP) lần lượt $4.75\times10^{26}$ và $1.97\times10^{23}$. Đây là **ước lượng của tác giả** bằng phân tích Qualtran, không phải một thí nghiệm phần cứng hay điểm project.

Phát biểu quantum advantage/độ khó dựa trên các thuật toán cổ điển được tác giả xét, không phải cận dưới vô điều kiện cho mọi thuật toán cổ điển. Note chưa audit III–IV nên không dùng phát biểu tối ưu tiệm cận làm tiền đề triển khai. V.A mô tả gate count cho end-to-end DQI và qubit của reversible decoder; cần giữ phạm vi này khi so với benchmark chỉ chấm decoder.

## Thuật toán và công thức cần dùng

### Ký hiệu và giao diện

Theo Table II, tr. 5: $q=2^b$ là kích thước trường; $b$ là bit mỗi ký hiệu; $m$ là số ràng buộc/độ dài codeword; $n$ là số biến OPI/số syndrome; $\ell$ là số lỗi có thể sửa; $r=|F_i|$. Trong cấu hình RS được xét, $\ell=n/2$ với $n$ chẵn. Không nhầm $n$ với số qubit hoặc bậc field. Chữ $m$ trong Appendix C là bậc field, còn biến local `m=n+3` trong baseline là chiều dài mảng EEA, khác $m=4095$ của OPI.

### Chuẩn bị syndrome và sửa pha MBU

II.A, tr. 5–7, Eq. 3–8:

1. Chuẩn bị chồng chập các tập vị trí lỗi có kích thước $k\le\ell$, trọng số $w_k$. Lưu chỉ số tăng dần trong $\ell$ thanh ghi, mỗi thanh ghi $b$ bit, padding bằng 0. State trong Eq. 3 có hệ số $w_k/\sqrt{\binom mk}$ trên mỗi tập con kích thước $k$.
2. Chuẩn hóa $g_i=(f_i-\bar f)/c$ để Fourier coefficient $\tilde g_i(0)=0$ và tổng bình phương biên độ bằng 1. Isometry $G_i$ gửi bit 0 sang ký hiệu 0 và bit 1 sang $\sum_{e\ne0}\tilde g_i(e)|e\rangle$ (Eq. 4–5).
3. Tạo từng $e_i$, cập nhật syndrome bằng cột thứ $i$ của $B^T$ nhân $e_i$, đo thanh ghi lỗi trong cơ sở X, giữ kết quả cổ điển $c_i$. Pha sinh ra là $(-1)^{c_i\cdot e_i}$, tích vô hướng bit modulo 2. Tái dùng thanh ghi $b$ qubit cho vị trí kế tiếp. Việc MBU sparse locator cũng cần sửa pha tương ứng.
4. Decoder thuận nghịch suy ra từng lỗi từ syndrome để bù pha; dọn dữ liệu phụ, rồi IQFT và đo để lấy nghiệm OPI. Đo/xóa thanh ghi mà bỏ bước sửa pha không tương đương uncompute.

Project chỉ triển khai khâu decoder/phase fixup. Sparse Dicke, $G_i$, IQFT không thuộc giao diện submission hiện tại.

### EEA tường minh và thanh ghi dùng chung

II.B, tr. 7–11, Eq. 9–11, Fig. 1: với $r_{-1}=A,r_0=B$, tính $r_i=r_{i-2}-q_i r_{i-1}$ và duy trì $Au_i+Bv_i=r_i$. Mỗi bước có ma trận $\tau_i=\left(\begin{smallmatrix}0&1\\1&-q_i\end{smallmatrix}\right)$; thứ tự tích là $\tau_i\cdots\tau_1$. Chuẩn hóa và cách đánh số hàng/cofactor phải được kiểm tra khi chuyển sang code; không suy ra thứ tự thanh ghi chỉ từ ký hiệu $u,v$.

Synchronized EEA dùng hai mảng chứa phần dư và cofactor ở hai đầu, cùng con trỏ bậc, cờ, counter và halting counter. Khoảng trống được đảm bảo bởi quan hệ bậc cho phép chứa thương mà không cắt heuristic độ dài thương. Các giai đoạn logical là chia dài, chuẩn hóa phần dư, căn cofactor, cập nhật cofactor, hoán đổi. Một chu kỳ số học dùng chung phục vụ chia và cập nhật cofactor, với điều khiển theo counter; local CSWAP truy cập thương (II.B.2, tr. 10; F/Fig. 9, tr. 49).

Số vòng cố định phải bao phủ mọi nhánh của chồng chập, còn nhánh đã dừng giữ thông tin cần để đảo. Không được thay halt quantum bằng nhánh Python theo dữ liệu lượng tử. Sau sửa pha, đảo EEA và bước căn chỉnh để trả syndrome/ancilla đúng giao diện.

### Dialog và đánh đổi khi tiêu thụ kết quả

II.B.3, tr. 10–13: Dialog ghi các biến đổi đơn giản của EEA division-free, gồm dịch, đổi chỗ và trừ bội. Lịch này cho phép phát lại tác động lên vector khác hoặc đánh giá cofactor tại một điểm mà không lưu toàn bộ đa thức. Thanh ghi phần dư co lại khi Dialog tăng; cơ chế dùng lại chỗ trống là nguồn tiết kiệm space.

Không hiểu “division-free” là hoàn toàn không dùng nghịch đảo field: Table V vẫn có $n$ lần GF inverse cho EEA implicit và Fig. 11/12 vẫn có bước tính tỷ lệ hệ số. Tên gọi nói về biến thể EEA, không loại bỏ mọi chi phí arithmetic bên dưới.

Giới hạn biểu diễn: phần diễn giải II.B.3 dùng hạng đầu $2nb$; Fig. 11, tr. 51, khởi tạo `2*n+3+degree(gcd)` phần tử và giả thiết hệ số đầu khác 0, nên không suy rộng cận chính xác cho mọi cặp đa thức/GCD. Fig. 12, tr. 52, chuyên biệt RS dùng `2*n+3` và `n-1` bước, giữ cả hệ số lẫn quyết định swap. Cần tính control/garbage, căn chỉnh, GCD và uncompute thực tế nếu triển khai; note không chứng minh circuit Dialog đầy đủ.

### Key equation, Chien và Forney

II.D, tr. 13–15, Eq. 12–15:

$$S(z)=\sum_{i=0}^{n-1}s_i z^i,\qquad \sigma(z)S(z)\equiv\Omega(z)\pmod{z^{2\ell}}.$$

Trong miền lỗi hợp lệ $|e|\le\ell$, $\sigma$ là locator, $\Omega$ evaluator. EEA chạy trên $z^{2\ell}$ và $S$, dừng tại phần dư đầu tiên có bậc nhỏ hơn $\ell$, lấy $\sigma\propto v_i,\Omega\propto r_i$. Cặp này có tự do nhân cùng một scalar khác 0; phát biểu “unique” trên tr. 14 phải hiểu có quy ước chuẩn hóa thích hợp, không phải duy nhất hệ số thô. Trường hợp syndrome 0 cần nhánh không lỗi hợp lệ.

Chien tìm các điểm có $\sigma(\gamma_j^{-1})=0$. Theo Eq. 15 của paper, giá trị lỗi được viết

$$e_j=-\frac{\Omega(\gamma_j^{-1})}{\sigma'(\gamma_j^{-1})}.$$

Đây là công thức theo convention của nguồn; chỉ chia tại root đơn hợp lệ với mẫu khác 0. Trong characteristic 2 dấu trừ bằng dấu cộng và đạo hàm chỉ giữ hệ số bậc lẻ. Không áp Eq. 15 thẳng lên mảng packed: Fig. 10, tr. 50, dùng đảo chỉ số vị trí và `const_to_mul` theo bậc/cách căn thanh ghi; Fig. 12 cũng có prefactor. Baseline gộp prefactor vào các phép nhân hằng ở Chien. Cần giữ convention syndrome $S_i=\sum_j e_j\alpha^{(i+1)j}$ của verifier khi ánh xạ.

Table V, tr. 15, so chi phí leading-order của decoder (QQ = hai toán hạng lượng tử; QC = một toán hạng hằng cổ điển):

| Khâu | Explicit QQ | Explicit QC | Explicit inverse | Implicit QQ | Implicit QC | Implicit inverse |
| --- | --- | --- | --- | --- | --- | --- |
| EEA | $3n^2$ | — | $6n$ | $n^2$ | — | $n$ |
| Chien + Forney | — | $mn$ | $m$ | $2mn$ | $mn/2$ | $m$ |
| Tổng | $3n^2$ | $mn$ | $m+6n$ | $2mn+n^2$ | $mn/2$ | $m+n$ |

Trên GF($2^b$), QC có thể chỉ cần Clifford, còn QQ cần Toffoli. Vì $m\gg n$, giảm EEA bằng Dialog có thể bị chi phí phát lại $2mn$ QQ lấn át. Không dùng cột EEA riêng để kết luận Dialog tốt hơn decoder explicit. Các con số là số phép field, chưa phải tổng gate sau control, dọn ancilla hoặc score benchmark; cũng không thay thế Table III về full GCD.

## Điều kiện đúng, sai số và tài nguyên

### Vòng lặp và giới hạn cần kiểm chứng

Appendix D, tr. 41–43, đặt $d_i=\deg Q_i$, $s_i$ là giảm bậc phần dư, $D_k=\sum_i d_i$, $S_k=\sum_i s_i$ và $d_0=0$. Nguồn đếm $T_i=2d_i+s_i+d_{i-1}+2$, do đó $T=3D_k+S_k-d_k+2k$. Với full PEEA trên đầu vào coprime bậc $(n,n-1)$, Theorem D.5 ghi $6n-1$. Với half-PEEA, Theorem D.6 ghi $6\lfloor n/2\rfloor+5$.

**Giới hạn kiểm chứng:** chưa tái lập chứng minh cận half-PEEA cho mọi syndrome hoặc ánh xạ từng cycle sang baseline. Phần chứng minh tr. 43 lấy $D_{k,\max}=\lfloor n/2\rfloor+1$ khi dừng $D_k>n/2$; cần kiểm tra riêng khả năng bước cuối nhảy bậc lớn, vì ngưỡng dừng tự nó không chứng minh cận trên này. Không dùng số 215 (thế $n=70$) làm căn cứ tự động giảm baseline từ 222 bước. Fig. 10 còn gọi `n_steps=3.75`, khác công thức default của baseline; initialization, padding và halting cần được đối chiếu độc lập.

### Arithmetic và lỗi ký hiệu trong nguồn

II.C và Appendix C: phép cộng/squaring/nhân hằng là exact field arithmetic theo basis và đa thức bất khả quy đã chọn. Table VII, tr. 39, báo GF($2^{12}$) multiplication 51 Toffoli + 1506 CNOT, hoặc 51 PCTOF trong thư viện parity-control. PCTOF gộp parity controls/targets nên “0 CNOT” ở cột thư viện đó không có nghĩa không còn công việc tuyến tính khi phân rã sang gate set khác. Không chuyển số này sang Kickmix mà chưa đối chiếu basis, polynomial, target initialization và uncompute.

Appendix C.3, tr. 40, trình bày uncompute $|x\rangle|y\rangle|xy\rangle$ bằng đo X của product rồi sửa pha Clifford/CZ. **Lưu ý nguồn v1:** đoạn này định nghĩa $h(a,b)$ là Hamming weight của $a\oplus b$ rồi dùng làm số mũ pha Hadamard; định nghĩa đó không khớp quy tắc Fourier nhị phân. Suy luận kiểm tra của người viết note: $\langle c|H^{\otimes b}|p\rangle=2^{-b/2}(-1)^{c\cdot p}$, nên pha cần là $(-1)^{c\cdot(xy)}$. Vì mỗi bit product là đa thức bilinear trên bit của $x,y$, pha có thể bù bằng các CZ theo kết quả đo. Giữ rõ đây là hiệu chỉnh ký hiệu được suy ra từ đồng nhất thức Hadamard, không chép nguyên định nghĩa $h$ sai thành công thức triển khai. Chưa audit gate-depth bound CZ trên cùng trang.

### Ước lượng vật lý

V.B, tr. 28, báo khoảng 800 nghìn physical qubit và khoảng 1 giờ cho instance 4095/70/12. Các giả thiết gồm grid nearest-neighbor, gate error 0.1%, cycle surface code 1 microsecond, reaction 10 microseconds, hot/cold storage và magic-state cultivation. Nguồn ước lượng khoảng 16 phút/shot, xác suất thành công khoảng 77.9%, khoảng 4 lượt để tăng xác suất. Đây là dự toán kiến trúc với overhead giả định; chưa kiểm chứng layout và không phải thời gian chạy simulator/project.

## Khả năng áp dụng vào project

Snapshot đối chiếu: commit `9e4a371da8c952bdc6f96090562efeff8d71bf59`; SHA-256 của Git blob được ghi trong `source.json`. Đây là snapshot đọc code, không gán làm SHA build artifact cũ.

| Nơi trong project | Liên hệ và ràng buộc |
| --- | --- |
| [solution.py](../../../../src/dqi/DQI-BASELINE/solution.py), `ProosAndZalkaDecoder.build_syndrome_decoding_mbuc` | Căn đầu vào → EEA thuận → Chien/Forney sửa pha → EEA ngược → dọn initialization. Hai mảng dài `n+3`, con trỏ/counter và scaffold góp vào qubit thực. |
| Cùng file, `_multiply_and_add_or_sub`, `_shift_b_array_right`, `_update_metadata`, `_swap_a_and_b` | Các giai đoạn synchronized EEA tương ứng II.B.2/Fig. 9; invariant thanh ghi/con trỏ quan trọng hơn việc chỉ đúng phép chia cổ điển. |
| Cùng file, `_chien_search_and_forney_mbuc` | Tận dụng nhân hằng; gộp prefactor vào bước cập nhật omega; mask cổ điển điều khiển phase fixup; dọn inverse scaffold và hoàn tác alignment. |
| Cùng file, `default_n_iters` | `3*(n+1)+9=222` tại `n=70`; chưa có chứng minh trong note cho một số vòng nhỏ hơn. |
| [baseline.json](../../../../src/dqi/DQI-BASELINE/configs/baseline.json) | `m=4095,n=70,degree=12`; trong verifier thêm `r=2016`, tối đa 35 lỗi. |
| [verify_submission_dqi.py](../../../../verifiers/dqi/verify_submission_dqi.py) | Chấm decoder phase oracle, không chấm toàn bộ OPI. Thanh ghi syndrome little-endian phải phục hồi; mọi qubit phụ về 0; pha bằng $(-1)^{\sum_j\operatorname{popcount}(e_j\mathbin{\&}M_j)}$; không cho `Z_POW`. |

Verifier dùng $\epsilon_+$ là cận trên Clopper–Pearson một phía, confidence $1-2^{-128}$; yêu cầu $\epsilon_+<1/16$ và score $R(\epsilon_+)Q^2T$, với $R(\epsilon)=\ln2/[-\ln(1/2+2\sqrt\epsilon)]$, $Q$ là số qubit và $T$ là mean Toffoli-like/shot. Do đó không suy ra cải thiện score từ gate count paper. Không phát hiện lỗi trong mẫu cũng không có nghĩa $\epsilon_+=0$. So sánh cần cùng profile/shot count/environment/verifier, và kiểm tra cả giá trị, pha, workspace.

## Hypothesis gợi ý và cách kiểm chứng

Đây là suy luận để bàn giao, chưa nhận Issue hoặc triển khai thử nghiệm:

- **Tối ưu liveness/con trỏ của explicit EEA:** có thể giảm $Q^2T$ nếu giảm workspace mà không làm tăng compute/uncompute quá nhiều. Đối chứng baseline cùng config/profile; bác bỏ nếu score không giảm hoặc tăng lỗi pha/ancilla. Kiểm tra đặc biệt syndrome 0, ít lỗi và 35 lỗi, thương bậc lớn, vùng padding chạm nhau, chuyển counter và nhánh dừng.
- **Đánh giá Dialog ở mức decoder hoàn chỉnh:** nếu chỉ giảm QQ trong EEA mà tăng Chien playback thì chưa đủ. Đếm cả $m$ điểm, derivative, inverse, metadata/swap và cleanup; bác bỏ nếu tổng score xấu hơn explicit. Chưa có triển khai Dialog trong đợt này.
- **Giảm vòng EEA chỉ sau chứng minh/kiểm tra cycle mapping:** phân tích riêng initial shift, degree jumps và halted branches, rồi mới cân nhắc đo dưới cùng verifier. Cận D.6 hiện là phát biểu nguồn có giới hạn nêu trên, không phải bảo đảm cho baseline.

Mọi phép thử sau này phải theo luồng experiment riêng, giữ verifier và tham số chính thức; kết quả mẫu cần phân biệt với chứng minh toàn miền.

## Bằng chứng trong project và câu hỏi còn mở

[Run full baseline đã có](../../../../results/dqi/DQI-BASELINE/baseline/full/20261107T094931Z-local-full-5ed1c6/verifier.json) ghi PASS, 102400 shots, 0 value errors, 0 phase errors, 1893 qubit, mean Toffoli-like 5725108.382109375, score 24439463583672.93. Đây là bằng chứng lịch sử được đọc, **không chạy lại trong nhiệm vụ này**. [Provenance](../../../../results/dqi/DQI-BASELINE/baseline/full/20261107T094931Z-local-full-5ed1c6/provenance.json) thuộc build trước Git; không suy ra SHA build từ snapshot đọc code hiện tại. Gần con số Table VI không chứng minh hai mạch hoặc phạm vi đếm giống hệt nhau.

Chưa có kết quả mới để quy cải thiện cho việc đọc paper này. Còn cần reviewer kiểm tra: convention Forney/packed arrays; caveat D.6; ký hiệu MBU ở C.3; chi phí control/cleanup của Dialog; phạm vi Table VI so với decoder benchmark. Các phần classical hardness và chứng minh tiệm cận chưa đọc đầy đủ phải được đọc/review bổ sung trước khi dùng làm căn cứ mới.

## Tài liệu liên quan

- [Nguồn và hash](source.json), [PDF v1](paper.pdf).
- [Note DQI gốc đã có](../doi-10.1038--s41586-025-09527-5/note.md): khung DQI tổng quát; note hiện tại bổ sung kiến trúc decoder binary field.
- [Baseline description](../../../../src/dqi/DQI-BASELINE/DESCRIPTION.md), [mã tham chiếu BTC](../../../../verifiers/dqi/dqi_reference_circuit.py), [license source](../../../../src/LICENSE.txt). Không copy code paper/Zenodo vào project trong đợt này.
