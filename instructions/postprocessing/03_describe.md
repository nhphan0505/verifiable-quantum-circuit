# 03 — Viết DESCRIPTION trước triển khai

Áp dụng [workflow PP](README.md). Đầu vào: Issue, mã, owner và branch đã xác
minh. Chỉ viết DESCRIPTION của PP, dòng danh mục tương ứng và đồng bộ Issue;
không sửa DESCRIPTION experiment nguồn.

## Nội dung bắt buộc

H1 trùng title Issue. Viết đủ để người khác triển khai và kiểm chứng:

1. Hypothesis, phạm vi common/track và điểm khác hướng đã có.
2. Nguồn kế thừa, phiên bản/commit, attribution nếu có.
3. Thuật toán, điều kiện áp dụng/từ chối; lập luận bảo toàn ngữ nghĩa, pha,
   ancilla khi liên quan. Nếu xấp xỉ, ghi ngân sách sai số và cách đánh giá.
4. API đầu vào/đầu ra, cách gọi, tham số/default và xử lý giá trị không hợp lệ.
   Không tạo config JSON riêng cho kiểm chứng PP.
5. Tests mạch nhỏ: trường hợp thường, biên, không được áp dụng và kiểm tra
   hành vi thay vì chỉ số cổng.
6. Mạch benchmark từ experiment cũ: đường dẫn/phiên bản nguồn, hash khi đã
   xác minh, cách biết đầu vào chưa qua PP khác. Không bịa giá trị còn thiếu.
7. Đối chứng không PP và ứng viên chỉ bật PP này, cùng mạch và profile chấm;
   chỉ tiêu đúng/chi phí, dự đoán, tiêu chí ủng hộ/bác bỏ, giới hạn thử/dừng.
8. Mục kết luận để cập nhật sau kiểm chứng; ban đầu ghi rõ chưa chấm.

Mô tả là bản chuẩn; đồng bộ nội dung Issue và dùng link GitHub đọc được khi
đưa lên Issue. Không chép mô tả thuật toán nguồn dài dòng nếu chỉ kế thừa.
Đổi tiêu chí sau khi thấy kết quả phải ghi lý do, không sửa thành dự đoán ban đầu.

## Nghiệm thu

- [ ] DESCRIPTION và Issue thống nhất, danh mục có link hợp lệ.
- [ ] Có thuật toán, API, điều kiện đúng và kế hoạch kiểm chứng riêng PP.
- [ ] Chưa gán PASS hoặc số đo cho công việc chưa thực hiện.
