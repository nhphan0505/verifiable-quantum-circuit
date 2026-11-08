# Elucidating reaction mechanisms on quantum computers — ước lượng tài nguyên FeMoco bằng Trotter/QPE (mốc 2017)

Status: ready
Track: dfthcsos
Source: doi:10.1073/pnas.1619152114; paper.pdf; metadata và SHA-256 trong source.json
Version: bản xuất bản PNAS 114(29):7555–7560 (2017), PDF tải ngày 2026-11-07 theo chân trang; truy cập 2026-11-08

- Paper: Markus Reiher, Nathan Wiebe, Krysta M. Svore, Dave Wecker, Matthias Troyer, *Elucidating reaction mechanisms on quantum computers*, PNAS 114(29):7555–7560, 2017, doi:10.1073/pnas.1619152114. PDF không ghi mã arXiv; không tra nguồn ngoài để bổ sung.
- Track: `dfthcsos`. Căn cứ: task 3 chấm block encoding cho Hamiltonian FeMoco ([SCORING_README](../../../../verifiers/dfthcsos/SCORING_README.md)); paper này là ước lượng tài nguyên FeMoco đầu tiên được PRX 2025 liệt kê ở Table I là mốc "2017, first resource estimate by Trotterization [37]" (xem [note PRX](../doi-10.1103--pb2g-j9cw/note.md)). Độ chắc chắn phân loại: cao về chủ đề, nhưng **liên hệ kỹ thuật với mạch ANGLE_k là gián tiếp**.
- Từ khóa: FeMoco, nitrogenase, CAS, quantum phase estimation (QPE), Trotter–Suzuki, T gate, surface code, T factory, rotation factory, Serial / Nesting / PAR.
- Bản đã đọc: [paper.pdf](paper.pdf) (6 trang, giữ nguyên bytes; SHA-256 trong source.json). Trang PDF 1–6 tương ứng trang tạp chí 7555–7560.
- Phạm vi đọc: toàn bộ thân bài tr. 1–5 (abstract, Significance, các mục "Quantum Chemical Methods for Mechanistic Studies", "Exact Diagonalization Methods", "Ways Quantum Computers Will Help", "Quantum Simulation of Quantum Chemical Systems", "Resource Estimates", "Resource Requirements with Quantum Error Correction", "Discussion"), Fig. 1–3, Table 1–2. Đã đối chiếu trực quan ảnh trang 3 (Table 1) và trang 4 (Table 2, Fig. 3) vì text trích xuất bị vỡ cột.
- Chưa đọc: **SI Appendix** (không có trong PDF được giao; paper dẫn tới nó cho chi tiết mô hình Hamiltonian, mạch Trotter, độ sâu giảm 4 lần, phase estimation song song, chuẩn bị trial state). Danh sách tài liệu tham khảo tr. 5–6 chỉ lướt. Không truy cập nguồn dẫn.

## Vấn đề và kết quả của paper

Paper đặt câu hỏi "dùng máy tính lượng tử thế nào, cụ thể, cho một bài toán hóa học mở" và chọn cơ chế cố định nitơ ở FeMoco của nitrogenase làm ví dụ (tr. 1–2). Đóng góp gồm hai phần:

1. **Quy trình lai cổ điển–lượng tử** (Fig. 2, tr. 2): cổ điển sinh và tối ưu cấu trúc (DFT), chọn orbital cho active space, biến đổi tích phân 4 chỉ số; máy lượng tử trả năng lượng CAS-QFCI (full CI trong complete active space); cổ điển thêm hiệu chỉnh nhiệt độ/entropy rồi mô hình động học. Paper lập luận năng lượng kích hoạt vào hàm mũ của hằng số tốc độ nên cần sai số rất nhỏ (tr. 1–2).
2. **Ước lượng tài nguyên** cho hai cấu trúc FeMoco (Table 1, tr. 3; Table 2, tr. 4). Đây là **ước lượng lý thuyết của tác giả**, không phải chạy trên phần cứng. Chú thích Table 1 ghi rõ con số "likely to be pessimistic".

Mô hình hệ trong Table 1 (tr. 3):

| Cấu trúc | Spin / điện tích | Electron / orbital không gian |
| --- | --- | --- |
| Structure 1 | S = 0, +3 | 54 e / 54 orbital |
| Structure 2 | S = 1/2, 0 | 65 e / 57 orbital |

Lưu ý: hệ chấm của project là **FeMoCo76o113e** (76 orbital, 113 electron; SCORING_README). Đây không phải mô hình 54 orbital của paper này. PRX 2025 phân biệt FeMoco-54 [37] (paper này) với FeMoco-76 [38] (nguồn khác).

## Thuật toán và công thức cần dùng

- QPE: với $e^{-iHt}|n\rangle = e^{-iE_n t}|n\rangle$, QPE học pha $\phi = E_n t$; đo từ trạng thái gần ground state sẽ chiếu về một trạng thái riêng và cho năng lượng của nó (tr. 3).
- Tiến hóa thời gian bằng **Trotter–Suzuki bậc thấp**. Tác giả biết có thuật toán scaling tốt hơn (ref. 39–44) nhưng đánh giá sơ bộ cho rằng ở kích thước này chúng tệ hơn, nên để việc tính chi phí đầy đủ cho các phương pháp đó cho công việc sau (tr. 3). Chi tiết mạch nằm trong SI, **chưa đọc**.
- Chịu lỗi: surface code; Clifford coi là rẻ; phép quay một qubit được xấp xỉ bằng Clifford+T. Mỗi T cần magic state distillation, được tác giả coi là phần đắt nhất (tr. 3–4).
- Ba cách thực hiện phép quay (tr. 4):
  - **Serial**: quay tuần tự; tổng hợp theo ref. 48.
  - **Nesting** (ref. 18): các số hạng Hamiltonian tác động lên tập spin-orbital rời nhau chạy song song.
  - **PAR** (programmable ancilla rotations, ref. 12): tạo trước phép quay trong các factory song song rồi teleport vào mạch. Nesting và PAR tổng hợp theo ref. 49.
- Kiến trúc (Fig. 3, tr. 4–5): siêu máy tính cổ điển + bộ xử lý lượng tử chính + các T factory (Tfac) và rotation factory (QRot) chuyên dụng. Tác giả nhận xét mô phỏng chỉ cần magic state khi thực hiện phép quay một qubit (tr. 5).

## Điều kiện đúng, sai số và tài nguyên

Giả định của tác giả (tr. 4): logical T gate mất 10 ns hoặc 100 ns; Clifford tốn thời gian không đáng kể; **có sẵn trial state tốt** (chi phí chuẩn bị nằm trong SI). Mục tiêu sai số tổng 0.1 mHa ("quantitatively accurate"), tức đã cộng mọi sai số rời rạc hóa và thống kê; ngoài ra xét 1 mHa ("qualitatively accurate").

Table 1 (tr. 3, đối chiếu ảnh trang). T gates, Clifford gates, thời gian ở 10 ns / 100 ns cho mỗi T, logical qubit:

| Độ chính xác | Cấu trúc | Cách | T gates | Cl. gates | Δt (10 ns) | Δt (100 ns) | Qubits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.1 mHa | 1 | Serial | 1.1×10¹⁵ | 1.7×10¹⁵ | 130 d | 3.6 y | 111 |
| 0.1 mHa | 1 | Nesting | 3.5×10¹⁵ | 5.7×10¹⁵ | 15 d | 4.9 mo | 135 |
| 0.1 mHa | 1 | PAR | 3.1×10¹⁶ | 3.1×10¹⁶ | 110 h | 1.5 mo | 1,982 |
| 0.1 mHa | 2 | Serial | 2.0×10¹⁵ | 3.1×10¹⁵ | 240 d | 6.6 y | 117 |
| 0.1 mHa | 2 | Nesting | 6.5×10¹⁵ | 1.0×10¹⁶ | 27 d | 8.9 mo | 142 |
| 0.1 mHa | 2 | PAR | 6.0×10¹⁶ | 6.0×10¹⁶ | 210 h | 2.9 mo | 2,024 |
| 1 mHa | 1 | Serial | 1.0×10¹⁴ | 1.6×10¹⁴ | 12 d | 3.9 mo | 111 |
| 1 mHa | 1 | Nesting | 3.3×10¹⁴ | 5.6×10¹⁴ | 1.4 d | 14 d | 135 |
| 1 mHa | 1 | PAR | 3.0×10¹⁵ | 3.0×10¹⁵ | 11 h | 4.6 d | 1,982 |
| 1 mHa | 2 | Serial | 1.9×10¹⁴ | 3.0×10¹⁴ | 22 d | 7.2 mo | 117 |
| 1 mHa | 2 | Nesting | 6.0×10¹⁴ | 9.9×10¹⁴ | 2.5 d | 25 d | 142 |
| 1 mHa | 2 | PAR | 5.5×10¹⁵ | 5.5×10¹⁵ | 20 h | 8.3 d | 2,024 |

Table 2 (tr. 4) tính overhead chịu lỗi cho Structure 1, mục tiêu 0.1 mHa, cổng vật lý 100 MHz, theo ref. 45. Một số giá trị đại diện (đối chiếu ảnh trang):

- Serial: logical qubit 111. Ở error rate 10⁻³ cần 202 T factory, tổng ~1.8×10⁸ physical qubit. Ở 10⁻⁶: 68 factory, ~1.2×10⁶ qubit. Ở 10⁻⁹: 38 factory, ~2.3×10⁵ qubit.
- PAR: 1872 rotation factory; số T factory tăng khoảng 1000 lần so với Serial (166462 ở 10⁻³); tổng ~1.8×10¹¹ physical qubit ở 10⁻³.
- Nesting: 26 rotation factory; tổng ~5.1×10⁹ / 3.0×10⁷ / 5.2×10⁶ physical qubit ở 10⁻³ / 10⁻⁶ / 10⁻⁹.
- Code distance in trong bảng (ví dụ "35,17" ở 10⁻³) có hai số cho một số cột; paper không giải thích trong thân bài. Note này không diễn giải thêm.

Kết luận của tác giả (tr. 5): 10⁻³ error rate với cổng 10 MHz có thể chạy trong thời gian hợp lý bằng Nesting/PAR nhưng số physical qubit "likely prohibitive"; mục tiêu "aspirational" là cổng 100 MHz, error rate 10⁻⁶. Với 54 orbital và Nesting, tài nguyên được so sánh ngang Shor cho số 4096 bit (ref. 45). Số lần lặp phase estimation để chiếu từ ansatz về ground state là **bài toán mở** (tr. 5).

Khác biệt mô hình chi phí với project: paper đếm **T gate và Clifford** của tiến hóa Trotter, thời gian tường và physical qubit. Verifier của project chấm `lambda_eff × T_total × Q_total`, với T_total là số Toffoli-like (CCX/CCZ/CSWAP) của mạch ANGLE_k cộng mô hình heuristic của state preparation và phép quay Givens; Q_total là logical qubit theo mô hình `SpinFreeData_V1` (SCORING_README, mục Scoring). Không có số nào trong paper này so trực tiếp được với điểm project.

## Khả năng áp dụng vào project

Snapshot đối chiếu: commit `cd4f4ac58360aad26e634a29c13cc6046298dbd5`.

- [src/dfthcsos/DFT-BASELINE/solution.py](../../../../src/dfthcsos/DFT-BASELINE/solution.py), SHA-256 blob `5c4599510c1bf0a1a26873e08edb05127534b91fb079e0ac7eae904d9ad7327b`.
- [verifiers/dfthcsos/SCORING_README.md](../../../../verifiers/dfthcsos/SCORING_README.md), SHA-256 blob `c2228569f96e58e118419bc32be2be9e33d6abffb8117cb0b91e1fc25b2a0230`.

Suy luận của nhóm (không phải kết quả paper):

- Paper này **không cung cấp kỹ thuật mạch dùng thay được** trong ANGLE_k: baseline là QROM tải word góc Givens cho block encoding DF/THC-SOS qua qubitization, còn paper dùng Trotter–Suzuki. Phương pháp Trotter không có trong verifier.
- Giá trị chính là **bối cảnh và động cơ**: vì sao FeMoco là benchmark; mức chính xác mục tiêu (0.1–1 mHa); con số mốc 2017 để hiểu chuỗi cải tiến (PRX 2025 Table I đặt 5.0×10¹³ Toffoli cho mốc 2017 trên FeMoco-54, khác đơn vị T gate ở đây; xem note PRX).
- Quan sát của paper rằng "chỉ phép quay mới cần magic state" và việc tách rotation factory khớp tinh thần rằng chi phí non-Clifford tập trung ở phép quay/tải góc. Đây chỉ là liên hệ định tính, không dẫn tới thay đổi cụ thể cho ANGLE_k.

## Hypothesis gợi ý và cách kiểm chứng

Không đề xuất hypothesis thuật toán trực tiếp từ paper này: không có thành phần nào ánh xạ vào mạch ANGLE_k hay factorization được chấm. Khi sinh hypothesis cho track, nên dùng note PRX 2025 (DFTHC/SA) làm nguồn kỹ thuật, còn note này chỉ để dẫn bối cảnh/mức chính xác.

## Bằng chứng trong project và câu hỏi còn mở

- Chưa có Issue/run nào dùng nguồn này. Best đã kiểm tra đầy đủ của track: chưa có (src/dfthcsos/README.md); SCORES.md chỉ có DEV_5MIN của baseline.
- Câu hỏi mở (từ paper): số lần lặp QPE để chuẩn bị ground state từ ansatz; chi phí chuẩn bị trial state (SI, chưa đọc).
- Chưa kiểm chứng: mọi chi tiết trong SI Appendix; ý nghĩa cặp code distance trong Table 2.

## Tài liệu liên quan

- [Note PRX 2025 — DFTHC + spectral amplification](../doi-10.1103--pb2g-j9cw/note.md): trích dẫn paper này là [37] (FeMoco-54).
- [Mô tả baseline DFT-BASELINE](../../../../src/dfthcsos/DFT-BASELINE/DESCRIPTION.md).
- Không kế thừa code; không có giấy phép code cần ghi.
