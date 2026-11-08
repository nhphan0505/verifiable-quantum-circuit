# Discovering state-of-the-art quantum circuits with large language models

Status: ready
Track: dqi
Source: https://arxiv.org/abs/2610.22367v1
Version: arXiv:2610.22367v1 (2026-10-15)

- Tác giả: Andi Gu, Alek H. Kemeny, Susanne F. Yelin, Mikhail D. Lukin (2026).
- Bản đọc: [paper.pdf](paper.pdf), 46 trang PDF; SHA-256 `3607f457c3349db74e10b131abadef23a4a2dea0fefa0cf6ac6d0ed9f37fdfd9`.
- Metadata/coverage: [source.json](source.json); truy cập bản local ngày 2026-11-08.
- Từ khóa: reversible arithmetic, conditional routing, history decoding, bounded failure, BM, phase-only decoding, quantized polynomial fitting, QROM.
- Quy ước dẫn trang: `PDF p.` tính từ trang đầu file. Phụ lục SI bắt đầu tại PDF p.18 (SI p.1); vì vậy SI p.n = PDF p.(n+17).

## Phạm vi đã đọc và giới hạn

Đọc main text PDF pp.1-11, gồm nguyên lý thiết kế, ví dụ divsteps và Methods; Table I PDF p.7; Extended Data Table 1 PDF p.17; SI I mở đầu và I.1 PDF pp.18-23; SI III và IV PDF pp.33-39 (p.33 chỉ từ đầu SI III). Kiểm tra trực quan PDF pp.7,17,19,21,23,34,36,37,38,39 để đối chiếu bảng và công thức (pp.17,19,37,39 được kiểm tra bổ sung ở bước 03). Đã xem mục lục SI p.1.

Chưa đọc chi tiết references PDF pp.12-14, Extended Data Figures PDF pp.15-16, Hermitian decoder SI I.2 PDF pp.24-27, modular-inversion SI II PDF pp.27-33, lattice gauge SI V PDF pp.40-43, hoặc chứng minh Appendix A PDF pp.44-46. Các trang biên chỉ đọc phần đã nêu; không coi phần divsteps main text là đã kiểm tra chứng minh. Không mở nguồn ngoài, code tác giả hoặc chạy evaluator của paper. Không khẳng định tái lập kết quả. Bản draft đã được tác giả tự rà và sửa ở bước 03 trên đầu vào `e04341630595f40fe30afa2d2f2bade8cf1e57dc`; chưa có review độc lập bước 04. Phạm vi và findings tự rà được ghi ở cuối note.

Paper được người dùng phân loại vào **dqi** trong bước 03; trọng tâm áp dụng là decoder Reed-Solomon. Phần hàm số và hóa học dưới đây giữ làm bối cảnh kỹ thuật dùng chung đã đọc, không đổi phạm vi hay ghi đè nguồn.

## Vấn đề và kết quả của paper

Paper tìm mạch tính hàm cổ điển nhưng phải tác động coherently, giữ interface và xóa ancilla. LLM đề xuất chương trình Python sinh mạch; evaluator kiểm tra và chấm; các họ kiến trúc được phát triển riêng rồi chia sẻ ứng viên tốt. Methods dùng OpenEvolve và MAP-Elites giữ các phương án đánh đổi giữa Toffoli và qubit, không chỉ giữ một thiết kế đang dẫn đầu (PDF pp.1-2,11). Đây là mô tả hệ thống của tác giả, không phải bằng chứng rằng search luôn tìm tối ưu toàn cục.

Mục tiêu paper là `TQ = T × Q`: T đếm Toffoli/CCZ; Q là số qubit logical đồng thời cực đại (Methods Eq.22, PDF p.11). Các số sau do tác giả báo, đã làm tròn trong Table I PDF p.7; không phải số đo project:

| Benchmark | Baseline (T,Q) | Mạch tìm được (T,Q) | Gain TQ tác giả báo |
| --- | --- | --- | --- |
| Reed-Solomon DQI | (5.1 triệu, 1938) | (440000, 1837) | 12× |
| HHL angle | (16000, 300) | (1348, 115) | 32× |
| Coulomb potential | (6355, 252) | (1140, 142) | 9.9× |
| Gaussian fixed-point | (24000, 362) | (1583, 139) | 39× |
| Fe2S2 alias-Select | (55000, 139) | (15000, 126) | 4.1× |

Paper xét tổng cộng tám task; bảy task giảm cả T và Q so baseline, nhưng baseline Hermitian chỉ là cách đảo tính ngây thơ, chưa có reversible compilation trước đó. Prime-field modular inversion báo (4.0 triệu,935) cho **toàn benchmark**, không chỉ một phép nghịch đảo và không gán một gain chung (Table I footnotes, Extended Data Table 1 PDF p.17). Các task này không cùng interface/dung sai với ba task trong project.

## Thuật toán và công thức cần dùng

### 1. Routing, giải mã lịch sử và ngân sách lỗi

**Routing** (PDF p.3, Eq.1): thay hai multiply-add có điều khiển bằng controlled swap chọn y/z, một multiply-add không điều khiển, rồi undo swap. Dạng tổng quát là `U_b = R_b^{-1} K R_b`: chỉ R_b phụ thuộc nhánh, K là kernel dùng chung. Chỉ áp dụng khi cả biểu diễn và đầu ra thật sự tương đương dưới routing; nhận thấy hai phép toán giống tên chưa đủ.

**Giải mã lịch sử** (PDF p.3, Eq.2): khởi tạo g_0=0, cập nhật `g_{j+1}=g_j+b_j 2^j`, với b_j là bit, không overflow. Invariant `0 <= g_j < 2^j` cho phép đọc bit j của g_{j+1} để biết b_j khi đảo. Quan trọng là invariant trên trạng thái reachable từ khởi tạo, không chỉ suy từ một phép cập nhật cục bộ.

**Ngân sách lỗi** (PDF pp.3,6-7): phải cô lập tài nguyên chỉ phục vụ các input hiếm, như vòng lặp/cuộn stack/prefix hệ số, rồi mới cắt bỏ. Xác suất hiếm phụ thuộc phân bố được quy định; không chuyển cutoff sang phân bố khác mà giữ nguyên khẳng định lỗi.

Ví dụ divsteps main text dùng tính chẵn/lẻ của hệ số để giải mã swap; các quyết định còn lại được giải mã hoặc lưu tùy độ sâu. Đây là minh họa đổi T lấy Q; note này không cung cấp decoder divsteps có thể triển khai độc lập vì chưa đọc SI II/Appendix A.

### 2. DQI: BM với routing và lưu rất ít discrepancy

SI I/I.1 (PDF pp.18-23), Eqs.24-40. Đặt F=GF(2^12), gamma là primitive element; có 4095 vị trí, tối đa 35 lỗi, 70 syndrome, mỗi syndrome 12 bit. Với error word e_j:

`S_i = sum_{j=0}^{4094} e_j gamma^{ij}`, i=1..70.

Locator `sigma(z)=product_{e_j != 0}(1-gamma^j z)` có nghiệm beta_j=gamma^{-j}. Đặt `S(z)=S_1+S_2 z+...+S_70 z^69`; key equation là `sigma S = omega mod z^70`, `deg omega < deg sigma <= 35` (Eqs.26-29). Promise trọng số <=35 bảo đảm duy nhất. DQI cần pha `(-1)^{<c,e(s)>_2}` và khôi phục syndrome, không cần xuất cả e (Eq.24). c là bit mask trong basis nhị phân cố định của trường.

BM xây locator từ discrepancy `Delta=sum_{i=0}^{min(deg sigma,r-1)} sigma_i S_{r-i}` tại vòng r. Bắt đầu `(sigma,tau,delta,d)=(1,1,1,0)`, mỗi vòng dịch template `tau_tilde=z tau`; Eq.33 định nghĩa bản BM chưa rescale:

- Delta=0: giữ sigma, dùng tau_tilde, giữ delta, d <- d+1.
- Delta!=0 và d>=0 (replace): `(sigma,tau,delta,d) <- (sigma-(Delta/delta)tau_tilde, sigma_old, Delta, -d)`.
- Delta!=0 và d<0 (retain): cập nhật sigma tương tự, giữ tau_tilde/delta, d <- d+1.

Tie-breaking của paper chọn replace khi bộ đếm cho phép, để ít lưu lịch sử; không tự thay bằng textbook BM. Với `alpha=Delta/delta != 0`, bản rescale (main Eq.5, PDF p.4) cho locator `tau_tilde-alpha^{-1}sigma_old` trong nhánh replace và giữ template sigma_old. Locator mới bằng `-alpha^{-1}` lần locator chuẩn, nên giữ nguyên nghiệm. Retain vẫn dùng `sigma_old-alpha tau_tilde`. Swap và chọn alpha/alpha^{-1} cho phép chia sẻ arithmetic path.

Invariant của bản rescale là `sigma_0 delta=1` (Eq.34, PDF p.21); vì tau_tilde có hệ số tự do bằng 0, có thể suy delta từ sigma_0 thay vì một thanh ghi riêng. Sau replace, `sigma_0=Delta^{-1}`, nên discrepancy cũng có thể khôi phục. Chỉ retain với Delta!=0 phải lưu discrepancy hiện tại. Stack bảo đảm worst-case cần 35 entry/665 qubit; paper cấp 1 entry/19 qubit. Đồng thời mỗi vòng chỉ cập nhật một prefix hệ số chọn offline từ phân bố DQI, không luôn toàn 36 hệ số. **Không có bảng cutoff đầy đủ trong đoạn SI đã đọc; không thể dựng chính xác mạch paper chỉ từ những con số tóm tắt.**

Figure S1 (PDF p.22): hơn một stack entry xuất hiện khoảng 1.0e-4; trên 400 triệu mẫu, tổng hai failure mode stack/prefix khoảng 1.4e-4. Đây là ước lượng thực nghiệm của tác giả, không phải bound worst-case cho từng syndrome.

### 3. DQI: reciprocal polynomial và pha trực tiếp

Sau BM, chuẩn hóa sigma_0=1. Eq.35-36 (PDF p.22) cho phép ghi đè syndrome bằng tích tam giác:

`omega_i = S_{i+1} + sum_{j=1}^{i} sigma_j S_{i-j+1}`, 0<=i<35, với sigma_j=0 khi j>deg sigma. Các S ở vế phải là syndrome ban đầu.

Một lịch khả thi suy trực tiếp từ tính tam giác (không phải lịch gate-level do paper cung cấp) là cập nhật i giảm dần: các S có chỉ số thấp hơn đích còn nguyên; khi đảo, đi i tăng dần để khôi phục các nguồn thấp trước khi dùng chúng. Mỗi cập nhật cộng một hàm của các thanh ghi khác nên đảo được; trong trường đặc trưng 2, cộng và trừ giống nhau. Mở rộng cùng công thức cho 0<=i<70 trên cả 70 word làm 35 word cao thành 0 trên decode đúng; dùng làm workspace rồi đảo để khôi phục input. Không được giả định các word này bằng 0 trên một decode đã bị cutoff làm sai.

Forney cần `e_j = kappa_j omega(beta_j)/sigma'(beta_j)` tại nghiệm (Eq.30); kappa_j là hệ số cố định theo convention vị trí. Binary parity biểu diễn được bằng field trace `Tr(mu_j e_j)`, với `Tr(a)=sum_{r=0}^{11}a^{2^r}` và mu_j là dual-basis mask tương ứng (Eq.37). Paper dùng **mask c cố định ngẫu nhiên**, chọn offline một phần pha tuyến tính trên syndrome để bỏ 71 vị trí, còn 4024 vị trí (PDF pp.18,23).

Vì sigma là tích các nhân tử khác nhau, sigma' không triệt tiêu tại nghiệm. Tính trước `Psi sigma' = 1 mod sigma` thay vì nghịch đảo trường tại mỗi vị trí; khi sigma(beta)=0, residual parity là `Tr(nu_j omega(beta) Psi(beta))`, với nu_j hấp thụ mask còn lại và kappa_j (Eqs.38-39). Với nu_j **cố định**, biểu thức là bilinear trên hai giá trị trường; paper dùng 12 Toffoli cộng zero-test 11 Toffoli, tổng 23/vị trí. Không mặc định giữ nguyên chi phí khi mask là dữ liệu runtime.

Đặc trưng 2 cho `sigma=E^2+z O^2`, E_i=sqrt(sigma_{2i}), O_i=sqrt(sigma_{2i+1}), `deg E,deg O<=17`, `sigma'=O^2`. Square/square-root trường là map tuyến tính trên bit. EEA tìm `AE+BO=1`; suy ra:

`(B^2+z A^2)sigma' = 1+A^2 sigma`.

Vậy `B^2+z A^2` cho giá trị reciprocal đúng tại các nghiệm (PDF p.23, Eq.40 và đoạn sau). Không cần nó trùng biểu diễn chuẩn bậc thấp của Psi. EEA này chạy trên hai đa thức bậc <=17, vẫn dùng EEA cho bài nhỏ dù BM thay EEA chính. A/B được lưu trong 35 syndrome word đã zero; sau scan đảo EEA rồi đảo tích syndrome. Trường hợp locator hằng/không có lỗi cần xử lý riêng khi triển khai; note chưa có implementation của tác giả cho biên này.

Tác giả báo scan khoảng 93000 Toffoli, EEA phụ khoảng 44000 mỗi chiều; tổng mạch khoảng 440000 Toffoli/1837 qubit. Có 7 wrong-sign trong 100000 test (PDF p.23), không đồng nghĩa mạch đúng mọi input hoặc full PASS trong project.

### 4. Hàm số: chia miền theo bit và fit đúng số học lượng tử hóa

SI III (PDF pp.33-36) dùng map cộng fixed-point `|x>|k> -> |x>|k+f_tilde(x)>`; cơ chế khác oracle pha invsqrt của project. Kỹ thuật chung là chọn interval từ bit, giảm bậc đa thức/độ rộng toán hạng, tích lũy thẳng vào đích, fit offline theo **đúng** cột tích bị bỏ, dịch, truncation và rounding. Không chỉ làm tròn hệ số fit số thực rồi giả định vẫn đạt sai số.

HHL (PDF p.34, Eqs.61-64): x=X/2^16 thuộc [1,32), cộng `round(2^32 arcsin(2^15/X))` vào accumulator 33 bit. Dùng 345 dyadic leaf `[L,L+2^b)` với L chia hết 2^b, b=8..15. Cyclic shift 15 bit thấp tạo `d=2^{15-b}(X-L)+c_L`, c_L cố định trong leaf và được hấp thụ vào fit. Kernel chung dùng `t <- g_1-g_2 d` ghi vào g_1, rồi `k <- k+g_0-dt`. Paper báo max error 9.95e-8 rad, T=1348,Q=115; đây không phải độ chính xác cho 1/sqrt(x).

Coulomb (PDF pp.35-36, Eqs.65-66): input hai điểm 3D, mỗi tọa độ 8 bit, hai điểm khác nhau. Cộng `round(2^24/sqrt(d2))` vào accumulator 25 bit, `d2=sum_c(r_i,c-r_j,c)^2`. Cộng trực tiếp các partial product vào một accumulator tính d2 chính xác. Chuẩn hóa `d2=2^e u`, 1<=u<2; parity e và 6 bit đầu mantissa chọn 128 đoạn tuyến tính, 6 bit kế là tọa độ cục bộ. Không có chuyện dùng thêm bit thấp rồi miễn phí bỏ sai số. MBU lookup tốn 17 Toffoli thay vì 126 khi đảo lookup; tác giả báo max absolute error 1.91e-6 trên các d2 đạt được, T=1140,Q=142.

Gaussian (PDF p.36, Eq.67): X_s signed 39 bit, x=X_s/2^32 thuộc [-8,8), cộng `round(2^32 exp(-x^2))`. Với x<0, chỉ complement để biểu diễn y=|x|-2^-32, bỏ carry +1 trong budget lỗi. Không cần tạo x^2. Trong 1024 interval rộng 2^-7: 455 dùng quadratic, 59 dùng constant, 510 trả 0; pruning cây lookup giảm 1022 xuống 495 Toffoli. Tái dùng coefficient qubit sau MBU làm carry ancilla. Max error tác giả báo 9.99e-8; T=1583,Q=139. Các cutoff này gắn hàm/domain riêng, không chuyển trực tiếp sang invsqrt.

### 5. Hóa học: tổ chức dữ liệu để rút ngắn QROM/Select

SI IV (PDF pp.36-39): `H=sum_l w_l P_l`, `lambda=sum_l |w_l|`. Prepare biên độ sqrt(|w_l|/lambda), Select áp dụng sign(w_l)P_l; block encoding cho H/lambda (Eqs.68-71). Benchmark là Fe2S2 20 orbital không gian/40 spin-orbital, 41052 Pauli term sau bỏ |w|<1e-4 Ha. Paper chủ động **không** benchmark mạng Givens DFTHC vì vượt mô hình kickmix (PDF p.37).

Alias method dùng bucket i và số tau 16 bit: chọn i nếu tau<keep(i), ngược lại alt(i) (Eq.72). Benchmark chỉ gồm `U_alias† Select U_alias`, giữ i/tau; không gồm chuẩn bị superposition đồng đều hay reflection của walk. Alias word rộng 34 bit chứa threshold, alternate index và dấu hai hệ số. Tính đúng cần cả bit permutation trên system và pha (PDF pp.37-38, Eqs.73-75). Cụ thể, a_l đánh dấu vị trí X/Y, z_l đánh dấu Z/Y, theta_l=0/1 cho dấu hệ số dương/âm. Các Pauli trong bảng này có số lượng Y chẵn, nên `eta_l=(n_Y(P_l) mod 4)/2` là bit và pha chỉ là dấu thực. Đặt sel=sel(i,tau), mạch cần:

`|i>|tau>|x> -> (-1)^phi |i>|tau>|x XOR a_sel>`,

`phi = theta_sel XOR eta_sel XOR parity(x AND z_sel)`.

x trong công thức pha là system state trước khi flip. Ancilla h/sel phải được xóa, i/tau giữ nguyên. Điều kiện Y chẵn thuộc benchmark cụ thể; không áp dạng pha ±1 này cho Pauli tổng quát có số Y lẻ.

Hai tự do preprocessing: đổi thứ tự term cùng hệ số/Pauli không đổi H; alias pairing khác nhau có thể giữ cùng phân bố đã làm tròn 16 bit. Nhóm các Pauli liên hệ bởi fixed Clifford frame thành block 2^k, dùng bit địa chỉ chọn conjugation của representative. Bảy frame giao hoán tạo 3221 block từ 41052 term; representative Select 3327 Toffoli, điều khiển/frame 534 (PDF p.38). Chỉ hai frame spin là symmetry bảo toàn độ lớn hệ số; các frame môi trường gần giống không bảo đảm hệ số bằng nhau, phải giữ từng hệ số độc lập. Quan hệ Pauli qua conjugation vẫn phải exact.

Alias pairing ưu tiên các row giống nhau, rồi pruning subtree khi hai nửa chứa cùng **chuỗi** word: `A,A,B,B,A,A,B,B` bỏ được một address bit, không chỉ khi cả subtree hằng. Paper báo alias QROM 10000 Toffoli so baseline đã merge repeated word 13000; không so với 41000 rồi coi đó là lookup baseline chuẩn. Cleanup MBU/sửa pha thêm 782 Toffoli. Tổng benchmark 15000/126, test mỗi row và thêm 2^24 input ngẫu nhiên (PDF p.39). Yêu cầu exact toàn domain là contract, không phải tuyên bố đã exhaustive mọi system state/tau.

## Điều kiện đúng, sai số và tài nguyên

Methods PDF pp.9-11, Eqs.10-22: trên mỗi basis input, circuit phải giữ permutation đích, pha đúng và ancilla sạch. MBU temporary AND dùng đo X rồi CZ theo outcome; bỏ correction có thể giữ đúng output cổ điển nhưng sai interference. Measurement record chỉ điều khiển diagonal correction theo mô hình paper, không chọn permutation khác nhau.

Nếu mọi trajectory (input x, measurement record m) đúng thì linearity cho coherent correctness. Sampling không chứng minh điều đó cho mọi trajectory. Với defective probability epsilon theo đúng input distribution và measurement record uniform, Eq.19 chặn norm sai khác bởi `2 sqrt(epsilon)`. Với candidate cố định trước khi lấy k mẫu độc lập và không lỗi, upper bound một phía tại confidence 1-delta là `epsilon <= 1-delta^(1/k)` (Eq.20); cho phép b lỗi thì dùng binomial tail Eq.21. Không áp bound ấy trực tiếp lên candidate được chọn bằng chính test draw sau nhiều vòng search.

Cần tách hai xác suất: epsilon_traj của Methods là tỷ lệ sai trên cặp (x,m); còn epsilon_input của SI I (PDF p.19) là trọng số các input mà circuit có thể sai pha/reset dirty ancilla. SI I chấp nhận <=100 wrong-sign/100000 test; với tính chất sign là hàm affine theo measurement record, một input lỗi bị phát hiện với xác suất ít nhất 1/2. Nếu p_det là tỷ lệ wrong-sign quan sát theo cả input và record, lập luận cho `epsilon_input <= 2 p_det`; vì vậy upper bound thống kê cho p_det phải được chuyển qua hệ số 2 trước khi áp cho input lỗi. Tác giả báo `epsilon_input <= 2.434e-3` tại confidence 97.5%, cùng Eq.25:

`|<f>_impl - <f>| <= 4 epsilon_input <f>`.

f là số constraint được thỏa, <f> là kỳ vọng DQI lý tưởng trên benchmark. Đây là bound riêng tác giả nêu cho circuit của họ (dẫn [16]); chưa kiểm tra lại chứng minh nguồn [16], không coi là hệ quả tự động của bound norm Methods cho mọi decoder. Các con số này khác confidence 1-2^-128 của verifier project; budget 10^-3 trong bảng không thay cho epsilon_input upper bound thống kê. Điều kiện candidate cố định trước test vẫn cần giữ khi diễn giải confidence sau search. Numerical tasks có bound sai số uniform riêng; phase và cleanup vẫn cần đúng, không được dùng numerical tolerance để bỏ sửa pha MBU.

## Khả năng áp dụng vào project

Snapshot đọc là commit `215bc3d10bbdcc59b9c860e9b3acf077703dfcd1`; các link dưới tính từ thư mục note. Hash **Git blob** của file đối chiếu nằm trong source.json; snapshot đọc không phải SHA build của các run lịch sử.

| Track | Điểm nối cụ thể | Khác biệt cần xử lý |
| --- | --- | --- |
| dqi | [baseline](../../../../src/dqi/DQI-BASELINE/solution.py), `ProosAndZalkaDecoder.build_syndrome_decoding_mbuc`, `_chien_search_and_forney_mbuc`; [verifier](../../../../verifiers/dqi/verify_submission_dqi.py) | Cùng 70 syndrome GF(2^12), m=4095; baseline synchronized EEA, và vẫn nghịch đảo sigma_prime tại từng vị trí. Project nhận E0..E4094 là classical mask **runtime, ngẫu nhiên mỗi shot**, khác fixed mask của paper. BM/routing có thể nghiên cứu riêng; phần cancel 71 vị trí và mạch bilinear 23 Toffoli không được bê nguyên xi. |
| invsqrt | [baseline](../../../../src/invsqrt/INV-BASELINE/solution.py), `_load_coefficients`, `_horner`, `_compute_y1`, `fixed_point_model`; [verifier](../../../../verifiers/invsqrt/verify_submission_invsqrt.py) | Cần pha beta/sqrt(x) với x nguyên 1..3133452, giữ input/ancilla; tol(x)=2^-24 beta/sqrt(x). Baseline đã Horner in-place và cắt partial product, hệ số bốn miền hiện tải bằng Clifford; thêm QROM nhiều đoạn có chi phí mới. Sai số tuyệt đối 1.91e-6 của Coulomb paper không chứng minh đạt relative phase tolerance này. |
| dfthcsos | [baseline](../../../../src/dfthcsos/DFT-BASELINE/solution.py), `batch_deltas`, `build_angle_k_circuit`; [contract](../../../../verifiers/dfthcsos/scoreinfra/circuits.py), [scoring](../../../../verifiers/dfthcsos/SCORING_README.md) | Task FeMoCo N=76 tải XOR delta batch góc, không phải sparse Pauli alias-Select Fe2S2. Có thể khảo sát repeated-subtree pruning trên bảng delta; phải giữ nguyên thứ tự selection/angle hoặc chứng minh đồng bộ mapping. Không mặc định được hoán vị row hay factorization tự do như alias table. |

Mô hình điểm thực trong snapshot:

- DQI: `R(eps_plus) Q^2 T`, `R(eps)=ln(2)/[-ln(1/2+2 sqrt(eps))]`, yêu cầu eps_plus<1/16, full mặc định 102400 shots, log2_delta=-128. T là mean Toffoli-like thực thi; Q dùng circuit.num_qubits. Đừng suy gain project từ TQ gain paper.
- Invsqrt: `Q (Toffoli + T_Z_POW/4)`, trong đó T_Z_POW gồm cả góc T chính xác và chi phí tổng hợp góc không Clifford/T theo verifier (góc Clifford miễn phí). Dung sai còn sau sai số số học quyết định chi phí tổng hợp Z_POW, nên giảm arithmetic T có thể tăng rotation cost.
- DFTHC: `lambda_eff T_total Q_total`, gồm chi phí mô hình hóa ngoài ANGLE oracle và giới hạn từng mạch; qubit toàn thuật toán khác Q cục bộ. Cần đánh giá vector giải mã từ góc và Hamiltonian accuracy, không chỉ QROM.

## Hypothesis gợi ý và cách kiểm chứng

Đây là suy luận của nhóm từ paper và snapshot, chưa nhận Issue/triển khai/chạy chấm trong luồng tài liệu.

1. **BM trước, phase scan sau:** so một BM locator có routing/invariant sigma_0 delta=1 với EEA baseline, giữ runtime-mask scan hiện có làm đối chứng tách phần thay đổi. Thử bản không cutoff trước trên trường nhỏ và các trọng số biên; sau đó khảo sát stack/prefix trên đúng distribution verifier. Bác bỏ nếu lỗi cleanup/pha hoặc `R Q²T` không giảm dù T giảm. Cần riêng test syndrome 0, Delta=0, tie replace/retain, stack overflow và suffix coefficient bị cắt; không lấy input làm lỗi rồi vẫn suy word cao bằng 0.
2. **Reciprocal polynomial với mask runtime:** kiểm tra lợi ích bỏ inverse tại từng scan point khi tính Psi từ locator; thiết kế trace/product nhận mask như dữ liệu classical, giữ chính xác field basis/prefactor của project. So chi phí EEA phụ, root test, phase correction và qubit sống đồng thời với baseline; bác bỏ nếu chuẩn bị reciprocal/điều khiển mask triệt tiêu lợi ích. Không mặc định offline cancel được 71 vị trí hoặc 23 Toffoli/point. Kiểm chứng root đơn, sigma hằng, error weight 0/1/35 và đảo toàn map syndrome.
3. **Invsqrt fit theo integer model:** so bảng nhiều đoạn/đa thức bậc thấp với baseline cubic+Newton, fit cả truncation vào một end-to-end error budget. Tính đủ lookup/MBU, normalization và Z_POW synthesis; kiểm tra mọi x hoặc bound chắc chắn trên miền, đặc biệt biên interval/power-of-four và margin tuyệt đối nhỏ nhất. Bác bỏ nếu không đạt tol(x) hoặc điểm Q*C tăng. Bảng/coefficients Coulomb của paper không phải cấu hình sẵn cho project.
4. **Prune repeated subtree của bảng angle delta:** đếm các subtree có hai nửa là cùng chuỗi word, không đổi data/địa chỉ. So với `build_angle_k_circuit` hiện có trên cùng batch/brot, giữ f_k(a) exact cho mọi a hợp lệ, mọi word đầu vào và phase sạch; kiểm tra padding, thứ tự forward/reverse và giới hạn 128 qubit/mạch. Bác bỏ nếu không có repetition hoặc logic phát hiện/điều khiển làm tăng tổng cost. Chưa kết luận bảng thật có đủ cấu trúc; không chạy dữ liệu/thí nghiệm trong luồng tài liệu.

Ứng viên được chọn bằng dev cần lượt kiểm chứng độc lập chưa dùng để chọn config, cùng đối chứng/profile/hash phù hợp; full hoặc seed mới theo quy trình experiment. Mô hình số học hoặc test trường nhỏ không thay full verifier.

## Bằng chứng trong project và câu hỏi còn mở

Chưa có run trong nhiệm vụ này triển khai BM/reciprocal hay tái lập các mạch paper. Không gán attribution nguồn này cho các run có trước chỉ vì kỹ thuật tương tự.

- [DQI-10 DESCRIPTION](../../../../src/dqi/DQI-10/DESCRIPTION.md) và [run dev](../../../../results/dqi/DQI-10/merged/dev_5min/20261108T052816Z-local-dev_5min-619295/verifier.json): shared-unary-ancilla/EEA đã PASS 4096 shots nhưng Q giảm 1893->1889, T tăng khoảng 1.102%, score tăng khoảng 0.6752% (gain 0.99329323). Đây là kết quả âm cho bản kết hợp đó, không bác bỏ BM hay mọi cách chia sẻ kernel; chưa full/seed độc lập.
- [INV-6 DESCRIPTION](../../../../src/invsqrt/INV-6/DESCRIPTION.md) và [delta12 dev](../../../../results/invsqrt/INV-6/delta12/dev_5min/20261108T021502Z-local-dev_5min-b9ca90/verifier.json): project đã khảo sát precision/bias theo integer model, có dev PASS và kiểm tra mô hình; chưa full/seed chấm độc lập cho ứng viên cuối. Không coi đây là tái lập bảng 128 lines của paper hoặc bằng chứng có thể bỏ Newton.
- Còn mở: lịch cutoff/pseudocode gate-level BM, xử lý deg sigma=0 trong reciprocal, runtime-mask phase cost, và cấu trúc repetition thật của delta angle. Nguồn hiện tại chưa đủ để khẳng định số gate dự kiến của bản tích hợp.

## Tài liệu liên quan

- [Nguồn arXiv đúng phiên bản](https://arxiv.org/abs/2610.22367v1); toàn bộ số liệu paper trong note lấy từ PDF local, không xác minh trạng thái web/phiên bản mới.
- [Note Optimized DQI Circuits](../../../dqi/papers/arxiv-2510.10967/note.md), nguồn baseline [13] trong paper; không đọc lại nguồn đó trong lượt này.
- [Note spectral amplification/DFTHC](../../../dfthcsos/papers/doi-10.1103--pb2g-j9cw/note.md) để định vị khác biệt với sparse Pauli benchmark; chưa đọc lại trong lượt này.
- Metadata PDF ghi license CC BY-NC-SA 4.0. Chưa tải/kế thừa code tác giả và chưa xác minh license code; note diễn giải kết quả kèm citation, không khẳng định PDF license áp dụng cho mọi repository bên ngoài.


## Tự rà bước 03 và bàn giao review độc lập

Tác giả tự rà trên draft đầu vào `e04341630595f40fe30afa2d2f2bade8cf1e57dc`, ngày 2026-11-08; đây không phải kết luận reviewer độc lập.

| Finding tự rà | Căn cứ | Xử lý |
| --- | --- | --- |
| Chưa tách tỷ lệ trajectory sai và trọng số input lỗi DQI | Methods Eqs.18-21 PDF p.10; SI I Eq.25 PDF p.19 | Đã tách epsilon_traj/epsilon_input, p_det và hệ số phát hiện 1/2; thêm Eq.25 cùng giới hạn chưa kiểm chứng nguồn [16]. |
| Công thức ghi đè syndrome thiếu miền i và lịch tránh dùng nguồn đã bị ghi đè | SI I.1 Eqs.35-36 PDF p.22 | Đã thêm miền 0<=i<35, mở rộng <70, zero-extension sigma và lịch giảm/tăng i; ghi rõ lịch là suy luận từ map tam giác. |
| Alias-Select thiếu điều kiện để pha là dấu thực và công thức pha đầy đủ | SI IV Eqs.73-75 PDF pp.37-38 | Đã thêm điều kiện Y chẵn, định nghĩa a/z/theta/eta, map x và phi tính trên x ban đầu. |
| Ký hiệu T_synthesis có thể khiến bỏ sót góc T chính xác trong điểm invsqrt | Docstring verifier tại snapshot đọc | Đã đổi thành T_Z_POW và nêu đủ thành phần; không đổi công thức chấm. |
| Phân loại shared chưa khớp mục đích DQI người dùng xác nhận | Chỉ dẫn người dùng trong bước 03 | Đã chuyển nguyên PDF/note/source.json sang research/dqi/papers/arxiv-2610.22367, đổi Track và mục lục; hash PDF giữ nguyên. |
| Coverage/trạng thái còn ghi chưa tự rà bước 03 | Metadata note/source.json | Đã đồng bộ, giữ draft, thêm các trang kiểm tra trực quan và hash Git blob cho file project đối chiếu bổ sung. |

Đã đối chiếu bảng tài nguyên, số test, BM/routing/invariant, reciprocal identity, numerical domains/error bounds, alias ordering/pruning và mô hình điểm với nguồn trong coverage. PDF và snapshot blob đã kiểm hash; các số DQI-10 đã đối chiếu [review.json lịch sử](../../../../results/dqi/DQI-10/merged/dev_5min/20261108T052816Z-local-dev_5min-619295/review.json), INV-6 đối chiếu [model_validation.json](../../../../results/invsqrt/INV-6/delta12/build_only/20261108T020740Z-local-build/model_validation.json). Không sửa hay chạy lại run.

Giới hạn còn mở cho reviewer: cutoff BM/gate schedule chưa đủ để tái lập; locator hằng cần xử lý biên; mask runtime khác fixed-mask benchmark; chưa kiểm chứng [16]/Appendix A, code tác giả hay full verification. Các mục này đã được khai là giới hạn, chưa coi là kết quả đã xác nhận. Phiên độc lập bước 04 cần đọc trực tiếp PDF, note và source.json tại SHA cuối PR; chưa có SHA review độc lập và chưa đủ căn cứ đặt ready/merge.
