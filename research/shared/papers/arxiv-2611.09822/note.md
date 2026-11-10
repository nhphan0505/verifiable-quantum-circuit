# Discovering formally verified quantum programs with AI

Status: draft
Track: shared
Source: https://arxiv.org/pdf/2611.09822v1
Version: arXiv:2611.09822v1, truy cập ngày 2026-11-10

- **Paper** — Sergey Shirobokov, Ben Jaderberg, Katerina Hristova và cộng sự (2026). Định danh bản lưu là arXiv:2611.09822v1.
- **Từ khóa** — Lean, đặc tả đóng băng, fixed-point, uncompute, Givens, DFTHC SOS, tra bảng one-hot.
- **Bản đọc** — [PDF v1](paper.pdf) và [metadata kèm SHA-256](source.json). Số trang bên dưới theo PDF.

## Vấn đề và kết quả của paper

Các tác giả dùng agent để đề xuất chương trình lượng tử và chứng minh tính đúng cùng chi phí trong Lean. Logic Hoare cổ điển–lượng tử mô hình hóa cả phép đo giữa mạch, rẽ nhánh và reset. Với chương trình `P` và hậu điều kiện `Ψ`, bộ biến đổi weakest precondition đi ngược các lệnh để xây dựng tiền điều kiện đủ. App. A (tr. 19–20) phân biệt đếm cổng trên mạch động theo nhánh đắt nhất với chi phí kỳ vọng của chương trình tổng quát, trong đó mỗi nhánh được tính theo xác suất đi vào nhánh.

Lean Comparator kiểm tra lại submission trong sandbox sạch dựa trên đặc tả ghim theo commit. Nó đối chiếu định lý đích và các định nghĩa phụ thuộc theo đặc tả, giới hạn tiên đề ở `propext`, `Quot.sound` và `Classical.choice`, loại `sorry` khỏi bằng chứng đã biên dịch và đối chiếu chi phí đã chứng minh với giá trị khai báo. Wiki dùng lại nghiệm đã qua kiểm tra và ghi cả hướng thất bại. Bảo đảm hình thức phụ thuộc vào mô hình và đặc tả đã chọn (§1.1–1.2, tr. 3–4 và App. B, tr. 20).

Hình 3 (tr. 5) dùng tích số qubit logic `Q` và số cổng `T` làm chi phí cho các bài dưới đây. Đây là số do paper báo trong mô hình logic.

| Bài trong paper | Mốc so sánh | Kết quả tác giả báo |
| --- | --- | --- |
| Fixed-point arcsin (App. F, tr. 29–32) | Cận dưới `245 × 440.576 ≈ 1,08 × 10^8` của baseline, với sai số baseline khoảng `10^-6` | Kickmix `100 × 4.152 = 415.200`. Clifford+T `100 × 3.698 = 369.800`, khoảng 290 lần so với cận dưới baseline. |
| Stopping power (App. G, tr. 32–35) | `5,42 × 10^15` mỗi lần chạy, trung bình theo thời điểm | `4,98 × 10^14` mỗi lần chạy, giảm 10,9 lần. |
| P450 Compound I (App. I, tr. 37–41) | Baseline tinh chỉnh `481 × 2,26 × 10^9 ≈ 1,09 × 10^12` | `333 × 1.310.839.337 = 436.509.499.221`, giảm 2,49 lần. |

## Thuật toán và công thức cần dùng

### Arcsin fixed-point (§2.2 và App. F, tr. 6, 29–32)

Mạch cộng một giá trị xấp xỉ `z`y`` vào thanh ghi đích `b` modulo `2^25`, giữ `y` và dọn ancilla. Dùng số bù hai 25 bit, với 23 bit lẻ. Ràng buộc xấp xỉ là `|z`y` − arcsin`y`| ≤ 1,25 × 10^-7` radian cho mọi điểm lưới `y` từ −1 đến 1. Phép cộng thuận nghịch phải thực hiện đúng trên thanh ghi đích bất kỳ (App. F.1).

1. Dùng tính lẻ để xử lý độ lớn `u = |y|`. Cộng riêng phần tuyến tính `u` rồi xấp xỉ phần dư `arcsin`u` − u` bằng đa thức bậc hai trên 440 khoảng. Khoảng hẹp dần về 1 và điểm `u = 1` đi nhánh riêng.
2. Đếm số bit 0 đầu của `1 − u`, dịch có điều khiển và xác định chỉ số khoảng `s` (9 bit) cùng độ lệch nội bộ `t`. Tra hệ số `A, B, C`, rồi cộng `A + Bt + Ct²` vào đích. Hoàn nguyên dịch và biến đổi dấu khi kết thúc.
3. Cộng 19 bit cao của `A` rồi dọn chúng để tái sử dụng chỗ cho các bit hệ số sau. Dọn `C` và `t²` giữa chừng để dành chỗ cho phần còn lại của `Bt`. Bản kickmix tính mỗi bit hệ số như XOR các tích bit của `s`, chia sẻ tích xuất hiện ở nhiều bit. Bản Clifford+T thay nhiều khối bằng gadget tích vô hướng nhị phân gồm `r` cặp, tốn `2r + 2` cổng `T/T†` mỗi khối với `2 ≤ r ≤ 7`, rồi triệt dấu phụ thuộc đầu vào bằng `Z/CZ` (Hình S10, Bảng S2).

### Stopping power (§2.3 và App. G, tr. 7, 32–35)

Đặc tả cần mô phỏng `exp(−iHt)` với sai số chuẩn vector tối đa `10^-2` khi cho phép một pha toàn cục, trên các trạng thái lưới chuẩn hóa phản đối xứng khi đổi hai electron cùng spin. Cả trạng thái so sánh trong (12) đều chứa thanh ghi ancilla, vì vậy sai số bao gồm phần rò khỏi workspace sạch. Chi phí báo cáo lấy trung bình mỗi lần chạy trên 10 thời điểm, mỗi thời điểm lặp 50 lần.

Tác giả đổi sang lưới vị trí cho một số tương tác Coulomb. Hai nhánh LCU cho mỗi điểm lưới sinh pha `i^n` và `(−i)^n` nếu có `n` electron tại điểm đó. Trung bình bằng `cos(πn/2) = 1 − n` khi (n=0,1,2). Giới hạn tối đa hai electron đến từ điều kiện phản đối xứng cùng spin. Nhờ đó có thể gộp phần tương tác tầm ngắn vào chuẩn hóa LCU, còn phần tầm xa vẫn cộng theo cặp. Mạch cũng giữ tổng động lượng electron trong thanh ghi 42 qubit giữa các bước walk, dọn trước đoạn đổi tổng động lượng và tính lại sau đó. Cách này giảm một nửa số lần tính tổng và giảm khoảng 10% cổng `T` mỗi bước so với phương án tính/xóa quanh mỗi phép dịch (App. G.3).

### Xấp xỉ nghịch đảo căn trong mô phỏng non-Born–Oppenheimer (§2.4 và App. H.3–H.4, tr. 7, 36–37)

Paper xấp xỉ `1/√(r²)` bằng đa thức Bernstein bậc ba theo tọa độ chuẩn hóa `u ∈ [0,1)` của khoảng chứa `r²`. Tổng là `Σₖ C(3,k) u^k (1−u)^(3−k) wₖ` với `k = 0..3`, `wₖ` là hệ số của khoảng. Ba so sánh với ba số đều độc lập cho số lần thành công `k` có trọng số nhị thức. Mạch dùng phân nhánh lượng tử để lấy `wₖ` theo trọng số đó. Giá trị xấp xỉ xuất hiện qua trung bình trong block encoding. Chi phí paper báo là 3.116 cổng T cho khối đánh giá có 512 hệ số, trong bước walk của mô phỏng. Nếu dùng kết quả của một nhánh làm pha trực tiếp trong invsqrt, sai số kỳ vọng chưa đủ để bảo đảm đúng pha trên từng nhánh đo.

### Tra bit góc one-hot của P450 (§2.5 và App. I.2–I.4, tr. 8, 38–41)

Ở mỗi lần SELECT, baseline nạp góc Givens 13 bit theo nhóm 19 góc và điều khiển cộng chúng vào thanh ghi phase-gradient. Mạch mới tạo 145 dây one-hot, mỗi dây đại diện một cặp vector. Bit `s` chọn vector thứ nhất ((`s = 0`)) hay thứ hai ((`s = 1`)). Với một bit góc, `M₀` và `M₁` là XOR các dây có bit đó bằng 1 ở vector tương ứng, còn `M₀₁` là XOR các dây mà cả hai vector đều có bit 1. Vì có tối đa một dây bật, `M₀₁ = M₀M₁`.

Phương trình (23) tạo addend bit có điều khiển từ các parity trên. Với `q_c` là bit điều khiển phép quay, đặt `β = q_c AND s` và `α = q_c XOR β`. Addend là `((α XOR M₁) AND (β XOR M₀)) XOR M₀₁`. Khai triển cho `α M₀ XOR β M₁` vì `αβ=0` và `M₀M₁=M₀₁`. Khi `q_c = 0` kết quả bằng 0. Khi `q_c = 1` kết quả là `M_s`. Phép đổi này cần một AND cho mỗi bit và thêm một AND mỗi phép quay để tạo (eta), đồng thời bỏ thanh ghi góc riêng. Tác giả báo 11.818 cổng `T` mỗi SELECT cho nhóm quay và góc, so với 18.844 cổng `T` của baseline.

## Điều kiện đúng, sai số và tài nguyên

- **Arcsin.** Dung sai là sai số tuyệt đối của giá trị fixed-point trên lưới. Cần chứng minh phép cộng modulo và phục hồi input, workspace, pha trên các nhánh đo. Gadget H/T/T† tạo giao thoa ở Hình S10c nằm ngoài tập cổng kickmix dùng cho phép tra bảng của paper. Bảng S2 gồm 3.104 cổng `T` từ 776 temporary AND và 594 cổng `T/T†` từ 41 gadget, tổng 3.698. Tỉ lệ khoảng 290 lần dùng baseline có dung sai yếu hơn, còn lợi ích của bước từ bản kickmix sang Clifford+T trên cùng đặc tả là khoảng 11% chi phí.
- **Stopping power.** Điều kiện `n ≤ 2` gắn với phân hoạch spin và miền vật lý, nên đẳng thức trên không mở rộng sang trạng thái lưới bất kỳ có nhiều hơn hai electron tại một điểm. Chi phí dùng mạch Clifford+T đã biên dịch và nhánh đo đắt nhất. Tác giả báo 4.374 qubit, gồm 3.948 qubit hệ và 426 ancilla, cùng khoảng `1,14 × 10^11` cổng `T` trung bình mỗi lần chạy (App. G.4).
- **P450.** Tác giả cố định bộ factor DFTHC của 63 electron trên 58 orbital không gian, với `(R, B, C) = (9, 29, 14)` (App. I.1). Với cửa sổ đến `E_top = E₀ + 0,1 Ha`, phương trình (20) chặn RMS của chênh lệch giữa năng lượng ước lượng và năng lượng thật, sau khi chặn trên cả hai giá trị tại `E_top`, ở 1 mHa cho mỗi eigenstate 63 electron. Chi phí là một lượt phase estimation trên eigenstate, chưa tính tạo trial state hoặc lặp theo overlap. Phương trình (21) dùng `λ_eff = sqrt(E_gap (2Λ − E_gap))` và `N_steps = ceil(π λ_eff / (2ε))` cho ước lượng baseline, với `Λ` là chuẩn hóa block encoding, `E_gap = E_ub + 0,1 Ha − E_SOS`, `E_ub` là cận trên của năng lượng cơ bản và `E_SOS` là cận dưới SOS. Kết quả tốt nhất dùng 47.487 bước theo cận chặt hơn và sai số Hamiltonian từ chuẩn bị trạng thái tối đa `4,0 × 10^-7` Ha trên sector 63 electron (App. I.4).

## Khả năng áp dụng vào project

Đối chiếu project tại commit `a19b0e08bb6af0f7b4cdf6fe10569d2ad43e870f`.

- **invsqrt.** [INV-BASELINE](../../../../src/invsqrt/INV-BASELINE/DESCRIPTION.md) chuẩn hóa `x` theo cặp bit, dùng Horner bậc ba và một bước Newton rồi áp pha `1/√x`. [Verifier](../../../../verifiers/invsqrt/verify_submission_invsqrt.py) yêu cầu giữ `x`, dọn workspace, theo dõi pha modulo một vòng trên miền `1..3.133.452` với dung sai `2^-24 / sqrt`x``. Điểm tính `Q` nhân chi phí Toffoli-like trung bình cộng `T/4` cho phép quay. Kỹ thuật tra hệ số và dọn thanh ghi theo liveness có thể đối chiếu. Đa thức arcsin, dung sai tuyệt đối và gadget giao thoa cần mô hình khác. App. F.3 chú thích 2 dẫn mạch `1/√x` 260 qubit, 7.735 Toffoli để minh họa tác động của baseline mới.
- **dfthcsos.** [DFT-BASELINE](../../../../src/dfthcsos/DFT-BASELINE/DESCRIPTION.md) nạp XOR delta của các batch góc 12 bit vào word riêng, với 75 góc và 3.976 địa chỉ. [Verifier](../../../../verifiers/dfthcsos/verify.py) chấm trên FeMoCo76o113e theo `λ_eff × T_total × Q_total`. Submission cung cấp họ ANGLE_k và factorization; verifier tự tính chi phí các phép quay Givens và chuẩn bị trạng thái. Vì vậy phần bỏ thanh ghi góc và ghép addend vào phase-gradient của P450 nằm ngoài giao diện submission. Ý tưởng có thể chuyển là giải mã cục bộ một nhóm nhỏ địa chỉ rồi XOR parity của các dây vào word delta, dưới giới hạn 128 qubit mỗi ANGLE_k.
- **dqi.** Liên hệ ở việc đóng băng verifier, tách bằng chứng và số đo. Phạm vi đã đọc chưa cung cấp kernel giải mã Reed–Solomon thay thế.

## Hypothesis gợi ý và cách kiểm chứng

- **invsqrt.** Giả thuyết cần kiểm là giữ nguyên các word fixed-point và lịch pha, nhưng thay cấu trúc tính bit hệ số bằng các tích bit chọn đoạn dùng chung, có thể giảm chi phí sau khi tính liveness. Trước hết so truth table của bốn đoạn baseline, kể cả bit dấu và các điểm biên; xác định liệu baseline đã chia sẻ hết tích có lợi. Đối chứng tiếp theo là [INV-3](../../../../src/invsqrt/INV-3/DESCRIPTION.md) nếu phần mới thay đổi peak workspace. Bác bỏ nếu mất tính đúng/biên pha hoặc nếu điểm cùng profile tăng vì ancilla hay chi phí dọn bổ sung.
- **dfthcsos.** Giả thuyết cần kiểm là decode one-hot theo block vừa với workspace, chia sẻ parity giữa bit delta, có thể giảm Toffoli mà giữ bảng từ baseline. Đối chiếu từng địa chỉ, từng batch, padding, cả hai lượt thuận/ngược, tính độc lập với outcome đo và dọn ancilla. Giữ factorization, tree, `J` và `brot` khi đo cơ chế; `λ_eff` dự kiến bằng đối chứng nếu toàn bộ word giống nhau. Bác bỏ nếu chi phí decode/uncompute hoặc qubit làm điểm cùng profile tăng hay vi phạm cap. Cần tính chi phí làm lại decode ở mỗi ANGLE_k, vì paper chia sẻ trong một SELECT hoàn chỉnh.

## Bằng chứng trong project và câu hỏi còn mở

- [Điểm invsqrt](../../../../src/invsqrt/SCORES.md) ghi INV-3 dev cải thiện 1,15 lần với dọn sớm/pebbling, còn INV-6 ghi 1,14 lần với cắt cụt và bù sai lệch. Hai mốc này là kết quả project của các thiết kế đã có. Chưa đối chiếu thiết kế gợi ý từ paper bằng một lượt chấm ghép cặp.
- [Điểm dfthcsos](../../../../src/dfthcsos/SCORES.md) có mốc DFT-BASELINE dev. Chưa đo phương án parity one-hot cục bộ trên cùng bảng XOR delta. Chi phí thêm của decode lặp lại và phân bổ workspace còn bỏ ngỏ.

## Tài liệu liên quan và phạm vi đọc

- Đã đọc trực tiếp tr. 1–5, §2.2–2.5 (tr. 6–8), App. A phần chi phí và App. B (tr. 19–20), App. F–G (tr. 29–35), App. H.3–H.4 (tr. 36–37), App. I (tr. 37–41). Đối chiếu Hình S10, Bảng S2, phương trình (23) và Bảng S3 trong PDF v1.
- Ngoài phạm vi đọc sâu là chứng minh Grover ở App. E, đặc tả và baseline non-Born–Oppenheimer ở App. H.1–H.2, các phụ lục tổ chức agent và mã Lean của nghiệm. Note ghi các kết quả tác giả mô tả; phần kiểm chứng Lean chưa được chạy lại.
- [Note nền về stopping power](../../../invsqrt/papers/arxiv-2308.12352/note.md), [note về spectral amplification](../../../dfthcsos/papers/doi-10.1103--pb2g-j9cw/note.md) và [note về uncompute bằng đo](../arxiv-2407.20167/note.md).
