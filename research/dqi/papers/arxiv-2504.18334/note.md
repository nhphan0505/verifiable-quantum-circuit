# Quantum Circuit Design for Decoded Quantum Interferometry — giới hạn của Gauss–Jordan khi giải mã syndrome

Status: draft
Track: dqi
Source: arXiv:2504.18334
Version: v2 (truy cập 2026-11-09)

- Natchapol Patamawisut, Naphan Benchasattabuse, Michal Hajdušek và Rodney Van Meter (2025).
- Từ khóa — Max-XORSAT, Dicke state, Gauss–Jordan thuận nghịch, hậu chọn, va chạm syndrome.
- [PDF arXiv v2](paper.pdf) và [metadata/SHA-256](source.json). Số trang tính từ trang đầu PDF.

## Vấn đề và kết quả của paper

Bài dựng các khối của DQI cho Max-XORSAT trên GF(2), gồm chuẩn bị chồng chập Dicke, gắn pha của vế phải, tạo syndrome, thử xóa thanh ghi lỗi bằng Gauss–Jordan (GJE) hoặc bảng tra, rồi Hadamard và hậu chọn. Tác giả báo mô phỏng các ví dụ MaxCut đến 30 qubit. Kết quả hậu chọn của ví dụ 6 bit tập trung xác suất tại các đỉnh của hàm mục tiêu (mục VII, tr. 8–10, Hình 5). Đây là kết quả mô phỏng đầu cuối trên instance nhỏ. Mục Điều kiện đúng bên dưới kiểm tra riêng liệu GJE có thể xóa chính xác mọi lỗi trong miền đã chuẩn bị hay không.

## Thuật toán và công thức cần dùng

Với $m$ ràng buộc và $n$ biến, $B∈GF(2)^{m×n}$, $v∈GF(2)^m$ và $f(x)=Σ_i(-1)^{v_i+b_i·x}$. Cho $ℓ$ là bậc của đa thức lọc kiêm trọng số Hamming tối đa của lỗi cần giải mã, và $Σ_{k=0}^{ℓ}|w_k|²=1$. Pipeline của mục II–V (tr. 2–5, Eq. 4 và 9–13, Hình 1):

1. Chuẩn bị $Σ_k w_k|0^{m-k}1^k⟩$ với mã unary. Khối $U_{m,ℓ}$ dùng các phép chia biên độ SCS để đưa thành $Σ_k w_k|D(m,k)⟩$, trong đó $|D(m,k)⟩$ là tổng chuẩn hóa đều trên các xâu $y$ trọng số $k$. Hệ số của hai nhánh khi tách bit đầu là $√((m-k)/m)$ và $√(k/m)$.
2. Gắn pha $(-1)^{v·y}$ bằng Z trên thanh ghi lỗi. Với thanh ghi syndrome sạch, CNOT ở các phần tử $B_{ij}=1$ tạo $s=B^T y$ và giữ lại $y$.
3. Nếu có decoder thuận nghịch đúng trên miền, dùng $s$ để XOR $D(s)$ vào $y$ và đảo scratch decoder. Điều kiện để thanh ghi lỗi về 0 là $D(B^T y)=y$. Sau đó áp $H^{⊗n}$ lên syndrome và đo. Mạch paper hậu chọn trên thanh ghi lỗi bằng 0 (mục V.A.6, tr. 6, và VII.C, tr. 9).

Mục IV và VI.E (tr. 3, 7) mô tả chọn pivot, đổi hàng, rồi XOR để triệt các phần tử còn lại của cột pivot. Nếu $B^T$ cố định, có thể tìm lịch hàng cổ điển. Mỗi phép đổi hàng trên syndrome là SWAP, mỗi phép cộng hàng là CNOT. Với tích khả nghịch $E$ của các phép hàng, mạch tạo $Es=EB^T y$. Trường hợp vuông khả nghịch có $EB^T=I$. Khi đó XOR kết quả vào thanh ghi lỗi rồi đảo mạng $E$ phục hồi $s$. Với ma trận chữ nhật hoặc suy biến, cần giải thích các biến tự do và ràng buộc trọng số trước khi xem $Es$ là $y$.

**Trọng số lọc.** Ở Eq. 14 (tr. 5), $w$ là vector riêng đơn vị ứng với trị riêng lớn nhất của ma trận ba đường chéo có $A_{kk}=kd$, $A_{k-1,k}=A_{k,k-1}=√(k(m-k+1))$ với $k=1,…,ℓ$, và $d=(p-2r)/√(r(p-r))$. $p$ là kích thước trường nguyên tố và $r$ là số giá trị thỏa của mỗi ràng buộc. Trong Max-XORSAT, $p=2$, $r=1$, nên $d=0$. Verifier RS cũng dùng cấu trúc ma trận này để lấy mẫu $k$ theo $|w_k|²$, với $q=4096$ thay cho $p$ và $r=2016$. Đây là đối chiếu quy tắc lấy mẫu trong code, còn tính duy nhất của decoder phải xét theo mã và miền lỗi tương ứng.

## Điều kiện đúng, sai số và tài nguyên

**Tính duy nhất.** Trên miền $|y|≤ℓ$, syndrome là đơn ánh nếu và chỉ nếu $\ker B^T$ không có vector khác 0 trọng số ≤ $2ℓ$. Nếu hai lỗi hợp lệ va chạm, hiệu của chúng nằm trong kernel và có trọng số ≤ $2ℓ$. Ngược lại, có thể chia support của một vector kernel như vậy thành hai lỗi, mỗi lỗi trọng số ≤ $ℓ$. GJE chỉ giải hệ tuyến tính. Ngay cả khi syndrome đơn ánh trên miền lỗi nhẹ, việc tìm nghiệm nhẹ vẫn cần khai thác cấu trúc mã hoặc một thuật toán tìm nghiệm. Nếu $m>n$ và $ℓ≥1$, một ánh xạ **tuyến tính** từ syndrome về toàn bộ lỗi mà đúng với mọi lỗi trọng số 1 sẽ phải thỏa $LB^T=I_m$, điều bất khả do hạng.

**Kiểm tra đại số trên ví dụ của paper.** Đánh số hàng từ 1 trong ma trận $B$ ở mục VII.C, tr. 9. Ba hàng $b_1=(1,0,0,0,0,1)$, $b_2=(1,1,0,0,0,0)$ và $b_5=(0,1,0,0,0,1)$ thỏa $b_1=b_2⊕b_5$. Lỗi ở riêng vị trí 1 và lỗi ở cặp vị trí 2, 5 cùng syndrome, dù cả hai đều nằm trong miền $ℓ=2$. Do đó không có hàm của syndrome xóa đúng đồng thời cả hai lỗi đó. Phân bố đã hậu chọn trong Hình 5 vẫn có thể tập trung vào nghiệm tốt trên instance này. Hình không chứng minh giải mã tất định trên toàn miền.

**Đối chiếu mã tác giả.** Snapshot mã công khai được dẫn tại mục VII.D dùng phép khử mod 2 ở phía cổ điển, ghi danh sách phép hàng rồi phát CNOT/SWAP. Đường GJE của script truyền `B.T` trực tiếp vào gate. Hàm lập lịch coi cột cuối của đầu vào là vế phải và loại khỏi cột pivot, trong khi gate chỉ nhận một thanh ghi và không lấy nghiệm trọng số thấp. Quan sát này giới hạn ở snapshot đã đọc. Chưa xác định snapshot đó có tái lập đúng Hình 5 hay Bảng II hay không. [Lập lịch](https://github.com/BankNatchapol/DQI-Circuit/blob/ae7692318ecfb627a7100fbe9be8e3169bc99de9/src/dqi/qiskit/decoding/algorithms.py), [gate](https://github.com/BankNatchapol/DQI-Circuit/blob/ae7692318ecfb627a7100fbe9be8e3169bc99de9/src/dqi/qiskit/decoding/gates.py), [script](https://github.com/BankNatchapol/DQI-Circuit/blob/ae7692318ecfb627a7100fbe9be8e3169bc99de9/scripts/generate_dqi_circuit_qiskit.py).

**Chi phí paper.** Bảng I và Eq. 20 (tr. 6–7) báo cho khối GJE ≤ $mn$ CNOT, ≤ $n$ SWAP, depth ≤ $n(m+1)$ và $m+n$ dây. Đây là cận tác giả nêu cho lịch hàng và thao tác XOR theo mô tả, chưa là cận của decoder tổng quát đúng trên mọi lỗi. Nếu dùng thêm lượt đảo để phục hồi syndrome sau khi áp pha hoặc XOR, cần tính cả lượt đảo. Eq. 21–23 dùng $\sum_{j=0}^{ℓ}\binom{n}{j}$ trong chi phí bảng tra. Với $y$ dài $m$ theo định nghĩa ở mục II, số ứng viên lỗi nhị phân trước khi xử lý va chạm là $\sum_{j=0}^{ℓ}\binom{m}{j}$, nên cần kiểm tra lại chỉ số khi $m≠n$.

Bảng II (tr. 9) ghi tại $m=15$ khối GJE dùng 46 cổng, depth 39, và bảng tra dùng 67.027 cổng, depth 62.547, cả hai trên 30 qubit. Số đếm lấy sau transpile Qiskit vào tập cổng được liệt kê trong bảng. Paper chưa định lượng đầy đủ chi phí cổ điển, tổng hợp góc, xác suất chấp nhận hậu chọn ở quy mô lớn hay lỗi phần cứng.

## Khả năng áp dụng vào project

[Verifier DQI](../../../../verifiers/dqi/verify_submission_dqi.py) và [mô tả baseline](../../../../src/dqi/DQI-BASELINE/DESCRIPTION.md) tại main `84bdf39776f20902ff1abb454bb37c70ff75f4bb` cho thấy bài thi chỉ chấm decoder pha Reed–Solomon trên GF(2^12). Có 4.095 vị trí, 70 syndrome 12 bit, tối đa 35 lỗi ký hiệu. Mỗi shot nhận $S$ và mask cổ điển $M_j$. Cần giữ $S$, trả ancilla sạch và áp dấu $(-1)^{Σ_j\mathrm{popcount}(e_j\mathbin{\&}M_j)}$. Không được dùng hậu chọn để loại shot sai. Baseline lấy đa thức định vị và đánh giá qua EEA rồi dùng Chien–Forney để áp pha và uncompute. Điểm verifier là $R(ε_+)·Q²·T$, với $T$ là Toffoli-like trung bình theo shot và $R$ phụ thuộc cận lỗi. Các số cổng/depth của Bảng II không quy đổi trực tiếp thành điểm này.

Phép hàng khả nghịch và tuyến tính có thể chuyển thành một lớp CNOT để đổi biểu diễn syndrome. Ánh xạ đó bảo toàn thông tin, nhưng không giải phần phi tuyến của việc tìm support và giá trị lỗi. Việc áp dụng sang RS cần ghi ánh xạ ở biên decoder, bảo toàn thứ tự hệ số và thứ tự bit dùng trong tích mask.

## Hypothesis gợi ý và cách kiểm chứng

Nếu một biểu diễn tuyến tính của syndrome giúp gộp hai khối tuyến tính cố định trong một decoder RS hiện có, thử tổng hợp phép hợp thành thay vì tạo thanh ghi trung gian riêng. Đây là suy luận kỹ thuật từ cách lập lịch phép hàng, chưa có bằng chứng giảm điểm. Trước khi so chi phí, cần đối chiếu ma trận hai cách trên toàn bộ vector cơ sở, chứng minh biến đổi ngược khôi phục $S$, và kiểm tra pha/ancilla ở trọng số 0, 1 và 35 với mask ngẫu nhiên và mask đơn bit. Bác bỏ nếu chỉ giảm CNOT mà $Q$, $T$ và cận lỗi vẫn như cũ, hoặc nếu phát sinh sai pha hay lỗi hồi phục thanh ghi.

## Bằng chứng trong project và câu hỏi còn mở

Baseline đã có các run đối chiếu trong DESCRIPTION. Repo chưa có kết quả chấm phương án GJE hoặc đổi biểu diễn syndrome từ paper này. Đã đọc mục I–VII, tr. 1–10, với trọng tâm decoder, Bảng I–II và ví dụ 6 bit. Chưa tái lập mô phỏng, rà toàn bộ notebook/mã tác giả, tài liệu dẫn hay bản IEEE. Xem [coverage](source.json).

## Tài liệu liên quan

- [arXiv v2](https://arxiv.org/abs/2504.18334v2) và [bản IEEE QCE](https://doi.org/10.1109/QCE65121.2025.00041).
- [Note về DQI gốc](../doi-10.1038--s41586-025-09527-5/note.md) và [note về DQI trên GF(2^b)](../arxiv-2510.10967/note.md).
