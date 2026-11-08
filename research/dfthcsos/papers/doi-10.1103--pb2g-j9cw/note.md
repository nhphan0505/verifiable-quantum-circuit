# Fast Quantum Simulation of Electronic Structure by Spectral Amplification — DFTHC-SOS, λ_eff và chi phí tải góc Givens

Status: ready
Track: dfthcsos
Source: doi:10.1103/pb2g-j9cw; paper.pdf; metadata và SHA-256 trong source.json
Version: Phys. Rev. X 15, 041016 (2025), xuất bản 2025-10-31, bản PDF APS 41 trang; truy cập 2026-11-08

- Paper: Guang Hao Low, Robbie King, Dominic W. Berry, Qiushi Han, A. Eugene DePrince III, Alec F. White, Ryan Babbush, Rolando D. Somma, Nicholas C. Rubin, *Fast Quantum Simulation of Electronic Structure by Spectral Amplification*, Phys. Rev. X 15, 041016 (2025), doi:10.1103/pb2g-j9cw. Giấy phép CC BY 4.0 (tr. 1). PDF không ghi mã arXiv của chính bài; không tra nguồn ngoài.
- Track: `dfthcsos`. Căn cứ: verifier chấm đúng đại lượng của paper này (`lambda_eff = sqrt(E_gap (2Λ − E_gap))`, factorization (R, B, C), bảng góc `N + R·B` địa chỉ, mô hình `SpinFreeData_V1`; xem [SCORING_README](../../../../verifiers/dfthcsos/SCORING_README.md)). Độ chắc chắn: cao.
- Từ khóa: spectral amplification (SA), sum-of-squares (SOS), DFTHC, double factorization (DF), tensor hypercontraction (THC), BLISS, qubitization, coherent alias sampling, QROM/QROAM, Givens rotation, b_rot, randomized rounding, FeMoco-76.
- Bản đã đọc: [paper.pdf](paper.pdf) (41 trang, giữ nguyên bytes). Trang ghi theo số trang PDF; trang tạp chí là 041016-<trang>.
- Đọc kỹ: I–VI (tr. 1–16); Appendix B "DFTHC block-encoding cost" (tr. 20–27, gồm Tables VII–IX); Appendix D "Truncation to finite bits" (tr. 33–36); Table X phần FeMoco-76 (tr. 30); Table XI (tr. 33); đoạn đầu Appendix E (tr. 36). Đối chiếu trực quan ảnh trang 3 (Table I), 10 (Fig. 2, Table III), 14 (Table V), 30 (Table X), 36 (randomized rounding, Eq. D3–D4).
- Chưa đọc / chỉ lướt: Appendix A (quantum walk trên căn Hermitian/rectangular, tr. 17–20, chỉ đọc đoạn cuối tr. 20 về W₂W₁); Appendix C (robust selection, tr. 28–33, chỉ đọc Table X/XI); Fig. 7 (tr. 34–35, chỉ chú thích); phần còn lại của E; Appendix F (spin-free formalism, tr. 37, chỉ lướt tiêu đề/Table XII); Appendix G (tr. 38); references (chỉ tra [37], [38]). Không xác minh lại chứng minh, không chạy code tác giả, không truy cập nguồn dẫn.

## Vấn đề và kết quả của paper

Bài toán: ước lượng năng lượng ground state $E_{gs}$ của Hamiltonian cấu trúc điện tử spin-free (Eq. 2, tr. 3)
$H=\sum_{pq}h^{(1)}_{pq}E_{pq}+\tfrac12\sum_{pqrs}h^{(2)}_{pqrs}E_{pq}E_{rs}$, $E_{pq}=\sum_\sigma a^\dagger_{p\sigma}a_{q\sigma}$,
bằng phase estimation (PEA) trên quantum walk với chi phí tỉ lệ với hệ số chuẩn hóa block encoding.

Ba kết quả (I, tr. 2–3):

1. **Mạch SA thực tế** cho Hamiltonian dạng SOS $H=\sum_\alpha O_\alpha^\dagger O_\alpha+E_{SOS}$ (Eq. 1, 5): block encoding hình chữ nhật của $H_{sqrt}=\sum_\alpha|\chi_\alpha\rangle\otimes O_\alpha$, rẻ hơn dilation Hermitian ít nhất 2 lần (II, tr. 5; App. A).
2. **SOS cho hóa học**: tìm $E_{SOS}$ tối ưu bằng SDP trên đại số spin-free cấp 2 (Eq. 14, 22) trong thời gian đa thức; Table II (tr. 8) cho FeMoco [113e, 76o]: DMRG M=6000 cận trên −1119.05933 Ha, cận dưới SDP −1123.300 Ha, $E_{gap}$ 4.240 Ha, cận dưới $\lambda_{eff}$ 21.691 Ha.
3. **Factorization DFTHC** (IV, tr. 8–9) nằm giữa DF và THC, tối ưu bằng gradient descent; kết hợp BLISS + SA. Cho FeMoco-76: $(R,B,C)=(15,57,19)$, $\Lambda=179.7296$ Ha, $E_{gap}=5.3820$ Ha, $\lambda_{eff}=43.6538$ Ha, Cost[BE] = 14629 Toffoli, 1454 qubit, tổng 1.00×10⁹ Toffoli; cải thiện 4.3× so với THC+BLISS [8] và 36.9× so với DF (Table V, tr. 14; Table I, tr. 3).

Mọi con số là **ước lượng tài nguyên của tác giả** (đếm Toffoli logic, $\sigma_{PEA}=1$ mHa, giả định overlap trial state p = 1, tr. 4). Không có thí nghiệm phần cứng. Ước lượng vật lý: FeMoco-76 cần 4.5×10⁶ physical qubit trong 8.6 h (4 CCZ factory, error 10⁻³, d = 27; tr. 15), theo mô hình của ref. [7] mà tác giả tự nhận là đã lỗi thời trước magic state cultivation (VI, tr. 16).

Lưu ý tên hệ: FeMoco-54 [37] là Reiher et al. 2017 ([note](../doi-10.1073--pnas.1619152114/note.md)); FeMoco-76 [38] là Li et al., J. Chem. Phys. 150, 024302 (2019). Hệ chấm của project là FeMoCo76o113e (76 orbital, 113 electron).

## Thuật toán và công thức cần dùng

### Spectral amplification và λ_eff (II, tr. 4–6)

- PREP/SEL (Eq. 7): $\lambda_{sqrt}=\sqrt{\sum_\alpha\lambda_\alpha^2}$ với $\lambda_\alpha\ge\|O_\alpha\|$; $\mathrm{SEL}\cdot\mathrm{PREP}$ là block encoding của $H_{sqrt}/\lambda_{sqrt}$ (Eq. 8).
- Hai bước walk: $W=W_2W_1$ có pha $2\arccos(\sqrt{E_j}/\lambda_{sqrt})=\arccos(2E_j/\lambda_{sqrt}^2-1)$ (Eq. 9), tương đương walk của $2H_{SA}/\lambda_{sqrt}^2-I$. Block encoding (Eq. 10): $\mathrm{PREP}^\dagger\mathrm{SEL}^\dagger\mathrm{REF}\,\mathrm{SEL}\,\mathrm{PREP}$, với $\Lambda\equiv\lambda_{sqrt}^2/2$. Mỗi $O_\alpha$ được dùng qua $T_2$ (đa thức Chebyshev bậc 2, Fig. 1).
- Số truy vấn PEA (Eq. 11): $\pi\lambda_{eff}/(2\sigma_{E_{gap}})$, $\lambda_{eff}=\sqrt{E_{gap}(2\Lambda-E_{gap})}$, với $E_{gap}=E_{gs}-E_{SOS}$. **Đây chính là công thức `lambda_eff` của verifier.** Khi $E_{gap}\ll\Lambda$: $\lambda_{eff}\approx\sqrt{2\Lambda E_{gap}}$, nên giảm $\Lambda$ hay $E_{gap}$ chỉ giảm $\lambda_{eff}$ theo căn bậc hai.

### DFTHC (IV, tr. 8–9, Eq. 23–33)

- Biểu diễn (Eq. 23–24): tham số $(R,B,C)$; vector đơn vị $\vec u^{(r)}_b\in\mathbb R^N$ (r ∈ [R], b ∈ [B]), trọng số $w^{(rc)}_b$, thành phần đơn vị $W^{(rc)}$, với $w^{(rc)}_B=W^{(rc)}+\sum_{b<B}w^{(rc)}_b$. $h^{(2)\prime}_{pqmn}=\sum_{r,c}(\sum_b w^{(rc)}_b u^{(r)}_{b,p}u^{(r)}_{b,q})(\sum_{b'}w^{(rc)}_{b'}u^{(r)}_{b',m}u^{(r)}_{b',n})$.
  - DF là trường hợp $B=N$, $w_B=0$, $C\in\{1,2,N\}$, vector trực giao trong mỗi rank; THC factorized là $(1,R_{THC},R_{THC})$ (tr. 8–9).
- Toán tử Majorana $\gamma_{\vec u\sigma x}=\sum_j u_j\gamma_{j\sigma x}$ (Eq. 25). Bộ sinh SOS: $O_{D\sigma_1,r}$, $O_{Q\sigma_1,r}$ từ phân rã trị riêng dương/âm của $h^{(1)\prime}$ (Eq. 26–28), và $O_{SF,rc}=\frac1{\sqrt2}(w_B^{(rc)}+\frac i2\sum_b\sum_\sigma w^{(rc)}_b\gamma_{\vec u_b\sigma0}\gamma_{\vec u_b\sigma1})$ (Eq. 29).
- $E_{SOS}=-2\sum_r w^{(r)}_- -\frac12\sum_{rc}|W^{(rc)}|^2$ (Eq. 30).
- **Chuẩn hóa** (Eq. 33): $\Lambda=\|h^{(1)\prime}\|_1+\frac14\sum_{r,c}\big(\sum_{b\in[B+1]}|w^{(rc)}_b|\big)^2$ ($\|\cdot\|_1$ là chuẩn Schatten-1).
- Một-hạt được chọn tự do để khớp chính xác Hamiltonian (Eq. 34–36); $E_{gap}$ theo Eq. 39.
- BLISS (Eq. 40): thay $(h^{(2)},h^{(1)},h^{(0)})$ bằng họ tương đương phổ trong sector η hạt, tham số $\beta_1$ và $h^{(sym)}$. Verifier cố định $S,\beta_1$ của baseline (SCORING_README: `FeMoCo76o113e.fixed_shifts.npz`).
- Hàm mục tiêu tối ưu (Eq. 41): $\|h^{(2)}_S-h^{(2)\prime}\|_{fro}/\epsilon_{reg}+\Lambda/\lambda_{reg}+\mathrm{Relu}((E_{gap}-E_{reg})/E_{reg})$, Adam (Optax/Jax), khởi tạo ngẫu nhiên; mỗi bước $O(RCN^4)$ phép nhân (tr. 12). Table IV: (76, 15, 57, 19) với $\lambda_{reg}$ = 100 Ha, $\epsilon_{reg}$ = 10 mHa, $E_{reg}$ ∈ [4, 8] Ha, 4.4 ms/bước trên Nvidia L4, 10⁵–10⁶ bước.

### Block encoding và chi phí (IV tr. 9–11; App. B tr. 20–27)

Ba thành phần chiếm ~90% Toffoli, trong đó Sel chiếm ~60% (tr. 11):

1. **Rot** — table lookup theo $N+RB$ chỉ số, xuất $(N-1)$ góc, mỗi góc $b_{rot}$ bit, quay $\gamma_{0\sigma x}$ thành $\gamma_{\vec u\sigma x}$ (tr. 9). App. B mục 5 (tr. 26–27): unary iteration với chi phí $N+RB$ (Eq. B41–B42: N cho D₁/Q₁, $B(R-1)+(B-1)=RB$ cho SF; vector chỉ chọn theo $(r,b)$, **không theo c**). Xóa bằng phase fixup với chi phí $R+B$ (Eq. B47, tr. 27). Eq. B47 mô tả xóa "the second QROM from Item 5", tức lookup SF trên $(r,b)$. Phần N địa chỉ D₁/Q₁ được xuất trong unary iteration của state preparation và được phase fixup ở bước 8 (Eq. B50–B51). Table IX gộp QROM† thành $R+B$. Persistent ancilla $(N-1)b_{rot}$ (Eq. B43). Table IX: mỗi thứ 2 lần gọi/walk.
2. **Qroam** cho hệ số alias sampling: theo $N+R(B+1)C$ chỉ số, xuất $b_Q=\lceil\log_2B\rceil+b_{coeff}$ bit; chi phí ≈ $RBC/(\lambda+1)+\lambda b_Q$ với $\lambda\le(N-1)b_{rot}/b_Q$, tận dụng qubit rảnh sẽ chứa output của Rot sau này (tr. 11).
3. **Sel**: Givens rotation điều khiển bởi góc, $U_{Rot}$ tốn $2(N-1)b_{rot}$ Toffoli (Eq. B20–B21, B46: forward + reverse), cộng 4 CSWAP spin $4(N+1)$ và Majorana 7 Toffoli. Table X dùng $8(N-1)b_{rot}$ cho hai select unitary (tr. 29–30).

Cấu trúc khác: $U(\vec u)$ gồm $N-1$ phép quay một qubit góc $\theta_j$ cùng $O(N)$ cổng Clifford hai qubit, với $U^\dagger\gamma_{00x}U=\tilde\gamma_{\vec u0x}$. Nghiệm $\vec\theta=f^{-1}(\vec u)$ không duy nhất, chọn tùy ý (tr. 23). Dấu của $w_b$ được xử lý bằng 1 qubit dấu trong alias sampling và gộp vào sửa pha khi xóa QROM bằng đo X (Eq. B16–B19, tr. 22–23). Trạng thái σ được xóa bằng đo X và fixup Clifford, không tốn Toffoli (tr. 22).

Ví dụ đối chiếu ảnh: Table III (tr. 10), FeMoco-54, $(10,27,27)$, $b_{rot}=15$:

- RPrep: QROM($\vec u$) có $N+RB=324$, QROM† có $R+B=37$; persistent $(N-1)b_{rot}=795$.
- Sel: Rot $4b_{rot}(N-1)=3180$.
- Tổng 9997 Toffoli, 1021 qubit (Table V ghi Cost[BE] 10203 và 1132 qubit cho cùng hệ; paper không giải thích chênh lệch trong phần đã đọc. Chú thích Table III nói tổng 1131 qubit do dùng lại 313 qubit tạm).

Table X (tr. 30), FeMoco-76o113e, $(b_{coeff},b_{rot})=(9,15)$. Các cột C = ⌊N/4⌋ với $(M,\lfloor3N/4\rfloor,\cdot)$ có M = 15: Rot 3420, Coeff 2476, Select 9000 (= 8·75·15), tổng 14896; $\lambda$ = 179.7 Ha, $E_{gap}$ = 5.037 Ha, $\lambda_{eff}$ = 42.25 Ha. DF-like (130, 76, 1): Rot 39520, tổng 50490. THC-like (1, 220, 220): Rot 880, Coeff 4484, tổng 14364. Note không kiểm chứng cách tác giả tính cột Rot (chú thích: "computing and uncomputing twice").

### Số bit và randomized rounding (IV tr. 11; App. D tr. 33–36)

- Chemical precision đạt với $b_{rot}\in[11,18]$, $b_{coeff}\in[6,14]$ tùy hệ (tr. 11).
- Góc $\theta\in[0,2\pi)$: lấy $b_{rot}-1$ bit đầu $x=\lfloor 2^{b_{rot}-1}\theta/(2\pi)\rfloor$; bit cuối lấy mẫu Bernoulli với $p=2^{b_{rot}-1}\theta/(2\pi)\bmod1$; $\theta^{(b_{rot})}=2\pi(x+\mathbb B(p))/2^{b_{rot}-1}$ (tr. 36, đã đối chiếu ảnh). Mỗi vector lệch tối đa $O(N2^{-b_{rot}})$ nhưng kỳ vọng lệch $O(N4^{-b_{rot}})$, tức "hiệu dụng gấp đôi số bit". Paper làm tròn **một lần** cho mỗi lời giải, không làm tròn lại mỗi lần gọi block encoding (tr. 36).
- Hệ số: alias sampling chia thành $M=(B+1)2^{b_{coeff}-1}$ bin (1 bit dấu); gán $\lfloor M|w_b|/|w|_1\rfloor$ bin rồi lấy mẫu phần dư (tr. 36).
- $\sigma_{trunc}$ giảm theo $O(2^{-b_{rot}},2^{-b_{coeff}})$, $|\bar\epsilon_{trunc}|$ hội tụ về 0 (Fig. 6, tr. 33). FeMoco-54: ngân sách 0.830 mHa đạt với $(b_{coeff},b_{rot})=(9,15)$, ngân sách 0.331 mHa đạt với (10, 17) (tr. 33).
- Một-hạt: sai số do $b_{rot}$ hữu hạn có thể bù bằng tổ hợp tuyến tính $H_1'^{(b_{rot})}$ và phần dư, chỉ tốn thêm N địa chỉ (Eq. D3–D4, tr. 36).

## Điều kiện đúng, sai số và tài nguyên

- Tiêu chí chính xác: $\sigma_E\le\sigma_{PEA}+|\epsilon_{corr}|\le\epsilon_{chem}=1.6$ mHa (Eq. 3), $\sigma_{PEA}=1.0$ mHa, $|\epsilon_{corr}|\le0.3$ mHa theo CCSD(T) high-spin (IV.B, tr. 13; FeMoco-76 dùng $n_\uparrow-n_\downarrow=35$). Biến thể thống kê (Eq. 4, 44, 45, D1–D2) cho phép $\sigma_{PEA}=1.4$ mHa (Table XI). Ở bản này FeMoco-76 dùng (15, 64, 32), (11, 16) bit, 1560 qubit, vẫn 1.00×10⁹ Toffoli.
- Tác giả tự cảnh báo (V, tr. 15–16; Table VI): sai số tương quan CCSD(T) high-spin có thể khác hàng bậc độ lớn so với DMRG low-spin; ngưỡng truncation thấp có thể biểu diễn "physics khác". Đây là giới hạn mở, chưa có metric thay thế.
- $E_{gap}$ từ SDP là cận dưới cho Fock space, còn năng lượng biến phân là cho sector hạt cố định (Table II). $E_{gap}$ trong Table V được tính lại bằng CCSD(T), không phải cận trên chặt (tr. 13).
- Mô hình chi phí paper: Toffoli logic của **một walk** (Cost[BE]) × số lần gọi $\lceil\pi\lambda_{eff}/(2\sigma_{PEA})\rceil$ (Eq. 11, tr. 6; chú thích Table V tr. 14 và Table XI tr. 33). Hàng DF/THC trong Table V dùng λ của phương pháp tương ứng. Với SA phải dùng $\lambda_{eff}$, không dùng $\Lambda$ thô: ở FeMoco-76, $\Lambda$ = 179.7296 Ha còn $\lambda_{eff}$ = 43.6538 Ha, nên dùng nhầm $\Lambda$ sẽ phóng đại số lần gọi khoảng 4.12 lần; qubit logic gồm persistent + max temporary + hệ thống $2N$. Không giới hạn số qubit cho từng lookup.
- **Khác biệt với verifier project** (đối chiếu README/code verifier, không phải kết quả paper):
  - Điểm $=\lambda_{eff}\times T_{total}\times Q_{total}$, không nhân số lần gọi PEA hay $\sigma_{PEA}$.
  - Góc: hai quy ước **không cùng độ phân giải** với cùng giá trị $b_{rot}$.
    - Verifier (SCORING_README, mục Submission files; `dfthc_math.py` nhân word đã chuẩn hóa với π) giải mã $\theta=\pi w/2^{b_{rot}-1}$ với word $b_{rot}$ bit. Bước lưới là $\pi/2^{b_{rot}-1}=2\pi/2^{b_{rot}}$, phủ [0, 2π).
    - Paper (App. D, tr. 36) cho góc làm tròn $2\pi(x+\mathbb B(p))/2^{b_{rot}-1}$. Bước lưới là $2\pi/2^{b_{rot}-1}$, thô hơn verifier hệ số 2, tức lệch một bit.
    - Ví dụ $b_{rot}=12$: paper có bước $2\pi/2048$, verifier có bước $2\pi/4096$.
    - Vì vậy không chuyển trực tiếp $b_{rot}$ của paper (ví dụ 15 cho FeMoco-76) sang word của verifier. Note chưa xác minh ánh xạ bit/góc: cách paper đếm bit Bernoulli cuối và overflow khi $x+\mathbb B(p)=2^{b_{rot}-1}$ chưa được kiểm chứng. Chỉ coi hai quy ước tương đương sau khi đã kiểm chứng ánh xạ này.
  - Givens: verifier tính $2(N-1)(2b_{rot}-1)$ (adder $2\beta-1$ mỗi lượt, `costs_prepare.py::givens_rotations`), còn paper dùng $2(N-1)b_{rot}$ cho mỗi $U_{Rot}$ (Eq. B46).
  - Tải góc: paper xuất **toàn bộ** $(N-1)b_{rot}$ bit một lần (FeMoco-76, b_rot = 15: 1125 qubit persistent). Verifier giới hạn mỗi ANGLE_k ≤ 128 qubit, nên baseline chia thành batch J word (J = 8, 12 bit, 10 mạch) và cộng $J\cdot b_{rot}$ vào $Q_{total}$.
  - Verifier từ chối nếu error_1 hoặc error_2 > 20 mHa, $\Lambda\le49.0$, hoặc $E_{gap}\le3.914898$ Ha. Đây là tiêu chí Frobenius/tái dựng của cuộc thi, không phải $\epsilon_{corr}$ CCSD(T) của paper.

## Khả năng áp dụng vào project

Snapshot đối chiếu: commit `cd4f4ac58360aad26e634a29c13cc6046298dbd5`. SHA-256 blob:

- [src/dfthcsos/DFT-BASELINE/solution.py](../../../../src/dfthcsos/DFT-BASELINE/solution.py) `5c4599510c1bf0a1a26873e08edb05127534b91fb079e0ac7eae904d9ad7327b`
- [src/dfthcsos/DFT-BASELINE/DESCRIPTION.md](../../../../src/dfthcsos/DFT-BASELINE/DESCRIPTION.md) `972713ec13b0a76b1306d216b156d3e7ef75ed41663dca66e89a53c0d41fc253`
- [verifiers/dfthcsos/verify.py](../../../../verifiers/dfthcsos/verify.py) `0775be7a528922367caebe9e4d051d6199811f1aefeaa4b793eaaa4621b8ec9d`
- [verifiers/dfthcsos/SCORING_README.md](../../../../verifiers/dfthcsos/SCORING_README.md) `c2228569f96e58e118419bc32be2be9e33d6abffb8117cb0b91e1fc25b2a0230`
- [verifiers/dfthcsos/scoreinfra/costs_prepare.py](../../../../verifiers/dfthcsos/scoreinfra/costs_prepare.py) `7f1e190c42fc5325f3e6689fbbef51f95b0cb12f1c828cda92b6c088e72206da`
- [verifiers/dfthcsos/scoreinfra/dfthc_math.py](../../../../verifiers/dfthcsos/scoreinfra/dfthc_math.py) `ae82898d47a7a86b96378fb906e0f8a9f46003065cf19c7c09952a123b5b5af8`

Ánh xạ (suy luận của nhóm từ đối chiếu, chưa đo):

- Mạch ANGLE_k của project tương ứng với **RPrep/QROM($\vec u$)** của paper: bảng $N+RB$ địa chỉ (76 + 65·60 = 3976 ở baseline), mỗi địa chỉ $N-1=75$ góc. Paper cost lookup này $N+RB$ Toffoli cho một lần tính (unary iteration). Phần xóa $R+B$ chỉ áp cho lookup SF trên $(r,b)$; N địa chỉ D₁/Q₁ được xuất và xóa ghép với state preparation (Eq. B50–B51). Vì vậy $R+B$ không phải chi phí xóa trọn vẹn cho toàn bảng $N+RB$ của một mạch ANGLE_k độc lập. Baseline lặp QROM trên toàn 3976 địa chỉ cho mỗi batch delta, cả thuận lẫn ngược (DESCRIPTION).
- Chỉ số $(r,b)$ có cấu trúc tích: paper lặp b ngoài, r trong, với chi phí $B(R-1)+(B-1)$ (Eq. B42). Baseline dùng địa chỉ phẳng `76 + R·B` theo thứ tự `(rho, b)` (SCORING_README).
- Phần state prep và Givens được verifier tính bằng heuristic cố định theo $(N,R,B,C,b_{rot})$; chỉ ANGLES được đếm thực từ mạch. Vì vậy $b_{rot}$, $J$, $(R,B,C)$ và chất lượng factorization (qua $\Lambda$, $E_{gap}$) ảnh hưởng đồng thời cả ba thừa số.
- Không có code của tác giả trong PDF; không kế thừa code.

## Hypothesis gợi ý và cách kiểm chứng

Các mục dưới là **suy luận của nhóm**, chưa thử, cần Issue riêng theo luồng experiment:

1. **Xóa bảng góc bằng phase fixup thay vì chạy lại QROM.** Paper xóa output lookup SF trên $(r,b)$ với chi phí $R+B$ (Eq. B47); N địa chỉ một hạt được xóa ghép với phase fixup của state preparation (Eq. B50–B51), nên chưa có căn cứ coi $R+B$ là chi phí thay thế trọn vẹn cho bảng $N+RB$. Khi áp dụng sang ANGLE_k độc lập phải hạch toán thêm phần một hạt (76 địa chỉ đầu), việc chuyển địa chỉ phẳng `76 + R·B` sang cặp $(r,b)$, và workspace của binary-to-unary (tạm thời $\min(R,B)$, tr. 27) trong giới hạn 128 qubit. Ở project, lượt ngược hiện chạy lại các oracle XOR. Cần kiểm tra verifier có chấp nhận đo X + sửa pha có điều kiện trong lượt ngược hay không (README nói gate điều kiện theo bit đo chỉ tính trên shot bit = 1) và mạch có còn tải đúng góc. Đối chứng: Toffoli ANGLES của baseline; bác bỏ nếu verifier từ chối hoặc không giảm T_total.
2. **Unary iteration theo cấu trúc (b, r)** thay cho iteration trên địa chỉ phẳng, theo Eq. B42. Kiểm chứng bằng đếm Toffoli ANGLE_k ở cùng bảng delta.
3. **Chọn b_rot / J và làm tròn ngẫu nhiên không thiên lệch** (App. D) để giảm b_rot. Lưu ý quy ước góc của paper và verifier lệch một bit (mục "Điều kiện đúng"), nên phải tính lại số bit theo $\theta=\pi w/2^{b_{rot}-1}$ của verifier, mà vẫn giữ error_1/error_2 < 20 mHa và $\Lambda$, $E_{gap}$ hợp lệ. Lưu ý paper đo bằng $\epsilon_{corr}$ CCSD(T), không phải metric verifier; phải đo lại bằng verifier. Rủi ro: $E_{gap}$ hoặc $\Lambda$ chạm ngưỡng sàn strict.
4. **Tối ưu lại (R, B, C)** theo heuristic tr. 11 (C = Θ(N), B = Θ(N), R = Θ̃(1); paper dùng (15, 57, 19) cho FeMoco-76 so với (65, 60, 60) baseline). R nhỏ hơn giảm số địa chỉ $N+RB$ và giảm ANGLES. Cần huấn luyện lại factorization và chịu thay đổi $\Lambda$, $E_{gap}$. Kiểm tra cả hai ngưỡng sàn của verifier; đây có thể là ràng buộc chặn, chưa biết.

## Bằng chứng trong project và câu hỏi còn mở

- Chưa có Issue/run dùng nguồn này. SCORES.md chỉ có DEV_5MIN của DFT-BASELINE (3355599588.3155365); chưa có FULL.
- Câu hỏi mở:
  - Ánh xạ bit/góc giữa paper (bước $2\pi/2^{b_{rot}-1}$) và verifier (bước $2\pi/2^{b_{rot}}$): cách paper đếm bit Bernoulli cuối và xử lý overflow chưa được kiểm chứng.
  - Vì sao Table III (9997) và Table V (10203) khác nhau?
  - Cột Rot Toffolis của Table X được tính thế nào?
  - Chi tiết App. A, C, F, G chưa đọc.
- Paper nêu mở: tối ưu không gian–thời gian thay vì chỉ Toffoli; chuyển sang SDP low-rank; mở rộng đại số SOS; metric truncation tốt hơn CCSD(T) high-spin (V–VI, tr. 15–16).

## Tài liệu liên quan

- [Note Reiher et al. 2017](../doi-10.1073--pnas.1619152114/note.md) (FeMoco-54 [37]).
- Li et al. 2019, J. Chem. Phys. 150, 024302 ([38], FeMoco-76): chưa có trong repo, chưa đọc.
- [DFT-BASELINE](../../../../src/dfthcsos/DFT-BASELINE/DESCRIPTION.md); [SCORING_README](../../../../verifiers/dfthcsos/SCORING_README.md).
- Paper CC BY 4.0; note không sao chép code.
