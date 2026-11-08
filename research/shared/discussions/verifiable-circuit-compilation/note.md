# Biên dịch mạch lượng tử có thể kiểm chứng bằng mô phỏng cổ điển

Status: draft
Track: shared
Source: https://arxiv.org/abs/2610.23832v2
Version: arXiv:2610.23832v2

Khattar, Rubin, Gidney, Broughton, Low và Babbush trình bày ba benchmark cho cuộc thi biên dịch mạch lượng tử. Note tập trung vào phương pháp kiểm chứng và hợp đồng của từng benchmark trong phần II–III. [PDF gốc](verifiable_circuit_compilation.pdf)

## Câu hỏi và bối cảnh

Có thể đánh giá nhanh một mạch lượng tử đã biên dịch nếu mạch con chỉ dùng logic cổ điển khả nghịch, cổng pha và phép đo để dọn qubit phụ. Với đầu vào ở cơ sở tính toán, mỗi nhánh đo có thể được mô phỏng bằng cách theo dõi bit và pha. Verifier đối chiếu đầu ra, pha và workspace với tham chiếu cổ điển. Với miền lớn, tác giả dùng mẫu ngẫu nhiên và cận trên cho xác suất lỗi. Seed được dẫn xuất từ SHA-256 của bytes mạch để phép thử có thể tái lập. [PDF, §II.A–C, tr. 3–6](verifiable_circuit_compilation.pdf#page=3)

Cận lỗi trên chồng chập ở §II.C dựa trên hai điều kiện chính. Mẫu đầu vào phải theo phân bố xác suất của trạng thái cần xét, và với mỗi chuỗi kết quả đo, mạch phải ánh xạ các đầu vào khác nhau trong miền hỗ trợ tới các đầu ra khác nhau. Bài báo dùng các điều kiện đó để nối xác suất lỗi trên mẫu cơ sở với sai lệch của trạng thái lượng tử. [PDF, §II.C, tr. 5–6](verifiable_circuit_compilation.pdf#page=5)

## Ba benchmark và điều kiện áp dụng

| Bài | Thiết kế tham chiếu | Điều kiện kiểm và đánh đổi |
| --- | --- | --- |
| **Invsqrt** | Tính pha tỉ lệ với nghịch đảo căn bậc hai để mô phỏng thế Coulomb. Mạch tham chiếu chuẩn hóa đầu vào, tạo xấp xỉ ban đầu bằng đa thức và dùng một bước Newton–Raphson. Thực hiện bước Newton trước khi dịch lại giúp giữ toán hạng hẹp. | Mọi shot được thử phải qua dung sai pha tương đối 2⁻²⁴. Điểm là Q × C, với Q là tổng qubit và C là số Toffoli cộng một phần tư số cổng T. Tác giả còn dành phần biên sai số pha cho việc tổng hợp các phép quay. [PDF, §III.A.2–3, tr. 8–10](verifiable_circuit_compilation.pdf#page=8) |
| **DQI** | Giải syndrome Reed–Solomon trên GF(2¹²) cho bài toán optimal polynomial intersection. Mạch tham chiếu dùng Euclid mở rộng để tìm đa thức định vị lỗi, Chien/Forney để tìm vị trí và giá trị lỗi, rồi hoàn tác workspace trong khi giữ pha hiệu chỉnh. | Đầu vào có 70 syndrome, chiếm 840 qubit, và bộ giải mã xử lý tối đa 35 lỗi ký hiệu trong thiết lập tham chiếu. Verifier lấy 102.400 shot và tính cận trên ε₊ cho xác suất lỗi. Điểm là R(ε₊) × Q² × T, trong đó R là hệ số lặp và T là chi phí Toffoli. Việc giảm workspace có lợi rõ rệt, còn một thay đổi làm tăng lỗi có thể đẩy R lên. [PDF, §III.B.2–3, tr. 12–14](verifiable_circuit_compilation.pdf#page=12) |
| **DFTHCSOS** | Phân rã DF-THC biểu diễn Hamiltonian FeMoCo. Mạch nạp word góc nhị phân để áp dụng cây quay Givens, từ đó xác định các hệ số Majorana dùng trong block encoding. Có thể nạp góc tuần tự, theo lô hoặc song song để đổi số qubit lấy chi phí. | Verifier phục hồi word từ mạch trên từng địa chỉ hợp lệ, dùng 64 mẫu đo mỗi địa chỉ và kiểm workspace, địa chỉ cùng pha. Mỗi mạch nạp góc có giới hạn 128 qubit, còn Q_total trong điểm tính cả workspace theo mô hình. Hai sai số hệ số phải ≤ 0,020 Ha, gap phải > 3,914898 Ha và Λ phải > 49,0 Ha. Điểm là λ_eff × T_total × Q_total. Các ngưỡng 20 mHa áp dụng cho sai số chuẩn Frobenius của hệ số Hamiltonian. [PDF, §III.C.4–7, tr. 17–21](verifiable_circuit_compilation.pdf#page=17) |

## Hướng kiểm chứng tiếp

- **Invsqrt.** Đối chiếu một thay đổi số học hoặc lịch dọn qubit với mạch tham chiếu. Theo dõi riêng sai số pha xấu nhất và Q × C để thấy mức tiết kiệm có dùng hết biên sai số hay không.
- **DQI.** So một lịch giải mã mới trên cùng thiết lập số shot và phân bố lỗi. Ghi riêng lỗi giá trị, lỗi pha, workspace và Toffoli trước khi so điểm tổng.
- **DFTHCSOS.** Khi so cách nạp góc, cố định factorization và word góc để tách chi phí loader. Khi đổi độ chính xác hoặc refit, kiểm lại cả hai sai số hệ số và gap trên các word phục hồi từ mạch.

Đây là ghi chú từ bài báo. Các phương án kiểm chứng ở trên là suy luận cho công việc tiếp theo, và chưa có lượt chấm mới. Phụ lục triển khai nằm ngoài phạm vi tóm tắt. [Thông tin nguồn](source.json)
