# Nghịch đảo trường nhị phân bằng Itoh–Tsujii trong normal basis và ghost-bit basis

Status: ready
Track: dqi
Source: https://arxiv.org/abs/1209.5491v1
Version: arXiv:1209.5491v1 (2012-09-25)

- Brittanney Amento, Martin Rötteler và Rainer Steinwandt, *Quantum binary field inversion: improved circuit depth via choice of basis representation*.
- Từ khóa: GF(2^m), Frobenius, Itoh–Tsujii, depth, Toffoli, uncompute.
- Đọc [bản HTML gốc v1](https://arxiv.org/html/1209.5491v1) ngày 2026-11-09. [Metadata nguồn](source.json).

## Vấn đề và kết quả của paper

Bài xây mạch nghịch đảo trong trường nhị phân. Dùng multiplier depth tuyến tính và Frobenius dưới dạng hoán vị, tác giả đưa ra cận depth O(m log m) cho ghost-bit basis, và cho Gaussian normal basis nếu type t được giữ hằng. m là bậc mở rộng trường và t là tham số của Gaussian normal basis. Bảng 1 so sánh depth và Bảng 2 so sánh số cổng. Đây là cận xây dựng lý thuyết cho số học trường, chưa bao gồm decoder Reed–Solomon. [Paper v1, §1, §4–5](https://arxiv.org/html/1209.5491v1)

## Thuật toán và công thức cần dùng

Với a khác zero, đặt βᵢ = a^(2ⁱ−1). Quan hệ βᵢ₊ⱼ = βᵢ·(βⱼ)^(2ⁱ) cho phép dựng các mốc chỉ số là lũy thừa của hai rồi ghép theo các bit của m−1. Kết quả a⁻¹ = (βₘ₋₁)². Với m=12, một cách thế công thức của paper cho chuỗi chỉ số 1 → 2 → 4 → 8 → 10 → 11. Ba tích đầu dùng cùng toán hạng với một bản Frobenius của nó, hai tích sau dùng hai mốc khác nhau. Năm tích là chi phí tính tới kết quả trước dọn lịch sử, chưa tính toàn bộ phép nghịch đảo có cleanup. [Paper v1, §2.4, Eq. 6 và §4](https://arxiv.org/html/1209.5491v1)

Trong normal basis, bình phương xoay vòng các tọa độ. Ghost-bit basis ở Definition 2.2 dùng m+1 tọa độ khi đa thức toàn hệ số một bậc m bất khả quy. Trong biểu diễn vòng của §2.2, bình phương hoán vị các vị trí theo nhân hai modulo m+1. Đọc kết quả về basis đa thức tương ứng bằng XOR ghost bit vào các tọa độ còn lại. Mạch có yêu cầu trả ghost bit về zero phải tính phần cleanup này. Với m=12, đa thức toàn hệ số một bậc 12 thỏa điều kiện vì 2 có bậc 12 modulo 13. Đó là suy luận cho biểu diễn thay thế, còn modulus của verifier dùng basis đa thức khác. [Paper v1, §2.2–2.3, Eq. 1–2](https://arxiv.org/html/1209.5491v1) · [Companion v2, §III.2.2](https://arxiv.org/html/2610.23832v2#S3.SS2)

## Điều kiện đúng, sai số và tài nguyên

Phép toán trường là exact. Footnote 3 ở §4 ghi mạch lũy thừa cho đầu vào zero xuất zero. Trong decoder, tính đúng của nhánh pivot zero còn phụ thuộc vào recurrence và chiều đảo.

Proposition 3.1 cho multiplier ghost-bit tổng quát dùng (m+1)² Toffoli, depth m+1. Proposition 3.2 cho tích đặc biệt a·a^(2ʳ), với r cố định, dùng cận m²+m Toffoli, m+1 CNOT và depth 2m+2. Thế m=12 vào cận nghịch đảo ghost-bit của Proposition 4.1 với floor(log₂(11))=3 và popcount(11)=3 cho **1.612 Toffoli, 78 CNOT, depth 208 và 78 qubit** theo các biểu thức của mệnh đề. Cận gate/depth đã nhân đôi để tính uncompute. Đây là số thế công thức, chưa tính chuyển basis tại biên decoder hoặc tối ưu bằng HMR. [Paper v1, Proposition 3.1–3.2 và 4.1](https://arxiv.org/html/1209.5491v1)

## Khả năng áp dụng vào project

DQI phải giữ nguyên các word syndrome, áp parity theo mask cổ điển runtime và trả scratch sạch. Frobenius đã tuyến tính trên GF(2) trong basis của verifier. Lợi ích cần đo của normal basis nằm ở lịch dây, depth và chi phí tích đặc biệt. Mỗi ghost-bit bổ sung cũng có thể làm tăng peak Q, ảnh hưởng trực tiếp đến R·Q²·T. [Verifier DQI](../../../../verifiers/dqi/verify_submission_dqi.py) · [Companion v2, §III.2](https://arxiv.org/html/2610.23832v2#S3.SS2)

Repo đã có tensor rank-42 và kernel multiply-add có quantum control 54 Toffoli-like ở DQI-19. DQI-27 có primitive nghịch đảo riêng dùng norm và conjugate. Hai mốc này tại main `b61293b7dec859a2cacd1ec64c54ef03dbaef5ac` là đối chứng phù hợp cho từng phép toán, với giao diện và cleanup tương ứng. [DQI-19](../../../../src/dqi/DQI-19/DESCRIPTION.md) · [DQI-27 solution.py](../../../../src/dqi/DQI-27/solution.py)

## Hypothesis gợi ý và cách kiểm chứng

Nếu thử Itoh–Tsujii, cô lập một primitive nghịch đảo có cùng giao diện với primitive hiện tại. Kiểm toàn bộ 4.096 giá trị, kể cả quy ước zero, rồi kiểm pha và cleanup ở cả hai chiều. Tính cả đổi basis, ancilla và control ở nơi gọi. Chỉ đưa vào decoder nếu số đo primitive và lịch sống ở biên có đường cải thiện Q²T. Đây là đề xuất áp dụng, chưa có run đo.

## Bằng chứng trong project và câu hỏi còn mở

Chưa có kết quả project cho inverter ghost-bit của paper này. Kết quả DQI-19 đo phép nhân theo tensor khác, còn DQI-27 dùng đường nghịch đảo khác. Chưa biết thiết kế Itoh–Tsujii có thể giảm tài nguyên tại một điểm gọi cụ thể sau khi tính cleanup hay không.

## Tài liệu liên quan

Đã đọc §1, §2.2–2.4, §3.1, phần lập chi phí của §4 và §5. Chưa rà toàn bộ chứng minh cho Gaussian normal basis trong §3.2, chưa tái lập các mạch trong paper. Mục nguồn pin arXiv v1 bằng URL. [Bản gốc và thông tin phiên bản](https://arxiv.org/abs/1209.5491v1)
