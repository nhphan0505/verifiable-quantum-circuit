# Biên dịch mạch lượng tử có thể kiểm chứng bằng mô phỏng cổ điển

Status: ready
Track: shared
Source: https://arxiv.org/abs/2610.23832v2
Version: arXiv:2610.23832v2

Khattar, Rubin, Gidney, Broughton, Low và Babbush trình bày ba benchmark cho cuộc thi biên dịch mạch lượng tử. Note tập trung vào phương pháp kiểm chứng và hợp đồng của từng benchmark trong phần II–III. [PDF gốc](verifiable_circuit_compilation.pdf)

## Câu hỏi và bối cảnh

Có thể đánh giá nhanh một mạch lượng tử đã biên dịch nếu mạch con chỉ dùng logic cổ điển khả nghịch, cổng pha và phép đo để dọn qubit phụ. Với đầu vào ở cơ sở tính toán, mỗi nhánh đo có thể được mô phỏng bằng cách theo dõi bit và pha. Verifier đối chiếu đầu ra, pha và workspace với tham chiếu cổ điển. Với miền lớn, tác giả dùng mẫu ngẫu nhiên và cận trên cho xác suất lỗi. Trong cuộc thi, seed kết hợp SHA-256 của bytes mạch với salt riêng để hạn chế việc thử nhiều tệp nhằm chọn mẫu thuận lợi. Phép thử có thể tái lập khi salt được công bố. [PDF, §II.A–C, tr. 3–6](verifiable_circuit_compilation.pdf#page=3)

Cận lỗi trên chồng chập ở §II.C dựa trên hai điều kiện chính. Mẫu đầu vào phải theo phân bố xác suất của trạng thái cần xét, và với mỗi chuỗi kết quả đo, mạch phải ánh xạ các đầu vào khác nhau trong miền hỗ trợ tới các đầu ra khác nhau. Theo phương trình (3), với xác suất lỗi ε, khoảng cách vết tới trạng thái đích bị chặn bởi 2√ε. Nếu verifier chấp nhận dung sai pha τ vòng, chú thích 1 cộng thêm tối đa 2πτ vào cận. [PDF, §II.C, tr. 5–6](verifiable_circuit_compilation.pdf#page=5)

## Ba benchmark và điều kiện áp dụng

| Bài | Thiết kế tham chiếu | Điều kiện kiểm và đánh đổi |
| --- | --- | --- |
| **Invsqrt** | Tính pha tỉ lệ với nghịch đảo căn bậc hai để mô phỏng thế Coulomb. Mạch tham chiếu chuẩn hóa đầu vào, tạo xấp xỉ ban đầu bằng đa thức và dùng một bước Newton–Raphson. Thực hiện bước Newton trước khi dịch lại giúp giữ toán hạng hẹp. | Verifier chạy 64 shot cho mỗi x từ 1 đến 3.133.452, tổng cộng 200.540.928 shot. Mỗi shot phải giữ nguyên x, dọn workspace và qua dung sai pha tương đối 2⁻²⁴. Điểm là Q × C, với Q là tổng qubit và C là chi phí Toffoli tương đương trung bình. C gồm Toffoli cộng một phần tư chi phí T, kể cả chi phí tổng hợp phép quay được định theo biên sai số pha còn lại. [PDF, §III.A.2–3, tr. 8–10](verifiable_circuit_compilation.pdf#page=8) |
| **DQI** | Giải syndrome Reed–Solomon trên GF(2¹²) cho bài toán optimal polynomial intersection. Mạch tham chiếu dùng Euclid mở rộng để tìm đa thức định vị lỗi, Chien/Forney để tìm vị trí và giá trị lỗi, rồi hoàn tác workspace trong khi giữ pha hiệu chỉnh. | Một syndrome gồm 70 phần tử GF(2¹²), chiếm 840 qubit. Verifier lấy mẫu vector lỗi có tối đa 35 lỗi ký hiệu theo phân bố trọng số của DQI, chọn vị trí và giá trị lỗi theo trọng số đã lấy, rồi gửi syndrome và chuỗi bit đo đều ngẫu nhiên cho mạch. Mỗi shot kiểm khôi phục syndrome, dọn workspace và pha hiệu chỉnh. Từ 102.400 shot, verifier tính cận trên ε₊ cho xác suất lỗi ở mức tin cậy 1 − 2⁻¹²⁸. Điểm hữu hạn khi ε₊ < 1/16 và bằng R(ε₊) × Q² × T, với R(ε) = ln(2) / [−ln(1/2 + 2√ε)] Q tính cả workspace, còn T là chi phí Toffoli trung bình gồm cả dọn workspace. [PDF, §III.B.2–3, tr. 12–14](verifiable_circuit_compilation.pdf#page=12) |
| **DFTHCSOS** | Phân rã DF-THC biểu diễn Hamiltonian FeMoCo. Mạch nạp word góc nhị phân để áp dụng cây quay Givens, từ đó xác định các hệ số Majorana dùng trong block encoding. Có thể nạp góc tuần tự, theo lô hoặc song song để đổi số qubit lấy chi phí. | Với FeMoCo, shift S₀ và độ rộng word một hạt β₁,₀ được cố định theo tham chiếu. Verifier dùng 64 mẫu đo mỗi địa chỉ hợp lệ, kiểm word nhất quán, giữ nguyên địa chỉ, dọn workspace và sửa pha khi chạy xuôi và ngược. Mỗi mạch nạp góc có giới hạn 128 qubit và chỉ dùng pha bội của π, với Z_POW bị cấm. Q_total trong điểm tính cả workspace theo mô hình. Các đại lượng phải hữu hạn. Hai sai số hệ số theo chuẩn Frobenius phải ≤ 0,020 Ha. Chuẩn hóa LCU thô Λ phải > 49,0 Ha và gap E_gap = E_upper − E_SOS phải vừa lớn hơn 3,914898 Ha vừa thuộc miền 0 < E_gap < 2Λ. Điểm là λ_eff × T_total × Q_total, với λ_eff = √[E_gap(2Λ − E_gap)]. Các ngưỡng 20 mHa đo sai số hệ số Hamiltonian. Bài báo để ngỏ sai số năng lượng nhiều electron. [PDF, §III.C.4–7, tr. 17–21](verifiable_circuit_compilation.pdf#page=17) |

## Hướng kiểm chứng tiếp

- **Invsqrt.** Đối chiếu một thay đổi số học hoặc lịch dọn qubit với mạch tham chiếu. Theo dõi riêng sai số pha xấu nhất và Q × C để thấy mức tiết kiệm có dùng hết biên sai số hay không.
- **DQI.** So một lịch giải mã mới trên cùng thiết lập số shot và phân bố lỗi. Ghi riêng lỗi giá trị, lỗi pha, workspace và Toffoli trước khi so điểm tổng.
- **DFTHCSOS.** Khi so cách nạp góc, cố định factorization và word góc để tách chi phí loader. Khi đổi độ chính xác hoặc refit, kiểm lại cả hai sai số hệ số và gap trên các word phục hồi từ mạch.

Đây là ghi chú từ bài báo. Các phương án kiểm chứng ở trên là suy luận cho công việc tiếp theo, và chưa có lượt chấm mới. Phụ lục triển khai nằm ngoài phạm vi tóm tắt. [Thông tin nguồn](source.json)
