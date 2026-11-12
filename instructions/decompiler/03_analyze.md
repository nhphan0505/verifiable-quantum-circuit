# 03 — Phân tích và lập kế hoạch tái dựng

Áp dụng [README](README.md); đọc báo cáo bước 1–2. Chỉ sửa scratch.

- Đọc verifier, baseline/code/results liên quan. Trong research chỉ đọc note.md
  Status: ready đã merge main; không mở nguồn paper/discussion gốc.
- Lập bản đồ register input/output, qubit phụ, bit đo, điều kiện, compute/uncompute,
  sửa pha, các khối lặp, số học, QROM/góc. Ghi vị trí lệnh/khối làm bằng chứng.
- Đối chiếu baseline theo phiên bản/hash thực tế; không gọi khác biệt là cải
  thiện nếu chưa có phép đo. KMX là chuỗi lệnh cấp thấp: không thể mặc nhiên
  khôi phục tên biến, hàm, vòng lặp hay hypothesis ban đầu.
- Với task 3, phân biệt phục hồi các mảng NPZ và thuật toán tạo factorization.
  Nếu chỉ có mảng cuối, ghi dependency dữ liệu; không tuyên bố phục hồi thuật toán.
- Viết kế hoạch gồm khối đã hiểu, khối giữ nguyên chuỗi lệnh, dữ liệu cần giữ,
  API dự kiến, môi trường, mục tiêu hash, cách kiểm chứng, giới hạn tài nguyên và
  điều kiện dừng khi thiếu thông tin. Không hứa giải mã mọi submission.
- Phân loại nhận định: quan sát trực tiếp / hypothesis suy ra / đã kiểm chứng.
  Hypothesis tối thiểu là khả năng tái tạo artifact đúng bytes, không bịa giả
  thuyết tối ưu để vừa template. Kiểm tra Issues mở/đóng và PR mở trước nhận việc;
  nếu chưa truy cập được GitHub, báo chưa xác minh và chưa chuyển bước nhận Issue.

Nghiệm thu: bản đồ mạch và phương án đủ để triển khai, nguồn có hash, phạm vi
khả thi đã nêu. Không cần hiểu mọi khối, nhưng phải nêu rõ mức khôi phục dự kiến.
